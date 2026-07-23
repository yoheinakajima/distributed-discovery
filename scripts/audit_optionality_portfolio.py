#!/usr/bin/env python3
"""Validate the Phase 2 optionality portfolio and its non-scientific boundary."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def audit() -> dict[str, object]:
    source = yaml.safe_load(
        (ROOT / "docs/strategic-direction/optionality-portfolio.yml").read_text()
    )
    schema = json.loads(
        (ROOT / "docs/strategic-direction/optionality-portfolio.schema.json").read_text()
    )
    jsonschema.validate(source, schema, format_checker=jsonschema.FormatChecker())
    options = source["options"]
    ids = [item["id"] for item in options]
    if len(ids) != len(set(ids)):
        raise RuntimeError("optionality portfolio contains duplicate IDs")
    if ids[0] != source["first_option_to_exercise"]:
        raise RuntimeError("first option is not first in the staged portfolio")
    return {
        "options": len(options),
        "first_option": ids[0],
        "scientific_score": source["measurement_boundary"]["scientific_score"],
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
