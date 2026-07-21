"""Primary exact evaluator for DD-014 conditional policies."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Any

POLICY_TYPES = ("private-dominant", "public-dominant", "contrarian")


def policy_action(policy: str, private: int, shared: int) -> int:
    if private == shared:
        return private
    if policy == "private-dominant":
        return private
    if policy == "public-dominant":
        return shared
    if policy == "contrarian":
        return 3 - private - shared
    raise ValueError(f"unknown policy: {policy}")


def anonymous_profiles(n: int) -> list[tuple[int, int, int]]:
    return [
        (private, public, n - private - public)
        for private in range(n + 1)
        for public in range(n - private + 1)
    ]


def _signal_probability(signal: int, target: int, accuracy: Fraction, labels: int) -> Fraction:
    return accuracy if signal == target else (1 - accuracy) / (labels - 1)


def evaluate_profile(counts: tuple[int, int, int], p: Fraction, q: Fraction) -> dict[str, Any]:
    """Enumerate a three-label anonymous role profile using branching policies."""
    policies = [
        *([POLICY_TYPES[0]] * counts[0]),
        *([POLICY_TYPES[1]] * counts[1]),
        *([POLICY_TYPES[2]] * counts[2]),
    ]
    n = len(policies)
    probability_mass = Fraction()
    discovery = Fraction()
    action_quality = Fraction()
    distinct_actions = Fraction()
    payoffs = [Fraction() for _ in policies]
    for target in range(3):
        for shared in range(3):
            for private_signals in product(range(3), repeat=n):
                probability = Fraction(1, 3) * _signal_probability(shared, target, q, 3)
                for signal in private_signals:
                    probability *= _signal_probability(signal, target, p, 3)
                actions = [
                    policy_action(policy, private, shared)
                    for policy, private in zip(policies, private_signals, strict=True)
                ]
                winners = [action == target for action in actions]
                winner_count = sum(winners)
                success = winner_count > 0
                probability_mass += probability
                discovery += probability * success
                action_quality += probability * Fraction(winner_count, n)
                distinct_actions += probability * len(set(actions))
                for index, winner in enumerate(winners):
                    if winner:
                        payoffs[index] += probability / winner_count
    if probability_mass != 1:
        raise ValueError("conditional profile probabilities do not normalize")
    type_payoffs: dict[str, Fraction | None] = {}
    offset = 0
    for policy, count in zip(POLICY_TYPES, counts, strict=True):
        type_payoffs[policy] = None if count == 0 else payoffs[offset]
        offset += count
    if (
        sum(
            count * (type_payoffs[policy] or Fraction())
            for policy, count in zip(POLICY_TYPES, counts, strict=True)
        )
        != discovery
    ):
        raise ValueError("conditional payoff accounting failed")
    return {
        "probability_mass": probability_mass,
        "discovery": discovery,
        "action_quality": action_quality,
        "expected_distinct_actions": distinct_actions,
        "payoffs": type_payoffs,
    }


def raw_policy_action(policy_id: int, private: int, shared: int) -> int:
    """Action from one of all sixteen deterministic two-label policy tables."""
    if not 0 <= policy_id < 16:
        raise ValueError("two-label raw policy ID must lie in [0,15]")
    observation = 2 * private + shared
    return (policy_id >> observation) & 1


def evaluate_raw_ordered(policies: tuple[int, int], p: Fraction, q: Fraction) -> dict[str, Any]:
    probability_mass = Fraction()
    discovery = Fraction()
    payoffs = [Fraction(), Fraction()]
    for target in range(2):
        for shared in range(2):
            for private_signals in product(range(2), repeat=2):
                probability = Fraction(1, 2) * _signal_probability(shared, target, q, 2)
                for signal in private_signals:
                    probability *= _signal_probability(signal, target, p, 2)
                actions = [
                    raw_policy_action(policy, private, shared)
                    for policy, private in zip(policies, private_signals, strict=True)
                ]
                winners = [action == target for action in actions]
                winner_count = sum(winners)
                success = winner_count > 0
                probability_mass += probability
                discovery += probability * success
                for index, winner in enumerate(winners):
                    if winner:
                        payoffs[index] += probability / winner_count
    if probability_mass != 1 or sum(payoffs) != discovery:
        raise ValueError("raw-policy probability or payoff accounting failed")
    return {"probability_mass": probability_mass, "discovery": discovery, "payoffs": payoffs}


def raw_policy_table(policy_id: int) -> list[int]:
    return [
        raw_policy_action(policy_id, private, shared) for private in range(2) for shared in range(2)
    ]
