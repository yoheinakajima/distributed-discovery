from fractions import Fraction

import pytest

from distributed_discovery.threshold_discovery.model import (
    exhaustive_planner_value,
    labeled_canonical_evaluation,
    occupancy_statistics,
    planner_value,
    split_prize_closed_form,
    strategic_candidate_payoff,
    threshold_two_closed_form,
)
from distributed_discovery.threshold_discovery.verification import (
    corruption_tests,
    histogram_canonical_evaluation,
    planner_audit,
    strategic_payoff_audit,
    verify_bundle,
)


@pytest.fixture(scope="module")
def canonical_bundle() -> dict[str, object]:
    thresholds = list(range(1, 9))
    method_a = labeled_canonical_evaluation(16, 8, Fraction(1, 5), thresholds)
    method_b = histogram_canonical_evaluation(16, 8, Fraction(1, 5), thresholds)
    bundle = {
        "config": {"agents": 8, "labeled_count_vectors": 490314},
        "method_a": method_a,
        "method_b": method_b,
        "planner_audit": planner_audit(),
        "strategic_payoff_audit": strategic_payoff_audit(),
    }
    return bundle


def test_planner_formula_matches_exhaustive_allocations() -> None:
    posterior = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    for agents in range(1, 7):
        for threshold in range(1, agents + 1):
            assert planner_value(posterior, agents, threshold) == exhaustive_planner_value(
                posterior, agents, threshold
            )


def test_strategic_closed_forms_and_zero_limits() -> None:
    for agents in range(2, 9):
        for probability in (Fraction(0), Fraction(1, 8), Fraction(1, 2), Fraction(1)):
            assert strategic_candidate_payoff(
                Fraction(1), agents, 1, probability
            ) == split_prize_closed_form(agents, probability)
            assert strategic_candidate_payoff(
                Fraction(1), agents, 2, probability
            ) == threshold_two_closed_form(agents, probability)
    assert split_prize_closed_form(8, Fraction(0)) == 1
    assert threshold_two_closed_form(8, Fraction(0)) == 0


def test_single_mode_occupancy_accounting() -> None:
    statistics = occupancy_statistics(1, 8, 2)
    assert statistics["expected_distinct_candidates"] == 1
    assert statistics["expected_viable_candidates"] == 1
    assert statistics["failed_subthreshold_attempts"] == 0
    assert statistics["necessary_overlap"] == 1
    assert statistics["excess_overlap"] == 6
    assert statistics["expected_largest_crowd"] == 8
    assert statistics["pair_collision"] == 1


def test_canonical_methods_and_regression_targets(
    canonical_bundle: dict[str, object],
) -> None:
    method_a = canonical_bundle["method_a"]
    method_b = canonical_bundle["method_b"]
    assert isinstance(method_a, dict) and isinstance(method_b, dict)
    assert method_a["state_count"] == 490314
    assert method_b["state_count"] == 67
    assert method_a["probability_mass"] == method_b["probability_mass"] == 1
    assert method_a["rows"] == method_b["rows"]
    row = method_a["rows"][1]
    expected = {
        "common_deterministic_mode_discovery": 0.383468709731,
        "tied_mode_mixed_discovery": 0.478039904380,
        "private_clue_following": 0.49668352,
        "planner_discovery": 0.670580744448,
        "expected_distinct_candidates": 1.717068008,
        "expected_viable_candidates": 1.419780805,
        "expected_largest_crowd": 6.559306873,
        "pair_collision": 0.757029321,
        "target_selected_at_least_one": 0.513796192,
        "target_selected_exactly_one": 0.035756287,
    }
    for key, value in expected.items():
        assert float(row[key]) == pytest.approx(value, abs=5e-10)


def test_verifier_rejects_all_registered_corruptions(
    canonical_bundle: dict[str, object],
) -> None:
    assert verify_bundle(canonical_bundle)["passed"]
    assert all(corruption_tests(canonical_bundle).values())
