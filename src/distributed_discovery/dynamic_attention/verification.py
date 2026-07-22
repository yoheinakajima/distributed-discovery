"""Independent labeled path enumeration for DD-015."""

from __future__ import annotations

import copy
from fractions import Fraction
from itertools import product
from typing import Any

from distributed_discovery.dynamic_attention.model import (
    Objective,
    action_from_policy,
    bayes_action,
    clue_posterior,
    initial_belief,
    signal_probability,
)


def enumerate_policy(
    agents: int,
    private_accuracy: Fraction,
    shared_accuracy: Fraction,
    objective: Objective,
    policy: dict[str, tuple[int, int, int]],
) -> dict[str, Fraction | int]:
    total_mass = Fraction()
    discovery = Fraction()
    actions_used = Fraction()
    distinct_actions = Fraction()
    follow_shared = Fraction()
    follow_previous = Fraction()
    lean_against_repeat = Fraction()
    decision_mass = Fraction()
    later_decision_mass = Fraction()
    for target in range(3):
        for shared in range(3):
            for clues in product(range(3), repeat=agents):
                probability = Fraction(1, 3) * signal_probability(shared, target, shared_accuracy)
                for clue in clues:
                    probability *= signal_probability(clue, target, private_accuracy)
                total_mass += probability
                history: tuple[int, ...] = ()
                hit = False
                path_follow_shared = 0
                path_follow_previous = 0
                path_lean = 0
                for stage, clue in enumerate(clues):
                    if objective == "stopping-on-success" and hit:
                        break
                    action = action_from_policy(policy, objective, shared, history, clue)
                    decision_mass += probability
                    if stage:
                        later_decision_mass += probability
                    if action == shared:
                        path_follow_shared += 1
                    if history and action == history[-1]:
                        path_follow_previous += 1
                    if history and len(set(history)) == 1 and action != history[-1]:
                        path_lean += 1
                    history = (*history, action)
                    hit = hit or action == target
                discovery += probability * int(hit)
                actions_used += probability * len(history)
                distinct_actions += probability * len(set(history))
                follow_shared += probability * path_follow_shared
                follow_previous += probability * path_follow_previous
                lean_against_repeat += probability * path_lean
    return {
        "probability_mass": total_mass,
        "discovery": discovery,
        "expected_actions": actions_used,
        "expected_rounds": actions_used,
        "expected_distinct_actions": distinct_actions,
        "shared_follow_rate": follow_shared / decision_mass,
        "previous_action_follow_rate": (
            follow_previous / later_decision_mass if later_decision_mass else Fraction()
        ),
        "lean_against_repeat_rate": (
            lean_against_repeat / later_decision_mass if later_decision_mass else Fraction()
        ),
        "labeled_paths": 3 ** (agents + 2),
    }


def enumerate_simple_policy(
    agents: int,
    private_accuracy: Fraction,
    shared_accuracy: Fraction,
    objective: Objective,
    rule: str,
) -> dict[str, Fraction]:
    total_mass = Fraction()
    discovery = Fraction()
    actions_used = Fraction()
    distinct_actions = Fraction()
    for target in range(3):
        for shared in range(3):
            for clues in product(range(3), repeat=agents):
                probability = Fraction(1, 3) * signal_probability(shared, target, shared_accuracy)
                for clue in clues:
                    probability *= signal_probability(clue, target, private_accuracy)
                total_mass += probability
                actions: list[int] = []
                for clue in clues:
                    if objective == "stopping-on-success" and target in actions:
                        break
                    if rule == "private-only":
                        action = clue
                    elif rule == "public-only":
                        action = shared
                    elif rule == "history-hidden-bayes":
                        action = bayes_action(
                            clue_posterior(
                                initial_belief(shared, shared_accuracy),
                                clue,
                                private_accuracy,
                            )
                        )
                    else:
                        raise ValueError(f"unknown simple policy {rule}")
                    actions.append(action)
                discovery += probability * int(target in actions)
                actions_used += probability * len(actions)
                distinct_actions += probability * len(set(actions))
    if total_mass != 1:
        raise RuntimeError("simple-policy enumeration did not normalize")
    return {
        "discovery": discovery,
        "expected_actions": actions_used,
        "expected_rounds": actions_used,
        "expected_distinct_actions": distinct_actions,
    }


def verify_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    checks = []
    for row in bundle["rows"]:
        for protocol in ("autonomous", "planner"):
            result = row[protocol]
            direct = enumerate_policy(
                row["agents"],
                Fraction(row["private_accuracy"]),
                Fraction(row["shared_accuracy"]),
                row["objective"],
                result["policy"],
            )
            checks.append(
                {
                    "cell": row["cell_id"],
                    "protocol": protocol,
                    "probability_normalized": direct["probability_mass"] == 1,
                    "discovery_equal": direct["discovery"] == result["discovery"],
                    "actions_equal": direct["expected_actions"] == result["expected_actions"],
                }
            )
    return {
        "passed": all(
            check["probability_normalized"] and check["discovery_equal"] and check["actions_equal"]
            for check in checks
        ),
        "checks": checks,
        "check_count": len(checks),
    }


def corruption_tests(bundle: dict[str, Any]) -> dict[str, bool]:
    row = bundle["rows"][0]
    changed_discovery = copy.deepcopy(bundle)
    changed_discovery["rows"][0]["planner"]["discovery"] += Fraction(1, 100)
    changed_action = copy.deepcopy(bundle)
    policy = changed_action["rows"][0]["autonomous"]["policy"]
    first = next(iter(policy))
    prescription = list(policy[first])
    prescription[0] = (prescription[0] + 1) % 3
    policy[first] = tuple(prescription)
    changed_objective = copy.deepcopy(bundle)
    changed_objective["rows"][0]["objective"] = "stopping-on-success"

    def rejected(candidate: dict[str, Any]) -> bool:
        try:
            return not verify_bundle(candidate)["passed"]
        except (KeyError, ValueError):
            return True

    return {
        "altered_planner_value_rejected": rejected(changed_discovery),
        "altered_action_rejected": rejected(changed_action),
        "altered_objective_rejected": rejected(changed_objective),
        "registered_row_was_valid": row["planner"]["discovery"] >= row["autonomous"]["discovery"],
    }
