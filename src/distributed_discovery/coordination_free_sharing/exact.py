"""Independent target/source/signal/action enumeration for DD-022."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from fractions import Fraction

from distributed_discovery.coordination_free_sharing.model import (
    OutcomeMetrics,
    joint_probability,
    posterior,
    prize,
    public_profile_probability,
)


@dataclass(frozen=True)
class EnumeratedSelection:
    probability: Fraction
    regime: str
    unique: bool


def _action_probability(signal: int, action: int, follow: Fraction) -> Fraction:
    return follow if action == signal else 1 - follow


def private_metrics(p: Fraction, rho: Fraction, follow: Fraction) -> OutcomeMetrics:
    discovery = Fraction()
    payoffs = [Fraction(), Fraction()]
    collision = Fraction()
    quality = Fraction()
    for theta, first_signal, second_signal, first_action, second_action in itertools.product(
        (0, 1), repeat=5
    ):
        probability = joint_probability(theta, first_signal, second_signal, p, rho)
        probability *= _action_probability(first_signal, first_action, follow)
        probability *= _action_probability(second_signal, second_action, follow)
        actions = (first_action, second_action)
        discovery += probability * int(theta in actions)
        collision += probability * int(first_action == second_action)
        quality += probability * Fraction(sum(action == theta for action in actions), 2)
        for player in (0, 1):
            payoffs[player] += probability * prize(actions[player], actions[1 - player], theta)
    if payoffs[0] != payoffs[1] or payoffs[0] + payoffs[1] != discovery:
        raise AssertionError("symmetric exact prize accounting failed")
    return OutcomeMetrics(
        discovery,
        payoffs[0],
        collision,
        1 - collision,
        2 - collision,
        quality,
    )


def private_payoff_difference(
    p: Fraction, rho: Fraction, peer_follow: Fraction, own_signal: int = 0
) -> Fraction:
    results = []
    for own_action in (own_signal, 1 - own_signal):
        value = Fraction()
        for theta, peer_signal, peer_action in itertools.product((0, 1), repeat=3):
            probability = joint_probability(theta, own_signal, peer_signal, p, rho)
            probability *= _action_probability(peer_signal, peer_action, peer_follow)
            value += probability * prize(own_action, peer_action, theta)
        results.append(value)
    marginal = Fraction(1, 2)
    return (results[0] - results[1]) / marginal


def private_selected_equilibrium(p: Fraction, rho: Fraction) -> EnumeratedSelection:
    difference_zero = private_payoff_difference(p, rho, Fraction())
    difference_one = private_payoff_difference(p, rho, Fraction(1))
    if difference_zero == difference_one == 0:
        return EnumeratedSelection(Fraction(1, 2), "degenerate-continuum-selected-half", False)
    if difference_one >= 0:
        return EnumeratedSelection(Fraction(1), "follow", True)
    slope = difference_one - difference_zero
    root = -difference_zero / slope
    if not 0 < root < 1:
        raise AssertionError("interior private root outside the simplex")
    return EnumeratedSelection(root, "interior-anti-crowding", True)


def _symmetric_probability(high_posterior: Fraction) -> EnumeratedSelection:
    def difference(peer_high: Fraction) -> Fraction:
        return high_posterior * (1 - peer_high / 2) - (1 - high_posterior) * (1 + peer_high) / 2

    at_one = difference(Fraction(1))
    if at_one >= 0:
        return EnumeratedSelection(Fraction(1), "pure-agreement", True)
    at_zero = difference(Fraction())
    root = -at_zero / (at_one - at_zero)
    return EnumeratedSelection(root, "interior-anti-crowding", True)


def shared_profile_selection(
    first: int, second: int, p: Fraction, rho: Fraction
) -> tuple[tuple[Fraction, Fraction], int, EnumeratedSelection]:
    mu = posterior(first, second, p, rho)
    high = first if first == second else 0
    if mu[1 - high] > mu[high]:
        high = 1 - high
    return mu, high, _symmetric_probability(mu[high])


def shared_metrics(p: Fraction, rho: Fraction) -> OutcomeMetrics:
    discovery = Fraction()
    payoffs = [Fraction(), Fraction()]
    collision = Fraction()
    quality = Fraction()
    for first_signal, second_signal in itertools.product((0, 1), repeat=2):
        weight = public_profile_probability(first_signal, second_signal, p, rho)
        if weight == 0:
            continue
        mu, high, selection = shared_profile_selection(first_signal, second_signal, p, rho)
        for theta, first_action, second_action in itertools.product((0, 1), repeat=3):
            first_high = (
                selection.probability if first_action == high else 1 - selection.probability
            )
            second_high = (
                selection.probability if second_action == high else 1 - selection.probability
            )
            probability = weight * mu[theta] * first_high * second_high
            actions = (first_action, second_action)
            discovery += probability * int(theta in actions)
            collision += probability * int(first_action == second_action)
            quality += probability * Fraction(sum(action == theta for action in actions), 2)
            for player in (0, 1):
                payoffs[player] += probability * prize(actions[player], actions[1 - player], theta)
    if payoffs[0] != payoffs[1] or payoffs[0] + payoffs[1] != discovery:
        raise AssertionError("shared exact prize accounting failed")
    return OutcomeMetrics(
        discovery,
        payoffs[0],
        collision,
        1 - collision,
        2 - collision,
        quality,
    )
