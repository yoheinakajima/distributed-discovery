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
    compact = source.replace("\n", " ")
    assert "independently implemented repository verification" in compact
    assert "not external replication" in compact
    assert "511 parameter chains" in compact
    assert "2,044 adjacent transitions" in compact
    assert "whether mixed curves are feasible within each registered family" in compact
    assert "was not tested" in compact


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
    assert len(validation["generated_tables"]) == 9
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


def test_information_sharing_frontier_review_corrections_are_source_generated() -> None:
    sharing = (PAPER / "tables/sharing-paths.tex").read_text(encoding="utf-8")
    strategic = (PAPER / "tables/strategic-gain-by-accuracy.tex").read_text(encoding="utf-8")
    registry = (PAPER / "tables/registry-counts.tex").read_text(encoding="utf-8")
    witnesses = (PAPER / "tables/minimal-witnesses.tex").read_text(encoding="utf-8")
    claim_map = (PAPER / "tables/claim-evidence-map.tex").read_text(encoding="utf-8")

    assert "$C_2$" in sharing
    for value in ["$1/2$", "$5/6$", "$4/9$", "$11/16$"]:
        assert value in sharing
    for row in [
        r"$1/2$ & 0 & 7 & 0",
        r"$11/20$ & 4 & 1 & 2",
        r"$3/5$ & 2 & 1 & 4",
        r"$13/20$ & 0 & 1 & 6",
        r"$2/3$ & 0 & 1 & 6",
        r"$1$ & 0 & 7 & 0",
    ]:
        assert row in strategic
    for claim in ["DD-C-0099", "DD-C-0101", "DD-C-0102", "DD-C-0103"]:
        assert claim in registry
    assert "DD-C-0100" in witnesses
    assert all(claim not in witnesses for claim in ["DD-C-0101", "DD-C-0102", "DD-C-0103"])
    assert "independently implemented repository verification" in claim_map
    assert "external replication" in claim_map


def test_information_sharing_frontier_public_evidence_access_is_exact() -> None:
    source = (PAPER / "main.tex").read_text(encoding="utf-8")
    for token in [
        "66ba4449572b20c519a4629ef20cfc030fae1762",
        "82f8c71d65b27a48b075d06d0a186040cc9e6015aaee9bc695ff2e9fa823a972",
        "69ac4c760d7a34b6ee315ae619287b7928f69cc8a20eaf4a62202868baadcacd",
        "3d905723eda6069cf870f1fb7b2a241cfa592ea43e9009473bd2b0878bdd5bb1",
        "a4f63d52f402ce14f91e469d4b425ce65a92740b31530c7da9384cc726030e3a",
        "3521286a341595d27b95248a0720f4df672bb1b811d17edf7f286b5520912697",
        "98fb7d475365548fcc723603b3c3721e673b0b0423bc89579c411c3252ac54f1",
    ]:
        assert token in source
