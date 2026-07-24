#!/usr/bin/env python3
"""Validate paper dependencies and enforce logical freeze blockers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
STABLE = {"tagged-release", "version-doi", "arxiv-version", "published"}


def audit() -> dict[str, Any]:
    source = yaml.safe_load(
        (ROOT / "docs/publication/paper-dependency-edges.yml").read_text(encoding="utf-8")
    )
    schema = json.loads(
        (ROOT / "docs/publication/paper-dependency-edges.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(source, schema)
    papers = {
        record["paper_id"]
        for record in yaml.safe_load(
            (ROOT / "docs/paper-lifecycle.yml").read_text(encoding="utf-8")
        )["records"]
    }
    claims = {
        record["id"]
        for record in yaml.safe_load((ROOT / "claims/claims.yml").read_text(encoding="utf-8"))[
            "claims"
        ]
    }
    edges = source["edges"]
    ids = {edge["edge_id"] for edge in edges}
    assert len(ids) == len(edges)
    roles: Counter[str] = Counter()
    blocked = 0
    for edge in edges:
        assert edge["source_paper"] in papers
        assert edge["target_paper"] in papers
        assert set(edge["claim_ids"]) <= claims
        assert edge["source_paper"] != edge["target_paper"]
        roles[edge["role"]] += 1
        if edge["role"] != "logical-required":
            continue
        satisfied = (
            edge["stable_identifier_current_status"] in STABLE
            or edge["self_containment_status"] == "satisfied-by-restatement"
        )
        if satisfied:
            assert not edge["submission_blocker"]
        else:
            assert edge["submission_blocker"]
            blocked += 1
    assert set(roles) == {
        "logical-required",
        "background",
        "companion-scope",
        "shared-method",
        "shared-definition",
        "counterboundary",
        "future-absorption",
        "synthesis-only",
    }
    return {"edges": len(edges), "roles": dict(sorted(roles.items())), "freeze_blockers": blocked}


if __name__ == "__main__":
    print(audit())
