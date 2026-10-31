"""Study evidence links need passing manifests, not central claim promotion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from distributed_discovery.site.build import _runs, _study_data

RUN_A = "20261031T000000Z_DD-024_caa1bf80_0000000001"
RUN_B = "20261031T000000Z_DD-024_caa1bf80_0000000002"
FOREIGN_RUN = "20261031T000000Z_DD-022_caa1bf80_0000000003"


def write_study(root: Path, public_fields: dict[str, Any]) -> None:
    directory = root / "studies/DD-024-example"
    directory.mkdir(parents=True)
    public = {
        "study_id": "DD-024",
        "title": "Exploratory fixture",
        "slug": "dd-024",
        "phase": "complete-bounded-study",
        "summary": "Unpromoted synthetic observation.",
        "public_artifacts": [],
        "claim_ids": [],
    }
    public.update(public_fields)
    (directory / "public.yml").write_text(yaml.safe_dump(public))
    (directory / "status.yml").write_text(
        yaml.safe_dump(
            {
                "study_id": "DD-024",
                "status": "complete-bounded-study",
                "evidence_status": "audited-exploratory-synthetic",
                "next_action": "Preserve evidence.",
            }
        )
    )
    (directory / "question.md").write_text("# Question\n\nCan unclaimed evidence be linked?\n")


def write_manifest(
    root: Path,
    run_id: str,
    *,
    study_id: str = "DD-024",
    validation_status: str = "passed",
    exit_status: int = 0,
) -> None:
    directory = root / "results/exploratory" / run_id
    directory.mkdir(parents=True)
    artifact = directory / "fixture.json"
    artifact.write_text('{"development_fixture": true}\n')
    manifest = {
        "run_id": run_id,
        "study_id": study_id,
        "validation_status": validation_status,
        "exit_status": exit_status,
        "started_utc": "2026-10-31T00:00:00Z",
        "ended_utc": "2026-10-31T00:00:01Z",
        "outputs": {"fixture.json": hashlib.sha256(artifact.read_bytes()).hexdigest()},
    }
    (directory / "manifest.json").write_text(json.dumps(manifest))


def study_index(
    root: Path, claims: dict[str, dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    passing, _ = _runs(root)
    owners = {run["run_id"]: run["study_id"] for run in passing}
    return _study_data(root, claims or {}, owners)


def test_unclaimed_exploratory_run_is_shown_from_its_validated_manifest(tmp_path: Path) -> None:
    write_study(tmp_path, {"run_ids": [RUN_A]})
    write_manifest(tmp_path, RUN_A)
    study = study_index(tmp_path)[0]
    assert study["claim_ids"] == []
    assert study["run_ids"] == [RUN_A]
    assert study["evidence_status"] == "audited-exploratory-synthetic"


def test_declared_and_claim_linked_runs_are_unioned_without_duplicates(tmp_path: Path) -> None:
    write_study(tmp_path, {"run_ids": [RUN_B, RUN_A, RUN_B]})
    write_manifest(tmp_path, RUN_A)
    write_manifest(tmp_path, RUN_B)
    claims = {"DD-C-0001": {"id": "DD-C-0001", "study_id": "DD-024", "run_ids": [RUN_A]}}
    study = study_index(tmp_path, claims)[0]
    assert study["claim_ids"] == ["DD-C-0001"]
    assert study["run_ids"] == [RUN_A, RUN_B]


def test_legacy_claim_only_study_does_not_require_a_declaration(tmp_path: Path) -> None:
    write_study(tmp_path, {})
    write_manifest(tmp_path, RUN_A)
    claims = {"DD-C-0001": {"id": "DD-C-0001", "study_id": "DD-024", "run_ids": [RUN_A]}}
    assert study_index(tmp_path, claims)[0]["run_ids"] == [RUN_A]


@pytest.mark.parametrize("declaration", [None, RUN_A, [123], [""], {}])
def test_malformed_run_declaration_is_rejected(tmp_path: Path, declaration: Any) -> None:
    write_study(tmp_path, {"run_ids": declaration})
    with pytest.raises(RuntimeError, match="invalid declared run IDs"):
        study_index(tmp_path)


@pytest.mark.parametrize("state", ["absent", "failed", "nonzero-exit"])
def test_missing_or_nonpassing_run_is_rejected(tmp_path: Path, state: str) -> None:
    write_study(tmp_path, {"run_ids": [RUN_A]})
    if state != "absent":
        write_manifest(
            tmp_path,
            RUN_A,
            validation_status="failed" if state == "failed" else "passed",
            exit_status=1,
        )
    with pytest.raises(RuntimeError, match="declares missing/nonpassing run"):
        study_index(tmp_path)


def test_run_owned_by_another_study_is_rejected(tmp_path: Path) -> None:
    write_study(tmp_path, {"run_ids": [FOREIGN_RUN]})
    write_manifest(tmp_path, FOREIGN_RUN, study_id="DD-022")
    with pytest.raises(RuntimeError, match="belongs to a different study"):
        study_index(tmp_path)


def test_claim_linked_missing_run_still_fails(tmp_path: Path) -> None:
    write_study(tmp_path, {})
    claims = {"DD-C-0001": {"id": "DD-C-0001", "study_id": "DD-024", "run_ids": [RUN_A]}}
    with pytest.raises(RuntimeError, match="claim refers to missing/nonpassing run"):
        study_index(tmp_path, claims)


def test_public_declaration_cannot_bypass_manifest_output_checks(tmp_path: Path) -> None:
    write_study(tmp_path, {"run_ids": [RUN_A]})
    write_manifest(tmp_path, RUN_A)
    (tmp_path / "results/exploratory" / RUN_A / "fixture.json").write_text("corrupted")
    with pytest.raises(RuntimeError, match="unsafe or invalid public run output"):
        study_index(tmp_path)
