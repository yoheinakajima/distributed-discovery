#!/usr/bin/env python3
"""Build and verify the owner-gated Common-Source Trap arXiv handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.papers.build_common_source_trap import _source_epoch

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/common-source-trap"
PDF_NAME = "The_Common_Source_Trap.pdf"
ARCHIVE_NAME = "common-source-trap-arxiv-source.zip"
METADATA_PATH = PAPER / "arxiv-metadata.yml"
SOURCE_MEMBERS = [
    "main.tex",
    "generated/atlas-slice.tex",
    "generated/discovery-gap.tex",
    "generated/equilibrium-counts.tex",
    "generated/evidence-status-table.tex",
    "generated/experiment-map.tex",
    "generated/independence-gap.tex",
    "generated/interventions.tex",
    "generated/planner-counts.tex",
    "generated/references.bib",
    "generated/trap-region.tex",
    "generated/welfare-gap.tex",
]
README = """Common-Source Trap arXiv source package

Top-level TeX file: main.tex
Processor: PDFLaTeX
All figures are generated TeX inputs under generated/; no external figure file is required.
The bibliography input is generated/references.bib.
"""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeError(f"expected mapping in {path}")
    return loaded


def _write_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(info, members[name])


def _compile_twice(archive_path: Path, expected_pdf: bytes) -> list[str]:
    hashes: list[str] = []
    with tempfile.TemporaryDirectory(prefix="cst-arxiv-package-") as temporary:
        extracted = Path(temporary) / "source"
        extracted.mkdir()
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            if any(Path(name).is_absolute() or ".." in Path(name).parts for name in names):
                raise RuntimeError("archive contains a non-portable path")
            archive.extractall(extracted)
        for index in range(2):
            output = Path(temporary) / f"build-{index}"
            output.mkdir()
            result = subprocess.run(
                ["tectonic", "main.tex", "--outdir", str(output)],
                cwd=extracted,
                env={**os.environ, "SOURCE_DATE_EPOCH": _source_epoch(ROOT)},
                capture_output=True,
                text=True,
            )
            log = result.stdout + result.stderr
            if result.returncode:
                raise RuntimeError("portable source compilation failed\n" + log[-4000:])
            pdf = (output / "main.pdf").read_bytes()
            hashes.append(_sha256(pdf))
            if pdf != expected_pdf:
                raise RuntimeError("portable source build differs from the canonical PDF")
    return hashes


def build(output_dir: Path) -> dict[str, Any]:
    validation = _load_yaml(PAPER / "validation.json")
    metadata = _load_yaml(METADATA_PATH)
    pdf = (PAPER / PDF_NAME).read_bytes()
    pdf_sha = _sha256(pdf)
    if validation["pdf_sha256"] != pdf_sha or validation["page_count"] != 21:
        raise RuntimeError("canonical PDF does not match its validation receipt")
    if metadata["submitted"] is not False or metadata["doi"] is not None:
        raise RuntimeError("submission metadata must remain unsubmitted with no DOI")
    if metadata["arxiv_license"] != "owner-selection-required":
        raise RuntimeError("the irrevocable arXiv license must remain an owner choice")

    members = {name: (PAPER / name).read_bytes() for name in SOURCE_MEMBERS}
    members["00README"] = README.encode("utf-8")
    source_text = b"\n".join(members.values())
    if b"/Users/" in source_text or b"file://" in source_text:
        raise RuntimeError("source package contains a host-specific path")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / ARCHIVE_NAME
    _write_zip(archive_path, members)
    canonical_pdf_path = output_dir / PDF_NAME
    canonical_pdf_path.write_bytes(pdf)
    shutil.copy2(METADATA_PATH, output_dir / "SUBMISSION_METADATA.yml")
    compiled_hashes = _compile_twice(archive_path, pdf)

    archive_sha = _sha256(archive_path.read_bytes())
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "paper_id": "common-source-trap",
        "status": "owner-upload-gated",
        "submitted": False,
        "doi": None,
        "source_archive": {
            "path": archive_path.name,
            "sha256": archive_sha,
            "members": {name: _sha256(data) for name, data in sorted(members.items())},
            "host_paths_absent": True,
            "portable_compile_twice": True,
            "compiled_pdf_sha256": compiled_hashes,
        },
        "pdf": {"path": canonical_pdf_path.name, "sha256": pdf_sha, "page_count": 21},
        "metadata": {
            "path": "SUBMISSION_METADATA.yml",
            "sha256": _sha256((output_dir / "SUBMISSION_METADATA.yml").read_bytes()),
            "primary_category_recommendation": metadata["primary_category_recommendation"],
            "cross_list_candidates": metadata["cross_list_candidates"],
            "arxiv_license": metadata["arxiv_license"],
        },
    }
    manifest_path = output_dir / "package-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    checklist = f"""# Common-Source Trap owner upload checklist

- Upload `{ARCHIVE_NAME}` (SHA-256 `{archive_sha}`).
- Confirm arXiv detects `main.tex` and PDFLaTeX, then inspect all 21 rendered pages.
- Copy the title, author, abstract, and category fields from `SUBMISSION_METADATA.yml`.
- Confirm primary category `cs.GT`; add `econ.TH` only if the arXiv interface permits
  the cross-list.
- Choose the arXiv distribution license personally; the package intentionally does not preselect it.
- Confirm the submission remains a working paper with DOI blank until arXiv assigns an identifier.
- Stop before the final Submit Article action unless that external action is separately authorized.

Canonical PDF SHA-256: `{pdf_sha}`.
"""
    (output_dir / "OWNER_UPLOAD_CHECKLIST.md").write_text(checklist, encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
