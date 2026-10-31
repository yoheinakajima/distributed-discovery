"""Small non-evidence fixtures only; never execute the frozen 80-cell grid."""

from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from distributed_discovery.behavioral_diversity import feedback

CONFIG = (
    Path(__file__).resolve().parents[2]
    / "studies/DD-024-behavioral-diversity-discovery/tracks/track-03/config.json"
)


def small_config(p: str, r: str, laws: list[str]) -> dict[str, Any]:
    config: dict[str, Any] = json.loads(CONFIG.read_text())
    config.update(p_values=[p], r_values=[r], failure_laws=laws, expected_cells=len(laws))
    return config


def test_perfect_clues_hand_values_and_schedule_control() -> None:
    # Both first actions inspect the known true target. Four iid tries succeed
    # with 1-(1-r)^4; agent-persistent trials with 1-(1-r)^2; global with r.
    config = small_config("1/1", "1/2", list(feedback.LAWS))
    result = feedback.run(config)
    expected = {
        "iid": "15/16",
        "searcher_persistent": "3/4",
        "round_common": "3/4",
        "global_common": "1/2",
    }
    for row in result["rows"]:
        assert row["policy_values"]["calibrated_joint"] == expected[row["failure_law"]]
        assert row["estimands"]["schedule_equivalence_control"] == "0/1"
        assert all(value is None for value in row["disagreement_policy_values"].values())
    assert feedback.verify(config, result)["passed"]


def test_cross_searcher_rescue_matches_explicit_persistent_hand_case() -> None:
    config = small_config("2/3", "1/2", ["searcher_persistent"])
    result = feedback.run(config)
    row = result["rows"][0]
    # For X=(0,1), target 0 has joint weight (1/3)*(2/3)*(1/6)=1/27.
    # Rescue requires its first searcher dead and the other alive: probability 1/4.
    # Target 1 contributes the same amount, hence cross-rescue mass 1/54.
    audit = next(item for item in row["continuation_audit"] if item["clues"] == [0, 1])
    assert Fraction(audit["candidate_rescue_masses"]["1,0"]) == Fraction(1, 54)
    assert audit["candidate_rescue_masses"]["0,1"] == "0/1"
    checked = feedback.verify(config, result)
    assert checked["passed"]
    assert all(checked["corruptions"].values())


def test_perfect_detection_dependence_and_elimination_boundary() -> None:
    config = small_config("1/2", "1/1", list(feedback.LAWS))
    result = feedback.run(config)
    values = [row["policy_values"] for row in result["rows"]]
    assert all(value == values[0] for value in values)
    assert all(row["estimands"]["failure_elimination_regret"] == "0/1" for row in result["rows"])
    assert feedback.verify(config, result)["passed"]


def test_verifier_rejects_modified_candidate_and_summary() -> None:
    config = small_config("1/3", "1/4", ["iid"])
    result = feedback.run(config)
    damaged = copy.deepcopy(result)
    damaged["rows"][0]["continuation_audit"][0]["candidate_rescue_masses"]["0,0"] = "1/1"
    assert not feedback.verify(config, damaged)["passed"]
    damaged = copy.deepcopy(result)
    damaged["summary"]["cells"] = 99
    assert not feedback.verify(config, damaged)["passed"]


def test_action_budget_cannot_change_silently() -> None:
    config = small_config("1/3", "1/4", ["iid"])
    config["budget"]["attempts_per_trial"] = 3
    with pytest.raises(ValueError, match="budget"):
        feedback.run(config)
