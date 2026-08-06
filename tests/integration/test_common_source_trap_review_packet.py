from __future__ import annotations

import hashlib
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / "reports/editorial/common-source-trap-review-packet.yml"
DISPOSITION_PATH = ROOT / "reports/editorial/common-source-trap-review-disposition.yml"


def _packet() -> dict[str, Any]:
    loaded = yaml.safe_load(PACKET_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _disposition() -> dict[str, Any]:
    loaded = yaml.safe_load(DISPOSITION_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _assert_frozen_file(commit: str, record: dict[str, Any]) -> None:
    path = record["path"]
    expected = record["sha256"]
    assert isinstance(path, str)
    assert isinstance(expected, str)
    assert _sha256(_git_bytes(commit, path)) == expected


def test_review_packet_freezes_exact_source_pdf_receipts_and_inputs() -> None:
    packet = _packet()
    source = packet["source"]
    assert isinstance(source, dict)
    commit = source["commit"]
    assert commit == "7268e445347c4d7f9106d129af42d0e8667eb115"
    tree = subprocess.check_output(
        ["git", "rev-parse", f"{commit}:papers/common-source-trap"],
        cwd=ROOT,
        text=True,
    ).strip()
    assert tree == source["paper_tree_oid"] == "2c34089accf3e9bbd2d6d038aceb2156bc0aa2a4"

    _assert_frozen_file(commit, source["manuscript"])
    _assert_frozen_file(commit, source["pdf"])
    for record in source["supporting_files"]:
        _assert_frozen_file(commit, record)
    for record in packet["receipts"]:
        _assert_frozen_file(commit, record)
    for record in packet["evidence"]["inputs"]:
        _assert_frozen_file(commit, record)
    _assert_frozen_file(commit, packet["build"]["generator"])
    _assert_frozen_file(commit, packet["build"]["wrapper"])
    _assert_frozen_file(commit, packet["build"]["dependency_lock"])


def test_review_packet_claims_match_manuscript_and_canonical_ledger() -> None:
    packet = _packet()
    commit = packet["source"]["commit"]
    manuscript = _git_bytes(commit, "papers/common-source-trap/main.tex").decode()
    manuscript_claims = set(re.findall(r"DD-C-\d{4}", manuscript))
    packet_claims = {record["id"] for record in packet["evidence"]["claims"]}
    assert (
        packet_claims
        == manuscript_claims
        == {
            "DD-C-0051",
            "DD-C-0052",
            "DD-C-0053",
            "DD-C-0054",
            "DD-C-0056",
            "DD-C-0057",
            "DD-C-0058",
        }
    )

    ledger = yaml.safe_load(_git_bytes(commit, "claims/claims.yml"))["claims"]
    canonical = {record["id"]: record for record in ledger}
    for record in packet["evidence"]["claims"]:
        claim = canonical[record["id"]]
        assert record["study_id"] == claim["study_id"]
        assert record["status"] == claim["status"]
        assert record["run_id"] in claim["run_ids"]


def test_review_packet_matches_validation_and_provenance_receipts() -> None:
    packet = _packet()
    commit = packet["source"]["commit"]
    validation = yaml.safe_load(_git_bytes(commit, "papers/common-source-trap/validation.json"))
    provenance = yaml.safe_load(
        _git_bytes(commit, "papers/common-source-trap/generated/provenance.json")
    )
    assert validation["pdf_sha256"] == packet["source"]["pdf"]["sha256"]
    assert validation["page_count"] == packet["source"]["pdf"]["page_count"]
    assert validation["source_runs"] == packet["evidence"]["source_runs"]
    assert provenance["source_runs"] == packet["evidence"]["source_runs"]
    packet_inputs = {record["path"]: record["sha256"] for record in packet["evidence"]["inputs"]}
    assert validation["inputs"] == packet_inputs
    assert provenance["inputs"] == packet_inputs
    assert validation["byte_reproducible_two_builds"] is True
    assert validation["unresolved_references_citations_or_overfull_boxes"] is False


def test_review_round_is_complete_bundle_only_and_zero_authority_expansion() -> None:
    packet = _packet()
    assert packet["paper"] == {
        "id": "common-source-trap",
        "title": (
            "The Common-Source Trap: Endogenous Independent Evidence in Distributed Discovery"
        ),
        "lifecycle": "working-paper",
        "submission_authorized": False,
        "peer_reviewed": False,
    }
    review = packet["review_round"]
    assert review["required_reviewers"] == ["chatgpt", "claude", "gemini", "grok"]
    assert review["independent"] is True
    assert review["reviewer_must_not_receive_other_reviews"] is True
    assert review["atlas_must_return_complete_bundle_simultaneously"] is True
    assert review["provider_api_or_spend_authorized"] is False
    assert packet["bundle_gate"]["required_reviews"] == 4
    assert packet["bundle_gate"]["partial_bundle_accepted"] is False
    assert packet["bundle_gate"]["manuscript_edit_authorized_before_complete_bundle"] is False
    assert packet["authority"]["atlas_scientific_authority"] is False
    assert "information-sharing-frontier-work" in packet["prohibitions"]
    assert "pull-request-readiness-or-merge" in packet["prohibitions"]


def test_review_packet_and_guide_are_public_safe() -> None:
    text = (
        PACKET_PATH.read_text(encoding="utf-8")
        + (ROOT / "reports/editorial/common-source-trap-review-guide.md").read_text(
            encoding="utf-8"
        )
        + DISPOSITION_PATH.read_text(encoding="utf-8")
    )
    assert "/Users/" not in text
    assert ".env.txt" not in text
    assert "api_key" not in text.lower()
    assert "authorization:" not in text.lower()
    assert "papers/information-sharing-frontier" not in text


def test_complete_round_one_bundle_and_dispositions_preserve_boundaries() -> None:
    record = _disposition()
    assert record["bundle"]["received_complete_simultaneously"] is True
    assert record["bundle"]["partial_bundle_used"] is False
    assert [item["reviewer"] for item in record["bundle"]["reviewers"]] == [
        "chatgpt",
        "claude",
        "gemini",
        "grok",
    ]
    assert all(len(item["input_sha256"]) == 64 for item in record["bundle"]["reviewers"])
    assert record["synthesis"]["critical_objections"] == 0
    assert record["synthesis"]["ready_or_minor_vote"] == "4-of-4"
    assert [item["finding_id"] for item in record["dispositions"]] == [
        f"CST-R1-M{number:02d}" for number in range(1, 12)
    ]
    assert record["authority"]["new_scientific_claim_authorized"] is False
    assert record["authority"]["manuscript_merge_authorized"] is False
    revision = record["revision_candidate"]
    artifact_commit = revision["reviewed_artifact_commit"]
    assert artifact_commit == "4fa15aa7f77dcae9f02a42c64273a04969247571"
    for kind in ["manuscript", "pdf"]:
        path = revision[f"{kind}_path"]
        assert _sha256(_git_bytes(artifact_commit, path)) == revision[f"{kind}_sha256"]
    assert revision["page_count"] == 21
    assert revision["byte_reproducible_two_builds"] is True
    assert revision["all_pages_visually_inspected"] is True
    assert record["round2_packet"]["fresh_isolated_sessions"] is True
    assert record["round2_packet"]["round1_sessions_reusable"] is False
    assert record["round2_packet"]["status"] == "frozen-not-dispatched"
    assert record["round2_packet"]["reviewed_artifact_commit"] == artifact_commit
    assert record["round2_packet"]["complete_bundle_required"] is True
    assert record["round2_packet"]["dispatch_authorized"] is False


def test_reviewer_interior_condition_is_derived_but_not_promoted() -> None:
    def sign(value: Fraction) -> int:
        return (value > 0) - (value < 0)

    for n in range(3, 33):
        for denominator in range(2, 34):
            for numerator in range(1, denominator):
                p = Fraction(numerator, denominator)
                q = 1 - p
                a1 = p * q * (n - 2) * (q / (n - 1) + p / (2 * n))
                b1 = p * q * q
                proposed_boundary = p * (n * n - n + 2) - 2 * n
                assert sign(a1 - b1) == sign(proposed_boundary)

    record = _disposition()
    finding = next(item for item in record["dispositions"] if item["finding_id"] == "CST-R1-M05")
    assert finding["disposition"] == "defer-needs-evidence"
    source = (ROOT / "papers/common-source-trap/main.tex").read_text(encoding="utf-8")
    assert "N^2-N+2" not in source


def test_round_one_edits_are_evidence_bounded() -> None:
    source = (ROOT / "papers/common-source-trap/main.tex").read_text(encoding="utf-8")
    for phrase in [
        "net social value",
        "all-finite-$N$ threshold characterization",
        "the exact connection",
        "infimum required subsidy",
        "total information cost $1/4$ across both channels",
        "candidate synthetic preregistration package",
        "precise all-common boundary in the frozen model",
    ]:
        assert phrase in source
    for rejected_phrase in [
        "raises net discovery",
        "The smallest strict subsidy is any",
        "Assignment is mechanically stronger",
        "The Atlas also prevents favorable cherry-picking",
        "The Common-Source Trap has a precise general boundary",
    ]:
        assert rejected_phrase not in source
