"""DD-024 track 03: exact negative-feedback dependence audit.

The evaluator factors miss events by detector group.  Verification independently
enumerates detector worlds and executes the saved policies.  Neither route is a
personality model; the joint allocator has declared coordination authority.
"""

from __future__ import annotations

import copy
from fractions import Fraction
from itertools import permutations, product
from typing import Any, cast

Pair = tuple[int, int]
Bits = tuple[int, int, int, int]
F = Fraction
ZERO = F(0)
ONE = F(1)
PAIRS: tuple[Pair, ...] = tuple((left, right) for left in range(3) for right in range(3))
LAWS = ("iid", "searcher_persistent", "round_common", "global_common")
POLICIES = (
    "calibrated_joint",
    "precommitted_calibrated",
    "iid_assumed_joint",
    "perfect_elimination_joint",
    "same_searcher_revisit",
    "cross_searcher_revisit",
    "unvisited_only",
)
BUDGET = {
    "targets": 3,
    "searchers": 2,
    "rounds": 2,
    "attempts_per_trial": 4,
    "clues_per_trial": 2,
    "shared_detection_bits_after_round_one": 2,
}


def _s(value: F) -> str:
    return f"{value.numerator}/{value.denominator}"


def _key(pair: Pair) -> str:
    return f"{pair[0]},{pair[1]}"


def _settings(config: dict[str, Any]) -> list[tuple[F, F, str]]:
    if config.get("study_id") != "DD-024" or config.get("track_id") != "track-03":
        raise ValueError("wrong study or track")
    if config.get("budget") != BUDGET:
        raise ValueError("the registered action/information budget changed")
    if config.get("policies") != list(POLICIES):
        raise ValueError("the registered policy set changed")
    if config.get("time_cap_seconds") != 120 or config.get("memory_cap_mb") != 1024:
        raise ValueError("the registered resource limits changed")
    if config.get("random_seeds") != {"algorithm": [], "model": None}:
        raise ValueError("exact enumeration has no random seed")
    if config.get("arithmetic") != "exact rational":
        raise ValueError("the registered arithmetic changed")
    if config.get("tie_breaking") != "lexicographically first ordered target pair":
        raise ValueError("the registered tie convention changed")
    if config.get("after_success_default") != [0, 0]:
        raise ValueError("the registered after-success continuation changed")
    ps = [F(str(value)) for value in config["p_values"]]
    rs = [F(str(value)) for value in config["r_values"]]
    laws = list(config["failure_laws"])
    if not ps or not rs or not laws:
        raise ValueError("empty parameter grid")
    if len(set(ps)) != len(ps) or len(set(rs)) != len(rs) or len(set(laws)) != len(laws):
        raise ValueError("duplicate grid entry")
    if not set(ps) <= {F(1, 3), F(1, 2), F(2, 3), F(5, 6), ONE}:
        raise ValueError("unregistered clue accuracy")
    if not set(rs) <= {F(1, 4), F(1, 2), F(3, 4), ONE}:
        raise ValueError("unregistered reliability")
    if not set(laws) <= set(LAWS):
        raise ValueError("unregistered detector law")
    cells = [(p, r, str(law)) for p in ps for r in rs for law in laws]
    if config.get("expected_cells") != len(cells):
        raise ValueError("grid cardinality mismatch")
    return cells


def _groups(law: str) -> tuple[int, int, int, int]:
    return {
        "iid": (0, 1, 2, 3),
        "searcher_persistent": (0, 1, 0, 1),
        "round_common": (0, 0, 1, 1),
        "global_common": (0, 0, 0, 0),
    }[law]


def _miss(target: int, actions: tuple[int, ...], r: F, law: str) -> F:
    groups = _groups(law)
    tested = {groups[index] for index, action in enumerate(actions) if action == target}
    return (ONE - r) ** len(tested)


def _pattern_weights(r: F, law: str) -> dict[str, str]:
    groups = _groups(law)
    weights: dict[str, str] = {}
    for bits in product((0, 1), repeat=4):
        assignments: dict[int, int] = {}
        consistent = True
        for group, bit in zip(groups, bits, strict=True):
            if group in assignments and assignments[group] != bit:
                consistent = False
            assignments[group] = bit
        value = ONE
        if consistent:
            for bit in assignments.values():
                value *= r if bit else ONE - r
        else:
            value = ZERO
        weights["".join(str(bit) for bit in bits)] = _s(value)
    return weights


def _weights(p: F, clues: Pair) -> list[F]:
    return [
        F(1, 3)
        * (p if clues[0] == target else (ONE - p) / 2)
        * (p if clues[1] == target else (ONE - p) / 2)
        for target in range(3)
    ]


def _scores(weights: list[F], clues: Pair, r: F, law: str) -> dict[Pair, F]:
    return {
        tail: sum(
            (
                weights[target]
                * (_miss(target, clues, r, law) - _miss(target, clues + tail, r, law))
                for target in range(3)
            ),
            ZERO,
        )
        for tail in PAIRS
    }


def _best(scores: dict[Pair, F], allowed: tuple[Pair, ...] = PAIRS) -> tuple[Pair, ...]:
    best_value = max(scores[pair] for pair in allowed)
    return tuple(pair for pair in allowed if scores[pair] == best_value)


def _primary_row(p: F, r: F, law: str) -> dict[str, Any]:
    policy_tables: dict[str, dict[str, list[int]]] = {name: {} for name in POLICIES}
    values = dict.fromkeys(POLICIES, ZERO)
    disagreement_values = dict.fromkeys(POLICIES, ZERO)
    optimal: dict[str, list[list[int]]] = {}
    audit: list[dict[str, Any]] = []
    first_success = ZERO
    disagreement_mass = ZERO
    fallback_true_mass = ZERO
    for clues in PAIRS:
        key = _key(clues)
        weights = _weights(p, clues)
        mass = sum(weights, ZERO)
        failure = sum((weights[target] * _miss(target, clues, r, law) for target in range(3)), ZERO)
        success = mass - failure
        first_success += success
        if clues[0] != clues[1]:
            disagreement_mass += mass
        scores = _scores(weights, clues, r, law)
        iid_scores = _scores(weights, clues, r, "iid")
        unseen = tuple(pair for pair in PAIRS if all(action not in clues for action in pair))
        perfect_failure = sum((weights[target] for target in range(3) if target not in clues), ZERO)
        fallback = perfect_failure == ZERO
        perfect_weights = weights
        if fallback:
            unseen_targets = [target for target in range(3) if target not in clues]
            perfect_weights = [
                F(1, len(unseen_targets)) if target in unseen_targets else ZERO
                for target in range(3)
            ]
            fallback_true_mass += failure
        perfect_scores = _scores(perfect_weights, clues, ONE, "iid")
        best = _best(scores)
        chosen = {
            "calibrated_joint": best[0],
            "precommitted_calibrated": best[0],
            "iid_assumed_joint": _best(iid_scores)[0],
            "perfect_elimination_joint": _best(perfect_scores, unseen)[0],
            "same_searcher_revisit": clues,
            "cross_searcher_revisit": (clues[1], clues[0]),
            "unvisited_only": _best(scores, unseen)[0],
        }
        for name, tail in chosen.items():
            policy_tables[name][key] = list(tail)
            if name == "precommitted_calibrated":
                value = sum(
                    (
                        weights[target] * (ONE - _miss(target, clues + tail, r, law))
                        for target in range(3)
                    ),
                    ZERO,
                )
            else:
                value = success + scores[tail]
            values[name] += value
            if clues[0] != clues[1]:
                disagreement_values[name] += value
        optimal[key] = [list(tail) for tail in best]
        audit.append(
            {
                "clues": list(clues),
                "signal_pair_probability": _s(mass),
                "first_failure_mass": _s(failure),
                "candidate_rescue_masses": {_key(tail): _s(scores[tail]) for tail in PAIRS},
                "perfect_elimination_fallback": fallback,
            }
        )
    estimands = {
        "iid_misspecification_regret": values["calibrated_joint"] - values["iid_assumed_joint"],
        "failure_elimination_regret": values["calibrated_joint"]
        - values["perfect_elimination_joint"],
        "cross_searcher_rescue_contrast": values["cross_searcher_revisit"]
        - values["same_searcher_revisit"],
        "schedule_equivalence_control": values["calibrated_joint"]
        - values["precommitted_calibrated"],
    }
    if estimands["schedule_equivalence_control"] != ZERO:
        raise ArithmeticError("precommitted schedule equivalence failed")
    if any(value > values["calibrated_joint"] for value in values.values()):
        raise ArithmeticError("declared continuation benchmark lost dominance")
    return {
        "cell_id": f"p={_s(p)}|r={_s(r)}|law={law}",
        "p": _s(p),
        "r": _s(r),
        "failure_law": law,
        "budget": dict(BUDGET),
        "policy_values": {name: _s(value) for name, value in values.items()},
        "disagreement_policy_values": {
            name: _s(value / disagreement_mass) if disagreement_mass else None
            for name, value in disagreement_values.items()
        },
        "estimands": {name: _s(value) for name, value in estimands.items()},
        "first_round_success": _s(first_success),
        "double_failure_probability": _s(ONE - first_success),
        "disagreement_clue_probability": _s(disagreement_mass),
        "perfect_elimination_fallback_true_mass": _s(fallback_true_mass),
        "detector_pattern_weights": _pattern_weights(r, law),
        "policies": policy_tables,
        "optimal_continuations": optimal,
        "continuation_audit": audit,
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {"cells": len(rows)}
    for name in (
        "iid_misspecification_regret",
        "failure_elimination_regret",
        "cross_searcher_rescue_contrast",
        "schedule_equivalence_control",
    ):
        values = [F(row["estimands"][name]) for row in rows]
        result[name] = {
            "positive_cells": sum(value > ZERO for value in values),
            "zero_cells": sum(value == ZERO for value in values),
            "negative_cells": sum(value < ZERO for value in values),
            "minimum": _s(min(values)),
            "maximum": _s(max(values)),
        }
    return result


def run(config: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the supplied registered grid; the caller owns run provenance/caps."""
    cells = _settings(config)
    rows = [_primary_row(p, r, law) for p, r, law in cells]
    return {
        "study_id": "DD-024",
        "track_id": "track-03",
        "evidence_class": "exact-bounded-computation",
        "method": "factored detector-group miss probabilities and finite continuation maximization",
        "configuration": copy.deepcopy(config),
        "rows": rows,
        "summary": _summary(rows),
    }


def _raw_detectors(r: F, law: str) -> list[tuple[Bits, F]]:
    """Independent generative detector construction; no primary grouping logic."""
    worlds: list[tuple[Bits, F]] = []
    dimension = 4 if law == "iid" else 1 if law == "global_common" else 2
    for independent_bits in product((0, 1), repeat=dimension):
        probability = ONE
        for bit in independent_bits:
            probability *= r if bit else ONE - r
        if law == "iid":
            a, b, c, d = independent_bits
            bits = (a, b, c, d)
        elif law == "searcher_persistent":
            a, b = independent_bits
            bits = (a, b, a, b)
        elif law == "round_common":
            a, b = independent_bits
            bits = (a, a, b, b)
        elif law == "global_common":
            (a,) = independent_bits
            bits = (a, a, a, a)
        else:
            raise ValueError("unknown detector law")
        worlds.append((bits, probability))
    return worlds


def _raw_tables(p: F, r: F, law: str) -> dict[str, Any]:
    """Execute every candidate schedule in full latent worlds, without posteriors."""
    detectors = _raw_detectors(r, law)
    masses = {clues: ZERO for clues in PAIRS}
    failures = {clues: ZERO for clues in PAIRS}
    rescues = {clues: dict.fromkeys(PAIRS, ZERO) for clues in PAIRS}
    total_world_mass = ZERO
    detector_weights = {"".join(map(str, bits)): ZERO for bits in product((0, 1), repeat=4)}
    marginal = [ZERO, ZERO, ZERO, ZERO]
    for bits, probability in detectors:
        detector_weights["".join(map(str, bits))] += probability
        for index in range(4):
            marginal[index] += probability * bits[index]
    for target, x0, x1 in product(range(3), repeat=3):
        clues = (x0, x1)
        # Deliberately independent of the primary clue-weight helper.
        clue_probability = F(1, 3)
        for observation in clues:
            clue_probability *= p if observation == target else F(1, 2) * (ONE - p)
        for bits, detection_probability in detectors:
            weight = clue_probability * detection_probability
            total_world_mass += weight
            masses[clues] += weight
            first_detected = (x0 == target and bits[0] == 1) or (x1 == target and bits[1] == 1)
            if first_detected:
                continue
            failures[clues] += weight
            for tail in PAIRS:
                second_detected = (tail[0] == target and bits[2] == 1) or (
                    tail[1] == target and bits[3] == 1
                )
                if second_detected:
                    rescues[clues][tail] += weight
    return {
        "masses": masses,
        "failures": failures,
        "rescues": rescues,
        "world_mass": total_world_mass,
        "marginal": marginal,
        "detector_weights": detector_weights,
    }


def _read_pair(value: Any) -> Pair:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("malformed saved action pair")
    if any(type(item) is not int or item not in range(3) for item in value):
        raise ValueError("saved action outside target set")
    return (value[0], value[1])


def _raw_policy_execution(p: F, r: F, law: str, tables: dict[str, Any]) -> dict[str, Any]:
    """Execute all four slots for each saved policy, including after success."""
    values = dict.fromkeys(POLICIES, ZERO)
    disagreements = dict.fromkeys(POLICIES, ZERO)
    weighted_attempts = dict.fromkeys(POLICIES, ZERO)
    for target, x0, x1 in product(range(3), repeat=3):
        clues = (x0, x1)
        probability = F(1, 3)
        for clue in clues:
            probability *= p if clue == target else (ONE - p) / 2
        for bits, detector_probability in _raw_detectors(r, law):
            weight = probability * detector_probability
            first_outcomes = (x0 == target and bool(bits[0]), x1 == target and bool(bits[1]))
            for name in POLICIES:
                # Every policy receives the same clue pair and the same two bits.
                if any(first_outcomes) and name != "precommitted_calibrated":
                    tail = (0, 0)
                else:
                    tail = _read_pair(tables[name][_key(clues)])
                actions = (x0, x1, tail[0], tail[1])
                outcomes = [
                    action == target and bool(bit)
                    for action, bit in zip(actions, bits, strict=True)
                ]
                weighted_attempts[name] += weight * len(actions)
                if any(outcomes):
                    values[name] += weight
                    if x0 != x1:
                        disagreements[name] += weight
    return {"values": values, "disagreements": disagreements, "attempts": weighted_attempts}


def _audit(config: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    cells = _settings(config)
    if result.get("configuration") != config:
        raise ValueError("saved configuration mismatch")
    if result.get("study_id") != "DD-024" or result.get("track_id") != "track-03":
        raise ValueError("saved study identity mismatch")
    rows = cast(list[dict[str, Any]], result["rows"])
    if len(rows) != len(cells):
        raise ValueError("saved grid cardinality mismatch")
    checked_candidates = 0
    permutation_checks = 0
    for (p, r, law), row in zip(cells, rows, strict=True):
        if (row["p"], row["r"], row["failure_law"]) != (_s(p), _s(r), law):
            raise ValueError("saved parameter cell mismatch")
        if row["cell_id"] != f"p={_s(p)}|r={_s(r)}|law={law}":
            raise ValueError("saved cell identity mismatch")
        if row["budget"] != BUDGET:
            raise ValueError("saved budget mismatch")
        raw = _raw_tables(p, r, law)
        iid = _raw_tables(p, r, "iid")
        perfect = _raw_tables(p, ONE, "iid")
        masses = cast(dict[Pair, F], raw["masses"])
        failures = cast(dict[Pair, F], raw["failures"])
        rescues = cast(dict[Pair, dict[Pair, F]], raw["rescues"])
        if raw["world_mass"] != ONE or raw["marginal"] != [r, r, r, r]:
            raise ValueError("raw probability normalization or marginal failure")
        expected_patterns = {key: _s(value) for key, value in raw["detector_weights"].items()}
        if row["detector_pattern_weights"] != expected_patterns:
            raise ValueError("detector distribution mismatch")
        if set(row["policies"]) != set(POLICIES):
            raise ValueError("saved policy set mismatch")
        values = dict.fromkeys(POLICIES, ZERO)
        disagreements = dict.fromkeys(POLICIES, ZERO)
        disagreement_mass = sum((masses[x] for x in PAIRS if x[0] != x[1]), ZERO)
        fallback_mass = ZERO
        if len(row["continuation_audit"]) != len(PAIRS):
            raise ValueError("incomplete continuation audit")
        for clues, saved_audit in zip(PAIRS, row["continuation_audit"], strict=True):
            key = _key(clues)
            candidates = rescues[clues]
            # Verify all finite alternatives, without using _best or _scores.
            maximum = max(candidates.values())
            optimal = [pair for pair in PAIRS if candidates[pair] == maximum]
            unseen = [pair for pair in PAIRS if pair[0] not in clues and pair[1] not in clues]
            best_unseen = max(candidates[pair] for pair in unseen)
            iid_maximum = max(iid["rescues"][clues].values())
            fallback = perfect["failures"][clues] == ZERO
            if fallback:
                fallback_mass += failures[clues]
                allowed_targets = [target for target in range(3) if target not in clues]
                # Explicit perfect-detection success count for uniform fallback.
                elimination_scores = {
                    pair: F(sum(target in pair for target in allowed_targets), len(allowed_targets))
                    for pair in unseen
                }
            else:
                elimination_scores = {pair: perfect["rescues"][clues][pair] for pair in unseen}
            elimination_maximum = max(elimination_scores.values())
            expected_choices = {
                "calibrated_joint": optimal[0],
                "precommitted_calibrated": optimal[0],
                "iid_assumed_joint": next(
                    pair for pair in PAIRS if iid["rescues"][clues][pair] == iid_maximum
                ),
                "perfect_elimination_joint": next(
                    pair for pair in unseen if elimination_scores[pair] == elimination_maximum
                ),
                "same_searcher_revisit": clues,
                "cross_searcher_revisit": (clues[1], clues[0]),
                "unvisited_only": next(pair for pair in unseen if candidates[pair] == best_unseen),
            }
            for name in POLICIES:
                if set(row["policies"][name]) != {_key(pair) for pair in PAIRS}:
                    raise ValueError("incomplete saved policy")
                tail = _read_pair(row["policies"][name][key])
                if tail != expected_choices[name]:
                    raise ValueError(f"policy mismatch: {name} at {key}")
                value = masses[clues] - failures[clues] + candidates[tail]
                values[name] += value
                if clues[0] != clues[1]:
                    disagreements[name] += value
            if row["optimal_continuations"][key] != [list(pair) for pair in optimal]:
                raise ValueError("optimal continuation set mismatch")
            expected_audit = {
                "clues": list(clues),
                "signal_pair_probability": _s(masses[clues]),
                "first_failure_mass": _s(failures[clues]),
                "candidate_rescue_masses": {_key(pair): _s(candidates[pair]) for pair in PAIRS},
                "perfect_elimination_fallback": fallback,
            }
            if saved_audit != expected_audit:
                raise ValueError("candidate continuation evidence mismatch")
            checked_candidates += len(PAIRS)
        executed = _raw_policy_execution(p, r, law, row["policies"])
        if executed["values"] != values or executed["disagreements"] != disagreements:
            raise ValueError("direct saved-policy execution disagrees with candidate worlds")
        if any(value != F(4) for value in executed["attempts"].values()):
            raise ValueError("saved-policy execution changed the four-attempt budget")
        expected_values = {name: _s(value) for name, value in executed["values"].items()}
        if row["policy_values"] != expected_values:
            raise ValueError("raw world policy value mismatch")
        expected_disagreements = {
            name: _s(value / disagreement_mass) if disagreement_mass else None
            for name, value in disagreements.items()
        }
        if row["disagreement_policy_values"] != expected_disagreements:
            raise ValueError("disagreement stratum mismatch")
        first_success = ONE - sum(failures.values(), ZERO)
        expected_scalars = {
            "first_round_success": first_success,
            "double_failure_probability": ONE - first_success,
            "disagreement_clue_probability": disagreement_mass,
            "perfect_elimination_fallback_true_mass": fallback_mass,
        }
        if any(row[name] != _s(value) for name, value in expected_scalars.items()):
            raise ValueError("raw world scalar mismatch")
        contrasts = {
            "iid_misspecification_regret": values["calibrated_joint"] - values["iid_assumed_joint"],
            "failure_elimination_regret": values["calibrated_joint"]
            - values["perfect_elimination_joint"],
            "cross_searcher_rescue_contrast": values["cross_searcher_revisit"]
            - values["same_searcher_revisit"],
            "schedule_equivalence_control": values["calibrated_joint"]
            - values["precommitted_calibrated"],
        }
        if row["estimands"] != {name: _s(value) for name, value in contrasts.items()}:
            raise ValueError("raw world contrast mismatch")
        if contrasts["schedule_equivalence_control"] != ZERO:
            raise ValueError("schedule equivalence failure")
        if any(value < ZERO or value > ONE for value in values.values()):
            raise ValueError("probability bound failure")
        if any(value > values["calibrated_joint"] for value in values.values()):
            raise ValueError("continuation benchmark dominance failure")
        for permutation in permutations(range(3)):
            for clues in PAIRS:
                changed_clues = (permutation[clues[0]], permutation[clues[1]])
                for tail in PAIRS:
                    changed_tail = (permutation[tail[0]], permutation[tail[1]])
                    if rescues[clues][tail] != rescues[changed_clues][changed_tail]:
                        raise ValueError("target permutation failure")
                    permutation_checks += 1
        for clues in PAIRS:
            for tail in PAIRS:
                if rescues[clues][tail] != rescues[(clues[1], clues[0])][(tail[1], tail[0])]:
                    raise ValueError("searcher permutation failure")
                permutation_checks += 1
    # At perfect detection every registered detector dependence law is identical.
    perfect_values: dict[str, dict[str, str]] = {}
    for row in rows:
        if row["r"] == "1/1":
            if row["p"] in perfect_values and row["policy_values"] != perfect_values[row["p"]]:
                raise ValueError("perfect-detection law equivalence failure")
            perfect_values[row["p"]] = row["policy_values"]
    if result["summary"] != _summary(rows):
        raise ValueError("summary is inconsistent with verified rows")
    return {
        "cells_checked": len(rows),
        "candidate_pairs_checked": checked_candidates,
        "permutation_equalities_checked": permutation_checks,
        "attempts_per_policy_per_trial": 4,
        "shared_clues_per_policy": 2,
        "shared_first_round_outcomes_per_policy": 2,
        "method": "independent explicit detector-world execution and finite action checks",
        "shared_with_primary": (
            "configuration/schema constants, rational serialization, summary formatting"
        ),
    }


def verify(config: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Verify frozen outputs independently and exercise four corruption fixtures."""
    try:
        checked = _audit(config, result)
        first = copy.deepcopy(result["rows"][0])
        mini_config = copy.deepcopy(config)
        mini_config.update(
            p_values=[first["p"]],
            r_values=[first["r"]],
            failure_laws=[first["failure_law"]],
            expected_cells=1,
        )
        fixture = copy.deepcopy(result)
        fixture["configuration"] = mini_config
        fixture["rows"] = [first]
        fixture["summary"] = _summary([first])
        corruptions: dict[str, bool] = {}
        for kind in ("detector_weight", "revisit_mapping", "saved_value", "attempt_budget"):
            damaged = copy.deepcopy(fixture)
            damaged_row = damaged["rows"][0]
            if kind == "detector_weight":
                old = F(damaged_row["detector_pattern_weights"]["0000"])
                damaged_row["detector_pattern_weights"]["0000"] = _s(old + F(1, 100))
            elif kind == "revisit_mapping":
                damaged_row["policies"]["cross_searcher_revisit"]["0,1"] = [0, 1]
            elif kind == "saved_value":
                old = F(damaged_row["policy_values"]["calibrated_joint"])
                damaged_row["policy_values"]["calibrated_joint"] = _s(old + F(1, 100))
            else:
                damaged_row["budget"]["attempts_per_trial"] = 5
            try:
                _audit(mini_config, damaged)
            except (ValueError, KeyError, TypeError, ArithmeticError):
                corruptions[kind] = True
            else:
                corruptions[kind] = False
        return {
            "passed": all(corruptions.values()),
            "checks": checked,
            "errors": [name for name, rejected in corruptions.items() if not rejected],
            "corruptions": corruptions,
        }
    except (ValueError, KeyError, TypeError, ArithmeticError) as error:
        return {"passed": False, "checks": {}, "errors": [str(error)], "corruptions": {}}
