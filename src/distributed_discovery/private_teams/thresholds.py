"""Exact two-searcher threshold formulas and bounded symbolic certificates."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from fractions import Fraction

from distributed_discovery.private_teams.model import Policy, Profile
from distributed_discovery.private_teams.signatures import (
    SignatureProfile,
    all_feasible_signatures,
)

Quadratic = tuple[Fraction, Fraction, Fraction]  # constant, linear, quadratic


@dataclass(frozen=True)
class IntervalCertificate:
    candidates: int
    signature_count: int
    profile_count: int
    hybrid_interval_passed: bool
    direct_interval_passed: bool
    minimum_hybrid_margin: Fraction
    minimum_direct_margin: Fraction


def direct_two_value(accuracy: Fraction) -> Fraction:
    return 2 * accuracy - accuracy * accuracy


def distinct_territorial_value(candidates: int) -> Fraction:
    if candidates < 2:
        raise ValueError("candidates must be at least two")
    return Fraction(2, candidates)


def one_reroute_hybrid_value(candidates: int, accuracy: Fraction) -> Fraction:
    if candidates < 2:
        raise ValueError("candidates must be at least two")
    return Fraction(1 + (candidates - 2) * accuracy, candidates - 1)


def one_reroute_hybrid_profile(candidates: int) -> Profile:
    if candidates < 2:
        raise ValueError("candidates must be at least two")
    constant: Policy = (0,) * candidates
    follower = tuple(1 if signal == 0 else signal for signal in range(candidates))
    return (constant, follower)


def restricted_winners(candidates: int, accuracy: Fraction) -> tuple[str, ...]:
    values = {
        "direct": direct_two_value(accuracy),
        "territorial": distinct_territorial_value(candidates),
        "one-reroute-hybrid": one_reroute_hybrid_value(candidates, accuracy),
    }
    best = max(values.values())
    return tuple(name for name, value in values.items() if value == best)


def signature_profile_polynomial(profile: SignatureProfile) -> Quadratic:
    """Return exact coefficients for the two-searcher discovery polynomial in p."""
    if len(profile) != 2:
        raise ValueError("threshold polynomial requires exactly two searchers")
    candidates = len(profile[0])
    if candidates < 2 or len(profile[1]) != candidates:
        raise ValueError("signatures must share a target space of size at least two")
    constant = Fraction(0)
    linear = Fraction(0)
    quadratic = Fraction(0)
    for target in range(candidates):
        terms: list[tuple[Fraction, Fraction]] = []
        for signature in profile:
            count, fixed = signature[target]
            alpha = Fraction(count - fixed, candidates - 1)
            beta = Fraction(fixed) - alpha
            terms.append((alpha, beta))
        (alpha_1, beta_1), (alpha_2, beta_2) = terms
        constant += alpha_1 + alpha_2 - alpha_1 * alpha_2
        linear += beta_1 + beta_2 - alpha_1 * beta_2 - alpha_2 * beta_1
        quadratic -= beta_1 * beta_2
    scale = Fraction(1, candidates)
    return constant * scale, linear * scale, quadratic * scale


def evaluate_quadratic(polynomial: Quadratic, point: Fraction) -> Fraction:
    constant, linear, quadratic = polynomial
    return constant + linear * point + quadratic * point * point


def _subtract(left: Quadratic, right: Quadratic) -> Quadratic:
    return tuple(a - b for a, b in zip(left, right, strict=True))  # type: ignore[return-value]


def minimum_on_interval(
    polynomial: Quadratic, lower: Fraction, upper: Fraction
) -> tuple[Fraction, Fraction]:
    if lower > upper:
        raise ValueError("interval endpoints are reversed")
    points = [lower, upper]
    _, linear, quadratic = polynomial
    if quadratic > 0:
        vertex = -linear / (2 * quadratic)
        if lower <= vertex <= upper:
            points.append(vertex)
    values = [(evaluate_quadratic(polynomial, point), point) for point in points]
    return min(values)


def certify_informative_envelope(candidates: int) -> IntervalCertificate:
    """Exhaustively certify hybrid/direct optimality for one finite M."""
    if candidates < 3:
        raise ValueError("informative envelope certificate requires M at least three")
    signatures = all_feasible_signatures(candidates)
    hybrid = (
        Fraction(1, candidates - 1),
        Fraction(candidates - 2, candidates - 1),
        Fraction(0),
    )
    direct = (Fraction(0), Fraction(2), Fraction(-1))
    hybrid_lower = Fraction(1, candidates)
    boundary = Fraction(1, candidates - 1)
    hybrid_margin: Fraction | None = None
    direct_margin: Fraction | None = None
    hybrid_passed = True
    direct_passed = True
    profile_count = 0
    for profile in itertools.combinations_with_replacement(signatures, 2):
        profile_count += 1
        polynomial = signature_profile_polynomial(profile)
        margin, _ = minimum_on_interval(_subtract(hybrid, polynomial), hybrid_lower, boundary)
        hybrid_margin = margin if hybrid_margin is None else min(hybrid_margin, margin)
        hybrid_passed &= margin >= 0
        margin, _ = minimum_on_interval(_subtract(direct, polynomial), boundary, Fraction(1))
        direct_margin = margin if direct_margin is None else min(direct_margin, margin)
        direct_passed &= margin >= 0
    assert hybrid_margin is not None and direct_margin is not None
    return IntervalCertificate(
        candidates=candidates,
        signature_count=len(signatures),
        profile_count=profile_count,
        hybrid_interval_passed=hybrid_passed,
        direct_interval_passed=direct_passed,
        minimum_hybrid_margin=hybrid_margin,
        minimum_direct_margin=direct_margin,
    )


def exact_signature_optimum_fast(
    candidates: int, accuracy: Fraction
) -> tuple[Fraction, SignatureProfile]:
    signatures = all_feasible_signatures(candidates)
    best = Fraction(-1)
    winner: SignatureProfile | None = None
    for profile in itertools.combinations_with_replacement(signatures, 2):
        value = evaluate_quadratic(signature_profile_polynomial(profile), accuracy)
        if value > best:
            best = value
            winner = profile
    if winner is None:
        raise RuntimeError("no signature profile was enumerated")
    return best, winner
