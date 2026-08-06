from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from distributed_discovery.agent_ops.core import load_yaml
from distributed_discovery.benchmark.agents_v1.live_inputs import load_credentials
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime import (
    CONTAINER_DIGEST,
    MODEL_REVISION,
    RUNTIME_IDENTITY,
    RuntimeConformanceError,
    _canonical_digest,
    attestation_signature,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r2 import (
    AUTO_TERMINATION_CONTROL,
    CREDENTIAL_NAMES,
    FAILURE_CLASSES,
    BillingRecord,
    Lifecycle,
    MutableSecret,
    ResourceRef,
    _redacted_outcome,
    build_pod_spec,
    build_template_spec,
    finalize_lifecycle,
    namespace_for,
    operational_projections,
    reconcile_ambiguous_create,
    require_remote_conflict_free,
    run_offline_rehearsal,
    validate_measured_attestation,
)

REPO = Path(__file__).resolve().parents[1]


class FakePlane:
    def __init__(self) -> None:
        self.pods: list[dict[str, Any]] = []
        self.templates: list[dict[str, Any]] = []
        self.secrets: list[dict[str, Any]] = []
        self.fail_delete_pod = False
        self.keep_pod = False
        self.fail_delete_template = False
        self.keep_template = False
        self.fail_delete_secret = False
        self.keep_secret = False
        self.fail_billing = False
        self.deleted_pods: list[str] = []

    def list_pods(self) -> list[dict[str, Any]]:
        return list(self.pods)

    def list_templates(self) -> list[dict[str, Any]]:
        return list(self.templates)

    def list_secrets(self) -> list[dict[str, Any]]:
        return list(self.secrets)

    def create_secret(self, name: str, value: str) -> ResourceRef:
        assert value
        item = {"id": f"secret-{len(self.secrets)}", "name": name}
        self.secrets.append(item)
        return ResourceRef(str(item["id"]), name)

    def delete_secret(self, resource: ResourceRef) -> None:
        if self.fail_delete_secret:
            raise RuntimeError("secret delete failed")
        if not self.keep_secret:
            self.secrets = [item for item in self.secrets if item["id"] != resource.id]

    def create_template(self, spec: dict[str, object]) -> ResourceRef:
        item = {"id": "template-1", "name": spec["name"]}
        self.templates.append(item)
        return ResourceRef("template-1", str(spec["name"]))

    def delete_template(self, resource: ResourceRef) -> None:
        if self.fail_delete_template:
            raise RuntimeError("template delete failed")
        if not self.keep_template:
            self.templates = [item for item in self.templates if item["id"] != resource.id]

    def create_pod(self, spec: dict[str, object]) -> dict[str, Any]:
        item = {
            "id": "pod-1",
            "name": spec["name"],
            "createdAt": datetime.now(UTC).isoformat(),
        }
        self.pods.append(item)
        return item

    def delete_pod(self, pod_id: str) -> None:
        self.deleted_pods.append(pod_id)
        if self.fail_delete_pod:
            raise RuntimeError("pod delete failed")
        if not self.keep_pod:
            self.pods = [item for item in self.pods if item["id"] != pod_id]

    def get_pod(self, pod_id: str) -> dict[str, Any] | None:
        return next((item for item in self.pods if item["id"] == pod_id), None)

    def billing(self, pod_id: str, started_at: datetime) -> BillingRecord:
        if self.fail_billing:
            raise RuntimeError("billing missing")
        return BillingRecord(Decimal("0.695"), 1_800_000, Decimal("120"), 1)


def lifecycle() -> Lifecycle:
    value = Lifecycle(
        namespace="ao0012-owcal-r2-0123456789abcdef",
        authorization_digest="sha256:" + "0" * 64,
        started_at=datetime.now(UTC),
        pod_id="pod-1",
        possible_pod=True,
        template=ResourceRef("template-1", "ao0012-owcal-r2-0123456789abcdef"),
        secrets=[
            ResourceRef("secret-1", "ao0012-owcal-r2-0123456789abcdef-hf"),
            ResourceRef("secret-2", "ao0012-owcal-r2-0123456789abcdef-endpoint"),
            ResourceRef("secret-3", "ao0012-owcal-r2-0123456789abcdef-attestation"),
        ],
    )
    return value


def test_exact_repository_local_credential_subset_and_clearing(tmp_path: Path) -> None:
    credential_file = tmp_path / ".env.txt"
    credential_file.write_text(
        "RUNPOD_API_KEY=fake-runpod\nHF_TOKEN=fake-hf\nOPENAI_API_KEY=must-remain-inaccessible\n",
        encoding="utf-8",
    )
    credential_file.chmod(0o600)
    credentials = load_credentials(
        credential_file,
        explicit_live_mode=True,
        requested_names=CREDENTIAL_NAMES,
    )
    assert credentials.get_secret("RUNPOD_API_KEY") == "fake-runpod"
    assert credentials.get_secret("HF_TOKEN") == "fake-hf"
    with pytest.raises(PermissionError):
        credentials.get_secret("OPENAI_API_KEY")
    assert "must-remain-inaccessible" not in repr(credentials)
    credentials.clear()
    assert credentials.get_secret("RUNPOD_API_KEY") is None


@pytest.mark.parametrize("condition", ["missing", "unsafe", "symlink"])
def test_credential_metadata_refusals(tmp_path: Path, condition: str) -> None:
    path = tmp_path / ".env.txt"
    if condition != "missing":
        path.write_text("RUNPOD_API_KEY=fake\nHF_TOKEN=fake\n", encoding="utf-8")
        path.chmod(0o600)
    if condition == "unsafe":
        path.chmod(0o644)
    if condition == "symlink":
        target = tmp_path / "real"
        path.rename(target)
        path.symlink_to(target)
    with pytest.raises((FileNotFoundError, PermissionError)):
        load_credentials(path, explicit_live_mode=True, requested_names=CREDENTIAL_NAMES)


def test_mutable_secret_clears_on_success_and_error_style_cleanup() -> None:
    value = MutableSecret("synthetic")
    assert value.reveal() == "synthetic"
    value.clear()
    assert value.cleared
    with pytest.raises(RuntimeConformanceError):
        value.reveal()


def test_template_contains_only_secret_references() -> None:
    spec = build_template_spec(REPO, "ao0012-owcal-r2-0123456789abcdef")
    env = spec["env"]
    for name in (
        "HF_TOKEN",
        "TREASUREBENCH_RUNTIME_API_KEY",
        "TREASUREBENCH_RUNTIME_ATTESTATION_KEY",
    ):
        assert env[name].startswith("{{ RUNPOD_SECRET_")
    serialized = str(spec)
    assert "fake-hf" not in serialized
    assert "fake-runpod" not in serialized
    assert spec["isPublic"] is False
    assert spec["isServerless"] is False


def test_pod_spec_has_exact_identity_and_server_side_kill_switch() -> None:
    now = datetime(2026, 8, 1, tzinfo=UTC)
    spec = build_pod_spec("namespace", "template-1", now)
    assert spec["cloudType"] == "SECURE"
    assert spec["gpuTypeId"] == "NVIDIA A100 80GB PCIe"
    assert spec["gpuCount"] == 1
    assert spec["terminateAfter"] == "2026-08-01T06:00:00Z"
    assert spec["templateId"] == "template-1"
    assert AUTO_TERMINATION_CONTROL == "podFindAndDeployOnDemand.terminateAfter"


@pytest.mark.parametrize("kind", ["pod", "template", "secret"])
def test_duplicate_namespace_refused(kind: str) -> None:
    plane = FakePlane()
    namespace = "ao0012-owcal-r2-0123456789abcdef"
    if kind == "pod":
        plane.pods.append({"id": "x", "name": namespace})
    elif kind == "template":
        plane.templates.append({"id": "x", "name": namespace})
    else:
        plane.secrets.append({"id": "x", "name": f"{namespace}-hf"})
    with pytest.raises(RuntimeConformanceError):
        require_remote_conflict_free(plane, namespace)


def test_ambiguous_create_unique_match_is_reconciled() -> None:
    plane = FakePlane()
    state = lifecycle()
    state.pod_id = None
    plane.pods = [
        {
            "id": "pod-unique",
            "name": state.namespace,
            "createdAt": state.started_at.isoformat(),
        }
    ]
    assert reconcile_ambiguous_create(plane, state) == "pod-unique"
    assert state.pod_id == "pod-unique"


def test_ambiguous_create_multiple_match_refused() -> None:
    plane = FakePlane()
    state = lifecycle()
    state.pod_id = None
    plane.pods = [
        {"id": "one", "name": state.namespace, "createdAt": state.started_at.isoformat()},
        {"id": "two", "name": state.namespace, "createdAt": state.started_at.isoformat()},
    ]
    with pytest.raises(RuntimeConformanceError, match="multiple exact namespace"):
        reconcile_ambiguous_create(plane, state)


def test_success_finalizer_deletes_everything_and_reconciles_bill() -> None:
    plane = FakePlane()
    state = lifecycle()
    plane.pods = [{"id": "pod-1", "name": state.namespace}]
    plane.templates = [{"id": "template-1", "name": state.namespace}]
    plane.secrets = [{"id": item.id, "name": item.name} for item in state.secrets]
    result = finalize_lifecycle(plane, state, poll=lambda _: None)
    assert result.exact
    assert state.pod_unaddressable is True
    assert state.volume_deleted is True
    assert state.template_deleted is True
    assert state.secrets_deleted is True
    assert state.billing == BillingRecord(Decimal("0.695"), 1_800_000, Decimal("120"), 1)


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        ("pod", "teardown-ambiguity"),
        ("template", "secret-template-deletion-ambiguity"),
        ("secret", "secret-template-deletion-ambiguity"),
        ("billing", "billing-reconciliation-unavailable"),
    ],
)
def test_finalizer_ambiguity_is_a_hard_stop(failure: str, expected: str) -> None:
    plane = FakePlane()
    state = lifecycle()
    plane.pods = [{"id": "pod-1", "name": state.namespace}]
    plane.templates = [{"id": "template-1", "name": state.namespace}]
    plane.secrets = [{"id": item.id, "name": item.name} for item in state.secrets]
    if failure == "pod":
        plane.keep_pod = True
    elif failure == "template":
        plane.keep_template = True
    elif failure == "secret":
        plane.keep_secret = True
    else:
        plane.fail_billing = True
    result = finalize_lifecycle(plane, state, poll=lambda _: None)
    assert not result.exact
    assert result.hard_stop_class == expected
    outcome = _redacted_outcome(
        state,
        failure_class=result.hard_stop_class,
        finalization=result,
        matrix=None,
        projections=None,
    )
    schema = load_yaml(
        REPO / "docs/benchmark/agents-v1/open-weight-public-calibration-outcome-r2.schema.json"
    )
    Draft202012Validator(schema).validate(outcome)
    assert outcome["merge_or_issue_close_allowed"] is False
    assert outcome["decision"] != (
        "open-weight-self-operated-cloud-runtime-feasible-base-registration-next"
    )


def measured_attestation() -> tuple[dict[str, Any], dict[str, Any], str]:
    manifest = load_yaml(
        REPO / "docs/benchmark/agents-v1/open-weight-cloud-runtime-manifest-r2.yml"
    )
    key = "synthetic-attestation-key"
    value: dict[str, Any] = {
        "evidence_class": "measured-runtime-r2",
        "runtime_identity": RUNTIME_IDENTITY,
        "manifest_sha256": _canonical_digest(manifest),
        "image_digest": CONTAINER_DIGEST,
        "model_revision": MODEL_REVISION,
        "model_weight_sha256": manifest["model"]["primary_weight"]["sha256"],
        "tokenizer_sha256": manifest["tokenizer"]["sha256"],
        "vllm_version": "0.23.0",
        "mistral_common_version": "1.11.3",
        "gpu_names": ["NVIDIA A100 80GB PCIe"],
        "gpu_count": 1,
        "gpu_memory_mib": [81920],
        "driver_version": "580.65.06",
        "requested_cuda_compatibility_class": "13.0",
        "measured_container_cuda_toolkit": "13.0",
        "pytorch_cuda_runtime": "13.0",
        "quantization": None,
        "tensor_parallel_size": 1,
        "startup_seconds": 100,
        "model_load_seconds": 200,
        "peak_gpu_memory_mib": 70000,
    }
    value["signature"] = attestation_signature(value, key)
    return value, manifest, key


def test_measured_attestation_passes_and_echo_is_rejected() -> None:
    value, manifest, key = measured_attestation()
    validate_measured_attestation(value, manifest=manifest, key=key)
    value["evidence_class"] = "manifest-echo"
    value["signature"] = attestation_signature(
        {k: v for k, v in value.items() if k != "signature"}, key
    )
    with pytest.raises(RuntimeConformanceError, match="manifest echo"):
        validate_measured_attestation(value, manifest=manifest, key=key)


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("mistral_common_version", "1.11.2"),
        ("pytorch_cuda_runtime", "12.8"),
        ("measured_container_cuda_toolkit", "12.8"),
        ("quantization", "awq"),
        ("tensor_parallel_size", 2),
        ("gpu_count", 2),
    ],
)
def test_measured_attestation_drift_rejected(field: str, bad: object) -> None:
    value, manifest, key = measured_attestation()
    value[field] = bad
    value["signature"] = attestation_signature(
        {k: v for k, v in value.items() if k != "signature"}, key
    )
    with pytest.raises(RuntimeConformanceError):
        validate_measured_attestation(value, manifest=manifest, key=key)


def test_in_pod_children_receive_no_credentials() -> None:
    startup = (REPO / "scripts/treasurebench_open_weight_runtime_start_r2.sh").read_text()
    assert startup.index("volumeEncrypted") < startup.index('TREASUREBENCH_RUNTIME_API_KEY}" >"')
    assert "unset HF_TOKEN" in startup
    assert "unset RUNPOD_API_KEY" in startup
    assert "unset TREASUREBENCH_RUNTIME_ATTESTATION_KEY" in startup
    assert startup.count("env -i") >= 2
    assert "--bearer-file" in startup
    proxy = (REPO / "scripts/treasurebench_open_weight_proxy_r2.py").read_text()
    assert "scrub_environment()" in proxy
    assert "FORBIDDEN_ENV_NAMES.intersection(os.environ)" in proxy


def test_operational_projection_separates_fixed_and_marginal() -> None:
    value = operational_projections(
        fixed_seconds=Decimal("1200"),
        generation_seconds=Decimal("600"),
        exact_cost=Decimal("0.695"),
        tokens=6000,
        calls=294,
        retries=0,
        peak_gpu_memory_mib=70000,
    )
    assert value["observed_tokens_per_second"] == "10"
    assert value["open_weight_arm_continuous_runtime"]["seconds"] == "37200"
    assert value["open_weight_arm_repeated_batch_upper_bound"]["seconds"] == "108000"
    assert (
        "OpenAI and Anthropic costs"
        in (value["complete_9000_pairing_mechanical_reference"]["interpretation"])
    )


def test_complete_50_pairing_rehearsal_is_preserved() -> None:
    value = run_offline_rehearsal(REPO)
    matrix = value["synthetic_public_matrix"]
    assert matrix["intended_pairings"] == 50
    assert matrix["terminal_pairings"] == 50
    assert matrix["calls"] == 294
    assert matrix["protocol_valid_count"] == 50
    assert matrix["bound_count"] == 72
    assert matrix["primary_and_independent_bounds_agree"] is True
    assert value["live_action"] is False


def test_public_files_contain_no_synthetic_secret_or_raw_payload() -> None:
    forbidden = (
        "fake-runpod",
        "fake-hf",
        "must-remain-inaccessible",
        "Authorization: Bearer synthetic",
        '"prompt":',
        '"raw_output":',
    )
    paths = [
        REPO / "docs/benchmark/agents-v1/open-weight-cloud-runtime-manifest-r2.yml",
        REPO / "src/distributed_discovery/benchmark/agents_v1/open_weight_cloud_runtime_r2.py",
        REPO / "scripts/treasurebench_open_weight_runtime_start_r2.sh",
        REPO / "scripts/treasurebench_open_weight_proxy_r2.py",
    ]
    joined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for fragment in forbidden:
        assert fragment not in joined


def test_failure_class_set_contains_all_registered_bounded_failures() -> None:
    assert len(FAILURE_CLASSES) == 15
    assert "teardown-ambiguity" in FAILURE_CLASSES
    assert "billing-reconciliation-unavailable" in FAILURE_CLASSES


def test_namespace_is_authorization_bound() -> None:
    one = namespace_for("sha256:" + "1" * 64)
    two = namespace_for("sha256:" + "2" * 64)
    assert one != two
    assert one.startswith("ao0012-owcal-r2-")


def test_synthetic_tests_do_not_read_repository_env(monkeypatch: pytest.MonkeyPatch) -> None:
    real_open = Path.open

    def guarded(path: Path, *args: object, **kwargs: object):
        if path.name == ".env.txt":
            raise AssertionError("real credential source accessed")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    result = run_offline_rehearsal(REPO)
    assert result["live_action"] is False


@pytest.mark.parametrize(
    "failure_class",
    [
        "container-image-identity-mismatch",
        "driver-cuda-runtime-attestation-mismatch",
        "artifact-download-or-checksum-failure",
        "engine-startup-readiness-failure",
        "endpoint-authentication-control-failure",
        "calibration-contract-safety-failure",
        "circuit-breaker-or-runtime-cap-failure",
        "calibration-integrity-failure",
    ],
)
def test_every_post_create_failure_still_tears_down_and_bills(
    failure_class: str,
) -> None:
    plane = FakePlane()
    state = lifecycle()
    plane.pods = [{"id": "pod-1", "name": state.namespace}]
    plane.templates = [{"id": "template-1", "name": state.namespace}]
    plane.secrets = [{"id": item.id, "name": item.name} for item in state.secrets]
    result = finalize_lifecycle(plane, state, poll=lambda _: None)
    outcome = _redacted_outcome(
        state,
        failure_class=failure_class,
        finalization=result,
        matrix=None,
        projections=None,
    )
    assert result.exact
    assert state.pod_unaddressable is True
    assert state.volume_deleted is True
    assert state.template_deleted is True
    assert state.secrets_deleted is True
    assert state.billing is not None
    assert outcome["merge_or_issue_close_allowed"] is False
    assert outcome["decision"] != (
        "open-weight-self-operated-cloud-runtime-feasible-base-registration-next"
    )
