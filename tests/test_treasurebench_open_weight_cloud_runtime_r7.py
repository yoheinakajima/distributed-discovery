from __future__ import annotations

import copy
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

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
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r7 import (
    BRANCH,
    CONTRACT_PATH,
    EXPECTED_CUMULATIVE_STATE,
    EXPECTED_HARD_CAPS,
    EXPECTED_REMAINING_CAPS,
    GATE_ID,
    HARD_CAP,
    MAX_CALLS,
    MAX_GPU_SECONDS,
    MAX_HOURLY_RATE,
    enforce_outcome_caps,
    namespace_for,
    run_live_calibration,
    run_offline_rehearsal,
    validate_canonical_caps,
    validate_hourly_rate,
    validate_owner_authorization,
    validate_r7_registration,
)

REPO = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 6, 18, 0, tzinfo=UTC)


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
        "purpose": "Synthetic authorization-free R7 calibration-gate regression.",
        "irreversible_actions": [],
        "private_actions": [],
        "external_actions": [],
        "cumulative_state": copy.deepcopy(EXPECTED_CUMULATIVE_STATE),
        "hard_caps": copy.deepcopy(EXPECTED_HARD_CAPS),
        "remaining_caps": copy.deepcopy(EXPECTED_REMAINING_CAPS),
        "owner_confirmation_statements": ["Synthetic R7 regression only; no live action."],
        "explicit_prohibitions": [
            "credential-read",
            "authenticated-network",
            "resource-create",
            "model-download",
            "inference-call",
            "spend",
        ],
        "expires_at_utc": "2026-08-31T23:59:59Z",
        "authorization_output_symbolic_path": (
            f"XDG_CONFIG_HOME/distributed-discovery/agent-ops/authorizations/{GATE_ID}.yml"
        ),
        "next_milestone": "Regression completes without live action.",
        "generated_resume_message": "Synthetic R7 regression only; perform no live action.",
    }
    validate(gate, "owner-gate.schema.json")
    return gate


def no_live_state(_: Path, __: Mapping[str, Any]) -> None:
    return None


def test_r7_registration_and_qualified_observation_are_exact() -> None:
    result = validate_r7_registration(REPO)
    assert result["contract"] == "pass"
    outcome = load_yaml(
        REPO / "reports/benchmark/treasurebench-open-weight-secret-cleanup-outcome-r6.yml"
    )
    assert outcome["failure_class"] == "inventory-ambiguity"
    assert outcome["owner_observation"]["current_state"] == "no-saved-secrets-visible"
    assert outcome["owner_observation"]["api_proof"] is False
    assert outcome["qualified_cleanup_outcome"]["target_historical_absence_claimed"] is False
    assert (
        outcome["qualified_cleanup_outcome"]["automated_query_delete_or_retry_permitted"] is False
    )


def test_r7_gate_id_validates_against_gate_and_authorization_schemas(tmp_path: Path) -> None:
    gate = exact_gate()
    path, prior = write_authorization(
        gate,
        authorization_challenge(gate),
        config_root=tmp_path,
        now=NOW,
    )
    assert prior is None
    authorization = load_yaml(path)
    validate(authorization, "owner-authorization.schema.json")
    validate_owner_authorization(
        REPO,
        authorization,
        gate_override=gate,
        live_state_validator=no_live_state,
        now=NOW,
        synthetic_branch_context=BRANCH,
    )


def test_r7_synthetic_branch_context_rejects_wrong_registered_branch(tmp_path: Path) -> None:
    gate = exact_gate()
    path, prior = write_authorization(
        gate,
        authorization_challenge(gate),
        config_root=tmp_path,
        now=NOW,
    )
    assert prior is None
    authorization = load_yaml(path)
    with pytest.raises(RuntimeConformanceError, match="live branch mismatch"):
        validate_owner_authorization(
            REPO,
            authorization,
            gate_override=gate,
            live_state_validator=no_live_state,
            now=NOW,
            synthetic_branch_context="main",
        )


def test_r7_synthetic_branch_context_cannot_override_real_live_validation(
    tmp_path: Path,
) -> None:
    gate = exact_gate()
    path, prior = write_authorization(
        gate,
        authorization_challenge(gate),
        config_root=tmp_path,
        now=NOW,
    )
    assert prior is None
    authorization = load_yaml(path)
    with pytest.raises(
        RuntimeConformanceError,
        match="synthetic branch context requires synthetic live-state validator",
    ):
        validate_owner_authorization(
            REPO,
            authorization,
            gate_override=gate,
            now=NOW,
            synthetic_branch_context=BRANCH,
        )


def test_default_r7_path_still_reads_and_rejects_wrong_live_branch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate = exact_gate()
    path, prior = write_authorization(
        gate,
        authorization_challenge(gate),
        config_root=tmp_path,
        now=NOW,
    )
    assert prior is None
    authorization = load_yaml(path)
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0],
            0,
            stdout="main\n",
        ),
    )
    with pytest.raises(RuntimeConformanceError, match="live branch mismatch"):
        validate_owner_authorization(
            REPO,
            authorization,
            gate_override=gate,
            live_state_validator=no_live_state,
            now=NOW,
        )


@pytest.mark.parametrize(
    "mutator",
    [
        lambda gate: gate["cumulative_state"].update(spend="0.01"),
        lambda gate: gate["hard_caps"].update(spend="11"),
        lambda gate: gate["hard_caps"].update(calls=401),
        lambda gate: gate["remaining_caps"].update(spend="9"),
    ],
    ids=["cumulative-spend", "hard-spend", "hard-calls", "remaining"],
)
def test_r7_cap_corruptions_reject(mutator: Any) -> None:
    gate = exact_gate()
    mutator(gate)
    with pytest.raises(RuntimeConformanceError):
        validate_canonical_caps(gate)


def test_r7_cost_and_time_envelope_is_tighter_than_account_balance() -> None:
    assert Decimal("10") == HARD_CAP
    assert Decimal("1.50") == MAX_HOURLY_RATE
    assert MAX_GPU_SECONDS == 21_600
    assert MAX_CALLS == 400
    assert MAX_HOURLY_RATE * Decimal(MAX_GPU_SECONDS) / Decimal(3600) == Decimal("9.00")
    assert Decimal("200") > HARD_CAP


def test_hourly_rate_ceiling_is_exact() -> None:
    assert validate_hourly_rate("1.39") == Decimal("1.39")
    assert validate_hourly_rate("1.50") == Decimal("1.50")
    with pytest.raises(RuntimeConformanceError, match="hourly rate above R7"):
        validate_hourly_rate("1.51")


def test_r7_namespace_never_reuses_r5_namespace() -> None:
    namespace = namespace_for("sha256:" + "a" * 64)
    assert namespace == "ao0012-owcal-r7-aaaaaaaaaaaaaaaa"
    assert "owcal-r5" not in namespace


def test_outcome_cap_breach_fails_closed() -> None:
    outcome: dict[str, object] = {
        "status": "public-calibration-operational-closeout",
        "failure_class": None,
        "decision": "open-weight-self-operated-cloud-runtime-feasible-base-registration-next",
        "billing": {
            "exact_amount_usd": "10.01",
            "billed_milliseconds": 1,
        },
        "operational_counts": {"calls": 50},
        "merge_or_issue_close_allowed": True,
    }
    result = enforce_outcome_caps(outcome)
    assert result["status"] == "hard-stop"
    assert result["failure_class"] == "circuit-breaker-or-runtime-cap-failure"
    assert result["decision"] == "calibration-integrity-failure-stop"
    assert result["merge_or_issue_close_allowed"] is False


def test_pre_ingress_failure_keeps_credentials_and_provider_unreachable(tmp_path: Path) -> None:
    gate = exact_gate()
    gate["hard_caps"]["spend"] = "11"
    auth_path, _ = write_authorization(
        gate,
        authorization_challenge(gate),
        config_root=tmp_path,
        now=NOW,
    )
    actions = {"credential": 0, "provider": 0}

    def credential_loader(*_: object, **__: object) -> Any:
        actions["credential"] += 1
        raise AssertionError("credential loader must remain unreachable")

    def plane_factory(_: str) -> Any:
        actions["provider"] += 1
        raise AssertionError("provider plane must remain unreachable")

    def reject(repo: Path, authorization: Mapping[str, Any]) -> Lifecycle:
        validate_owner_authorization(
            repo,
            authorization,
            gate_override=gate,
            live_state_validator=no_live_state,
            now=NOW,
        )
        raise AssertionError("corrupt R7 gate unexpectedly validated")

    with pytest.raises(RuntimeConformanceError):
        run_live_calibration(
            REPO,
            credential_loader=credential_loader,
            plane_factory=plane_factory,
            authorization_file=auth_path,
            pre_ingress_validator=reject,
        )
    assert actions == {"credential": 0, "provider": 0}


def test_full_50_pairing_offline_rehearsal_remains_exact() -> None:
    result = run_offline_rehearsal(REPO)
    matrix = result["synthetic_public_matrix"]
    assert isinstance(matrix, dict)
    assert matrix["intended_pairings"] == 50
    assert matrix["terminal_pairings"] == 50
    assert matrix["calls"] == 294
    assert matrix["protocol_valid_count"] == 50
    assert matrix["method_a_b_agree"] is True
    assert matrix["method_c_classifies_every_completed_response"] is True
    assert matrix["primary_and_independent_bounds_agree"] is True
    assert result["live_action"] is False
    assert result["prospective_caps"]["hard_spend_usd"] == "10"
