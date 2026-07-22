"""Frozen binary hidden-dependence model and shared metric objects.

The public-signal result deliberately selects identical action distributions
that depend only on the common posterior.  It is not a claim about every
equilibrium when players may condition on ownership of the two signals.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from fractions import Fraction
from typing import Any


@dataclass(frozen=True)
class OutcomeMetrics:
    discovery: Fraction
    payoff_per_agent: Fraction
    collision: Fraction
    diversity: Fraction
    expected_distinct_actions: Fraction
    average_action_quality: Fraction
    centralized_top_two: Fraction = Fraction(1)

    @property
    def implementation_gap(self) -> Fraction:
        return self.centralized_top_two - self.discovery

    def record(self) -> dict[str, Fraction]:
        return {**asdict(self), "implementation_gap": self.implementation_gap}


def validate_parameters(p: Fraction, rho: Fraction) -> None:
    if not Fraction(1, 2) <= p <= 1:
        raise ValueError("signal accuracy must lie in [1/2,1]")
    if not 0 <= rho <= 1:
        raise ValueError("dependence must lie in [0,1]")


def signal_pair_probability(
    theta: int, first: int, second: int, p: Fraction, rho: Fraction
) -> Fraction:
    """Return P(s1,s2|theta) under the world-level mixture."""
    validate_parameters(p, rho)
    if any(value not in (0, 1) for value in (theta, first, second)):
        raise ValueError("binary state required")
    common = Fraction()
    if first == second:
        common = p if first == theta else 1 - p
    independent = (p if first == theta else 1 - p) * (p if second == theta else 1 - p)
    return rho * common + (1 - rho) * independent


def joint_probability(theta: int, first: int, second: int, p: Fraction, rho: Fraction) -> Fraction:
    return Fraction(1, 2) * signal_pair_probability(theta, first, second, p, rho)


def public_profile_probability(first: int, second: int, p: Fraction, rho: Fraction) -> Fraction:
    return sum((joint_probability(theta, first, second, p, rho) for theta in (0, 1)), Fraction())


def posterior(first: int, second: int, p: Fraction, rho: Fraction) -> tuple[Fraction, Fraction]:
    weights = tuple(joint_probability(theta, first, second, p, rho) for theta in (0, 1))
    total = sum(weights, Fraction())
    if total == 0:
        raise ValueError("public profile has zero probability")
    return weights[0] / total, weights[1] / total


def prize(action: int, peer_action: int, theta: int) -> Fraction:
    if action != theta:
        return Fraction()
    return Fraction(1, 2) if peer_action == theta else Fraction(1)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def serialize(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_text(value)
    if is_dataclass(value) and not isinstance(value, type):
        return serialize(asdict(value))
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialize(item) for item in value]
    return value
