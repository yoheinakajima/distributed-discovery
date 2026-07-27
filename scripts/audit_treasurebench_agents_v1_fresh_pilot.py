#!/usr/bin/env python3
"""Audit the fresh repair-confirmation registration and offline rehearsal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from distributed_discovery.benchmark.agents_v1.fresh_pilot import (
    audit_corruptions,
    run_synthetic_rehearsal,
    validate_registration,
)
from distributed_discovery.benchmark.agents_v1.fresh_pilot_live import (
    audit_live_corruptions,
)

ROOT = Path(__file__).resolve().parents[1]
REHEARSAL = ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-offline-rehearsal.yml"
CORRUPTIONS = ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-corruptions.yml"
REPAIRED = ROOT / "reports/benchmark/treasurebench-agents-v1-pilot-repair-rehearsal.yml"


def _load(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected mapping: {path}")
    return value


def audit(*, rehearsal: bool = False) -> dict[str, object]:
    registration = validate_registration(ROOT)
    corruptions = audit_corruptions(ROOT)
    live_corruptions = audit_live_corruptions(ROOT)
    committed_corruptions = _load(CORRUPTIONS)
    combined_corruptions = (*corruptions, *live_corruptions)
    if committed_corruptions["corruptions"] != list(combined_corruptions):
        raise ValueError("committed fresh corruption report is stale")
    repaired = _load(REPAIRED)
    if repaired["status"] != "pass" or repaired["corruptions_rejected"] != 28:
        raise ValueError("repaired instrument corruption suite is not passing")
    result: dict[str, object] = {
        **registration,
        "fresh_boundary_corruptions_rejected": len(combined_corruptions),
        "repaired_instrument_corruptions_rejected": 28,
        "total_registered_corruptions_rejected": len(combined_corruptions) + 28,
    }
    if rehearsal:
        observed = run_synthetic_rehearsal(ROOT)
        if _load(REHEARSAL) != observed:
            raise ValueError("committed fresh rehearsal report is stale")
        result["rehearsal"] = observed
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rehearsal", action="store_true")
    args = parser.parse_args()
    print(json.dumps(audit(rehearsal=args.rehearsal), sort_keys=True))


if __name__ == "__main__":
    main()
