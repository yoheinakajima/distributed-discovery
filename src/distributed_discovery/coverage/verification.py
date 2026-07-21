"""Independent bit-mask verifier for DD-005 frontiers."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations


def verify_exact(
    weights: tuple[Fraction, ...], actions: tuple[frozenset[int], ...], budget: int
) -> tuple[tuple[int, ...], Fraction]:
    masks = [sum(1 << item for item in action) for action in actions]

    def score(mask: int) -> Fraction:
        return sum(
            (weight for item, weight in enumerate(weights) if mask & (1 << item)), Fraction(0)
        )

    results = []
    for choice in combinations(range(len(actions)), budget):
        mask = 0
        for index in choice:
            mask |= masks[index]
        results.append((choice, score(mask)))
    return max(results, key=lambda item: (item[1], tuple(-index for index in item[0])))
