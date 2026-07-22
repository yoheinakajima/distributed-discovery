"""Independent histogram evaluator and corruption checks for DD-016."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from math import factorial
from typing import Any

from distributed_discovery.threshold_discovery.model import (
    _aggregate_categories,
    _probability_integers,
    exhaustive_planner_value,
    planner_value,
    split_prize_closed_form,
    strategic_candidate_payoff,
    threshold_two_closed_form,
)


def histogram_canonical_evaluation(
    candidates: int,
    agents: int,
    accuracy: Fraction,
    thresholds: list[int],
) -> dict[str, Any]:
    """Method B: false-label occupancy histograms conditional on target zero."""

    p_num, q_num, probability_denominator = _probability_integers(candidates, agents, accuracy)
    factorials = tuple(factorial(index) for index in range(candidates + agents + 1))
    categories: dict[tuple[int, bool, tuple[Fraction, ...]], int] = {}
    mass = 0
    orbit_count = 0

    for target_count in range(agents + 1):
        false_reports = agents - target_count
        histogram = [0] * (agents + 1)

        def visit(
            occupancy: int,
            remaining: int,
            used_labels: int,
            fixed_target_count: int,
            fixed_false_reports: int,
            fixed_histogram: list[int],
        ) -> None:
            nonlocal mass, orbit_count
            if occupancy > fixed_false_reports:
                if remaining:
                    return
                fixed_histogram[0] = candidates - 1 - used_labels
                numerator = factorials[agents] * factorials[candidates - 1]
                divisor = factorials[fixed_target_count]
                for count, label_count in enumerate(fixed_histogram):
                    divisor *= factorials[count] ** label_count
                    divisor *= factorials[label_count]
                if numerator % divisor:
                    raise ArithmeticError("histogram orbit multiplicity is not integral")
                multiplicity = numerator // divisor
                weight = multiplicity * p_num**fixed_target_count * q_num**fixed_false_reports
                false_maximum = max(
                    (count for count, number in enumerate(fixed_histogram) if number),
                    default=0,
                )
                maximum = max(fixed_target_count, false_maximum)
                target_is_mode = fixed_target_count == maximum
                modes = fixed_histogram[maximum] + int(target_is_mode)
                shares = []
                for threshold in thresholds:
                    budget = min(candidates, agents // threshold)
                    greater = sum(
                        fixed_histogram[count]
                        for count in range(fixed_target_count + 1, agents + 1)
                    )
                    tied = fixed_histogram[fixed_target_count] + 1
                    if greater >= budget:
                        share = Fraction(0)
                    else:
                        share = Fraction(min(tied, budget - greater), tied)
                    shares.append(share)
                key = (modes, target_is_mode, tuple(shares))
                categories[key] = categories.get(key, 0) + weight
                mass += weight
                orbit_count += 1
                return
            maximum_labels = min(remaining // occupancy, candidates - 1 - used_labels)
            for label_count in range(maximum_labels + 1):
                fixed_histogram[occupancy] = label_count
                visit(
                    occupancy + 1,
                    remaining - occupancy * label_count,
                    used_labels + label_count,
                    fixed_target_count,
                    fixed_false_reports,
                    fixed_histogram,
                )
            fixed_histogram[occupancy] = 0

        visit(1, false_reports, 0, target_count, false_reports, histogram)

    result = _aggregate_categories(
        categories,
        probability_denominator,
        candidates,
        agents,
        accuracy,
        thresholds,
    )
    return {
        "method": "false-label-occupancy-histograms",
        "state_count": orbit_count,
        "probability_mass": Fraction(mass, probability_denominator),
        **result,
    }


def planner_audit() -> dict[str, Any]:
    posterior_fixtures = [
        (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
        (Fraction(8, 15), Fraction(4, 15), Fraction(2, 15), Fraction(1, 15)),
        (Fraction(1, 4),) * 4,
    ]
    rows = []
    for posterior in posterior_fixtures:
        for agents in range(1, 7):
            for threshold in range(1, agents + 1):
                formula = planner_value(posterior, agents, threshold)
                exhaustive = exhaustive_planner_value(posterior, agents, threshold)
                rows.append(
                    {
                        "posterior": posterior,
                        "agents": agents,
                        "threshold": threshold,
                        "formula": formula,
                        "exhaustive": exhaustive,
                        "agrees": formula == exhaustive,
                    }
                )
    return {"rows": rows, "passed": all(row["agrees"] for row in rows)}


def strategic_payoff_audit() -> dict[str, Any]:
    rows = []
    for agents in range(2, 9):
        for probability in (
            Fraction(0),
            Fraction(1, 8),
            Fraction(1, 3),
            Fraction(1, 2),
            Fraction(1),
        ):
            tau_one = strategic_candidate_payoff(Fraction(1), agents, 1, probability)
            tau_two = strategic_candidate_payoff(Fraction(1), agents, 2, probability)
            rows.append(
                {
                    "agents": agents,
                    "probability": probability,
                    "tau_one_sum": tau_one,
                    "tau_one_closed": split_prize_closed_form(agents, probability),
                    "tau_two_sum": tau_two,
                    "tau_two_closed": threshold_two_closed_form(agents, probability),
                    "agrees": tau_one == split_prize_closed_form(agents, probability)
                    and tau_two == threshold_two_closed_form(agents, probability),
                }
            )
    return {
        "rows": rows,
        "tau_two_zero_limit": threshold_two_closed_form(8, Fraction(0)),
        "tau_one_zero_limit": split_prize_closed_form(8, Fraction(0)),
        "passed": all(row["agrees"] for row in rows),
    }


def verify_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    method_a = bundle["method_a"]
    method_b = bundle["method_b"]
    errors = []
    if method_a["probability_mass"] != 1 or method_b["probability_mass"] != 1:
        errors.append("probability mass does not normalize")
    if method_a["state_count"] != bundle["config"]["labeled_count_vectors"]:
        errors.append("labeled count-vector count mismatch")
    if method_a["rows"] != method_b["rows"]:
        errors.append("exact method rows differ")
    if method_a["signal_classes"] != method_b["signal_classes"]:
        errors.append("aggregated mode classes differ")
    for row in method_a["rows"]:
        if row["posterior_mass_opened"] != row["tied_mode_mixed_discovery"]:
            errors.append("posterior-mass accounting differs from target discovery")
        if not (0 <= row["tied_mode_mixed_discovery"] <= row["planner_discovery"] <= 1):
            errors.append("discovery bounds fail")
        viable_team_bound = Fraction(int(bundle["config"]["agents"]), int(row["threshold"]))
        if row["expected_viable_candidates"] > viable_team_bound:
            errors.append("viable-team bound fails")
    if not bundle["planner_audit"]["passed"]:
        errors.append("planner theorem audit failed")
    if not bundle["strategic_payoff_audit"]["passed"]:
        errors.append("strategic payoff identity audit failed")
    return {
        "passed": not errors,
        "errors": errors,
        "labeled_rows_equal_histogram_rows": method_a["rows"] == method_b["rows"],
        "planner_audit_rows": len(bundle["planner_audit"]["rows"]),
        "strategic_payoff_rows": len(bundle["strategic_payoff_audit"]["rows"]),
    }


def corruption_tests(bundle: dict[str, Any]) -> dict[str, bool]:
    tests = {}
    corrupt = deepcopy(bundle)
    corrupt["method_a"]["probability_mass"] += Fraction(1, 10**9)
    tests["altered_posterior_weight_rejected"] = not verify_bundle(corrupt)["passed"]

    corrupt = deepcopy(bundle)
    corrupt["method_a"]["rows"][1]["expected_viable_candidates"] += Fraction(1, 10**9)
    tests["altered_occupancy_probability_rejected"] = not verify_bundle(corrupt)["passed"]

    corrupt = deepcopy(bundle)
    corrupt["method_a"]["signal_classes"] += 1
    tests["altered_mode_count_rejected"] = not verify_bundle(corrupt)["passed"]

    corrupt = deepcopy(bundle)
    corrupt["method_a"]["rows"][1]["planner_discovery"] += Fraction(1, 10**9)
    tests["altered_planner_mass_rejected"] = not verify_bundle(corrupt)["passed"]
    return tests
