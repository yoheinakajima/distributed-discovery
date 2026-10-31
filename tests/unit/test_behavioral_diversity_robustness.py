from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, NoReturn

import pytest

from distributed_discovery.behavioral_diversity import robustness

CONFIG = (
    Path(__file__).resolve().parents[2]
    / "studies/DD-024-behavioral-diversity-discovery/tracks/track-02/config.json"
)


def _single_cell(identifier: str) -> dict[str, Any]:
    config: dict[str, Any] = json.loads(CONFIG.read_text())
    config["cells"] = [cell for cell in config["cells"] if cell["id"] == identifier]
    assert len(config["cells"]) == 1
    return config


@pytest.fixture(scope="module")
def hand_case() -> tuple[dict[str, Any], dict[str, Any]]:
    config = _single_cell("rho1-none-tau2")
    return config, robustness.run(config)


def test_hand_case_has_attaining_mixture_and_valid_all_policy_certificate(
    hand_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    config, result = hand_case
    row = result["rows"][0]
    # A common private source gives PP accuracies (1/3,5/6); SS reverses them.
    # Their equal mixture attains 7/12; the equal regime-prior dual bounds
    # all 36 six-role pairs by that value. No Monte Carlo estimate is involved.
    assert row["deterministic_maximin"]["worst_case"] == "1/3"
    assert row["coordinated_mixture"]["worst_case"] == "7/12"
    assert row["contrasts"]["mixture_minus_deterministic"] == "1/4"
    assert row["coordinated_mixture"]["certificate"]["regime_a_weight"] == "1/2"
    assert [entry["expected_success"] for entry in row["known_prior"]] == ["17/24", "7/12", "17/24"]
    audit = robustness.verify(config, result)
    assert audit["passed"], audit["errors"]
    assert audit["corruptions"] == {
        "mixture_weight": True,
        "source_branch_probability": True,
        "diagnostic_probability": True,
        "dual_upper_bound": True,
    }
    assert audit["checks"]["plan_vectors_checked"] == 36
    json.dumps(result, allow_nan=False)
    json.dumps(audit, allow_nan=False)


def test_perfect_diagnosis_removes_ambiguity_gap_with_same_two_actions() -> None:
    config = _single_cell("rho1-perfect-tau2")
    result = robustness.run(config)
    row = result["rows"][0]
    assert len(row["plans"]) == 1296
    assert row["deterministic_maximin"]["by_regime"] == {"A": "5/6", "B": "5/6"}
    assert row["contrasts"]["mixture_minus_deterministic"] == "0/1"
    audit = robustness.verify(config, result)
    assert audit["passed"], audit["errors"]


def test_noisy_diagnosis_and_both_private_source_branches_are_reconstructed() -> None:
    config = _single_cell("rhohalf-noisy-tau1")
    result = robustness.run(config)
    row = result["rows"][0]
    assert row["diagnostic_probabilities"] == {
        "A": {"A": "3/4", "B": "1/4"},
        "B": {"A": "1/4", "B": "3/4"},
    }
    assert row["profile_payoffs"][0]["by_regime"] == {"A": "4/9", "B": "65/72"}
    assert row["independent_departures"]["homogeneous"]["candidate_count"] == 25
    assert row["independent_departures"]["heterogeneous"]["candidate_count"] == 625
    audit = robustness.verify(config, result)
    assert audit["passed"], audit["errors"]


def test_verifier_rejects_changed_plan_outcome_and_missing_policy(
    hand_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    config, result = hand_case
    changed = copy.deepcopy(result)
    changed["rows"][0]["plans"][0]["by_regime"]["A"] = "1/1"
    audit = robustness.verify(config, changed)
    assert not audit["passed"]
    assert any("direct state enumeration" in error for error in audit["errors"])
    missing = copy.deepcopy(result)
    missing["rows"][0]["plans"].pop()
    assert not robustness.verify(config, missing)["passed"]


def test_verifier_does_not_call_primary_scientific_helpers(
    hand_case: tuple[dict[str, Any], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, result = hand_case

    def forbidden(*args: object, **kwargs: object) -> NoReturn:
        raise AssertionError("independent verifier called a primary scientific helper")

    for name in (
        "_primary_profile_values",
        "_primary_diagnostic",
        "_primary_plans",
        "_solve_mixture",
        "_primary_departures",
        "_summary",
    ):
        monkeypatch.setattr(robustness, name, forbidden)
    audit = robustness.verify(config, result)
    assert audit["passed"], audit["errors"]


def test_constant_policy_thresholds_and_invalid_configuration(
    hand_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    config, result = hand_case
    row = result["rows"][0]
    assert row["profile_payoffs"][21]["by_regime"] == {"A": "1/3", "B": "1/3"}
    assert row["profile_payoffs"][22]["by_regime"] == {"A": "0/1", "B": "0/1"}
    assert sum(Fraction(item["weight"]) for item in row["coordinated_mixture"]["support"]) == 1
    invalid = copy.deepcopy(config)
    invalid["model"]["agents"] = 3
    with pytest.raises(ValueError, match="finite policy class"):
        robustness.run(invalid)
