#!/usr/bin/env python3
"""Audit structural literature transmission without judging novelty."""

from __future__ import annotations

import re
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def audit() -> dict[str, int]:
    registry = yaml.safe_load((ROOT / "docs/literature/family-coverage.yml").read_text())
    schema = __import__("json").loads(
        (ROOT / "docs/literature/family-coverage.schema.json").read_text()
    )
    jsonschema.validate(registry, schema)
    assert all(value is False for value in registry["audit_limits"].values())
    entries = registry["entries"]
    ids = [entry["adjacency_id"] for entry in entries]
    assert len(ids) == len(set(ids))
    assert set(registry["required_adjacencies"]) == {
        entry["adjacency_id"] for entry in entries if entry["disposition"] == "required"
    }
    bib = (ROOT / "bibliography/references.bib").read_text()
    bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.MULTILINE))
    citation_checks = 0
    for entry in entries:
        assert set(entry["primary_keys"]) <= bib_keys
        assert set(entry["paper_slugs"]) == set(entry["anchors"])
        paper_sources = []
        for slug in entry["paper_slugs"]:
            source = (ROOT / "papers" / slug / "main.tex").read_text()
            assert entry["anchors"][slug] in source
            paper_sources.append(source)
        transmitted = "\n".join(paper_sources)
        for key in entry["primary_keys"]:
            assert re.search(r"\\cite\w*\{[^}]*\b" + re.escape(key) + r"\b", transmitted)
            citation_checks += 1
    return {"entries": len(entries), "citation_checks": citation_checks}


if __name__ == "__main__":
    print(audit())
