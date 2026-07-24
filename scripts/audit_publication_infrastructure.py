#!/usr/bin/env python3
"""Validate publication policy, citation, lifecycle, licensing, and naming records."""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _yaml(path: str) -> dict[str, Any]:
    value = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _audit_dependencies() -> dict[str, Any]:
    path = ROOT / "scripts/audit_paper_dependencies.py"
    spec = importlib.util.spec_from_file_location("audit_paper_dependencies", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit()


def audit() -> dict[str, Any]:
    citation = _yaml("docs/publication/paper-citation-metadata.yml")
    citation_schema = json.loads(
        (ROOT / "docs/publication/paper-citation-metadata.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(citation, citation_schema, format_checker=jsonschema.FormatChecker())
    assert len(citation["papers"]) == 8
    assert len({paper["paper_id"] for paper in citation["papers"]}) == 8
    assert all(paper["arxiv_id"] is None and paper["doi"] is None for paper in citation["papers"])
    claim_ids = {claim["id"] for claim in _yaml("claims/claims.yml")["claims"]}
    assert all(set(paper["claim_ownership"]) <= claim_ids for paper in citation["papers"])
    existing_run_ids = {
        path.parent.name for path in (ROOT / "results/verified").glob("*/manifest.json")
    }
    for example in citation["examples"]:
        assert example["arxiv_id"] is None and example["doi"] is None
        if example["run_id"]:
            assert example["run_id"] in existing_run_ids

    preprint = _yaml("docs/publication/preprint-first-policy.yml")
    queue = _yaml("reports/editorial/preprint-queue.yml")
    journal = _yaml("docs/publication/journal-track-policy.yml")
    readiness = _yaml("reports/editorial/arxiv-readiness-map.yml")
    assert preprint["decision"] == "preprint-first-journal-deferred"
    assert preprint["public_queue_allowed"] is False
    assert queue["visibility"] == "internal-only"
    assert queue["public_promise_authorized"] is False
    assert queue["first_freeze_candidate"] == readiness["first_freeze_candidate"]
    assert readiness["first_freeze_candidate"] == "common-source-trap"
    foundations = next(
        record for record in readiness["records"] if record["paper_id"] == "foundations"
    )
    assert foundations["readiness_decision"] == "not-an-arxiv-candidate-currently"
    assert journal["decision"] == "deferred-not-abandoned"
    assert journal["submission_authorized"] is False
    assert len(journal["revisit_triggers"]["any_of"]) >= 2
    assert journal["aer_insights"]["status"] == "parked-journal-track-only"

    lifecycle = _yaml("docs/paper-lifecycle.yml")
    anchor = next(
        record
        for record in lifecycle["records"]
        if record["paper_id"] == "shared-discovery-paradox"
    )
    assert anchor["publication_status"] == "canonical-public-anchor"
    assert anchor["lifecycle_class"] == "canonical-public-anchor"
    assert "canonical-published" not in yaml.safe_dump(lifecycle)
    migration = _yaml("reports/editorial/lifecycle-terminology-decision.yml")
    assert migration["deprecated_aliases"]["canonical-published"] == "canonical-public-anchor"

    licensing = _yaml("docs/licensing/artifact-license-matrix.yml")
    required_categories = {
        "code",
        "machine-readable-data",
        "schemas",
        "fixtures",
        "site-code",
        "site-prose",
        "paper-source",
        "pdfs",
        "generated-figures",
        "pinned-upstream-content",
        "third-party-citations-and-assets",
    }
    categories = {record["category"] for record in licensing["records"]}
    assert categories == required_categories
    assert licensing["license_changes_authorized"] is False
    assert licensing["owner_decisions"]

    candidates = _yaml("reports/editorial/benchmark-name-candidates.yml")
    naming = _yaml("reports/editorial/benchmark-name-decision.yml")
    assert len(candidates["candidates"]) >= 10
    for candidate in candidates["candidates"]:
        assert sum(candidate["scores"].values()) == candidate["total"]
    ranked = sorted(candidates["candidates"], key=lambda item: (-item["total"], item["name"]))
    assert ranked[0]["name"] == "ActionPortfolioBench"
    assert ranked[0]["total"] == 91
    assert ranked[0]["total"] - ranked[1]["total"] == 5
    discoverybench = next(
        item for item in candidates["candidates"] if item["name"] == "DiscoveryBench"
    )
    assert discoverybench["fatal_collision"] is True
    assert naming["decision"] == "owner-name-decision-required"
    assert naming["external_scholarly_name"] is None
    assert naming["rename_implemented"] is False
    assert naming["current_internal_name"] == "DiscoveryBench"

    framework = _yaml("reports/editorial/post-discoverybench-publication-decision-framework.yml")
    assert len(framework["branches"]) == 6
    assert framework["actions_authorized"] == []
    rejections = _yaml("reports/editorial/publication-options-rejection-log.yml")
    assert len(rejections["options"]) == 5
    dependency_result = _audit_dependencies()
    roles = Counter(
        edge["role"] for edge in _yaml("docs/publication/paper-dependency-edges.yml")["edges"]
    )
    assert len(roles) == 8

    public_sources = (ROOT / "src/distributed_discovery/site/build.py").read_text(
        encoding="utf-8"
    ) + (ROOT / "site/README.md").read_text(encoding="utf-8")
    assert "preprint-queue" not in public_sources
    assert "coming soon" not in public_sources.lower()
    return {
        "citation_records": len(citation["papers"]),
        "dependency_edges": dependency_result["edges"],
        "dependency_roles": dict(sorted(roles.items())),
        "first_freeze_candidate": readiness["first_freeze_candidate"],
        "lifecycle_anchor": anchor["lifecycle_class"],
        "licensing_categories": len(categories),
        "benchmark_name_decision": naming["decision"],
    }


if __name__ == "__main__":
    print(audit())
