"""Exact equilibrium-selection procedures for the frozen DD-002 fixture."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from typing import Any

from distributed_discovery.information_design.game import (
    Likelihood,
    Partition,
    canonical_partitions,
    message_posterior,
    planner_discovery,
    pure_equilibria,
    refines,
    symmetric_equilibrium,
)

Profile = tuple[int, int]
Absorption = tuple[tuple[Profile, Fraction], ...]
RULES = (
    "anonymous_symmetric",
    "best_pure",
    "worst_pure",
    "uniform_potential_maximum",
    "uniform_strict_best_response_basin",
    "planner",
)


@dataclass(frozen=True)
class MessageSelection:
    """Exact message-game selections and dynamic certificate objects."""

    block: tuple[int, ...]
    weight: Fraction
    posterior: tuple[Fraction, ...]
    symmetric_strategy: tuple[Fraction, ...]
    pure_equilibrium_profiles: tuple[Profile, ...]
    best_pure_discovery: Fraction
    worst_pure_discovery: Fraction
    potential_maximizers: tuple[Profile, ...]
    potential_maximum: Fraction
    potential_discovery: Fraction
    best_response_moves: tuple[tuple[Profile, tuple[Profile, ...]], ...]
    absorption_by_initial: tuple[tuple[Profile, Absorption], ...]
    basin_terminal_distribution: Absorption
    basin_discovery: Fraction
    basin_branch_dependent: bool
    planner_discovery: Fraction
    anonymous_symmetric_discovery: Fraction


@dataclass(frozen=True)
class PartitionSelection:
    """Exact selected values for one deterministic disclosure partition."""

    partition_id: str
    partition: Partition
    messages: tuple[MessageSelection, ...]
    values: dict[str, Fraction]
    potential_tied_profile_count: int
    potential_multiple_discovery_values: bool
    basin_branch_dependent: bool


def profile_payoffs(posterior: tuple[Fraction, ...], profile: Profile) -> tuple[Fraction, Fraction]:
    """Return exact equal-split payoffs for a labeled pure profile."""

    first, second = profile
    return (
        posterior[first] / (2 if first == second else 1),
        posterior[second] / (2 if first == second else 1),
    )


def profile_discovery(posterior: tuple[Fraction, ...], profile: Profile) -> Fraction:
    """Return posterior union discovery at a pure action profile."""

    first, second = profile
    return posterior[first] if first == second else posterior[first] + posterior[second]


def exact_potential(posterior: tuple[Fraction, ...], profile: Profile) -> Fraction:
    """Return the exact Rosenthal potential of the equal-split game."""

    first, second = profile
    if first == second:
        return Fraction(3, 2) * posterior[first]
    return posterior[first] + posterior[second]


def strict_best_response_moves(
    posterior: tuple[Fraction, ...], profile: Profile
) -> tuple[Profile, ...]:
    """Enumerate labeled unilateral strict moves to payoff-maximizing actions."""

    moves: list[Profile] = []
    for player in (0, 1):
        other_action = profile[1 - player]
        candidate_payoffs = tuple(
            posterior[action] / (2 if action == other_action else 1)
            for action in range(len(posterior))
        )
        maximum = max(candidate_payoffs)
        current = candidate_payoffs[profile[player]]
        if maximum <= current:
            continue
        for action, payoff in enumerate(candidate_payoffs):
            if payoff == maximum:
                updated = list(profile)
                updated[player] = action
                moves.append((updated[0], updated[1]))
    if any(
        exact_potential(posterior, move) <= exact_potential(posterior, profile) for move in moves
    ):
        raise AssertionError("strict best response must increase the exact potential")
    return tuple(moves)


def _sorted_absorption(distribution: dict[Profile, Fraction]) -> Absorption:
    return tuple(sorted((profile, probability) for profile, probability in distribution.items()))


def _basin_certificate(
    posterior: tuple[Fraction, ...],
) -> tuple[
    tuple[tuple[Profile, tuple[Profile, ...]], ...],
    tuple[tuple[Profile, Absorption], ...],
    Absorption,
    bool,
]:
    profiles: tuple[Profile, ...] = tuple(
        (first, second) for first in range(len(posterior)) for second in range(len(posterior))
    )
    transition_map = {
        profile: strict_best_response_moves(posterior, profile) for profile in profiles
    }

    @cache
    def absorb(profile: Profile) -> Absorption:
        moves = transition_map[profile]
        if not moves:
            return ((profile, Fraction(1)),)
        distribution: dict[Profile, Fraction] = {}
        for move in moves:
            for terminal, probability in absorb(move):
                distribution[terminal] = distribution.get(
                    terminal, Fraction(0)
                ) + probability / len(moves)
        return _sorted_absorption(distribution)

    by_initial = tuple((profile, absorb(profile)) for profile in profiles)
    terminal_distribution: dict[Profile, Fraction] = {}
    for _, absorption in by_initial:
        for terminal, probability in absorption:
            terminal_distribution[terminal] = terminal_distribution.get(
                terminal, Fraction(0)
            ) + probability / len(profiles)
    branch_dependent = any(
        len({profile_discovery(posterior, terminal) for terminal, _ in absorption}) > 1
        for _, absorption in by_initial
    )
    return (
        tuple((profile, transition_map[profile]) for profile in profiles),
        by_initial,
        _sorted_absorption(terminal_distribution),
        branch_dependent,
    )


def evaluate_message(likelihood: Likelihood, block: tuple[int, ...]) -> MessageSelection:
    """Evaluate all exact selection procedures for one public-message game."""

    weight, posterior = message_posterior(likelihood, block)
    symmetric = symmetric_equilibrium(posterior)
    pure = pure_equilibria(posterior)
    pure_profiles = tuple(equilibrium.actions for equilibrium in pure)
    pure_discoveries = tuple(equilibrium.discovery for equilibrium in pure)
    all_profiles: tuple[Profile, ...] = tuple(
        (first, second) for first in range(len(posterior)) for second in range(len(posterior))
    )
    potential_maximum = max(exact_potential(posterior, profile) for profile in all_profiles)
    potential_maximizers = tuple(
        profile
        for profile in all_profiles
        if exact_potential(posterior, profile) == potential_maximum
    )
    if any(profile not in pure_profiles for profile in potential_maximizers):
        raise AssertionError("every global exact-potential maximum must be a pure equilibrium")
    potential_discovery = sum(
        (profile_discovery(posterior, profile) for profile in potential_maximizers),
        start=Fraction(0),
    ) / len(potential_maximizers)
    moves, absorption, terminal_distribution, branch_dependent = _basin_certificate(posterior)
    basin_discovery = sum(
        (
            probability * profile_discovery(posterior, terminal)
            for terminal, probability in terminal_distribution
        ),
        start=Fraction(0),
    )
    return MessageSelection(
        block=block,
        weight=weight,
        posterior=posterior,
        symmetric_strategy=symmetric.strategy,
        pure_equilibrium_profiles=pure_profiles,
        best_pure_discovery=max(pure_discoveries),
        worst_pure_discovery=min(pure_discoveries),
        potential_maximizers=potential_maximizers,
        potential_maximum=potential_maximum,
        potential_discovery=potential_discovery,
        best_response_moves=moves,
        absorption_by_initial=absorption,
        basin_terminal_distribution=terminal_distribution,
        basin_discovery=basin_discovery,
        basin_branch_dependent=branch_dependent,
        planner_discovery=planner_discovery(posterior),
        anonymous_symmetric_discovery=symmetric.discovery,
    )


def evaluate_partition(
    partition_id: str, partition: Partition, likelihood: Likelihood
) -> PartitionSelection:
    """Evaluate exact ex-ante selection values for a disclosure partition."""

    messages = tuple(evaluate_message(likelihood, block) for block in partition)
    values = {
        "anonymous_symmetric": sum(
            (message.weight * message.anonymous_symmetric_discovery for message in messages),
            start=Fraction(0),
        ),
        "best_pure": sum(
            (message.weight * message.best_pure_discovery for message in messages),
            start=Fraction(0),
        ),
        "worst_pure": sum(
            (message.weight * message.worst_pure_discovery for message in messages),
            start=Fraction(0),
        ),
        "uniform_potential_maximum": sum(
            (message.weight * message.potential_discovery for message in messages),
            start=Fraction(0),
        ),
        "uniform_strict_best_response_basin": sum(
            (message.weight * message.basin_discovery for message in messages),
            start=Fraction(0),
        ),
        "planner": sum(
            (message.weight * message.planner_discovery for message in messages),
            start=Fraction(0),
        ),
    }
    return PartitionSelection(
        partition_id=partition_id,
        partition=partition,
        messages=messages,
        values=values,
        potential_tied_profile_count=sum(len(message.potential_maximizers) for message in messages),
        potential_multiple_discovery_values=any(
            len(
                {
                    profile_discovery(message.posterior, profile)
                    for profile in message.potential_maximizers
                }
            )
            > 1
            for message in messages
        ),
        basin_branch_dependent=any(message.basin_branch_dependent for message in messages),
    )


def evaluate_catalogue(likelihood: Likelihood) -> tuple[PartitionSelection, ...]:
    """Evaluate every canonical four-state deterministic disclosure partition."""

    return tuple(
        evaluate_partition(f"P{index:02d}", partition, likelihood)
        for index, partition in enumerate(canonical_partitions(4))
    )


def refinement_comparisons(
    catalogue: tuple[PartitionSelection, ...],
) -> tuple[dict[str, Any], ...]:
    """Return all strict refinement comparisons for every declared rule."""

    comparisons: list[dict[str, Any]] = []
    for finer, coarser in itertools.permutations(catalogue, 2):
        if not refines(finer.partition, coarser.partition):
            continue
        comparisons.append(
            {
                "more_informative": finer.partition_id,
                "less_informative": coarser.partition_id,
                "differences": {rule: finer.values[rule] - coarser.values[rule] for rule in RULES},
            }
        )
    return tuple(comparisons)


def _fraction(value: Fraction) -> str:
    return str(value)


def _profile(profile: Profile) -> list[int]:
    return [profile[0], profile[1]]


def _absorption(value: Absorption) -> list[dict[str, Any]]:
    return [
        {"terminal": _profile(profile), "probability": _fraction(probability)}
        for profile, probability in value
    ]


def selection_certificate(
    likelihood: Likelihood,
    catalogue: tuple[PartitionSelection, ...],
    comparisons: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    """Serialize complete exact finite-game and absorption witnesses."""

    records = []
    for partition in catalogue:
        messages = []
        for message in partition.messages:
            messages.append(
                {
                    "block": list(message.block),
                    "weight": _fraction(message.weight),
                    "posterior": [_fraction(value) for value in message.posterior],
                    "anonymous_symmetric": {
                        "strategy": [_fraction(value) for value in message.symmetric_strategy],
                        "discovery": _fraction(message.anonymous_symmetric_discovery),
                    },
                    "pure_equilibrium_profiles": [
                        _profile(profile) for profile in message.pure_equilibrium_profiles
                    ],
                    "best_pure_discovery": _fraction(message.best_pure_discovery),
                    "worst_pure_discovery": _fraction(message.worst_pure_discovery),
                    "potential_maximum": _fraction(message.potential_maximum),
                    "potential_maximizers": [
                        _profile(profile) for profile in message.potential_maximizers
                    ],
                    "potential_discovery": _fraction(message.potential_discovery),
                    "best_response_moves": [
                        {
                            "profile": _profile(profile),
                            "moves": [_profile(move) for move in moves],
                        }
                        for profile, moves in message.best_response_moves
                    ],
                    "absorption_by_initial": [
                        {"initial": _profile(profile), "absorption": _absorption(absorption)}
                        for profile, absorption in message.absorption_by_initial
                    ],
                    "basin_terminal_distribution": _absorption(message.basin_terminal_distribution),
                    "basin_discovery": _fraction(message.basin_discovery),
                    "basin_branch_dependent": message.basin_branch_dependent,
                    "planner_discovery": _fraction(message.planner_discovery),
                }
            )
        records.append(
            {
                "partition_id": partition.partition_id,
                "partition": [list(block) for block in partition.partition],
                "messages": messages,
                "values": {rule: _fraction(value) for rule, value in partition.values.items()},
                "potential_tied_profile_count": partition.potential_tied_profile_count,
                "potential_multiple_discovery_values": (
                    partition.potential_multiple_discovery_values
                ),
                "basin_branch_dependent": partition.basin_branch_dependent,
            }
        )
    serialized_comparisons = [
        {
            "more_informative": comparison["more_informative"],
            "less_informative": comparison["less_informative"],
            "differences": {
                rule: _fraction(value) for rule, value in comparison["differences"].items()
            },
        }
        for comparison in comparisons
    ]
    counts = {
        rule: {
            "harmful": sum(
                Fraction(item["differences"][rule]) < 0 for item in serialized_comparisons
            ),
            "improving": sum(
                Fraction(item["differences"][rule]) > 0 for item in serialized_comparisons
            ),
            "tied": sum(
                Fraction(item["differences"][rule]) == 0 for item in serialized_comparisons
            ),
        }
        for rule in RULES
    }
    return {
        "schema_version": 1,
        "method": "exact finite selection catalogue with Bellman absorption witnesses",
        "likelihood": [[_fraction(value) for value in row] for row in likelihood],
        "rules": list(RULES),
        "partitions": records,
        "refinement_comparisons": serialized_comparisons,
        "refinement_counts": counts,
    }
