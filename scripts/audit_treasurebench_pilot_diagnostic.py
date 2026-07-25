#!/usr/bin/env python3
"""Audit public Phase A diagnostic records without private-state access."""

from __future__ import annotations

import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.pilot_diagnostic import (
    diagnose_synthetic_cases,
    load_public_yaml,
    validate_phase_a_documents,
)


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    fixture = load_public_yaml(
        repo / "docs/benchmark/agents-v1/fixtures/pilot-diagnostic-synthetic-cases.yml"
    )
    result = {
        **validate_phase_a_documents(repo),
        "synthetic": diagnose_synthetic_cases(fixture),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
