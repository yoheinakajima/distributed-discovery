from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from distributed_discovery.benchmark.agents_v1.campaign import (
    build_base_allocation,
    validate_base_allocation,
    validate_inactive_authorization,
)

ROOT = Path(__file__).resolve().parents[1]


def _yaml(path: str) -> dict[str, object]:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_base_allocation_is_deterministic_balanced_and_public_only() -> None:
    committed = _yaml("docs/benchmark/agents-v1/base-campaign-allocation.yml")
    assert committed == build_base_allocation()
    validate_base_allocation(committed)
    assert committed["counts"] == {
        "slots": 200,
        "batches": 4,
        "slots_per_batch": 50,
        "families": 5,
        "slots_per_family": 40,
        "canonical_cells_covered": 138,
        "boundary_priority_repeats": 62,
        "private_instances_generated": 0,
    }
    text = (ROOT / "docs/benchmark/agents-v1/base-campaign-allocation.yml").read_text()
    assert "seed:" not in text
    assert "answer_key" not in text
    assert "holdout" not in text


def test_allocation_corruptions_reject() -> None:
    allocation = build_base_allocation()
    missing = deepcopy(allocation)
    missing_slots = missing["slots"]
    assert isinstance(missing_slots, list)
    missing["slots"] = missing_slots[:-1]
    with pytest.raises(ValueError, match="200"):
        validate_base_allocation(missing)
    unbalanced = deepcopy(allocation)
    slots = unbalanced["slots"]
    assert isinstance(slots, list)
    slots[0]["target_relabeling_class"] = "target-B"
    with pytest.raises(ValueError, match="isomorphism"):
        validate_base_allocation(unbalanced)


def test_authorization_template_is_inactive_and_positive_mutations_reject() -> None:
    authorization = _yaml("docs/benchmark/agents-v1/evaluation-authorization-template.yml")
    validate_inactive_authorization(authorization)
    assert authorization["external_spend_cap_usd"] == 0
    assert authorization["execution_allowed"] is False
    assert authorization["owner_attestation"] is None
    for field, value in (
        ("external_spend_cap_usd", 1),
        ("execution_allowed", True),
        ("owner_attestation", "fabricated"),
    ):
        mutation = deepcopy(authorization)
        mutation[field] = value
        with pytest.raises(ValueError):
            validate_inactive_authorization(mutation)


def test_tier_model_hardware_and_study_boundaries() -> None:
    tier = _yaml("reports/benchmark/agents-v1-campaign-tier-decision.yml")
    hardware = _yaml("reports/benchmark/agents-v1-local-hardware-audit.yml")
    model = _yaml("docs/benchmark/agents-v1/evaluation-model-manifest.yml")
    prospectus = _yaml("plans/discoverybench-agents-v1-evaluation-study-prospectus/status.yml")
    hardware_candidate = hardware["candidate"]
    local_model = model["local_model"]
    assert isinstance(hardware_candidate, dict)
    assert isinstance(local_model, dict)
    assert tier["selected_next_tier"] == "sealed-engineering-pilot"
    assert hardware_candidate["current_host_feasible"] is False
    assert local_model["current_host_eligible"] is False
    assert prospectus["study_id_allocated"] is False
    assert not (ROOT / "studies/DD-023-discoverybench-agents-v1-evaluation").exists()


def test_evaluation_audit_passes_without_execution() -> None:
    path = ROOT / "scripts/audit_discoverybench_agents_v1_evaluation.py"
    spec = importlib.util.spec_from_file_location("evaluation_audit", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.audit() == {
        "status": "pass",
        "allocation_slots": 200,
        "canonical_cells": 138,
        "priority_repeats": 62,
        "inactive_authorization": True,
        "focused_corruptions_rejected": 4,
        "provider_calls": 0,
        "model_invocations": 0,
        "model_downloads": 0,
        "cost_incurred_usd": 0,
        "private_material_exists": False,
        "study_id_allocated": False,
    }
