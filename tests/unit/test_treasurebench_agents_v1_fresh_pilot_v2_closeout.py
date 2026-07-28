from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _closeout() -> dict[str, object]:
    value = yaml.safe_load(
        (ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v2-closeout.yml").read_text(
            encoding="utf-8"
        )
    )
    assert isinstance(value, dict)
    return value


def test_fresh_pilot_v2_public_closeout_is_exact_quarantine() -> None:
    closeout = _closeout()
    assert closeout["status"] == "quarantined"
    assert closeout["decision"] == "fresh-pilot-v2-quarantined-engineering-only"
    assert closeout["campaign_id"] == "treasurebench-agents-v1-repair-confirmation-v2"
    assert closeout["batch_id"] == "tb-agents-v1-repair-confirmation-v2-b01"

    executed = closeout["executed"]
    assert isinstance(executed, dict)
    assert executed["stage"] == "custody"
    assert executed["failure_class"] == "custody-creation-failure"
    assert executed["attempts"] == executed["successes"] == 2
    assert executed["private_runs"] == 0
    assert executed["OpenAI_calls"] == executed["Anthropic_calls"] == 1
    assert executed["input_tokens"] == 1349
    assert executed["output_tokens"] == 253
    assert Decimal(str(executed["cost_usd"])) == Decimal("0.0076095")
    provider_cost = executed["provider_cost_usd"]
    assert isinstance(provider_cost, dict)
    assert sum((Decimal(str(value)) for value in provider_cost.values()), Decimal()) == Decimal(
        "0.0076095"
    )


def test_fresh_pilot_v2_closeout_preserves_lock_and_redaction_boundaries() -> None:
    closeout = _closeout()
    lock = closeout["lock"]
    assert isinstance(lock, dict)
    assert lock["provider_phase_closed"] is True
    assert lock["provider_calls_after_lock"] == 0
    assert lock["output_lock_verified"] is True
    assert lock["minimum_unseal_performed"] is False
    assert lock["objects_locked"] == 8

    custody = closeout["custody"]
    assert isinstance(custody, dict)
    assert custody["retained_state_preserved"] is True
    assert custody["os_csprng_seed_created"] is True
    assert custody["task_ciphertext_created"] is False
    assert custody["answer_ciphertext_created"] is False
    assert custody["custody_manifest_created"] is False

    redaction = closeout["redaction"]
    assert isinstance(redaction, dict)
    assert redaction["status"] == "pass"
    assert all(value is False for name, value in redaction.items() if name != "status")

    disposition = closeout["disposition"]
    assert isinstance(disposition, dict)
    assert disposition["further_provider_calls_permitted"] is False
    assert disposition["replacement_or_splice_performed"] is False
    assert disposition["semantic_retry_performed"] is False
    assert disposition["campaign_and_batch_permanently_quarantined"] is True


def test_fresh_pilot_v2_closeout_creates_no_scientific_or_release_authority() -> None:
    authority = _closeout()["authority"]
    assert isinstance(authority, dict)
    assert all(value is False for value in authority.values())
