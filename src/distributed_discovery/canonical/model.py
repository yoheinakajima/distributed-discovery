"""Independent finite-model calculations for the canonical box benchmark.

This module does not import or parse upstream code. It enumerates raw count
vectors and evaluates finite likelihood formulas directly.
"""

from __future__ import annotations

import math
from collections.abc import Iterator, Sequence
from fractions import Fraction


def blind_discovery(candidates: int, actions: int) -> Fraction:
    """Discovery under coordinated distinct blind actions."""
    if not 0 <= actions <= candidates:
        raise ValueError("actions must lie between zero and candidates")
    return Fraction(actions, candidates)


def private_discovery(searchers: int, accuracy: Fraction) -> Fraction:
    """Discovery when conditionally independent searchers follow their clues."""
    return 1 - (1 - accuracy) ** searchers


def private_expected_distinct(candidates: int, searchers: int, accuracy: Fraction) -> Fraction:
    """Expected number of distinct private clues conditional on one target."""
    error_probability = (1 - accuracy) / (candidates - 1)
    target_named = 1 - (1 - accuracy) ** searchers
    false_named = 1 - (1 - error_probability) ** searchers
    return target_named + (candidates - 1) * false_named


def posterior_from_counts(counts: Sequence[int], accuracy: Fraction) -> tuple[Fraction, ...]:
    """Posterior over a uniform target given independent symmetric clues."""
    candidates = len(counts)
    if candidates < 2 or any(count < 0 for count in counts):
        raise ValueError("counts must be nonnegative for at least two candidates")
    error_probability = (1 - accuracy) / (candidates - 1)
    weights = tuple(
        accuracy ** counts[target] * error_probability ** (sum(counts) - counts[target])
        for target in range(candidates)
    )
    total = sum(weights)
    if total == 0:
        raise ValueError("signal profile has zero probability")
    return tuple(weight / total for weight in weights)


def count_vectors(candidates: int, total: int) -> Iterator[tuple[int, ...]]:
    """Yield every labeled nonnegative count vector summing to total."""
    if candidates == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for remainder in count_vectors(candidates - 1, total - first):
            yield (first, *remainder)


def _multinomial_probability(counts: Sequence[int], probabilities: Sequence[float]) -> float:
    total = sum(counts)
    coefficient = math.factorial(total)
    for count in counts:
        coefficient //= math.factorial(count)
    value = float(coefficient)
    for count, probability in zip(counts, probabilities, strict=True):
        value *= probability**count
    return value


def independent_count_frontier(
    candidates: int, searchers: int, accuracy: float
) -> tuple[tuple[float, ...], float]:
    """Return the pooled top-L frontier and enumerated probability mass.

    Candidate zero is fixed as the true state by symmetry. At each cutoff,
    ties are broken uniformly. For accuracy above the false-clue probability,
    posterior order equals count order.
    """
    if not (0.0 < accuracy < 1.0):
        raise ValueError("accuracy must lie strictly between zero and one")
    false_probability = (1.0 - accuracy) / (candidates - 1)
    if accuracy <= false_probability:
        raise ValueError("this count-order evaluator requires informative clues")
    probabilities = (accuracy, *(false_probability for _ in range(candidates - 1)))
    terms: list[list[float]] = [[] for _ in range(min(searchers, candidates))]
    probability_terms: list[float] = []
    for counts in count_vectors(candidates, searchers):
        probability = _multinomial_probability(counts, probabilities)
        probability_terms.append(probability)
        target_count = counts[0]
        greater = sum(count > target_count for count in counts)
        equal = sum(count == target_count for count in counts)
        for budget, values in enumerate(terms, start=1):
            if greater >= budget:
                inclusion = 0.0
            elif greater + equal <= budget:
                inclusion = 1.0
            else:
                inclusion = (budget - greater) / equal
            values.append(probability * inclusion)
    return tuple(math.fsum(values) for values in terms), math.fsum(probability_terms)


def tiny_consensus_bruteforce(candidates: int, searchers: int, accuracy: Fraction) -> Fraction:
    """Brute-force all target and labeled signal profiles with exact rationals."""
    if candidates**searchers > 100_000:
        raise ValueError("tiny brute-force guardrail exceeded")
    false_probability = (1 - accuracy) / (candidates - 1)
    total = Fraction(0)
    profile_count = candidates**searchers
    for target in range(candidates):
        for encoded in range(profile_count):
            remainder = encoded
            counts = [0] * candidates
            probability = Fraction(1, candidates)
            for _ in range(searchers):
                signal = remainder % candidates
                remainder //= candidates
                counts[signal] += 1
                probability *= accuracy if signal == target else false_probability
            maximum = max(counts)
            winners = [index for index, count in enumerate(counts) if count == maximum]
            if target in winners:
                total += probability / len(winners)
    return total
