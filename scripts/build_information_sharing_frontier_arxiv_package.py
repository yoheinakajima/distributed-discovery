#!/usr/bin/env python3
"""Rebuild the historical Information Sharing Frontier arXiv source package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/information-sharing-frontier"
PDF_NAME = "When_Does_Information_Sharing_Improve_Decentralized_Discovery.pdf"
ARCHIVE_NAME = "information-sharing-frontier-arxiv-source.zip"
METADATA_PATH = PAPER / "arxiv-metadata.yml"
SOURCE_MEMBERS = [
    "main.tex",
    "abstract.tex",
    "generated/references.bib",
    "figures/architecture.tex",
    "figures/dependence-discovery.tex",
    "figures/evidence-authority-map.tex",
    "figures/incremental-curves.tex",
    "figures/registry-classification.tex",
    "figures/residual-frontier.tex",
    "figures/same-accuracy-profile.tex",
    "figures/selection-map.tex",
    "tables/action-budget-profiles.tex",
    "tables/channel-definitions.tex",
    "tables/claim-evidence-map.tex",
    "tables/equilibrium-formulas.tex",
    "tables/minimal-witnesses.tex",
    "tables/registry-counts.tex",
    "tables/sharing-paths.tex",
    "tables/strategic-gain-by-accuracy.tex",
    "tables/threshold-gap.tex",
]
RUNS = {
    "DD-019": "20260722T084145Z_DD-019_a77bb786_04a5e9f0c5",
    "DD-020": "20260722T142551Z_DD-020_3854fff6_37c11a850a",
    "DD-021": "20260722T185924Z_DD-021_3cdbbc40_2fea269a9a",
    "DD-022": "20260722T210334Z_DD-022_2376d5b7_ad67765ca8",
}
EVIDENCE_OUTPUTS = {
    "DD-019": ["profiles.json", "summary.json", "verification.json", "corruption-tests.json"],
    "DD-020": [
        "channel-profiles.json",
        "point-census.json",
        "summary.json",
        "verification.json",
        "corruption-tests.json",
    ],
    "DD-021": [
        "registry.json",
        "summary.json",
        "minimal-witnesses.json",
        "method-agreement-certificate.json",
        "verification.json",
        "corruption-tests.json",
    ],
    "DD-022": [
        "registry.json",
        "summary.json",
        "threshold-certificate.json",
        "verification.json",
        "corruption-tests.json",
    ],
}
README = """Information Sharing Frontier arXiv source package

Top-level TeX file: main.tex
Processor: PDFLaTeX
All figures and tables are generated TeX inputs; no external figure is required.
The bibliography input is generated/references.bib.
The evidence/ tree contains compact copies of the public immutable records cited
by the manuscript. These files support auditability and are not recomputed here.
"""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeError(f"expected mapping in {path}")
    return loaded


def _source_epoch() -> str:
    manifest_path = ROOT / "results/verified" / RUNS["DD-019"] / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stamp = datetime.fromisoformat(str(manifest["started_utc"]).replace("Z", "+00:00"))
    return str(int(stamp.timestamp()))


def _evidence_members() -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    index: dict[str, Any] = {
        "schema_version": 1,
        "source_commit": "66ba4449572b20c519a4629ef20cfc030fae1762",
        "repository": "https://github.com/yoheinakajima/distributed-discovery",
        "runs": {},
    }
    for study, run_id in RUNS.items():
        run = ROOT / "results/verified" / run_id
        manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        manifest_data = (run / "manifest.json").read_bytes()
        members[f"evidence/{study}/manifest.json"] = manifest_data
        outputs: dict[str, str] = {}
        for name in EVIDENCE_OUTPUTS[study]:
            path = run / "outputs" / name
            data = path.read_bytes()
            expected = manifest["outputs"][f"outputs/{name}"]
            if _sha256(data) != expected:
                raise RuntimeError(f"immutable evidence hash mismatch: {study}/{name}")
            members[f"evidence/{study}/outputs/{name}"] = data
            outputs[name] = expected
        index["runs"][study] = {
            "run_id": run_id,
            "manifest_sha256": _sha256(manifest_data),
            "outputs": outputs,
        }
    members["evidence/INDEX.json"] = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    return members


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
    with tempfile.TemporaryDirectory(prefix="isf-arxiv-package-") as temporary:
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
                env={**os.environ, "SOURCE_DATE_EPOCH": _source_epoch()},
                capture_output=True,
                text=True,
            )
            log = result.stdout + result.stderr
            if result.returncode:
                raise RuntimeError("portable source compilation failed\n" + log[-5000:])
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
    if validation["pdf_sha256"] != pdf_sha:
        raise RuntimeError("canonical PDF does not match its validation receipt")
    if metadata["status"] != "working-paper" or metadata["submitted"] is not True:
        raise RuntimeError("public metadata must remain a submitted working-paper/preprint")
    if metadata["peer_reviewed"] is not False:
        raise RuntimeError("submission metadata must remain not peer reviewed")
    if metadata["arxiv_id"] != "2609.01814" or metadata["doi"] != "10.48550/arXiv.2609.01814":
        raise RuntimeError("public arXiv identifiers do not match the recorded v1")
    if metadata["doi_registration_status"] != "pending-at-observation":
        raise RuntimeError("DOI registration status must remain explicitly pending at observation")
    if metadata["primary_category"] != "cs.AI" or metadata["cross_list_categories"] != ["cs.GT"]:
        raise RuntimeError("public arXiv category metadata does not match the recorded v1")
    if metadata["arxiv_license"] != "arXiv-perpetual-non-exclusive-1.0":
        raise RuntimeError("the recorded arXiv license does not match the public v1")

    members = {name: (PAPER / name).read_bytes() for name in SOURCE_MEMBERS}
    members.update(_evidence_members())
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
        "paper_id": "information-sharing-frontier",
        "status": "public-arxiv-v1-record",
        "submitted": True,
        "peer_reviewed": False,
        "arxiv_id": metadata["arxiv_id"],
        "doi": metadata["doi"],
        "doi_registration_status": metadata["doi_registration_status"],
        "source_archive": {
            "path": archive_path.name,
            "sha256": archive_sha,
            "members": {name: _sha256(data) for name, data in sorted(members.items())},
            "host_paths_absent": True,
            "portable_compile_twice": True,
            "compiled_pdf_sha256": compiled_hashes,
        },
        "pdf": {
            "path": canonical_pdf_path.name,
            "sha256": pdf_sha,
            "page_count": validation["page_count"],
        },
        "metadata": {
            "path": "SUBMISSION_METADATA.yml",
            "sha256": _sha256((output_dir / "SUBMISSION_METADATA.yml").read_bytes()),
            "primary_category": metadata["primary_category"],
            "cross_list_categories": metadata["cross_list_categories"],
            "arxiv_license": metadata["arxiv_license"],
        },
    }
    (output_dir / "package-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checklist = f"""# Information Sharing Frontier arXiv v1 source-record checklist

- Historical source archive reconstructed as `{ARCHIVE_NAME}` (SHA-256 `{archive_sha}`).
- The recorded public arXiv v1 is `2609.01814`, primary `cs.AI`, cross-list `cs.GT`.
- The recorded arXiv license is perpetual non-exclusive distribution, not CC BY 4.0.
- The displayed DOI is `10.48550/arXiv.2609.01814`; DataCite registration was pending
  at observation, so this receipt does not claim DOI registration or resolution.
- This is a receipt only. Do not upload, edit, resubmit, withdraw, or otherwise act at
  arXiv from this package.

Canonical repository PDF SHA-256: `{pdf_sha}`.
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
