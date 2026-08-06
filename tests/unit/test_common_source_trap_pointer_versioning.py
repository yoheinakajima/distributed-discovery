from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "scripts/build_compendium_release.py"
CURRENT_SOURCE = ROOT / "papers/common-source-trap/main.tex"
CURRENT_PDF = ROOT / "papers/common-source-trap/The_Common_Source_Trap.pdf"
CURRENT_SOURCE_SHA256 = "87a6e85450c72fc9c93b281646ecfbd60193747c80aae9eac0a022301e1f06e1"
CURRENT_PDF_SHA256 = "ab53c6e4bd099234e42178646abdd7c9692533dfb0b63cea9d3d60ba1ccf1150"
RELEASE_SOURCE_REVISION = "3ca173f4e9e81a6d0e3e56205e428c596edc050e"
RELEASE_SOURCE_SHA256 = "2f7d9ead7e54a7c4b852935b9648361cc682772c5fe41853d0193b86ce3fbdad"
RELEASE_PDF_SHA256 = "afa9384eca60cf2a0291c2c42012f15ca59bf3d29b7c939b1882a0237ea58ff7"
RELEASE_CONTENT_SHA256 = "4964528d324a7d9bfdace1478ec5d7094bb66b798ccbc7842f9e268b4f5588a4"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(revision: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def _paper(records: list[dict[str, object]]) -> dict[str, object]:
    return next(record for record in records if record["paper_id"] == "common-source-trap")


def test_current_working_paper_pointers_use_the_revised_artifact() -> None:
    lifecycle = yaml.safe_load((ROOT / "docs/paper-lifecycle.yml").read_text())
    citation = yaml.safe_load((ROOT / "docs/publication/paper-citation-metadata.yml").read_text())
    lifecycle_record = _paper(lifecycle["records"])
    citation_record = _paper(citation["papers"])
    example = next(
        record for record in citation["examples"] if record["paper_id"] == "common-source-trap"
    )

    assert _sha256(CURRENT_SOURCE.read_bytes()) == CURRENT_SOURCE_SHA256
    assert _sha256(CURRENT_PDF.read_bytes()) == CURRENT_PDF_SHA256
    assert lifecycle_record["pdf_sha256"] == CURRENT_PDF_SHA256
    assert lifecycle_record["publication_status"] == "public-working-paper"
    assert citation_record["pdf_sha256"] == CURRENT_PDF_SHA256
    assert citation_record["version"] == f"repository-artifact-sha256-{CURRENT_PDF_SHA256}"
    assert example["artifact_sha256"] == CURRENT_PDF_SHA256
    assert CURRENT_PDF_SHA256 in (ROOT / "papers/README.md").read_text()


def test_compendium_v010_records_retain_the_immutable_release_artifact() -> None:
    content_path = ROOT / "docs/releases/compendium-v0.1.0-content.yml"
    registry = yaml.safe_load(content_path.read_text())
    dry_run = json.loads(
        (ROOT / "reports/releases/release-evidence-manifest.dry-run.json").read_text()
    )
    releases = yaml.safe_load((ROOT / "docs/releases/releases.yml").read_text())

    assert _sha256(content_path.read_bytes()) == RELEASE_CONTENT_SHA256
    assert releases["releases"][0]["source_revision"] == RELEASE_SOURCE_REVISION
    registry_record = _paper(registry["papers"])
    dry_run_record = _paper(dry_run["artifacts"])
    assert registry_record["pdf_sha256"] == RELEASE_PDF_SHA256
    assert registry_record["main_source_sha256"] == RELEASE_SOURCE_SHA256
    assert dry_run_record["pdf_sha256"] == RELEASE_PDF_SHA256
    assert dry_run_record["source_sha256"] == RELEASE_SOURCE_SHA256
    assert RELEASE_PDF_SHA256 != CURRENT_PDF_SHA256
    assert RELEASE_SOURCE_SHA256 != CURRENT_SOURCE_SHA256


def test_release_snapshot_hashes_are_resolved_from_the_registered_git_tree() -> None:
    source_path = "papers/common-source-trap/main.tex"
    pdf_path = "papers/common-source-trap/The_Common_Source_Trap.pdf"
    content_path = "docs/releases/compendium-v0.1.0-content.yml"
    assert _sha256(_git_blob(RELEASE_SOURCE_REVISION, source_path)) == RELEASE_SOURCE_SHA256
    assert _sha256(_git_blob(RELEASE_SOURCE_REVISION, pdf_path)) == RELEASE_PDF_SHA256
    assert _sha256(_git_blob(RELEASE_SOURCE_REVISION, content_path)) == RELEASE_CONTENT_SHA256


def test_release_builder_uses_the_snapshot_not_the_moving_worktree(tmp_path: Path) -> None:
    current_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    output = tmp_path / "release-candidate"
    completed = subprocess.run(
        [
            sys.executable,
            str(BUILD_SCRIPT),
            "--version",
            "0.1.0",
            "--source-revision",
            current_head,
            "--output-dir",
            str(output),
            "--mode",
            "dry-run",
            "--generated-utc",
            "2026-07-24T00:00:00Z",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    manifest_path = (
        output / "distributed-discovery-compendium-v0.1.0-release-evidence-manifest.json"
    )
    manifest = json.loads(manifest_path.read_text())
    archive_path = output / "distributed-discovery-compendium-v0.1.0-papers.zip"
    with zipfile.ZipFile(archive_path) as archive:
        archived_pdf = archive.read(
            "distributed-discovery-compendium-v0.1.0/papers/common-source-trap/"
            "The_Common_Source_Trap.pdf"
        )

    assert result["requested_build_revision"] == current_head
    assert result["release_source_revision"] == RELEASE_SOURCE_REVISION
    assert manifest["source_revision"] == RELEASE_SOURCE_REVISION
    assert _paper(manifest["artifacts"])["pdf_sha256"] == RELEASE_PDF_SHA256
    assert _sha256(archived_pdf) == RELEASE_PDF_SHA256
