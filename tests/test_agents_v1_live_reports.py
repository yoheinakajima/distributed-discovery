from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _yaml(relative: str) -> dict[str, object]:
    loaded = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_public_readiness_and_receipt_preserve_exact_boundary() -> None:
    decision = _yaml("reports/benchmark/agents-v1-provider-preflight-decision.yml")
    readiness = _yaml("reports/benchmark/agents-v1-provider-readiness.yml")
    assert decision["decision"] == readiness["overall_decision"]
    assert decision["accounting"]["cumulative_calls_across_all_attempts"] == 607
    assert decision["accounting"]["cumulative_cost_usd"] == "2.311758000"
    assert decision["scope"] == {
        "base_campaign_executed": False,
        "composite_score_created": False,
        "private_material_created": False,
        "provider_ranking_created": False,
        "public_tasks_only": True,
        "scientific_evidence_created": False,
        "sealed_pilot_executed": False,
    }
    for route_id in ("openai_direct", "anthropic_direct"):
        route = readiness["routes"][route_id]
        assert route["calibration_complete"] is True
        assert route["calibration_summary"]["cases"] == 50


def test_every_public_trace_has_reconciled_usage_totals() -> None:
    path = ROOT / "reports/benchmark/agents-v1-public-operational-traces.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 104
    for record in records:
        usage = record["registered_usage_totals"]
        assert usage["granularity"] == "trace-run-total"
        assert isinstance(usage["input_tokens"], int)
        assert isinstance(usage["output_tokens"], int)
        assert usage["calls"] >= len(record["trace"]["events"])


def test_editorial_reconciliation_is_complete_and_non_authorizing() -> None:
    report = _yaml("reports/editorial/four-paper-citation-review-reconciliation.yml")
    items = report["items"]
    assert len(items) == 28
    counts = Counter(item["disposition"] for item in items)
    assert all(counts[key] == value for key, value in report["summary"].items())
    assert sum(report["summary"].values()) == 28
    assert report["review_scope"]["paper_sources_edited"] is False
    assert report["calibration_authorizes_paper_action"] is False


def test_interpretation_map_uses_existing_owners_and_stays_prospective() -> None:
    report = _yaml("reports/editorial/discoverybench-to-paper-interpretation-map.yml")
    claims = _yaml("claims/claims.yml")
    claim_ids = {item["id"] for item in claims["claims"]}
    study_ids = {
        "-".join(path.parent.name.split("-")[:2]) for path in ROOT.glob("studies/DD-*/status.yml")
    }
    assert len(report["families"]) == 5
    for family in report["families"]:
        assert set(family["claim_owners"]) <= claim_ids
        assert set(family["study_owners"]) <= study_ids
        assert family["forbidden_generalization"]
    assert report["evidence_state"] == "no-sealed-or-claim-grade-results"
    assert report["paper_action_authorized"] is False


def test_publication_template_remains_on_hold() -> None:
    template = _yaml("reports/editorial/post-discoverybench-publication-implications-template.yml")
    assert template["activation_gate"]["public_calibration_satisfies_gate"] is False
    assert template["decision"]["paper_action"] == "hold"
