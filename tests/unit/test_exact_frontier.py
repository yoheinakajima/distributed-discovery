from copy import deepcopy
from fractions import Fraction

from distributed_discovery.canonical.exact_frontier import (
    expected_labeled_count_vectors,
    histogram_orbit_frontier,
    labeled_count_frontier,
)
from distributed_discovery.canonical.exact_frontier_verification import verify_certificate
from distributed_discovery.private_teams.model import pooled_planner_value


def _certificate() -> dict[str, object]:
    labeled = labeled_count_frontier(3, 2, Fraction(1, 2))
    histogram = histogram_orbit_frontier(3, 2, Fraction(1, 2))
    rows = [
        {
            "budget": budget,
            "numerator": value.numerator,
            "denominator": value.denominator,
            "method_a_fraction": str(value),
            "method_b_fraction": str(histogram.values[budget - 1]),
        }
        for budget, value in enumerate(labeled.values, start=1)
    ]
    lower = Fraction(1, 2)
    return {
        "parameters": {"candidates": 3, "reports": 2, "accuracy": "1/2"},
        "method_a": {"probability_mass_fraction": "1"},
        "method_b": {
            "probability_mass_fraction": "1",
            "histogram_orbit_count": histogram.state_count,
        },
        "frontier": rows,
        "private_team_interval": {
            "lower_fraction": str(lower),
            "upper_fraction": str(labeled.values[-1]),
            "gap_fraction": str(labeled.values[-1] - lower),
            "upper_attainability_claimed": False,
            "global_tightness_claimed": False,
        },
    }


def test_two_exact_representations_match_direct_tiny_enumeration() -> None:
    labeled = labeled_count_frontier(3, 2, Fraction(1, 2))
    histogram = histogram_orbit_frontier(3, 2, Fraction(1, 2))
    assert labeled.probability_mass == histogram.probability_mass == 1
    assert labeled.state_count == expected_labeled_count_vectors(3, 2) == 6
    assert labeled.values == histogram.values
    assert labeled.values[-1] == pooled_planner_value(3, 2, Fraction(1, 2))


def test_canonical_frontier_has_exact_requested_endpoint() -> None:
    labeled = labeled_count_frontier(16, 8, Fraction(1, 5))
    histogram = histogram_orbit_frontier(16, 8, Fraction(1, 5))
    assert labeled.probability_mass == histogram.probability_mass == 1
    assert labeled.state_count == 490_314
    assert histogram.state_count == 67
    assert labeled.values == histogram.values
    assert labeled.values[-1] == Fraction(860391662035297, 1001129150390625)


def test_independent_verifier_detects_corrupted_frontier() -> None:
    certificate = _certificate()
    assert verify_certificate(certificate) == []
    corrupted = deepcopy(certificate)
    frontier = corrupted["frontier"]
    assert isinstance(frontier, list)
    frontier[-1]["numerator"] += 1
    assert "budget 2 exact value mismatch" in verify_certificate(corrupted)
