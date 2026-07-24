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
    assert result["benchmark_name_decision"] == "owner-name-decision-required"


def test_release_manifest_is_a_deterministic_nonrelease() -> None:
    result = _audit("audit_release_readiness.py")
    assert result == {
        "manifest": "dry-run-only",
        "artifacts": 7,
        "pages": 119,
        "external_identifiers": None,
    }


def test_benchmark_name_gate_preserves_compatibility_until_owner_decides() -> None:
    decision = yaml.safe_load(
        (ROOT / "reports/editorial/benchmark-name-decision.yml").read_text(encoding="utf-8")
    )
    assert decision["decision"] == "owner-name-decision-required"
    assert decision["external_scholarly_name"] is None
    assert decision["rename_implemented"] is False
    assert decision["current_internal_name"] == "DiscoveryBench"
    assert "DD-010" in decision["compatibility_if_later_renamed"]["preserve"]


def test_license_matrix_records_unresolved_owner_decisions_without_relicensing() -> None:
    matrix = yaml.safe_load(
        (ROOT / "docs/licensing/artifact-license-matrix.yml").read_text(encoding="utf-8")
    )
    assert len(matrix["records"]) == 11
    assert matrix["repository_license"] == "MIT"
    assert matrix["license_changes_authorized"] is False
    assert matrix["owner_decisions"]
