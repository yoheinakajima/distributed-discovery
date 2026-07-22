"""Labeled exact evaluator and analytic identities for DD-016."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator, Sequence
from fractions import Fraction
from math import comb, factorial, lcm
from typing import Any


def binomial_probability(trials: int, successes: int, probability: Fraction) -> Fraction:
    if not 0 <= successes <= trials:
        return Fraction(0)
    return (
        comb(trials, successes) * probability**successes * (1 - probability) ** (trials - successes)
    )


def binomial_tail(trials: int, probability: Fraction, threshold: int) -> Fraction:
    return sum(
        (binomial_probability(trials, k, probability) for k in range(threshold, trials + 1)),
        Fraction(0),
    )


def strategic_candidate_payoff(
    posterior: Fraction,
    agents: int,
    threshold: int,
    other_choice_probability: Fraction,
    prize: Fraction = Fraction(1),
) -> Fraction:
    """Expected equal-split payoff from one candidate action."""

    if agents < 1 or not 1 <= threshold <= agents:
        raise ValueError("agents and threshold are inconsistent")
    if not 0 <= other_choice_probability <= 1:
        raise ValueError("choice probability must lie in [0,1]")
    return (
        prize
        * posterior
        * sum(
            (
                binomial_probability(agents - 1, k, other_choice_probability) / (k + 1)
                for k in range(threshold - 1, agents)
            ),
            Fraction(0),
        )
    )


def split_prize_closed_form(agents: int, probability: Fraction) -> Fraction:
    """Ordinary threshold-one share factor, including its zero limit."""

    if probability == 0:
        return Fraction(1)
    return (1 - (1 - probability) ** agents) / (agents * probability)


def threshold_two_closed_form(agents: int, probability: Fraction) -> Fraction:
    """Threshold-two share factor, including its zero limit."""

    if probability == 0:
        return Fraction(0)
    return split_prize_closed_form(agents, probability) - (1 - probability) ** (agents - 1)


def planner_value(posterior: Sequence[Fraction], agents: int, threshold: int) -> Fraction:
    if agents < 1 or not 1 <= threshold <= agents:
        raise ValueError("agents and threshold are inconsistent")
    if any(value < 0 for value in posterior) or sum(posterior, Fraction(0)) != 1:
        raise ValueError("posterior must be a probability vector")
    teams = min(len(posterior), agents // threshold)
    return sum(sorted(posterior, reverse=True)[:teams], Fraction(0))


def occupancy_vectors(candidates: int, agents: int) -> Iterator[tuple[int, ...]]:
    if candidates == 1:
        yield (agents,)
        return
    for first in range(agents + 1):
        for remainder in occupancy_vectors(candidates - 1, agents - first):
            yield (first, *remainder)


def exhaustive_planner_value(
    posterior: Sequence[Fraction], agents: int, threshold: int
) -> Fraction:
    return max(
        sum(
            (posterior[index] for index, count in enumerate(occupancy) if count >= threshold),
            Fraction(0),
        )
        for occupancy in occupancy_vectors(len(posterior), agents)
    )


def _bounded_sequence_count(boxes: int, balls: int, maximum: int) -> int:
    """Labeled ball sequences whose occupancy in every box is at most maximum."""

    ways = [0] * (balls + 1)
    ways[0] = 1
    placed_boxes = 0
    for _ in range(boxes):
        updated = [0] * (balls + 1)
        for used, count in enumerate(ways):
            if not count:
                continue
            remaining = balls - used
            for addition in range(min(maximum, remaining) + 1):
                updated[used + addition] += count * comb(used + addition, addition)
        ways = updated
        placed_boxes += 1
    if placed_boxes != boxes:
        raise AssertionError("box recursion failed")
    return ways[balls]


def occupancy_statistics(modes: int, agents: int, threshold: int) -> dict[str, Fraction]:
    """Exact statistics for iid uniform allocation over a mode set."""

    if modes < 1:
        raise ValueError("a mode set must be nonempty")
    probability = Fraction(1, modes)
    one_box = [binomial_probability(agents, count, probability) for count in range(agents + 1)]
    distinct = modes * (1 - one_box[0])
    viable = modes * sum(one_box[threshold:], Fraction(0))
    failed_agents = modes * sum(
        (count * one_box[count] for count in range(1, threshold)), Fraction(0)
    )
    excess = modes * sum(
        ((count - threshold) * one_box[count] for count in range(threshold, agents + 1)),
        Fraction(0),
    )
    largest = sum(
        (
            1
            - Fraction(
                _bounded_sequence_count(modes, agents, level - 1),
                modes**agents,
            )
            for level in range(1, agents + 1)
        ),
        Fraction(0),
    )
    return {
        "expected_distinct_candidates": distinct,
        "expected_viable_candidates": viable,
        "failed_subthreshold_attempts": failed_agents,
        "necessary_overlap": viable * (threshold - 1),
        "excess_overlap": excess,
        "expected_largest_crowd": largest,
        "pair_collision": probability,
        "effective_team_count": Fraction(modes),
    }


def _probability_integers(candidates: int, agents: int, accuracy: Fraction) -> tuple[int, int, int]:
    wrong = (1 - accuracy) / (candidates - 1)
    base = lcm(accuracy.denominator, wrong.denominator)
    return int(accuracy * base), int(wrong * base), base**agents


def _cutoff_share(counts: Sequence[int], target: int, budget: int) -> Fraction:
    target_count = counts[target]
    greater = sum(count > target_count for index, count in enumerate(counts) if index != target)
    tied = 1 + sum(count == target_count for index, count in enumerate(counts) if index != target)
    if greater >= budget:
        return Fraction(0)
    return Fraction(min(tied, budget - greater), tied)


def _aggregate_categories(
    categories: dict[tuple[int, bool, tuple[Fraction, ...]], int],
    denominator: int,
    candidates: int,
    agents: int,
    accuracy: Fraction,
    thresholds: Sequence[int],
) -> dict[str, Any]:
    rows = []
    for threshold_index, threshold in enumerate(thresholds):
        totals: dict[str, Fraction] = defaultdict(Fraction)
        for (modes, target_is_mode, planner_shares), integer_weight in categories.items():
            signal_probability = Fraction(integer_weight, denominator)
            stats = occupancy_statistics(modes, agents, threshold)
            for name, value in stats.items():
                totals[name] += signal_probability * value
            mode_probability = Fraction(1, modes)
            target_at_least_one = (
                1 - (1 - mode_probability) ** agents if target_is_mode else Fraction(0)
            )
            target_exactly_one = (
                agents * mode_probability * (1 - mode_probability) ** (agents - 1)
                if target_is_mode
                else Fraction(0)
            )
            target_opens = (
                binomial_tail(agents, mode_probability, threshold)
                if target_is_mode
                else Fraction(0)
            )
            totals["common_deterministic_mode_discovery"] += signal_probability * (
                Fraction(1, modes) if target_is_mode else Fraction(0)
            )
            totals["tied_mode_mixed_discovery"] += signal_probability * target_opens
            totals["planner_discovery"] += signal_probability * planner_shares[threshold_index]
            totals["target_selected_at_least_one"] += signal_probability * target_at_least_one
            totals["target_selected_exactly_one"] += signal_probability * target_exactly_one
            totals["singleton_target_failure"] += signal_probability * (
                target_exactly_one if threshold > 1 else Fraction(0)
            )
            totals["posterior_mass_opened"] += signal_probability * target_opens
        private = binomial_tail(agents, accuracy, threshold)
        blind = Fraction(min(candidates, agents // threshold), candidates)
        common = totals["common_deterministic_mode_discovery"]
        mixed = totals["tied_mode_mixed_discovery"]
        planner = totals["planner_discovery"]
        rows.append(
            {
                "threshold": threshold,
                "private_clue_following": private,
                "blind_viable_team_allocation": blind,
                **dict(totals),
                "common_vs_private": "raises"
                if common > private
                else ("lowers" if common < private else "ties"),
                "tied_mode_vs_private": "raises"
                if mixed > private
                else ("lowers" if mixed < private else "ties"),
                "coordination_necessary_for_planner": planner > mixed,
                "only_one_viable_coalition_can_form": agents // threshold == 1,
                "diversification_dominates_common_mode": planner > common,
                "common_mode_has_excess_overlap": agents > threshold,
            }
        )
    return {"rows": rows, "signal_classes": len(categories)}


def labeled_canonical_evaluation(
    candidates: int,
    agents: int,
    accuracy: Fraction,
    thresholds: Sequence[int],
) -> dict[str, Any]:
    """Method A: all labeled clue-count vectors conditional on target zero."""

    p_num, q_num, denominator = _probability_integers(candidates, agents, accuracy)
    factorials = tuple(factorial(index) for index in range(agents + 1))
    categories: dict[tuple[int, bool, tuple[Fraction, ...]], int] = defaultdict(int)
    counts = [0] * candidates
    state_count = 0
    mass = 0

    def visit(index: int, remaining: int) -> None:
        nonlocal state_count, mass
        if index == candidates - 1:
            counts[index] = remaining
            coefficient = factorials[agents]
            for count in counts:
                coefficient //= factorials[count]
            weight = coefficient * p_num ** counts[0] * q_num ** (agents - counts[0])
            maximum = max(counts)
            modes = sum(count == maximum for count in counts)
            target_is_mode = counts[0] == maximum
            shares = tuple(
                _cutoff_share(counts, 0, min(candidates, agents // threshold))
                for threshold in thresholds
            )
            categories[(modes, target_is_mode, shares)] += weight
            state_count += 1
            mass += weight
            return
        for count in range(remaining + 1):
            counts[index] = count
            visit(index + 1, remaining - count)

    visit(0, agents)
    result = _aggregate_categories(
        categories, denominator, candidates, agents, accuracy, thresholds
    )
    return {
        "method": "labeled-count-vectors",
        "state_count": state_count,
        "probability_mass": Fraction(mass, denominator),
        **result,
    }
