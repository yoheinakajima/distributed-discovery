#!/usr/bin/env python3
"""Validate the immutable release registry and offline release tooling."""

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
    assert cff["title"] == "Distributed Discovery Research Compendium"
    assert cff["type"] == "software"
    assert cff["license"] == "MIT"
    assert cff["version"] == "0.1.0"
    assert str(cff["date-released"]) == "2026-07-24"
    assert cff["doi"] == "10.5281/zenodo.21535005"
    assert not (ROOT / ".zenodo.json").exists()

    release_registry = yaml.safe_load((ROOT / "docs/releases/releases.yml").read_text())
    release_schema = json.loads((ROOT / "docs/releases/releases.schema.json").read_text())
    jsonschema.validate(
        release_registry,
        release_schema,
        format_checker=jsonschema.FormatChecker(),
    )
    assert release_registry["citation_convention"] == {
        "exact_version": "10.5281/zenodo.21535005",
        "evolving_compendium": "10.5281/zenodo.21535004",
    }
    assert len(release_registry["releases"]) == 1
    release = release_registry["releases"][0]
    assert release["version"] == "0.1.0"
    assert release["tag"] == "dd-compendium-v0.1.0"
    assert release["tag_type"] == "annotated"
    assert release["tag_object"] == "0fa9bd22b9a49a0e028e6fccda60b9bc2dadc7f6"
    assert release["source_revision"] == "3ca173f4e9e81a6d0e3e56205e428c596edc050e"
    assert release["status"] == "published-zenodo-verified"
    assert len(release["custom_assets"]) == 5
    assert release["fresh_download_verification"] == "byte-identical"
    assert release["zenodo"]["record_id"] == 21535005
    assert release["zenodo"]["version_doi"] == cff["doi"]
    assert release["papers"]["peer_review_implied"] is False
    assert release["scientific_inventory"] == {
        "claims": 110,
        "maximum_claim_id": "DD-C-0110",
        "studies": 26,
        "maximum_study_id": "DD-022",
        "run_manifests": 51,
        "passing_immutable_runs": 48,
    }
    source_available = (
        subprocess.run(
            ["git", "cat-file", "-e", f"{release['source_revision']}^{{commit}}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )
    if source_available:
        resolved_source = subprocess.run(
            ["git", "rev-parse", f"{release['source_revision']}^{{commit}}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert resolved_source == release["source_revision"]
    tags = subprocess.run(
        ["git", "tag", "--list"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if release["tag"] in tags:
        tag_type = subprocess.run(
            ["git", "cat-file", "-t", release["tag"]],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        tag_target = subprocess.run(
            ["git", "rev-list", "-n", "1", release["tag"]],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert tag_type == "tag"
        assert tag_target == release["source_revision"]
    return {
        "manifest": "dry-run-only",
        "artifacts": len(dry_run["artifacts"]),
        "pages": sum(item["page_count"] for item in dry_run["artifacts"]),
        "release": release["status"],
        "tag": release["tag"],
        "version_doi": release["zenodo"]["version_doi"],
        "concept_doi": release["zenodo"]["concept_doi"],
    }


if __name__ == "__main__":
    print(audit())
