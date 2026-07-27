from __future__ import annotations

from pathlib import Path

import pytest

from distributed_discovery.benchmark.agents_v1 import fresh_pilot
from distributed_discovery.benchmark.agents_v1.fresh_pilot_live import (
    audit_live_corruptions,
    private_state_root,
    run_live_fresh_pilot,
    run_mock_fresh_pilot,
)

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


def test_all_fresh_live_corruptions_reject() -> None:
    outcomes = audit_live_corruptions(ROOT)
    assert len(outcomes) >= 8
    assert all(item["status"] == "rejected" for item in outcomes)


def test_fresh_offline_module_has_no_provider_or_credential_runtime() -> None:
    source = (ROOT / "src/distributed_discovery/benchmark/agents_v1/fresh_pilot.py").read_text(
        encoding="utf-8"
    )
    assert "load_credentials" not in source
    assert "UrllibTransport" not in source
    assert "OpenAIResponsesAdapter" not in source
    assert "AnthropicMessagesAdapter" not in source


def _synthetic_generic_authorization() -> dict[str, object]:
    return {
        "schema_version": "agent-ops-owner-authorization-v1",
        "kind": "owner-authorization",
        "synthetic": True,
        "gate_id": fresh_pilot.GATE_ID,
        "issue": fresh_pilot.ISSUE,
        "pull_request": 197,
        "branch": fresh_pilot.BRANCH,
        "commit": fresh_pilot._git(ROOT, "rev-parse", "HEAD"),
        "task_contract_sha256": "sha256:" + "0" * 64,
        "tree_hashes": fresh_pilot.execution_tree_hashes(ROOT),
        "authorized_at_utc": "2026-07-27T00:00:00+00:00",
        "expires_at_utc": "2099-01-01T00:00:00Z",
        "challenge": "SYNTHETIC-OFFLINE-ONLY",
        "owner_confirmation_statements": ["synthetic offline fixture"],
        "authorization_digest": "sha256:" + "1" * 64,
    }


def test_fresh_live_driver_uses_distinct_private_root() -> None:
    path = private_state_root().as_posix()
    assert path.endswith("/treasurebench-agents-v1/repair-confirmation-v1")
    assert "/pilot-v1" not in path


def test_fresh_live_driver_fails_before_authorization_or_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    with pytest.raises(FileNotFoundError):
        run_live_fresh_pilot(ROOT)
    assert not (tmp_path / "state").exists()


def test_fresh_staged_driver_passes_with_mocks_and_resumes_without_calls(
    tmp_path: Path,
) -> None:
    root = tmp_path / "fresh-mock-live"
    authorization = _synthetic_generic_authorization()
    first, first_adapters = run_mock_fresh_pilot(ROOT, authorization=authorization, root=root)
    assert first["status"] == "pass"
    assert first["campaign_id"] == fresh_pilot.CAMPAIGN_ID
    assert first["batch_id"] == fresh_pilot.BATCH_ID
    assert first["tasks"] == 50
    assert first["private_runs"] == 500
    assert first["method_a_b_disagreements"] == 0
    assert first["contamination_findings"] == 0
    assert first["protocol_errors"] == 0
    assert first["provider_phase_closed"] is True
    assert first["output_lock_verified"] is True
    assert first["unseal_after_lock_verified"] is True
    assert first["base_campaign_authorized"] is False
    assert sum(adapter.calls for adapter in first_adapters.values()) > 0

    second, second_adapters = run_mock_fresh_pilot(ROOT, authorization=authorization, root=root)
    assert second == first
    assert sum(adapter.calls for adapter in second_adapters.values()) == 0
