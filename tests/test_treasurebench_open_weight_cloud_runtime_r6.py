from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from collections.abc import Mapping
from datetime import UTC, datetime
from email.message import Message
from pathlib import Path
from typing import Any

import pytest
import yaml

from distributed_discovery.benchmark.agents_v1.live_inputs import CredentialSet
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime import (
    RuntimeConformanceError,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    Lifecycle,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    run_live_calibration as run_r5_frozen_lifecycle,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r6 import (
    CREDENTIAL_NAMES,
    FAILED_GATE_ID,
    FAILED_GATE_PATH,
    GATE_ID,
    MAX_AUTHENTICATED_OPERATIONS,
    NAMESPACE,
    POSTMORTEM_PATH,
    RUNPOD_GRAPHQL,
    TARGET_SECRET_NAME,
    RunPodSecretCleanupPlane,
    run_cleanup_with_plane,
    run_live_cleanup,
    run_offline_rehearsal,
    validate_r6_registration,
)

REPO = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 5, 22, 47, 55, tzinfo=UTC)


class FakeResponse:
    def __init__(self, value: Mapping[str, object]) -> None:
        self._raw = json.dumps(value).encode()

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, _: int) -> bytes:
        return self._raw


class QueueUrlopen:
    def __init__(self, values: list[object]) -> None:
        self.values = list(values)
        self.requests: list[urllib.request.Request] = []

    def __call__(self, request: urllib.request.Request, *, timeout: int) -> FakeResponse:
        assert timeout == 20
        self.requests.append(request)
        value = self.values.pop(0)
        if isinstance(value, Exception):
            raise value
        assert isinstance(value, Mapping)
        return FakeResponse(value)


def inventory(*items: tuple[str, str]) -> dict[str, object]:
    return {
        "data": {
            "myself": {"secrets": [{"id": secret_id, "name": name} for secret_id, name in items]}
        }
    }


class SyntheticPlane:
    def __init__(
        self,
        inventories: list[list[dict[str, str]]],
        *,
        delete_error: bool = False,
    ) -> None:
        self.inventories = list(inventories)
        self.delete_error = delete_error
        self.operations = 0
        self.deleted: list[str] = []
        self.cleared = False

    def list_secrets(self) -> list[dict[str, str]]:
        if self.operations >= MAX_AUTHENTICATED_OPERATIONS:
            raise AssertionError("operation cap exceeded")
        self.operations += 1
        value = self.inventories.pop(0)
        if value and value[0].get("id") == "raise":
            raise RuntimeConformanceError("synthetic inventory ambiguity")
        return value

    def delete_secret(self, secret_id: str) -> None:
        if self.operations >= MAX_AUTHENTICATED_OPERATIONS:
            raise AssertionError("operation cap exceeded")
        self.operations += 1
        self.deleted.append(secret_id)
        if self.delete_error:
            raise RuntimeConformanceError("synthetic delete ambiguity")

    def clear(self) -> None:
        self.cleared = True


class FrozenR5StopPlane:
    def __init__(self, failure: str) -> None:
        self.failure = failure
        self.calls: list[str] = []
        self.inventory_secret_calls = 0

    def list_pods(self) -> list[dict[str, Any]]:
        self.calls.append("list_pods")
        if self.failure == "conflict-inventory":
            raise RuntimeConformanceError("synthetic conflict inventory failure")
        return []

    def list_templates(self) -> list[dict[str, Any]]:
        self.calls.append("list_templates")
        return []

    def list_secrets(self) -> list[dict[str, Any]]:
        self.calls.append("list_secrets")
        self.inventory_secret_calls += 1
        return []

    def create_secret(self, name: str, _: str) -> Any:
        self.calls.append(f"create_secret:{name}")
        raise RuntimeConformanceError("synthetic ambiguous first Secret create")

    def create_template(self, _: Mapping[str, object]) -> Any:
        raise AssertionError("template must remain unreachable")

    def create_pod(self, _: Mapping[str, object]) -> dict[str, Any]:
        raise AssertionError("Pod must remain unreachable")

    def get_pod(self, _: str) -> dict[str, Any] | None:
        raise AssertionError("Pod lookup must remain unreachable")

    def delete_pod(self, _: str) -> None:
        raise AssertionError("Pod deletion must remain unreachable")

    def delete_template(self, _: Any) -> None:
        raise AssertionError("template deletion must remain unreachable")

    def delete_secret(self, _: Any) -> None:
        raise AssertionError("returned Secret deletion must remain unreachable")

    def billing(self, *_: object) -> Any:
        raise AssertionError("billing must remain unreachable")

    def clear(self) -> None:
        self.calls.append("clear")


def synthetic_credentials() -> CredentialSet:
    return CredentialSet(
        {"RUNPOD_API_KEY": "synthetic-runpod", "HF_TOKEN": "synthetic-hf"},
        allowed_names={"RUNPOD_API_KEY", "HF_TOKEN"},
        configured={"RUNPOD_API_KEY": True, "HF_TOKEN": True},
        unused_present=(),
    )


def synthetic_r6_credentials() -> CredentialSet:
    return CredentialSet(
        {"RUNPOD_API_KEY": "synthetic-runpod"},
        allowed_names={"RUNPOD_API_KEY"},
        configured={"RUNPOD_API_KEY": True},
        unused_present=(),
    )


def write_synthetic_authorization(path: Path) -> None:
    path.write_text("synthetic: true\n", encoding="utf-8")
    path.chmod(0o600)


@pytest.mark.parametrize("failure", ["conflict-inventory", "first-secret-create"])
def test_r5_early_failures_leave_all_later_surfaces_unreachable(
    tmp_path: Path,
    failure: str,
) -> None:
    auth = tmp_path / "authorization.yml"
    state = tmp_path / "state.json"
    outcome = tmp_path / "outcome.yml"
    write_synthetic_authorization(auth)
    plane = FrozenR5StopPlane(failure)

    def preflight(_: Path, __: Mapping[str, Any]) -> Lifecycle:
        return Lifecycle(NAMESPACE, "sha256:" + "1" * 64, NOW)

    result = run_r5_frozen_lifecycle(
        REPO,
        credential_loader=lambda *_args, **_kwargs: synthetic_credentials(),
        plane_factory=lambda _: plane,
        authorization_file=auth,
        pre_ingress_validator=preflight,
        live_state_file=state,
        outcome_path=outcome,
    )
    assert state.exists() is False
    assert result["resource_ids"] == {"pod": None, "template": None, "secrets": []}
    assert result["billing"] is None
    assert result["operational_counts"] is None
    if failure == "conflict-inventory":
        assert not any(call.startswith("create_secret:") for call in plane.calls)
    else:
        assert plane.calls.count(f"create_secret:{TARGET_SECRET_NAME}") == 1
    assert not any(
        call.startswith("create_secret:") and not call.endswith("-hf") for call in plane.calls
    )
    assert "clear" in plane.calls


def test_postmortem_preserves_exact_only_possible_resource_and_ambiguity() -> None:
    value = yaml.safe_load((REPO / POSTMORTEM_PATH).read_text(encoding="utf-8"))
    assert value["exact_possible_resource"]["name"] == TARGET_SECRET_NAME
    assert value["exact_possible_resource"]["presence"] == "ambiguous"
    assert value["provider_presence_conclusion"] == "ambiguous"
    assert value["root_cause_conclusion"] == (
        "ambiguous-between-conflict-inventory-and-first-secret-create"
    )
    assert value["limitations"][1].endswith("currently exists at RunPod.")


def test_short_r6_gate_is_compatible_and_failed_long_gate_remains_immutable() -> None:
    gate_schema = json.loads((REPO / "docs/agent-ops/owner-gate.schema.json").read_text())
    authorization_schema = json.loads(
        (REPO / "docs/agent-ops/owner-authorization.schema.json").read_text()
    )
    gate_pattern = gate_schema["properties"]["gate_id"]["pattern"]
    authorization_pattern = authorization_schema["properties"]["gate_id"]["pattern"]
    assert gate_pattern == authorization_pattern
    assert GATE_ID == "AOG-AO-0012-R6-RUNPOD-SECRET-CLEANUP"
    assert re.fullmatch(gate_pattern, GATE_ID)
    assert len(FAILED_GATE_ID) == 55
    assert re.fullmatch(gate_pattern, FAILED_GATE_ID) is None
    failed_gate = yaml.safe_load((REPO / FAILED_GATE_PATH).read_text(encoding="utf-8"))
    assert failed_gate["gate_id"] == FAILED_GATE_ID


def test_runpod_cleanup_transport_is_query_key_only_and_url_encoded() -> None:
    key = "synthetic key+/=?"
    transport = QueueUrlopen([inventory()])
    plane = RunPodSecretCleanupPlane(key, urlopen=transport)
    assert plane.list_secrets() == []
    request = transport.requests[0]
    assert request.full_url == f"{RUNPOD_GRAPHQL}?api_key=synthetic%20key%2B%2F%3D%3F"
    assert request.get_header("Authorization") is None
    assert request.get_method() == "POST"
    assert "Bearer" not in repr(request.header_items())
    assert key not in repr(plane)
    plane.clear()


def test_transport_redacts_key_url_and_raw_provider_error() -> None:
    key = "synthetic-private-key"
    error = urllib.error.HTTPError(
        f"{RUNPOD_GRAPHQL}?api_key={key}",
        503,
        "raw",
        Message(),
        None,
    )
    plane = RunPodSecretCleanupPlane(key, urlopen=QueueUrlopen([error]))
    with pytest.raises(RuntimeConformanceError) as captured:
        plane.list_secrets()
    public = str(captured.value)
    assert public == "RunPod R6 GraphQL HTTP 503"
    assert key not in public
    assert RUNPOD_GRAPHQL not in public
    assert "raw" not in public
    plane.clear()


def test_zero_target_is_verified_absent_with_one_operation_and_no_delete() -> None:
    plane = SyntheticPlane([[{"id": "other", "name": "unrelated"}]])
    outcome = run_cleanup_with_plane(plane)
    assert outcome["status"] == "verified"
    assert outcome["target_absent_verified"] is True
    assert outcome["authenticated_operations"] == 1
    assert outcome["delete_attempted"] is False
    assert plane.deleted == []


def test_unique_target_is_deleted_and_verified_in_exactly_three_operations() -> None:
    plane = SyntheticPlane(
        [[{"id": "secret-1", "name": TARGET_SECRET_NAME}], []],
    )
    outcome = run_cleanup_with_plane(plane)
    assert outcome["status"] == "verified"
    assert outcome["target_secret_id"] == "secret-1"
    assert outcome["target_absent_verified"] is True
    assert outcome["authenticated_operations"] == 3
    assert plane.deleted == ["secret-1"]


@pytest.mark.parametrize(
    "items",
    [
        [
            {"id": "secret-1", "name": TARGET_SECRET_NAME},
            {"id": "secret-2", "name": TARGET_SECRET_NAME},
        ],
        [{"id": "secret-2", "name": f"{NAMESPACE}-endpoint"}],
    ],
)
def test_multiple_or_sibling_namespace_matches_stop_without_delete(
    items: list[dict[str, str]],
) -> None:
    plane = SyntheticPlane([items])
    outcome = run_cleanup_with_plane(plane)
    assert outcome["status"] == "hard-stop"
    assert outcome["failure_class"] == "namespace-conflict"
    assert outcome["authenticated_operations"] == 1
    assert plane.deleted == []


def test_ambiguous_delete_uses_only_verification_and_accepts_proven_absence() -> None:
    plane = SyntheticPlane(
        [[{"id": "secret-1", "name": TARGET_SECRET_NAME}], []],
        delete_error=True,
    )
    outcome = run_cleanup_with_plane(plane)
    assert outcome["status"] == "verified"
    assert outcome["target_absent_verified"] is True
    assert outcome["authenticated_operations"] == 3
    assert plane.deleted == ["secret-1"]


def test_verification_ambiguity_hard_stops_without_fourth_operation() -> None:
    plane = SyntheticPlane(
        [
            [{"id": "secret-1", "name": TARGET_SECRET_NAME}],
            [{"id": "raise", "name": "synthetic"}],
        ]
    )
    outcome = run_cleanup_with_plane(plane)
    assert outcome["status"] == "hard-stop"
    assert outcome["failure_class"] == "verification-ambiguity"
    assert outcome["authenticated_operations"] == 3


def test_authenticated_operation_cap_rejects_fourth_call_before_transport() -> None:
    transport = QueueUrlopen([inventory(), inventory(), inventory()])
    plane = RunPodSecretCleanupPlane("synthetic", urlopen=transport)
    plane.list_secrets()
    plane.list_secrets()
    plane.list_secrets()
    with pytest.raises(RuntimeConformanceError, match="operation cap"):
        plane.list_secrets()
    assert len(transport.requests) == 3
    plane.clear()


def test_live_entry_missing_authorization_stops_before_credential_loader(tmp_path: Path) -> None:
    calls = {"credential": 0}

    def credential_loader(*_: object, **__: object) -> Any:
        calls["credential"] += 1
        raise AssertionError("credential loader must remain unreachable")

    with pytest.raises(RuntimeConformanceError, match="R6 owner authorization required"):
        run_live_cleanup(
            REPO,
            authorization_file=tmp_path / "absent.yml",
            credential_loader=credential_loader,
        )
    assert calls == {"credential": 0}


def test_live_entry_requests_only_runpod_key_and_clears_every_exit(tmp_path: Path) -> None:
    auth = tmp_path / "authorization.yml"
    outcome_path = tmp_path / "outcome.yml"
    write_synthetic_authorization(auth)
    observed: dict[str, object] = {}
    credential = synthetic_r6_credentials()

    def loader(_: Path, *, explicit_live_mode: bool, requested_names: object) -> CredentialSet:
        observed["live"] = explicit_live_mode
        observed["names"] = requested_names
        return credential

    plane = SyntheticPlane([[]])
    outcome = run_live_cleanup(
        REPO,
        authorization_file=auth,
        consumption_file=tmp_path / "consumed.json",
        credential_loader=loader,
        plane_factory=lambda _: plane,
        pre_ingress_validator=lambda _repo, _authorization: None,
        outcome_path=outcome_path,
    )
    assert outcome["status"] == "verified"
    assert observed == {"live": True, "names": CREDENTIAL_NAMES}
    assert credential.get_secret("RUNPOD_API_KEY") is None
    with pytest.raises(PermissionError):
        credential.get_secret("HF_TOKEN")
    assert plane.cleared is True
    assert outcome_path.is_file()


def test_r6_authorization_is_consumed_before_credentials_and_cannot_be_reused(
    tmp_path: Path,
) -> None:
    auth = tmp_path / "authorization.yml"
    consumed = tmp_path / "consumed.json"
    write_synthetic_authorization(auth)
    calls = {"credential": 0}

    def loader(_: Path, *, explicit_live_mode: bool, requested_names: object) -> CredentialSet:
        assert explicit_live_mode is True
        assert requested_names == CREDENTIAL_NAMES
        calls["credential"] += 1
        return synthetic_r6_credentials()

    run_live_cleanup(
        REPO,
        authorization_file=auth,
        consumption_file=consumed,
        credential_loader=loader,
        plane_factory=lambda _: SyntheticPlane([[]]),
        pre_ingress_validator=lambda _repo, _authorization: None,
        outcome_path=tmp_path / "first.yml",
    )
    assert consumed.stat().st_mode & 0o777 == 0o600
    with pytest.raises(RuntimeConformanceError, match="already consumed"):
        run_live_cleanup(
            REPO,
            authorization_file=auth,
            consumption_file=consumed,
            credential_loader=loader,
            plane_factory=lambda _: SyntheticPlane([[]]),
            pre_ingress_validator=lambda _repo, _authorization: None,
            outcome_path=tmp_path / "second.yml",
        )
    assert calls == {"credential": 1}


def test_r6_registration_and_full_50_pairing_rehearsal_are_offline_exact() -> None:
    registration = validate_r6_registration(REPO)
    assert registration["credential_read"] is False
    assert registration["authenticated_provider_call"] is False
    result = run_offline_rehearsal(REPO)
    matrix = result["synthetic_public_matrix"]
    assert isinstance(matrix, Mapping)
    assert matrix["intended_pairings"] == 50
    assert matrix["terminal_pairings"] == 50
    assert matrix["calls"] == 294
    assert matrix["method_a_b_agree"] is True
    assert matrix["method_c_classifies_every_completed_response"] is True
    assert matrix["primary_and_independent_bounds_agree"] is True
    assert result["live_action"] is False
