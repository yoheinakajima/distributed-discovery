"""AO-0012 fail-closed open-weight cloud-runtime controls.

Importing this module performs no network, credential, model, GPU, or spend
operation. Live operations require a generic Agent Operations authorization.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import stat
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

from distributed_discovery.agent_ops.core import (
    authorization_challenge,
    hash_path,
    load_yaml,
    sha256_file,
    validate,
)
from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    MockAdapter,
    ModelManifest,
    Usage,
)
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.models import canonical_json
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.protocol_contract import (
    verify_protocol_contract,
)
from distributed_discovery.benchmark.agents_v1.protocol_validity import PRIMARY_CONTRASTS
from distributed_discovery.benchmark.agents_v1.protocol_validity_independent import (
    reconstruct_contrast_bounds,
    require_bound_agreement,
)
from distributed_discovery.benchmark.agents_v1.provider_outcome import (
    PROTOCOL_INVALID,
    PROTOCOL_VALID,
    PROVIDER_CONTRACT_OR_SAFETY_FAILURE,
    PROVIDER_OPERATIONAL_MISSING,
    MetricIntervalV3,
    OperationalCircuitBreaker,
    PairingClassificationV3,
    architecture_contrast_bounds_v3,
    metric_intervals_v3,
    validate_terminal_classifications_v3,
)
from distributed_discovery.benchmark.agents_v1.provider_schema import (
    compile_openai_action_schema,
)
from distributed_discovery.benchmark.agents_v1.traces import (
    build_trace,
    verify_trace_hashes,
)
from distributed_discovery.benchmark.agents_v1.verification import (
    verify_method_agreement,
    verify_task,
)

TASK_ID = "AO-0012"
ISSUE = 212
BRANCH = "agent/treasurebench-open-weight-cloud-runtime"
GATE_ID = "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION"
MODEL_REPOSITORY = "mistralai/Mistral-Small-3.1-24B-Instruct-2503"
MODEL_REVISION = "68faf511d618ef198fef186659617cfd2eb8e33a"
MODEL_NAME = f"{MODEL_REPOSITORY}@{MODEL_REVISION}"
RUNTIME_IDENTITY = "treasurebench-mistral-small-3.1-24b-bf16-vllm-0.23.0-a100-80gb-pcie-r1"
CONTAINER_DIGEST = "sha256:3a1e7f5904e1a1192a02aa0086ceaffc33985d7044c7bb25b3a43d61bdbe3ac0"
RUNTIME_DEFINITION_PATH = Path("docs/benchmark/agents-v1/open-weight-runtime-definition.yml")
MANIFEST_PATH = Path("docs/benchmark/agents-v1/open-weight-cloud-runtime-manifest.yml")
CALIBRATION_PATH = Path("docs/benchmark/agents-v1/open-weight-public-calibration.yml")
POLICY_EXTENSION_PATH = Path(
    "docs/benchmark/agents-v1/open-weight-provider-outcome-policy-v3-extension.yml"
)
FEASIBILITY_PATH = Path("reports/benchmark/treasurebench-open-weight-cloud-runtime-feasibility.yml")
DECISION_PATH = Path("reports/benchmark/treasurebench-open-weight-cloud-runtime-decision.yml")
CONTRACT_PATH = Path("tasks/treasurebench-open-weight-cloud-runtime.yml")
GATE_PATH = Path("reports/agent-ops/AO-0012-open-weight-public-calibration-owner-gate.yml")
STARTUP_PATH = Path("scripts/treasurebench_open_weight_runtime_start.sh")
PROXY_PATH = Path("scripts/treasurebench_open_weight_proxy.py")
OUTCOME_PATH = Path("reports/benchmark/treasurebench-open-weight-public-calibration-outcome.yml")
ALLOWED_ENVIRONMENT = frozenset(
    {
        "RUNPOD_API_KEY",
        "HF_TOKEN",
        "TREASUREBENCH_RUNTIME_API_KEY",
        "TREASUREBENCH_RUNTIME_ATTESTATION_KEY",
        "TREASUREBENCH_EXPECTED_IMAGE_DIGEST",
        "TREASUREBENCH_RUNTIME_MANIFEST_B64",
        "TREASUREBENCH_STARTUP_SCRIPT_B64",
        "TREASUREBENCH_PROXY_SCRIPT_B64",
    }
)
FORBIDDEN_REQUEST_KEYS = frozenset(
    {
        "answer",
        "answer_key",
        "evaluator",
        "generator",
        "generator_internals",
        "hidden_labels",
        "private_seed",
    }
)
CLASS_PROPERTIES = (
    "weights_controlled_and_checksum_verifiable",
    "exact_upstream_revision_pinned",
    "tokenizer_pinned",
    "inference_engine_and_version_pinned",
    "container_digest_pinned",
    "cuda_driver_and_hardware_recorded",
    "sampling_and_structured_output_configuration_controlled",
    "no_provider_side_model_substitution",
    "no_moving_model_alias",
    "no_hidden_provider_prompt_transformation",
    "no_provider_managed_semantic_retry",
    "prompt_output_retention_controllable",
    "raw_task_and_answer_custody_isolated",
    "benchmark_runner_can_authenticate_endpoint",
    "independently_recreatable_on_compatible_gpu",
    "cloud_infrastructure_provider_distinct_from_model_origin",
    "physical_locality",
    "full_infrastructure_independence",
)
RUNTIME_CLASSES = (
    "physical-local-owner-operated",
    "rented-raw-gpu-owner-operated",
    "managed-custom-container",
    "managed-model-endpoint",
    "third-party-routed-model-api",
)


class RuntimeConformanceError(ValueError):
    """A frozen runtime, attestation, or calibration invariant failed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeConformanceError(message)


def _canonical_digest(value: Mapping[str, object]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def load_registration(repo: Path) -> dict[str, dict[str, Any]]:
    return {
        "definition": load_yaml(repo / RUNTIME_DEFINITION_PATH),
        "manifest": load_yaml(repo / MANIFEST_PATH),
        "calibration": load_yaml(repo / CALIBRATION_PATH),
        "feasibility": load_yaml(repo / FEASIBILITY_PATH),
        "decision": load_yaml(repo / DECISION_PATH),
    }


def validate_runtime_definition(value: Mapping[str, Any]) -> None:
    _require(value.get("definition_version") == "ow-runtime-v1", "definition drift")
    _require(tuple(value.get("property_order", ())) == CLASS_PROPERTIES, "property order drift")
    classes = value.get("classes")
    if not isinstance(classes, Mapping):
        raise RuntimeConformanceError("runtime classes missing")
    _require(tuple(classes) == RUNTIME_CLASSES, "runtime class identity drift")
    allowed = {True, False, "conditional", "not_applicable"}
    for class_id in RUNTIME_CLASSES:
        item = classes[class_id]
        if not isinstance(item, Mapping):
            raise RuntimeConformanceError(f"malformed runtime class: {class_id}")
        properties = item.get("properties")
        if not isinstance(properties, Mapping):
            raise RuntimeConformanceError(f"missing properties: {class_id}")
        _require(tuple(properties) == CLASS_PROPERTIES, f"property drift: {class_id}")
        _require(set(properties.values()).issubset(allowed), f"invalid property value: {class_id}")
    selected = classes["rented-raw-gpu-owner-operated"]
    _require(selected["self_operated_open_weight_condition"] is True, "selected class rejected")
    _require(selected["properties"]["physical_locality"] is False, "cloud GPU called local")
    _require(
        selected["properties"]["full_infrastructure_independence"] is False,
        "cloud infrastructure independence overstated",
    )
    _require(
        classes["managed-model-endpoint"]["self_operated_open_weight_condition"] is False,
        "managed endpoint accepted",
    )
    _require(
        classes["third-party-routed-model-api"]["self_operated_open_weight_condition"] is False,
        "routed API accepted",
    )


def validate_runtime_manifest(value: Mapping[str, Any]) -> None:
    _require(value.get("runtime_identity") == RUNTIME_IDENTITY, "runtime identity drift")
    _require(
        value.get("runtime_class") == "rented-raw-gpu-owner-operated",
        "managed endpoint or router rejected",
    )
    compute = value.get("compute", {})
    _require(compute.get("provider") == "RunPod", "compute provider drift")
    _require(compute.get("cloud_type") == "SECURE", "RunPod cloud type drift")
    _require(compute.get("gpu_type_id") == "NVIDIA A100 80GB PCIe", "GPU type drift")
    _require(compute.get("gpu_count") == 1, "GPU count drift")
    _require(compute.get("acceptable_cuda_versions") == ["13.0"], "CUDA drift")
    _require(
        compute.get("minimum_linux_driver_version") == "580.65.06",
        "minimum CUDA driver drift",
    )
    container = value.get("container", {})
    _require(container.get("release") == "v0.23.0", "engine release drift")
    _require(container.get("image_digest") == CONTAINER_DIGEST, "container digest drift")
    _require(
        container.get("immutable_reference", "").endswith(f"@{CONTAINER_DIGEST}"),
        "moving container reference rejected",
    )
    engine = value.get("engine", {})
    _require(engine.get("version") == "0.23.0", "engine version drift")
    _require(engine.get("load_format") == "mistral", "model load format drift")
    _require(engine.get("tokenizer_mode") == "mistral", "tokenizer mode drift")
    _require(engine.get("model_implementation") == "vllm", "engine fallback drift")
    _require(engine.get("dtype") == "bfloat16", "precision drift")
    _require(engine.get("quantization") is None, "quantized weights rejected")
    _require(engine.get("hidden_fallbacks") is False, "hidden fallback rejected")
    _require(engine.get("request_logging") is False, "prompt/output logging enabled")
    model = value.get("model", {})
    _require(model.get("repository") == MODEL_REPOSITORY, "model repository drift")
    _require(model.get("revision") == MODEL_REVISION, "wrong model revision")
    _require(model.get("precision") == "BF16", "wrong model precision")
    _require(model.get("quantized") is False, "quantized weights rejected")
    _require(model.get("sharded_across_gpus") is False, "multi-GPU sharding rejected")
    tokenizer = value.get("tokenizer", {})
    _require(tokenizer.get("revision") == MODEL_REVISION, "wrong tokenizer revision")
    _require(
        tokenizer.get("sha256")
        == "c604f35d1035f534519622c0ec83fed6184978d4fdee92a5bd2a50bc05438094",
        "wrong tokenizer checksum",
    )
    endpoint = value.get("endpoint", {})
    _require(endpoint.get("authentication") == "bearer", "endpoint authentication missing")
    _require(
        endpoint.get("public_unauthenticated_access") is False,
        "endpoint without authentication rejected",
    )
    _require(endpoint.get("fallback_routes") == [], "endpoint fallback rejected")
    logging = value.get("logging_and_retention", {})
    _require(
        logging.get("public_logs_may_contain_prompt_or_output") is False,
        "prompt/output logging enabled",
    )
    _require(
        set(value.get("environment_allowlist", ())) == ALLOWED_ENVIRONMENT,
        "environment allowlist drift",
    )
    forbidden = set(value.get("forbidden_environment_names", ()))
    _require(
        {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"}.issubset(forbidden),
        "model-provider credential prohibition drift",
    )


def validate_calibration(
    value: Mapping[str, Any],
    *,
    generated_tasks: Sequence[Any] | None = None,
) -> None:
    _require(value.get("public_only") is True, "calibration is not public-only")
    _require(value.get("scientific_run") is False, "calibration became scientific")
    _require(value.get("intended_pairings") == 50, "calibration pairing count drift")
    _require(value.get("task_count") == 10, "calibration task count drift")
    _require(value.get("architecture_count") == 5, "calibration architecture count drift")
    _require(value.get("repeat_count") == 1, "calibration repeat drift")
    _require(tuple(value.get("architectures", ())) == ARCHITECTURES, "architecture drift")
    tasks = generated_tasks or generate_public_calibration()
    expected = [(task.task_id, task.family_id, task.cell_id, task.commitment) for task in tasks]
    observed = [
        (
            item["task_id"],
            item["family_id"],
            item["cell_id"],
            item["commitment"],
        )
        for item in value.get("tasks", ())
    ]
    _require(observed == expected, "public calibration task commitment drift")
    families: dict[str, int] = {}
    for _, family, _, _ in observed:
        families[family] = families.get(family, 0) + 1
    _require(set(families.values()) == {2} and len(families) == 5, "not two tasks per family")
    acceptance = value.get("acceptance", {})
    _require(
        acceptance.get("observed_protocol_validity_rate_threshold") is None,
        "post-observation validity threshold prohibited",
    )


def validate_decision(value: Mapping[str, Any]) -> None:
    allowed = {
        "open-weight-self-operated-cloud-runtime-feasible-base-registration-next",
        "open-weight-runtime-technically-feasible-budget-owner-decision-required",
        "open-weight-runtime-feasible-but-bound-informativeness-gate-required",
        "exact-bf16-runtime-infeasible-quantized-or-sharded-identity-gate-required",
        "self-operated-control-boundary-failed-managed-api-rejected",
        "calibration-integrity-failure-stop",
    }
    _require(set(value.get("permitted_decisions", ())) == allowed, "decision set drift")
    selected = value.get("selected_decision")
    _require(selected is None or selected in allowed, "unregistered final decision")
    if value.get("status") == "pending-owner-authorized-public-calibration":
        _require(selected is None and value.get("preselection") is False, "decision preselected")


def validate_registration(repo: Path) -> dict[str, object]:
    values = load_registration(repo)
    validate_runtime_definition(values["definition"])
    validate_runtime_manifest(values["manifest"])
    validate_calibration(values["calibration"])
    validate_decision(values["decision"])
    feasibility = values["feasibility"]
    _require(feasibility.get("official_sources_only") is True, "unofficial feasibility source")
    _require(
        feasibility.get("controls_and_limits", {}).get("physical_locality") is False,
        "physical locality overstated",
    )
    _require(
        feasibility.get("controls_and_limits", {}).get("full_infrastructure_independence") is False,
        "infrastructure independence overstated",
    )
    _require((repo / STARTUP_PATH).is_file(), "startup script missing")
    _require((repo / PROXY_PATH).is_file(), "endpoint proxy missing")
    extension = load_yaml(repo / POLICY_EXTENSION_PATH)
    _require(
        extension.get("composes_with") == "treasurebench-agents-v1-provider-outcome-policy-v3",
        "provider-outcome policy extension drift",
    )
    _require(
        extension.get("retry", {}).get("semantic_answer_retries") == 0,
        "semantic retry introduced",
    )
    return {
        "status": "pass-authorization-free",
        "runtime_definition_version": values["definition"]["definition_version"],
        "runtime_identity": RUNTIME_IDENTITY,
        "container_digest": CONTAINER_DIGEST,
        "model_revision": MODEL_REVISION,
        "intended_pairings": 50,
        "credential_reads": 0,
        "provider_calls": 0,
        "model_downloads": 0,
        "gpu_provisioning": 0,
        "spend_usd": "0",
    }


def attestation_signature(value: Mapping[str, object], key: str) -> str:
    unsigned = dict(value)
    unsigned.pop("signature", None)
    return (
        "hmac-sha256:"
        + hmac.new(key.encode(), canonical_json(unsigned), hashlib.sha256).hexdigest()
    )


def _numeric_version(value: object) -> tuple[int, ...]:
    parts = str(value).split(".")
    _require(bool(parts) and all(part.isdigit() for part in parts), "malformed version identity")
    return tuple(int(part) for part in parts)


def validate_attestation(
    value: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    key: str,
) -> None:
    required = set(manifest["attestation"]["required_fields"])
    _require(required.issubset(value), "malformed runtime attestation")
    signature = value.get("signature")
    _require(
        isinstance(signature, str)
        and hmac.compare_digest(signature, attestation_signature(value, key)),
        "runtime attestation authentication failed",
    )
    expected = {
        "runtime_identity": RUNTIME_IDENTITY,
        "manifest_sha256": _canonical_digest(manifest),
        "image_digest": CONTAINER_DIGEST,
        "model_repository": MODEL_REPOSITORY,
        "model_revision": MODEL_REVISION,
        "model_weight_sha256": manifest["model"]["primary_weight"]["sha256"],
        "tokenizer_sha256": manifest["tokenizer"]["sha256"],
        "vllm_version": "0.23.0",
        "gpu_names": ["NVIDIA A100 80GB PCIe"],
        "gpu_count": 1,
        "cuda_runtime": "13.0.2",
    }
    for name, expected_value in expected.items():
        _require(value.get(name) == expected_value, f"runtime attestation drift: {name}")
    _require(
        _numeric_version(value.get("driver_version"))
        >= _numeric_version(manifest["compute"]["minimum_linux_driver_version"]),
        "NVIDIA driver below CUDA 13.0 minimum",
    )
    _require(
        isinstance(value.get("gpu_memory_mib"), list)
        and len(value["gpu_memory_mib"]) == 1
        and int(value["gpu_memory_mib"][0]) >= 80000,
        "A100 memory identity mismatch",
    )


def build_chat_payload(request: AdapterRequest) -> dict[str, object]:
    schema = compile_openai_action_schema(request)
    payload: dict[str, object] = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": request.prompt.system},
            {"role": "user", "content": request.prompt.user},
        ],
        "max_tokens": request.max_output_tokens,
        "temperature": 0.15,
        "top_p": 1.0,
        "seed": int(
            hashlib.sha256(
                f"{request.prompt.task_commitment}:{request.prompt.agent_id}:"
                f"{request.round_number}:{int(request.schema_retry)}".encode()
            ).hexdigest()[:8],
            16,
        ),
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "treasurebench_action",
                "strict": True,
                "schema": schema,
            },
        },
    }
    _require(not FORBIDDEN_REQUEST_KEYS.intersection(payload), "benchmark internals leaked")
    serialized = json.dumps(payload, sort_keys=True)
    for token in ('"answer_key"', '"generator_internals"', '"private_seed"'):
        _require(token not in serialized, "answer or generator internals leaked")
    return payload


Transport = Callable[[Mapping[str, object]], Mapping[str, object]]


class OpenWeightRuntimeAdapter:
    """Repository-controlled adapter with no hidden repair or semantic retry."""

    manifest = ModelManifest(
        provider="RunPod-compute/Mistral-origin/vLLM-engine",
        model_id=MODEL_REPOSITORY,
        exact_snapshot=MODEL_NAME,
        adapter_version="open-weight-runtime-adapter-v1",
        moving_alias=False,
        live_capable=True,
    )

    def __init__(
        self,
        transport: Transport,
        *,
        runtime_attested: bool,
        enabled: bool = False,
    ) -> None:
        self._transport = transport
        self._runtime_attested = runtime_attested
        self._enabled = enabled
        self.calls: list[dict[str, object]] = []
        self.terminal_error: str | None = None

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        _require(self._enabled, "live runtime adapter disabled")
        _require(self._runtime_attested, "runtime is not attested")
        if self.terminal_error is not None:
            return AdapterResponse("", error_class=self.terminal_error)
        payload = build_chat_payload(request)
        started = time.monotonic()
        response = self._transport(payload)
        latency = time.monotonic() - started
        runtime_error = response.get("_runtime_error")
        if runtime_error is not None:
            self.terminal_error = str(runtime_error)
            return AdapterResponse(
                "",
                error_class=self.terminal_error,
                operational_metadata={"latency_seconds": latency},
            )
        _require(response.get("model") == MODEL_NAME, "exact served model mismatch")
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            return AdapterResponse(
                "",
                error_class="self-operated-invalid-provider-envelope",
                operational_metadata={"latency_seconds": latency},
            )
        message = choices[0].get("message", {})
        output = message.get("content", "") if isinstance(message, Mapping) else ""
        usage = response.get("usage", {})
        input_tokens = int(usage.get("prompt_tokens", 0)) if isinstance(usage, Mapping) else 0
        output_tokens = int(usage.get("completion_tokens", 0)) if isinstance(usage, Mapping) else 0
        record: dict[str, object] = {
            "call": len(self.calls) + 1,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_seconds": latency,
        }
        self.calls.append(record)
        return AdapterResponse(
            raw_output=str(output),
            usage=Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=Decimal("0"),
            ),
            operational_metadata=record,
        )


def build_runpod_create_request(
    repo: Path,
    *,
    endpoint_key: str,
    attestation_key: str,
    hf_token: str,
) -> dict[str, object]:
    manifest = load_yaml(repo / MANIFEST_PATH)
    validate_runtime_manifest(manifest)
    startup = (repo / STARTUP_PATH).read_bytes()
    proxy = (repo / PROXY_PATH).read_bytes()
    manifest_bytes = (repo / MANIFEST_PATH).read_bytes()
    environment = {
        "HF_TOKEN": hf_token,
        "TREASUREBENCH_RUNTIME_API_KEY": endpoint_key,
        "TREASUREBENCH_RUNTIME_ATTESTATION_KEY": attestation_key,
        "TREASUREBENCH_EXPECTED_IMAGE_DIGEST": CONTAINER_DIGEST,
        "TREASUREBENCH_RUNTIME_MANIFEST_B64": base64.b64encode(manifest_bytes).decode(),
        "TREASUREBENCH_STARTUP_SCRIPT_B64": base64.b64encode(startup).decode(),
        "TREASUREBENCH_PROXY_SCRIPT_B64": base64.b64encode(proxy).decode(),
    }
    _require(set(environment).issubset(ALLOWED_ENVIRONMENT), "deployment env drift")
    launch = (
        "printf '%s' \"$TREASUREBENCH_STARTUP_SCRIPT_B64\" | base64 --decode "
        ">/tmp/treasurebench-start.sh && chmod 700 /tmp/treasurebench-start.sh "
        "&& exec /tmp/treasurebench-start.sh"
    )
    return {
        "name": "ao0012-open-weight-public-calibration",
        "cloudType": "SECURE",
        "computeType": "GPU",
        "interruptible": False,
        "gpuTypeIds": ["NVIDIA A100 80GB PCIe"],
        "gpuTypePriority": "availability",
        "gpuCount": 1,
        "allowedCudaVersions": ["13.0"],
        "countryCodes": ["US"],
        "imageName": manifest["container"]["immutable_reference"],
        "containerDiskInGb": 50,
        "volumeInGb": 120,
        "volumeMountPath": "/workspace",
        "volumeEncrypted": True,
        "ports": ["8000/http"],
        "dockerEntrypoint": ["/bin/bash"],
        "dockerStartCmd": ["-lc", launch],
        "env": environment,
        "desiredStatus": "RUNNING",
    }


def validate_runpod_pod_identity(
    value: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
) -> Decimal:
    _require(value.get("image") == manifest["container"]["immutable_reference"], "Pod image drift")
    _require(value.get("interruptible") is False, "interruptible Pod rejected")
    _require(value.get("desiredStatus") == "RUNNING", "Pod did not enter requested state")
    _require(value.get("containerDiskInGb") == 50, "container disk drift")
    _require(value.get("volumeInGb") == 120, "volume disk drift")
    _require(value.get("volumeMountPath") == "/workspace", "volume mount drift")
    _require(value.get("volumeEncrypted") is True, "encrypted volume boundary failed")
    _require(value.get("networkVolume") is None, "network volume substitution rejected")
    gpu = value.get("gpu")
    if not isinstance(gpu, Mapping):
        raise RuntimeConformanceError("Pod GPU identity missing")
    _require(gpu.get("id") == "NVIDIA A100 80GB PCIe", "Pod GPU type drift")
    _require(gpu.get("count") == 1, "Pod GPU count drift")
    machine = value.get("machine")
    if not isinstance(machine, Mapping):
        raise RuntimeConformanceError("Pod machine identity missing")
    _require(machine.get("secureCloud") is True, "Pod is not Secure Cloud")
    _require(machine.get("gpuTypeId") == "NVIDIA A100 80GB PCIe", "machine GPU drift")
    observed_rate = value.get("costPerHr")
    _require(observed_rate is not None, "RunPod response missing exact hourly cost")
    rate = Decimal(str(observed_rate))
    _require(rate > 0 and rate * Decimal(6) < Decimal(20), "live hourly rate exceeds cap")
    return rate


def authorization_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return root / "distributed-discovery" / "agent-ops" / "authorizations" / f"{GATE_ID}.yml"


def _authorization_digest(value: Mapping[str, object]) -> str:
    unsigned = dict(value)
    unsigned.pop("authorization_digest", None)
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def validate_owner_authorization(repo: Path, value: Mapping[str, Any]) -> None:
    validate(dict(value), "owner-authorization.schema.json")
    gate = load_yaml(repo / GATE_PATH)
    validate(gate, "owner-gate.schema.json")
    _require(value.get("gate_id") == GATE_ID, "owner authorization gate mismatch")
    _require(value.get("issue") == ISSUE, "owner authorization issue mismatch")
    _require(value.get("branch") == BRANCH, "owner authorization branch mismatch")
    _require(value.get("commit") == gate["commit"], "owner authorization commit mismatch")
    _require(
        value.get("challenge") == authorization_challenge(gate),
        "owner authorization challenge mismatch",
    )
    _require(
        value.get("task_contract_sha256") == sha256_file(repo / CONTRACT_PATH),
        "owner authorization contract mismatch",
    )
    _require(value.get("tree_hashes") == gate["tree_hashes"], "owner tree hashes mismatch")
    _require(
        value.get("authorization_digest") == _authorization_digest(value),
        "owner authorization digest mismatch",
    )
    now = datetime.now(UTC)
    authorized = datetime.fromisoformat(str(value["authorized_at_utc"]).replace("Z", "+00:00"))
    expires = datetime.fromisoformat(str(value["expires_at_utc"]).replace("Z", "+00:00"))
    _require(authorized <= now < expires, "owner authorization is outside active interval")
    for relative, expected in gate["tree_hashes"].items():
        _require(hash_path(repo / relative) == expected, f"authorized tree drift: {relative}")
    current_branch = subprocess.run(
        ("git", "branch", "--show-current"),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _require(current_branch == BRANCH, "live branch mismatch")
    ancestry = subprocess.run(
        ("git", "merge-base", "--is-ancestor", str(value["commit"]), "HEAD"),
        cwd=repo,
        check=False,
        capture_output=True,
    )
    _require(ancestry.returncode == 0, "authorized execution commit is not an ancestor")


def run_offline_rehearsal(repo: Path) -> dict[str, object]:
    registration = validate_registration(repo)
    manifest = load_yaml(repo / MANIFEST_PATH)
    key = "synthetic-attestation-key"
    attestation = {
        "runtime_identity": RUNTIME_IDENTITY,
        "manifest_sha256": _canonical_digest(manifest),
        "image_digest": CONTAINER_DIGEST,
        "model_repository": MODEL_REPOSITORY,
        "model_revision": MODEL_REVISION,
        "model_weight_sha256": manifest["model"]["primary_weight"]["sha256"],
        "tokenizer_sha256": manifest["tokenizer"]["sha256"],
        "vllm_version": "0.23.0",
        "mistral_common_version": "synthetic-pinned-by-container",
        "python_version": "3.12",
        "os_release": "synthetic-linux",
        "gpu_names": ["NVIDIA A100 80GB PCIe"],
        "gpu_count": 1,
        "gpu_memory_mib": [81920],
        "driver_version": "580.65.06",
        "cuda_runtime": "13.0.2",
        "startup_seconds": 1,
        "model_load_seconds": 1,
    }
    attestation["signature"] = attestation_signature(attestation, key)
    validate_attestation(attestation, manifest=manifest, key=key)
    request = build_runpod_create_request(
        repo,
        endpoint_key="synthetic-endpoint-key",
        attestation_key=key,
        hf_token="synthetic-hf-token",
    )
    matrix = _run_synthetic_public_matrix()
    return {
        **registration,
        "synthetic_attestation": "pass",
        "synthetic_deployment_request": "pass",
        "deployment_environment_names": sorted(cast(Mapping[str, object], request["env"])),
        "synthetic_public_matrix": matrix,
        "live_action": False,
    }


def _json_request(
    url: str,
    *,
    token: str,
    method: str = "GET",
    body: Mapping[str, object] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(2_000_000)
    if not raw:
        return {}
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeConformanceError("non-object network response")
    return value


def _billing_cost(
    *,
    runpod_key: str,
    pod_id: str,
    started_at: datetime,
) -> tuple[Decimal, int]:
    query = urllib.parse.urlencode(
        {
            "bucketSize": "hour",
            "grouping": "podId",
            "podId": pod_id,
            "startTime": started_at.isoformat().replace("+00:00", "Z"),
            "endTime": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
    )
    request = urllib.request.Request(
        f"https://rest.runpod.io/v1/billing/pods?{query}",
        method="GET",
        headers={"Authorization": f"Bearer {runpod_key}"},
    )
    for _ in range(30):
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(2_000_000)
        value = json.loads(raw)
        if isinstance(value, list):
            matching = [
                item for item in value if isinstance(item, Mapping) and item.get("podId") == pod_id
            ]
            amount = sum((Decimal(str(item.get("amount", 0))) for item in matching), Decimal())
            billed_ms = sum(int(str(item.get("timeBilledMs", 0))) for item in matching)
            if amount > 0 and billed_ms > 0:
                return amount, billed_ms
        time.sleep(10)
    raise RuntimeConformanceError("RunPod billing reconciliation unavailable after teardown")


def _terminate_and_verify(*, runpod_key: str, pod_id: str) -> bool:
    _json_request(
        f"https://rest.runpod.io/v1/pods/{pod_id}",
        token=runpod_key,
        method="DELETE",
    )
    for _ in range(24):
        try:
            value = _json_request(
                f"https://rest.runpod.io/v1/pods/{pod_id}",
                token=runpod_key,
            )
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return True
            raise RuntimeConformanceError(
                f"Pod termination verification failed: HTTP {error.code}"
            ) from error
        if not value or value.get("id") != pod_id:
            return True
        time.sleep(5)
    raise RuntimeConformanceError(
        "Pod remains addressable after termination; retained volume deletion unverified"
    )


def _completion_transport(
    endpoint: str,
    endpoint_key: str,
    *,
    call_records: list[dict[str, object]],
    pairing_id: str,
    deadline: float,
    started: float,
    hourly_rate: Decimal,
    call_cap: int = 400,
) -> Transport:
    def transport(payload: Mapping[str, object]) -> Mapping[str, object]:
        last_error = "self-operated-unregistered-runtime-error"
        for attempt in (1, 2):
            if time.monotonic() >= deadline:
                raise RuntimeConformanceError("six-hour runtime cap reached")
            accrued = hourly_rate * Decimal(str(time.monotonic() - started)) / Decimal(3600)
            if accrued >= Decimal("20"):
                raise RuntimeConformanceError("hard cost cap reached")
            if len(call_records) >= call_cap:
                raise RuntimeConformanceError("inference call cap reached")
            attempt_started = time.monotonic()
            error_class: str | None = None
            status: int | None = None
            try:
                response = _json_request(
                    f"{endpoint}/v1/chat/completions",
                    token=endpoint_key,
                    method="POST",
                    body=payload,
                    timeout=180,
                )
                call_records.append(
                    {
                        "pairing_id": pairing_id,
                        "attempt": attempt,
                        "latency_seconds": time.monotonic() - attempt_started,
                        "status": 200,
                        "request_sha256": _canonical_digest(payload),
                        "response_sha256": _canonical_digest(response),
                        "input_tokens": int(
                            response.get("usage", {}).get("prompt_tokens", 0)
                            if isinstance(response.get("usage"), Mapping)
                            else 0
                        ),
                        "output_tokens": int(
                            response.get("usage", {}).get("completion_tokens", 0)
                            if isinstance(response.get("usage"), Mapping)
                            else 0
                        ),
                    }
                )
                return response
            except urllib.error.HTTPError as error:
                status = error.code
                if status in {429, 500, 502, 503, 504}:
                    error_class = f"self-operated-http-{status}"
                else:
                    raise RuntimeConformanceError(
                        f"request contract or endpoint failure: HTTP {status}"
                    ) from error
            except TimeoutError:
                error_class = "self-operated-client-timeout"
            except urllib.error.URLError:
                error_class = "self-operated-transient-transport"
            except json.JSONDecodeError:
                error_class = "self-operated-invalid-json-envelope"
            last_error = error_class or last_error
            call_records.append(
                {
                    "pairing_id": pairing_id,
                    "attempt": attempt,
                    "latency_seconds": time.monotonic() - attempt_started,
                    "status": status,
                    "error_class": last_error,
                }
            )
            if attempt == 1:
                delay = 5 if status in {429, 500, 502, 503, 504} else 2
                time.sleep(delay)
        return {"_runtime_error": last_error}

    return transport


def _operational_metrics(
    run: Any,
    *,
    exact_network_calls: int,
    exact_cost: Decimal,
) -> dict[str, object]:
    evaluation = evaluate_run(run[0], run[1])
    values = dict(evaluation.__dict__)
    values["calls"] = exact_network_calls
    values["retry_count"] = max(0, exact_network_calls - len(run[1].turns))
    values["cost_usd"] = exact_cost
    return values


def _verify_public_bounds(
    classifications: Sequence[PairingClassificationV3],
    pending: Sequence[tuple[Any, Any, int]],
    *,
    reconciled_cost_usd: Decimal,
) -> int:
    _require(len(classifications) == 50, "bound input classification count mismatch")
    _require(len(pending) == 50, "bound input pairing count mismatch")
    pairing_cost = reconciled_cost_usd / Decimal(50)
    intervals: list[MetricIntervalV3] = []
    for classification, (task, run, network_calls) in zip(
        classifications,
        pending,
        strict=True,
    ):
        metrics = _operational_metrics(
            (task, run),
            exact_network_calls=network_calls,
            exact_cost=pairing_cost,
        )
        intervals.extend(
            metric_intervals_v3(
                task=task,
                classification=classification,
                exact_metrics=metrics,
            )
        )
    primary_bounds = architecture_contrast_bounds_v3(intervals)
    independent_bounds = reconstruct_contrast_bounds(
        [item.serializable() for item in intervals],
        PRIMARY_CONTRASTS,
    )
    require_bound_agreement(
        [item.serializable() for item in primary_bounds],
        independent_bounds,
    )
    return len(primary_bounds)


def _run_synthetic_public_matrix() -> dict[str, object]:
    tasks = generate_public_calibration()
    classifications: list[PairingClassificationV3] = []
    pending: list[tuple[Any, Any, int]] = []
    method_a_b_agree = True
    method_c_complete = True
    breaker = OperationalCircuitBreaker()
    calls = 0
    for sequence, (task, architecture) in enumerate(
        ((task, architecture) for task in tasks for architecture in ARCHITECTURES),
        start=1,
    ):
        errors = verify_task(task)
        _require(not errors, f"public theoretical baseline failed: {errors}")
        pairing_id = f"OWCAL-SYNTHETIC-{sequence:03d}"
        adapter = MockAdapter()
        run = run_architecture(task, architecture, adapter)
        calls += adapter.calls
        trace = build_trace(run)
        _require(verify_trace_hashes(trace.raw), "synthetic trace hash mismatch")
        method_c_errors = tuple(
            sorted(set(tuple(verify_protocol_contract(task, run).errors) + run.protocol_errors))
        )
        classification = PairingClassificationV3(
            pairing_id=pairing_id,
            provider="offline",
            model="deterministic-mock@deterministic-mock-v1",
            task_commitment=task.commitment,
            architecture_id=architecture,
            trace_id=str(trace.raw["trace_hash"]),
            status=PROTOCOL_INVALID if method_c_errors else PROTOCOL_VALID,
            provider_response_completed=True,
            protocol_compliance="fail" if method_c_errors else "pass",
            method_c_errors=method_c_errors,
        )
        evaluation = evaluate_run(task, run)
        if verify_method_agreement(evaluation.__dict__, task, run):
            method_a_b_agree = False
        classifications.append(classification)
        pending.append((task, run, adapter.calls))
        snapshot = breaker.observe(classification, sequence=sequence)
        _require(not snapshot.fired, "synthetic circuit breaker fired")
    validate_terminal_classifications_v3(
        [f"OWCAL-SYNTHETIC-{index:03d}" for index in range(1, 51)],
        classifications,
    )
    bound_count = _verify_public_bounds(
        classifications,
        pending,
        reconciled_cost_usd=Decimal(),
    )
    counts = Counter(item.status for item in classifications)
    _require(calls <= 400, "synthetic matrix exceeds registered call cap")
    return {
        "intended_pairings": 50,
        "terminal_pairings": len(classifications),
        "protocol_valid_count": counts[PROTOCOL_VALID],
        "protocol_invalid_count": counts[PROTOCOL_INVALID],
        "provider_operational_missing_count": counts[PROVIDER_OPERATIONAL_MISSING],
        "runtime_failure_count": counts[PROVIDER_CONTRACT_OR_SAFETY_FAILURE],
        "calls": calls,
        "method_a_b_agree": method_a_b_agree,
        "method_c_classifies_every_completed_response": method_c_complete,
        "primary_and_independent_bounds_agree": True,
        "bound_count": bound_count,
        "circuit_breaker": breaker.snapshot().serializable(),
    }


def _run_public_matrix(
    endpoint: str,
    endpoint_key: str,
    *,
    deadline: float,
    started: float,
    hourly_rate: Decimal,
) -> dict[str, object]:
    tasks = generate_public_calibration()
    for task in tasks:
        errors = verify_task(task)
        _require(not errors, f"public theoretical baseline failed: {errors}")
    call_records: list[dict[str, object]] = []
    classifications: list[PairingClassificationV3] = []
    pending: list[tuple[Any, Any, int]] = []
    method_a_b_agree = True
    method_c_complete = True
    breaker = OperationalCircuitBreaker()
    for sequence, (task, architecture) in enumerate(
        ((task, architecture) for task in tasks for architecture in ARCHITECTURES),
        start=1,
    ):
        pairing_id = f"OWCAL-{sequence:03d}"
        before = len(call_records)
        adapter = OpenWeightRuntimeAdapter(
            _completion_transport(
                endpoint,
                endpoint_key,
                call_records=call_records,
                pairing_id=pairing_id,
                deadline=deadline,
                started=started,
                hourly_rate=hourly_rate,
            ),
            runtime_attested=True,
            enabled=True,
        )
        run = run_architecture(task, architecture, adapter)
        network_calls = len(call_records) - before
        trace = build_trace(run)
        _require(verify_trace_hashes(trace.raw), "ephemeral trace hash mismatch")
        _require(
            all(record.get("pairing_id") == pairing_id for record in call_records[before:]),
            "call ledger pairing identity mismatch",
        )
        missing = adapter.terminal_error is not None
        method_c_errors = () if missing else tuple(verify_protocol_contract(task, run).errors)
        method_c_errors = tuple(sorted(set(method_c_errors + run.protocol_errors)))
        if missing:
            classification = PairingClassificationV3(
                pairing_id=pairing_id,
                provider="RunPod-raw-compute",
                model=MODEL_NAME,
                task_commitment=task.commitment,
                architecture_id=architecture,
                trace_id=str(trace.raw["trace_hash"]),
                status=PROVIDER_OPERATIONAL_MISSING,
                provider_response_completed=False,
                protocol_compliance="not-applicable",
                method_c_errors=(),
                provider_error_class=adapter.terminal_error,
            )
        else:
            status = PROTOCOL_INVALID if method_c_errors else PROTOCOL_VALID
            classification = PairingClassificationV3(
                pairing_id=pairing_id,
                provider="RunPod-raw-compute",
                model=MODEL_NAME,
                task_commitment=task.commitment,
                architecture_id=architecture,
                trace_id=str(trace.raw["trace_hash"]),
                status=status,
                provider_response_completed=True,
                protocol_compliance="fail" if method_c_errors else "pass",
                method_c_errors=method_c_errors,
            )
            evaluation = evaluate_run(task, run)
            if verify_method_agreement(evaluation.__dict__, task, run):
                method_a_b_agree = False
        classifications.append(classification)
        pending.append((task, run, network_calls))
        snapshot = breaker.observe(classification, sequence=sequence)
        if snapshot.fired:
            raise RuntimeConformanceError(f"operational circuit breaker fired: {snapshot.reason}")
    _require(len(classifications) == 50, "not all 50 pairings terminalized")
    validate_terminal_classifications_v3(
        [f"OWCAL-{index:03d}" for index in range(1, 51)],
        classifications,
    )
    counts = Counter(item.status for item in classifications)
    return {
        "intended_pairings": 50,
        "terminal_pairings": len(classifications),
        "protocol_valid_count": counts[PROTOCOL_VALID],
        "protocol_invalid_count": counts[PROTOCOL_INVALID],
        "provider_operational_missing_count": counts[PROVIDER_OPERATIONAL_MISSING],
        "runtime_failure_count": counts[PROVIDER_CONTRACT_OR_SAFETY_FAILURE],
        "calls": len(call_records),
        "input_tokens": sum(int(str(item.get("input_tokens", 0))) for item in call_records),
        "output_tokens": sum(int(str(item.get("output_tokens", 0))) for item in call_records),
        "method_a_b_agree": method_a_b_agree,
        "method_c_classifies_every_completed_response": method_c_complete,
        "circuit_breaker": breaker.snapshot().serializable(),
        "_classifications": classifications,
        "_pending": pending,
    }


def run_live_calibration(repo: Path) -> dict[str, object]:
    """Provision only after the generic gate; always terminate the created Pod.

    The normal live path is intentionally unavailable until the committed gate
    exists and its mode-0600 authorization validates. Calibration orchestration
    is invoked only after the runtime attestation passes.
    """

    validate_registration(repo)
    auth_path = authorization_path()
    _require(auth_path.is_file(), "generic owner authorization required")
    info = auth_path.lstat()
    _require(stat.S_ISREG(info.st_mode), "authorization must be a regular file")
    _require(stat.S_IMODE(info.st_mode) == 0o600, "authorization mode must be 0600")
    validate_owner_authorization(repo, load_yaml(auth_path))
    runpod_key = os.environ.get("RUNPOD_API_KEY", "")
    hf_token = os.environ.get("HF_TOKEN", "")
    _require(bool(runpod_key), "RUNPOD_API_KEY required after authorization")
    _require(bool(hf_token), "HF_TOKEN required after authorization")
    endpoint_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    attestation_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    payload = build_runpod_create_request(
        repo,
        endpoint_key=endpoint_key,
        attestation_key=attestation_key,
        hf_token=hf_token,
    )
    pod_id: str | None = None
    started = time.monotonic()
    started_at = datetime.now(UTC)
    pod_hourly_rate: Decimal | None = None
    matrix: dict[str, object] | None = None
    attestation: dict[str, Any] | None = None
    teardown_verified = False
    try:
        pod = _json_request(
            "https://rest.runpod.io/v1/pods",
            token=runpod_key,
            method="POST",
            body=payload,
        )
        pod_id = str(pod.get("id", ""))
        _require(bool(pod_id), "RunPod create response missing Pod ID")
        manifest = load_yaml(repo / MANIFEST_PATH)
        pod_hourly_rate = validate_runpod_pod_identity(pod, manifest=manifest)
        endpoint = f"https://{pod_id}-8000.proxy.runpod.net"
        deadline = started + 21600
        while time.monotonic() - started < 3600:
            if time.monotonic() >= deadline:
                raise RuntimeConformanceError("six-hour runtime cap reached")
            try:
                attestation = _json_request(
                    f"{endpoint}/runtime-attestation",
                    token=endpoint_key,
                    timeout=10,
                )
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                time.sleep(10)
        _require(attestation is not None, "runtime attestation timeout")
        if attestation is None:
            raise RuntimeConformanceError("runtime attestation timeout")
        validate_attestation(attestation, manifest=manifest, key=attestation_key)
        matrix = _run_public_matrix(
            endpoint,
            endpoint_key,
            deadline=deadline,
            started=started,
            hourly_rate=pod_hourly_rate,
        )
    finally:
        if pod_id:
            try:
                teardown_verified = _terminate_and_verify(
                    runpod_key=runpod_key,
                    pod_id=pod_id,
                )
            except Exception as error:
                raise RuntimeConformanceError(
                    f"Pod termination verification required: {type(error).__name__}"
                ) from error
    _require(
        matrix is not None and attestation is not None and pod_hourly_rate is not None,
        "calibration did not complete",
    )
    if matrix is None or attestation is None or pod_hourly_rate is None:
        raise RuntimeConformanceError("calibration did not complete")
    if pod_id is None:
        raise RuntimeConformanceError("calibration Pod identity missing")
    total_seconds = Decimal(str(time.monotonic() - started))
    exact_cost, billed_milliseconds = _billing_cost(
        runpod_key=runpod_key,
        pod_id=pod_id,
        started_at=started_at,
    )
    _require(exact_cost <= Decimal("20"), "hard cost cap exceeded")
    _require(total_seconds <= Decimal(21600), "six-hour runtime cap exceeded")
    classifications = cast(
        list[PairingClassificationV3],
        matrix.pop("_classifications"),
    )
    pending = cast(
        list[tuple[Any, Any, int]],
        matrix.pop("_pending"),
    )
    matrix["bound_count"] = _verify_public_bounds(
        classifications,
        pending,
        reconciled_cost_usd=exact_cost,
    )
    matrix["primary_and_independent_bounds_agree"] = True
    input_tokens = int(str(matrix["input_tokens"]))
    output_tokens = int(str(matrix["output_tokens"]))
    generation_seconds = max(
        Decimal("0.000001"),
        total_seconds
        - Decimal(str(attestation["startup_seconds"]))
        - Decimal(str(attestation["model_load_seconds"])),
    )
    outcome = {
        "schema_version": "treasurebench-open-weight-public-calibration-outcome-v1",
        "status": "public-calibration-complete-decision-pending",
        "authority_task": TASK_ID,
        "scientific_run": False,
        "runtime_identity": RUNTIME_IDENTITY,
        "model_identity": MODEL_NAME,
        "engine_identity": "vLLM-0.23.0",
        "hardware_identity": "one-NVIDIA-A100-80GB-PCIe",
        "startup_seconds": attestation["startup_seconds"],
        "model_load_seconds": attestation["model_load_seconds"],
        "total_wall_clock_seconds": str(total_seconds),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "throughput_tokens_per_second": str(
            Decimal(input_tokens + output_tokens) / generation_seconds
        ),
        "gpu_memory_observations_mib": attestation["gpu_memory_mib"],
        "calls": matrix["calls"],
        "failures": int(str(matrix["provider_operational_missing_count"]))
        + int(str(matrix["runtime_failure_count"])),
        "protocol_valid_count": matrix["protocol_valid_count"],
        "protocol_invalid_count": matrix["protocol_invalid_count"],
        "provider_operational_missing_count": matrix["provider_operational_missing_count"],
        "runtime_failure_count": matrix["runtime_failure_count"],
        "exact_cost_usd": str(exact_cost),
        "runpod_billed_milliseconds": billed_milliseconds,
        "all_50_pairings_completed": matrix["terminal_pairings"] == 50,
        "methods_and_bounds_agree": bool(matrix["method_a_b_agree"])
        and bool(matrix["method_c_classifies_every_completed_response"])
        and bool(matrix["primary_and_independent_bounds_agree"]),
        "projected_open_weight_arm_runtime_and_cost": {
            "pairings": 3000,
            "wall_clock_seconds": str(total_seconds * Decimal(60)),
            "compute_cost_usd": str(exact_cost * Decimal(60)),
        },
        "projected_complete_base_campaign_runtime_and_cost": {
            "pairings": 9000,
            "wall_clock_seconds_if_same_runtime": str(total_seconds * Decimal(180)),
            "compute_cost_usd_if_same_runtime": str(exact_cost * Decimal(180)),
            "interpretation": (
                "mechanical all-pairing reference only; proprietary-arm pricing "
                "is not supplied by this calibration"
            ),
        },
        "teardown_verified": teardown_verified,
        "performance_values_published": False,
        "decision": None,
    }
    import yaml

    (repo / OUTCOME_PATH).write_text(
        yaml.safe_dump(outcome, sort_keys=False),
        encoding="utf-8",
    )
    return outcome


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--rehearsal", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.live:
        result = run_live_calibration(args.repo)
    elif args.rehearsal:
        result = run_offline_rehearsal(args.repo)
    else:
        result = validate_registration(args.repo)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
