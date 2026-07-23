#!/usr/bin/env python3
"""Validate paper lifecycle without changing scientific authority."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
FORMAL_PUBLICATION = {"submitted", "accepted"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit() -> dict[str, Any]:
    source = yaml.safe_load((ROOT / "docs/paper-lifecycle.yml").read_text())
    schema = json.loads((ROOT / "docs/paper-lifecycle.schema.json").read_text())
    jsonschema.validate(source, schema)
    records = source["records"]
    by_id = {record["paper_id"]: record for record in records}
    assert len(by_id) == len(records)
    canonical = [r for r in records if r["lifecycle_class"] == "canonical-published"]
    assert len(canonical) == 1
    anchor = canonical[0]
    assert anchor["paper_id"] == "shared-discovery-paradox"
    assert anchor["build_policy"] == "external-read-only"
    assert anchor["upstream_lock"] == "integrations/shared-discovery-paradox/upstream.lock"
    lock = yaml.safe_load((ROOT / anchor["upstream_lock"]).read_text())
    publication = lock["publication_metadata"]
    assert anchor["pdf_sha256"] == publication["paper_pdf_sha256"]
    assert anchor["page_count"] == publication["paper_page_count"]
    assert not publication["doi_evidence"]
    assert not publication["submitted_evidence"]
    assert not publication["accepted_evidence"]
    assert not publication["peer_review_evidence"]
    assert not anchor["editable_fields"]

    ledger_ids = {
        claim["id"] for claim in yaml.safe_load((ROOT / "claims/claims.yml").read_text())["claims"]
    }
    local_count = 0
    for record in records:
        assert set(record["primary_paper_claims"]) <= ledger_ids
        assert anchor["paper_id"] not in record["supersedes"]
        if record["publication_status"] in FORMAL_PUBLICATION:
            assert record["publication_evidence"]
        if record["editorial_status"] == "superseded":
            replacement = record["superseded_by"]
            assert replacement in by_id
            assert by_id[replacement]["editorial_status"] in {"active", "living-synthesis"}
        if record["editorial_status"] == "archived-source":
            assert record["archive_reason"] and record["archive_date"]
        if record["scientific_status"] == "withdrawn-for-error":
            assert record["scientific_correction_record"]
            assert record["lifecycle_class"] == "withdrawn-with-reason"
        if record["paper_id"] == anchor["paper_id"]:
            continue
        local_count += 1
        source_path = ROOT / record["source_path"]
        assert source_path.is_file()
        directory = source_path.parent
        validation = json.loads((directory / "validation.json").read_text())
        pdfs = list(directory.glob("*.pdf"))
        assert len(pdfs) == 1
        assert _sha256(pdfs[0]) == record["pdf_sha256"] == validation["pdf_sha256"]
        assert record["page_count"] == validation["page_count"]
        assert record["route"].startswith("publications/")
        assert record["download"].startswith("downloads/")
        assert record["build_policy"] == "active-deterministic-build"
    assert local_count == 7
    active_primary = [
        (r["primary_theorem_family"], r["paper_id"])
        for r in records
        if r["editorial_status"] == "active" and r["primary_theorem_family"]
    ]
    assert len({family for family, _ in active_primary}) == len(active_primary)
    return {
        "records": len(records),
        "canonical": anchor["paper_id"],
        "local": local_count,
        "archived_or_superseded": sum(
            r["editorial_status"] in {"archived-source", "superseded"} for r in records
        ),
    }


if __name__ == "__main__":
    print(audit())
