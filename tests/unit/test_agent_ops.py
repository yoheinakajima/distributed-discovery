from __future__ import annotations

import importlib.util
from pathlib import Path

from distributed_discovery.agent_ops.core import render_prompt

ROOT = Path(__file__).resolve().parents[2]


def _audit() -> dict[str, object]:
    path = ROOT / "scripts/audit_agent_ops.py"
    spec = importlib.util.spec_from_file_location("audit_agent_ops", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit()


def test_agent_operations_full_semantic_audit() -> None:
    result = _audit()
    assert result["schemas"] >= 7
    assert result["task_types"] == 7
    assert result["acceptance_profiles"] == 7
    assert result["scientific_authority"] == "unchanged"
    assert result["private_paths_or_secrets"] == 0


def test_fresh_pilot_preview_prompt_is_compact_and_nonexecuting(tmp_path: Path) -> None:
    output = render_prompt(
        ROOT / "reports/agent-ops/next-task-treasurebench-fresh-pilot.yml",
        output=tmp_path / "prompt.md",
    )
    text = output.read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 120
    assert output.stat().st_size <= 12 * 1024
    assert "do not execute" in text.lower()
    assert "no committed task contract" in text.lower()
