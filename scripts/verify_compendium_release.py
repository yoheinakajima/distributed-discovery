#!/usr/bin/env python3
"""Verify local Compendium v0.1.0 assets without external access."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import build_compendium_release as builder
import jsonschema

EXPECTED_INVENTORY = {
    "claims": 110,
    "maximum_claim_id": "DD-C-0110",
    "studies": 26,
    "maximum_study_id": "DD-022",
    "manifests": 51,
    "passing_manifests": 48,
}
FORBIDDEN_MEMBER_PARTS = {
    ".env",
    ".env.txt",
    ".git",
    ".venv",
    "__pycache__",
    "authorization",
    "private",
    "sealed",
    "site/dist",
}


class ReleaseVerificationError(RuntimeError):
    """Release assets failed an offline invariant."""


def _expected_names(version: str) -> set[str]:
    stem = f"distributed-discovery-compendium-v{version}"
    return {
        f"{stem}-release-evidence-manifest.json",
        f"{stem}-SHA256SUMS.txt",
        f"{stem}-paper-citation-metadata.yml",
        f"{stem}-papers.zip",
        f"{stem}-release-notes.md",
    }


def _parse_checksums(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines != sorted(lines, key=lambda line: line.split("  ", 1)[1]):
        raise ReleaseVerificationError("SHA256SUMS entries are not sorted")
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\n]+)", line)
        if match is None:
            raise ReleaseVerificationError(f"invalid checksum line: {line}")
        digest, filename = match.groups()
        if filename in records:
            raise ReleaseVerificationError(f"duplicate checksum filename: {filename}")
        records[filename] = digest
    return records


def _safe_member_name(name: str) -> None:
    pure = PurePosixPath(name)
    if pure.is_absolute() or ".." in pure.parts or "\\" in name:
        raise ReleaseVerificationError(f"unsafe archive path: {name}")
    lowered = name.lower()
    if any(part in lowered for part in FORBIDDEN_MEMBER_PARTS):
        raise ReleaseVerificationError(f"forbidden archive path: {name}")
    if " 2." in name:
        raise ReleaseVerificationError(f"collision-copy member rejected: {name}")


def _verify_zip(path: Path, registry: dict[str, Any], version: str) -> dict[str, Any]:
    expected_members, expected_inventory = builder._paper_members(registry, version)
    expected = dict(expected_members)
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if names != sorted(names):
            raise ReleaseVerificationError("archive members are not sorted")
        if len(names) != len(set(names)):
            raise ReleaseVerificationError("archive has duplicate members")
        if set(names) != set(expected):
            missing = sorted(set(expected) - set(names))
            extra = sorted(set(names) - set(expected))
            raise ReleaseVerificationError(
                f"archive inventory mismatch; missing={missing}, extra={extra}"
            )
        for info in infos:
            _safe_member_name(info.filename)
            if info.date_time != builder.ZIP_TIMESTAMP:
                raise ReleaseVerificationError(f"timestamp is not normalized: {info.filename}")
            if info.create_system != 3 or (info.external_attr >> 16) != 0o100644:
                raise ReleaseVerificationError(f"permissions are not normalized: {info.filename}")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise ReleaseVerificationError(f"compression is not normalized: {info.filename}")
            data = archive.read(info)
            if data != expected[info.filename]:
                raise ReleaseVerificationError(f"archive member bytes changed: {info.filename}")
            for marker in builder.FORBIDDEN_BYTES:
                if marker in data:
                    raise ReleaseVerificationError(
                        f"secret or host path marker in archive: {info.filename}"
                    )
        inventory_name = f"distributed-discovery-compendium-v{version}/paper-bundle-inventory.json"
        inventory = json.loads(archive.read(inventory_name))
        if inventory != expected_inventory:
            raise ReleaseVerificationError("machine-readable bundle inventory changed")
    return {
        "members": len(expected),
        "papers": expected_inventory["paper_count"],
        "pages": expected_inventory["page_count"],
    }


def verify_release(*, version: str, output_dir: Path) -> dict[str, Any]:
    expected_names = _expected_names(version)
    actual_names = {path.name for path in output_dir.iterdir() if path.is_file()}
    if actual_names != expected_names:
        raise ReleaseVerificationError(
            f"expected five assets; missing={sorted(expected_names - actual_names)}, "
            f"extra={sorted(actual_names - expected_names)}"
        )
    stem = f"distributed-discovery-compendium-v{version}"
    manifest_path = output_dir / f"{stem}-release-evidence-manifest.json"
    checksums_path = output_dir / f"{stem}-SHA256SUMS.txt"
    papers_path = output_dir / f"{stem}-papers.zip"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    schema = json.loads(builder.MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(manifest, schema, format_checker=jsonschema.FormatChecker())
    if manifest["compendium_version"] != version:
        raise ReleaseVerificationError("manifest version mismatch")
    if manifest["candidate_tag"] != f"dd-compendium-v{version}":
        raise ReleaseVerificationError("candidate tag mismatch")
    if manifest["inventory"] != EXPECTED_INVENTORY:
        raise ReleaseVerificationError("scientific inventory changed")
    if not builder.SHA_RE.fullmatch(manifest["source_revision"]):
        raise ReleaseVerificationError("manifest source revision is not full SHA")
    if manifest["manifest_kind"] == "dry-run":
        if manifest["release_status"] != "dry-run-only":
            raise ReleaseVerificationError("dry-run release status is false")
        for field in (
            "tag",
            "github_release_url",
            "version_doi",
            "concept_doi",
        ):
            if manifest[field] is not None:
                raise ReleaseVerificationError(f"dry-run {field} must be null")
    registry = builder.load_content_registry()
    if manifest["content_registry"]["sha256"] != builder.sha256_file(builder.CONTENT_PATH):
        raise ReleaseVerificationError("content registry hash mismatch")
    if len(manifest["artifacts"]) != 7:
        raise ReleaseVerificationError("manifest must describe seven paper artifacts")
    if sum(item["page_count"] for item in manifest["artifacts"]) != 119:
        raise ReleaseVerificationError("manifest paper pages must total 119")
    for artifact, paper in zip(manifest["artifacts"], registry["papers"], strict=True):
        if artifact["paper_id"] != paper["paper_id"]:
            raise ReleaseVerificationError("paper order or identity changed")
        if builder.sha256_file(builder.ROOT / artifact["pdf_path"]) != artifact["pdf_sha256"]:
            raise ReleaseVerificationError(f"PDF hash mismatch: {artifact['paper_id']}")
        if builder.sha256_file(builder.ROOT / paper["main_source"]) != artifact["source_sha256"]:
            raise ReleaseVerificationError(f"main source hash mismatch: {artifact['paper_id']}")
    zip_result = _verify_zip(papers_path, registry, version)
    if manifest["paper_bundle"]["sha256"] != builder.sha256_file(papers_path):
        raise ReleaseVerificationError("paper-bundle hash mismatch")
    if manifest["paper_bundle"]["archive_members"] != zip_result["members"]:
        raise ReleaseVerificationError("paper-bundle member count mismatch")

    checksums = _parse_checksums(checksums_path)
    expected_checksummed = expected_names - {checksums_path.name}
    if set(checksums) != expected_checksummed:
        raise ReleaseVerificationError("SHA256SUMS must cover four non-self assets")
    for filename, digest in checksums.items():
        if builder.sha256_file(output_dir / filename) != digest:
            raise ReleaseVerificationError(f"checksum mismatch: {filename}")
    asset_records = {item["filename"]: item for item in manifest["release_assets"]}
    expected_peer_assets = {
        f"{stem}-paper-citation-metadata.yml",
        f"{stem}-papers.zip",
        f"{stem}-release-notes.md",
    }
    if set(asset_records) != expected_peer_assets:
        raise ReleaseVerificationError("manifest peer-asset inventory mismatch")
    for filename, record in asset_records.items():
        path = output_dir / filename
        if record["sha256"] != builder.sha256_file(path):
            raise ReleaseVerificationError(f"manifest asset hash mismatch: {filename}")
        if record["bytes"] != path.stat().st_size:
            raise ReleaseVerificationError(f"manifest asset size mismatch: {filename}")
    return {
        "status": "verified-offline",
        "assets": 5,
        "checksummed_assets": 4,
        "archive_members": zip_result["members"],
        "papers": zip_result["papers"],
        "pages": zip_result["pages"],
        "manifest_kind": manifest["manifest_kind"],
        "source_revision": manifest["source_revision"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = verify_release(version=args.version, output_dir=args.output_dir)
    except (
        ReleaseVerificationError,
        builder.ReleaseBuildError,
        jsonschema.ValidationError,
        ValueError,
        OSError,
    ) as exc:
        print(f"compendium release verification failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
