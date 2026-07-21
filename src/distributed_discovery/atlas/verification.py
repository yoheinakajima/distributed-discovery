"""Separate exact evaluator for DD-009 architecture rows."""

from __future__ import annotations

from collections.abc import Iterator
from fractions import Fraction
from itertools import product


def _probability(target: int, signal: int) -> Fraction:
    return Fraction(2, 3) if target == signal else Fraction(1, 6)


def _states(evidence: str) -> Iterator[tuple[int, tuple[int, int], Fraction]]:
    if evidence == "common":
        for target, signal in product(range(3), repeat=2):
            yield target, (signal, signal), Fraction(1, 3) * _probability(target, signal)
    else:
        for target, first, second in product(range(3), repeat=3):
            yield (
                target,
                (first, second),
                Fraction(1, 3) * _probability(target, first) * _probability(target, second),
            )


def _diversify(signals: tuple[int, int]) -> tuple[int, int]:
    if signals[0] != signals[1]:
        return signals
    return signals[0], (signals[0] + 1) % 3


def _actions(allocation: str, signals: tuple[int, int], target: int) -> tuple[int, ...]:
    if allocation == "direct":
        return signals
    if allocation in {"consensus", "market"}:
        choice = signals[0] if signals[0] == signals[1] else min(signals)
        return choice, choice
    if allocation in {"planner", "joint"}:
        return _diversify(signals)
    if signals[0] == target:
        return (signals[0],)
    second = signals[1] if signals[1] != signals[0] else (signals[0] + 1) % 3
    return signals[0], second


def _information_score(report: int, target: int) -> Fraction:
    forecast = [Fraction(1, 6)] * 3
    forecast[report] = Fraction(2, 3)
    return 2 * forecast[target] - sum((value * value for value in forecast), Fraction())


def _labels(row: dict[str, object]) -> tuple[str, str, int, str]:
    reward = str(row["reward"])
    allocation = str(row["allocation"])
    if reward == "DD-006A":
        return (
            "weak",
            "weak",
            81,
            "maximum unilateral best responses per type at the truthful profile",
        )
    if reward == "DD-006B":
        return "strict", "strict", 1, "unilateral best responses per type at the truthful profile"
    if allocation == "market":
        return "not-applicable", "selected-equilibrium", 1, "declared selected pooled outcome"
    if allocation == "joint":
        return "not-verified", "not-verified", 1, "registered deterministic candidate profile"
    return "not-applicable", "protocol-controlled", 1, "registered deterministic protocol profile"


def verify_row(row: dict[str, object]) -> bool:
    evidence = str(row["evidence"])
    allocation = str(row["allocation"])
    reward = str(row["reward"])
    discovery = Fraction()
    action_count = Fraction()
    distinct = Fraction()
    correct = Fraction()
    budget = Fraction()
    benchmark = Fraction()
    for target, signals, probability in _states(evidence):
        actions = _actions(allocation, signals, target)
        found = target in actions
        discovery += probability * found
        action_count += probability * len(actions)
        distinct += probability * len(set(actions))
        correct += probability * sum(action == target for action in actions)
        benchmark += probability * Fraction(target in _diversify(signals))
        if reward in {"sole-rescue", "marginal-coverage"}:
            budget += probability * Fraction(found and actions.count(target) == 1)
        elif reward == "DD-006B":
            budget += probability * (
                Fraction(3, 2)
                + Fraction(1, 4)
                * sum((_information_score(report, target) for report in signals), Fraction())
            )
    information_cost = Fraction() if evidence == "common" else Fraction(1, 4)
    rounds = action_count if row["timing"] == "sequential" else Fraction(1)
    truthfulness, obedience, multiplicity, basis = _labels(row)
    expected = {
        "channels": 1 if evidence == "common" else 2,
        "information_cost": str(information_cost),
        "expected_actions": str(action_count),
        "action_quality": str(correct / action_count),
        "expected_distinct_actions": str(distinct),
        "discovery": str(discovery),
        "protocol_loss": str(benchmark - discovery),
        "average_private_payoff": str((discovery + budget - information_cost) / 2),
        "social_net_value": str(discovery - information_cost - budget),
        "transfer_budget": str(budget),
        "rounds": str(rounds),
        "truthfulness": truthfulness,
        "obedience": obedience,
        "equilibrium_multiplicity": multiplicity,
        "equilibrium_multiplicity_basis": basis,
    }
    return all(row.get(key) == value for key, value in expected.items())
