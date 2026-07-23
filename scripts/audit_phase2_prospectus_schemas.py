#!/usr/bin/env python3
"""Validate Gate C and the draft minimal-ledger profile fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def audit() -> dict[str, object]:
    gate = yaml.safe_load(
        (ROOT / "reports/roadmap-consolidation/provenance-gate-c-prospectus.yml").read_text()
    )
    gate_schema = json.loads(
        (
            ROOT / "reports/roadmap-consolidation/provenance-gate-c-prospectus.schema.json"
        ).read_text()
    )
    jsonschema.validate(gate, gate_schema)

    ledger_schema = json.loads(
        (ROOT / "docs/verification/minimal-ledger-profile.schema.json").read_text()
    )
    valid = json.loads((ROOT / "docs/verification/fixtures/valid-minimal-ledger.json").read_text())
    invalid = json.loads(
        (ROOT / "docs/verification/fixtures/invalid-minimal-ledger.json").read_text()
    )
    jsonschema.validate(valid, ledger_schema)
    try:
        jsonschema.validate(invalid, ledger_schema)
    except jsonschema.ValidationError:
        invalid_rejected = True
    else:
        invalid_rejected = False
    if not invalid_rejected:
        raise RuntimeError("invalid minimal-ledger fixture unexpectedly validates")
    return {
        "gate_c_dimensions": len(gate["dimensions"]),
        "minimal_ledger_valid": True,
        "minimal_ledger_invalid_rejected": True,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
