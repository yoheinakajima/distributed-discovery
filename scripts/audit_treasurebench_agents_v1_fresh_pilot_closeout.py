#!/usr/bin/env python3
"""Audit only the committed public-safe AO-0002 quarantined closeout."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT = ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-closeout.yml"
LOCK = ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-output-lock-commitment.yml"
HANDOFF = ROOT / "reports/agent-ops/AO-0002-stop-by-policy-handoff.yml"

DECISION = "sealed-pilot-quarantined-provider-failure"
CAMPAIGN = "treasurebench-agents-v1-repair-confirmation-v1"
BATCH = "tb-agents-v1-repair-confirmation-v1-b01"
EXECUTION_COMMIT = "fe313602df7f4e8ffac1a1a02c2b3a83f3c72943"
OUTPUT_LOCK = "sha256:8102a6c1b6bda003336d5503136dfe29301b04cb8f35e7740edd8d56f0eb3c1d"


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML mapping: {path}")
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def audit() -> dict[str, object]:
    """Validate exact redacted facts without touching credentials or private state."""

    closeout = _load(CLOSEOUT)
    lock = _load(LOCK)
    handoff = _load(HANDOFF)

    for record in (closeout, handoff):
        _require(record["decision"] == DECISION, "closeout decision changed")
    for record in (closeout, lock):
        _require(record["campaign_id"] == CAMPAIGN, "campaign identity changed")
        _require(record["batch_id"] == BATCH, "batch identity changed")
        _require(record["execution_commit"] == EXECUTION_COMMIT, "execution commit changed")

    executed = closeout["executed"]
    _require(isinstance(executed, dict), "executed summary is not a mapping")
    _require(executed["attempts"] == 1, "OpenAI canary attempt count changed")
    _require(executed["OpenAI_calls"] == 1, "OpenAI call count changed")
    _require(executed["Anthropic_calls"] == 0, "Anthropic call count changed")
    _require(executed["terminal_http_status"] == 400, "terminal status changed")
    _require(
        executed["error_classes"] == {"schema-or-parameter": 1},
        "terminal error class changed",
    )
    _require(executed["input_tokens"] == 0, "reported input tokens changed")
    _require(executed["output_tokens"] == 0, "reported output tokens changed")
    _require(executed["cost_usd"] == "0.00", "reported cost changed")
    _require(executed["private_runs"] == 0, "private run count changed")
    _require(executed["semantic_retries"] == 0, "semantic retry count changed")
    _require(executed["transport_retries"] == 0, "transport retry count changed")
    _require(executed["schema_repairs"] == 0, "schema repair count changed")

    custody = closeout["custody"]
    _require(isinstance(custody, dict), "custody summary is not a mapping")
    for key in (
        "os_csprng_task_seed_created",
        "task_key_created",
        "answer_key_created",
        "task_ciphertext_created",
        "answer_ciphertext_created",
        "custody_manifest_created",
    ):
        _require(custody[key] is False, f"forbidden custody object changed: {key}")
    _require(custody["tasks_created"] == 0, "private task count changed")
    _require(custody["answers_created"] == 0, "private answer count changed")

    lock_summary = closeout["lock"]
    _require(isinstance(lock_summary, dict), "lock summary is not a mapping")
    _require(
        lock_summary["output_lock_commitment"] == OUTPUT_LOCK,
        "closeout output lock changed",
    )
    _require(lock["output_lock_commitment"] == OUTPUT_LOCK, "lock commitment changed")
    _require(lock_summary["provider_phase_closed"] is True, "provider phase reopened")
    _require(lock_summary["provider_calls_after_lock"] == 0, "post-lock call occurred")
    _require(lock_summary["output_lock_verified"] is True, "output lock unverified")
    _require(lock_summary["unsealed_before_lock"] is False, "pre-lock unseal recorded")

    authority = closeout["authority"]
    _require(isinstance(authority, dict), "authority summary is not a mapping")
    _require(not any(authority.values()), "forbidden authority became true")
    _require(
        handoff["external_calls_cost"] == {"calls": 1, "cost": "0.00", "currency": "USD"},
        "handoff ledger changed",
    )
    _require(handoff["scientific_state_change"] == "none", "scientific state changed")

    return {
        "status": "pass",
        "task_id": "AO-0002",
        "decision": DECISION,
        "campaign_id": CAMPAIGN,
        "batch_id": BATCH,
        "execution_commit": EXECUTION_COMMIT,
        "calls": {"OpenAI": 1, "Anthropic": 0},
        "reported_tokens": 0,
        "cost_usd": "0.00",
        "private_runs": 0,
        "output_lock": OUTPUT_LOCK,
        "provider_phase": "closed",
        "private_state_accessed_by_audit": False,
    }


def main() -> None:
    print(json.dumps(audit(), sort_keys=True))


if __name__ == "__main__":
    main()
