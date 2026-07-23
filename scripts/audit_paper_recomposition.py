#!/usr/bin/env python3
"""Validate the paper recomposition prospectus."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def audit() -> dict[str, object]:
    source = yaml.safe_load((ROOT / "docs/paper-recomposition-map.yml").read_text())
    schema = json.loads((ROOT / "docs/paper-recomposition.schema.json").read_text())
    jsonschema.validate(source, schema)
    lifecycle = yaml.safe_load((ROOT / "docs/paper-lifecycle.yml").read_text())["records"]
    lifecycle_ids = {record["paper_id"] for record in lifecycle}
    records = source["records"]
    assert {record["paper_id"] for record in records} == lifecycle_ids
    assert all(record["no_action_rationale"] for record in records)
    assert all(
        record["candidate_disposition"] != "locked-canonical-anchor"
        or record["paper_id"] == "shared-discovery-paradox"
        for record in records
    )
    assert all(record["editorial_status"] == "active" for record in lifecycle)
    return {"records": len(records), "workflow_steps": len(source["workflow"])}


if __name__ == "__main__":
    print(audit())
