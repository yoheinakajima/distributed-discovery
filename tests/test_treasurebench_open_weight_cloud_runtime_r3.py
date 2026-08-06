from __future__ import annotations

import inspect
import io
import json
import urllib.error
import urllib.request
from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from email.message import Message
from pathlib import Path
from typing import Any, cast
from urllib.parse import quote

import pytest

from distributed_discovery.benchmark.agents_v1 import (
    open_weight_cloud_runtime_r2 as r2,
)
from distributed_discovery.benchmark.agents_v1 import (
    open_weight_cloud_runtime_r3 as r3,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime import (
    RuntimeConformanceError,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r3 import (
    POD_CREATE_INPUT_FIELDS,
    BillingRecord,
    RunPodControlPlane,
    build_pod_spec,
    run_offline_rehearsal,
)

REPO = Path(__file__).resolve().parents[1]
SYNTHETIC_KEY = "rpa_+/=?&% space"


def expected_graphql_url() -> str:
    return f"{r3.RUNPOD_GRAPHQL}?api_key={quote(SYNTHETIC_KEY, safe='')}"


def require_secret_safe(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class FakeResponse:
    def __init__(self, value: object) -> None:
        self._payload = json.dumps(value).encode()

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, _: int) -> bytes:
        return self._payload


class RecordingOpener:
    def __init__(self, responses: list[object]) -> None:
        self.responses = list(responses)
        self.requests: list[urllib.request.Request] = []

    def __call__(
        self,
        request: urllib.request.Request,
        *,
        timeout: int,
    ) -> FakeResponse:
        assert timeout == 30
        self.requests.append(request)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return FakeResponse(response)


def request_body(request: urllib.request.Request) -> dict[str, Any]:
    raw = request.data
    assert isinstance(raw, bytes)
    value = json.loads(raw)
    assert isinstance(value, dict)
    return value


def test_graphql_authentication_is_exact_query_parameter_only() -> None:
    opener = RecordingOpener(
        [{"data": {"myself": {"pods": [], "podTemplates": [], "secrets": []}}}]
    )
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=opener)
    assert plane.list_pods() == []
    request = opener.requests[0]
    require_secret_safe(request.full_url == expected_graphql_url(), "GraphQL URL drift")
    assert request.get_header("Authorization") is None
    assert request.get_header("Content-type") == "application/json"
    assert request.get_method() == "POST"
    require_secret_safe("api_key=" in request.full_url, "GraphQL query auth missing")
    assert "Authorization" not in request.headers
    plane.clear()


def test_graphql_url_encoding_is_exact_and_not_retained_in_repr() -> None:
    opener = RecordingOpener(
        [{"data": {"myself": {"pods": [], "podTemplates": [], "secrets": []}}}]
    )
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=opener)
    plane.list_secrets()
    require_secret_safe(
        opener.requests[0].full_url == expected_graphql_url(), "GraphQL URL encoding drift"
    )
    require_secret_safe(SYNTHETIC_KEY not in repr(plane), "API key repr leak")
    require_secret_safe(expected_graphql_url() not in repr(plane), "URL repr leak")
    plane.clear()


def test_graphql_inventory_secret_and_pod_create_use_corrected_transport() -> None:
    opener = RecordingOpener(
        [
            {"data": {"myself": {"pods": [], "podTemplates": [], "secrets": []}}},
            {"data": {"secretCreate": {"id": "secret-1", "name": "synthetic-name"}}},
            {"data": {"secretDelete": True}},
            {
                "data": {
                    "podFindAndDeployOnDemand": {
                        "id": "pod-1",
                        "name": "ao0012-owcal-r3-synthetic",
                    }
                }
            },
        ]
    )
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=opener)
    plane.list_pods()
    secret = plane.create_secret("synthetic-name", "synthetic-value")
    plane.delete_secret(secret)
    spec = build_pod_spec(
        "ao0012-owcal-r3-synthetic",
        "template-synthetic",
        datetime(2026, 8, 2, tzinfo=UTC),
    )
    plane.create_pod(spec)
    assert len(opener.requests) == 4
    queries = [str(request_body(item)["query"]) for item in opener.requests]
    assert "AO0012Inventory" in queries[0]
    assert "AO0012SecretCreate" in queries[1]
    assert "AO0012SecretDelete" in queries[2]
    assert "AO0012PodCreate" in queries[3]
    for request in opener.requests:
        require_secret_safe(request.full_url == expected_graphql_url(), "GraphQL URL drift")
        assert request.get_header("Authorization") is None
    assert request_body(opener.requests[-1])["variables"] == {"input": spec}
    plane.clear()


def test_rest_authentication_remains_bearer_header_only() -> None:
    opener = RecordingOpener(
        [
            {"id": "template-1", "name": "synthetic-template"},
            {},
            {},
            {"id": "pod-1"},
            [
                {
                    "podId": "pod-1",
                    "amount": "0.695",
                    "timeBilledMs": 1_800_000,
                    "diskSpaceBilledGb": "120",
                }
            ],
        ]
    )
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=opener)
    template = plane.create_template({"name": "synthetic-template"})
    plane.delete_template(template)
    plane.delete_pod("pod-1")
    assert plane.get_pod("pod-1") == {"id": "pod-1"}
    bill = plane.billing("pod-1", datetime(2026, 8, 2, tzinfo=UTC))
    assert bill == BillingRecord(Decimal("0.695"), 1_800_000, Decimal("120"), 1)
    assert [item.get_method() for item in opener.requests] == [
        "POST",
        "DELETE",
        "DELETE",
        "GET",
        "GET",
    ]
    for request in opener.requests:
        require_secret_safe(
            request.full_url.startswith("https://rest.runpod.io/v1/"),
            "REST route drift",
        )
        require_secret_safe("api_key" not in request.full_url, "REST query auth leak")
        require_secret_safe(
            request.get_header("Authorization") == f"Bearer {SYNTHETIC_KEY}",
            "REST authentication drift",
        )
    plane.clear()


def test_no_request_combines_graphql_and_rest_authentication() -> None:
    opener = RecordingOpener(
        [
            {"data": {"myself": {"pods": [], "podTemplates": [], "secrets": []}}},
            {"id": "template-1", "name": "template"},
        ]
    )
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=opener)
    plane.list_pods()
    plane.create_template({"name": "template"})
    graphql, rest = opener.requests
    require_secret_safe("api_key=" in graphql.full_url, "GraphQL query auth missing")
    assert graphql.get_header("Authorization") is None
    require_secret_safe("api_key=" not in rest.full_url, "REST query auth leak")
    require_secret_safe(
        rest.get_header("Authorization") == f"Bearer {SYNTHETIC_KEY}", "REST authentication drift"
    )
    plane.clear()


@pytest.mark.parametrize(
    ("transport", "status"),
    [("graphql", 401), ("rest", 403)],
)
def test_http_exception_surface_is_fixed_and_redacted(
    transport: str,
    status: int,
) -> None:
    raw_body = b"synthetic raw provider body sentinel"
    authenticated = (
        expected_graphql_url() if transport == "graphql" else "https://rest.runpod.io/v1/pods"
    )
    headers = Message()
    headers["Authorization"] = f"Bearer {SYNTHETIC_KEY}"
    error = urllib.error.HTTPError(
        authenticated,
        status,
        "synthetic raw provider message",
        headers,
        io.BytesIO(raw_body),
    )
    opener = RecordingOpener([error])
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=opener)
    with pytest.raises(RuntimeConformanceError) as caught:
        if transport == "graphql":
            plane.list_pods()
        else:
            plane.get_pod("pod-1")
    expected = f"RunPod {'GraphQL' if transport == 'graphql' else 'REST'} HTTP {status}"
    assert str(caught.value) == expected
    surface = str(caught.value) + repr(caught.value) + repr(plane)
    for forbidden in (
        SYNTHETIC_KEY,
        expected_graphql_url(),
        "Authorization",
        "synthetic raw provider",
    ):
        require_secret_safe(forbidden not in surface, "redacted exception leak")
    plane.clear()


def test_graphql_error_body_and_malformed_rest_body_are_redacted() -> None:
    graphql = RecordingOpener([{"errors": [{"message": "synthetic raw GraphQL error sentinel"}]}])
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=graphql)
    with pytest.raises(RuntimeConformanceError) as caught:
        plane.list_pods()
    assert str(caught.value) == "RunPod GraphQL operation rejected"
    assert "sentinel" not in str(caught.value)
    plane.clear()

    class MalformedResponse(FakeResponse):
        def read(self, _: int) -> bytes:
            return b"synthetic raw REST body sentinel"

    class MalformedOpener:
        def __call__(self, request: urllib.request.Request, *, timeout: int) -> MalformedResponse:
            return MalformedResponse({})

    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=MalformedOpener())
    with pytest.raises(RuntimeConformanceError) as caught:
        plane.get_pod("pod-1")
    assert str(caught.value) == "RunPod REST malformed JSON"
    assert "sentinel" not in str(caught.value)
    plane.clear()


def test_control_plane_credential_clears_after_success_and_failure() -> None:
    success = RunPodControlPlane(
        SYNTHETIC_KEY,
        urlopen=RecordingOpener(
            [{"data": {"myself": {"pods": [], "podTemplates": [], "secrets": []}}}]
        ),
    )
    try:
        success.list_pods()
    finally:
        success.clear()
    with pytest.raises(RuntimeConformanceError, match="secret already cleared"):
        success.list_pods()

    failure = RunPodControlPlane(
        SYNTHETIC_KEY,
        urlopen=RecordingOpener([TimeoutError("synthetic URL sentinel")]),
    )
    try:
        with pytest.raises(RuntimeConformanceError, match="GraphQL transport failure"):
            failure.list_pods()
    finally:
        failure.clear()
    with pytest.raises(RuntimeConformanceError, match="secret already cleared"):
        failure.list_pods()


def test_pod_create_input_exact_supported_field_set() -> None:
    spec = build_pod_spec(
        "ao0012-owcal-r3-synthetic",
        "template-exact",
        datetime(2026, 8, 2, tzinfo=UTC),
    )
    assert frozenset(spec) == POD_CREATE_INPUT_FIELDS
    assert spec == {
        "name": "ao0012-owcal-r3-synthetic",
        "cloudType": "SECURE",
        "gpuCount": 1,
        "gpuTypeId": "NVIDIA A100 80GB PCIe",
        "templateId": "template-exact",
        "containerDiskInGb": 50,
        "volumeInGb": 120,
        "volumeMountPath": "/workspace",
        "countryCode": "US",
        "allowedCudaVersions": ["13.0"],
        "startSsh": False,
        "supportPublicIp": False,
        "terminateAfter": "2026-08-02T06:00:00Z",
    }
    serialized = json.dumps(spec, sort_keys=True)
    assert '"allowedCudaVersions": ["13.0"]' in serialized
    assert "minCudaVersion" not in serialized
    assert '"cudaVersion"' not in serialized


@pytest.mark.parametrize("mutation", ["minCudaVersion", "cudaVersion", "extra"])
def test_pod_create_rejects_unsupported_or_guessed_cuda_field(mutation: str) -> None:
    spec = build_pod_spec(
        "ao0012-owcal-r3-synthetic",
        "template-exact",
        datetime(2026, 8, 2, tzinfo=UTC),
    )
    spec[mutation] = "13.0"
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=RecordingOpener([]))
    with pytest.raises(RuntimeConformanceError, match="field set rejected"):
        plane.create_pod(spec)
    plane.clear()


def test_pod_create_rejects_allowed_cuda_value_drift() -> None:
    spec = build_pod_spec(
        "ao0012-owcal-r3-synthetic",
        "template-exact",
        datetime(2026, 8, 2, tzinfo=UTC),
    )
    spec["allowedCudaVersions"] = ["12.8"]
    plane = RunPodControlPlane(SYNTHETIC_KEY, urlopen=RecordingOpener([]))
    with pytest.raises(RuntimeConformanceError, match="CUDA field rejected"):
        plane.create_pod(spec)
    plane.clear()


def test_inherited_r2_lifecycle_controls_are_implementation_identical() -> None:
    for name in (
        "reconcile_ambiguous_create",
        "require_remote_conflict_free",
        "finalize_lifecycle",
        "validate_measured_attestation",
        "operational_projections",
        "_redacted_outcome",
    ):
        assert inspect.getsource(getattr(r3, name)) == inspect.getsource(getattr(r2, name))


def test_r3_rehearsal_preserves_complete_public_matrix_and_zero_live_action() -> None:
    value = run_offline_rehearsal(REPO)
    assert value["r3_gate"] == "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R3"
    assert value["superseded_gates"] == [
        "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION",
        "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R2",
    ]
    registration = cast(Mapping[str, Any], value["r3_registration"])
    assert registration["corruptions"] == 54
    matrix = cast(Mapping[str, Any], value["synthetic_public_matrix"])
    assert matrix["intended_pairings"] == 50
    assert matrix["terminal_pairings"] == 50
    assert matrix["calls"] == 294
    assert matrix["bound_count"] == 72
    assert value["credential_reads"] == 0
    assert value["provider_calls"] == 0
    assert value["gpu_provisioning"] == 0
    assert value["spend_usd"] == "0"
    assert value["live_action"] is False


def test_no_authenticated_surface_or_raw_payload_is_publicly_serialized() -> None:
    public_paths = (
        REPO
        / "reports/benchmark/treasurebench-open-weight-cloud-runtime-r3-api-contract-audit.yml",
        REPO / "docs/benchmark/agents-v1/open-weight-cloud-runtime-corruptions-r3.yml",
    )
    joined = "\n".join(path.read_text(encoding="utf-8") for path in public_paths)
    for forbidden in (
        SYNTHETIC_KEY,
        expected_graphql_url(),
        "synthetic raw provider",
        "Authorization: Bearer synthetic",
    ):
        require_secret_safe(forbidden not in joined, "public serialization leak")
