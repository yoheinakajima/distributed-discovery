#!/usr/bin/env bash
set -euo pipefail
umask 077

die() {
  printf 'runtime-startup-failed:%s\n' "$1" >&2
  exit 1
}

for name in \
  HF_TOKEN \
  TREASUREBENCH_RUNTIME_API_KEY \
  TREASUREBENCH_RUNTIME_ATTESTATION_KEY \
  TREASUREBENCH_EXPECTED_IMAGE_DIGEST \
  TREASUREBENCH_RUNTIME_MANIFEST_B64 \
  TREASUREBENCH_PROXY_SCRIPT_B64
do
  [[ -n "${!name:-}" ]] || die "missing-${name}"
done

runtime_dir=/workspace/treasurebench-runtime
model_dir=/workspace/model
manifest_path="${runtime_dir}/manifest.yml"
proxy_path="${runtime_dir}/proxy.py"
attestation_path="${runtime_dir}/runtime-attestation.json"
mkdir -p "${runtime_dir}" "${model_dir}"
chmod 700 "${runtime_dir}" "${model_dir}"
printf '%s' "${TREASUREBENCH_RUNTIME_MANIFEST_B64}" | base64 --decode >"${manifest_path}"
printf '%s' "${TREASUREBENCH_PROXY_SCRIPT_B64}" | base64 --decode >"${proxy_path}"
chmod 600 "${manifest_path}" "${proxy_path}"

python3 - "${manifest_path}" "${TREASUREBENCH_EXPECTED_IMAGE_DIGEST}" <<'PY'
import sys
import yaml

manifest = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
expected = manifest["container"]["image_digest"]
if expected != sys.argv[2]:
    raise SystemExit("container digest mismatch")
if manifest["container"]["immutable_reference"].split("@", 1)[1] != expected:
    raise SystemExit("container immutable reference mismatch")
if manifest["model"]["quantized"] or manifest["model"]["precision"] != "BF16":
    raise SystemExit("quantized or non-BF16 model rejected")
if manifest["compute"]["gpu_count"] != 1:
    raise SystemExit("GPU count mismatch")
PY

mapfile -t gpu_names < <(nvidia-smi --query-gpu=name --format=csv,noheader)
[[ "${#gpu_names[@]}" -eq 1 ]] || die "gpu-count"
[[ "${gpu_names[0]}" == "NVIDIA A100 80GB PCIe" ]] || die "gpu-type"
driver_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | tr -d '[:space:]')
python3 - "${manifest_path}" "${driver_version}" <<'PY'
import sys
import yaml

manifest = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))


def version(value):
    parts = value.split(".")
    if not parts or any(not part.isdigit() for part in parts):
        raise SystemExit("malformed NVIDIA driver version")
    return tuple(int(part) for part in parts)


if version(sys.argv[2]) < version(manifest["compute"]["minimum_linux_driver_version"]):
    raise SystemExit("NVIDIA driver below CUDA 13.0 minimum")
PY

export HF_HUB_DISABLE_TELEMETRY=1
export HF_HOME=/workspace/hf-home
export DO_NOT_TRACK=1
export VLLM_NO_USAGE_STATS=1
export VLLM_DEBUG_LOG_API_SERVER_RESPONSE=False
export VLLM_API_KEY=
download_started=$(date +%s)
python3 - "${manifest_path}" "${model_dir}" <<'PY'
import hashlib
import pathlib
import sys
import yaml
from huggingface_hub import snapshot_download

manifest = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
model = manifest["model"]
destination = pathlib.Path(sys.argv[2])
allow = [
    ".gitattributes",
    "README.md",
    "chat_template.json",
    "config.json",
    "generation_config.json",
    "params.json",
    "processor_config.json",
    "tokenizer_config.json",
    "consolidated.safetensors",
    "tekken.json",
]
snapshot_download(
    repo_id=model["repository"],
    revision=model["revision"],
    local_dir=destination,
    allow_patterns=allow,
    token=True,
)
for item in model["required_artifacts"]:
    path = destination / item["path"]
    if not path.is_file() or path.stat().st_size != item["bytes"]:
        raise SystemExit(f"artifact size mismatch: {item['path']}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != item["sha256"]:
        raise SystemExit(f"artifact digest mismatch: {item['path']}")
for name, expected in model["exact_small_files"].items():
    data = (destination / name).read_bytes()
    git_blob = hashlib.sha1(
        f"blob {len(data)}\0".encode() + data,
        usedforsecurity=False,
    ).hexdigest()
    if git_blob != expected:
        raise SystemExit(f"exact revision file mismatch: {name}")
PY
download_finished=$(date +%s)

vllm_version=$(python3 -c 'import importlib.metadata as m; print(m.version("vllm"))')
[[ "${vllm_version}" == "0.23.0" ]] || die "vllm-version"
mistral_common_version=$(python3 -c 'import importlib.metadata as m; print(m.version("mistral-common"))')

load_started=$(date +%s)
vllm serve "${model_dir}" \
  --host 127.0.0.1 \
  --port 8001 \
  --served-model-name "mistralai/Mistral-Small-3.1-24B-Instruct-2503@68faf511d618ef198fef186659617cfd2eb8e33a" \
  --tokenizer-mode mistral \
  --config-format mistral \
  --load-format mistral \
  --dtype bfloat16 \
  --model-impl vllm \
  --tensor-parallel-size 1 \
  --max-model-len 8192 \
  --generation-config vllm \
  --no-enable-log-requests \
  --disable-log-stats \
  --no-enable-prompt-embeds \
  --no-trust-remote-code \
  >"${runtime_dir}/engine-operational.log" 2>&1 &
engine_pid=$!

ready=0
for _ in $(seq 1 180); do
  if ! kill -0 "${engine_pid}" 2>/dev/null; then
    die "engine-exited"
  fi
  if curl -fsS http://127.0.0.1:8001/health >/dev/null; then
    ready=1
    break
  fi
  sleep 2
done
[[ "${ready}" -eq 1 ]] || die "engine-readiness-timeout"
load_finished=$(date +%s)

python3 - \
  "${manifest_path}" \
  "${attestation_path}" \
  "${download_started}" \
  "${download_finished}" \
  "${load_started}" \
  "${load_finished}" \
  "${mistral_common_version}" <<'PY'
import hashlib
import hmac
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import yaml

manifest = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
gpu = subprocess.check_output(
    [
        "nvidia-smi",
        "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader,nounits",
    ],
    text=True,
).strip().splitlines()
parts = [part.strip() for part in gpu[0].split(",")]
record = {
    "runtime_identity": manifest["runtime_identity"],
    "manifest_sha256": "sha256:" + hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest(),
    "image_digest": manifest["container"]["image_digest"],
    "model_repository": manifest["model"]["repository"],
    "model_revision": manifest["model"]["revision"],
    "model_weight_sha256": manifest["model"]["primary_weight"]["sha256"],
    "tokenizer_sha256": manifest["tokenizer"]["sha256"],
    "vllm_version": importlib.metadata.version("vllm"),
    "mistral_common_version": sys.argv[7],
    "python_version": platform.python_version(),
    "os_release": platform.platform(),
    "gpu_names": [parts[0]],
    "gpu_count": 1,
    "gpu_memory_mib": [int(parts[1])],
    "driver_version": parts[2],
    "cuda_runtime": manifest["compute"]["expected_container_cuda"],
    "startup_seconds": int(sys.argv[4]) - int(sys.argv[3]),
    "model_load_seconds": int(sys.argv[6]) - int(sys.argv[5]),
}
payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
record["signature"] = "hmac-sha256:" + hmac.new(
    os.environ["TREASUREBENCH_RUNTIME_ATTESTATION_KEY"].encode(),
    payload,
    hashlib.sha256,
).hexdigest()
with open(sys.argv[2], "w", encoding="utf-8") as stream:
    json.dump(record, stream, sort_keys=True, separators=(",", ":"))
    stream.write("\n")
PY
chmod 600 "${attestation_path}"

exec python3 "${proxy_path}" \
  --listen-host 0.0.0.0 \
  --listen-port 8000 \
  --upstream http://127.0.0.1:8001 \
  --attestation "${attestation_path}"
