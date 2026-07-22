"""Pure and symmetric-mixed equilibrium primitives for DD-017."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from fractions import Fraction
from itertools import combinations, product
from typing import Any

from distributed_discovery.threshold_discovery.model import (
    occupancy_vectors,
    planner_value,
    strategic_candidate_payoff,
)


def validate_game(
    posterior: Sequence[Fraction], agents: int, threshold: int
) -> tuple[Fraction, ...]:
    values = tuple(posterior)
    if len(values) < 2 or any(value <= 0 for value in values):
        raise ValueError("posterior must have at least two positive entries")
    if sum(values, Fraction(0)) != 1:
        raise ValueError("posterior must normalize")
    if agents < 2 or not 1 <= threshold <= agents:
        raise ValueError("agents and threshold are inconsistent")
    return values


def discovery_value(
    occupancy: Sequence[int], posterior: Sequence[Fraction], threshold: int
) -> Fraction:
    return sum(
        (posterior[index] for index, count in enumerate(occupancy) if count >= threshold),
        Fraction(0),
    )


def action_payoff(posterior_mass: Fraction, occupancy: int, threshold: int) -> Fraction:
    if occupancy < threshold:
        return Fraction(0)
    return posterior_mass / occupancy


def pure_nash_witness(
    occupancy: Sequence[int], posterior: Sequence[Fraction], threshold: int
) -> dict[str, Any] | None:
    """Return one strict unilateral deviation, or None for a weak pure Nash state."""

    for origin, origin_count in enumerate(occupancy):
        if not origin_count:
            continue
        current = action_payoff(posterior[origin], origin_count, threshold)
        for destination, destination_count in enumerate(occupancy):
            if destination == origin:
                continue
            deviating = action_payoff(posterior[destination], destination_count + 1, threshold)
            if deviating > current:
                return {
                    "origin": origin,
                    "destination": destination,
                    "current_payoff": current,
                    "deviation_payoff": deviating,
                }
    return None


def is_pure_nash(occupancy: Sequence[int], posterior: Sequence[Fraction], threshold: int) -> bool:
    return pure_nash_witness(occupancy, posterior, threshold) is None


def pure_nash_occupancies(
    posterior: Sequence[Fraction], agents: int, threshold: int
) -> tuple[tuple[int, ...], ...]:
    values = validate_game(posterior, agents, threshold)
    return tuple(
        occupancy
        for occupancy in occupancy_vectors(len(values), agents)
        if is_pure_nash(occupancy, values, threshold)
    )


def _actions_from_occupancy(occupancy: Sequence[int]) -> tuple[int, ...]:
    return tuple(action for action, count in enumerate(occupancy) for _ in range(count))


def strict_coalition_witness(
    occupancy: Sequence[int],
    posterior: Sequence[Fraction],
    threshold: int,
    coalition_size: int,
) -> dict[str, Any] | None:
    """Find a deviation making every named coalition member strictly better."""

    actions = _actions_from_occupancy(occupancy)
    agents = len(actions)
    if not 1 <= coalition_size <= agents:
        raise ValueError("coalition size is inconsistent")
    candidates = len(occupancy)
    current_payoffs = tuple(
        action_payoff(posterior[action], occupancy[action], threshold) for action in actions
    )
    for coalition in combinations(range(agents), coalition_size):
        for destinations in product(range(candidates), repeat=coalition_size):
            if all(
                actions[member] == destination
                for member, destination in zip(coalition, destinations, strict=True)
            ):
                continue
            deviated_actions = list(actions)
            for member, destination in zip(coalition, destinations, strict=True):
                deviated_actions[member] = destination
            new_occupancy = tuple(deviated_actions.count(action) for action in range(candidates))
            new_payoffs = tuple(
                action_payoff(
                    posterior[deviated_actions[member]],
                    new_occupancy[deviated_actions[member]],
                    threshold,
                )
                for member in coalition
            )
            if all(
                new_payoff > current_payoffs[member]
                for member, new_payoff in zip(coalition, new_payoffs, strict=True)
            ):
                return {
                    "coalition": coalition,
                    "origins": tuple(actions[member] for member in coalition),
                    "destinations": destinations,
                    "new_occupancy": new_occupancy,
                    "old_payoffs": tuple(current_payoffs[member] for member in coalition),
                    "new_payoffs": new_payoffs,
                }
    return None


def tied_mode_distribution(posterior: Sequence[Fraction]) -> tuple[Fraction, ...]:
    maximum = max(posterior)
    modes = sum(value == maximum for value in posterior)
    return tuple(Fraction(1, modes) if value == maximum else Fraction(0) for value in posterior)


def symmetric_mixed_equilibrium_check(
    posterior: Sequence[Fraction],
    agents: int,
    threshold: int,
    probabilities: Sequence[Fraction],
) -> dict[str, Any]:
    values = validate_game(posterior, agents, threshold)
    mixture = tuple(probabilities)
    if len(mixture) != len(values) or any(value < 0 for value in mixture):
        raise ValueError("mixture has invalid support")
    if sum(mixture, Fraction(0)) != 1:
        raise ValueError("mixture must normalize")
    payoffs = tuple(
        strategic_candidate_payoff(values[index], agents, threshold, probability)
        for index, probability in enumerate(mixture)
    )
    support = tuple(index for index, probability in enumerate(mixture) if probability)
    support_payoff = payoffs[support[0]]
    support_equal = all(payoffs[index] == support_payoff for index in support)
    outside_bounded = all(
        payoffs[index] <= support_payoff
        for index, probability in enumerate(mixture)
        if not probability
    )
    return {
        "is_equilibrium": support_equal and outside_bounded,
        "probabilities": mixture,
        "action_payoffs": payoffs,
        "support": support,
        "support_payoff": support_payoff,
        "support_equal": support_equal,
        "outside_bounded": outside_bounded,
    }


def _ratio_or_infinity(numerator: Fraction, denominator: Fraction) -> Fraction | str:
    if denominator == 0:
        return "infinity" if numerator > 0 else Fraction(1)
    return numerator / denominator


def evaluate_game(
    name: str,
    posterior: Sequence[Fraction],
    agents: int,
    threshold: int,
) -> dict[str, Any]:
    values = validate_game(posterior, agents, threshold)
    equilibria = pure_nash_occupancies(values, agents, threshold)
    if not equilibria:
        raise RuntimeError("registered finite game has no pure Nash occupancy")
    rows: list[dict[str, Any]] = []
    for occupancy in equilibria:
        discovery = discovery_value(occupancy, values, threshold)
        pair_block = strict_coalition_witness(occupancy, values, threshold, 2)
        tau_block = strict_coalition_witness(occupancy, values, threshold, threshold)
        rows.append(
            {
                "occupancy": occupancy,
                "discovery": discovery,
                "pairwise_strict_stable": pair_block is None,
                "tau_strict_stable": tau_block is None,
                "pairwise_block_witness": pair_block,
                "tau_block_witness": tau_block,
            }
        )
    discoveries = tuple(row["discovery"] for row in rows)
    planner = planner_value(values, agents, threshold)
    best = max(discoveries)
    worst = min(discoveries)
    tied = symmetric_mixed_equilibrium_check(
        values, agents, threshold, tied_mode_distribution(values)
    )
    return {
        "name": name,
        "posterior": values,
        "agents": agents,
        "threshold": threshold,
        "occupancy_states": sum(1 for _ in occupancy_vectors(len(values), agents)),
        "pure_nash_count": len(rows),
        "pure_nash": rows,
        "planner_discovery": planner,
        "best_equilibrium_discovery": best,
        "worst_equilibrium_discovery": worst,
        "price_of_stability": _ratio_or_infinity(planner, best),
        "price_of_anarchy": _ratio_or_infinity(planner, worst),
        "pairwise_strict_stable_count": sum(row["pairwise_strict_stable"] for row in rows),
        "tau_strict_stable_count": sum(row["tau_strict_stable"] for row in rows),
        "tied_mode_mixed": tied,
    }


def evaluate_registry(
    fixtures: Iterable[dict[str, Any]], agent_grid: Iterable[int]
) -> dict[str, Any]:
    rows = []
    for fixture in fixtures:
        posterior = tuple(Fraction(value) for value in fixture["posterior"])
        for agents in agent_grid:
            for threshold in range(1, agents + 1):
                rows.append(evaluate_game(fixture["name"], posterior, agents, threshold))
    return {
        "games": rows,
        "game_count": len(rows),
        "occupancy_state_count": sum(row["occupancy_states"] for row in rows),
        "zero_worst_equilibrium_games": sum(
            row["worst_equilibrium_discovery"] == 0 for row in rows
        ),
        "no_pairwise_stable_equilibrium_games": sum(
            row["pairwise_strict_stable_count"] == 0 for row in rows
        ),
        "no_tau_stable_equilibrium_games": sum(row["tau_strict_stable_count"] == 0 for row in rows),
        "tied_mode_mixed_failures": sum(
            not row["tied_mode_mixed"]["is_equilibrium"] for row in rows
        ),
    }
