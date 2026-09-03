from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/build_information_sharing_frontier_arxiv_package.py"
PAPER = ROOT / "papers/information-sharing-frontier"


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("isf_arxiv_package", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_information_sharing_frontier_metadata_records_public_v1_without_doi_promotion() -> None:
    metadata = yaml.safe_load((PAPER / "arxiv-metadata.yml").read_text(encoding="utf-8"))
    assert metadata["status"] == "working-paper"
    assert metadata["submitted"] is True
    assert metadata["peer_reviewed"] is False
    assert metadata["arxiv_id"] == "2609.01814"
    assert metadata["doi"] == "10.48550/arXiv.2609.01814"
    assert metadata["doi_registration_status"] == "pending-at-observation"
    assert metadata["primary_category"] == "cs.AI"
    assert metadata["cross_list_categories"] == ["cs.GT"]
    assert metadata["arxiv_license"] == "arXiv-perpetual-non-exclusive-1.0"


def test_information_sharing_frontier_public_record_preserves_preparation_history() -> None:
    public_record = yaml.safe_load(
        (ROOT / "reports/editorial/information-sharing-frontier-arxiv-public-record.yml").read_text(
            encoding="utf-8"
        )
    )
    observation = public_record["public_arxiv_observation"]
    assert public_record["repository_binding"]["pdf_sha256"] == (
        "8d116b86cdbbc6cda66d65ac72077d29c15b05b86f4dc862ee8ec8e69d8f4ac0"
    )
    assert public_record["repository_binding"]["pdf_page_count"] == 28
    assert (
        public_record["repository_binding"]["arxiv_pdf_byte_identity"] == "unverified-not-asserted"
    )
    assert observation["arxiv_id"] == "2609.01814"
    assert observation["arxiv_submission_state"] == "submitted"
    assert observation["peer_review_venue_state"] == "unknown-not-asserted"
    assert "venue_state" not in observation
    assert observation["doi"] == "10.48550/arXiv.2609.01814"
    assert observation["doi_registration_status"] == "pending-at-observation"
    assert observation["primary_category"] == "cs.AI"
    assert observation["cross_list_categories"] == ["cs.GT"]
    assert observation["arxiv_license"] == "arXiv-perpetual-non-exclusive-1.0"
    assert observation["license_not"] == "CC-BY-4.0"
    assert (
        public_record["historical_preparation_receipt"]["rewritten_as_current_public_record"]
        is False
    )


def test_information_sharing_frontier_packager_starts_without_source_package(
    tmp_path: Path,
) -> None:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    completed = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--help"],
        cwd=tmp_path,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--output-dir" in completed.stdout
    assert "distributed_discovery" not in SCRIPT.read_text(encoding="utf-8")


def test_information_sharing_frontier_source_package_is_portable_and_exact(tmp_path: Path) -> None:
    module = _module()
    manifest = module.build(tmp_path)
    validation = yaml.safe_load((PAPER / "validation.json").read_text(encoding="utf-8"))
    archive_path = tmp_path / "information-sharing-frontier-arxiv-source.zip"
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        source = b"\n".join(archive.read(name) for name in names)

    assert names == sorted(names)
    assert "main.tex" in names
    assert "generated/references.bib" in names
    assert "evidence/DD-020/outputs/point-census.json" in names
    assert "evidence/DD-021/outputs/registry.json" in names
    assert "evidence/DD-022/outputs/registry.json" in names
    assert set(module.SOURCE_MEMBERS) <= set(names)
    assert not any(name.endswith(".pdf") for name in names)
    assert b"/Users/" not in source
    assert b"file://" not in source
    assert manifest["source_archive"]["portable_compile_twice"] is True
    assert manifest["source_archive"]["compiled_pdf_sha256"] == [
        validation["pdf_sha256"],
        validation["pdf_sha256"],
    ]
    assert manifest["pdf"]["sha256"] == validation["pdf_sha256"]
    assert manifest["status"] == "public-arxiv-v1-record"
    assert manifest["arxiv_id"] == "2609.01814"
    assert manifest["doi"] == "10.48550/arXiv.2609.01814"
    assert manifest["doi_registration_status"] == "pending-at-observation"
