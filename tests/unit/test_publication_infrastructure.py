from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _audit(script: str):
    path = ROOT / "scripts" / script
    spec = importlib.util.spec_from_file_location(script.removesuffix(".py"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit()


def test_dependency_edges_cover_every_registered_role() -> None:
    result = _audit("audit_paper_dependencies.py")
    assert result["edges"] >= 8
    assert len(result["roles"]) == 8
    assert result["freeze_blockers"] == 1


def test_foundations_is_not_in_current_arxiv_queue() -> None:
    readiness = yaml.safe_load(
        (ROOT / "reports/editorial/arxiv-readiness-map.yml").read_text(encoding="utf-8")
    )
    record = next(r for r in readiness["records"] if r["paper_id"] == "foundations")
    assert record["readiness_decision"] == "not-an-arxiv-candidate-currently"
    assert readiness["first_freeze_candidate"] == "common-source-trap"


def test_journal_track_is_deferred_not_abandoned() -> None:
    policy = yaml.safe_load(
        (ROOT / "docs/publication/journal-track-policy.yml").read_text(encoding="utf-8")
    )
    assert policy["decision"] == "deferred-not-abandoned"
    assert policy["submission_authorized"] is False


def test_publication_infrastructure_is_null_safe_and_internal_queue_stays_private() -> None:
    result = _audit("audit_publication_infrastructure.py")
    assert result["citation_records"] == 8
    assert result["first_freeze_candidate"] == "common-source-trap"
    assert result["lifecycle_anchor"] == "canonical-public-anchor"
    assert result["benchmark_name_decision"] == "treasurebench-selected-and-implemented"


def test_release_readiness_preserves_dry_run_fixture_and_records_public_release() -> None:
    result = _audit("audit_release_readiness.py")
    assert result == {
        "manifest": "dry-run-only",
        "artifacts": 7,
        "pages": 119,
        "release": "published-zenodo-verified",
        "tag": "dd-compendium-v0.1.0",
        "version_doi": "10.5281/zenodo.21535005",
        "concept_doi": "10.5281/zenodo.21535004",
    }


def test_benchmark_name_gate_records_owner_decision_and_preserves_compatibility() -> None:
    decision = yaml.safe_load(
        (ROOT / "reports/editorial/benchmark-name-decision.yml").read_text(encoding="utf-8")
    )
    assert decision["decision"] == "treasurebench-selected-and-implemented"
    assert decision["external_scholarly_name"] == "TreasureBench"
    assert decision["playable_companion"] == "Treasure Hunt"
    assert decision["rename_implemented"] is True
    assert decision["current_internal_name"] == "DiscoveryBench"
    assert "DD-010" in decision["compatibility"]["preserve"]


def test_license_matrix_records_unresolved_owner_decisions_without_relicensing() -> None:
    matrix = yaml.safe_load(
        (ROOT / "docs/licensing/artifact-license-matrix.yml").read_text(encoding="utf-8")
    )
    assert len(matrix["records"]) == 11
    assert matrix["repository_license"] == "MIT"
    assert matrix["license_changes_authorized"] is False
    assert matrix["owner_decisions"]
