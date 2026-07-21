"""Materially separate labeled-state verifier for DD-012."""

from __future__ import annotations

import copy
from fractions import Fraction
from itertools import product
from typing import Any

from distributed_discovery.attention.model import (
    STRATEGIC_REWARD_RULES,
    equilibrium,
    reward_equilibrium,
)


def _signal_probability(signal: int, target: int, accuracy: Fraction) -> Fraction:
    return accuracy if signal == target else (1 - accuracy) / 2


def direct_profile(n: int, k: int, p: Fraction, q: Fraction) -> dict[str, Any]:
    """Enumerate target, shared signal, and every action-relevant private signal."""
    probability_mass = Fraction()
    discovery = Fraction()
    payoffs = {rule: [Fraction() for _ in range(n)] for rule in STRATEGIC_REWARD_RULES}
    budgets = {rule: Fraction() for rule in STRATEGIC_REWARD_RULES}
    for target in range(3):
        for shared in range(3):
            for private in product(range(3), repeat=n - k):
                probability = Fraction(1, 3) * _signal_probability(shared, target, q)
                for signal in private:
                    probability *= _signal_probability(signal, target, p)
                probability_mass += probability
                actions = [shared] * k + list(private)
                winners = [action == target for action in actions]
                winner_count = sum(winners)
                discovered = winner_count > 0
                discovery += probability * discovered

                equal = [
                    Fraction(1, winner_count) if winner and winner_count else Fraction()
                    for winner in winners
                ]
                sole = [Fraction(int(winner and winner_count == 1)) for winner in winners]
                off_shared = [
                    Fraction(int(winner and action != shared))
                    for action, winner in zip(actions, winners, strict=True)
                ]
                assigned = [
                    value + (Fraction(1, n) if index < k and action == shared else 0)
                    for index, (action, value) in enumerate(zip(actions, equal, strict=True))
                ]
                pooled = [Fraction(int(discovered), n) for _ in range(n)]
                realized = {
                    "equal-split": equal,
                    "sole-rescue": sole,
                    "off-shared-success": off_shared,
                    "marginal-coverage": sole,
                    "assigned-reader-reward": assigned,
                    "universal-pooling": pooled,
                }
                for rule, values in realized.items():
                    budgets[rule] += probability * sum(values)
                    for index, value in enumerate(values):
                        payoffs[rule][index] += probability * value
    if probability_mass != 1:
        raise ValueError("direct state probabilities do not normalize")
    result: dict[str, Any] = {
        "probability_mass": probability_mass,
        "discovery": discovery,
        "rules": {},
    }
    for rule in STRATEGIC_REWARD_RULES:
        result["rules"][rule] = {
            "attending": None if k == 0 else payoffs[rule][0],
            "ignoring": None if k == n else payoffs[rule][k],
            "budget": budgets[rule],
        }
    return result


def verify_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    verified_profiles = 0
    verified_reward_rows = 0
    for cell in bundle["cells"]:
        n = int(cell["agents"])
        p = Fraction(cell["private_accuracy"])
        q = Fraction(cell["shared_accuracy"])
        direct_rows: list[dict[str, Any]] = []
        for profile in cell["profiles"]:
            k = int(profile["attenders"])
            direct = direct_profile(n, k, p, q)
            direct_rows.append(direct)
            if str(direct["probability_mass"]) != profile["probability_mass"]:
                raise ValueError("probability normalization mismatch")
            if str(direct["discovery"]) != profile["discovery"]:
                raise ValueError("discovery corruption or evaluator mismatch")
            expected_weak, expected_strict = equilibrium(n, k, p, q)
            if (
                profile["weak_equilibrium"] != expected_weak
                or profile["strict_equilibrium"] != expected_strict
            ):
                raise ValueError("equal-split equilibrium mismatch")
            for rule in STRATEGIC_REWARD_RULES:
                direct_rule = direct["rules"][rule]
                recorded = profile["rewards"][rule]
                for key in ("attending", "ignoring", "budget"):
                    expected = None if direct_rule[key] is None else str(direct_rule[key])
                    if recorded[key] != expected:
                        raise ValueError(f"reward accounting mismatch: {rule}/{key}")
                verified_reward_rows += 1
            verified_profiles += 1
        for rule in STRATEGIC_REWARD_RULES:
            direct_equilibria: list[int] = []
            direct_strict: list[int] = []
            for k, direct in enumerate(direct_rows):
                attending = direct["rules"][rule]["attending"]
                ignoring = direct["rules"][rule]["ignoring"]
                attend_ok = k == 0 or attending >= direct_rows[k - 1]["rules"][rule]["ignoring"]
                ignore_ok = k == n or ignoring >= direct_rows[k + 1]["rules"][rule]["attending"]
                attend_strict = k == 0 or attending > direct_rows[k - 1]["rules"][rule]["ignoring"]
                ignore_strict = k == n or ignoring > direct_rows[k + 1]["rules"][rule]["attending"]
                if attend_ok and ignore_ok:
                    direct_equilibria.append(k)
                if attend_strict and ignore_strict:
                    direct_strict.append(k)
                if reward_equilibrium(rule, n, k, p, q) != (
                    attend_ok and ignore_ok,
                    attend_strict and ignore_strict,
                ):
                    raise ValueError("closed reward equilibrium does not match direct deviations")
            recorded = cell["reward_equilibria"][rule]
            if recorded["weak"] != direct_equilibria or recorded["strict"] != direct_strict:
                raise ValueError("reward equilibrium registry mismatch")
    return {
        "passed": True,
        "profiles_verified": verified_profiles,
        "reward_rows_verified": verified_reward_rows,
        "state_enumerator": "target/shared/action-relevant-private labeled states",
    }


def corruption_tests(bundle: dict[str, Any]) -> dict[str, bool]:
    mutations = []
    altered_discovery = copy.deepcopy(bundle)
    altered_discovery["cells"][0]["profiles"][0]["discovery"] = "0"
    mutations.append(altered_discovery)
    altered_reward = copy.deepcopy(bundle)
    altered_reward["cells"][0]["profiles"][0]["rewards"]["equal-split"]["budget"] = "0"
    mutations.append(altered_reward)
    altered_equilibrium = copy.deepcopy(bundle)
    original = altered_equilibrium["cells"][0]["profiles"][0]["weak_equilibrium"]
    altered_equilibrium["cells"][0]["profiles"][0]["weak_equilibrium"] = not original
    mutations.append(altered_equilibrium)
    rejected = []
    for mutation in mutations:
        try:
            verify_bundle(mutation)
        except ValueError:
            rejected.append(True)
        else:
            rejected.append(False)
    return {
        "altered_discovery_rejected": rejected[0],
        "altered_reward_rejected": rejected[1],
        "altered_equilibrium_rejected": rejected[2],
    }
