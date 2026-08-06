from __future__ import annotations

import copy
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from jsonschema import ValidationError

from distributed_discovery.agent_ops.core import (
    authorization_challenge,
    load_yaml,
    sha256_file,
    validate,
    write_authorization,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime import (
    RuntimeConformanceError,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import Lifecycle
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r5 import (
    BRANCH,
    CONSUMED_GATE_ID,
    CONTRACT_PATH,
    EXPECTED_CUMULATIVE_STATE,
    EXPECTED_HARD_CAPS,
    EXPECTED_REMAINING_CAPS,
    GATE_ID,
    run_live_calibration,
    run_offline_rehearsal,
    validate_canonical_caps,
    validate_owner_authorization,
)

REPO = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 4, 18, 0, tzinfo=UTC)


def exact_gate() -> dict[str, Any]:
    commit = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    contract_hash = sha256_file(REPO / CONTRACT_PATH)
    gate: dict[str, Any] = {
        "schema_version": "agent-ops-owner-gate-v1",
        "kind": "owner-gate",
        "synthetic": False,
        "gate_id": GATE_ID,
        "task_contract": {"path": str(CONTRACT_PATH), "sha256": contract_hash},
        "issue": 212,
        "pull_request": {"number": 213, "expected_state": "OPEN", "head_sha": commit},
        "branch": BRANCH,
        "commit": commit,
        "tree_hashes": {str(CONTRACT_PATH): contract_hash},
        "purpose": "Synthetic authorization-free R5 compatibility regression.",
        "irreversible_actions": [],
        "private_actions": [],
        "external_actions": [],
        "cumulative_state": copy.deepcopy(EXPECTED_CUMULATIVE_STATE),
        "hard_caps": copy.deepcopy(EXPECTED_HARD_CAPS),
        "remaining_caps": copy.deepcopy(EXPECTED_REMAINING_CAPS),
        "owner_confirmation_statements": ["Synthetic R5 regression only; no live action."],
        "explicit_prohibitions": [
            "credential-read",
            "authenticated-network",
            "resource-create",
            "model-download",
            "inference-call",
            "spend",
        ],
        "expires_at_utc": "2026-08-20T23:59:59Z",
        "authorization_output_symbolic_path": (
            f"XDG_CONFIG_HOME/distributed-discovery/agent-ops/authorizations/{GATE_ID}.yml"
        ),
        "next_milestone": "Regression completes without live action.",
        "generated_resume_message": "Synthetic R5 regression only; perform no live action.",
    }
    validate(gate, "owner-gate.schema.json")
    return gate


def real_writer_authorization(tmp_path: Path, gate: dict[str, Any]) -> dict[str, Any]:
    path, prior = write_authorization(
        gate,
        authorization_challenge(gate),
        config_root=tmp_path,
        now=NOW,
    )
    assert prior is None
    return load_yaml(path)


def no_live_state(_: Path, __: Mapping[str, Any]) -> None:
    return None


def validate_synthetic(gate: dict[str, Any], authorization: dict[str, Any]) -> None:
    validate_owner_authorization(
        REPO,
        authorization,
        gate_override=gate,
        live_state_validator=no_live_state,
        now=NOW,
    )


def test_exact_generic_gate_shape_has_no_budget_and_validates() -> None:
    gate = exact_gate()
    assert "budget" not in gate
    validate_canonical_caps(gate)


def test_real_generic_authorization_writer_output_validates(tmp_path: Path) -> None:
    gate = exact_gate()
    authorization = real_writer_authorization(tmp_path, gate)
    assert "cumulative_state" not in authorization
    assert "hard_caps" not in authorization
    assert "remaining_caps" not in authorization
    validate_synthetic(gate, authorization)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda gate: gate["cumulative_state"].update(spend="0.01"),
        lambda gate: gate["cumulative_state"].update(calls=1),
        lambda gate: gate["hard_caps"].update(spend="19"),
        lambda gate: gate["hard_caps"].update(calls=399),
        lambda gate: gate["remaining_caps"].update(spend="19"),
        lambda gate: gate["hard_caps"]["category_spend"].update(
            runpod_gpu_compute_and_storage="19"
        ),
        lambda gate: gate["hard_caps"]["category_spend"].update(hidden_provider="1"),
        lambda gate: gate["remaining_caps"].update(currency="EUR"),
    ],
    ids=[
        "cumulative-spend",
        "cumulative-calls",
        "hard-spend",
        "hard-calls",
        "remaining-mismatch",
        "category-mismatch",
        "hidden-category",
        "currency",
    ],
)
def test_exact_cap_corruptions_reject(tmp_path: Path, mutator: Any) -> None:
    gate = exact_gate()
    mutator(gate)
    authorization = real_writer_authorization(tmp_path, gate)
    with pytest.raises(RuntimeConformanceError):
        validate_synthetic(gate, authorization)


def test_legacy_budget_insertion_never_becomes_authority(tmp_path: Path) -> None:
    gate = exact_gate()
    gate["budget"] = {"cumulative_spend": "0", "cumulative_calls": 0}
    authorization = real_writer_authorization(tmp_path, gate)
    with pytest.raises(ValidationError):
        validate_synthetic(gate, authorization)


def test_consumed_r4_authorization_cannot_authorize_r5(tmp_path: Path) -> None:
    r4_gate = load_yaml(
        REPO / "reports/agent-ops/AO-0012-open-weight-public-calibration-r4-owner-gate.yml"
    )
    assert r4_gate["gate_id"] == CONSUMED_GATE_ID
    authorization = real_writer_authorization(tmp_path, r4_gate)
    with pytest.raises(RuntimeConformanceError, match="R5 owner authorization required"):
        validate_synthetic(exact_gate(), authorization)


def test_mismatch_stops_live_entry_before_credentials_or_actions(tmp_path: Path) -> None:
    gate = exact_gate()
    gate["cumulative_state"]["calls"] = 1
    auth_path, _ = write_authorization(
        gate,
        authorization_challenge(gate),
        config_root=tmp_path,
        now=NOW,
    )
    actions = {"credential": 0, "plane": 0}

    def credential_loader(*_: object, **__: object) -> Any:
        actions["credential"] += 1
        raise AssertionError("credential loader must remain unreachable")

    def plane_factory(_: str) -> Any:
        actions["plane"] += 1
        raise AssertionError("provider control plane must remain unreachable")

    def reject_before_ingress(repo: Path, authorization: Mapping[str, Any]) -> Lifecycle:
        validate_owner_authorization(
            repo,
            authorization,
            gate_override=gate,
            live_state_validator=no_live_state,
            now=NOW,
        )
        raise AssertionError("corrupt gate unexpectedly validated")

    with pytest.raises(RuntimeConformanceError):
        run_live_calibration(
            REPO,
            credential_loader=credential_loader,
            plane_factory=plane_factory,
            authorization_file=auth_path,
            pre_ingress_validator=reject_before_ingress,
        )
    assert actions == {"credential": 0, "plane": 0}


def test_no_ao0012_live_adapter_has_legacy_budget_dependency() -> None:
    root = REPO / "src/distributed_discovery/benchmark/agents_v1"
    for path in sorted(root.glob("open_weight_cloud_runtime*.py")):
        source = path.read_text(encoding="utf-8")
        assert 'gate["budget"]' not in source
        assert "gate['budget']" not in source


def test_full_50_pairing_offline_rehearsal_remains_exact() -> None:
    result = run_offline_rehearsal(REPO)
    matrix = result["synthetic_public_matrix"]
    assert isinstance(matrix, dict)
    assert matrix["intended_pairings"] == 50
    assert matrix["terminal_pairings"] == 50
    assert matrix["calls"] == 294
    assert matrix["protocol_valid_count"] == 50
    assert matrix["provider_operational_missing_count"] == 0
    assert matrix["runtime_failure_count"] == 0
    assert matrix["method_a_b_agree"] is True
    assert matrix["method_c_classifies_every_completed_response"] is True
    assert matrix["primary_and_independent_bounds_agree"] is True
    assert result["live_action"] is False
