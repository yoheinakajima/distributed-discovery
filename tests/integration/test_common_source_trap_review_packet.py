from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PACKET_PATH = ROOT / "reports/editorial/common-source-trap-review-packet.yml"


def _packet() -> dict[str, Any]:
    loaded = yaml.safe_load(PACKET_PATH.read_text(encoding="utf-8"))
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
    assert packet_claims == manuscript_claims == {
        "DD-C-0051",
        "DD-C-0052",
        "DD-C-0053",
        "DD-C-0054",
        "DD-C-0056",
        "DD-C-0057",
        "DD-C-0058",
    }

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
    validation = yaml.safe_load(
        _git_bytes(commit, "papers/common-source-trap/validation.json")
    )
    provenance = yaml.safe_load(
        _git_bytes(commit, "papers/common-source-trap/generated/provenance.json")
    )
    assert validation["pdf_sha256"] == packet["source"]["pdf"]["sha256"]
    assert validation["page_count"] == packet["source"]["pdf"]["page_count"]
    assert validation["source_runs"] == packet["evidence"]["source_runs"]
    assert provenance["source_runs"] == packet["evidence"]["source_runs"]
    packet_inputs = {
        record["path"]: record["sha256"] for record in packet["evidence"]["inputs"]
    }
    assert validation["inputs"] == packet_inputs
    assert provenance["inputs"] == packet_inputs
    assert validation["byte_reproducible_two_builds"] is True
    assert validation["unresolved_references_citations_or_overfull_boxes"] is False


def test_review_round_is_complete_bundle_only_and_zero_authority_expansion() -> None:
    packet = _packet()
    assert packet["paper"] == {
        "id": "common-source-trap",
        "title": (
            "The Common-Source Trap: Endogenous Independent Evidence in "
            "Distributed Discovery"
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
    text = PACKET_PATH.read_text(encoding="utf-8") + (
        ROOT / "reports/editorial/common-source-trap-review-guide.md"
    ).read_text(encoding="utf-8")
    assert "/Users/" not in text
    assert ".env.txt" not in text
    assert "api_key" not in text.lower()
    assert "authorization:" not in text.lower()
    assert "papers/information-sharing-frontier" not in text
