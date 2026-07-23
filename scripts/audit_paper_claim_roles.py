#!/usr/bin/env python3
"""Validate editorial claim roles and active primary ownership."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def audit() -> dict[str, Any]:
    source = yaml.safe_load((ROOT / "docs/paper-claim-roles.yml").read_text())
    schema = json.loads((ROOT / "docs/paper-claim-roles.schema.json").read_text())
    jsonschema.validate(source, schema)
    ledger = yaml.safe_load((ROOT / "claims/claims.yml").read_text())["claims"]
    ledger_by_id = {claim["id"]: claim for claim in ledger}
    records = source["claims"]
    by_id = {record["claim_id"]: record for record in records}
    assert len(by_id) == len(records)
    assert set(by_id) == set(ledger_by_id)

    lifecycle = yaml.safe_load((ROOT / "docs/paper-lifecycle.yml").read_text())["records"]
    papers = {record["paper_id"]: record for record in lifecycle}
    active = {
        paper_id
        for paper_id, record in papers.items()
        if record["editorial_status"] in {"active", "living-synthesis"}
    }
    counts: Counter[str] = Counter()
    for claim_id, record in by_id.items():
        assert record["study_id"] == ledger_by_id[claim_id]["study_id"]
        role_pairs = {(role["paper_id"], role["role"]) for role in record["paper_roles"]}
        assert len(role_pairs) == len(record["paper_roles"])
        assert {paper for paper, _ in role_pairs} <= set(papers)
        primary = [paper for paper, role in role_pairs if role == "primary" and paper in active]
        assert len(primary) <= 1
        counts.update(role for _, role in role_pairs)
    for paper_id, record in papers.items():
        for claim_id in record["primary_paper_claims"]:
            assert {
                "paper_id": paper_id,
                "role": "primary",
            } in by_id[claim_id]["paper_roles"]
    return {"claims": len(records), "roles": dict(sorted(counts.items()))}


if __name__ == "__main__":
    print(audit())
