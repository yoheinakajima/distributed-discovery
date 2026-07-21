"""Materially separate labeled-state verifier for DD-013."""

from __future__ import annotations

import copy
from fractions import Fraction
from itertools import product
from typing import Any


def _signal_probability(signal: int, target: int, accuracy: Fraction) -> Fraction:
    return accuracy if signal == target else (1 - accuracy) / 2


def direct_profile(n: int, readers: int, p: Fraction, q: Fraction) -> dict[str, Any]:
    probability_mass = Fraction()
    discovered = Fraction()
    correct_actions = Fraction()
    distinct_actions = Fraction()
    equal_payoffs = [Fraction() for _ in range(n)]
    pooled_payoffs = [Fraction() for _ in range(n)]
    for target in range(3):
        for shared in range(3):
            for private in product(range(3), repeat=n - readers):
                probability = Fraction(1, 3) * _signal_probability(shared, target, q)
                for signal in private:
                    probability *= _signal_probability(signal, target, p)
                actions = [shared] * readers + list(private)
                winners = [action == target for action in actions]
                winner_count = sum(winners)
                success = winner_count > 0
                probability_mass += probability
                discovered += probability * success
                correct_actions += probability * Fraction(winner_count, n)
                distinct_actions += probability * len(set(actions))
                for index, winner in enumerate(winners):
                    if winner:
                        equal_payoffs[index] += probability / winner_count
                    if success:
                        pooled_payoffs[index] += probability / n
    if probability_mass != 1:
        raise ValueError("direct audience probabilities do not normalize")
    return {
        "probability_mass": probability_mass,
        "discovery": discovered,
        "action_quality": correct_actions,
        "expected_distinct_actions": distinct_actions,
        "equal_attending": None if readers == 0 else equal_payoffs[0],
        "equal_private": None if readers == n else equal_payoffs[readers],
        "pooled_attending": None if readers == 0 else pooled_payoffs[0],
        "pooled_private": None if readers == n else pooled_payoffs[readers],
    }


def _direct_equilibrium(
    rows: list[dict[str, Any]], audience: int, reward: str
) -> dict[str, list[int]]:
    weak_counts: list[int] = []
    strict_counts: list[int] = []
    attending_key = f"{reward}_attending"
    private_key = f"{reward}_private"
    for readers in range(audience + 1):
        current = rows[readers]
        reader_ok = reader_strict = True
        if readers:
            assert current[attending_key] is not None
            switched = rows[readers - 1][private_key]
            assert switched is not None
            reader_ok = current[attending_key] >= switched
            reader_strict = current[attending_key] > switched
        private_ok = private_strict = True
        if readers < audience:
            assert current[private_key] is not None
            switched = rows[readers + 1][attending_key]
            assert switched is not None
            private_ok = current[private_key] >= switched
            private_strict = current[private_key] > switched
        if reader_ok and private_ok:
            weak_counts.append(readers)
        if reader_strict and private_strict:
            strict_counts.append(readers)
    return {"weak": weak_counts, "strict": strict_counts}


def _verify_cell(
    cell: dict[str, Any], cache: dict[tuple[int, str, str, int], dict[str, Any]]
) -> None:
    n = int(cell["agents"])
    p_text = str(cell["private_accuracy"])
    q_text = str(cell["shared_accuracy"])
    rows = [cache[(n, p_text, q_text, readers)] for readers in range(n + 1)]
    for binding in cell["binding_audiences"]:
        readers = int(binding["audience"])
        direct = rows[readers]
        for key in ("discovery", "action_quality", "expected_distinct_actions"):
            if binding[key] != str(direct[key]):
                raise ValueError(f"binding audience mismatch: {key}")
    for audience in cell["voluntary_audiences"]:
        size = int(audience["audience"])
        expected = _direct_equilibrium(rows, size, "equal")
        if audience["weak_equilibria"] != expected["weak"]:
            raise ValueError("voluntary weak-equilibrium corruption")
        if audience["strict_equilibria"] != expected["strict"]:
            raise ValueError("voluntary strict-equilibrium corruption")
    pooled = _direct_equilibrium(rows, n, "pooled")
    recorded_pool = cell["mechanisms"]["public_universal_pooling"]
    if pooled["weak"] != recorded_pool["weak"] or pooled["strict"] != recorded_pool["strict"]:
        raise ValueError("universal-pooling mechanism corruption")
    for garbled in cell["garbling_rows"]:
        g_text = str(garbled["delivered_accuracy"])
        readers = int(garbled["audience"])
        direct = cache[(n, p_text, g_text, readers)]
        if garbled["discovery"] != str(direct["discovery"]):
            raise ValueError("garbling discovery corruption")
        optimum = max(Fraction(row["discovery"]) for row in cell["binding_audiences"])
        if garbled["weakly_dominated_by_binding_optimum"] != (direct["discovery"] <= optimum):
            raise ValueError("garbling dominance corruption")


def verify_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    cache: dict[tuple[int, str, str, int], dict[str, Any]] = {}
    profiles = 0
    state_count = 0
    for cell in bundle["cells"]:
        n = int(cell["agents"])
        p_text = str(cell["private_accuracy"])
        q_text = str(cell["shared_accuracy"])
        p, q = Fraction(p_text), Fraction(q_text)
        for readers in range(n + 1):
            key = (n, p_text, q_text, readers)
            if key not in cache:
                cache[key] = direct_profile(n, readers, p, q)
                state_count += 9 * 3 ** (n - readers)
                profiles += 1
    for cell in bundle["cells"]:
        _verify_cell(cell, cache)
    return {
        "passed": True,
        "unique_profiles_verified": profiles,
        "direct_labeled_states": state_count,
        "binding_rows_verified": sum(len(cell["binding_audiences"]) for cell in bundle["cells"]),
        "voluntary_rows_verified": sum(
            len(audience["profiles"])
            for cell in bundle["cells"]
            for audience in cell["voluntary_audiences"]
        ),
        "garbling_rows_verified": sum(len(cell["garbling_rows"]) for cell in bundle["cells"]),
        "mechanism_cells_verified": len(bundle["cells"]),
    }


def corruption_tests(bundle: dict[str, Any]) -> dict[str, bool]:
    cell = bundle["cells"][0]
    n = int(cell["agents"])
    p_text = str(cell["private_accuracy"])
    accuracies = {
        str(cell["shared_accuracy"]),
        *(str(row["delivered_accuracy"]) for row in cell["garbling_rows"]),
    }
    cache = {
        (n, p_text, accuracy, readers): direct_profile(
            n, readers, Fraction(p_text), Fraction(accuracy)
        )
        for accuracy in accuracies
        for readers in range(n + 1)
    }
    mutations: list[dict[str, Any]] = []
    binding = copy.deepcopy(cell)
    binding["binding_audiences"][0]["discovery"] = "0"
    mutations.append(binding)
    voluntary = copy.deepcopy(cell)
    voluntary["voluntary_audiences"][0]["weak_equilibria"] = []
    mutations.append(voluntary)
    mechanism = copy.deepcopy(cell)
    mechanism["mechanisms"]["public_universal_pooling"]["weak"] = []
    mutations.append(mechanism)
    garbling = copy.deepcopy(cell)
    garbling["garbling_rows"][0]["weakly_dominated_by_binding_optimum"] = False
    mutations.append(garbling)
    rejected: list[bool] = []
    for mutation in mutations:
        try:
            _verify_cell(mutation, cache)
        except ValueError:
            rejected.append(True)
        else:
            rejected.append(False)
    return {
        "altered_binding_discovery_rejected": rejected[0],
        "altered_voluntary_equilibrium_rejected": rejected[1],
        "altered_mechanism_equilibrium_rejected": rejected[2],
        "altered_garbling_dominance_rejected": rejected[3],
    }
