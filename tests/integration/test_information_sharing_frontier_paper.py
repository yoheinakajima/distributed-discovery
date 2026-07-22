import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "papers/information-sharing-frontier"
PDF = PAPER / "When_Does_Information_Sharing_Improve_Decentralized_Discovery.pdf"
GENERATOR = "distributed_discovery.papers.build_information_sharing_frontier"


def test_information_sharing_frontier_structure_and_boundaries() -> None:
    source = (PAPER / "main.tex").read_text(encoding="utf-8")
    abstract = (PAPER / "abstract.tex").read_text(encoding="utf-8")
    for title in [
        "Introduction",
        "Discovery architectures and comparison baselines",
        "Signal geometry is not one-person accuracy",
        "Aggregation gain and independent rescue",
        "The General Sharing Frontier",
        "Centralized action-budget recovery",
        "Coordination-free positive sharing",
        "Equilibrium selection and implementation failure",
        "Design implications and limitations",
        "Conclusion",
    ]:
        assert rf"\section{{{title}}}" in source
    assert set(re.findall(r"DD-C-\d{4}", source + abstract)) >= {
        f"DD-C-{number:04d}" for number in range(89, 111)
    }
    assert "not an every-equilibrium result" in abstract
    assert "does not reveal" in abstract
    assert "centralized" in abstract
    assert "no human or real data" in abstract
    assert "every equilibrium improves" not in abstract
    assert source.index("Strict selected sharing gain") < source.index("Selection failure")
    assert "bounded negative result" in source
    assert "not promoted to a general monotonicity theorem" in source.replace("\n", " ")


def test_information_sharing_frontier_generated_contract() -> None:
    validation = json.loads((PAPER / "validation.json").read_text(encoding="utf-8"))
    provenance = json.loads((PAPER / "source-provenance.json").read_text(encoding="utf-8"))
    audit = json.loads((PAPER / "paper-audit.json").read_text(encoding="utf-8"))
    corruption = json.loads((PAPER / "asset-corruption-tests.json").read_text(encoding="utf-8"))
    assert validation["generator"] == GENERATOR
    assert validation["page_count"] in range(26, 41)
    assert validation["byte_reproducible_two_builds"] is True
    assert validation["unresolved_references_citations_or_overfull_boxes"] is False
    assert len(validation["generated_figures"]) == 8
    assert len(validation["generated_tables"]) == 8
    assert len(validation["figure_data"]) == 8
    assert len(provenance["source_runs"]) == 4
    assert len(provenance["claim_ids"]) == 22
    assert audit["passed"] is True and audit["independent_of_generator_import"] is True
    assert corruption["passed"] is True
    assert all(item["rejected"] for item in corruption["tests"])
    assert PDF.is_file()
    assert "/Users/" not in (PAPER / "build.log").read_text(encoding="utf-8")


def test_information_sharing_frontier_metadata_and_ownership() -> None:
    metadata = yaml.safe_load((PAPER / "metadata.yml").read_text(encoding="utf-8"))
    ownership = yaml.safe_load((PAPER / "ownership.yml").read_text(encoding="utf-8"))
    assert metadata["status"] == "working-paper"
    assert metadata["doi"] is None
    assert metadata["submitted"] is False
    assert metadata["peer_reviewed"] is False
    assert ownership["paper"]["status"] == "working-paper"
    assert set(ownership["studies"]) == {"DD-019", "DD-020", "DD-021", "DD-022"}
    claims = [claim for study in ownership["studies"].values() for claim in study["claims"]]
    assert claims == [f"DD-C-{number:04d}" for number in range(89, 111)]
    assert "@misc{Nakajima2026InformationSharingFrontier" in (PAPER / "citation.bib").read_text(
        encoding="utf-8"
    )
