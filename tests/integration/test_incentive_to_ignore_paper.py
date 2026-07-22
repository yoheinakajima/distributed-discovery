import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/incentive-to-ignore"
SOURCE = PAPER / "main.tex"
GENERATOR = "distributed_discovery.papers.build_incentive_to_ignore"


def test_incentive_paper_has_required_structure_and_boundaries() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    for title in [
        "Introduction",
        "Related literature",
        "Model",
        "First-use value and duplicate-use loss",
        "Private attention equilibrium",
        "The attention wedge",
        "Audience design",
        "Information firewalls and implementation",
        "Conditional attention",
        "Institutional implications",
        "Experimental predictions",
        "Limitations",
        "Conclusion",
    ]:
        assert rf"\section{{{title}}}" in source
    assert "no verified novelty claim" in source
    assert "No participants were recruited" in source
    assert "No human data" in source
    assert "No experiment was conducted" in source
    assert set(re.findall(r"DD-C-\d{4}", source)) >= {
        "DD-C-0059",
        "DD-C-0060",
        "DD-C-0061",
        "DD-C-0062",
        "DD-C-0063",
        "DD-C-0064",
        "DD-C-0065",
        "DD-C-0066",
        "DD-C-0067",
        "DD-C-0068",
    }


def test_incentive_paper_assets_and_validation_are_complete() -> None:
    validation = json.loads((PAPER / "validation.json").read_text(encoding="utf-8"))
    provenance = json.loads((PAPER / "generated/provenance.json").read_text(encoding="utf-8"))
    assert validation["generator"] == GENERATOR
    assert validation["page_count"] in range(20, 33)
    assert validation["byte_reproducible_two_builds"] is True
    assert validation["unresolved_references_citations_or_overfull_boxes"] is False
    assert provenance["generator"] == GENERATOR
    assert len(provenance["generated_assets"]) == 9
    assert all(len(value) == 64 for value in provenance["inputs"].values())
    build_log = (PAPER / "build.log").read_text(encoding="utf-8")
    assert "/Users/" not in build_log
    assert "/home/" not in build_log
