from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def audit():
    path = ROOT / "scripts/audit_program_memory.py"
    spec = importlib.util.spec_from_file_location("audit_program_memory", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit()


def test_program_memory_registry_routes_every_record() -> None:
    result = audit()
    assert result["records"] >= 25
    assert result["owner_adopted_unrouted"] == 0
    assert result["duplicate_canonical_records"] == 0
    assert result["raw_transcripts"] == 0


def test_program_memory_preserves_due_categories() -> None:
    result = audit()
    assert result["classifications"]["capture-now"] >= 1
    assert result["classifications"]["evidence-dependent"] >= 1
    assert result["classifications"]["superseded"] >= 1
    assert result["statuses"]["rejected"] >= 1


def test_execplan_places_delta_audit_immediately_after_live_state() -> None:
    plan = (ROOT / "plans/PROGRAM_MEMORY_PREPRINT_INFRASTRUCTURE.md").read_text(encoding="utf-8")
    live_state = plan.index("## Live state")
    delta_audit = plan.index("## DISCUSSION AND DECISION DELTA AUDIT")
    next_heading = plan.find("\n## ", live_state + len("## Live state"))
    assert next_heading == delta_audit - 1
