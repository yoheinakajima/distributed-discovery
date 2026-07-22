"""Exact aggregation and independent-rescue calculations for DD-020."""

from __future__ import annotations

from collections.abc import Iterator
from fractions import Fraction
from itertools import product
from math import comb, factorial
from typing import Any

from distributed_discovery.signal_geometry.model import channels, one_person_accuracy


def compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    """Yield weak compositions in a deterministic order."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first, *rest)


def multinomial(counts: tuple[int, ...]) -> int:
    value = factorial(sum(counts))
    for count in counts:
        value //= factorial(count)
    return value


def pooled_accuracy_counts(targets: int, block_size: int, accuracy: Fraction) -> Fraction:
    """Method A: enumerate full signal-count vectors conditional on target zero."""
    if accuracy == Fraction(1, targets):
        return accuracy
    wrong = (1 - accuracy) / (targets - 1)
    value = Fraction()
    for counts in compositions(block_size, targets):
        maximum = max(counts)
        if counts[0] != maximum:
            continue
        ties = sum(count == maximum for count in counts)
        probability = (
            multinomial(counts) * accuracy ** counts[0] * wrong ** (block_size - counts[0])
        )
        value += probability / ties
    return value


def wrong_occupancy_tie_weight(balls: int, boxes: int, correct_count: int) -> Fraction:
    """Probability-weighted tie credit from an occupancy dynamic program."""
    # State is (allocated wrong signals, boxes tied with the correct target).
    states: dict[tuple[int, int], Fraction] = {(0, 0): Fraction(1)}
    for _ in range(boxes):
        nxt: dict[tuple[int, int], Fraction] = {}
        for (used, ties), weight in states.items():
            for count in range(min(correct_count, balls - used) + 1):
                key = (used + count, ties + int(count == correct_count))
                nxt[key] = nxt.get(key, Fraction()) + weight / factorial(count)
        states = nxt
    coefficient = Fraction(factorial(balls), boxes**balls)
    return coefficient * sum(
        weight / (1 + ties) for (used, ties), weight in states.items() if used == balls
    )


def pooled_accuracy_occupancy(targets: int, block_size: int, accuracy: Fraction) -> Fraction:
    """Method B: condition on correct count, then use a wrong-occupancy DP."""
    if accuracy == Fraction(1, targets):
        return accuracy
    value = Fraction()
    for correct_count in range(block_size + 1):
        wrong_count = block_size - correct_count
        correct_probability = (
            comb(block_size, correct_count)
            * accuracy**correct_count
            * (1 - accuracy) ** wrong_count
        )
        value += correct_probability * wrong_occupancy_tie_weight(
            wrong_count, targets - 1, correct_count
        )
    return value


def group_discovery(
    pooled_accuracy: Fraction, private_accuracy: Fraction, agents: int, block_size: int
) -> Fraction:
    return 1 - (1 - pooled_accuracy) * (1 - private_accuracy) ** (agents - block_size)


def point_profile(
    targets: int, agents: int, accuracy: Fraction, *, method: str = "counts"
) -> tuple[Fraction, ...]:
    evaluator = pooled_accuracy_counts if method == "counts" else pooled_accuracy_occupancy
    return tuple(
        group_discovery(evaluator(targets, block_size, accuracy), accuracy, agents, block_size)
        for block_size in range(1, agents + 1)
    )


def point_census(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for targets in config["targets"]:
        for accuracy_text in config["accuracies_by_targets"][targets]:
            accuracy = Fraction(accuracy_text)
            for agents in config["agents"]:
                profile_a = point_profile(targets, agents, accuracy, method="counts")
                profile_b = point_profile(targets, agents, accuracy, method="occupancy")
                for block_size, (discovery_a, discovery_b) in enumerate(
                    zip(profile_a, profile_b, strict=True), start=1
                ):
                    pooled_a = pooled_accuracy_counts(targets, block_size, accuracy)
                    pooled_b = pooled_accuracy_occupancy(targets, block_size, accuracy)
                    previous = profile_a[block_size - 2] if block_size > 1 else None
                    rows.append(
                        {
                            "targets": targets,
                            "agents": agents,
                            "accuracy": accuracy,
                            "block_size": block_size,
                            "pooled_accuracy": pooled_a,
                            "independent_pooled_accuracy": pooled_b,
                            "group_discovery": discovery_a,
                            "independent_group_discovery": discovery_b,
                            "increment": None if previous is None else discovery_a - previous,
                        }
                    )
    return rows


def channel_pooled_accuracy_labeled(channel: dict[str, Any], block_size: int) -> Fraction:
    value = Fraction()
    for observations in product(channel["signals"], repeat=block_size):
        value += max(
            channel["prior"][target]
            * _product(channel["law"][target][signal] for signal in observations)
            for target in channel["targets"]
        )
    return value


def channel_pooled_accuracy_histogram(channel: dict[str, Any], block_size: int) -> Fraction:
    value = Fraction()
    for counts in compositions(block_size, len(channel["signals"])):
        observations = tuple(
            signal
            for signal, count in zip(channel["signals"], counts, strict=True)
            for _ in range(count)
        )
        value += multinomial(counts) * max(
            channel["prior"][target]
            * _product(channel["law"][target][signal] for signal in observations)
            for target in channel["targets"]
        )
    return value


def channel_profiles(agents: int = 3) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for channel in channels():
        private = one_person_accuracy(channel)
        pooled_a = tuple(
            channel_pooled_accuracy_labeled(channel, block_size)
            for block_size in range(1, agents + 1)
        )
        pooled_b = tuple(
            channel_pooled_accuracy_histogram(channel, block_size)
            for block_size in range(1, agents + 1)
        )
        profile_a = tuple(
            group_discovery(value, private, agents, block_size)
            for block_size, value in enumerate(pooled_a, start=1)
        )
        profile_b = tuple(
            group_discovery(value, private, agents, block_size)
            for block_size, value in enumerate(pooled_b, start=1)
        )
        rows.append(
            {
                "channel_id": channel["channel_id"],
                "family": channel["family"],
                "one_person_accuracy": private,
                "pooled_accuracy": pooled_a,
                "independent_pooled_accuracy": pooled_b,
                "profile": profile_a,
                "independent_profile": profile_b,
                "increments": tuple(profile_a[i] - profile_a[i - 1] for i in range(1, agents)),
            }
        )
    return rows


def _product(values: Iterator[Fraction]) -> Fraction:
    out = Fraction(1)
    for value in values:
        out *= value
    return out
