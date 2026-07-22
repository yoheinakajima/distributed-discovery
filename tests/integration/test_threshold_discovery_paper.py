import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/threshold-discovery"
SOURCE = PAPER / "main.tex"
GENERATOR = "distributed_discovery.papers.build_threshold_discovery"


def test_threshold_discovery_paper_has_required_structure_and_boundaries() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    for title in [
        "Introduction",
        "Related literature",
        "Threshold discovery model",
        "Minimum viable teams",
        "Strategic equilibrium and selection",
        "Dynamic attention",
        "Mechanisms for team formation",
        "Benchmark and synthetic predictions",
        "Institutional implications",
        "Limitations",
        "Conclusion",
    ]:
        assert rf"\section{{{title}}}" in source
    assert "no verified novelty claim" in source
    assert "No participants were recruited" in source
    assert "No human data were collected" in source
    assert "No experiment was conducted" in source
    assert set(re.findall(r"DD-C-\d{4}", source)) >= {
        f"DD-C-{number:04d}" for number in range(71, 89)
    }


def test_threshold_discovery_assets_and_validation_are_complete() -> None:
    validation = json.loads((PAPER / "validation.json").read_text(encoding="utf-8"))
    provenance = json.loads((PAPER / "generated/provenance.json").read_text(encoding="utf-8"))
    assert validation["generator"] == GENERATOR
    assert validation["page_count"] in range(20, 33)
    assert validation["byte_reproducible_two_builds"] is True
    assert validation["unresolved_references_citations_or_overfull_boxes"] is False
    assert provenance["generator"] == GENERATOR
    assert len(provenance["source_runs"]) == 7
    assert len(provenance["generated_assets"]) == 8
    assert all(len(value) == 64 for value in provenance["inputs"].values())
    build_log = (PAPER / "build.log").read_text(encoding="utf-8")
    assert "/Users/" not in build_log
    assert "/home/" not in build_log
