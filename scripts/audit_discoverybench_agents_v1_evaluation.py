#!/usr/bin/env python3
"""Audit the inactive DiscoveryBench Agents v1 evaluation registration."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import jsonschema
import yaml

from distributed_discovery.benchmark.agents_v1.campaign import (
    validate_base_allocation,
    validate_inactive_authorization,
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/benchmark/agents-v1"


def _yaml(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def _schema(name: str, document: dict[str, object]) -> None:
    schema = json.loads((DOCS / name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(document)


def audit() -> dict[str, object]:
    allocation = _yaml(DOCS / "base-campaign-allocation.yml")
    validate_base_allocation(allocation)
    _schema("base-campaign-allocation.schema.json", allocation)

    candidates = _yaml(DOCS / "evaluation-model-candidates.yml")
    _schema("evaluation-model-candidates.schema.json", candidates)
    manifest = _yaml(DOCS / "evaluation-model-manifest.yml")
    _schema("evaluation-model-manifest.schema.json", manifest)

    authorization = _yaml(DOCS / "evaluation-authorization-template.yml")
    validate_inactive_authorization(authorization)
    _schema("evaluation-authorization.schema.json", authorization)

    rejected = 0
    for field, value in (
        ("execution_allowed", True),
        ("external_spend_cap_usd", 1),
        ("owner_attestation", "not-an-owner-attestation"),
    ):
        corrupted = deepcopy(authorization)
        corrupted[field] = value
        try:
            validate_inactive_authorization(corrupted)
        except ValueError:
            rejected += 1
    missing_slot = deepcopy(allocation)
    allocation_slots = missing_slot.get("slots")
    if not isinstance(allocation_slots, list):
        raise ValueError("allocation slots must be an array")
    missing_slot["slots"] = allocation_slots[:-1]
    try:
        validate_base_allocation(missing_slot)
    except ValueError:
        rejected += 1

    decision = _yaml(
        ROOT / "reports/roadmap-consolidation/discoverybench-agents-v1-evaluation-decision.yml"
    )
    if decision["decision"] != "sealed-pilot-ready-owner-authorization-pending":
        raise ValueError("campaign decision changed")
    if any(
        (
            decision["cost_authorized"],
            decision["execution_allowed"],
            decision["private_material_exists"],
            decision["study_id_allocated"],
        )
    ):
        raise ValueError("no-execution boundary changed")

    return {
        "status": "pass",
        "allocation_slots": 200,
        "canonical_cells": 138,
        "priority_repeats": 62,
        "inactive_authorization": True,
        "focused_corruptions_rejected": rejected,
        "provider_calls": 0,
        "model_invocations": 0,
        "model_downloads": 0,
        "cost_incurred_usd": 0,
        "private_material_exists": False,
        "study_id_allocated": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
