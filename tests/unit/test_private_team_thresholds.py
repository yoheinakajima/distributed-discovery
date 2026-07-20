from fractions import Fraction

import pytest

from distributed_discovery.private_teams.model import evaluate_direct, evaluate_formula
from distributed_discovery.private_teams.optimize import exhaustive_optimum
from distributed_discovery.private_teams.signatures import signature_from_policy
from distributed_discovery.private_teams.thresholds import (
    certify_informative_envelope,
    direct_two_value,
    distinct_territorial_value,
    evaluate_quadratic,
    exact_signature_optimum_fast,
    minimum_on_interval,
    one_reroute_hybrid_profile,
    one_reroute_hybrid_value,
    restricted_winners,
    signature_profile_polynomial,
)


@pytest.mark.parametrize("candidates", [3, 4, 5])
@pytest.mark.parametrize("accuracy", [Fraction(1, 5), Fraction(3, 10), Fraction(2, 5)])
def test_hybrid_formula_matches_independent_evaluators(candidates: int, accuracy: Fraction) -> None:
    profile = one_reroute_hybrid_profile(candidates)
    expected = one_reroute_hybrid_value(candidates, accuracy)
    direct, normalization = evaluate_direct(profile, candidates, accuracy)
    signatures = tuple(signature_from_policy(policy) for policy in profile)
    polynomial = signature_profile_polynomial(signatures)
    assert expected == evaluate_formula(profile, candidates, accuracy)
    assert expected == direct == evaluate_quadratic(polynomial, accuracy)
    assert normalization == 1


def test_restricted_thresholds_and_ties() -> None:
    for candidates in range(3, 9):
        lower = Fraction(1, candidates)
        upper = Fraction(1, candidates - 1)
        assert restricted_winners(candidates, lower) == (
            "territorial",
            "one-reroute-hybrid",
        )
        assert restricted_winners(candidates, (lower + upper) / 2) == ("one-reroute-hybrid",)
        assert restricted_winners(candidates, upper) == (
            "direct",
            "one-reroute-hybrid",
        )
        assert restricted_winners(candidates, (upper + 1) / 2) == ("direct",)
        assert one_reroute_hybrid_value(candidates, lower) == distinct_territorial_value(candidates)
        assert one_reroute_hybrid_value(candidates, upper) == direct_two_value(upper)


def test_exact_quadratic_minimum_checks_vertex() -> None:
    value, point = minimum_on_interval(
        (Fraction(1), Fraction(-2), Fraction(1)), Fraction(0), Fraction(2)
    )
    assert value == 0
    assert point == 1


@pytest.mark.parametrize("candidates", [3, 4])
def test_unrestricted_informative_envelope_certificate(candidates: int) -> None:
    certificate = certify_informative_envelope(candidates)
    assert certificate.hybrid_interval_passed
    assert certificate.direct_interval_passed
    assert certificate.minimum_hybrid_margin == 0
    assert certificate.minimum_direct_margin == 0


@pytest.mark.parametrize(("candidates", "expected"), [(3, Fraction(11, 12)), (4, Fraction(2, 3))])
def test_anti_informative_optima_match_raw_enumeration(candidates: int, expected: Fraction) -> None:
    signature_value, _ = exact_signature_optimum_fast(candidates, Fraction(0))
    raw_value = exhaustive_optimum(candidates, 2, Fraction(0)).value
    assert signature_value == raw_value == expected
