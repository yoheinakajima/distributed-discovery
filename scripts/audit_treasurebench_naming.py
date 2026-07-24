#!/usr/bin/env python3
"""Audit the TreasureBench/Treasure Hunt naming and compatibility contract."""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from distributed_discovery.site.build import build

ROOT = Path(__file__).resolve().parents[1]
SUBTITLE = "TreasureBench: a benchmark for collective search under shared and private evidence."
ATTRIBUTION = "The playable companion to the TreasureBench suite."
KEYWORDS = {"collective search", "multi-agent", "benchmark", "shared"}
LEGACY_ROUTES = {
    "benchmark.html": "treasurebench.html",
    "benchmark/tasks.html": "treasurebench/tasks.html",
    "benchmark/protocols.html": "treasurebench/protocols.html",
    "benchmark/metrics.html": "treasurebench/metrics.html",
    "benchmark/results.html": "treasurebench/results.html",
    "benchmark/attention.html": "treasurebench/attention.html",
    "benchmark/agents-v1.html": "treasurebench/agents-v1.html",
}
FROZEN_SCHEMA_HASHES = {
    "task-v1.schema.json": "5bfca5952c35823986137f4c13740d9c56d90ef1fdb0d11ac7f9bd2c0fa90d92",
    "task-v2.schema.json": "c52bb69bbfa76ffeee316b02aad3d5c0d72ab46643de596cc2025f64344bc6f2",
    "task-v3.schema.json": "9da2709a5790afeecd7c8e6dac81c3215cbdb15731f6dd6a77ddda2e6ce7c5d1",
}


def _yaml(relative: str) -> dict[str, Any]:
    value = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict), relative
    return value


def _visible_text(source: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", source).split())


def audit() -> dict[str, Any]:
    naming = _yaml("docs/benchmark/treasurebench-naming-system.yml")
    schema = json.loads(
        (ROOT / "docs/benchmark/treasurebench-naming-system.schema.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.validate(naming, schema, format_checker=jsonschema.FormatChecker())
    assert naming["formal_suite"]["name"] == "TreasureBench"
    assert naming["formal_suite"]["subtitle"] == SUBTITLE
    assert set(naming["formal_suite"]["keywords"]) == KEYWORDS
    assert naming["companion"]["name"] == "Treasure Hunt"
    assert naming["companion"]["required_attribution"] == ATTRIBUTION
    assert naming["companion"]["separate_benchmark"] is False
    assert naming["historical_alias"]["name"] == "DiscoveryBench"
    assert naming["fixture"]["preferred_terms"] == [
        "the sixteen-box model",
        "the sixteen-box game",
    ]
    assert naming["legal_clearance"] is False
    assert naming["global_uniqueness_claimed"] is False

    decision = _yaml("reports/editorial/benchmark-name-decision.yml")
    clearance = _yaml("reports/editorial/treasurebench-name-clearance-decision.yml")
    assert decision["decision"] == "treasurebench-selected-and-implemented"
    assert decision["external_scholarly_name"] == "TreasureBench"
    assert decision["playable_companion"] == "Treasure Hunt"
    assert decision["rename_implemented"] is True
    assert decision["partial_rename_permitted"] is False
    assert clearance["legal_clearance"] is False
    assert clearance["global_uniqueness_claimed"] is False
    assert clearance["namespace_ownership_claimed"] is False

    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "distributed-discovery"' in pyproject
    assert 'treasurebench = "distributed_discovery.cli:treasurebench_main"' in pyproject

    for name, expected in FROZEN_SCHEMA_HASHES.items():
        path = ROOT / "studies/DD-010-discoverybench/schemas" / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
        source = json.loads(path.read_text(encoding="utf-8"))
        assert "/discoverybench-task-v" in str(source["$id"])

    formal_namespace_sources = [
        ROOT / "claims/claims.yml",
        *sorted((ROOT / "studies/DD-010-discoverybench/schemas").glob("*.json")),
    ]
    assert all(
        "Treasure Hunt" not in path.read_text(encoding="utf-8") for path in formal_namespace_sources
    )

    readme_opening = (ROOT / "README.md").read_text(encoding="utf-8")[:2200]
    assert "TreasureBench" in readme_opening
    assert "Treasure Hunt" in readme_opening
    announcement = (ROOT / "docs/benchmark/treasurebench-announcement-copy.md").read_text(
        encoding="utf-8"
    )
    assert "TreasureBench" in announcement[:800] and "Treasure Hunt" in announcement[:800]

    with tempfile.TemporaryDirectory(prefix="treasurebench-audit-") as temporary:
        output = Path(temporary) / "site"
        report = build(ROOT, output)
        formal_overview = (output / "treasurebench.html").read_text(encoding="utf-8")
        formal_visible = _visible_text(formal_overview)
        assert SUBTITLE in formal_visible
        assert "Treasure Hunt is the interactive playable companion." in formal_visible
        assert 'href="treasure-hunt.html"' in formal_overview

        companion = (output / "treasure-hunt.html").read_text(encoding="utf-8")
        companion_visible = _visible_text(companion)
        assert ATTRIBUTION in companion_visible
        assert "Treasure Hunt is not a separate benchmark." in companion_visible
        assert 'href="treasurebench.html"' in companion
        assert "<noscript>" in companion
        assert companion.count("<h1") == 1
        assert all(
            title in companion_visible
            for title in (
                "Better maps, one shovel hole",
                "Split the crew",
                "Copied maps",
                "One map reader",
                "Minimum digging crew",
            )
        )

        for legacy, canonical in LEGACY_ROUTES.items():
            legacy_page = output / legacy
            canonical_page = output / canonical
            assert legacy_page.is_file() and canonical_page.is_file()
            source = legacy_page.read_text(encoding="utf-8")
            assert "Historical route." in source
            assert f'{canonical}"' in source
            assert (
                f'<link rel="canonical" href="https://yoheinakajima.github.io/distributed-discovery/{canonical}">'
                in source
            )

        route_aliases = json.loads((output / "data/route-aliases.json").read_text(encoding="utf-8"))
        assert {
            item["legacy"]: item["canonical"] for item in route_aliases["aliases"]
        } == LEGACY_ROUTES
        formal_metadata = json.loads(
            (output / "data/treasurebench/naming.json").read_text(encoding="utf-8")
        )
        assert formal_metadata["formal_suite"]["name"] == "TreasureBench"
        assert set(formal_metadata["formal_suite"]["keywords"]) == KEYWORDS
        assert formal_metadata["companion"]["role"] == "interactive-companion"
        assert (output / "data/benchmark/results.json").is_file()
        assert (output / "data/treasurebench/results.json").is_file()

        forbidden_artifact_names = {"SharedBench", "SharedSearch", "SharedHunt"}
        current_display = "\n".join(
            [
                formal_overview,
                companion,
                (output / "data/treasurebench/naming.json").read_text(encoding="utf-8"),
            ]
        )
        assert not forbidden_artifact_names.intersection(current_display.split())

    return {
        "decision": "treasurebench-selected-and-implemented",
        "audit_date": "2026-07-23",
        "formal_suite": "TreasureBench",
        "companion": "Treasure Hunt",
        "historical_alias": "DiscoveryBench",
        "canonical_routes": 7,
        "historical_routes": 7,
        "funnel": "pass",
        "frozen_schema_hashes": "pass",
        "root_distribution": "distributed-discovery",
        "site_pages": report["page_count"],
        "legal_clearance": False,
        "namespace_reserved": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
