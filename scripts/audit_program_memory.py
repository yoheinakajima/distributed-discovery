#!/usr/bin/env python3
"""Validate the program-memory router without treating it as evidence."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def audit() -> dict[str, Any]:
    registry_path = ROOT / "docs/program-memory/registry.yml"
    source = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    schema = json.loads(
        (ROOT / "docs/program-memory/registry.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(source, schema, format_checker=jsonschema.FormatChecker())
    records = source["records"]
    by_id = {record["idea_id"]: record for record in records}
    assert len(by_id) == len(records)
    assert len({record["proposition"] for record in records}) == len(records)

    classifications: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    for record in records:
        classifications[record["capture_classification"]] += 1
        statuses[record["status"]] += 1
        destination = ROOT / record["canonical_destination"]["path"]
        assert destination.exists(), f"missing canonical destination: {destination}"
        if record["status"] == "owner-adopted":
            assert record["canonical_destination"]["path"]
        if record["status"] == "superseded":
            assert record["superseded_by"]
        if record["capture_classification"] == "evidence-dependent":
            assert record["promotion_trigger"] and record["review_after"]
        serialized = yaml.safe_dump(record).lower()
        assert "chat://" not in serialized
        assert "conversation url" not in serialized
        assert "raw transcript" not in serialized
        assert "api_key" not in serialized
        assert "dd-c-0111" not in serialized
        assert "dd-023" not in serialized

    protocol = yaml.safe_load(
        (ROOT / "docs/governance/conversation-to-repository-protocol.yml").read_text(
            encoding="utf-8"
        )
    )
    assert set(classifications) <= set(protocol["capture_classifications"])
    assert set(statuses) <= set(protocol["durable_statuses"])
    assert {record["review_after"] for record in records if record["review_after"]} <= set(
        protocol["review_triggers"]
    )
    assert "DISCUSSION AND DECISION DELTA AUDIT" in (ROOT / ".agent/PLANS.md").read_text(
        encoding="utf-8"
    )
    return {
        "records": len(records),
        "classifications": dict(sorted(classifications.items())),
        "statuses": dict(sorted(statuses.items())),
        "owner_adopted_unrouted": sum(
            r["status"] == "owner-adopted" and not r["canonical_destination"]["path"]
            for r in records
        ),
        "duplicate_canonical_records": len(records) - len(by_id),
        "raw_transcripts": 0,
    }


if __name__ == "__main__":
    print(audit())
