from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "scripts/build_compendium_release.py"
VERIFY_SCRIPT = ROOT / "scripts/verify_compendium_release.py"
AUTH_SCRIPT = ROOT / "scripts/validate_first_compendium_release_authorization.py"
SOURCE_REVISION = "ec29be1bd632e11dedf02ea18ab14b817fcc8074"
GENERATED_UTC = "2026-07-24T00:00:00Z"


def _run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def _build(output_dir: Path) -> dict[str, object]:
    completed = _run(
        str(BUILD_SCRIPT),
        "--version",
        "0.1.0",
        "--source-revision",
        SOURCE_REVISION,
        "--output-dir",
        str(output_dir),
        "--mode",
        "dry-run",
        "--generated-utc",
        GENERATED_UTC,
    )
    return json.loads(completed.stdout)


def _hashes(directory: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.iterdir())
        if path.is_file()
    }


def test_content_registry_has_seven_exact_papers_and_exclusions() -> None:
    registry = yaml.safe_load((ROOT / "docs/releases/compendium-v0.1.0-content.yml").read_text())
    schema = json.loads((ROOT / "docs/releases/compendium-release-content.schema.json").read_text())
    jsonschema.validate(registry, schema)
    assert registry["tracked_files_only"] is True
    assert len(registry["papers"]) == 7
    assert sum(paper["page_count"] for paper in registry["papers"]) == 119
    exclusions = " ".join(registry["global_exclusions"])
    for marker in (".env.txt", "authorization", "private", "site/dist", "untracked"):
        assert marker in exclusions


def test_dry_run_builds_five_byte_deterministic_assets(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_result = _build(first)
    second_result = _build(second)
    assert first_result["assets"] == second_result["assets"]
    assert _hashes(first) == _hashes(second)
    assert len(_hashes(first)) == 5


def test_verifier_accepts_deterministic_dry_run(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    _build(output)
    completed = _run(
        str(VERIFY_SCRIPT),
        "--version",
        "0.1.0",
        "--output-dir",
        str(output),
    )
    result = json.loads(completed.stdout)
    assert result["status"] == "verified-offline"
    assert result["assets"] == 5
    assert result["papers"] == 7
    assert result["pages"] == 119


def test_archive_metadata_and_inventory_are_normalized(tmp_path: Path) -> None:
    output = tmp_path / "candidate"
    _build(output)
    archive_path = next(output.glob("*-papers.zip"))
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        assert [info.filename for info in infos] == sorted(info.filename for info in infos)
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in infos)
        assert all((info.external_attr >> 16) == 0o100644 for info in infos)
        assert all(not info.filename.startswith("/") for info in infos)
        assert all(".." not in Path(info.filename).parts for info in infos)
        inventory_name = next(
            info.filename for info in infos if info.filename.endswith("paper-bundle-inventory.json")
        )
        inventory = json.loads(archive.read(inventory_name))
    assert inventory["paper_count"] == 7
    assert inventory["page_count"] == 119
    assert inventory["tracked_files_only"] is True
    assert all("build.log" not in item["archive_path"] for item in inventory["files"])
    assert all(" 2." not in item["archive_path"] for item in inventory["files"])


def test_dry_run_rejects_external_coordinates_and_authorization(tmp_path: Path) -> None:
    completed = _run(
        str(BUILD_SCRIPT),
        "--version",
        "0.1.0",
        "--source-revision",
        SOURCE_REVISION,
        "--output-dir",
        str(tmp_path),
        "--mode",
        "dry-run",
        "--generated-utc",
        GENERATED_UTC,
        "--release-url",
        "https://github.com/yoheinakajima/distributed-discovery/releases/tag/dd-compendium-v0.1.0",
        check=False,
    )
    assert completed.returncode == 2
    assert "must remain null" in completed.stderr


def test_release_mode_refuses_without_explicit_authorization(tmp_path: Path) -> None:
    completed = _run(
        str(BUILD_SCRIPT),
        "--version",
        "0.1.0",
        "--source-revision",
        SOURCE_REVISION,
        "--output-dir",
        str(tmp_path),
        "--mode",
        "release",
        "--generated-utc",
        GENERATED_UTC,
        check=False,
    )
    assert completed.returncode == 2
    assert "requires explicit owner authorization" in completed.stderr


def test_authorization_template_is_inactive_and_synthetic_fixture_validates() -> None:
    template = yaml.safe_load(
        (ROOT / "docs/releases/first-compendium-release-authorization-template.yml").read_text()
    )
    assert template["authorization_status"] == "pending-owner-decision"
    assert template["release_allowed"] is False
    assert not any(template["other_permissions"].values())
    fixture = ROOT / "tests/fixtures/releases/valid-offline-release-authorization.yml"
    completed = _run(
        str(AUTH_SCRIPT),
        "--authorization",
        str(fixture),
        "--source-revision",
        "a" * 40,
        "--allow-synthetic-fixture",
    )
    assert json.loads(completed.stdout)["valid"] is True


@pytest.mark.parametrize(
    "fixture",
    sorted((ROOT / "tests/fixtures/releases/invalid-release-authorizations").glob("*.yml")),
)
def test_invalid_authorizations_are_rejected(fixture: Path) -> None:
    record = yaml.safe_load(fixture.read_text())
    source_revision = record.get("source_revision") or "d" * 40
    completed = _run(
        str(AUTH_SCRIPT),
        "--authorization",
        str(fixture),
        "--source-revision",
        source_revision,
        "--allow-synthetic-fixture",
        check=False,
    )
    assert completed.returncode == 2
