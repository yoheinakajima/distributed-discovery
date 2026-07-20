from fractions import Fraction

from distributed_discovery.private_teams.model import direct_profile, evaluate_formula
from distributed_discovery.private_teams.optimize import (
    coordinate_ascent,
    direct_is_coordinate_fixed,
    exhaustive_optimum,
    random_profile,
    reduced_profile_count,
)


def test_agent_symmetry_reduces_binary_profile_count() -> None:
    assert reduced_profile_count(2, 2) == 10
    result = exhaustive_optimum(2, 2, Fraction(1, 2))
    assert result.reduced_profile_count == 10
    assert result.value == 1


def test_informative_hybrid_counterexample_is_exact() -> None:
    result = exhaustive_optimum(3, 2, Fraction(2, 5))
    assert result.reduced_profile_count == 378
    assert result.value == Fraction(7, 10)
    assert result.value - Fraction(16, 25) == Fraction(3, 50)


def test_coordinate_ascent_never_lowers_value() -> None:
    initial = random_profile(3, 2, seed=17)
    before = evaluate_formula(initial, 3, Fraction(2, 3))
    after = coordinate_ascent(initial, 3, Fraction(2, 3), max_sweeps=20)
    assert after.value >= before


def test_direct_profile_is_canonical_coordinate_fixed_point() -> None:
    assert direct_is_coordinate_fixed(16, 8, Fraction(1, 5))
    profile = direct_profile(16, 8)
    result = coordinate_ascent(profile, 16, Fraction(1, 5), max_sweeps=5)
    assert result.termination == "coordinate-fixed-point"
