#!/usr/bin/env python3
"""Validate release-readiness records without creating a release."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit() -> dict[str, Any]:
    schema = json.loads((ROOT / "docs/releases/release-evidence-manifest.schema.json").read_text())
    example = json.loads(
        (ROOT / "docs/releases/release-evidence-manifest.example.json").read_text()
    )
    dry_run = json.loads(
        (ROOT / "reports/releases/release-evidence-manifest.dry-run.json").read_text()
    )
    jsonschema.validate(example, schema)
    jsonschema.validate(dry_run, schema)
    assert dry_run["manifest_kind"] == "dry-run"
    assert dry_run["release_status"] == "dry-run-only"
    for field in (
        "tag",
        "source_revision",
        "github_release_url",
        "version_doi",
        "concept_doi",
        "generated_utc",
    ):
        assert dry_run[field] is None
    assert dry_run["inventory"] == {
        "claims": 110,
        "maximum_claim_id": "DD-C-0110",
        "studies": 26,
        "maximum_study_id": "DD-022",
        "manifests": 51,
        "passing_manifests": 48,
    }
    assert len(dry_run["artifacts"]) == 7
    assert sum(item["page_count"] for item in dry_run["artifacts"]) == 119
    for artifact in dry_run["artifacts"]:
        assert _sha256(ROOT / artifact["pdf_path"]) == artifact["pdf_sha256"]
        assert _sha256(ROOT / artifact["source_bundle"]) == artifact["source_sha256"]
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    assert cff["cff-version"] == "1.2.0"
    assert cff["title"] == "Distributed Discovery research workspace"
    assert cff["type"] == "software"
    assert cff["license"] == "MIT"
    assert "doi" not in cff
    assert not (ROOT / ".zenodo.json").exists()
    tags = subprocess.run(
        ["git", "tag", "--list"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert not tags
    return {
        "manifest": "dry-run-only",
        "artifacts": len(dry_run["artifacts"]),
        "pages": sum(item["page_count"] for item in dry_run["artifacts"]),
        "external_identifiers": None,
        "git_tags": 0,
    }


if __name__ == "__main__":
    print(audit())
