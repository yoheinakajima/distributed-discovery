"""Certified tiny enumeration and bounded canonical search for DD-001."""

from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass
from fractions import Fraction

from distributed_discovery.private_teams.model import (
    Policy,
    Profile,
    action_success_probability,
    direct_policy,
    evaluate_formula,
)


@dataclass(frozen=True)
class ExhaustiveResult:
    value: Fraction
    profile: Profile
    policy_count: int
    reduced_profile_count: int
    ties: int


@dataclass(frozen=True)
class AscentResult:
    value: Fraction
    profile: Profile
    sweeps: int
    termination: str


def all_policies(candidates: int) -> tuple[Policy, ...]:
    return tuple(itertools.product(range(candidates), repeat=candidates))


def reduced_profile_count(candidates: int, searchers: int) -> int:
    policies = candidates**candidates
    return math.comb(policies + searchers - 1, searchers)


def exhaustive_optimum(candidates: int, searchers: int, accuracy: Fraction) -> ExhaustiveResult:
    policies = all_policies(candidates)
    best_value = Fraction(-1)
    best_profile: Profile | None = None
    ties = 0
    evaluated = 0
    for policy_indices in itertools.combinations_with_replacement(range(len(policies)), searchers):
        profile = tuple(policies[index] for index in policy_indices)
        value = evaluate_formula(profile, candidates, accuracy)
        evaluated += 1
        if value > best_value:
            best_value = value
            best_profile = profile
            ties = 1
        elif value == best_value:
            ties += 1
    expected = reduced_profile_count(candidates, searchers)
    if evaluated != expected or best_profile is None:
        raise RuntimeError("exhaustive profile count mismatch")
    return ExhaustiveResult(best_value, best_profile, len(policies), evaluated, ties)


def best_response(profile: Profile, agent: int, candidates: int, accuracy: Fraction) -> Policy:
    """Choose an exact coordinate best response; ties use the lowest action."""
    other_failure: list[Fraction] = []
    for theta in range(candidates):
        failure = Fraction(1)
        for index, policy in enumerate(profile):
            if index != agent:
                failure *= 1 - action_success_probability(policy, theta, candidates, accuracy)
        other_failure.append(failure)
    response: list[int] = []
    error_probability = (1 - accuracy) / (candidates - 1)
    for signal in range(candidates):
        scores = [
            other_failure[action] * (accuracy if action == signal else error_probability)
            for action in range(candidates)
        ]
        response.append(max(range(candidates), key=lambda action: (scores[action], -action)))
    return tuple(response)


def coordinate_ascent(
    initial: Profile,
    candidates: int,
    accuracy: Fraction,
    max_sweeps: int,
) -> AscentResult:
    profile = list(initial)
    previous = evaluate_formula(tuple(profile), candidates, accuracy)
    for sweep in range(1, max_sweeps + 1):
        changed = False
        for agent in range(len(profile)):
            candidate = best_response(tuple(profile), agent, candidates, accuracy)
            if candidate != profile[agent]:
                profile[agent] = candidate
                changed = True
        value = evaluate_formula(tuple(profile), candidates, accuracy)
        if value < previous:
            raise RuntimeError("coordinate ascent decreased the common objective")
        if not changed:
            return AscentResult(value, tuple(profile), sweep, "coordinate-fixed-point")
        previous = value
    return AscentResult(previous, tuple(profile), max_sweeps, "max-sweeps")


def random_profile(candidates: int, searchers: int, seed: int) -> Profile:
    generator = random.Random(seed)
    return tuple(
        tuple(generator.randrange(candidates) for _ in range(candidates)) for _ in range(searchers)
    )


def direct_is_coordinate_fixed(candidates: int, searchers: int, accuracy: Fraction) -> bool:
    policy = direct_policy(candidates)
    profile = tuple(policy for _ in range(searchers))
    return all(
        best_response(profile, agent, candidates, accuracy) == policy for agent in range(searchers)
    )
