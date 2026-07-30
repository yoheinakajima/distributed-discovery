#!/usr/bin/env python3
"""Audit AO-0011 registration, corruptions, and the full offline rehearsal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from distributed_discovery.benchmark.agents_v1.fresh_pilot_v5 import (
    audit_corruptions,
    load_corruption_registry,
    run_protocol_validity_scenarios,
    run_synthetic_rehearsal,
    validate_registration,
)
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v5_live import (
    audit_live_corruptions,
    run_production_permit_custody_rehearsal,
)
from distributed_discovery.benchmark.agents_v1.rehearsal import run_rehearsal

ROOT = Path(__file__).resolve().parents[1]
REHEARSAL = ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v5-offline-rehearsal.yml"
CORRUPTIONS = ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v5-corruptions.yml"
CUSTODY = (
    ROOT
    / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v5-production-custody-rehearsal.yml"
)
SCENARIOS = (
    ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v5-provider-outcome-scenarios.yml"
)


def _load(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected mapping: {path}")
    return value


def audit(*, rehearsal: bool = False) -> dict[str, object]:
    registration = validate_registration(ROOT)
    registry = load_corruption_registry(ROOT)
    observed = (*audit_corruptions(ROOT), *audit_live_corruptions(ROOT))
    by_id = {str(item["corruption_id"]): item for item in observed}
    required_ids = [str(item) for item in registry["corruptions"]]
    if set(by_id) != set(required_ids):
        raise ValueError("v5 corruption implementation and registry differ")
    ordered = [by_id[corruption_id] for corruption_id in required_ids]
    if any(item["status"] != "rejected" for item in ordered):
        raise ValueError("a v5 corruption was accepted")

    repaired = run_rehearsal()
    if repaired["status"] != "pass" or repaired["corruptions_rejected"] != 28:
        raise ValueError("repaired instrument C01-C28 rehearsal is not passing")
    committed_corruptions = _load(CORRUPTIONS)
    if committed_corruptions["corruptions"] != ordered:
        raise ValueError("committed v5 corruption report is stale")

    result: dict[str, object] = {
        **registration,
        "v5_boundary_corruptions_rejected": len(ordered),
        "repaired_instrument_corruptions_reexecuted": 28,
        "total_registered_corruptions_rejected": len(ordered) + 28,
        "repaired_instrument_rehearsal_hash": repaired["rehearsal_hash"],
    }
    if rehearsal:
        full = run_synthetic_rehearsal(ROOT)
        if _load(REHEARSAL) != full:
            raise ValueError("committed v5 full rehearsal report is stale")
        custody = run_production_permit_custody_rehearsal(ROOT)
        if _load(CUSTODY) != custody:
            raise ValueError("committed v5 production custody rehearsal report is stale")
        scenarios = run_protocol_validity_scenarios(ROOT)
        if _load(SCENARIOS) != scenarios:
            raise ValueError("committed v5 protocol-validity scenario report is stale")
        result["rehearsal"] = full
        result["production_custody_rehearsal"] = custody
        result["provider_outcome_scenarios"] = scenarios
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rehearsal", action="store_true")
    args = parser.parse_args()
    print(json.dumps(audit(rehearsal=args.rehearsal), sort_keys=True))


if __name__ == "__main__":
    main()
