from fractions import Fraction

import pytest

from distributed_discovery.acquisition.common_source_analysis import (
    all_common_trap_interval,
    equilibrium_counts,
    fixed_k_large_n_limit,
    monotonicity_kernel,
    overacquisition_counterexample,
    planner_counts,
    planner_threshold,
    private_threshold,
)
from distributed_discovery.acquisition.common_source_verification import (
    direct_planner_threshold,
    direct_private_threshold,
    verify_threshold_rows,
)
from distributed_discovery.acquisition.n_agent import equilibrium, planner


def test_thresholds_match_independent_direct_enumeration() -> None:
    for n in range(2, 6):
        for p in (Fraction(1, 2), Fraction(2, 3), Fraction(3, 4)):
            for k in range(n):
                assert private_threshold(n, k, p) == direct_private_threshold(n, k, p)
                assert planner_threshold(n, k, p) == direct_planner_threshold(n, k, p)


def test_threshold_counts_match_legacy_finite_classifiers() -> None:
    costs = (Fraction(), Fraction(1, 24), Fraction(1, 8), Fraction(1, 4))
    for n in range(2, 9):
        for p in (Fraction(1, 2), Fraction(2, 3), Fraction(3, 4)):
            for cost in costs:
                expected_equilibria = [k for k in range(n + 1) if equilibrium(n, k, p, cost)[0]]
                assert equilibrium_counts(n, p, cost) == expected_equilibria
                assert planner_counts(n, p, cost) == planner(n, p, cost)


def test_private_thresholds_are_strictly_decreasing() -> None:
    for n in range(2, 20):
        for p in (Fraction(1, 5), Fraction(1, 2), Fraction(4, 5)):
            thresholds = [private_threshold(n, k, p) for k in range(n)]
            assert all(
                left > right for left, right in zip(thresholds, thresholds[1:], strict=False)
            )
            assert thresholds[-1] == 0
            for m in range(2, n + 1):
                for x in range(n - m + 1):
                    direct, numerator, denominator = monotonicity_kernel(x, m, p)
                    assert numerator > 0
                    assert direct == numerator / denominator


def test_general_all_common_trap_and_large_n_limit() -> None:
    for n in range(2, 20):
        p = Fraction(2, 3)
        lower, upper = all_common_trap_interval(n, p)
        assert lower == p * (1 - p) * Fraction(n - 1, n)
        assert upper == p * (1 - p)
        assert upper - lower == p * (1 - p) / n
    p = Fraction(3, 5)
    for k in range(5):
        limit = fixed_k_large_n_limit(k, p)
        assert private_threshold(10_000, k, p) < limit
        assert limit - private_threshold(10_000, k, p) < Fraction(1, 1000)


def test_exact_interior_overacquisition_counterexample() -> None:
    result = overacquisition_counterexample()
    assert result == {
        "agents": 3,
        "accuracy": "4/5",
        "cost": "13/375",
        "private_threshold_k1": "14/375",
        "planner_threshold_k1": "4/125",
        "equilibrium_k": [2],
        "planner_k": [1],
    }


def test_corrupted_threshold_is_rejected() -> None:
    row: dict[str, object] = {
        "agents": 3,
        "k": 1,
        "accuracy": "4/5",
        "private_threshold": "14/375",
        "planner_threshold": "4/125",
    }
    assert verify_threshold_rows([row]) == 1
    row["private_threshold"] = "15/375"
    with pytest.raises(ValueError, match="private threshold mismatch"):
        verify_threshold_rows([row])
