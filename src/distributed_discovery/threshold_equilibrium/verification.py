"""Independent labeled-profile verification for DD-017."""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction
from itertools import product
from typing import Any

from distributed_discovery.threshold_discovery.model import occupancy_vectors
from distributed_discovery.threshold_equilibrium.model import (
    action_payoff,
    discovery_value,
)


def labeled_pure_nash_occupancies(
    posterior: Sequence[Fraction], agents: int, threshold: int
) -> tuple[tuple[int, ...], ...]:
    """Enumerate every labeled action profile and deduplicate Nash occupancies."""

    candidates = len(posterior)
    equilibria = set()
    for actions in product(range(candidates), repeat=agents):
        occupancy = tuple(actions.count(candidate) for candidate in range(candidates))
        is_equilibrium = True
        for agent, origin in enumerate(actions):
            current = action_payoff(posterior[origin], occupancy[origin], threshold)
            for destination in range(candidates):
                if destination == origin:
                    continue
                changed = list(actions)
                changed[agent] = destination
                changed_occupancy = tuple(
                    changed.count(candidate) for candidate in range(candidates)
                )
                deviating = action_payoff(
                    posterior[destination], changed_occupancy[destination], threshold
                )
                if deviating > current:
                    is_equilibrium = False
                    break
            if not is_equilibrium:
                break
        if is_equilibrium:
            equilibria.add(occupancy)
    return tuple(sorted(equilibria))


def direct_mixed_action_payoffs(
    posterior: Sequence[Fraction],
    agents: int,
    threshold: int,
    probabilities: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    """Directly enumerate every labeled opponent action profile."""

    candidates = len(posterior)
    payoffs = []
    for chosen in range(candidates):
        expected = Fraction(0)
        for opponents in product(range(candidates), repeat=agents - 1):
            probability = Fraction(1)
            for action in opponents:
                probability *= probabilities[action]
            occupancy = 1 + opponents.count(chosen)
            expected += probability * action_payoff(posterior[chosen], occupancy, threshold)
        payoffs.append(expected)
    return tuple(payoffs)


def aggregate_strict_coalition_block_exists(
    occupancy: Sequence[int],
    posterior: Sequence[Fraction],
    threshold: int,
    coalition_size: int,
) -> bool:
    """Audit blocking through removal/addition occupancies and exact matching."""

    candidates = len(occupancy)
    for removed in occupancy_vectors(candidates, coalition_size):
        if any(removed[index] > occupancy[index] for index in range(candidates)):
            continue
        origins = tuple(
            origin for origin, removed_count in enumerate(removed) for _ in range(removed_count)
        )
        old_payoffs = tuple(
            action_payoff(posterior[origin], occupancy[origin], threshold) for origin in origins
        )
        for added in occupancy_vectors(candidates, coalition_size):
            new_occupancy = tuple(
                occupancy[index] - removed[index] + added[index] for index in range(candidates)
            )
            destinations = tuple(
                destination
                for destination, added_count in enumerate(added)
                for _ in range(added_count)
            )
            destination_payoffs = tuple(
                action_payoff(posterior[destination], new_occupancy[destination], threshold)
                for destination in destinations
            )

            def match(
                origin_index: int,
                available: tuple[int, ...],
                fixed_origins: tuple[int, ...],
                fixed_old_payoffs: tuple[Fraction, ...],
                fixed_destination_payoffs: tuple[Fraction, ...],
            ) -> bool:
                if origin_index == len(fixed_origins):
                    return True
                for slot in available:
                    if fixed_destination_payoffs[slot] <= fixed_old_payoffs[origin_index]:
                        continue
                    remaining = tuple(item for item in available if item != slot)
                    if match(
                        origin_index + 1,
                        remaining,
                        fixed_origins,
                        fixed_old_payoffs,
                        fixed_destination_payoffs,
                    ):
                        return True
                return False

            if match(
                0,
                tuple(range(coalition_size)),
                origins,
                old_payoffs,
                destination_payoffs,
            ):
                return True
    return False


def verify_registry(registry: dict[str, Any]) -> dict[str, Any]:
    errors = []
    labeled_profiles = 0
    for row in registry["games"]:
        posterior = row["posterior"]
        agents = row["agents"]
        threshold = row["threshold"]
        expected = tuple(sorted(item["occupancy"] for item in row["pure_nash"]))
        reproduced = labeled_pure_nash_occupancies(posterior, agents, threshold)
        labeled_profiles += len(posterior) ** agents
        if reproduced != expected:
            errors.append(f"pure equilibrium mismatch: {row['name']} N={agents} tau={threshold}")
        discoveries = tuple(
            discovery_value(occupancy, posterior, threshold) for occupancy in reproduced
        )
        if not discoveries:
            errors.append(f"missing pure equilibrium: {row['name']} N={agents} tau={threshold}")
            continue
        if min(discoveries) != row["worst_equilibrium_discovery"]:
            errors.append(f"worst discovery mismatch: {row['name']} N={agents} tau={threshold}")
        if max(discoveries) != row["best_equilibrium_discovery"]:
            errors.append(f"best discovery mismatch: {row['name']} N={agents} tau={threshold}")
        for equilibrium in row["pure_nash"]:
            occupancy = equilibrium["occupancy"]
            pairwise_stable = not aggregate_strict_coalition_block_exists(
                occupancy, posterior, threshold, 2
            )
            tau_stable = not aggregate_strict_coalition_block_exists(
                occupancy, posterior, threshold, threshold
            )
            if pairwise_stable != equilibrium["pairwise_strict_stable"]:
                errors.append(f"pair stability mismatch: {row['name']} N={agents} tau={threshold}")
            if tau_stable != equilibrium["tau_strict_stable"]:
                errors.append(f"tau stability mismatch: {row['name']} N={agents} tau={threshold}")
        tied = row["tied_mode_mixed"]
        mixed_payoffs = direct_mixed_action_payoffs(
            posterior, agents, threshold, tied["probabilities"]
        )
        if mixed_payoffs != tied["action_payoffs"]:
            errors.append(f"mixed payoff mismatch: {row['name']} N={agents} tau={threshold}")
        support_payoff = mixed_payoffs[tied["support"][0]]
        mixed_equilibrium = all(
            mixed_payoffs[index] == support_payoff for index in tied["support"]
        ) and all(
            mixed_payoffs[index] <= support_payoff
            for index, probability in enumerate(tied["probabilities"])
            if probability == 0
        )
        if mixed_equilibrium != tied["is_equilibrium"]:
            errors.append(f"mixed equilibrium mismatch: {row['name']} N={agents} tau={threshold}")
    return {
        "passed": not errors,
        "errors": errors,
        "labeled_profiles": labeled_profiles,
        "games_checked": len(registry["games"]),
    }
