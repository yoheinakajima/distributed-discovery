#!/usr/bin/env python3
"""Validate editorial claim prominence without altering evidence."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {"status", "claim_type", "evidence", "proof", "run_ids", "source_reference"}


def audit() -> dict[str, object]:
    source = yaml.safe_load((ROOT / "docs/claim-prominence.yml").read_text())
    schema = json.loads((ROOT / "docs/claim-prominence.schema.json").read_text())
    jsonschema.validate(source, schema)
    assert not (set(source) & FORBIDDEN)
    ledger = yaml.safe_load((ROOT / "claims/claims.yml").read_text())["claims"]
    ledger_ids = {claim["id"] for claim in ledger}
    assert set(source["claims"]) == ledger_ids
    counts = Counter(source["claims"].values())
    return {"claims": len(ledger_ids), "categories": dict(sorted(counts.items()))}


if __name__ == "__main__":
    print(audit())
