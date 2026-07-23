#!/usr/bin/env python3
"""Validate the editorial translation concordance against repository authority."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPERS = {
    "shared-discovery-paradox",
    "foundations",
    "three-results",
    "discovery-institutions",
    "common-source-trap",
    "incentive-to-ignore",
    "threshold-discovery",
    "information-sharing-frontier",
}
COMMUNITIES = {"or-ms", "economics-agt", "multi-agent-ai", "practitioner"}


def audit() -> dict[str, object]:
    source = yaml.safe_load(
        (ROOT / "docs/translation/community-concordance.yml").read_text(encoding="utf-8")
    )
    schema = json.loads(
        (ROOT / "docs/translation/community-concordance.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(source, schema)
    claim_ids = {
        claim["id"] for claim in yaml.safe_load((ROOT / "claims/claims.yml").read_text())["claims"]
    }
    study_ids = {
        yaml.safe_load(path.read_text())["study_id"]
        for path in (ROOT / "studies").glob("DD-*/status.yml")
    }
    literature_ids = {
        entry["adjacency_id"]
        for entry in yaml.safe_load((ROOT / "docs/literature/family-coverage.yml").read_text())[
            "entries"
        ]
    }
    entries = source["entries"]
    object_ids = {entry["object_id"] for entry in entries}
    assert len(object_ids) == len(entries)
    labels = {entry["canonical_label"] for entry in entries}
    assert len(labels) == len(entries)
    formulations = 0
    for entry in entries:
        assert {item["community"] for item in entry["formulations"]} == COMMUNITIES
        for item in entry["formulations"]:
            assert item["canonical_object"] == entry["object_id"]
            assert set(item["claim_ids"]) <= claim_ids
            assert set(item["study_ids"]) <= study_ids
            assert set(item["paper_owners"]) <= PAPERS
            assert set(item["literature_coverage"]) <= literature_ids
            formulations += 1
    assert source["retrievability_monitoring"] == {
        "search_rank": False,
        "ai_referrers": False,
        "predeclared_queries": False,
        "citation_rank": False,
        "semantic_visibility": False,
        "discoverybench_contamination_only": True,
    }
    return {"objects": len(entries), "formulations": formulations}


if __name__ == "__main__":
    print(audit())
