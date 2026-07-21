"""Exact rational values for perfect-elimination batched search."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations


def ordered_compositions(total: int) -> tuple[tuple[int, ...], ...]:
    if total < 1:
        raise ValueError("budget must be positive")
    compositions: list[tuple[int, ...]] = []
    for mask in range(1 << (total - 1)):
        parts: list[int] = []
        last = 0
        for index in range(total - 1):
            if mask & (1 << index):
                parts.append(index + 1 - last)
                last = index + 1
        parts.append(total - last)
        compositions.append(tuple(parts))
    return tuple(compositions)


def validate_prior(prior: tuple[Fraction, ...], budget: int) -> None:
    if not prior or len(prior) > 8 or not 1 <= budget <= min(4, len(prior)):
        raise ValueError("configured dimensions exceed the registered DD-004 bounds")
    if any(value < 0 for value in prior) or sum(prior) != 1:
        raise ValueError("prior must be nonnegative and normalized exactly")


def ordered_actions(prior: tuple[Fraction, ...]) -> tuple[int, ...]:
    return tuple(sorted(range(len(prior)), key=lambda action: (-prior[action], action)))


def evaluate_schedule(
    prior: tuple[Fraction, ...], budget: int, schedule: tuple[int, ...]
) -> dict[str, Fraction]:
    """Evaluate the top-prior policy; failures are the only continuation history."""
    validate_prior(prior, budget)
    if sum(schedule) != budget or any(size < 1 for size in schedule):
        raise ValueError("schedule must be an ordered positive composition of the budget")
    actions = ordered_actions(prior)[:budget]
    terminal = sum((prior[action] for action in actions), Fraction(0))
    expected_actions = Fraction(0)
    expected_rounds = Fraction(0)
    failure_probability = Fraction(1)
    cursor = 0
    for size in schedule:
        expected_actions += size * failure_probability
        expected_rounds += failure_probability
        batch_mass = sum((prior[action] for action in actions[cursor : cursor + size]), Fraction(0))
        failure_probability -= batch_mass
        cursor += size
    return {
        "terminal_discovery": terminal,
        "expected_actions": expected_actions,
        "expected_rounds": expected_rounds,
    }


def dynamic_optimum(
    prior: tuple[Fraction, ...], budget: int, schedule: tuple[int, ...]
) -> dict[str, Fraction]:
    """Bellman recursion over remaining candidates, with exact tie-breaking by action label."""
    validate_prior(prior, budget)
    states: dict[tuple[tuple[int, ...], int], tuple[Fraction, Fraction, Fraction]] = {}

    def solve(remaining: tuple[int, ...], stage: int) -> tuple[Fraction, Fraction, Fraction]:
        key = (remaining, stage)
        if key in states:
            return states[key]
        if stage == len(schedule):
            return Fraction(0), Fraction(0), Fraction(0)
        size = schedule[stage]
        mass = sum((prior[action] for action in remaining), Fraction(0))
        best: tuple[Fraction, Fraction, Fraction] | None = None
        for batch in combinations(remaining, size):
            hit = sum((prior[action] for action in batch), Fraction(0))
            next_remaining = tuple(action for action in remaining if action not in batch)
            future = solve(next_remaining, stage + 1)
            value = (hit + future[0], size * mass + future[1], mass + future[2])
            if best is None or value[0] > best[0] or (value[0] == best[0] and value[1] < best[1]):
                best = value
        if best is None:
            raise RuntimeError("no feasible batch")
        states[key] = best
        return best

    discovery, actions, rounds = solve(tuple(range(len(prior))), 0)
    return {"terminal_discovery": discovery, "expected_actions": actions, "expected_rounds": rounds}
