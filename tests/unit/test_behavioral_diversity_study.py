from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from distributed_discovery.behavioral_diversity import study
from distributed_discovery.site.build import _runs


def _fixture(tmp_path: Path) -> dict[str, object]:
    config: dict[str, object] = {
        "study_id": "DD-024",
        "track_id": "track-03",
        "time_cap_seconds": 120,
        "memory_cap_mb": 1024,
        "random_seeds": {"algorithm": [], "model": None},
    }
    folder = tmp_path / study.STUDY / "tracks/track-03"
    folder.mkdir(parents=True)
    (folder / "config.json").write_text(json.dumps(config))
    (tmp_path / study.STUDY / "registered-configs.json").write_text(
        json.dumps({"tracks": {"track-03": {"config_hash_sha256": study.config_digest(config)}}})
    )
    return config


def test_resource_and_identity_changes_are_rejected(tmp_path: Path) -> None:
    config = _fixture(tmp_path)
    path, loaded = study.load_config(tmp_path, "track-03")
    assert loaded == config
    for key, bad in (("study_id", "DD-023"), ("time_cap_seconds", 121), ("memory_cap_mb", 2048)):
        corrupt = {**config, key: bad}
        path.write_text(json.dumps(corrupt))
        with pytest.raises(ValueError):
            study.load_config(tmp_path, "track-03")


def test_closed_track_cannot_execute(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not admitted"):
        study.load_config(tmp_path, "track-01")


def test_dirty_source_stops_before_creating_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(study, "readiness", lambda *_: {"git_dirty": True})
    with pytest.raises(RuntimeError, match="clean committed"):
        study.execute(tmp_path, "track-03")
    assert not (tmp_path / "results").exists()


def test_result_shards_roundtrip_and_refuse_traversal(tmp_path: Path) -> None:
    original = {"rows": [{"value": "1/3"}, {"value": "2/3"}], "summary": {"cells": 2}}
    study._store_result(tmp_path, original)
    assert study.load_result(tmp_path) == original
    (tmp_path / "result.json").write_text(json.dumps({"row_files": ["../../private"]}))
    with pytest.raises(ValueError, match="unsafe"):
        study.load_result(tmp_path)


def test_primary_slot_is_shared_between_worktrees_and_config_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = tmp_path / "git-common"
    monkeypatch.setattr(study, "_git", lambda *_: str(common))
    binding = {"git_commit": "0" * 40, "config_hash_sha256": "1" * 64}
    reservation = study.reserve_attempt(tmp_path / "one", "track-03", binding, "first")
    assert json.loads(reservation.read_text())["run_id"] == "first"
    changed = {**binding, "config_hash_sha256": "2" * 64}
    with pytest.raises(RuntimeError, match="shared primary-attempt"):
        study.reserve_attempt(tmp_path / "two", "track-03", changed, "second")


def test_malformed_worker_output_preserves_consumed_failed_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _fixture(tmp_path)
    (tmp_path / "uv.lock").write_text("fixture lock")
    binding = {
        "git_commit": "0" * 40,
        "git_dirty": False,
        "config_hash_sha256": study.config_digest(config),
        "input_hashes": {"uv.lock": study._hash(tmp_path / "uv.lock")},
    }
    monkeypatch.setattr(study, "readiness", lambda *_: binding)
    monkeypatch.setattr(study, "_git", lambda *_: str(tmp_path / "git-common"))

    class FakeProcess:
        def __init__(self, command: list[str], **_: Any) -> None:
            output = Path(command[-1]) / "outputs"
            output.mkdir()
            (output / "verification.json").write_text("{truncated")

        def wait(self, **_: Any) -> int:
            return 0

    monkeypatch.setattr(study.subprocess, "Popen", FakeProcess)
    with pytest.raises(RuntimeError, match="preserved unsuccessful"):
        study.execute(tmp_path, "track-03")
    manifests = list((tmp_path / "results").glob("**/manifest.json"))
    assert len(manifests) == 1
    manifest = json.loads(manifests[0].read_text())
    assert manifest["validation_status"] == "failed"
    assert manifest["termination"] == "malformed-verification-output"
    inventory_path = manifests[0].parent / study.ARTIFACT_INVENTORY
    inventory = json.loads(inventory_path.read_text())
    assert manifest["outputs"][study.ARTIFACT_INVENTORY] == study._hash(inventory_path)
    for relative in ("stdout.log", "stderr.log", "reproduce.sh"):
        assert relative not in manifest["outputs"]
        assert inventory[relative] == study._hash(manifests[0].parent / relative)
    assert (
        json.loads((manifests[0].parent / "reservation.json").read_text())["track_id"] == "track-03"
    )
    with pytest.raises(RuntimeError, match="already has a preserved attempt"):
        study.execute(tmp_path, "track-03")


@pytest.mark.parametrize("corruption", ["changed_log", "inventory_escape"])
def test_mock_success_is_site_compatible_and_checks_transitive_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corruption: str
) -> None:
    config = _fixture(tmp_path)
    (tmp_path / "uv.lock").write_text("fixture lock")
    binding = {
        "git_commit": "0" * 40,
        "git_dirty": False,
        "config_hash_sha256": study.config_digest(config),
        "input_hashes": {"uv.lock": study._hash(tmp_path / "uv.lock")},
    }
    monkeypatch.setattr(study, "readiness", lambda *_: binding)
    monkeypatch.setattr(study, "_git", lambda *_: str(tmp_path / "git-common"))
    verification = {"passed": True, "errors": [], "corruptions": {"mock_corruption": True}}

    class FakeProcess:
        def __init__(self, command: list[str], **kwargs: Any) -> None:
            output = Path(command[-1]) / "outputs"
            study._store_result(output, {"rows": [{"fixture": True}], "summary": {"cells": 0}})
            study._write(output / "verification.json", verification)
            kwargs["stdout"].write("mock worker; no scientific cells evaluated\n")

        def wait(self, **_: Any) -> int:
            return 0

    monkeypatch.setattr(study.subprocess, "Popen", FakeProcess)
    run = study.execute(tmp_path, "track-03")
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    inventory_path = run / study.ARTIFACT_INVENTORY
    inventory = json.loads(inventory_path.read_text())
    assert set(inventory) == {
        str(path.relative_to(run))
        for path in run.rglob("*")
        if path.is_file() and path.name not in {"manifest.json", study.ARTIFACT_INVENTORY}
    }
    assert all(Path(relative).suffix in {".json", ".md"} for relative in manifest["outputs"])
    assert {"stdout.log", "stderr.log", "reproduce.sh"} <= set(inventory)
    summaries, run_ids = _runs(tmp_path)
    assert run_ids == {run.name}
    assert summaries[0]["run_id"] == run.name
    fake_module = SimpleNamespace(verify=lambda *_: verification)
    monkeypatch.setattr(study.importlib, "import_module", lambda _: fake_module)
    checked = study.verify_existing(tmp_path, "track-03", run)
    assert checked["verification"]["passed"]
    assert checked["new_primary_run"] is False
    if corruption == "changed_log":
        (run / "stdout.log").write_text("changed log")
        message = "artifact inventory checksum mismatch: stdout.log"
    else:
        inventory["../escaped"] = "0" * 64
        study._write(inventory_path, inventory)
        manifest["outputs"][study.ARTIFACT_INVENTORY] = study._hash(inventory_path)
        study._write(manifest_path, manifest)
        message = "unsafe artifact path"
    with pytest.raises(ValueError, match=message):
        study.verify_existing(tmp_path, "track-03", run)
