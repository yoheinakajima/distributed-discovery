"""Exact evaluators for zero-communication private-information teams."""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import TypeAlias

Policy: TypeAlias = tuple[int, ...]
Profile: TypeAlias = tuple[Policy, ...]


def validate_profile(profile: Profile, candidates: int) -> None:
    if candidates < 2:
        raise ValueError("candidates must be at least two")
    if not profile:
        raise ValueError("profile must contain at least one searcher")
    for policy in profile:
        if len(policy) != candidates:
            raise ValueError("each policy must define one action per signal")
        if any(action < 0 or action >= candidates for action in policy):
            raise ValueError("policy action outside candidate space")


def signal_probability(theta: int, signal: int, candidates: int, accuracy: Fraction) -> Fraction:
    if not 0 <= accuracy <= 1:
        raise ValueError("accuracy must lie in [0,1]")
    return accuracy if signal == theta else (1 - accuracy) / (candidates - 1)


def action_success_probability(
    policy: Policy, theta: int, candidates: int, accuracy: Fraction
) -> Fraction:
    return sum(
        (
            signal_probability(theta, signal, candidates, accuracy)
            for signal, action in enumerate(policy)
            if action == theta
        ),
        start=Fraction(0),
    )


def evaluate_formula(profile: Profile, candidates: int, accuracy: Fraction) -> Fraction:
    """Evaluate a fixed profile using conditional failure factorization."""
    validate_profile(profile, candidates)
    total = Fraction(0)
    for theta in range(candidates):
        failure = Fraction(1)
        for policy in profile:
            failure *= 1 - action_success_probability(policy, theta, candidates, accuracy)
        total += 1 - failure
    return total / candidates


def evaluate_direct(
    profile: Profile, candidates: int, accuracy: Fraction
) -> tuple[Fraction, Fraction]:
    """Independently enumerate target and every private-signal profile."""
    validate_profile(profile, candidates)
    searchers = len(profile)
    discovery = Fraction(0)
    normalization = Fraction(0)
    for theta in range(candidates):
        prior = Fraction(1, candidates)
        for signals in itertools.product(range(candidates), repeat=searchers):
            probability = prior
            for signal in signals:
                probability *= signal_probability(theta, signal, candidates, accuracy)
            normalization += probability
            actions = (policy[signal] for policy, signal in zip(profile, signals, strict=True))
            if theta in actions:
                discovery += probability
    return discovery, normalization


def direct_policy(candidates: int) -> Policy:
    return tuple(range(candidates))


def direct_profile(candidates: int, searchers: int) -> Profile:
    return tuple(direct_policy(candidates) for _ in range(searchers))


def territorial_profile(candidates: int, searchers: int) -> Profile:
    return tuple(tuple([agent % candidates] * candidates) for agent in range(searchers))


def direct_value(searchers: int, accuracy: Fraction) -> Fraction:
    return 1 - (1 - accuracy) ** searchers


def territorial_value(candidates: int, searchers: int) -> Fraction:
    return Fraction(min(candidates, searchers), candidates)


def pooled_planner_value(candidates: int, searchers: int, accuracy: Fraction) -> Fraction:
    """Directly enumerate the pooled top-N posterior frontier for small instances."""
    total = Fraction(0)
    budget = min(candidates, searchers)
    for signals in itertools.product(range(candidates), repeat=searchers):
        joint_by_theta: list[Fraction] = []
        for theta in range(candidates):
            likelihood = Fraction(1, candidates)
            for signal in signals:
                likelihood *= signal_probability(theta, signal, candidates, accuracy)
            joint_by_theta.append(likelihood)
        total += sum(sorted(joint_by_theta, reverse=True)[:budget], start=Fraction(0))
    return total
