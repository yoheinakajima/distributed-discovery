"""Closed-form posterior games after both signals become public."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from distributed_discovery.coordination_free_sharing.model import (
    OutcomeMetrics,
    public_profile_probability,
    validate_parameters,
)
from distributed_discovery.coordination_free_sharing.private_game import (
    dependence_index,
    signal_advantage,
)


@dataclass(frozen=True)
class PublicSelection:
    agreement_posterior: Fraction
    agreement_action_probability: Fraction
    agreement_regime: str
    disagreement_posterior: Fraction
    disagreement_action_probability: Fraction


def selected_equilibrium(p: Fraction, rho: Fraction) -> PublicSelection:
    validate_parameters(p, rho)
    t = signal_advantage(p)
    a = dependence_index(p, rho)
    u = Fraction(1, 2) + t / (1 + a)
    if u >= Fraction(2, 3):
        action = Fraction(1)
        regime = "pure-agreement"
    else:
        action = 3 * u - 1
        regime = "interior-anti-crowding"
    return PublicSelection(u, action, regime, Fraction(1, 2), Fraction(1, 2))


def _conditional_metrics(posterior: Fraction, action_probability: Fraction) -> OutcomeMetrics:
    discovery = posterior * (1 - (1 - action_probability) ** 2) + (1 - posterior) * (
        1 - action_probability**2
    )
    collision = action_probability**2 + (1 - action_probability) ** 2
    quality = posterior * action_probability + (1 - posterior) * (1 - action_probability)
    return OutcomeMetrics(
        discovery=discovery,
        payoff_per_agent=discovery / 2,
        collision=collision,
        diversity=1 - collision,
        expected_distinct_actions=2 - collision,
        average_action_quality=quality,
    )


def metrics(p: Fraction, rho: Fraction) -> OutcomeMetrics:
    selection = selected_equilibrium(p, rho)
    agreement_weight = public_profile_probability(0, 0, p, rho) + public_profile_probability(
        1, 1, p, rho
    )
    disagreement_weight = 1 - agreement_weight
    agreement = _conditional_metrics(
        selection.agreement_posterior, selection.agreement_action_probability
    )
    disagreement = _conditional_metrics(
        selection.disagreement_posterior, selection.disagreement_action_probability
    )

    discovery = (
        agreement_weight * agreement.discovery + disagreement_weight * disagreement.discovery
    )
    collision = (
        agreement_weight * agreement.collision + disagreement_weight * disagreement.collision
    )
    quality = (
        agreement_weight * agreement.average_action_quality
        + disagreement_weight * disagreement.average_action_quality
    )
    return OutcomeMetrics(
        discovery=discovery,
        payoff_per_agent=discovery / 2,
        collision=collision,
        diversity=1 - collision,
        expected_distinct_actions=2 - collision,
        average_action_quality=quality,
    )
