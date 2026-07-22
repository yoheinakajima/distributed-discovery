"""Validate the presentation-layer copy map used by the public site."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "brand",
    "navigation",
    "home",
    "research",
    "results",
    "labs",
    "papers",
    "benchmark",
    "experiment",
    "study_sections",
    "technical",
    "metadata",
}


def load_copy_map(path: Path) -> dict[str, Any]:
    """Load and validate the presentation copy map without touching research data."""
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise RuntimeError(f"invalid site copy map: {path}")
    missing = REQUIRED_TOP_LEVEL - set(value)
    if missing:
        raise RuntimeError(f"site copy map is missing sections: {sorted(missing)}")
    navigation = value.get("navigation")
    if not isinstance(navigation, dict):
        raise RuntimeError("site copy map navigation must be a mapping")
    primary = navigation.get("primary")
    resources = navigation.get("resources")
    if not isinstance(primary, list) or len(primary) != 5:
        raise RuntimeError("site copy map must define exactly five primary links")
    if not isinstance(resources, list) or not resources:
        raise RuntimeError("site copy map must define footer resources")
    expected = ["Home", "Research", "Findings", "Labs", "Papers"]
    if [item.get("label") for item in primary if isinstance(item, dict)] != expected:
        raise RuntimeError("site copy map primary navigation does not match the brand system")
    for collection in (primary, resources):
        for item in collection:
            if not isinstance(item, dict) or not all(
                isinstance(item.get(key), str) and item[key] for key in ("label", "route")
            ):
                raise RuntimeError("site copy map contains an invalid navigation item")
    return value
