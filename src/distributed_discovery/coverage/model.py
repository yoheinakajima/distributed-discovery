"""Primary exact evaluator for deterministic weighted-union coverage."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations


def validate(
    weights: tuple[Fraction, ...], actions: tuple[frozenset[int], ...], budget: int
) -> None:
    if (
        not weights
        or len(weights) > 8
        or len(actions) > 10
        or not 1 <= budget <= min(4, len(actions))
    ):
        raise ValueError("fixture exceeds registered DD-005 bounds")
    if any(weight < 0 for weight in weights) or any(not action for action in actions):
        raise ValueError("coverage requires nonnegative weights and nonempty actions")
    if any(item < 0 or item >= len(weights) for action in actions for item in action):
        raise ValueError("action covers an invalid outcome")


def value(weights: tuple[Fraction, ...], portfolio: tuple[frozenset[int], ...]) -> Fraction:
    covered = frozenset().union(*portfolio)
    return sum((weights[item] for item in covered), Fraction(0))


def exact_frontier(
    weights: tuple[Fraction, ...], actions: tuple[frozenset[int], ...], budget: int
) -> tuple[tuple[int, ...], Fraction]:
    validate(weights, actions, budget)
    candidates = [
        (choice, value(weights, tuple(actions[index] for index in choice)))
        for choice in combinations(range(len(actions)), budget)
    ]
    return max(candidates, key=lambda item: (item[1], tuple(-index for index in item[0])))


def top_individual(
    weights: tuple[Fraction, ...], actions: tuple[frozenset[int], ...], budget: int
) -> tuple[tuple[int, ...], Fraction]:
    choice = tuple(
        sorted(range(len(actions)), key=lambda index: (-value(weights, (actions[index],)), index))[
            :budget
        ]
    )
    return choice, value(weights, tuple(actions[index] for index in choice))


def greedy(
    weights: tuple[Fraction, ...], actions: tuple[frozenset[int], ...], budget: int
) -> tuple[tuple[int, ...], Fraction]:
    validate(weights, actions, budget)
    chosen: list[int] = []
    covered: tuple[frozenset[int], ...] = ()
    for _ in range(budget):
        choice = max(
            (index for index in range(len(actions)) if index not in chosen),
            key=lambda index: (
                value(weights, covered + (actions[index],)) - value(weights, covered),
                -index,
            ),
        )
        chosen.append(choice)
        covered += (actions[choice],)
    return tuple(chosen), value(weights, covered)
