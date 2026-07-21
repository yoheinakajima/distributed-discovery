"""Independent policy-table verifier for DD-014."""

from __future__ import annotations

import copy
from fractions import Fraction
from itertools import product
from typing import Any

from distributed_discovery.conditional.model import POLICY_TYPES, anonymous_profiles


def _probability(signal: int, target: int, accuracy: Fraction, labels: int) -> Fraction:
    if signal == target:
        return accuracy
    return (1 - accuracy) / (labels - 1)


def policy_tables() -> dict[str, tuple[int, ...]]:
    tables: dict[str, list[int]] = {policy: [] for policy in POLICY_TYPES}
    for private in range(3):
        for shared in range(3):
            tables["private-dominant"].append(private)
            tables["public-dominant"].append(shared)
            tables["contrarian"].append(private if private == shared else 3 - private - shared)
    return {policy: tuple(actions) for policy, actions in tables.items()}


def direct_profile(counts: tuple[int, int, int], p: Fraction, q: Fraction) -> dict[str, Any]:
    tables = policy_tables()
    policies = [
        *([POLICY_TYPES[0]] * counts[0]),
        *([POLICY_TYPES[1]] * counts[1]),
        *([POLICY_TYPES[2]] * counts[2]),
    ]
    n = len(policies)
    mass = discovery = quality = distinct = Fraction()
    payoffs = [Fraction() for _ in policies]
    for target, shared, *private_signals in product(range(3), repeat=n + 2):
        probability = Fraction(1, 3) * _probability(shared, target, q, 3)
        for signal in private_signals:
            probability *= _probability(signal, target, p, 3)
        actions = [
            tables[policy][3 * private + shared]
            for policy, private in zip(policies, private_signals, strict=True)
        ]
        winners = [action == target for action in actions]
        winner_count = sum(winners)
        mass += probability
        discovery += probability * (winner_count > 0)
        quality += probability * Fraction(winner_count, n)
        distinct += probability * len(set(actions))
        for index, winner in enumerate(winners):
            if winner:
                payoffs[index] += probability / winner_count
    type_payoffs: dict[str, Fraction | None] = {}
    offset = 0
    for policy, count in zip(POLICY_TYPES, counts, strict=True):
        type_payoffs[policy] = None if count == 0 else payoffs[offset]
        offset += count
    return {
        "probability_mass": mass,
        "discovery": discovery,
        "action_quality": quality,
        "expected_distinct_actions": distinct,
        "payoffs": type_payoffs,
    }


def _raw_table(policy_id: int) -> tuple[int, ...]:
    return tuple((policy_id >> observation) & 1 for observation in range(4))


def direct_raw(policies: tuple[int, int], p: Fraction, q: Fraction) -> dict[str, Any]:
    tables = [_raw_table(policy) for policy in policies]
    mass = discovery = Fraction()
    payoffs = [Fraction(), Fraction()]
    for target, shared, private_a, private_b in product(range(2), repeat=4):
        probability = Fraction(1, 2) * _probability(shared, target, q, 2)
        probability *= _probability(private_a, target, p, 2)
        probability *= _probability(private_b, target, p, 2)
        actions = [tables[0][2 * private_a + shared], tables[1][2 * private_b + shared]]
        winners = [action == target for action in actions]
        winner_count = sum(winners)
        mass += probability
        discovery += probability * (winner_count > 0)
        for index, winner in enumerate(winners):
            if winner:
                payoffs[index] += probability / winner_count
    return {"probability_mass": mass, "discovery": discovery, "payoffs": payoffs}


def _equilibrium_flags(
    profiles: dict[tuple[int, int, int], dict[str, Any]], counts: tuple[int, int, int]
) -> tuple[bool, bool]:
    weak = strict = True
    for source, count in enumerate(counts):
        if count == 0:
            continue
        current = profiles[counts]["payoffs"][POLICY_TYPES[source]]
        assert current is not None
        for target in range(3):
            if target == source:
                continue
            changed = list(counts)
            changed[source] -= 1
            changed[target] += 1
            changed_key = (changed[0], changed[1], changed[2])
            deviating = profiles[changed_key]["payoffs"][POLICY_TYPES[target]]
            assert deviating is not None
            weak = weak and current >= deviating
            strict = strict and current > deviating
    return weak, strict


def _verify_cell(cell: dict[str, Any]) -> int:
    n = int(cell["agents"])
    p, q = Fraction(cell["private_accuracy"]), Fraction(cell["shared_accuracy"])
    profiles = {counts: direct_profile(counts, p, q) for counts in anonymous_profiles(n)}
    recorded = {
        (
            row["counts"][POLICY_TYPES[0]],
            row["counts"][POLICY_TYPES[1]],
            row["counts"][POLICY_TYPES[2]],
        ): row
        for row in cell["profiles"]
    }
    for counts, direct in profiles.items():
        row = recorded[counts]
        for key in ("probability_mass", "discovery", "action_quality", "expected_distinct_actions"):
            if row[key] != str(direct[key]):
                raise ValueError(f"conditional metric corruption: {key}")
        for policy in POLICY_TYPES:
            expected = direct["payoffs"][policy]
            expected_text = None if expected is None else str(expected)
            if row["payoffs"][policy] != expected_text:
                raise ValueError("conditional payoff corruption")
        weak, strict = _equilibrium_flags(profiles, counts)
        if row["weak_equilibrium"] != weak or row["strict_equilibrium"] != strict:
            raise ValueError("conditional equilibrium corruption")
    best = max(row["discovery"] for row in profiles.values())
    planner = sorted([list(counts) for counts, row in profiles.items() if row["discovery"] == best])
    if cell["planner_profiles"] != planner:
        raise ValueError("conditional planner corruption")
    return sum(9 * 3**n for _ in profiles)


def _verify_raw_cell(cell: dict[str, Any]) -> int:
    p, q = Fraction(cell["private_accuracy"]), Fraction(cell["shared_accuracy"])
    profiles = {
        (first, second): direct_raw((first, second), p, q)
        for first in range(16)
        for second in range(16)
    }
    optimum = max(row["discovery"] for row in profiles.values())
    equilibria: list[list[int]] = []
    for policies, row in profiles.items():
        weak = True
        for role in range(2):
            for deviation in range(16):
                changed = list(policies)
                changed[role] = deviation
                weak = (
                    weak
                    and row["payoffs"][role] >= profiles[(changed[0], changed[1])]["payoffs"][role]
                )
        if weak:
            equilibria.append(list(policies))
    equilibrium_best = max(profiles[(item[0], item[1])]["discovery"] for item in equilibria)
    if cell["raw_optimum_discovery"] != str(optimum):
        raise ValueError("raw optimum corruption")
    if cell["raw_best_equilibrium_discovery"] != str(equilibrium_best):
        raise ValueError("raw equilibrium corruption")
    if cell["raw_equilibrium_profiles"] != sorted(equilibria):
        raise ValueError("raw equilibrium-profile corruption")
    return 256 * 16


def verify_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    main_states = sum(_verify_cell(cell) for cell in bundle["cells"])
    raw_states = sum(_verify_raw_cell(cell) for cell in bundle["raw_audit"])
    return {
        "passed": True,
        "main_cells_verified": len(bundle["cells"]),
        "main_profiles_verified": sum(len(cell["profiles"]) for cell in bundle["cells"]),
        "main_labeled_states": main_states,
        "raw_cells_verified": len(bundle["raw_audit"]),
        "raw_ordered_profiles_verified": 256 * len(bundle["raw_audit"]),
        "raw_labeled_states": raw_states,
    }


def corruption_tests(bundle: dict[str, Any]) -> dict[str, bool]:
    mutations: list[tuple[str, dict[str, Any]]] = []
    discovery = copy.deepcopy(bundle["cells"][0])
    discovery["profiles"][0]["discovery"] = "0"
    mutations.append(("main", discovery))
    payoff = copy.deepcopy(bundle["cells"][0])
    present = next(policy for policy, count in payoff["profiles"][0]["counts"].items() if count)
    payoff["profiles"][0]["payoffs"][present] = "0"
    mutations.append(("main", payoff))
    equilibrium = copy.deepcopy(bundle["cells"][0])
    equilibrium["profiles"][0]["weak_equilibrium"] = not equilibrium["profiles"][0][
        "weak_equilibrium"
    ]
    mutations.append(("main", equilibrium))
    raw = copy.deepcopy(bundle["raw_audit"][0])
    raw["raw_optimum_discovery"] = "0"
    mutations.append(("raw", raw))
    rejected: list[bool] = []
    for kind, mutation in mutations:
        try:
            _verify_cell(mutation) if kind == "main" else _verify_raw_cell(mutation)
        except ValueError:
            rejected.append(True)
        else:
            rejected.append(False)
    return {
        "altered_discovery_rejected": rejected[0],
        "altered_payoff_rejected": rejected[1],
        "altered_equilibrium_rejected": rejected[2],
        "altered_raw_optimum_rejected": rejected[3],
    }
