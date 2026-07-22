"""Common-information dynamic programs for DD-015."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from itertools import product
from typing import Literal, cast

Objective = Literal["fixed-budget", "stopping-on-success"]
Protocol = Literal["autonomous", "planner"]
Prescription = tuple[int, int, int]


def signal_probability(signal: int, target: int, accuracy: Fraction) -> Fraction:
    if signal == target:
        return accuracy
    return (1 - accuracy) / 2


def normalize(weights: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    mass = sum(weights, Fraction())
    if mass <= 0:
        raise ValueError("cannot normalize zero probability mass")
    return tuple(value / mass for value in weights)


def clue_posterior(
    belief: tuple[Fraction, ...], clue: int, accuracy: Fraction
) -> tuple[Fraction, ...]:
    return normalize(
        tuple(belief[target] * signal_probability(clue, target, accuracy) for target in range(3))
    )


def bayes_action(belief: tuple[Fraction, ...]) -> int:
    return min(range(3), key=lambda action: (-belief[action], action))


def initial_belief(shared: int, accuracy: Fraction) -> tuple[Fraction, ...]:
    return clue_posterior((Fraction(1, 3),) * 3, shared, accuracy)


def autonomous_prescription(
    belief: tuple[Fraction, ...], private_accuracy: Fraction
) -> Prescription:
    return cast(
        Prescription,
        tuple(bayes_action(clue_posterior(belief, clue, private_accuracy)) for clue in range(3)),
    )


def prescriptions() -> tuple[Prescription, ...]:
    return tuple(cast(Prescription, item) for item in product(range(3), repeat=3))


@dataclass(frozen=True)
class Value:
    discovery: Fraction
    expected_actions: Fraction


def _branches(
    belief: tuple[Fraction, ...],
    private_accuracy: Fraction,
    prescription: Prescription,
) -> tuple[tuple[int, Fraction, tuple[Fraction, ...]], ...]:
    branches: list[tuple[int, Fraction, tuple[Fraction, ...]]] = []
    for action in range(3):
        weights = tuple(
            belief[target]
            * sum(
                (
                    signal_probability(clue, target, private_accuracy)
                    for clue in range(3)
                    if prescription[clue] == action
                ),
                Fraction(),
            )
            for target in range(3)
        )
        mass = sum(weights, Fraction())
        if mass:
            branches.append((action, mass, normalize(weights)))
    return tuple(branches)


def solve_protocol(
    agents: int,
    private_accuracy: Fraction,
    shared_accuracy: Fraction,
    objective: Objective,
    protocol: Protocol,
) -> dict[str, object]:
    if agents not in (2, 3):
        raise ValueError("DD-015 registers only two or three agents")
    if objective not in ("fixed-budget", "stopping-on-success"):
        raise ValueError("unknown DD-015 objective")
    if protocol not in ("autonomous", "planner"):
        raise ValueError("unknown DD-015 protocol")
    if not all(Fraction(1, 3) <= value <= 1 for value in (private_accuracy, shared_accuracy)):
        raise ValueError("registered clue accuracy must be at least random")

    policy: dict[str, Prescription] = {}
    choices: dict[tuple[int, tuple[Fraction, ...], frozenset[int]], Prescription] = {}
    state_count = 0

    @cache
    def solve(
        stage: int,
        belief: tuple[Fraction, ...],
        occupied: frozenset[int],
    ) -> Value:
        nonlocal state_count
        state_count += 1
        if stage == agents:
            return Value(sum((belief[t] for t in occupied), Fraction()), Fraction())

        candidates = (
            (autonomous_prescription(belief, private_accuracy),)
            if protocol == "autonomous"
            else prescriptions()
        )
        best: Value | None = None
        best_prescription: Prescription | None = None
        for prescription in candidates:
            discovery = Fraction()
            future_actions = Fraction()
            for action, branch_mass, action_belief in _branches(
                belief, private_accuracy, prescription
            ):
                next_occupied = occupied | {action}
                if objective == "fixed-budget":
                    future = solve(
                        stage + 1,
                        action_belief,
                        next_occupied,
                    )
                    discovery += branch_mass * future.discovery
                    future_actions += branch_mass * future.expected_actions
                else:
                    success_mass = branch_mass * action_belief[action]
                    failure_weights = tuple(
                        value if target != action else Fraction()
                        for target, value in enumerate(action_belief)
                    )
                    failure_mass_given_branch = sum(failure_weights, Fraction())
                    discovery += success_mass
                    if failure_mass_given_branch and stage + 1 < agents:
                        future = solve(
                            stage + 1,
                            normalize(failure_weights),
                            next_occupied,
                        )
                        joint_failure = branch_mass * failure_mass_given_branch
                        discovery += joint_failure * future.discovery
                        future_actions += joint_failure * future.expected_actions
            value = Value(discovery, Fraction(1) + future_actions)
            if (
                best is None
                or value.discovery > best.discovery
                or (
                    value.discovery == best.discovery
                    and value.expected_actions < best.expected_actions
                )
                or (
                    value == best
                    and best_prescription is not None
                    and prescription < best_prescription
                )
            ):
                best = value
                best_prescription = prescription
        if best is None or best_prescription is None:
            raise RuntimeError("no prescription evaluated")
        choices[(stage, belief, occupied)] = best_prescription
        return best

    initial_values = []
    for shared in range(3):
        initial_values.append(solve(0, initial_belief(shared, shared_accuracy), frozenset()))

    def materialize(
        stage: int,
        shared: int,
        history: tuple[int, ...],
        belief: tuple[Fraction, ...],
        occupied: frozenset[int],
    ) -> None:
        if stage == agents:
            return
        prescription = choices[(stage, belief, occupied)]
        policy[f"{objective}|{shared}|{','.join(map(str, history))}"] = prescription
        for action, _, action_belief in _branches(belief, private_accuracy, prescription):
            next_occupied = occupied | {action}
            if objective == "fixed-budget":
                materialize(
                    stage + 1,
                    shared,
                    (*history, action),
                    action_belief,
                    next_occupied,
                )
            else:
                failure_weights = tuple(
                    value if target != action else Fraction()
                    for target, value in enumerate(action_belief)
                )
                if sum(failure_weights, Fraction()) and stage + 1 < agents:
                    materialize(
                        stage + 1,
                        shared,
                        (*history, action),
                        normalize(failure_weights),
                        next_occupied,
                    )

    for shared in range(3):
        materialize(
            0,
            shared,
            (),
            initial_belief(shared, shared_accuracy),
            frozenset(),
        )
    return {
        "protocol": protocol,
        "objective": objective,
        "discovery": sum((value.discovery for value in initial_values), Fraction()) / 3,
        "expected_actions": sum((value.expected_actions for value in initial_values), Fraction())
        / 3,
        "expected_rounds": sum((value.expected_actions for value in initial_values), Fraction())
        / 3,
        "policy": policy,
        "state_evaluations": state_count,
    }


def action_from_policy(
    policy: dict[str, Prescription],
    objective: Objective,
    shared: int,
    history: tuple[int, ...],
    private_clue: int,
) -> int:
    key = f"{objective}|{shared}|{','.join(map(str, history))}"
    return policy[key][private_clue]
