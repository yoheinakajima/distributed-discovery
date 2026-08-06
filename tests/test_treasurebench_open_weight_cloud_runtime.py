from __future__ import annotations

import copy
import json
import re
import urllib.error
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from distributed_discovery.agent_ops.core import load_yaml
from distributed_discovery.benchmark.agents_v1 import open_weight_cloud_runtime as runtime
from distributed_discovery.benchmark.agents_v1.adapters import AdapterRequest
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime import (
    CALIBRATION_PATH,
    CONTAINER_DIGEST,
    MANIFEST_PATH,
    MODEL_NAME,
    MODEL_REPOSITORY,
    MODEL_REVISION,
    RUNTIME_IDENTITY,
    RuntimeConformanceError,
    attestation_signature,
    build_chat_payload,
    build_runpod_create_request,
    run_offline_rehearsal,
    validate_attestation,
    validate_calibration,
    validate_registration,
    validate_runpod_pod_identity,
    validate_runtime_definition,
    validate_runtime_manifest,
)
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt

ROOT = Path(__file__).resolve().parents[1]


def manifest() -> dict[str, object]:
    return load_yaml(ROOT / MANIFEST_PATH)


def valid_attestation(value: dict[str, object], key: str = "test-key") -> dict[str, object]:
    result: dict[str, object] = {
        "runtime_identity": RUNTIME_IDENTITY,
        "manifest_sha256": "sha256:"
        + __import__("hashlib")
        .sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())
        .hexdigest(),
        "image_digest": CONTAINER_DIGEST,
        "model_repository": MODEL_REPOSITORY,
        "model_revision": MODEL_REVISION,
        "model_weight_sha256": value["model"]["primary_weight"]["sha256"],  # type: ignore[index]
        "tokenizer_sha256": value["tokenizer"]["sha256"],  # type: ignore[index]
        "vllm_version": "0.23.0",
        "mistral_common_version": "1.11.3",
        "python_version": "3.12.11",
        "os_release": "Linux synthetic",
        "gpu_names": ["NVIDIA A100 80GB PCIe"],
        "gpu_count": 1,
        "gpu_memory_mib": [81920],
        "driver_version": "580.65.06",
        "cuda_runtime": "13.0.2",
        "startup_seconds": 42,
        "model_load_seconds": 180,
    }
    result["signature"] = attestation_signature(result, key)
    return result


def assert_manifest_rejects(path: tuple[str, ...], value: object) -> None:
    corrupted = copy.deepcopy(manifest())
    target: dict[str, object] = corrupted
    for part in path[:-1]:
        target = target[part]  # type: ignore[assignment]
    target[path[-1]] = value
    with pytest.raises(RuntimeConformanceError):
        validate_runtime_manifest(corrupted)


def test_registration_and_rehearsal_are_authorization_free() -> None:
    registration = validate_registration(ROOT)
    rehearsal = run_offline_rehearsal(ROOT)
    assert registration["status"] == "pass-authorization-free"
    assert registration["provider_calls"] == 0
    assert registration["model_downloads"] == 0
    assert registration["gpu_provisioning"] == 0
    matrix = rehearsal["synthetic_public_matrix"]
    assert matrix["terminal_pairings"] == 50
    assert matrix["provider_operational_missing_count"] == 0
    assert matrix["runtime_failure_count"] == 0
    assert matrix["method_a_b_agree"] is True
    assert matrix["primary_and_independent_bounds_agree"] is True
    assert matrix["calls"] <= 400
    assert rehearsal["live_action"] is False


def test_definition_separates_locality_and_infrastructure_independence() -> None:
    definition = load_yaml(ROOT / "docs/benchmark/agents-v1/open-weight-runtime-definition.yml")
    validate_runtime_definition(definition)
    selected = definition["classes"]["rented-raw-gpu-owner-operated"]["properties"]
    assert selected["physical_locality"] is False
    assert selected["full_infrastructure_independence"] is False
    assert (
        definition["classes"]["managed-model-endpoint"]["self_operated_open_weight_condition"]
        is False
    )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("model", "revision"), "moving-main"),
        (("tokenizer", "sha256"), "0" * 64),
        (("container", "image_digest"), "sha256:" + "0" * 64),
        (("compute", "gpu_type_id"), "NVIDIA L40S"),
        (("compute", "gpu_count"), 2),
        (("model", "quantized"), True),
        (("runtime_class",), "managed-model-endpoint"),
        (("runtime_class",), "third-party-routed-model-api"),
        (("engine", "hidden_fallbacks"), True),
        (("endpoint", "authentication"), "none"),
        (("endpoint", "public_unauthenticated_access"), True),
        (
            ("logging_and_retention", "public_logs_may_contain_prompt_or_output"),
            True,
        ),
        (("engine", "version"), "0.23.1"),
        (("engine", "load_format"), "bitsandbytes"),
        (("model", "precision"), "INT4"),
    ],
)
def test_manifest_corruptions_fail_closed(path: tuple[str, ...], value: object) -> None:
    assert_manifest_rejects(path, value)


def test_malformed_or_drifted_attestation_rejects() -> None:
    value = manifest()
    attestation = valid_attestation(value)
    validate_attestation(attestation, manifest=value, key="test-key")
    missing = copy.deepcopy(attestation)
    missing.pop("signature")
    with pytest.raises(RuntimeConformanceError):
        validate_attestation(missing, manifest=value, key="test-key")
    drifted = copy.deepcopy(attestation)
    drifted["gpu_names"] = ["NVIDIA L40S"]
    drifted["signature"] = attestation_signature(drifted, "test-key")
    with pytest.raises(RuntimeConformanceError):
        validate_attestation(drifted, manifest=value, key="test-key")
    old_driver = copy.deepcopy(attestation)
    old_driver["driver_version"] = "575.57.08"
    old_driver["signature"] = attestation_signature(old_driver, "test-key")
    with pytest.raises(RuntimeConformanceError):
        validate_attestation(old_driver, manifest=value, key="test-key")


def test_endpoint_payload_has_protocol_schema_but_no_answers_or_generator_internals() -> None:
    task = generate_public_calibration()[0]
    agent = sorted(task.capabilities)[0]
    prompt = compile_prompt(
        task,
        agent,
        architecture_id="isolated-private-agents",
        final_required=True,
    )
    request = AdapterRequest(
        prompt=prompt,
        manifest=None,  # type: ignore[arg-type]
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        final_required=True,
    )
    payload = build_chat_payload(request)
    serialized = json.dumps(payload, sort_keys=True)
    assert payload["model"] == MODEL_NAME
    assert '"answer_key"' not in serialized
    assert '"generator_internals"' not in serialized
    assert '"private_seed"' not in serialized
    assert payload["response_format"]["json_schema"]["strict"] is True  # type: ignore[index]


def test_deployment_request_is_exact_and_credential_names_are_allowlisted() -> None:
    request = build_runpod_create_request(
        ROOT,
        endpoint_key="synthetic-endpoint",
        attestation_key="synthetic-attestation",
        hf_token="synthetic-hf",
    )
    assert request["gpuTypeIds"] == ["NVIDIA A100 80GB PCIe"]
    assert request["gpuCount"] == 1
    assert request["allowedCudaVersions"] == ["13.0"]
    assert request["imageName"].endswith(f"@{CONTAINER_DIGEST}")
    assert request["volumeEncrypted"] is True
    assert set(request["env"]) == {
        "HF_TOKEN",
        "TREASUREBENCH_RUNTIME_API_KEY",
        "TREASUREBENCH_RUNTIME_ATTESTATION_KEY",
        "TREASUREBENCH_EXPECTED_IMAGE_DIGEST",
        "TREASUREBENCH_RUNTIME_MANIFEST_B64",
        "TREASUREBENCH_STARTUP_SCRIPT_B64",
        "TREASUREBENCH_PROXY_SCRIPT_B64",
    }


def test_runpod_returned_identity_rejects_gpu_or_storage_substitution() -> None:
    value = manifest()
    pod = {
        "image": value["container"]["immutable_reference"],
        "interruptible": False,
        "desiredStatus": "RUNNING",
        "containerDiskInGb": 50,
        "volumeInGb": 120,
        "volumeMountPath": "/workspace",
        "volumeEncrypted": True,
        "networkVolume": None,
        "gpu": {"id": "NVIDIA A100 80GB PCIe", "count": 1},
        "machine": {
            "secureCloud": True,
            "gpuTypeId": "NVIDIA A100 80GB PCIe",
        },
        "costPerHr": "1.39",
    }
    assert validate_runpod_pod_identity(pod, manifest=value) == Decimal("1.39")
    corrupted = copy.deepcopy(pod)
    corrupted["gpu"]["id"] = "NVIDIA L40S"
    with pytest.raises(RuntimeConformanceError):
        validate_runpod_pod_identity(corrupted, manifest=value)


def test_exact_billing_reconciliation_sums_only_the_created_pod(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Response:
        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self, _limit: int) -> bytes:
            return json.dumps(
                [
                    {"podId": "pod-exact", "amount": "4.125", "timeBilledMs": 10_000},
                    {"podId": "pod-exact", "amount": "0.375", "timeBilledMs": 1_000},
                    {"podId": "another-pod", "amount": "99", "timeBilledMs": 99_000},
                ]
            ).encode()

    monkeypatch.setattr(runtime.urllib.request, "urlopen", lambda *_args, **_kwargs: Response())
    amount, billed_ms = runtime._billing_cost(
        runpod_key="synthetic-runpod-key",
        pod_id="pod-exact",
        started_at=datetime(2026, 7, 31, tzinfo=UTC),
    )
    assert amount == Decimal("4.500")
    assert billed_ms == 11_000


def test_teardown_requires_deleted_pod_to_be_unaddressable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[tuple[str, str]] = []

    def fake_request(
        url: str,
        *,
        token: str,
        method: str = "GET",
        body: Any = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        del token, body, timeout
        requests.append((method, url))
        if method == "DELETE":
            return {}
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)

    monkeypatch.setattr(runtime, "_json_request", fake_request)
    assert runtime._terminate_and_verify(
        runpod_key="synthetic-runpod-key",
        pod_id="pod-exact",
    )
    assert requests == [
        ("DELETE", "https://rest.runpod.io/v1/pods/pod-exact"),
        ("GET", "https://rest.runpod.io/v1/pods/pod-exact"),
    ]


def test_public_calibration_is_exactly_two_tasks_per_family_and_fifty_pairings() -> None:
    calibration = load_yaml(ROOT / CALIBRATION_PATH)
    validate_calibration(calibration)
    assert calibration["task_count"] * calibration["architecture_count"] == 50
    assert calibration["acceptance"]["observed_protocol_validity_rate_threshold"] is None
    assert "architecture_performance" in calibration["prohibited_report_fields"]


def test_corruption_registry_covers_required_failures() -> None:
    registry = load_yaml(
        ROOT / "docs/benchmark/agents-v1/open-weight-cloud-runtime-corruptions.yml"
    )
    identifiers = {item["id"] for item in registry["corruptions"]}
    assert {
        "wrong-model-revision",
        "wrong-tokenizer",
        "wrong-container-digest",
        "wrong-gpu-type",
        "wrong-gpu-count",
        "quantized-weights",
        "managed-endpoint",
        "routed-api",
        "hidden-fallback",
        "no-endpoint-authentication",
        "prompt-output-logging",
        "engine-version-drift",
        "malformed-runtime-attestation",
        "answer-or-generator-leak",
        "credential-in-git-or-log",
    } == identifiers


def test_no_credential_value_or_private_material_in_public_package() -> None:
    paths = [
        ROOT / MANIFEST_PATH,
        ROOT / CALIBRATION_PATH,
        ROOT / "scripts/treasurebench_open_weight_runtime_start.sh",
        ROOT / "scripts/treasurebench_open_weight_proxy.py",
        ROOT / "src/distributed_discovery/benchmark/agents_v1/open_weight_cloud_runtime.py",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "sk-" not in text
    assert re.search(r"\bhf_[A-Za-z0-9]{20,}\b", text) is None
    assert "BEGIN PRIVATE KEY" not in text
    assert "OPENAI_API_KEY=" not in text
    assert "ANTHROPIC_API_KEY=" not in text
