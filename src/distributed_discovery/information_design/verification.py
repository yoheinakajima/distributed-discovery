"""Independent verifier for the DD-002 disclosure reversal witness."""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any

from distributed_discovery.information_design.game import Likelihood, Partition


def _posterior(
    likelihood: Likelihood, block: tuple[int, ...]
) -> tuple[Fraction, tuple[Fraction, ...]]:
    targets = len(likelihood)
    joint = tuple(
        sum((likelihood[target][state] for state in block), start=Fraction(0)) / targets
        for target in range(targets)
    )
    weight = sum(joint, start=Fraction(0))
    return weight, tuple(value / weight for value in joint)


def _pure_actions(posterior: tuple[Fraction, ...]) -> set[tuple[int, int]]:
    result = set()
    actions = range(len(posterior))
    for first, second in itertools.product(actions, repeat=2):
        first_payoff = posterior[first] / (2 if first == second else 1)
        second_payoff = posterior[second] / (2 if first == second else 1)
        if all(
            first_payoff >= posterior[deviation] / (2 if deviation == second else 1)
            for deviation in actions
        ) and all(
            second_payoff >= posterior[deviation] / (2 if deviation == first else 1)
            for deviation in actions
        ):
            result.add((first, second))
    return result


def _mixed_checks(
    posterior: tuple[Fraction, ...], strategy: tuple[Fraction, ...]
) -> tuple[bool, Fraction]:
    if any(probability < 0 for probability in strategy) or sum(strategy) != 1:
        return False, Fraction(-1)
    payoffs = tuple(
        posterior[action] * (1 - strategy[action] / 2) for action in range(len(posterior))
    )
    maximum = max(payoffs)
    equilibrium = all(
        payoffs[action] == maximum if probability > 0 else payoffs[action] <= maximum
        for action, probability in enumerate(strategy)
    )
    discovery = Fraction(0)
    for target, target_probability in enumerate(posterior):
        miss = Fraction(0)
        for first, second in itertools.product(range(len(posterior)), repeat=2):
            probability = strategy[first] * strategy[second]
            if target not in (first, second):
                miss += probability
        discovery += target_probability * (1 - miss)
    return equilibrium, discovery


def _refines(finer: Partition, coarser: Partition) -> bool:
    membership = {state: index for index, block in enumerate(coarser) for state in block}
    return all(len({membership[state] for state in block}) == 1 for block in finer)


def verify_witness(witness: dict[str, Any], likelihood: Likelihood) -> dict[str, Any]:
    fine: Partition = tuple(tuple(block) for block in witness["more_informative_partition"])
    coarse: Partition = tuple(tuple(block) for block in witness["less_informative_partition"])
    refinement = _refines(fine, coarse)
    message_checks = []
    selected_values = []
    pure_value_sets = []
    planner_values = []
    for partition, stored_messages in [
        (fine, witness["messages_more"]),
        (coarse, witness["messages_less"]),
    ]:
        selected = Fraction(0)
        pure_options: list[list[Fraction]] = []
        planner = Fraction(0)
        all_messages = True
        for block, stored in zip(partition, stored_messages, strict=True):
            weight, posterior = _posterior(likelihood, block)
            strategy = tuple(stored["anonymous_symmetric_equilibrium"]["strategy"])
            mixed_ok, mixed_discovery = _mixed_checks(posterior, strategy)
            stored_pure = {
                tuple(equilibrium["actions"]) for equilibrium in stored["pure_equilibria"]
            }
            reference_pure = _pure_actions(posterior)
            pure_discoveries = [
                posterior[first] if first == second else posterior[first] + posterior[second]
                for first, second in reference_pure
            ]
            planner_message = sum(sorted(posterior, reverse=True)[:2], start=Fraction(0))
            check = (
                weight == stored["probability"]
                and posterior == tuple(stored["posterior"])
                and mixed_ok
                and mixed_discovery == stored["anonymous_symmetric_equilibrium"]["discovery"]
                and stored_pure == reference_pure
                and planner_message == stored["planner_discovery"]
            )
            all_messages &= check
            selected += weight * mixed_discovery
            pure_options.append([weight * value for value in pure_discoveries])
            planner += weight * planner_message
        message_checks.append(all_messages)
        selected_values.append(selected)
        pure_value_sets.append(
            {
                sum(combination, start=Fraction(0))
                for combination in itertools.product(*pure_options)
            }
        )
        planner_values.append(planner)
    aggregates = (
        selected_values[0] == witness["selected_more"]
        and selected_values[1] == witness["selected_less"]
        and pure_value_sets[0] == set(witness["pure_more_values"])
        and pure_value_sets[1] == set(witness["pure_less_values"])
        and planner_values[0] == witness["planner_more"]
        and planner_values[1] == witness["planner_less"]
    )
    reversal = (
        selected_values[0] < selected_values[1]
        and min(pure_value_sets[0]) > max(pure_value_sets[1])
        and planner_values[0] >= planner_values[1]
    )
    return {
        "passed": refinement and all(message_checks) and aggregates and reversal,
        "refinement_verified": refinement,
        "message_games_verified": all(message_checks),
        "aggregates_verified": aggregates,
        "selection_dependent_reversal_verified": reversal,
    }
