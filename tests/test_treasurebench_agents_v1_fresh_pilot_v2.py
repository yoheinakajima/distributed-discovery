from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from distributed_discovery.benchmark.agents_v1 import fresh_pilot_v2
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v2_live import (
    RouteCappedLedger,
    audit_live_corruptions,
    private_state_root,
    run_live_fresh_pilot,
    run_mock_fresh_pilot,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v2_registration_allocation_budget_and_provider_boundary_are_exact() -> None:
    registration = fresh_pilot_v2.validate_registration(ROOT)
    slots = fresh_pilot_v2.allocation_slots(ROOT)
    tasks = fresh_pilot_v2.generate_tasks(
        ROOT,
        material="FRESH-RC-V2-TEST-PUBLIC",
        public_fixture=True,
    )
    boundary = fresh_pilot_v2.validate_provider_boundary(tasks)
    assert registration["status"] == "pass"
    assert registration["slots"] == 50
    assert registration["runs"] == 500
    assert len({slot.slot_id for slot in slots}) == 50
    assert all(slot.slot_id.startswith("RCV2-SLOT-") for slot in slots)
    assert boundary["provider_independent_semantic_validation"] == "pass"
    assert boundary["exactly_one_final_action"] == "pass"
    fingerprints = boundary["provider_schema_fingerprints"]
    assert isinstance(fingerprints, dict)
    assert len(set(fingerprints.values())) == 2
    assert registration["provider_calls"] == 0
    assert registration["credential_reads"] == 0
    assert registration["private_objects_created"] == 0
    assert registration["spend_usd"] == "0"


def test_v2_private_generation_fails_before_generic_owner_authorization() -> None:
    with pytest.raises(PermissionError, match="owner authorization"):
        fresh_pilot_v2.generate_tasks(ROOT, material="forbidden", public_fixture=False)


def test_v2_complete_500_run_rehearsal() -> None:
    result = fresh_pilot_v2.run_synthetic_rehearsal(ROOT)
    assert result["status"] == "pass"
    assert result["tasks"] == 50
    assert result["runs"] == 500
    assert result["turns"] == 3014
    assert result["exact_pairings_verified"] == 500
    assert result["incomplete_pairings"] == 0
    assert result["method_a_b_errors"] == 0
    assert result["method_c_errors"] == 0
    assert result["metric_range_errors"] == 0
    assert result["invalid_final_action_cardinalities"] == 0
    assert result["contamination_findings"] == 0
    assert result["nonfinal_proposals_excluded_from_scoring"] is True
    assert result["output_lock_verified"] is True
    assert result["provider_calls"] == 0
    assert result["credential_reads"] == 0
    assert result["private_objects_created"] == 0
    assert result["external_cost_usd"] == "0"


def test_all_41_v2_corruptions_reject_and_match_registry() -> None:
    observed = (
        *fresh_pilot_v2.audit_corruptions(ROOT),
        *audit_live_corruptions(ROOT),
    )
    registry = fresh_pilot_v2.load_corruption_registry(ROOT)
    assert len(observed) == 41
    assert {item["corruption_id"] for item in observed} == set(registry["corruptions"])
    assert all(item["status"] == "rejected" for item in observed)


@pytest.mark.parametrize(
    ("provider", "input_tokens", "output_tokens"),
    [
        ("OpenAI", 1_680_001, 0),
        ("OpenAI", 0, 386_049),
        ("Anthropic", 3_000_001, 0),
        ("Anthropic", 0, 386_049),
    ],
)
def test_v2_route_token_caps_fail_closed(
    tmp_path: Path,
    provider: str,
    input_tokens: int,
    output_tokens: int,
) -> None:
    ledger = RouteCappedLedger(tmp_path / f"{provider}.jsonl")
    with pytest.raises(PermissionError, match="token cap"):
        ledger.guard_next(
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=Decimal("0"),
        )


def test_v2_offline_module_has_no_credential_or_provider_runtime() -> None:
    source = (ROOT / "src/distributed_discovery/benchmark/agents_v1/fresh_pilot_v2.py").read_text(
        encoding="utf-8"
    )
    assert "load_credentials" not in source
    assert "UrllibTransport" not in source
    assert "OpenAIResponsesAdapter" not in source
    assert "AnthropicMessagesAdapter" not in source


def _synthetic_generic_authorization() -> dict[str, object]:
    request = fresh_pilot_v2.load_request(ROOT)
    return {
        "schema_version": "agent-ops-owner-authorization-v1",
        "kind": "owner-authorization",
        "synthetic": True,
        "gate_id": fresh_pilot_v2.GATE_ID,
        "issue": fresh_pilot_v2.ISSUE,
        "pull_request": 0,
        "branch": fresh_pilot_v2.BRANCH,
        "commit": request["starting_main"],
        "task_contract_sha256": "sha256:" + "0" * 64,
        "tree_hashes": fresh_pilot_v2.execution_tree_hashes(ROOT),
        "authorized_at_utc": "2026-07-28T00:00:00+00:00",
        "expires_at_utc": "2099-01-01T00:00:00Z",
        "challenge": "SYNTHETIC-OFFLINE-ONLY",
        "owner_confirmation_statements": ["synthetic offline fixture"],
        "authorization_digest": "sha256:" + "1" * 64,
    }


def test_v2_live_driver_uses_distinct_private_root() -> None:
    path = private_state_root().as_posix()
    assert path.endswith("/treasurebench-agents-v1/repair-confirmation-v2")
    assert "repair-confirmation-v1" not in path


def test_v2_live_driver_stops_before_authorization_and_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    with pytest.raises(FileNotFoundError):
        run_live_fresh_pilot(ROOT)
    assert not (tmp_path / "state").exists()


def test_v2_staged_mock_driver_completes_and_resumes_without_calls(tmp_path: Path) -> None:
    root = tmp_path / "fresh-v2-mock-live"
    authorization = _synthetic_generic_authorization()
    first, first_adapters = run_mock_fresh_pilot(
        ROOT,
        authorization=authorization,
        root=root,
    )
    assert first["status"] == "pass"
    assert first["campaign_id"] == fresh_pilot_v2.CAMPAIGN_ID
    assert first["batch_id"] == fresh_pilot_v2.BATCH_ID
    assert first["private_runs"] == 500
    assert first["method_a_b_disagreements"] == 0
    assert first["method_c_failures"] == 0
    assert first["invalid_final_action_cardinalities"] == 0
    assert first["metric_range_errors"] == 0
    assert first["incomplete_pairings"] == 0
    assert first["contamination_findings"] == 0
    assert first["provider_phase_closed"] is True
    assert first["output_lock_verified"] is True
    assert first["unseal_after_lock_verified"] is True
    assert first["exact_cost_reconciliation"] is True
    assert first["base_campaign_authorized"] is False
    assert sum(adapter.calls for adapter in first_adapters.values()) == 3016

    second, second_adapters = run_mock_fresh_pilot(
        ROOT,
        authorization=authorization,
        root=root,
    )
    assert second == first
    assert sum(adapter.calls for adapter in second_adapters.values()) == 0
