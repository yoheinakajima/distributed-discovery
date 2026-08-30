from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CURRENT_SOURCE = ROOT / "papers/information-sharing-frontier/main.tex"
CURRENT_PDF = (
    ROOT
    / "papers/information-sharing-frontier"
    / "When_Does_Information_Sharing_Improve_Decentralized_Discovery.pdf"
)
CURRENT_SOURCE_SHA256 = "3e671abbd5381d29fe55e273d153aa2ec5124d311103bd75ba6444e40e5fad32"
CURRENT_PDF_SHA256 = "cfc892fd1a74f6fc7ebbc9b4152f678f4696448e37fdeb46ba376f0ac30a4c58"
RELEASE_SOURCE_REVISION = "3ca173f4e9e81a6d0e3e56205e428c596edc050e"
RELEASE_SOURCE_SHA256 = "41cb86cb4ea4fc1221c3fb4c88a31418b2f5bff0fbc35777d9c895e35084982f"
RELEASE_PDF_SHA256 = "a317e8851a84b494d8ef30eccc1e31dd4448dc1bbcd3fb2de0fc2849bd581a13"
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
    return next(
        record for record in records if record["paper_id"] == "information-sharing-frontier"
    )


def test_current_information_sharing_pointers_use_revised_artifact() -> None:
    lifecycle = yaml.safe_load((ROOT / "docs/paper-lifecycle.yml").read_text())
    citation = yaml.safe_load((ROOT / "docs/publication/paper-citation-metadata.yml").read_text())
    lifecycle_record = _paper(lifecycle["records"])
    citation_record = _paper(citation["papers"])
    example = next(
        record
        for record in citation["examples"]
        if record["paper_id"] == "information-sharing-frontier"
    )

    assert _sha256(CURRENT_SOURCE.read_bytes()) == CURRENT_SOURCE_SHA256
    assert _sha256(CURRENT_PDF.read_bytes()) == CURRENT_PDF_SHA256
    assert lifecycle_record["pdf_sha256"] == CURRENT_PDF_SHA256
    assert lifecycle_record["page_count"] == 28
    assert lifecycle_record["publication_status"] == "public-working-paper"
    assert citation_record["pdf_sha256"] == CURRENT_PDF_SHA256
    assert citation_record["version"] == f"repository-artifact-sha256-{CURRENT_PDF_SHA256}"
    assert example["artifact_sha256"] == CURRENT_PDF_SHA256
    assert CURRENT_PDF_SHA256 in (ROOT / "papers/README.md").read_text()


def test_compendium_v010_keeps_information_sharing_snapshot() -> None:
    content_path = ROOT / "docs/releases/compendium-v0.1.0-content.yml"
    registry = yaml.safe_load(content_path.read_text())
    release_record = _paper(registry["papers"])

    assert _sha256(content_path.read_bytes()) == RELEASE_CONTENT_SHA256
    assert release_record["pdf_sha256"] == RELEASE_PDF_SHA256
    assert release_record["main_source_sha256"] == RELEASE_SOURCE_SHA256
    assert release_record["page_count"] == 26
    assert RELEASE_PDF_SHA256 != CURRENT_PDF_SHA256
    assert RELEASE_SOURCE_SHA256 != CURRENT_SOURCE_SHA256


def test_compendium_information_sharing_bytes_come_from_frozen_git_tree() -> None:
    source_path = "papers/information-sharing-frontier/main.tex"
    pdf_path = (
        "papers/information-sharing-frontier/"
        "When_Does_Information_Sharing_Improve_Decentralized_Discovery.pdf"
    )
    content_path = "docs/releases/compendium-v0.1.0-content.yml"

    assert _sha256(_git_blob(RELEASE_SOURCE_REVISION, source_path)) == RELEASE_SOURCE_SHA256
    assert _sha256(_git_blob(RELEASE_SOURCE_REVISION, pdf_path)) == RELEASE_PDF_SHA256
    assert _sha256(_git_blob(RELEASE_SOURCE_REVISION, content_path)) == RELEASE_CONTENT_SHA256
