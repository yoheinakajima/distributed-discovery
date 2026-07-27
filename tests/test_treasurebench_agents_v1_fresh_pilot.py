from __future__ import annotations

from pathlib import Path

import pytest

from distributed_discovery.benchmark.agents_v1 import fresh_pilot

ROOT = Path(__file__).resolve().parents[1]


def test_fresh_registration_and_allocation_are_exact_and_separate() -> None:
    result = fresh_pilot.validate_registration(ROOT)
    slots = fresh_pilot.allocation_slots(ROOT)
    assert result["status"] == "pass"
    assert result["slots"] == 50
    assert result["runs"] == 500
    assert len({slot.slot_id for slot in slots}) == 50
    assert all(slot.slot_id.startswith("RC-SLOT-") for slot in slots)
    assert result["provider_calls"] == 0
    assert result["credential_reads"] == 0
    assert result["private_objects_created"] == 0
    assert result["spend_usd"] == "0"


def test_private_generation_fails_before_generic_owner_authorization() -> None:
    with pytest.raises(PermissionError, match="owner authorization"):
        fresh_pilot.generate_tasks(ROOT, material="forbidden", public_fixture=False)


def test_fresh_repaired_full_matrix_rehearsal() -> None:
    result = fresh_pilot.run_synthetic_rehearsal(ROOT)
    assert result["status"] == "pass"
    assert result["tasks"] == 50
    assert result["runs"] == 500
    assert result["method_a_b_errors"] == 0
    assert result["method_c_errors"] == 0
    assert result["metric_range_errors"] == 0
    assert result["output_lock_verified"] is True
    assert result["provider_calls"] == 0
    assert result["credential_reads"] == 0
    assert result["private_objects_created"] == 0
    assert result["external_cost_usd"] == "0"


def test_all_fresh_pilot_corruptions_reject() -> None:
    outcomes = fresh_pilot.audit_corruptions(ROOT)
    assert len(outcomes) >= 18
    assert all(item["status"] == "rejected" for item in outcomes)


def test_fresh_offline_module_has_no_provider_or_credential_runtime() -> None:
    source = (
        ROOT
        / "src/distributed_discovery/benchmark/agents_v1/fresh_pilot.py"
    ).read_text(encoding="utf-8")
    assert "load_credentials" not in source
    assert "UrllibTransport" not in source
    assert "OpenAIResponsesAdapter" not in source
    assert "AnthropicMessagesAdapter" not in source
