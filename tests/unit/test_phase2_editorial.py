from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_literature_transmission_is_complete_and_limited() -> None:
    result = _load_script("audit_literature_transmission.py").audit()
    assert result["entries"] == 15
    source = yaml.safe_load((ROOT / "docs/literature/family-coverage.yml").read_text())
    assert not any(source["audit_limits"].values())


def test_claim_prominence_maps_every_claim_without_evidence_fields() -> None:
    result = _load_script("audit_claim_prominence.py").audit()
    assert result["claims"] == 110
    assert sum(result["categories"].values()) == 110


def test_phase2_maturity_schema_and_ai_native_boundary() -> None:
    source = yaml.safe_load((ROOT / "docs/phase-2-maturity.yml").read_text())
    schema = json.loads((ROOT / "docs/phase-2-maturity.schema.json").read_text())
    jsonschema.validate(source, schema)
    assert source["level_5_is_external_validation"] is False
    assert source["external_validation_claimed"] is False
    assert all(item["complete"] is False for item in source["ai_native_robustness"])


def test_publication_hierarchy_has_four_layers_and_no_submission_claim() -> None:
    source = yaml.safe_load((ROOT / "docs/publication-hierarchy.yml").read_text())
    assert len(source["layers"]) == 4
    assert source["universal_status"] == {
        "submitted": False,
        "peer_reviewed": False,
        "doi_present": False,
    }


def test_discoverybench_agents_gate_has_registered_campaign_but_no_execution() -> None:
    prospectus = yaml.safe_load(
        (ROOT / "reports/roadmap-consolidation/discoverybench-agents-v1-prospectus.yml").read_text()
    )
    assert prospectus["study_id"] is None
    assert prospectus["provider_calls"] is False
    assert prospectus["agents_executed"] is False
    assert prospectus["traces_exist"] is False
    assert prospectus["private_seeds_exist"] is False
    assert prospectus["encrypted_holdouts_exist"] is False
    assert prospectus["human_custodian"] is False
    assert "csprng-automated-seed-generation" in prospectus["contamination_controls"]
    assert (
        "exact-and-near-verbatim-public-value-wording-id-and-solution-pattern-probes"
        in prospectus["contamination_controls"]
    )
    assert len(prospectus["required_frozen_dimensions"]) == 23
    assert len(prospectus["registration_stops"]) == 8
    assert (ROOT / "plans/DISCOVERYBENCH_AGENTS_V1_REGISTRATION.md").is_file()
    assert (ROOT / "plans/DISCOVERYBENCH_AGENTS_V1_IMPLEMENTATION.md").is_file()
    assert (
        ROOT / "reports/benchmark/discoverybench-agents-v1-implementation-decision.yml"
    ).is_file()
    assert (ROOT / "plans/DISCOVERYBENCH_AGENTS_V1_EVALUATION.md").is_file()
    assert not (ROOT / "plans/DISCOVERYBENCH_AGENTS_V1_EXECUTION.md").exists()


def test_phase2_theorem_gates_are_unregistered_and_bounded() -> None:
    source = yaml.safe_load(
        (ROOT / "reports/roadmap-consolidation/phase-2-theorem-gates.yml").read_text()
    )
    assert source["registered"] is False
    assert [gate["order"] for gate in source["gates"]] == [1, 2, 3]
    required = {
        "scope_boundary",
        "closest_literature",
        "minimum_model_map",
        "required_nonoverlap_witness",
        "permitted_positive_result",
        "permitted_impossibility",
        "permitted_bounded_null",
        "permitted_classical_overlap_stop",
        "dependencies",
        "reason_not_registered",
        "paper_gate",
        "prohibited_claims",
    }
    assert all(required <= gate.keys() for gate in source["gates"])
