"""Complete bounded pure-equilibrium audits for DD-022."""

from __future__ import annotations

import itertools
from fractions import Fraction
from math import prod
from typing import Any

from distributed_discovery.coordination_free_sharing.model import (
    joint_probability,
    posterior,
    prize,
    public_profile_probability,
)

Strategy = tuple[int, int]
Profile = tuple[Strategy, Strategy]
STRATEGIES: dict[str, Strategy] = {
    "constant-0": (0, 0),
    "oppose": (1, 0),
    "follow": (0, 1),
    "constant-1": (1, 1),
}
STRATEGY_NAMES = {value: key for key, value in STRATEGIES.items()}


def _conditional_payoff(
    player: int,
    own_signal: int,
    own_action: int,
    opponent: Strategy,
    p: Fraction,
    rho: Fraction,
) -> Fraction:
    numerator = Fraction()
    denominator = Fraction()
    for theta, peer_signal in itertools.product((0, 1), repeat=2):
        signals = (own_signal, peer_signal) if player == 0 else (peer_signal, own_signal)
        probability = joint_probability(theta, signals[0], signals[1], p, rho)
        denominator += probability
        numerator += probability * prize(own_action, opponent[peer_signal], theta)
    if denominator == 0:
        raise AssertionError("private signals must have positive marginal probability")
    return numerator / denominator


def private_pure_equilibria(p: Fraction, rho: Fraction) -> tuple[Profile, ...]:
    result: list[Profile] = []
    strategies = tuple(STRATEGIES.values())
    for first, second in itertools.product(strategies, repeat=2):
        valid = True
        for player, own, peer in ((0, first, second), (1, second, first)):
            for signal in (0, 1):
                current = _conditional_payoff(player, signal, own[signal], peer, p, rho)
                deviation = _conditional_payoff(player, signal, 1 - own[signal], peer, p, rho)
                if deviation > current:
                    valid = False
        if valid:
            result.append((first, second))
    return tuple(result)


def private_profile_values(profile: Profile, p: Fraction, rho: Fraction) -> dict[str, Fraction]:
    discovery = Fraction()
    payoffs = [Fraction(), Fraction()]
    collision = Fraction()
    quality = Fraction()
    for theta, first_signal, second_signal in itertools.product((0, 1), repeat=3):
        probability = joint_probability(theta, first_signal, second_signal, p, rho)
        actions = (profile[0][first_signal], profile[1][second_signal])
        discovered = int(theta in actions)
        discovery += probability * discovered
        collision += probability * int(actions[0] == actions[1])
        quality += probability * Fraction(sum(action == theta for action in actions), 2)
        for player in (0, 1):
            payoffs[player] += probability * prize(actions[player], actions[1 - player], theta)
    if payoffs[0] + payoffs[1] != discovery:
        raise AssertionError("ex-post prize budget does not equal discovery")
    return {
        "discovery": discovery,
        "payoff_first": payoffs[0],
        "payoff_second": payoffs[1],
        "collision": collision,
        "diversity": 1 - collision,
        "average_action_quality": quality,
    }


def pure_action_equilibria(mu: tuple[Fraction, Fraction]) -> tuple[tuple[int, int], ...]:
    result: list[tuple[int, int]] = []
    for first, second in itertools.product((0, 1), repeat=2):
        first_payoff = mu[first] / (2 if first == second else 1)
        second_payoff = mu[second] / (2 if first == second else 1)
        if first_payoff >= mu[1 - first] / (2 if 1 - first == second else 1) and (
            second_payoff >= mu[1 - second] / (2 if 1 - second == first else 1)
        ):
            result.append((first, second))
    return tuple(result)


def shared_pure_correspondence(p: Fraction, rho: Fraction) -> dict[str, Any]:
    states: list[dict[str, Any]] = []
    best = Fraction()
    worst = Fraction()
    on_path_counts: list[int] = []
    for first, second in itertools.product((0, 1), repeat=2):
        weight = public_profile_probability(first, second, p, rho)
        if weight == 0:
            states.append({"signals": (first, second), "probability": weight, "on_path": False})
            continue
        mu = posterior(first, second, p, rho)
        equilibria = pure_action_equilibria(mu)
        discoveries = tuple(mu[a] if a == b else Fraction(1) for a, b in equilibria)
        states.append(
            {
                "signals": (first, second),
                "probability": weight,
                "on_path": True,
                "posterior": mu,
                "equilibria": equilibria,
                "discoveries": discoveries,
            }
        )
        on_path_counts.append(len(equilibria))
        best += weight * max(discoveries)
        worst += weight * min(discoveries)
    return {
        "states": states,
        "on_path_global_pure_selection_count": prod(on_path_counts),
        "best_pure_discovery": best,
        "worst_pure_discovery": worst,
    }


def private_correspondence_record(p: Fraction, rho: Fraction) -> dict[str, Any]:
    equilibria = private_pure_equilibria(p, rho)
    records = [
        {
            "strategies": (STRATEGY_NAMES[first], STRATEGY_NAMES[second]),
            **private_profile_values((first, second), p, rho),
        }
        for first, second in equilibria
    ]
    discoveries = [private_profile_values(profile, p, rho)["discovery"] for profile in equilibria]
    return {
        "equilibrium_count": len(records),
        "equilibria": records,
        "best_pure_discovery": max(discoveries),
        "worst_pure_discovery": min(discoveries),
    }
