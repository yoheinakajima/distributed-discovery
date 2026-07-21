import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/common-source-trap"
SOURCE = PAPER / "main.tex"
GENERATOR = "distributed_discovery.papers.build_common_source_trap"


def test_common_source_paper_has_required_structure_and_boundaries() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    for title in [
        "Introduction",
        "Related literature",
        "Model",
        "The two-agent Common-Source Trap",
        "Finite-team classification",
        "General finite-team thresholds",
        "Planner comparison",
        "Acquisition, discovery, and welfare gaps",
        "Institutional remedies",
        "Joint truth and allocation mechanisms",
        "Architecture Atlas implications",
        "Experimental predictions",
        "Limitations",
        "Conclusion",
    ]:
        assert rf"\section{{{title}}}" in source
    assert "not a universal under-acquisition theorem" in source
    assert "No participants were recruited" in source
    assert "no verified novelty claim" in source
    assert set(re.findall(r"DD-C-\d{4}", source)) >= {
        "DD-C-0051",
        "DD-C-0052",
        "DD-C-0053",
        "DD-C-0054",
        "DD-C-0056",
        "DD-C-0057",
        "DD-C-0058",
    }


def test_common_source_assets_and_validation_are_complete() -> None:
    validation = json.loads((PAPER / "validation.json").read_text(encoding="utf-8"))
    provenance = json.loads((PAPER / "generated/provenance.json").read_text(encoding="utf-8"))
    assert validation["generator"] == GENERATOR
    assert validation["page_count"] in range(20, 33)
    assert validation["byte_reproducible_two_builds"] is True
    assert validation["unresolved_references_citations_or_overfull_boxes"] is False
    assert validation["provenance_validated"] is True
    assert provenance["generator"] == GENERATOR
    assert len(provenance["generated_assets"]) == 10
    assert all(len(value) == 64 for value in provenance["inputs"].values())
