#!/usr/bin/env python3
"""Build deterministic, local-only Distributed Discovery compendium assets."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "docs/releases/compendium-v0.1.0-content.yml"
CONTENT_SCHEMA_PATH = ROOT / "docs/releases/compendium-release-content.schema.json"
MANIFEST_SCHEMA_PATH = ROOT / "docs/releases/release-evidence-manifest.schema.json"
AUTH_SCHEMA_PATH = ROOT / "docs/releases/first-compendium-release-authorization.schema.json"
CITATION_PATH = ROOT / "docs/publication/paper-citation-metadata.yml"
RELEASE_NOTES_PATH = ROOT / "docs/releases/compendium-v0.1.0-release-notes.md"
RELEASE_REGISTRY_PATH = ROOT / "docs/releases/releases.yml"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644 << 16
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
FORBIDDEN_PATH_PARTS = {
    ".env",
    ".env.txt",
    ".git",
    ".venv",
    "__pycache__",
    "authorization",
    "private",
    "sealed",
}
FORBIDDEN_BYTES = (
    b"/" + b"Users/",
    b"/" + b"home/",
    b"BEGIN PRIVATE KEY",
    b"BEGIN RSA PRIVATE KEY",
    b"BEGIN OPENSSH PRIVATE KEY",
    b"ghp_",
)


class ReleaseBuildError(RuntimeError):
    """A deterministic release build violated its declared boundary."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ReleaseBuildError(f"{path.relative_to(ROOT)} must contain a mapping")
    return data


def _load_yaml_bytes(data: bytes, *, label: str) -> dict[str, Any]:
    loaded = yaml.safe_load(data.decode("utf-8"))
    if not isinstance(loaded, dict):
        raise ReleaseBuildError(f"{label} must contain a mapping")
    return loaded


def git_blob(source_revision: str, repository_path: str) -> bytes:
    """Read one exact regular-file blob from an immutable Git revision."""
    if not SHA_RE.fullmatch(source_revision):
        raise ReleaseBuildError("source revision must be a full lowercase 40-hex SHA")
    if PurePosixPath(repository_path).is_absolute() or ".." in PurePosixPath(repository_path).parts:
        raise ReleaseBuildError(f"unsafe repository path: {repository_path}")
    completed = subprocess.run(
        ["git", "show", f"{source_revision}:{repository_path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ReleaseBuildError(f"immutable release blob unavailable: {repository_path}")
    return completed.stdout


def _release_source_revision(version: str) -> str:
    release_registry = _load_yaml(RELEASE_REGISTRY_PATH)
    matches = [
        release
        for release in release_registry.get("releases", [])
        if release.get("version") == version
    ]
    if len(matches) != 1:
        raise ReleaseBuildError(f"version {version} must have one release registry entry")
    source_revision = str(matches[0].get("source_revision", ""))
    if not SHA_RE.fullmatch(source_revision):
        raise ReleaseBuildError("registered release source revision is not a full SHA")
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{source_revision}^{{commit}}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ReleaseBuildError("registered release source revision is unavailable")
    return source_revision


def load_content_registry(source_revision: str | None = None) -> dict[str, Any]:
    if source_revision is None:
        registry = _load_yaml(CONTENT_PATH)
    else:
        registry = _load_yaml_bytes(
            git_blob(source_revision, CONTENT_PATH.relative_to(ROOT).as_posix()),
            label=CONTENT_PATH.relative_to(ROOT).as_posix(),
        )
    schema = json.loads(CONTENT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(registry, schema, format_checker=jsonschema.FormatChecker())
    paper_ids = [paper["paper_id"] for paper in registry["papers"]]
    if len(set(paper_ids)) != 7:
        raise ReleaseBuildError("content registry must contain seven unique paper IDs")
    if sum(int(paper["page_count"]) for paper in registry["papers"]) != 119:
        raise ReleaseBuildError("content registry paper pages must total 119")
    return registry


def validate_authorization(
    path: Path, *, source_revision: str, allow_synthetic: bool = False
) -> dict[str, Any]:
    authorization = _load_yaml(path)
    schema = json.loads(AUTH_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(authorization, schema, format_checker=jsonschema.FormatChecker())
    required_true = (
        "release_allowed",
        "create_annotated_tag",
        "push_tag",
        "create_github_release",
        "upload_release_assets",
    )
    if authorization["authorization_status"] != "active":
        raise ReleaseBuildError("authorization is not active")
    if not all(authorization[field] is True for field in required_true):
        raise ReleaseBuildError("authorization does not permit the complete release action")
    if authorization["source_revision"] != source_revision:
        raise ReleaseBuildError("authorization source revision does not match build revision")
    if not all(authorization["zenodo"].values()):
        raise ReleaseBuildError("Zenodo owner attestations are incomplete")
    if not authorization["owner_attestation"]["licensing_attested"]:
        raise ReleaseBuildError("owner licensing attestation is incomplete")
    if authorization["owner_attestation"]["synthetic_fixture"] and not allow_synthetic:
        raise ReleaseBuildError("synthetic fixtures cannot authorize release mode")
    if any(authorization["other_permissions"].values()):
        raise ReleaseBuildError("authorization improperly enables an out-of-scope action")
    return authorization


def _tracked_files(source_revision: str, root: str) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-tree", "-r", "-z", source_revision, "--", root],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ReleaseBuildError(f"immutable release tree unavailable under {root}")
    paths: list[str] = []
    for item in completed.stdout.split(b"\0"):
        if not item:
            continue
        metadata, raw_path = item.split(b"\t", 1)
        mode, object_type, _object_id = metadata.decode("ascii").split(" ", 2)
        path = raw_path.decode("utf-8")
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise ReleaseBuildError(f"non-regular immutable release member: {path}")
        paths.append(path)
    if not paths:
        raise ReleaseBuildError(f"no tracked files found under {root}")
    return sorted(paths)


def _is_excluded(relative_to_paper: str, patterns: list[str]) -> bool:
    return any(
        fnmatch.fnmatch(relative_to_paper, pattern)
        or fnmatch.fnmatch(PurePosixPath(relative_to_paper).name, pattern)
        for pattern in patterns
    )


def _validate_member(
    *, repository_path: str, paper_root: str, patterns: list[str], data: bytes
) -> bytes:
    relative = PurePosixPath(repository_path).relative_to(paper_root).as_posix()
    if _is_excluded(relative, patterns):
        raise ReleaseBuildError("excluded members must be filtered before validation")
    parts = {part.lower() for part in PurePosixPath(relative).parts}
    if parts & FORBIDDEN_PATH_PARTS or " 2." in relative:
        raise ReleaseBuildError(f"forbidden archive member path: {relative}")
    for marker in FORBIDDEN_BYTES:
        if marker in data:
            raise ReleaseBuildError(f"secret or host-path marker in {repository_path}")
    return data


def _paper_members(
    registry: dict[str, Any], version: str, *, source_revision: str
) -> tuple[list[tuple[str, bytes]], dict[str, Any]]:
    members: list[tuple[str, bytes]] = []
    inventory_files: list[dict[str, Any]] = []
    paper_summaries: list[dict[str, Any]] = []
    prefix = f"distributed-discovery-compendium-v{version}/papers"
    for paper in registry["papers"]:
        root = str(paper["root"])
        exclude_patterns = [str(item) for item in paper["exclude_patterns"]]
        selected: list[str] = []
        for path in _tracked_files(source_revision, root):
            relative = PurePosixPath(path).relative_to(root).as_posix()
            if _is_excluded(relative, exclude_patterns):
                continue
            selected.append(path)
        if not selected:
            raise ReleaseBuildError(f"paper has no selected members: {paper['paper_id']}")
        pdf = str(paper["pdf"])
        source = str(paper["main_source"])
        if pdf not in selected or source not in selected:
            raise ReleaseBuildError(f"paper PDF or main source omitted: {paper['paper_id']}")
        if sha256_bytes(git_blob(source_revision, pdf)) != paper["pdf_sha256"]:
            raise ReleaseBuildError(f"PDF hash changed: {paper['paper_id']}")
        if sha256_bytes(git_blob(source_revision, source)) != paper["main_source_sha256"]:
            raise ReleaseBuildError(f"main source hash changed: {paper['paper_id']}")
        validation = json.loads(git_blob(source_revision, f"{root}/validation.json"))
        if validation.get("pdf_sha256") != paper["pdf_sha256"]:
            raise ReleaseBuildError(f"validation PDF hash mismatch: {paper['paper_id']}")
        if validation.get("page_count") != paper["page_count"]:
            raise ReleaseBuildError(f"validation page count mismatch: {paper['paper_id']}")
        for path in selected:
            data = _validate_member(
                repository_path=path,
                paper_root=root,
                patterns=exclude_patterns,
                data=git_blob(source_revision, path),
            )
            relative = PurePosixPath(path).relative_to(root).as_posix()
            archive_name = f"{prefix}/{paper['paper_id']}/{relative}"
            members.append((archive_name, data))
            inventory_files.append(
                {
                    "archive_path": archive_name,
                    "repository_path": path,
                    "bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )
        paper_summaries.append(
            {
                "paper_id": paper["paper_id"],
                "pdf_path": paper["pdf"],
                "pdf_sha256": paper["pdf_sha256"],
                "page_count": paper["page_count"],
                "main_source": paper["main_source"],
                "main_source_sha256": paper["main_source_sha256"],
                "members": len(selected),
            }
        )
    members.sort(key=lambda item: item[0])
    inventory_files.sort(key=lambda item: item["archive_path"])
    inventory = {
        "schema_version": 1,
        "bundle_kind": "seven-paper-release-candidate",
        "compendium_version": version,
        "tracked_files_only": True,
        "timestamp_normalization": "1980-01-01T00:00:00Z",
        "regular_file_mode": "0644",
        "papers": paper_summaries,
        "paper_count": 7,
        "page_count": 119,
        "files": inventory_files,
    }
    inventory_name = f"distributed-discovery-compendium-v{version}/paper-bundle-inventory.json"
    inventory_bytes = json.dumps(inventory, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    members.append((inventory_name, inventory_bytes))
    members.sort(key=lambda item: item[0])
    return members, inventory


def _write_zip(path: Path, members: list[tuple[str, bytes]]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = FILE_MODE
            info.flag_bits |= 0x800
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def _validate_coordinates(
    *,
    mode: str,
    release_url: str | None,
    version_doi: str | None,
    concept_doi: str | None,
) -> None:
    if mode == "dry-run" and any((release_url, version_doi, concept_doi)):
        raise ReleaseBuildError("dry-run external coordinates must remain null")
    if release_url is not None and not release_url.startswith(
        "https://github.com/yoheinakajima/distributed-discovery/releases/tag/"
    ):
        raise ReleaseBuildError("release URL is outside the canonical repository")
    for label, value in (("version DOI", version_doi), ("concept DOI", concept_doi)):
        if value is not None and not DOI_RE.fullmatch(value):
            raise ReleaseBuildError(f"invalid {label}")
    if (version_doi is None) != (concept_doi is None):
        raise ReleaseBuildError("version and concept DOI must be supplied together")


def build_release(
    *,
    version: str,
    source_revision: str,
    output_dir: Path,
    mode: str,
    generated_utc: str,
    release_url: str | None = None,
    version_doi: str | None = None,
    concept_doi: str | None = None,
    authorization: Path | None = None,
) -> dict[str, Any]:
    if version != "0.1.0":
        raise ReleaseBuildError("this registry is frozen for version 0.1.0")
    if not SHA_RE.fullmatch(source_revision):
        raise ReleaseBuildError("source revision must be a full lowercase 40-hex SHA")
    if not UTC_RE.fullmatch(generated_utc):
        raise ReleaseBuildError("generated UTC must be a second-precision Z timestamp")
    datetime.strptime(generated_utc, "%Y-%m-%dT%H:%M:%SZ")
    if mode not in {"dry-run", "release"}:
        raise ReleaseBuildError("mode must be dry-run or release")
    _validate_coordinates(
        mode=mode,
        release_url=release_url,
        version_doi=version_doi,
        concept_doi=concept_doi,
    )
    if mode == "release":
        if authorization is None:
            raise ReleaseBuildError("release mode requires explicit owner authorization")
        validate_authorization(authorization, source_revision=source_revision)
    elif authorization is not None:
        raise ReleaseBuildError("dry-run mode must not read an authorization")

    release_source_revision = _release_source_revision(version)
    if mode == "release" and source_revision != release_source_revision:
        raise ReleaseBuildError(
            "release mode source revision must equal the immutable registered release source"
        )
    registry = load_content_registry(release_source_revision)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"distributed-discovery-compendium-v{version}"
    names = {
        "manifest": f"{stem}-release-evidence-manifest.json",
        "checksums": f"{stem}-SHA256SUMS.txt",
        "citation": f"{stem}-paper-citation-metadata.yml",
        "papers": f"{stem}-papers.zip",
        "notes": f"{stem}-release-notes.md",
    }
    for filename in names.values():
        target = output_dir / filename
        if target.exists():
            target.unlink()

    members, bundle_inventory = _paper_members(
        registry, version, source_revision=release_source_revision
    )
    papers_path = output_dir / names["papers"]
    _write_zip(papers_path, members)
    citation_path = output_dir / names["citation"]
    citation_path.write_bytes(
        git_blob(release_source_revision, CITATION_PATH.relative_to(ROOT).as_posix())
    )
    notes_path = output_dir / names["notes"]
    notes_path.write_bytes(
        git_blob(release_source_revision, RELEASE_NOTES_PATH.relative_to(ROOT).as_posix())
    )

    release_assets = []
    for path in sorted((citation_path, papers_path, notes_path), key=lambda p: p.name):
        release_assets.append(
            {"filename": path.name, "sha256": sha256_file(path), "bytes": path.stat().st_size}
        )
    artifacts = [
        {
            "paper_id": paper["paper_id"],
            "pdf_path": paper["pdf"],
            "pdf_sha256": paper["pdf_sha256"],
            "page_count": paper["page_count"],
            "source_bundle": paper["root"],
            "source_sha256": paper["main_source_sha256"],
        }
        for paper in registry["papers"]
    ]
    manifest = {
        "schema_version": 2,
        "manifest_kind": mode,
        "release_status": ("dry-run-only" if mode == "dry-run" else "authorized-assets-only"),
        "compendium_version": version,
        "candidate_tag": registry["candidate_tag"],
        "tag": None if mode == "dry-run" else registry["candidate_tag"],
        "source_revision": release_source_revision,
        "github_release_url": release_url,
        "version_doi": version_doi,
        "concept_doi": concept_doi,
        "generated_utc": generated_utc,
        "content_registry": {
            "path": CONTENT_PATH.relative_to(ROOT).as_posix(),
            "sha256": sha256_bytes(
                git_blob(
                    release_source_revision,
                    CONTENT_PATH.relative_to(ROOT).as_posix(),
                )
            ),
        },
        "inventory": {
            "claims": 110,
            "maximum_claim_id": "DD-C-0110",
            "studies": 26,
            "maximum_study_id": "DD-022",
            "manifests": 51,
            "passing_manifests": 48,
        },
        "artifacts": artifacts,
        "paper_bundle": {
            "filename": papers_path.name,
            "sha256": sha256_file(papers_path),
            "inventory_member": f"{stem}/paper-bundle-inventory.json",
            "archive_members": len(members),
            "papers": bundle_inventory["paper_count"],
            "pages": bundle_inventory["page_count"],
        },
        "release_assets": release_assets,
        "safety": {
            "tracked_files_only": True,
            "symlinks": 0,
            "external_mutations": 0,
            "private_material": 0,
            "credentials": 0,
            "host_paths": 0,
        },
    }
    manifest_schema = json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(manifest, manifest_schema, format_checker=jsonschema.FormatChecker())
    manifest_path = output_dir / names["manifest"]
    manifest_path.write_bytes(
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )
    checksummed = sorted(
        (manifest_path, citation_path, papers_path, notes_path),
        key=lambda path: path.name,
    )
    checksums_path = output_dir / names["checksums"]
    checksums_path.write_text(
        "".join(f"{sha256_file(path)}  {path.name}\n" for path in checksummed),
        encoding="utf-8",
        newline="\n",
    )
    return {
        "output_dir": str(output_dir),
        "assets": [names[key] for key in ("manifest", "checksums", "citation", "papers", "notes")],
        "hashes": {name: sha256_file(output_dir / name) for name in sorted(names.values())},
        "archive_members": len(members),
        "requested_build_revision": source_revision,
        "release_source_revision": release_source_revision,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("dry-run", "release"), required=True)
    parser.add_argument("--generated-utc", required=True)
    parser.add_argument("--release-url")
    parser.add_argument("--version-doi")
    parser.add_argument("--concept-doi")
    parser.add_argument("--authorization", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_release(
            version=args.version,
            source_revision=args.source_revision,
            output_dir=args.output_dir,
            mode=args.mode,
            generated_utc=args.generated_utc,
            release_url=args.release_url,
            version_doi=args.version_doi,
            concept_doi=args.concept_doi,
            authorization=args.authorization,
        )
    except (ReleaseBuildError, jsonschema.ValidationError, ValueError) as exc:
        print(f"compendium release build failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
