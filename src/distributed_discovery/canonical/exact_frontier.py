"""Exact pooled-posterior frontiers from two finite state representations."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, factorial, lcm


@dataclass(frozen=True)
class ExactFrontier:
    """Exact frontier and normalization from one exhaustive representation."""

    values: tuple[Fraction, ...]
    probability_mass: Fraction
    state_count: int


def _probability_integers(
    candidates: int, reports: int, accuracy: Fraction
) -> tuple[int, int, int]:
    if candidates < 2 or reports < 1:
        raise ValueError("candidates must be at least two and reports positive")
    if not Fraction(1, candidates) < accuracy <= 1:
        raise ValueError("count ranking requires accuracy above the uninformative level")
    false_accuracy = (1 - accuracy) / (candidates - 1)
    base = lcm(accuracy.denominator, false_accuracy.denominator)
    return int(accuracy * base), int(false_accuracy * base), base**reports


def _cutoff_share(counts: tuple[int, ...], target: int, budget: int) -> Fraction:
    target_count = counts[target]
    strictly_above = sum(
        count > target_count for index, count in enumerate(counts) if index != target
    )
    tied = 1 + sum(count == target_count for index, count in enumerate(counts) if index != target)
    if strictly_above >= budget:
        return Fraction(0)
    return Fraction(min(tied, budget - strictly_above), tied)


def labeled_count_frontier(candidates: int, reports: int, accuracy: Fraction) -> ExactFrontier:
    """Enumerate all labeled weak compositions of reports across candidates.

    The target is fixed at label zero by symmetry. Each count vector receives its
    exact conditional multinomial probability. A target tied at the top-L cutoff
    is included by its uniform share of the remaining cutoff slots.
    """

    p_num, q_num, probability_denominator = _probability_integers(candidates, reports, accuracy)
    cutoff_scale = lcm(*range(1, candidates + 1))
    factorials = tuple(factorial(index) for index in range(candidates + reports + 1))
    totals = [0] * reports
    mass_numerator = 0
    state_count = 0
    counts = [0] * candidates

    def visit(index: int, remaining: int) -> None:
        nonlocal mass_numerator, state_count
        if index == candidates - 1:
            counts[index] = remaining
            coefficient = factorials[reports]
            for count in counts:
                coefficient //= factorials[count]
            weight = coefficient * p_num ** counts[0] * q_num ** (reports - counts[0])
            mass_numerator += weight
            state_count += 1
            frozen = tuple(counts)
            for budget in range(1, reports + 1):
                share = _cutoff_share(frozen, 0, budget)
                totals[budget - 1] += weight * share.numerator * (cutoff_scale // share.denominator)
            return
        for count in range(remaining + 1):
            counts[index] = count
            visit(index + 1, remaining - count)

    visit(0, reports)
    denominator = probability_denominator * cutoff_scale
    return ExactFrontier(
        values=tuple(Fraction(total, denominator) for total in totals),
        probability_mass=Fraction(mass_numerator, probability_denominator),
        state_count=state_count,
    )


def histogram_orbit_frontier(candidates: int, reports: int, accuracy: Fraction) -> ExactFrontier:
    """Independently aggregate false-label counts into occupancy histograms.

    For target count k, h_j is the number of false labels occurring j times.
    Multiplicity combines assignments of occupancies to false labels and report
    sequences realizing the resulting count vector.
    """

    p_num, q_num, probability_denominator = _probability_integers(candidates, reports, accuracy)
    cutoff_scale = lcm(*range(1, candidates + 1))
    factorials = tuple(factorial(index) for index in range(candidates + reports + 1))
    totals = [0] * reports
    mass_numerator = 0
    state_count = 0

    def enumerate_target_count(target_count: int) -> None:
        false_reports = reports - target_count
        histogram = [0] * (reports + 1)

        def visit(occupancy: int, remaining: int, used_labels: int) -> None:
            nonlocal mass_numerator, state_count
            if occupancy > false_reports:
                if remaining:
                    return
                histogram[0] = candidates - 1 - used_labels
                numerator = factorials[reports] * factorials[candidates - 1]
                denominator = factorials[target_count]
                for count, label_count in enumerate(histogram):
                    denominator *= factorials[count] ** label_count
                    denominator *= factorials[label_count]
                if numerator % denominator:
                    raise ArithmeticError("orbit multiplicity is not integral")
                multiplicity = numerator // denominator
                weight = multiplicity * p_num**target_count * q_num**false_reports
                mass_numerator += weight
                state_count += 1
                strictly_above = sum(
                    histogram[count] for count in range(target_count + 1, reports + 1)
                )
                tied = histogram[target_count] + 1
                for budget in range(1, reports + 1):
                    if strictly_above >= budget:
                        continue
                    included = min(tied, budget - strictly_above)
                    totals[budget - 1] += weight * included * (cutoff_scale // tied)
                return
            max_count = min(remaining // occupancy, candidates - 1 - used_labels)
            for label_count in range(max_count + 1):
                histogram[occupancy] = label_count
                visit(
                    occupancy + 1,
                    remaining - occupancy * label_count,
                    used_labels + label_count,
                )
            histogram[occupancy] = 0

        visit(1, false_reports, 0)

    for target_count in range(reports + 1):
        enumerate_target_count(target_count)

    denominator = probability_denominator * cutoff_scale
    return ExactFrontier(
        values=tuple(Fraction(total, denominator) for total in totals),
        probability_mass=Fraction(mass_numerator, probability_denominator),
        state_count=state_count,
    )


def expected_labeled_count_vectors(candidates: int, reports: int) -> int:
    """Number of weak compositions of reports into labeled candidates."""

    return comb(candidates + reports - 1, candidates - 1)
