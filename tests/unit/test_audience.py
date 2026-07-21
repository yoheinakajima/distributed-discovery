from __future__ import annotations

from fractions import Fraction

import pytest

from distributed_discovery.attention.model import discovery
from distributed_discovery.audience.model import (
    binding_metrics,
    binding_optima,
    institution_registry,
    mechanism_results,
    voluntary_equilibria,
)
from distributed_discovery.audience.study import build_bundle
from distributed_discovery.audience.verification import (
    corruption_tests,
    direct_profile,
    verify_bundle,
)


@pytest.mark.parametrize("n", range(2, 9))
def test_binding_audience_theorem_and_garbling_dominance(n: int) -> None:
    p = Fraction(1, 2)
    high, low = Fraction(3, 4), Fraction(1, 3)
    assert binding_optima(n, p, high) == [1]
    assert binding_optima(n, p, low) == [0]
    assert binding_optima(n, p, p) == [0, 1]
    optimum = discovery(n, 1, p, high)
    for garbled in (Fraction(1, 3), Fraction(1, 2), high):
        for audience in range(1, n + 1):
            assert discovery(n, audience, p, garbled) <= optimum


def test_closed_metrics_match_labeled_enumerator() -> None:
    n, p, q = 4, Fraction(1, 2), Fraction(3, 4)
    for readers in range(n + 1):
        closed = binding_metrics(n, readers, p, q)
        direct = direct_profile(n, readers, p, q)
        for key in ("discovery", "action_quality", "expected_distinct_actions"):
            assert closed[key] == direct[key]


def test_voluntary_audience_truncates_available_deviations() -> None:
    n, p, q = 8, Fraction(1, 3), Fraction(5, 6)
    assert voluntary_equilibria(n, 1, p, q)["weak"] == [1]
    full = voluntary_equilibria(n, n, p, q)["weak"]
    assert min(full) >= 1
    assert binding_optima(n, p, q) == [1]


def test_universal_pooling_implements_count_optimum() -> None:
    for n in range(2, 9):
        for p in (Fraction(1, 3), Fraction(1, 2), Fraction(3, 4)):
            for q in (Fraction(1, 3), Fraction(1, 2), Fraction(3, 4)):
                result = mechanism_results(n, p, q)["public_universal_pooling"]
                assert result["weak"] == binding_optima(n, p, q)
                assert result["ex_post_budget_balance"] is True
                assert result["expected_external_subsidy"] == "0"


def test_information_firewalls_are_explicit() -> None:
    registry = institution_registry()
    assert len(registry) == 8
    assert len({row["institution_id"] for row in registry}) == 8
    assert all("commitment" in row and "external_subsidy" in row for row in registry)


def test_small_bundle_verifies_and_rejects_four_corruptions() -> None:
    bundle = build_bundle({"agents": [2, 3], "accuracies": ["1/2", "3/4"]})
    assert bundle["summary"]["grid_cells"] == 8
    assert bundle["summary"]["binding_audience_rows"] == 28
    assert bundle["summary"]["voluntary_profile_rows"] == 64
    assert bundle["summary"]["garbling_rows"] == 30
    verification = verify_bundle(bundle)
    assert verification["passed"] is True
    assert verification["unique_profiles_verified"] == 28
    assert all(corruption_tests(bundle).values())
