from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/audit_treasurebench_agents_v1_fresh_pilot_closeout.py"


def test_public_safe_fresh_pilot_closeout_is_exact_and_quarantined() -> None:
    spec = importlib.util.spec_from_file_location("audit_fresh_pilot_closeout", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.audit()
    assert result["status"] == "pass"
    assert result["decision"] == "sealed-pilot-quarantined-provider-failure"
    assert result["calls"] == {"OpenAI": 1, "Anthropic": 0}
    assert result["reported_tokens"] == 0
    assert result["cost_usd"] == "0.00"
    assert result["private_runs"] == 0
    assert result["provider_phase"] == "closed"
    assert result["private_state_accessed_by_audit"] is False
