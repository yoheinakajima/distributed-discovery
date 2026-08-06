from __future__ import annotations

import io
import json
import runpy
import urllib.error
import urllib.request
from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from urllib.parse import quote

import pytest

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
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    BRANCH,
    CREDENTIAL_NAMES,
    FAILURE_CLASSES,
    GATE_ID,
    MAX_GPU_SECONDS,
    ORPHAN_CONTROL,
    POD_CREATE_INPUT_FIELDS,
    BillingRecord,
    Finalization,
    Lifecycle,
    MutableSecret,
    ResourceRef,
    RunPodControlPlane,
    _redacted_outcome,
    _validate_live_github_and_git,
    build_pod_spec,
    build_template_spec,
    finalize_lifecycle,
    namespace_for,
    reconcile_ambiguous_create,
    require_remote_conflict_free,
    run_offline_rehearsal,
    validate_created_pod,
    validate_measured_attestation,
)

REPO = Path(__file__).resolve().parents[1]
SYNTHETIC_KEY = "rpa_+/=?&% synthetic space"
NAMESPACE = "ao0012-owcal-r4-0123456789abcdef"
WATCHDOG = runpy.run_path(str(REPO / "scripts/treasurebench_open_weight_watchdog_r4.py"))
DEADLINE_SECONDS = cast(int, WATCHDOG["DEADLINE_SECONDS"])
MutableKey = cast(Any, WATCHDOG["MutableKey"])
PodDeleteWatchdog = cast(Any, WATCHDOG["PodDeleteWatchdog"])


class FakeResponse:
    def __init__(self, value: object) -> None:
        self.payload = json.dumps(value).encode()

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, _: int) -> bytes:
        return self.payload


class RecordingOpener:
    def __init__(self, responses: list[object]) -> None:
        self.responses = list(responses)
        self.requests: list[urllib.request.Request] = []

    def __call__(self, request: urllib.request.Request, *, timeout: int) -> FakeResponse:
        assert timeout in (20, 30)
        self.requests.append(request)
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return FakeResponse(value)


def body(request: urllib.request.Request) -> dict[str, Any]:
    assert isinstance(request.data, bytes)
    value = json.loads(request.data)
    assert isinstance(value, dict)
    return value


def observed_pod(*, pod_id: str = "pod-1") -> dict[str, Any]:
    manifest = load_yaml(
        REPO / "docs/benchmark/agents-v1/open-weight-cloud-runtime-manifest-r4.yml"
    )
    return {
        "id": pod_id,
        "name": NAMESPACE,
        "templateId": "template-1",
        "image": manifest["container"]["immutable_reference"],
        "cloudType": "SECURE",
        "computeType": "GPU",
        "gpuCount": 1,
        "gpu": {"displayName": "NVIDIA A100 80GB PCIe"},
        "machine": {"secureCloud": True},
        "containerDiskInGb": 50,
        "volumeInGb": 120,
        "volumeMountPath": "/workspace",
        "volumeEncrypted": True,
        "networkVolume": None,
        "networkVolumeId": None,
        "interruptible": False,
        "supportPublicIp": False,
        "ports": ["8000/http"],
        "costPerHr": "1.39",
    }


class FakePlane:
    def __init__(self) -> None:
        self.pods: list[dict[str, Any]] = []
        self.templates: list[dict[str, Any]] = []
        self.secrets: list[dict[str, Any]] = []
        self.keep_pod = False
        self.keep_template = False
        self.keep_secret = False
        self.fail_billing = False
        self.create_calls = 0

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
        if not self.keep_secret:
            self.secrets = [item for item in self.secrets if item["id"] != resource.id]

    def create_template(self, spec: Mapping[str, object]) -> ResourceRef:
        item = {"id": "template-1", "name": spec["name"]}
        self.templates.append(item)
        return ResourceRef("template-1", str(spec["name"]))

    def delete_template(self, resource: ResourceRef) -> None:
        if not self.keep_template:
            self.templates = [item for item in self.templates if item["id"] != resource.id]

    def create_pod(self, spec: Mapping[str, object]) -> dict[str, Any]:
        self.create_calls += 1
        item = observed_pod()
        item["createdAt"] = datetime.now(UTC).isoformat()
        self.pods.append(item)
        return item

    def delete_pod(self, pod_id: str) -> None:
        if not self.keep_pod:
            self.pods = [item for item in self.pods if item["id"] != pod_id]

    def get_pod(self, pod_id: str) -> dict[str, Any] | None:
        return next((item for item in self.pods if item["id"] == pod_id), None)

    def billing(self, pod_id: str, started_at: datetime) -> BillingRecord:
        if self.fail_billing:
            raise RuntimeError("synthetic billing unavailable")
        return BillingRecord(Decimal("0.695"), 1_800_000, Decimal("120"), 1)


def lifecycle() -> Lifecycle:
    return Lifecycle(
        namespace=NAMESPACE,
        authorization_digest="sha256:" + "0" * 64,
        started_at=datetime.now(UTC),
        pod_id="pod-1",
        possible_pod=True,
        template=ResourceRef("template-1", NAMESPACE),
        secrets=[
            ResourceRef("secret-1", f"{NAMESPACE}-hf"),
            ResourceRef("secret-2", f"{NAMESPACE}-endpoint"),
            ResourceRef("secret-3", f"{NAMESPACE}-attestation"),
        ],
    )


def test_public_preflight_uses_no_gh_and_accepts_exact_public_state() -> None:
    head = "a" * 40
    calls: list[tuple[str, ...]] = []

    def runner(args: tuple[str, ...], **_: object) -> SimpleNamespace:
        calls.append(args)
        assert args[0] == "git"
        if args[1:3] == ("status", "--porcelain"):
            return SimpleNamespace(stdout="")
        if args[1:3] == ("rev-parse", "HEAD"):
            return SimpleNamespace(stdout=head + "\n")
        if args[1:3] == ("ls-remote", "origin"):
            return SimpleNamespace(stdout=f"{head}\trefs/heads/{BRANCH}\n")
        raise AssertionError(args)

    opener = RecordingOpener(
        [
            {"number": 212, "state": "open", "ignored": "not-retained"},
            {
                "number": 213,
                "state": "open",
                "draft": True,
                "base": {"ref": "main", "ignored": "x"},
                "head": {"ref": BRANCH, "sha": head, "ignored": "y"},
            },
        ]
    )
    _validate_live_github_and_git(
        REPO,
        {"pull_request": {"number": 213}},
        urlopen=opener,
        runner=runner,
    )
    assert all(item != "gh" for args in calls for item in args)
    assert [request.full_url for request in opener.requests] == [
        "https://api.github.com/repos/yoheinakajima/distributed-discovery/issues/212",
        "https://api.github.com/repos/yoheinakajima/distributed-discovery/pulls/213",
    ]
    assert all(
        request.get_header("User-agent") == "distributed-discovery-ao0012-r4-preflight"
        for request in opener.requests
    )


@pytest.mark.parametrize("mutation", ["issue", "pull", "base", "head", "remote"])
def test_public_preflight_mismatch_fails_before_credential_ingress(mutation: str) -> None:
    head = "b" * 40

    def runner(args: tuple[str, ...], **_: object) -> SimpleNamespace:
        if args[1] == "status":
            return SimpleNamespace(stdout="")
        if args[1] == "rev-parse":
            return SimpleNamespace(stdout=head + "\n")
        remote = ("c" * 40) if mutation == "remote" else head
        return SimpleNamespace(stdout=f"{remote}\trefs/heads/{BRANCH}\n")

    issue = {"number": 999 if mutation == "issue" else 212, "state": "open"}
    pull = {
        "number": 213,
        "state": "closed" if mutation == "pull" else "open",
        "draft": True,
        "base": {"ref": "wrong" if mutation == "base" else "main"},
        "head": {"ref": BRANCH, "sha": ("d" * 40) if mutation == "head" else head},
    }
    with pytest.raises(RuntimeConformanceError):
        _validate_live_github_and_git(
            REPO,
            {"pull_request": {"number": 213}},
            urlopen=RecordingOpener([issue, pull]),
            runner=runner,
        )


def test_public_github_error_surface_drops_raw_body() -> None:
    headers = Message()
    headers["Authorization"] = "Bearer synthetic-github-secret"
    error = urllib.error.HTTPError(
        "https://api.github.com/private?token=synthetic",
        403,
        "raw provider sentinel",
        headers,
        io.BytesIO(b"raw body sentinel"),
    )

    def runner(args: tuple[str, ...], **_: object) -> SimpleNamespace:
        return SimpleNamespace(stdout="" if args[1] == "status" else "a" * 40 + "\n")

    with pytest.raises(RuntimeConformanceError) as caught:
        _validate_live_github_and_git(
            REPO,
            {"pull_request": {"number": 213}},
            urlopen=RecordingOpener([error]),
            runner=runner,
        )
    assert str(caught.value) == "public GitHub issue-read HTTP 403"
    assert "sentinel" not in repr(caught.value)
    assert "token=" not in repr(caught.value)


def test_graphql_query_auth_and_rest_bearer_auth_are_disjoint() -> None:
    opener = RecordingOpener(
        [
            {"data": {"myself": {"pods": [], "podTemplates": [], "secrets": []}}},
            {"data": {"secretCreate": {"id": "secret-1", "name": "name"}}},
            {"id": "template-1", "name": "template"},
            observed_pod(),
        ]
    )
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=opener)
    plane.list_pods()
    plane.create_secret("name", "synthetic-value")
    plane.create_template({"name": "template"})
    plane.create_pod(build_pod_spec(NAMESPACE, "template-1"))
    graphql_url = f"https://api.runpod.io/graphql?api_key={quote(SYNTHETIC_KEY, safe='')}"
    for request in opener.requests[:2]:
        assert request.full_url == graphql_url
        assert request.get_header("Authorization") is None
    for request in opener.requests[2:]:
        assert "api_key=" not in request.full_url
        assert request.get_header("Authorization") == f"Bearer {SYNTHETIC_KEY}"
    assert opener.requests[-1].full_url == "https://rest.runpod.io/v1/pods"
    assert body(opener.requests[-1]) == build_pod_spec(NAMESPACE, "template-1")
    assert "podFindAndDeployOnDemand" not in "".join(
        str(body(request)) for request in opener.requests if request.data
    )
    plane.clear()


def test_exact_encrypted_rest_pod_create_field_set() -> None:
    spec = build_pod_spec(NAMESPACE, "template-1")
    assert frozenset(spec) == POD_CREATE_INPUT_FIELDS
    assert spec == {
        "name": NAMESPACE,
        "cloudType": "SECURE",
        "computeType": "GPU",
        "gpuCount": 1,
        "gpuTypeIds": ["NVIDIA A100 80GB PCIe"],
        "gpuTypePriority": "availability",
        "templateId": "template-1",
        "containerDiskInGb": 50,
        "volumeInGb": 120,
        "volumeMountPath": "/workspace",
        "volumeEncrypted": True,
        "countryCodes": ["US"],
        "ports": ["8000/http"],
        "allowedCudaVersions": ["13.0"],
        "supportPublicIp": False,
    }
    serialized = json.dumps(spec, sort_keys=True)
    for forbidden in ("minCudaVersion", "terminateAfter", "networkVolumeId", "HF_TOKEN"):
        assert forbidden not in serialized


@pytest.mark.parametrize("field", ["minCudaVersion", "terminateAfter", "networkVolumeId", "env"])
def test_pod_create_rejects_unsupported_field(field: str) -> None:
    spec = build_pod_spec(NAMESPACE, "template-1")
    spec[field] = "synthetic"
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=RecordingOpener([]))
    with pytest.raises(RuntimeConformanceError, match="field set rejected"):
        plane.create_pod(spec)
    plane.clear()


@pytest.mark.parametrize(
    ("field", "bad"),
    [("volumeEncrypted", False), ("allowedCudaVersions", ["12.8"])],
)
def test_pod_create_rejects_encryption_or_cuda_drift(field: str, bad: object) -> None:
    spec = build_pod_spec(NAMESPACE, "template-1")
    spec[field] = bad
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=RecordingOpener([]))
    with pytest.raises(RuntimeConformanceError, match="CUDA field rejected"):
        plane.create_pod(spec)
    plane.clear()


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("volumeEncrypted", False),
        ("networkVolumeId", "network-1"),
        ("gpuCount", 2),
        ("image", "moving:latest"),
        ("supportPublicIp", True),
    ],
)
def test_create_response_and_fresh_get_contract_drift_rejected(field: str, bad: object) -> None:
    manifest = load_yaml(
        REPO / "docs/benchmark/agents-v1/open-weight-cloud-runtime-manifest-r4.yml"
    )
    pod = observed_pod()
    pod[field] = bad
    with pytest.raises(RuntimeConformanceError):
        validate_created_pod(
            pod,
            pod_id="pod-1",
            namespace=NAMESPACE,
            template_id="template-1",
            manifest=manifest,
        )


def test_template_uses_only_secret_references_and_embeds_watchdog() -> None:
    spec = build_template_spec(REPO, NAMESPACE)
    environment = cast(Mapping[str, str], spec["env"])
    for name in (
        "HF_TOKEN",
        "TREASUREBENCH_RUNTIME_API_KEY",
        "TREASUREBENCH_RUNTIME_ATTESTATION_KEY",
    ):
        assert environment[name].startswith("{{ RUNPOD_SECRET_")
    assert environment["TREASUREBENCH_EXPECTED_NAMESPACE"] == NAMESPACE
    assert environment["TREASUREBENCH_WATCHDOG_SCRIPT_B64"]
    serialized = json.dumps(spec, sort_keys=True)
    assert SYNTHETIC_KEY not in serialized
    assert spec["isPublic"] is False


def test_watchdog_verifies_then_arms_then_deletes_exact_pod(tmp_path: Path) -> None:
    opener = RecordingOpener([observed_pod(), {}])
    key = MutableKey("synthetic-pod-scoped-key")
    sleeps: list[float] = []
    ticks = iter([100.0, 100.0])
    watchdog = PodDeleteWatchdog(
        "pod-1",
        key,
        urlopen=opener,
        monotonic=lambda: next(ticks),
        sleeper=sleeps.append,
    )
    status = tmp_path / "watchdog.json"
    watchdog.run(NAMESPACE, status)
    assert [request.get_method() for request in opener.requests] == ["GET", "DELETE"]
    assert all(request.full_url.endswith("/pods/pod-1") for request in opener.requests)
    assert sleeps == [21600.0]
    value = json.loads(status.read_text(encoding="utf-8"))
    assert value["verified"] is True and value["deadline_seconds"] == DEADLINE_SECONDS
    key.clear()


def test_watchdog_self_query_failure_stops_before_download_and_leaks_nothing() -> None:
    opener = RecordingOpener([{"id": "wrong", "name": NAMESPACE}])
    key = MutableKey("synthetic-pod-key")
    with pytest.raises(Exception, match="boundary mismatch") as caught:
        PodDeleteWatchdog("pod-1", key, urlopen=opener).verify(NAMESPACE)
    assert "synthetic-pod-key" not in repr(caught.value)
    key.clear()
    startup = (REPO / "scripts/treasurebench_open_weight_runtime_start_r4.sh").read_text()
    assert startup.index("watchdog_path") < startup.index("snapshot_download")
    assert startup.index("watchdog-self-query") < startup.index("download_started")


def test_vllm_proxy_and_workspace_receive_no_credentials() -> None:
    startup = (REPO / "scripts/treasurebench_open_weight_runtime_start_r4.sh").read_text()
    proxy = (REPO / "scripts/treasurebench_open_weight_proxy_r4.py").read_text()
    assert "runtime_dir=/run/treasurebench-runtime-r4" in startup
    assert 'bearer_path="${runtime_dir}/endpoint-bearer"' in startup
    assert "/workspace/treasurebench-runtime" not in startup
    assert startup.count("env -i") >= 3
    assert "unset RUNPOD_API_KEY RUNPOD_POD_ID" in startup
    assert "unset HF_TOKEN" in startup
    assert "unset TREASUREBENCH_RUNTIME_ATTESTATION_KEY" in startup
    assert "scrub_environment()" in proxy
    assert "FORBIDDEN_ENV_NAMES.intersection(os.environ)" in proxy


def test_exact_credential_subset_with_fake_file_only(tmp_path: Path) -> None:
    path = tmp_path / ".env.txt"
    path.write_text(
        "RUNPOD_API_KEY=fake-runpod\nHF_TOKEN=fake-hf\nOPENAI_API_KEY=inaccessible\n",
        encoding="utf-8",
    )
    path.chmod(0o600)
    credentials = load_credentials(path, explicit_live_mode=True, requested_names=CREDENTIAL_NAMES)
    assert credentials.get_secret("RUNPOD_API_KEY") == "fake-runpod"
    assert credentials.get_secret("HF_TOKEN") == "fake-hf"
    with pytest.raises(PermissionError):
        credentials.get_secret("OPENAI_API_KEY")
    credentials.clear()
    assert credentials.get_secret("RUNPOD_API_KEY") is None


@pytest.mark.parametrize("kind", ["pod", "template", "secret"])
def test_zero_exact_namespace_conflicts_required(kind: str) -> None:
    plane = FakePlane()
    if kind == "pod":
        plane.pods = [{"id": "pod", "name": NAMESPACE}]
    elif kind == "template":
        plane.templates = [{"id": "template", "name": NAMESPACE}]
    else:
        plane.secrets = [{"id": "secret", "name": f"{NAMESPACE}-hf"}]
    with pytest.raises(RuntimeConformanceError):
        require_remote_conflict_free(plane, NAMESPACE)


def test_ambiguous_create_reconciles_once_and_multiple_matches_fail() -> None:
    plane = FakePlane()
    state = lifecycle()
    state.pod_id = None
    plane.pods = [{"id": "unique", "name": NAMESPACE, "createdAt": state.started_at.isoformat()}]
    assert reconcile_ambiguous_create(plane, state) == "unique"
    assert plane.create_calls == 0
    state.pod_id = None
    plane.pods.append(
        {"id": "second", "name": NAMESPACE, "createdAt": state.started_at.isoformat()}
    )
    with pytest.raises(RuntimeConformanceError, match="multiple exact namespace"):
        reconcile_ambiguous_create(plane, state)


def test_success_finalizer_deletes_pod_volume_resources_and_reconciles_bill() -> None:
    plane = FakePlane()
    state = lifecycle()
    pod = observed_pod()
    plane.pods = [pod]
    plane.templates = [{"id": "template-1", "name": NAMESPACE}]
    plane.secrets = [{"id": item.id, "name": item.name} for item in state.secrets]
    result = finalize_lifecycle(plane, state, poll=lambda _: None)
    assert result.exact
    assert state.pod_unaddressable is True
    assert state.volume_deleted is True
    assert state.template_deleted is True
    assert state.secrets_deleted is True
    assert state.billing == BillingRecord(Decimal("0.695"), 1_800_000, Decimal("120"), 1)


@pytest.mark.parametrize(
    ("ambiguity", "expected"),
    [
        ("pod", "teardown-ambiguity"),
        ("network", "teardown-ambiguity"),
        ("template", "secret-template-deletion-ambiguity"),
        ("secret", "secret-template-deletion-ambiguity"),
        ("billing", "billing-reconciliation-unavailable"),
    ],
)
def test_every_resource_or_billing_ambiguity_is_nonmergeable(
    ambiguity: str,
    expected: str,
) -> None:
    plane = FakePlane()
    state = lifecycle()
    pod = observed_pod()
    if ambiguity == "network":
        pod["networkVolumeId"] = "network-1"
    plane.pods = [pod]
    plane.templates = [{"id": "template-1", "name": NAMESPACE}]
    plane.secrets = [{"id": item.id, "name": item.name} for item in state.secrets]
    plane.keep_pod = ambiguity == "pod"
    plane.keep_template = ambiguity == "template"
    plane.keep_secret = ambiguity == "secret"
    plane.fail_billing = ambiguity == "billing"
    result = finalize_lifecycle(plane, state, poll=lambda _: None)
    assert not result.exact and result.hard_stop_class == expected
    outcome = _redacted_outcome(
        state,
        failure_class=result.hard_stop_class,
        finalization=result,
        matrix=None,
        projections=None,
    )
    assert outcome["merge_or_issue_close_allowed"] is False
    assert (
        outcome["decision"]
        != "open-weight-self-operated-cloud-runtime-feasible-base-registration-next"
    )


def measured_attestation() -> tuple[dict[str, Any], dict[str, Any], str]:
    manifest = load_yaml(
        REPO / "docs/benchmark/agents-v1/open-weight-cloud-runtime-manifest-r4.yml"
    )
    key = "synthetic-attestation"
    value: dict[str, Any] = {
        "evidence_class": "measured-runtime-r4",
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
        "watchdog_pid": 123,
        "watchdog_verified": True,
        "watchdog_deadline_seconds": 21600,
    }
    value["signature"] = attestation_signature(value, key)
    return value, manifest, key


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("evidence_class", "manifest-echo"),
        ("mistral_common_version", "1.11.2"),
        ("pytorch_cuda_runtime", "12.8"),
        ("watchdog_verified", False),
        ("watchdog_deadline_seconds", 3600),
        ("watchdog_pid", 0),
    ],
)
def test_measured_attestation_rejects_echo_package_or_watchdog_drift(
    field: str,
    bad: object,
) -> None:
    value, manifest, key = measured_attestation()
    value[field] = bad
    value["signature"] = attestation_signature(
        {name: item for name, item in value.items() if name != "signature"}, key
    )
    with pytest.raises(RuntimeConformanceError):
        validate_measured_attestation(value, manifest=manifest, key=key)


@pytest.mark.parametrize("failure_class", sorted(FAILURE_CLASSES))
def test_no_bounded_failure_writes_false_feasible_decision(failure_class: str) -> None:
    state = lifecycle()
    state.dispatch_stopped = True
    result = Finalization(True, None, ())
    outcome = _redacted_outcome(
        state,
        failure_class=failure_class,
        finalization=result,
        matrix=None,
        projections=None,
    )
    assert outcome["merge_or_issue_close_allowed"] is False
    assert (
        outcome["decision"]
        != "open-weight-self-operated-cloud-runtime-feasible-base-registration-next"
    )


def test_complete_50_pairing_r4_rehearsal_and_zero_live_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_open = Path.open

    def guarded(path: Path, *args: Any, **kwargs: Any) -> Any:
        if path.name == ".env.txt":
            raise AssertionError("real credential source accessed")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    result = run_offline_rehearsal(REPO)
    assert result["r4_gate"] == GATE_ID
    assert result["orphan_control"] == {
        "control": ORPHAN_CONTROL,
        "duration_seconds": MAX_GPU_SECONDS,
        "native_terminate_after": False,
    }
    matrix = cast(Mapping[str, Any], result["synthetic_public_matrix"])
    assert matrix["intended_pairings"] == 50
    assert matrix["terminal_pairings"] == 50
    assert matrix["calls"] == 294
    assert matrix["protocol_valid_count"] == 50
    assert matrix["bound_count"] == 72
    assert matrix["primary_and_independent_bounds_agree"] is True
    assert result["credential_reads"] == 0
    assert result["provider_calls"] == 0
    assert result["gpu_provisioning"] == 0
    assert result["spend_usd"] == "0"
    assert result["live_action"] is False


def test_public_r4_files_contain_no_raw_secret_payload_or_performance_value() -> None:
    paths = (
        REPO / "tasks/treasurebench-open-weight-cloud-runtime-r4.yml",
        REPO / "docs/benchmark/agents-v1/open-weight-cloud-runtime-manifest-r4.yml",
        REPO / "docs/benchmark/agents-v1/open-weight-cloud-runtime-corruptions-r4.yml",
        REPO
        / "reports/benchmark/treasurebench-open-weight-cloud-runtime-r4-api-contract-audit.yml",
        REPO / "src/distributed_discovery/benchmark/agents_v1/open_weight_cloud_runtime_r4.py",
        REPO / "scripts/treasurebench_open_weight_runtime_start_r4.sh",
        REPO / "scripts/treasurebench_open_weight_proxy_r4.py",
        REPO / "scripts/treasurebench_open_weight_watchdog_r4.py",
    )
    joined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for forbidden in (
        SYNTHETIC_KEY,
        "fake-runpod",
        "fake-hf",
        '"prompt":',
        '"raw_output":',
        "/Users/yoheinakajima",
    ):
        assert forbidden not in joined


def test_mutable_credentials_clear_after_success_or_exception_cleanup() -> None:
    for secret in (MutableSecret("synthetic"), MutableSecret("synthetic-error")):
        try:
            assert secret.reveal().startswith("synthetic")
            if "error" in secret.reveal():
                raise RuntimeError("synthetic")
        except RuntimeError:
            pass
        finally:
            secret.clear()
        assert secret.cleared
        with pytest.raises(RuntimeConformanceError):
            secret.reveal()


def test_namespace_is_r4_authorization_bound() -> None:
    one = namespace_for("sha256:" + "1" * 64)
    two = namespace_for("sha256:" + "2" * 64)
    assert one != two
    assert one.startswith("ao0012-owcal-r4-")
