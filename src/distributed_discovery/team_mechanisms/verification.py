"""Independent finite-table verification and corruption gates for DD-018."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from itertools import combinations, product
from typing import Any

from distributed_discovery.team_mechanisms.model import (
    MECHANISMS,
    agent_utility,
    discovery,
    exhaustive_planner_check,
    is_committed,
    occupancy,
    planner_profile,
    recommendation_support,
)
from distributed_discovery.threshold_discovery.model import planner_value


def _replace(
    profile: tuple[int, ...], members: tuple[int, ...], actions: tuple[int, ...]
) -> tuple[int, ...]:
    values = list(profile)
    for member, action in zip(members, actions, strict=True):
        values[member] = action
    return tuple(values)


def _independent_stability(
    mechanism: str,
    posterior: tuple[Fraction, ...],
    profile: tuple[int, ...],
    coalition_size: int,
    threshold: int,
    assignment: tuple[int, ...],
) -> bool:
    coalitions = (
        ((0, 1), (2, 3))
        if mechanism == "pairwise-matching-market" and coalition_size == 2
        else tuple(combinations(range(len(profile)), coalition_size))
    )
    for members in coalitions:
        before = tuple(
            agent_utility(mechanism, posterior, profile, member, threshold, assignment)
            for member in members
        )
        for actions in product(range(len(posterior)), repeat=coalition_size):
            if all(
                profile[member] == action for member, action in zip(members, actions, strict=True)
            ):
                continue
            changed = _replace(profile, members, actions)
            after = tuple(
                agent_utility(mechanism, posterior, changed, member, threshold, assignment)
                for member in members
            )
            if all(candidate > baseline for baseline, candidate in zip(before, after, strict=True)):
                return False
    return True


def _independent_equilibrium_count(
    mechanism: str,
    posterior: tuple[Fraction, ...],
    agents: int,
    threshold: int,
    assignment: tuple[int, ...],
) -> int | str:
    if is_committed(mechanism):
        return "not-applicable-authoritative-commitment"
    if mechanism == "pairwise-matching-market":
        return sum(
            _independent_stability(
                mechanism,
                posterior,
                (left, left, right, right),
                2,
                threshold,
                assignment,
            )
            for left, right in product(range(len(posterior)), repeat=2)
        )
    count = 0
    for profile in product(range(len(posterior)), repeat=agents):
        if _independent_stability(mechanism, posterior, profile, 1, threshold, assignment):
            count += 1
    return count


def independent_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    agents = int(config["agents"])
    threshold = int(config["threshold"])
    rows = []
    for fixture in config["posterior_fixtures"]:
        posterior = tuple(Fraction(value) for value in fixture["posterior"])
        assignment = planner_profile(posterior, agents, threshold)
        for spec in MECHANISMS:
            support = recommendation_support(spec.name, posterior, agents, threshold)
            expected = sum(
                (
                    probability * discovery(profile, posterior, threshold)
                    for probability, profile in support
                ),
                Fraction(),
            )
            if is_committed(spec.name):
                unilateral: bool | str = "not-applicable-authoritative-commitment"
                pair: bool | str = "not-applicable-authoritative-commitment"
                tau: bool | str = "not-applicable-authoritative-commitment"
            elif spec.name == "pairwise-matching-market":
                unilateral = "not-applicable-binding-within-pair"
                pair = all(
                    _independent_stability(spec.name, posterior, profile, 2, threshold, assignment)
                    for _, profile in support
                )
                tau = pair
            else:
                unilateral = all(
                    _independent_stability(spec.name, posterior, profile, 1, threshold, assignment)
                    for _, profile in support
                )
                pair = all(
                    _independent_stability(spec.name, posterior, profile, 2, threshold, assignment)
                    for _, profile in support
                )
                tau = all(
                    _independent_stability(
                        spec.name, posterior, profile, threshold, threshold, assignment
                    )
                    for _, profile in support
                )
            rows.append(
                {
                    "fixture": fixture["name"],
                    "name": spec.name,
                    "support_mass": sum((probability for probability, _ in support), Fraction()),
                    "support_occupancies": tuple(
                        occupancy(profile, len(posterior)) for _, profile in support
                    ),
                    "expected_discovery": expected,
                    "planner_discovery": exhaustive_planner_check(posterior, agents, threshold),
                    "obedience": unilateral,
                    "pairwise_strict_stable": pair,
                    "tau_player_strict_stable": tau,
                    "equilibrium_multiplicity": _independent_equilibrium_count(
                        spec.name, posterior, agents, threshold, assignment
                    ),
                }
            )
    return rows


def verify_registry(registry: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    expected_rows = independent_rows(config)
    primary = {(row["fixture"], row["name"]): row for row in registry["rows"]}
    errors = []
    if registry["mechanism_count"] != len(MECHANISMS):
        errors.append("mechanism count mismatch")
    if registry["mechanism_fixture_rows"] != len(expected_rows):
        errors.append("mechanism-fixture row count mismatch")
    if registry["labeled_action_profiles_per_fixture"] != int(
        config["labeled_action_profiles_per_fixture"]
    ):
        errors.append("labeled action-profile count mismatch")
    for row in expected_rows:
        key = (row["fixture"], row["name"])
        candidate = primary.get(key)
        if candidate is None:
            errors.append(f"missing row {key}")
            continue
        if row["support_mass"] != 1:
            errors.append(f"support does not normalize {key}")
        for field in (
            "expected_discovery",
            "planner_discovery",
            "obedience",
            "pairwise_strict_stable",
            "tau_player_strict_stable",
            "equilibrium_multiplicity",
        ):
            if candidate[field] != row[field]:
                errors.append(f"independent mismatch {key} {field}")
        if not candidate["weak_budget_balance"] or candidate["external_subsidy"] != 0:
            errors.append(f"budget/subsidy failure {key}")
        if candidate["report_truthfulness"] != "not-applicable-common-posterior-input":
            errors.append(f"truthfulness boundary missing {key}")
    for fixture in config["posterior_fixtures"]:
        posterior = tuple(Fraction(value) for value in fixture["posterior"])
        if planner_value(
            posterior, int(config["agents"]), int(config["threshold"])
        ) != exhaustive_planner_check(posterior, int(config["agents"]), int(config["threshold"])):
            errors.append(f"planner exhaustive mismatch {fixture['name']}")
    return {
        "passed": not errors,
        "errors": errors,
        "independent_rows": len(expected_rows),
        "independent_action_table_entries": len(expected_rows)
        * int(config["labeled_action_profiles_per_fixture"]),
        "planner_exhaustive_fixtures": len(config["posterior_fixtures"]),
    }


def corruption_tests(registry: dict[str, Any], config: dict[str, Any]) -> dict[str, bool]:
    tests = {}
    corrupt = deepcopy(registry)
    corrupt["rows"][0]["expected_discovery"] += Fraction(1, 10**6)
    tests["altered_discovery_rejected"] = not verify_registry(corrupt, config)["passed"]

    corrupt = deepcopy(registry)
    corrupt["rows"][2]["equilibrium_multiplicity"] += 1
    tests["altered_equilibrium_count_rejected"] = not verify_registry(corrupt, config)["passed"]

    corrupt = deepcopy(registry)
    corrupt["rows"][3]["weak_budget_balance"] = False
    tests["altered_budget_record_rejected"] = not verify_registry(corrupt, config)["passed"]

    corrupt = deepcopy(registry)
    corrupt["mechanism_count"] -= 1
    tests["missing_mechanism_rejected"] = not verify_registry(corrupt, config)["passed"]
    return tests
