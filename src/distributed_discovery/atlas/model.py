"""Exact DD-009 architecture registry and metric evaluator."""

from __future__ import annotations

from collections.abc import Iterator
from fractions import Fraction
from itertools import product

from distributed_discovery.mechanisms.general import recommendation
from distributed_discovery.mechanisms.joint import realized_transfer
from distributed_discovery.mechanisms.model import signal_probability

EVIDENCE = ("common", "independent")
DISCLOSURE = ("private", "pooled")
ALLOCATION = ("direct", "consensus", "market", "planner", "sequential", "joint")
TIMING = ("simultaneous", "sequential")
REWARDS = ("equal-split", "pooling", "sole-rescue", "marginal-coverage", "DD-006A", "DD-006B")

REWARDS_BY_ALLOCATION = {
    "direct": {"equal-split", "sole-rescue", "marginal-coverage"},
    "consensus": {"equal-split", "pooling"},
    "market": {"equal-split"},
    "planner": {"pooling"},
    "sequential": {"equal-split"},
    "joint": {"sole-rescue", "DD-006A", "DD-006B"},
}


def cartesian_registry() -> list[dict[str, str]]:
    return [
        {
            "evidence": evidence,
            "disclosure": disclosure,
            "allocation": allocation,
            "timing": timing,
            "reward": reward,
        }
        for evidence, disclosure, allocation, timing, reward in product(
            EVIDENCE, DISCLOSURE, ALLOCATION, TIMING, REWARDS
        )
    ]


def validity(cell: dict[str, str]) -> tuple[bool, str]:
    allocation = cell["allocation"]
    if (allocation == "sequential") != (cell["timing"] == "sequential"):
        return False, "timing must be sequential exactly when allocation is sequential"
    private_allocations = {"direct", "sequential", "joint"}
    if (cell["disclosure"] == "private") != (allocation in private_allocations):
        return False, "allocation and disclosure observability are incompatible"
    if cell["reward"] not in REWARDS_BY_ALLOCATION[allocation]:
        return False, "reward is not registered for this allocation protocol"
    if (
        allocation == "joint"
        and cell["reward"] in {"DD-006A", "DD-006B"}
        and cell["evidence"] != "independent"
    ):
        return False, "DD-006 mechanisms require their registered independent-signal law"
    return True, "registered coherent architecture"


def _states(evidence: str) -> Iterator[tuple[int, tuple[int, int], Fraction]]:
    if evidence == "common":
        for target, signal in product(range(3), repeat=2):
            yield target, (signal, signal), Fraction(1, 3) * signal_probability(target, signal)
    else:
        for target, first, second in product(range(3), repeat=3):
            probability = (
                Fraction(1, 3)
                * signal_probability(target, first)
                * signal_probability(target, second)
            )
            yield target, (first, second), probability


def _actions(allocation: str, signals: tuple[int, int], target: int) -> tuple[int, ...]:
    if allocation == "direct":
        return signals
    if allocation in {"consensus", "market"}:
        leader = signals[0] if signals[0] == signals[1] else min(signals)
        return (leader, leader)
    if allocation in {"planner", "joint"}:
        return recommendation(signals, 0)
    first = signals[0]
    if first == target:
        return (first,)
    second = signals[1] if signals[1] != first else (first + 1) % 3
    return (first, second)


def _incentives(cell: dict[str, str]) -> tuple[str, str, int, str]:
    reward = cell["reward"]
    if reward == "DD-006A":
        return (
            "weak",
            "weak",
            81,
            "maximum unilateral best responses per type at the truthful profile",
        )
    if reward == "DD-006B":
        return "strict", "strict", 1, "unilateral best responses per type at the truthful profile"
    if cell["allocation"] == "market":
        return "not-applicable", "selected-equilibrium", 1, "declared selected pooled outcome"
    if cell["allocation"] == "joint":
        return "not-verified", "not-verified", 1, "registered deterministic candidate profile"
    return "not-applicable", "protocol-controlled", 1, "registered deterministic protocol profile"


def evaluate(cell: dict[str, str]) -> dict[str, object]:
    valid, reason = validity(cell)
    if not valid:
        raise ValueError(reason)
    discovery = Fraction()
    actions_count = Fraction()
    distinct = Fraction()
    correct = Fraction()
    transfer_budget = Fraction()
    planner_discovery = Fraction()
    for target, signals, probability in _states(cell["evidence"]):
        actions = _actions(cell["allocation"], signals, target)
        found = target in actions
        discovery += probability * Fraction(found)
        actions_count += probability * len(actions)
        distinct += probability * len(set(actions))
        correct += probability * sum(action == target for action in actions)
        planner_discovery += probability * Fraction(target in recommendation(signals, 0))
        if cell["reward"] in {"sole-rescue", "marginal-coverage"}:
            transfer_budget += probability * Fraction(found and actions.count(target) == 1)
        elif cell["reward"] == "DD-006B":
            pair = (actions[0], actions[1])
            coefficients = (Fraction(1, 4), Fraction(), Fraction(3, 4))
            transfer_budget += probability * sum(
                (
                    realized_transfer(
                        "target-actions", coefficients, target, signals, pair, agent, 0
                    )
                    for agent in range(2)
                ),
                Fraction(),
            )

    information_cost = Fraction() if cell["evidence"] == "common" else Fraction(1, 4)
    rounds = actions_count if cell["timing"] == "sequential" else Fraction(1)
    truthfulness, obedience, multiplicity, multiplicity_basis = _incentives(cell)
    return {
        **cell,
        "channels": 1 if cell["evidence"] == "common" else 2,
        "information_cost": str(information_cost),
        "expected_actions": str(actions_count),
        "action_quality": str(correct / actions_count),
        "expected_distinct_actions": str(distinct),
        "discovery": str(discovery),
        "protocol_loss": str(planner_discovery - discovery),
        "average_private_payoff": str((discovery + transfer_budget - information_cost) / 2),
        "social_net_value": str(discovery - information_cost - transfer_budget),
        "transfer_budget": str(transfer_budget),
        "rounds": str(rounds),
        "truthfulness": truthfulness,
        "obedience": obedience,
        "equilibrium_multiplicity": multiplicity,
        "equilibrium_multiplicity_basis": multiplicity_basis,
    }


def dominance(rows: list[dict[str, object]]) -> dict[str, object]:
    maximize = ("discovery", "action_quality", "social_net_value")
    minimize = ("information_cost", "transfer_budget", "rounds")
    dominated_by: dict[int, list[int]] = {index: [] for index in range(len(rows))}
    for left, right in product(range(len(rows)), repeat=2):
        if left == right:
            continue
        weak = all(
            Fraction(str(rows[left][key])) >= Fraction(str(rows[right][key])) for key in maximize
        )
        weak = weak and all(
            Fraction(str(rows[left][key])) <= Fraction(str(rows[right][key])) for key in minimize
        )
        strict = any(
            Fraction(str(rows[left][key])) > Fraction(str(rows[right][key])) for key in maximize
        ) or any(
            Fraction(str(rows[left][key])) < Fraction(str(rows[right][key])) for key in minimize
        )
        if weak and strict:
            dominated_by[right].append(left)
    return {
        "maximize": list(maximize),
        "minimize": list(minimize),
        "pareto_indices": [index for index, dominators in dominated_by.items() if not dominators],
        "dominated_by": {str(index): values for index, values in dominated_by.items()},
    }
