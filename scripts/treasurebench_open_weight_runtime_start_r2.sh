#!/usr/bin/env bash
set -euo pipefail
umask 077

die() {
  printf 'runtime-startup-failed:%s\n' "$1" >&2
  exit 1
}

required=(
  RUNPOD_API_KEY
  RUNPOD_POD_ID
  HF_TOKEN
  TREASUREBENCH_RUNTIME_API_KEY
  TREASUREBENCH_RUNTIME_ATTESTATION_KEY
  TREASUREBENCH_EXPECTED_IMAGE_DIGEST
  TREASUREBENCH_RUNTIME_MANIFEST_B64
  TREASUREBENCH_PROXY_SCRIPT_B64
)
for name in "${required[@]}"; do
  [[ -n "${!name:-}" ]] || die "missing-${name}"
done

runtime_dir=/workspace/treasurebench-runtime-r2
model_dir=/workspace/model
manifest_path="${runtime_dir}/manifest.yml"
proxy_path="${runtime_dir}/proxy.py"
bearer_path="${runtime_dir}/endpoint-bearer"
attestation_path="${runtime_dir}/runtime-attestation.json"
artifact_path="${runtime_dir}/artifact-measurements.json"
peak_path="${runtime_dir}/peak-memory-mib"
mkdir -p "${runtime_dir}" "${model_dir}"
chmod 700 "${runtime_dir}" "${model_dir}"
printf '%s' "${TREASUREBENCH_RUNTIME_MANIFEST_B64}" | base64 --decode >"${manifest_path}"
printf '%s' "${TREASUREBENCH_PROXY_SCRIPT_B64}" | base64 --decode >"${proxy_path}"
chmod 600 "${manifest_path}" "${proxy_path}"
unset TREASUREBENCH_RUNTIME_MANIFEST_B64 TREASUREBENCH_PROXY_SCRIPT_B64
unset TREASUREBENCH_STARTUP_SCRIPT_B64

# Verify the disposable volume before any secret is written to it.
pod_json=$(
  curl -fsS \
    -H "Authorization: Bearer ${RUNPOD_API_KEY}" \
    "https://rest.runpod.io/v1/pods/${RUNPOD_POD_ID}"
) || die "pod-self-query"
printf '%s' "${pod_json}" | python3 -c '
import json
import sys
pod = json.load(sys.stdin)
if pod.get("id") != sys.argv[1]:
    raise SystemExit("Pod self-identity mismatch")
if pod.get("volumeEncrypted") is not True:
    raise SystemExit("encrypted disposable Pod volume required")
if pod.get("networkVolume") not in (None, {}):
    raise SystemExit("network volume substitution rejected")
' "${RUNPOD_POD_ID}"
pod_json=
unset RUNPOD_API_KEY RUNPOD_POD_ID
printf '%s' "${TREASUREBENCH_RUNTIME_API_KEY}" >"${bearer_path}"
chmod 600 "${bearer_path}"
unset TREASUREBENCH_RUNTIME_API_KEY

python3 - "${manifest_path}" "${TREASUREBENCH_EXPECTED_IMAGE_DIGEST}" <<'PY'
import sys
import yaml

manifest = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
if manifest["schema_version"] != "treasurebench-open-weight-cloud-runtime-manifest-r2-v1":
    raise SystemExit("R2 manifest required")
expected = manifest["container"]["image_digest"]
if expected != sys.argv[2]:
    raise SystemExit("container digest mismatch")
if manifest["container"]["immutable_reference"].split("@", 1)[1] != expected:
    raise SystemExit("container immutable reference mismatch")
if manifest["model"]["quantized"] or manifest["model"]["precision"] != "BF16":
    raise SystemExit("quantized or non-BF16 model rejected")
if manifest["compute"]["gpu_count"] != 1:
    raise SystemExit("GPU count mismatch")
if manifest["engine"]["tensor_parallel_size"] != 1:
    raise SystemExit("sharding rejected")
PY
unset TREASUREBENCH_EXPECTED_IMAGE_DIGEST

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
download_started=$(date +%s)
python3 - "${manifest_path}" "${model_dir}" "${artifact_path}" <<'PY'
import hashlib
import json
import os
import pathlib
import sys
import yaml
from huggingface_hub import snapshot_download

manifest = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
model = manifest["model"]
destination = pathlib.Path(sys.argv[2])
token = os.environ.get("HF_TOKEN")
if not token:
    raise SystemExit("HF token missing")
allow = [
    ".gitattributes", "README.md", "chat_template.json", "config.json",
    "generation_config.json", "params.json", "processor_config.json",
    "tokenizer_config.json", "consolidated.safetensors", "tekken.json",
]
snapshot_download(
    repo_id=model["repository"],
    revision=model["revision"],
    local_dir=destination,
    allow_patterns=allow,
    token=token,
)
measurements = {}
for item in model["required_artifacts"]:
    path = destination / item["path"]
    if not path.is_file() or path.stat().st_size != item["bytes"]:
        raise SystemExit(f"artifact size mismatch: {item['path']}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    measured = digest.hexdigest()
    if measured != item["sha256"]:
        raise SystemExit(f"artifact digest mismatch: {item['path']}")
    measurements[item["path"]] = measured
for name, expected in model["exact_small_files"].items():
    data = (destination / name).read_bytes()
    git_blob = hashlib.sha1(
        f"blob {len(data)}\0".encode() + data,
        usedforsecurity=False,
    ).hexdigest()
    if git_blob != expected:
        raise SystemExit(f"exact revision file mismatch: {name}")
pathlib.Path(sys.argv[3]).write_text(
    json.dumps(measurements, sort_keys=True), encoding="utf-8"
)
PY
download_finished=$(date +%s)
unset HF_TOKEN

vllm_version=$(python3 -c 'import importlib.metadata as m; print(m.version("vllm"))')
[[ "${vllm_version}" == "0.23.0" ]] || die "vllm-version"
mistral_common_version=$(python3 -c 'import importlib.metadata as m; print(m.version("mistral-common"))')
python3 - "${mistral_common_version}" <<'PY'
import sys
from packaging.version import Version
if Version(sys.argv[1]) < Version("1.11.3"):
    raise SystemExit("mistral-common below registered minimum")
PY

# The provider-injected Pod key and attestation key never enter either child.
unset RUNPOD_API_KEY
export VLLM_NO_USAGE_STATS=1
export VLLM_DEBUG_LOG_API_SERVER_RESPONSE=False
load_started=$(date +%s)
env -i   PATH="${PATH}"   HOME=/root   HF_HOME=/workspace/hf-home   DO_NOT_TRACK=1   VLLM_NO_USAGE_STATS=1   VLLM_DEBUG_LOG_API_SERVER_RESPONSE=False   vllm serve "${model_dir}"     --host 127.0.0.1     --port 8001     --served-model-name "mistralai/Mistral-Small-3.1-24B-Instruct-2503@68faf511d618ef198fef186659617cfd2eb8e33a"     --tokenizer-mode mistral     --config-format mistral     --load-format mistral     --dtype bfloat16     --model-impl vllm     --tensor-parallel-size 1     --max-model-len 8192     --generation-config vllm     --no-enable-log-requests     --disable-log-stats     --no-enable-prompt-embeds     --no-trust-remote-code     >"${runtime_dir}/engine-operational.log" 2>&1 &
engine_pid=$!

ready=0
for _ in $(seq 1 180); do
  kill -0 "${engine_pid}" 2>/dev/null || die "engine-exited"
  if curl -fsS http://127.0.0.1:8001/health >/dev/null; then
    ready=1
    break
  fi
  sleep 2
done
[[ "${ready}" -eq 1 ]] || die "engine-readiness-timeout"
load_finished=$(date +%s)

# Public operational memory sampler; it never observes prompts or outputs.
(
  peak=0
  while kill -0 "${engine_pid}" 2>/dev/null; do
    current=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | tr -d '[:space:]')
    [[ "${current}" =~ ^[0-9]+$ ]] || exit 1
    (( current > peak )) && peak=${current}
    printf '%s\n' "${peak}" >"${peak_path}.tmp"
    chmod 600 "${peak_path}.tmp"
    mv "${peak_path}.tmp" "${peak_path}"
    sleep 1
  done
) &
memory_sampler_pid=$!

python3 -   "${manifest_path}" "${attestation_path}" "${artifact_path}"   "${download_started}" "${download_finished}" "${load_started}" "${load_finished}"   "${mistral_common_version}" "${peak_path}" <<'PY'
import ctypes
import hashlib
import hmac
import importlib.metadata
import json
import os
import platform
import pathlib
import subprocess
import sys
import time
import torch
import yaml

manifest = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
artifacts = json.load(open(sys.argv[3], encoding="utf-8"))
gpu = subprocess.check_output(
    ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
     "--format=csv,noheader,nounits"], text=True
).strip().splitlines()
parts = [part.strip() for part in gpu[0].split(",")]
runtime = ctypes.CDLL("libcudart.so")
version = ctypes.c_int()
if runtime.cudaRuntimeGetVersion(ctypes.byref(version)) != 0:
    raise SystemExit("CUDA runtime measurement failed")
cuda_runtime = f"{version.value // 1000}.{(version.value % 1000) // 10}"
toolkit = subprocess.check_output(
    ["nvcc", "--version"], text=True
) if pathlib.Path("/usr/local/cuda/bin/nvcc").exists() else ""
if "release 13.0" not in toolkit:
    raise SystemExit("CUDA toolkit measurement mismatch")
for _ in range(30):
    try:
        peak = int(open(sys.argv[9], encoding="utf-8").read().strip())
        break
    except (FileNotFoundError, ValueError):
        time.sleep(1)
else:
    raise SystemExit("peak memory sampler unavailable")
record = {
    "evidence_class": "measured-runtime-r2",
    "runtime_identity": manifest["runtime_identity"],
    "manifest_sha256": "sha256:" + hashlib.sha256(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest(),
    "image_digest": manifest["container"]["image_digest"],
    "model_repository": manifest["model"]["repository"],
    "model_revision": manifest["model"]["revision"],
    "model_weight_sha256": artifacts["consolidated.safetensors"],
    "tokenizer_sha256": artifacts["tekken.json"],
    "vllm_version": importlib.metadata.version("vllm"),
    "mistral_common_version": sys.argv[8],
    "python_version": platform.python_version(),
    "os_release": platform.platform(),
    "gpu_names": [parts[0]],
    "gpu_count": torch.cuda.device_count(),
    "gpu_memory_mib": [int(parts[1])],
    "peak_gpu_memory_mib": peak,
    "driver_version": parts[2],
    "requested_cuda_compatibility_class": manifest["compute"]["allowed_cuda_versions"][0],
    "measured_container_cuda_toolkit": "13.0",
    "measured_cuda_runtime": cuda_runtime,
    "pytorch_cuda_runtime": torch.version.cuda,
    "quantization": None,
    "tensor_parallel_size": 1,
    "startup_seconds": int(sys.argv[5]) - int(sys.argv[4]),
    "model_load_seconds": int(sys.argv[7]) - int(sys.argv[6]),
}
payload = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
key = os.environ.get("TREASUREBENCH_RUNTIME_ATTESTATION_KEY")
if not key:
    raise SystemExit("attestation key missing")
record["signature"] = "hmac-sha256:" + hmac.new(
    key.encode(), payload, hashlib.sha256
).hexdigest()
with open(sys.argv[2], "w", encoding="utf-8") as stream:
    json.dump(record, stream, sort_keys=True, separators=(",", ":"))
    stream.write("\n")
PY
chmod 600 "${attestation_path}"
unset TREASUREBENCH_RUNTIME_ATTESTATION_KEY
unset HF_HUB_DISABLE_TELEMETRY HF_HOME DO_NOT_TRACK
unset VLLM_NO_USAGE_STATS VLLM_DEBUG_LOG_API_SERVER_RESPONSE

exec env -i PATH="${PATH}" HOME=/root python3 "${proxy_path}"   --listen-host 0.0.0.0   --listen-port 8000   --upstream http://127.0.0.1:8001   --attestation "${attestation_path}"   --bearer-file "${bearer_path}"   --peak-memory-file "${peak_path}"
