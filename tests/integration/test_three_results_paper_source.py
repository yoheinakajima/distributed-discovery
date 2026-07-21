import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/three-results"
SOURCE = PAPER / "main.tex"
GENERATOR = "distributed_discovery.papers.build_three_results"
RUNS = {
    "roles": "20260720T200447Z_DD-001_6eb12861_ba766d1eba",
    "signatures": "20260720T221139Z_DD-001_b1d8d431_40bf5b06a5",
    "thresholds": "20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1",
    "disclosure": "20260720T225848Z_DD-002_94607423_e29b1460ae",
    "sources": "20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1",
    "canonical": "20260721T012208Z_DD-000_8e4b55e2_e8321d1048",
    "alignment": "20260721T022739Z_DD-001_358cb1eb_cd16846ba5",
}


def test_three_results_paper_has_required_structure_and_boundaries() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    required_sections = [
        "Introduction",
        "Framework and evidence discipline",
        "Private roles without communication",
        "Information disclosure under strategic search",
        "Correlated source networks",
        "Unified implications",
        "Limitations",
        "Research agenda",
        "Conclusion",
    ]
    assert "Three Results in Distributed Discovery" in text
    for section in required_sections:
        assert rf"\section{{{section}}}" in text
    assert "selection-dependent" in text
    assert "bounded null" in text
    assert "alignment-preserving" in text
    assert "randomized optimum is identical" in text
    assert len(re.findall(r"% Claims: DD-C-", text)) >= 8


def test_three_results_numeric_assets_are_generated_inputs() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    inputs = re.findall(r"\\input\{generated/([^}]+)\}", text)
    assert inputs == [
        "evidence-status-table.tex",
        "roles-figure.tex",
        "disclosure-figure.tex",
        "sources-figure.tex",
    ]


def test_three_results_generated_assets_have_complete_provenance() -> None:
    provenance = json.loads((PAPER / "generated/provenance.json").read_text(encoding="utf-8"))
    validation = json.loads((PAPER / "validation.json").read_text(encoding="utf-8"))
    assert provenance["generator"] == GENERATOR
    assert provenance["source_runs"] == RUNS
    assert set(provenance["generated_assets"]) == {
        "evidence-status-table.tex",
        "roles-figure.tex",
        "disclosure-figure.tex",
        "sources-figure.tex",
    }
    assert all(len(checksum) == 64 for checksum in provenance["inputs"].values())
    assert validation["page_count"] in range(12, 21)
    assert validation["byte_reproducible_two_builds"] is True
    assert validation["provenance_validated"] is True
    assert validation["unresolved_references_citations_or_overfull_boxes"] is False
