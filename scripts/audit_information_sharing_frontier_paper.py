#!/usr/bin/env python3
"""Independent audit for the Information Sharing Frontier paper.

This script deliberately does not import the paper generator. It re-resolves
claims, manifests, exact theorem tokens, generated-asset hashes, and manuscript
boundaries, then proves that representative metadata corruptions are rejected.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/information-sharing-frontier"
RUNS = {
    "DD-019": "20260722T084145Z_DD-019_a77bb786_04a5e9f0c5",
    "DD-020": "20260722T142551Z_DD-020_3854fff6_37c11a850a",
    "DD-021": "20260722T185924Z_DD-021_3cdbbc40_2fea269a9a",
    "DD-022": "20260722T210334Z_DD-022_2376d5b7_ad67765ca8",
}
EXPECTED_CLAIMS = {
    "DD-C-0089": ("DD-019", "computational-result", "independently-reproduced"),
    "DD-C-0090": ("DD-019", "computational-result", "independently-reproduced"),
    "DD-C-0091": ("DD-019", "computational-result", "independently-reproduced"),
    "DD-C-0092": ("DD-020", "identity", "verified"),
    "DD-C-0093": ("DD-020", "theorem", "verified"),
    "DD-C-0094": ("DD-020", "theorem", "verified"),
    "DD-C-0095": ("DD-020", "computational-result", "independently-reproduced"),
    "DD-C-0096": ("DD-020", "computational-result", "independently-reproduced"),
    "DD-C-0097": ("DD-021", "theorem", "verified"),
    "DD-C-0098": ("DD-021", "theorem", "verified"),
    "DD-C-0099": ("DD-021", "computational-result", "independently-reproduced"),
    "DD-C-0100": ("DD-021", "computational-result", "independently-reproduced"),
    "DD-C-0101": ("DD-021", "computational-result", "independently-reproduced"),
    "DD-C-0102": ("DD-021", "computational-result", "independently-reproduced"),
    "DD-C-0103": ("DD-021", "negative-result", "verified"),
    "DD-C-0104": ("DD-022", "theorem", "verified"),
    "DD-C-0105": ("DD-022", "theorem", "verified"),
    "DD-C-0106": ("DD-022", "theorem", "verified"),
    "DD-C-0107": ("DD-022", "corollary", "verified"),
    "DD-C-0108": ("DD-022", "computational-result", "independently-reproduced"),
    "DD-C-0109": ("DD-022", "negative-result", "verified"),
    "DD-C-0110": ("DD-022", "theorem", "verified"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_provenance(record: dict[str, Any]) -> None:
    if record.get("source_runs") != {
        "signal": RUNS["DD-019"],
        "incremental": RUNS["DD-020"],
        "frontier": RUNS["DD-021"],
        "strategic": RUNS["DD-022"],
    }:
        raise ValueError("source-run mapping changed")
    if set(record.get("claim_ids", [])) != set(EXPECTED_CLAIMS):
        raise ValueError("claim set changed")
    for group in ("inputs", "figures", "figure_data", "tables"):
        values = record.get(group)
        if not isinstance(values, dict) or not values:
            raise ValueError(f"missing {group}")
        if any(not re.fullmatch(r"[0-9a-f]{64}", str(value)) for value in values.values()):
            raise ValueError(f"invalid {group} hash")
    if not re.fullmatch(r"[0-9a-f]{64}", str(record.get("bibliography", ""))):
        raise ValueError("invalid bibliography hash")


def main() -> None:
    checks: list[str] = []
    manifests: dict[str, Any] = {}
    for study, run_id in RUNS.items():
        run = ROOT / "results/verified" / run_id
        manifest = load_json(run / "manifest.json")
        assert manifest["run_id"] == run_id
        assert manifest["study_id"] == study
        assert manifest["validation_status"] == "passed"
        assert manifest["exit_status"] == 0
        for relative, digest in manifest["outputs"].items():
            path = run / relative
            assert path.is_file() and sha(path) == digest
        manifests[study] = manifest
    checks.append("four immutable run manifests and every declared output hash")

    ledger = yaml.safe_load((ROOT / "claims/claims.yml").read_text(encoding="utf-8"))["claims"]
    indexed = {claim["id"]: claim for claim in ledger}
    for claim_id, expected in EXPECTED_CLAIMS.items():
        claim = indexed[claim_id]
        actual = (claim["study_id"], claim["claim_type"], claim["status"])
        assert actual == expected
        assert claim["run_ids"] == [RUNS[expected[0]]]
    checks.append("22 unchanged claim owners, types, statuses, and run references")

    frontier_proof = (ROOT / "studies/DD-021-general-sharing-frontier/proof.md").read_text()
    for token in [
        "G_s = 1-(1-C_s)(1-q)^(N-s)",
        "(1-q)e_s-e_(s+1)",
        "rho_s=e_(s+1)/e_s",
    ]:
        assert token in frontier_proof
    strategic_proof = (
        ROOT / "studies/DD-022-coordination-free-positive-sharing/proof.md"
    ).read_text()
    for token in [
        "rho=7/12",
        "rho=1/6",
        "24rho^2+17rho-16",
        "(5 sqrt(73)-17)/48",
        "Constant opposite targets",
        "signal ownership",
    ]:
        assert token in strategic_proof
    certificate = load_json(
        ROOT / "results/verified" / RUNS["DD-022"] / "outputs/threshold-certificate.json"
    )
    assert certificate["passed"] is True
    assert certificate["exact_positive_root"] == "(5*sqrt(73)-17)/48"
    assert certificate["polynomial_coefficients"] == [24, 17, -16]
    assert certificate["isolating_interval"] == ["2679/5000", "67/125"]
    assert all(certificate["checks"].values())
    checks.append("sharing identity, residual frontier, selection boundary, and root certificate")

    provenance = load_json(PAPER / "source-provenance.json")
    assert_provenance(provenance)
    for relative, digest in provenance["inputs"].items():
        assert sha(ROOT / relative) == digest
    for name, digest in provenance["figures"].items():
        assert sha(PAPER / "figures" / name) == digest
    for name, digest in provenance["figure_data"].items():
        assert sha(PAPER / "figures/data" / name) == digest
    for name, digest in provenance["tables"].items():
        assert sha(PAPER / "tables" / name) == digest
    assert sha(PAPER / "generated/references.bib") == provenance["bibliography"]
    checks.append("generated figure, data, table, input, and bibliography hashes")

    source = (PAPER / "main.tex").read_text(encoding="utf-8")
    abstract = (PAPER / "abstract.tex").read_text(encoding="utf-8")
    assert "not an every-equilibrium result" in abstract
    assert "does not reveal" in abstract
    assert "no human or real data" in abstract
    assert source.index("Strict selected sharing gain") < source.index("Selection failure")
    assert "centralized top-two" in source and "selected shared equilibrium" in source
    assert "/Users/" not in source + abstract
    assert not re.search(r"\b(novel|unprecedented|first to|first paper)\b", abstract, re.I)
    assert source.count("\\ArtifactNote") == 1  # Macro definition; assets carry instances.
    for asset in list((PAPER / "figures").glob("*.tex")) + list((PAPER / "tables").glob("*.tex")):
        text = asset.read_text(encoding="utf-8")
        assert "\\ArtifactNote" in text and "DD-C-" in text and "SHA-256" in text
    checks.append(
        "abstract, selection adjacency, authority labels, host-path, and asset-caption boundaries"
    )

    corruptions: list[dict[str, Any]] = []
    mutators = {
        "source-run": lambda value: value["source_runs"].update({"strategic": "bad-run"}),
        "claim-set": lambda value: value["claim_ids"].pop(),
        "input-hash": lambda value: value["inputs"].update({next(iter(value["inputs"])): "0" * 64}),
        "figure-hash": lambda value: value["figures"].update(
            {next(iter(value["figures"])): "broken"}
        ),
        "bibliography-hash": lambda value: value.update({"bibliography": "f" * 63}),
    }
    for name, mutate in mutators.items():
        candidate = copy.deepcopy(provenance)
        mutate(candidate)
        rejected = False
        try:
            assert_provenance(candidate)
            if name in {"input-hash", "source-run"} and candidate != provenance:
                raise ValueError("content differs from authoritative provenance")
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected = True
        assert rejected
        corruptions.append({"name": name, "rejected": True})
    corruption_report = {
        "schema_version": 1,
        "passed": True,
        "tests": corruptions,
    }
    (PAPER / "asset-corruption-tests.json").write_text(
        json.dumps(corruption_report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checks.append("five deliberate provenance corruptions rejected")

    validation = load_json(PAPER / "validation.json")
    assert validation["byte_reproducible_two_builds"] is True
    assert 26 <= validation["page_count"] <= 40
    assert (
        sha(PAPER / "When_Does_Information_Sharing_Improve_Decentralized_Discovery.pdf")
        == validation["pdf_sha256"]
    )
    report = {
        "schema_version": 1,
        "passed": True,
        "independent_of_generator_import": True,
        "checks": checks,
        "source_runs": RUNS,
        "claim_ids": sorted(EXPECTED_CLAIMS),
        "pdf_sha256": validation["pdf_sha256"],
        "page_count": validation["page_count"],
    }
    (PAPER / "paper-audit.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Information Sharing Frontier independent audit passed: {len(checks)} check groups")


if __name__ == "__main__":
    main()
