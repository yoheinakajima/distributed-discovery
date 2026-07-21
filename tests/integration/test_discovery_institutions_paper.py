import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/discovery-institutions"


def test_discovery_stack_paper_has_scoped_sections_and_provenance() -> None:
    source = (PAPER / "main.tex").read_text(encoding="utf-8")
    for title in [
        "The Discovery Stack",
        "Evidence discipline",
        "Acquisition",
        "Disclosure and allocation",
        "Adaptation",
        "Coverage",
        "Rewards",
        "Measurement",
        "Institutional implications and limitations",
        "Research agenda",
    ]:
        assert rf"\section{{{title}}}" in source
    assert "not a general information-public-good theorem" in source
    assert "arbitrary-transfer-table" in source
    assert "synthetic-only" in source
    assert "\\input{generated/stack-evidence-table.tex}" in source
    assert set(re.findall(r"DD-C-\d{4}", source)) >= {
        "DD-C-0045",
        "DD-C-0046",
        "DD-C-0047",
        "DD-C-0048",
        "DD-C-0049",
        "DD-C-0050",
        "DD-C-0051",
    }


def test_discovery_stack_validation_records_reproducible_pdf() -> None:
    validation = json.loads((PAPER / "validation.json").read_text(encoding="utf-8"))
    assert validation["generator"] == "distributed_discovery.papers.build_discovery_institutions"
    assert validation["page_count"] >= 3
    assert validation["byte_reproducible_two_builds"] is True
    assert validation["unresolved_references_citations_or_overfull_boxes"] is False
    assert set(validation["source_runs"]) == {
        "adaptation",
        "coverage",
        "rewards",
        "measurement",
        "acquisition",
    }
