"""Closed-form private-information symmetric Bayes game."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from distributed_discovery.coordination_free_sharing.model import (
    OutcomeMetrics,
    validate_parameters,
)


@dataclass(frozen=True)
class PrivateSelection:
    follow_probability: Fraction
    regime: str
    unique_in_symmetric_class: bool


def signal_advantage(p: Fraction) -> Fraction:
    return 2 * p - 1


def dependence_index(p: Fraction, rho: Fraction) -> Fraction:
    t = signal_advantage(p)
    return t * t + rho * (1 - t * t)


def payoff_difference(p: Fraction, rho: Fraction, peer_follow: Fraction) -> Fraction:
    """Interim payoff from follow minus oppose after either private signal."""
    validate_parameters(p, rho)
    if not 0 <= peer_follow <= 1:
        raise ValueError("follow probability must lie in [0,1]")
    t = signal_advantage(p)
    a = dependence_index(p, rho)
    return (3 * t + a * (1 - 2 * peer_follow)) / 4


def selected_equilibrium(p: Fraction, rho: Fraction) -> PrivateSelection:
    validate_parameters(p, rho)
    t = signal_advantage(p)
    a = dependence_index(p, rho)
    if a == 0:
        return PrivateSelection(Fraction(1, 2), "degenerate-continuum-selected-half", False)
    if a <= 3 * t:
        return PrivateSelection(Fraction(1), "follow", True)
    return PrivateSelection(
        Fraction(1, 2) + 3 * t / (2 * a),
        "interior-anti-crowding",
        True,
    )


def metrics(p: Fraction, rho: Fraction, follow: Fraction) -> OutcomeMetrics:
    validate_parameters(p, rho)
    if not 0 <= follow <= 1:
        raise ValueError("follow probability must lie in [0,1]")
    t = signal_advantage(p)
    a = dependence_index(p, rho)
    both_correct_signals = (1 + a + 2 * t) / 4
    failure = both_correct_signals - (a + t) * follow + a * follow * follow
    discovery = 1 - failure
    collision = (1 + a) / 2 - 2 * a * follow * (1 - follow)
    quality = (1 - t) / 2 + t * follow
    return OutcomeMetrics(
        discovery=discovery,
        payoff_per_agent=discovery / 2,
        collision=collision,
        diversity=1 - collision,
        expected_distinct_actions=2 - collision,
        average_action_quality=quality,
    )


def selected_metrics(p: Fraction, rho: Fraction) -> OutcomeMetrics:
    return metrics(p, rho, selected_equilibrium(p, rho).follow_probability)


def direct_private_metrics(p: Fraction, rho: Fraction) -> OutcomeMetrics:
    return metrics(p, rho, Fraction(1))
