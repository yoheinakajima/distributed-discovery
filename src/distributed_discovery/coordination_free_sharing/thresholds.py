"""Exact algebraic certificates for the canonical p=3/5 theorem slice."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

ROOT_POLYNOMIAL = (24, 17, -16)
ROOT_INTERVAL = (Fraction(2679, 5000), Fraction(67, 125))
ROOT_EXPRESSION = "(5*sqrt(73)-17)/48"


def polynomial(rho: Fraction, coefficients: tuple[int, int, int] = ROOT_POLYNOMIAL) -> Fraction:
    quadratic, linear, constant = coefficients
    return quadratic * rho * rho + linear * rho + constant


def above_positive_threshold(rho: Fraction) -> bool:
    return polynomial(rho) > 0


def certificate() -> dict[str, Any]:
    lower, upper = ROOT_INTERVAL
    discriminant = ROOT_POLYNOMIAL[1] ** 2 - 4 * ROOT_POLYNOMIAL[0] * ROOT_POLYNOMIAL[2]
    checks = {
        "polynomial_matches": ROOT_POLYNOMIAL == (24, 17, -16),
        "discriminant": discriminant == 1825 == 25 * 73,
        "lower_sign_negative": polynomial(lower) < 0,
        "upper_sign_positive": polynomial(upper) > 0,
        "interval_inside_unit": 0 < lower < upper < 1,
        "unique_positive_root": polynomial(Fraction(0)) < 0 < polynomial(Fraction(1)),
    }
    return {
        "polynomial_coefficients": ROOT_POLYNOMIAL,
        "exact_positive_root": ROOT_EXPRESSION,
        "isolating_interval": ROOT_INTERVAL,
        "endpoint_signs": (polynomial(lower), polynomial(upper)),
        "checks": checks,
        "passed": all(checks.values()),
    }


def corrupted_interval_rejected() -> bool:
    lower, upper = Fraction(1, 2), Fraction(13, 25)
    return not (polynomial(lower) < 0 < polynomial(upper))
