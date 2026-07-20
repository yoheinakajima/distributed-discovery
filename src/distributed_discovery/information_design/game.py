"""Exact bounded public-disclosure games for DD-002."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from fractions import Fraction

Partition = tuple[tuple[int, ...], ...]
Likelihood = tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class PureEquilibrium:
    actions: tuple[int, int]
    payoffs: tuple[Fraction, Fraction]
    discovery: Fraction


@dataclass(frozen=True)
class SymmetricEquilibrium:
    strategy: tuple[Fraction, ...]
    discovery: Fraction


def canonical_partitions(size: int) -> tuple[Partition, ...]:
    if size < 1:
        raise ValueError("partition size must be positive")
    result: list[Partition] = []

    def extend(item: int, blocks: list[list[int]]) -> None:
        if item == size:
            result.append(tuple(tuple(block) for block in blocks))
            return
        for index in range(len(blocks)):
            blocks[index].append(item)
            extend(item + 1, blocks)
            blocks[index].pop()
        blocks.append([item])
        extend(item + 1, blocks)
        blocks.pop()

    extend(0, [])
    return tuple(result)


def refines(finer: Partition, coarser: Partition) -> bool:
    coarse_block = {item: index for index, block in enumerate(coarser) for item in block}
    return all(len({coarse_block[item] for item in block}) == 1 for block in finer)


def message_posterior(
    likelihood: Likelihood, block: tuple[int, ...]
) -> tuple[Fraction, tuple[Fraction, ...]]:
    targets = len(likelihood)
    if targets < 2 or any(len(row) != len(likelihood[0]) for row in likelihood):
        raise ValueError("likelihood matrix must be rectangular with at least two targets")
    joints = tuple(
        sum((likelihood[target][signal] for signal in block), start=Fraction(0)) / targets
        for target in range(targets)
    )
    weight = sum(joints, start=Fraction(0))
    if weight == 0:
        raise ValueError("disclosure message has zero probability")
    return weight, tuple(joint / weight for joint in joints)


def pure_equilibria(posterior: tuple[Fraction, ...]) -> tuple[PureEquilibrium, ...]:
    result = []
    actions = range(len(posterior))
    for first, second in itertools.product(actions, repeat=2):
        payoff_first = posterior[first] / (2 if first == second else 1)
        payoff_second = posterior[second] / (2 if first == second else 1)
        first_best = all(
            payoff_first >= posterior[action] / (2 if action == second else 1) for action in actions
        )
        second_best = all(
            payoff_second >= posterior[action] / (2 if action == first else 1) for action in actions
        )
        if first_best and second_best:
            discovery = posterior[first]
            if second != first:
                discovery += posterior[second]
            result.append(
                PureEquilibrium((first, second), (payoff_first, payoff_second), discovery)
            )
    return tuple(result)


def symmetric_equilibrium(posterior: tuple[Fraction, ...]) -> SymmetricEquilibrium:
    actions = len(posterior)
    for mask in range(1, 1 << actions):
        support = [action for action in range(actions) if mask & (1 << action)]
        if any(posterior[action] == 0 for action in support):
            continue
        level = Fraction(2 * len(support) - 1, 2) / sum(
            (1 / posterior[action] for action in support), start=Fraction(0)
        )
        strategy = tuple(
            2 * (1 - level / posterior[action]) if action in support else Fraction(0)
            for action in range(actions)
        )
        if (
            all(strategy[action] > 0 for action in support)
            and all(
                posterior[action] <= level for action in range(actions) if action not in support
            )
            and sum(strategy, start=Fraction(0)) == 1
        ):
            discovery = sum(
                (
                    posterior[action] * (2 * strategy[action] - strategy[action] * strategy[action])
                    for action in range(actions)
                ),
                start=Fraction(0),
            )
            return SymmetricEquilibrium(strategy, discovery)
    raise RuntimeError("no anonymous symmetric equilibrium found")


def planner_discovery(posterior: tuple[Fraction, ...]) -> Fraction:
    return sum(sorted(posterior, reverse=True)[:2], start=Fraction(0))
