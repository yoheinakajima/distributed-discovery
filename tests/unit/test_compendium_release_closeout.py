from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
TAG = "dd-compendium-v0.1.0"
SOURCE_REVISION = "3ca173f4e9e81a6d0e3e56205e428c596edc050e"
VERSION_DOI = "10.5281/zenodo.21535005"
CONCEPT_DOI = "10.5281/zenodo.21535004"

EXPECTED_ASSETS = {
    "distributed-discovery-compendium-v0.1.0-release-evidence-manifest.json": (
        4733,
        "a6c742a3a0ed8e962fb24d05bad236c07fe058ce68ba6b5cf2cd057dc1044f9f",
    ),
    "distributed-discovery-compendium-v0.1.0-SHA256SUMS.txt": (
        511,
        "c6c9417933e305508a3c1ed418fb588b4fa897c471e98076732f30747fcc3231",
    ),
    "distributed-discovery-compendium-v0.1.0-paper-citation-metadata.yml": (
        5725,
        "37c66ed19a9d84cc021eb27567fa74fd399b0f73b34b7aae845486c9420e538c",
    ),
    "distributed-discovery-compendium-v0.1.0-papers.zip": (
        1088601,
        "08bab6f3d0fb7b1c6282b8663a11e1709ded0ee93769f7ee60fec690e01af469",
    ),
    "distributed-discovery-compendium-v0.1.0-release-notes.md": (
        2152,
        "35d757da84ea3a5400db4e64963c3aee484029fe0e3da9c0c07fa54352128b92",
    ),
}


def _registry() -> tuple[dict[str, object], dict[str, object]]:
    registry = yaml.safe_load((ROOT / "docs/releases/releases.yml").read_text())
    schema = json.loads((ROOT / "docs/releases/releases.schema.json").read_text())
    jsonschema.validate(registry, schema, format_checker=jsonschema.FormatChecker())
    return registry, registry["releases"][0]


def test_public_release_registry_validates_and_uses_distinct_doi_roles() -> None:
    registry, release = _registry()
    assert registry["citation_convention"] == {
        "exact_version": VERSION_DOI,
        "evolving_compendium": CONCEPT_DOI,
    }
    assert VERSION_DOI != CONCEPT_DOI
    assert release["tag"] == TAG
    assert release["source_revision"] == SOURCE_REVISION
    assert release["status"] == "published-zenodo-verified"
    assert release["github_release_url"].endswith(f"/releases/tag/{TAG}")


def test_registry_records_exact_custom_assets_and_verified_zenodo_archive() -> None:
    _, release = _registry()
    assets = {item["name"]: (item["bytes"], item["sha256"]) for item in release["custom_assets"]}
    assert assets == EXPECTED_ASSETS
    zenodo = release["zenodo"]
    assert zenodo["record_id"] == 21535005
    assert zenodo["record_url"] == "https://zenodo.org/records/21535005"
    assert zenodo["version_field"] == TAG
    assert zenodo["version_doi"] == VERSION_DOI
    assert zenodo["concept_doi"] == CONCEPT_DOI
    assert zenodo["files"] == [
        {
            "name": "yoheinakajima/distributed-discovery-dd-compendium-v0.1.0.zip",
            "bytes": 25825951,
            "checksum": "md5:b3484739a08bec27499a580b19755aff",
            "sha256": "8f04d5dc25b971c879c59d4f14cccb05459f67269fa486dc9acbdf692a3aa33f",
            "authorized_tree_files": 2379,
            "byte_exact_authorized_tree": True,
        }
    ]


def test_citation_and_closeout_records_match_the_release_registry() -> None:
    _, release = _registry()
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    closeout = yaml.safe_load(
        (ROOT / "reports/releases/compendium-v0.1.0-closeout.yml").read_text()
    )
    assert cff["version"] == release["version"]
    assert str(cff["date-released"]) == release["release_date"]
    assert cff["doi"] == release["zenodo"]["version_doi"]
    assert closeout["release"]["tag"] == release["tag"]
    assert closeout["release"]["source_revision"] == release["source_revision"]
    assert closeout["zenodo"]["version_doi"] == release["zenodo"]["version_doi"]
    assert closeout["zenodo"]["concept_doi"] == release["zenodo"]["concept_doi"]
    assert not (ROOT / ".zenodo.json").exists()


def test_release_did_not_promote_or_expand_the_scientific_program() -> None:
    _, release = _registry()
    assert release["scientific_inventory"] == {
        "claims": 110,
        "maximum_claim_id": "DD-C-0110",
        "studies": 26,
        "maximum_study_id": "DD-022",
        "run_manifests": 51,
        "passing_immutable_runs": 48,
    }
    assert release["papers"] == {
        "local_pdfs": 7,
        "pages": 119,
        "hashes_verified": True,
        "source_changed": False,
        "peer_review_implied": False,
    }
    closeout = yaml.safe_load(
        (ROOT / "reports/releases/compendium-v0.1.0-closeout.yml").read_text()
    )
    assert closeout["created"] == {"claims": 0, "studies": 0, "runs": 0}
    assert closeout["papers"]["lifecycle_changed"] is False
    assert closeout["next_gate"] == (
        "TreasureBench Agents v1 sealed engineering pilot registration and authorization"
    )
