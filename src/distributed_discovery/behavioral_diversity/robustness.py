"""DD-024 track 02: finite evidence-robustness audit and independent verifier.

The policy class is the registered six-role library, not every decentralized
policy. No stored expected metric is used to produce an outcome. The primary
path factors private outcomes and solves a two-dimensional convex hull. The
verification path enumerates joint outcomes and checks primal/dual certificates.
"""

from __future__ import annotations

import copy
import itertools
import time
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, TypeAlias

Vector: TypeAlias = tuple[Fraction, Fraction]
ROLES = ("P", "S", "C", "K0", "K1", "K2")
PROFILES = tuple((first, second) for first in ROLES for second in ROLES)
REGIMES = ("A", "B")
ZERO = Fraction(0)
ONE = Fraction(1)


@dataclass(frozen=True)
class _Cell:
    identifier: str
    rho: Fraction
    diagnostic: str
    threshold: int


@dataclass(frozen=True)
class _Settings:
    accuracies: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]
    cells: tuple[_Cell, ...]
    epsilons: tuple[Fraction, ...]
    priors: tuple[Fraction, ...]
    diagnostic_accuracy: dict[str, Fraction | None]
    time_cap: int


@dataclass(frozen=True)
class _Plan:
    index: int
    profiles: tuple[int, ...]
    values: Vector


@dataclass(frozen=True)
class _Reference:
    cell: _Cell
    symbols: tuple[str, ...]
    diagnostic: tuple[tuple[Fraction, ...], tuple[Fraction, ...]]
    profiles: tuple[Vector, ...]
    plans: tuple[_Plan, ...]
    departures: dict[str, dict[str, Any]]
    mass_checks: int


def _fraction(value: Any) -> Fraction:
    if not isinstance(value, str) or "/" not in value:
        raise ValueError("rational values must be canonical numerator/denominator strings")
    result = Fraction(value)
    if value != f"{result.numerator}/{result.denominator}":
        raise ValueError("noncanonical rational string")
    return result


def _text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _vector_json(values: Vector) -> dict[str, str]:
    return {"A": _text(values[0]), "B": _text(values[1])}


def _vector_read(value: Any) -> Vector:
    if not isinstance(value, dict) or set(value) != {"A", "B"}:
        raise ValueError("a vector must contain exactly regimes A and B")
    return _fraction(value["A"]), _fraction(value["B"])


def _plan_id(index: int) -> str:
    return f"d{index:04d}"


def _parse(config: dict[str, Any]) -> _Settings:
    try:
        if config["schema_version"] != "dd-024-robustness-config-v1":
            raise ValueError("unsupported configuration schema")
        if (config["study_id"], config["track_id"]) != ("DD-024", "track-02"):
            raise ValueError("wrong study or track identity")
        model = config["model"]
        fixed = {
            "candidates": 3,
            "agents": 2,
            "target_prior": "uniform",
            "roles": list(ROLES),
            "private_source_law": "shared-with-probability-rho-otherwise-independent",
            "role_assignment": "diagnostic-only-before-target-signals",
            "regime_timing": "chosen-before-signals-and-randomization",
        }
        if any(model.get(key) != value for key, value in fixed.items()):
            raise ValueError("model differs from the declared finite policy class")
        expected_regimes = {
            "A": {"private_accuracy": "1/3", "public_accuracy": "5/6"},
            "B": {"private_accuracy": "5/6", "public_accuracy": "1/3"},
        }
        if model["regimes"] != expected_regimes:
            raise ValueError("accuracy regimes differ from the admitted configuration")
        accuracies = tuple(
            (
                _fraction(model["regimes"][regime]["private_accuracy"]),
                _fraction(model["regimes"][regime]["public_accuracy"]),
            )
            for regime in REGIMES
        )
        comparator = config["comparators"]
        if comparator["known_prior_a"] != ["1/4", "1/2", "3/4"]:
            raise ValueError("known-prior grid differs from registration")
        if comparator["epsilon_grid"] != ["0/1", "1/4", "1/2", "3/4", "1/1"]:
            raise ValueError("departure grid differs from registration")
        if comparator["diagnostic_accuracy"] != {"none": None, "noisy": "3/4", "perfect": "1/1"}:
            raise ValueError("diagnostic law differs from registration")
        if comparator["tie_break"] != "first-in-declared-enumeration":
            raise ValueError("unregistered tie rule")
        if config["arithmetic"] != "exact-rational":
            raise ValueError("this audit requires exact rational arithmetic")
        if config["random_seeds"] != {"algorithm": [], "model": None}:
            raise ValueError("this finite enumeration uses no random seeds")
        if config["resource_caps"] != {"wall_seconds": 120, "memory_mib": 1024}:
            raise ValueError("resource caps differ from registration")
        if (config["time_cap_seconds"], config["memory_cap_mb"]) != (120, 1024):
            raise ValueError("runner resource caps differ from registration")
        if config["stopping_rule"] != "one-primary-run-preserve-failure-no-grid-expansion":
            raise ValueError("unregistered stopping rule")
        cells: list[_Cell] = []
        identifiers: set[str] = set()
        specifications: set[tuple[Fraction, str, int]] = set()
        for entry in config["cells"]:
            identifier = entry["id"]
            rho = _fraction(entry["rho"])
            diagnostic = entry["diagnostic"]
            threshold = entry["threshold"]
            if not isinstance(identifier, str) or not identifier or identifier in identifiers:
                raise ValueError("cell identifiers must be unique nonempty strings")
            if rho not in (ZERO, Fraction(1, 2), ONE):
                raise ValueError("unregistered private-source mixture")
            if diagnostic not in ("none", "noisy", "perfect"):
                raise ValueError("unregistered diagnostic")
            if type(threshold) is not int or threshold not in (1, 2):
                raise ValueError("threshold must be one or two")
            specification = (rho, diagnostic, threshold)
            if specification in specifications:
                raise ValueError("duplicate scientific cell")
            cells.append(_Cell(identifier, rho, diagnostic, threshold))
            identifiers.add(identifier)
            specifications.add(specification)
        if not cells or len(cells) > 18:
            raise ValueError("require between one development cell and 18 registered cells")
        return _Settings(
            (accuracies[0], accuracies[1]),
            tuple(cells),
            tuple(_fraction(value) for value in comparator["epsilon_grid"]),
            tuple(_fraction(value) for value in comparator["known_prior_a"]),
            {"none": None, "noisy": Fraction(3, 4), "perfect": ONE},
            120,
        )
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"malformed track-02 configuration: {exc}") from exc


def _action(role: str, private: int, public: int) -> int:
    if role == "P":
        return private
    if role == "S":
        return public
    if role == "C":
        return private if private == public else 3 - private - public
    return int(role[1])


def _primary_profile_values(settings: _Settings, cell: _Cell) -> tuple[Vector, ...]:
    """Factor conditional independent outcomes; sum the shared-source branch."""
    results: list[Vector] = []
    for roles in PROFILES:
        by_regime: list[Fraction] = []
        for private_accuracy, public_accuracy in settings.accuracies:
            value = ZERO
            for target, public in itertools.product(range(3), repeat=2):
                public_mass = public_accuracy if public == target else (1 - public_accuracy) / 2
                private_masses = tuple(
                    private_accuracy if clue == target else (1 - private_accuracy) / 2
                    for clue in range(3)
                )
                marginals = tuple(
                    sum(
                        (
                            private_masses[clue]
                            for clue in range(3)
                            if _action(role, clue, public) == target
                        ),
                        ZERO,
                    )
                    for role in roles
                )
                if cell.threshold == 1:
                    independent = 1 - (1 - marginals[0]) * (1 - marginals[1])
                else:
                    independent = marginals[0] * marginals[1]
                shared = sum(
                    (
                        private_masses[clue]
                        for clue in range(3)
                        if sum(_action(role, clue, public) == target for role in roles)
                        >= cell.threshold
                    ),
                    ZERO,
                )
                value += public_mass * ((1 - cell.rho) * independent + cell.rho * shared) / 3
            by_regime.append(value)
        results.append((by_regime[0], by_regime[1]))
    return tuple(results)


def _primary_diagnostic(
    settings: _Settings, mode: str
) -> tuple[tuple[str, ...], tuple[tuple[Fraction, ...], tuple[Fraction, ...]]]:
    accuracy = settings.diagnostic_accuracy[mode]
    if accuracy is None:
        return ("none",), ((ONE,), (ONE,))
    return ("A", "B"), ((accuracy, 1 - accuracy), (1 - accuracy, accuracy))


def _primary_plans(
    values: tuple[Vector, ...],
    diagnostic: tuple[tuple[Fraction, ...], tuple[Fraction, ...]],
) -> tuple[_Plan, ...]:
    plans = []
    for index, profiles in enumerate(itertools.product(range(36), repeat=len(diagnostic[0]))):
        vector = tuple(
            sum(
                (
                    diagnostic[regime][z] * values[profile][regime]
                    for z, profile in enumerate(profiles)
                ),
                ZERO,
            )
            for regime in range(2)
        )
        plans.append(_Plan(index, profiles, (vector[0], vector[1])))
    return tuple(plans)


def _choice(plan: _Plan) -> dict[str, Any]:
    return {
        "plan_id": _plan_id(plan.index),
        "by_regime": _vector_json(plan.values),
        "worst_case": _text(min(plan.values)),
    }


def _cross(first: _Plan, middle: _Plan, last: _Plan) -> Fraction:
    x1, y1 = first.values
    x2, y2 = middle.values
    x3, y3 = last.values
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)


def _solve_mixture(plans: tuple[_Plan, ...]) -> dict[str, Any]:
    """Upper hull optimum and a dual weight bounding every admissible plan."""
    best_pure = max(plans, key=lambda plan: min(plan.values))
    value = min(best_pure.values)
    support = [(best_pure, ONE)]
    vector = best_pure.values
    by_x: dict[Fraction, _Plan] = {}
    for plan in plans:
        x, y = plan.values
        previous = by_x.get(x)
        if previous is None or y > previous.values[1]:
            by_x[x] = plan
    nondominated: list[_Plan] = []
    highest_y = Fraction(-1)
    for x in sorted(by_x, reverse=True):
        point = by_x[x]
        if point.values[1] > highest_y:
            nondominated.append(point)
            highest_y = point.values[1]
    hull: list[_Plan] = []
    for point in reversed(nondominated):
        while len(hull) > 1 and _cross(hull[-2], hull[-1], point) >= 0:
            hull.pop()
        hull.append(point)
    for left, right in zip(hull, hull[1:], strict=False):
        left_difference = left.values[0] - left.values[1]
        right_difference = right.values[0] - right.values[1]
        if left_difference == right_difference:
            continue
        weight = right_difference / (right_difference - left_difference)
        if not 0 < weight < 1:
            continue
        candidate = (
            weight * left.values[0] + (1 - weight) * right.values[0],
            weight * left.values[1] + (1 - weight) * right.values[1],
        )
        if min(candidate) > value:
            value = min(candidate)
            support = [(left, weight), (right, 1 - weight)]
            vector = candidate
    lower, upper = ZERO, ONE
    for plan in plans:
        x, y = plan.values
        difference = x - y
        if difference > 0:
            upper = min(upper, (value - y) / difference)
        elif difference < 0:
            lower = max(lower, (value - y) / difference)
        elif y > value:
            raise ArithmeticError("hull optimum has no valid dual certificate")
    if lower > upper:
        raise ArithmeticError("hull optimum and dual inequalities disagree")
    return {
        "support": [
            {"plan_id": _plan_id(plan.index), "weight": _text(weight)} for plan, weight in support
        ],
        "by_regime": _vector_json(vector),
        "worst_case": _text(value),
        "certificate": {
            "regime_a_weight": _text(lower),
            "upper_bound": _text(value),
            "policy_count": len(plans),
            "support_size": len(support),
        },
    }


def _primary_departures(
    settings: _Settings,
    profiles: tuple[Vector, ...],
    symbols: tuple[str, ...],
    diagnostic: tuple[tuple[Fraction, ...], tuple[Fraction, ...]],
    homogeneous: bool,
) -> dict[str, Any]:
    rates = (
        tuple((epsilon, epsilon) for epsilon in settings.epsilons)
        if homogeneous
        else tuple(itertools.product(settings.epsilons, repeat=2))
    )
    base: list[Vector] = []
    for first, second in rates:
        weights = (
            (ZERO, 1 - first, ZERO, first / 3, first / 3, first / 3),
            (ZERO, 1 - second, ZERO, second / 3, second / 3, second / 3),
        )
        value = [ZERO, ZERO]
        for profile_index, (i, j) in enumerate(itertools.product(range(6), repeat=2)):
            mass = weights[0][i] * weights[1][j]
            for regime in range(2):
                value[regime] += mass * profiles[profile_index][regime]
        base.append((value[0], value[1]))
    best_value = Fraction(-1)
    selected: tuple[int, ...] = ()
    selected_vector = (ZERO, ZERO)
    for assignment in itertools.product(range(len(rates)), repeat=len(symbols)):
        values = tuple(
            sum((diagnostic[r][z] * base[index][r] for z, index in enumerate(assignment)), ZERO)
            for r in range(2)
        )
        if min(values) > best_value:
            best_value = min(values)
            selected = assignment
            selected_vector = (values[0], values[1])
    return {
        "epsilon_by_diagnostic": {
            symbol: [_text(epsilon) for epsilon in rates[selected[z]]]
            for z, symbol in enumerate(symbols)
        },
        "by_regime": _vector_json(selected_vector),
        "worst_case": _text(best_value),
        "candidate_count": len(rates) ** len(symbols),
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gaps = [_fraction(row["contrasts"]["mixture_minus_deterministic"]) for row in rows]
    return {
        "cell_count": len(rows),
        "deterministic_plan_count": sum(len(row["plans"]) for row in rows),
        "positive_mixture_gap_cells": [
            row["cell"]["id"] for row, gap in zip(rows, gaps, strict=True) if gap > 0
        ],
        "zero_mixture_gap_cells": [
            row["cell"]["id"] for row, gap in zip(rows, gaps, strict=True) if gap == 0
        ],
        "maximum_mixture_gap": _text(max(gaps)),
        "evidence_scope": "exact-finite-six-role-class-not-unrestricted-policies",
    }


def run(config: dict[str, Any]) -> dict[str, Any]:
    """Evaluate the registered cells without writing files or running verification.

    Root must enforce the total run-plus-verifier wall and memory limits. Small
    nonempty cell subsets are accepted only to support focused development tests.
    """
    settings = _parse(config)
    deadline = time.monotonic() + settings.time_cap
    cache: dict[tuple[Fraction, int], tuple[Vector, ...]] = {}
    rows: list[dict[str, Any]] = []
    for cell in settings.cells:
        if time.monotonic() > deadline:
            raise TimeoutError("track-02 primary time cap exceeded")
        key = (cell.rho, cell.threshold)
        if key not in cache:
            cache[key] = _primary_profile_values(settings, cell)
        profile_values = cache[key]
        symbols, diagnostic = _primary_diagnostic(settings, cell.diagnostic)
        plans = _primary_plans(profile_values, diagnostic)
        pure = max(plans, key=lambda plan: min(plan.values))
        nominal = max(plans, key=lambda plan: plan.values[0])
        mixture = _solve_mixture(plans)
        departures = {
            label: _primary_departures(settings, profile_values, symbols, diagnostic, homogeneous)
            for label, homogeneous in (("homogeneous", True), ("heterogeneous", False))
        }
        known_prior = []
        for prior in settings.priors:
            selected = max(
                plans, key=lambda plan: prior * plan.values[0] + (1 - prior) * plan.values[1]
            )
            known_prior.append(
                {
                    "prior_a": _text(prior),
                    **_choice(selected),
                    "expected_success": _text(
                        prior * selected.values[0] + (1 - prior) * selected.values[1]
                    ),
                }
            )
        pure_value = min(pure.values)
        rows.append(
            {
                "cell": {
                    "id": cell.identifier,
                    "rho": _text(cell.rho),
                    "diagnostic": cell.diagnostic,
                    "threshold": cell.threshold,
                },
                "source_branch_probabilities": {
                    "shared": _text(cell.rho),
                    "independent": _text(1 - cell.rho),
                },
                "diagnostic_probabilities": {
                    regime: {symbol: _text(diagnostic[r][z]) for z, symbol in enumerate(symbols)}
                    for r, regime in enumerate(REGIMES)
                },
                "profile_payoffs": [
                    {"profile_id": i, "roles": list(PROFILES[i]), "by_regime": _vector_json(values)}
                    for i, values in enumerate(profile_values)
                ],
                "plans": [
                    {
                        "plan_id": _plan_id(plan.index),
                        "profile_ids": list(plan.profiles),
                        "roles_by_diagnostic": {
                            symbol: list(PROFILES[plan.profiles[z]])
                            for z, symbol in enumerate(symbols)
                        },
                        "by_regime": _vector_json(plan.values),
                    }
                    for plan in plans
                ],
                "deterministic_maximin": _choice(pure),
                "coordinated_mixture": mixture,
                "nominal_a": _choice(nominal),
                "known_prior": known_prior,
                "independent_departures": departures,
                "contrasts": {
                    "mixture_minus_deterministic": _text(
                        _fraction(mixture["worst_case"]) - pure_value
                    ),
                    "homogeneous_departure_minus_deterministic": _text(
                        _fraction(departures["homogeneous"]["worst_case"]) - pure_value
                    ),
                    "heterogeneous_departure_minus_deterministic": _text(
                        _fraction(departures["heterogeneous"]["worst_case"]) - pure_value
                    ),
                },
            }
        )
    if time.monotonic() > deadline:
        raise TimeoutError("track-02 primary time cap exceeded")
    return {
        "schema_version": "dd-024-robustness-result-v1",
        "study_id": "DD-024",
        "track_id": "track-02",
        "input_config": copy.deepcopy(config),
        "rows": rows,
        "summary": _summary(rows),
    }


# Verification below deliberately does not call any primary scientific helper.
# Rational parsing/formatting and immutable role identifiers are shared utilities.


def _v_roles(private: int, public: int) -> tuple[int, ...]:
    contrary = public if private == public else next(iter({0, 1, 2}.difference({private, public})))
    return private, public, contrary, 0, 1, 2


def _v_departures(
    settings: _Settings,
    cell: _Cell,
    symbols: tuple[str, ...],
    diagnostic: tuple[tuple[Fraction, ...], tuple[Fraction, ...]],
    homogeneous: bool,
) -> dict[str, Any]:
    """Enumerate public evidence and each independent departure device."""
    rates = [
        (left, right)
        for left in settings.epsilons
        for right in settings.epsilons
        if not homogeneous or left == right
    ]
    conditional: dict[tuple[int, int], Vector] = {}
    for z in range(len(symbols)):
        for rate_index, (left, right) in enumerate(rates):
            totals = [ZERO, ZERO]
            devices = (
                [("shared", 1 - left)] + [(str(k), left / 3) for k in range(3)],
                [("shared", 1 - right)] + [(str(k), right / 3) for k in range(3)],
            )
            for r, (_, public_accuracy) in enumerate(settings.accuracies):
                for target in range(3):
                    for public in range(3):
                        public_probability = (
                            public_accuracy if target == public else (1 - public_accuracy) / 2
                        )
                        for first, second in itertools.product(*devices):
                            first_action = public if first[0] == "shared" else int(first[0])
                            second_action = public if second[0] == "shared" else int(second[0])
                            correct = int(first_action == target) + int(second_action == target)
                            if correct >= cell.threshold:
                                totals[r] += (
                                    diagnostic[r][z] * public_probability * first[1] * second[1] / 3
                                )
            conditional[(z, rate_index)] = (totals[0], totals[1])
    best = Fraction(-1)
    answer: dict[str, Any] = {}
    for choices in itertools.product(range(len(rates)), repeat=len(symbols)):
        totals = [ZERO, ZERO]
        for z, rate_index in enumerate(choices):
            for r in range(2):
                totals[r] += conditional[(z, rate_index)][r]
        candidate = min(totals)
        if candidate > best:
            best = candidate
            answer = {
                "epsilon_by_diagnostic": {
                    symbol: [_text(rate) for rate in rates[choices[z]]]
                    for z, symbol in enumerate(symbols)
                },
                "by_regime": {"A": _text(totals[0]), "B": _text(totals[1])},
                "worst_case": _text(candidate),
                "candidate_count": len(rates) ** len(symbols),
            }
    return answer


def _reference(settings: _Settings, cell: _Cell) -> _Reference:
    """Directly enumerate the joint latent/source/clue/diagnostic distribution."""
    symbols = ("none",) if cell.diagnostic == "none" else ("A", "B")
    correctness = settings.diagnostic_accuracy[cell.diagnostic]
    diagnostic_lists: list[tuple[Fraction, ...]] = []
    for regime in REGIMES:
        diagnostic_lists.append(
            tuple(
                ONE if correctness is None else correctness if symbol == regime else 1 - correctness
                for symbol in symbols
            )
        )
    diagnostic = (diagnostic_lists[0], diagnostic_lists[1])
    joint = [[[ZERO for _ in range(36)] for _ in symbols] for _ in REGIMES]
    normalizations = [[ZERO for _ in symbols] for _ in REGIMES]
    for r, (private_accuracy, public_accuracy) in enumerate(settings.accuracies):
        for target in range(3):
            public_law = {
                label: public_accuracy if label == target else (1 - public_accuracy) / 2
                for label in range(3)
            }
            private_law = {
                label: private_accuracy if label == target else (1 - private_accuracy) / 2
                for label in range(3)
            }
            branches = [(x, x, cell.rho * private_law[x]) for x in range(3)] + [
                (x, y, (1 - cell.rho) * private_law[x] * private_law[y])
                for x in range(3)
                for y in range(3)
            ]
            for public in range(3):
                for first, second, private_probability in branches:
                    for z in range(len(symbols)):
                        mass = public_law[public] * private_probability * diagnostic[r][z] / 3
                        normalizations[r][z] += mass
                        if not mass:
                            continue
                        first_actions = _v_roles(first, public)
                        second_actions = _v_roles(second, public)
                        for i in range(6):
                            for j in range(6):
                                correct = int(first_actions[i] == target)
                                correct += int(second_actions[j] == target)
                                if correct >= cell.threshold:
                                    joint[r][z][6 * i + j] += mass
    for r in range(2):
        if tuple(normalizations[r]) != diagnostic[r] or sum(normalizations[r]) != 1:
            raise ArithmeticError("independent joint-state normalization failed")
    profiles = tuple(
        (
            sum((joint[0][z][i] for z in range(len(symbols))), ZERO),
            sum((joint[1][z][i] for z in range(len(symbols))), ZERO),
        )
        for i in range(36)
    )
    plans: list[_Plan] = []
    for assignment in itertools.product(range(36), repeat=len(symbols)):
        values = [ZERO, ZERO]
        for z, profile in enumerate(assignment):
            for r in range(2):
                values[r] += joint[r][z][profile]
        plans.append(_Plan(len(plans), assignment, (values[0], values[1])))
    departures = {
        name: _v_departures(settings, cell, symbols, diagnostic, homogeneous)
        for name, homogeneous in (("homogeneous", True), ("heterogeneous", False))
    }
    return _Reference(
        cell, symbols, diagnostic, profiles, tuple(plans), departures, 2 * len(symbols)
    )


def _v_choice(plan: _Plan) -> dict[str, Any]:
    return {
        "plan_id": f"d{plan.index:04d}",
        "by_regime": {"A": _text(plan.values[0]), "B": _text(plan.values[1])},
        "worst_case": _text(min(plan.values)),
    }


def _v_row(
    settings: _Settings, reference: _Reference, row: dict[str, Any]
) -> tuple[list[str], Fraction]:
    problems: list[str] = []
    cell = reference.cell

    def require(condition: bool, message: str) -> None:
        if not condition:
            problems.append(f"{cell.identifier}: {message}")

    require(
        row["cell"]
        == {
            "id": cell.identifier,
            "rho": _text(cell.rho),
            "diagnostic": cell.diagnostic,
            "threshold": cell.threshold,
        },
        "cell specification mismatch",
    )
    require(
        row["source_branch_probabilities"]
        == {"shared": _text(cell.rho), "independent": _text(1 - cell.rho)},
        "source-branch probability mismatch",
    )
    require(
        row["diagnostic_probabilities"]
        == {
            regime: {
                symbol: _text(reference.diagnostic[r][z])
                for z, symbol in enumerate(reference.symbols)
            }
            for r, regime in enumerate(REGIMES)
        },
        "diagnostic probability mismatch",
    )
    require(len(row["profile_payoffs"]) == 36, "incomplete profile-payoff table")
    for i, record in enumerate(row["profile_payoffs"]):
        require(record["profile_id"] == i, "profile identifier mismatch")
        require(record["roles"] == list(PROFILES[i]), "profile action-role mismatch")
        require(
            _vector_read(record["by_regime"]) == reference.profiles[i],
            "profile payoff differs from direct state enumeration",
        )
    require(len(row["plans"]) == len(reference.plans), "incomplete deterministic-plan table")
    for plan, record in zip(reference.plans, row["plans"], strict=True):
        require(record["plan_id"] == f"d{plan.index:04d}", "plan identifier mismatch")
        require(record["profile_ids"] == list(plan.profiles), "plan assignment mismatch")
        require(
            record["roles_by_diagnostic"]
            == {
                symbol: list(PROFILES[plan.profiles[z]])
                for z, symbol in enumerate(reference.symbols)
            },
            "saved diagnostic-contingent roles mismatch",
        )
        require(
            _vector_read(record["by_regime"]) == plan.values,
            "plan payoff differs from direct state enumeration",
        )
        require(all(0 <= value <= 1 for value in plan.values), "probability outside [0,1]")
    pure = max(reference.plans, key=lambda plan: min(plan.values))
    nominal = max(reference.plans, key=lambda plan: plan.values[0])
    require(row["deterministic_maximin"] == _v_choice(pure), "pure optimum/tie rule mismatch")
    require(row["nominal_a"] == _v_choice(nominal), "nominal optimum/tie rule mismatch")
    require(
        row["independent_departures"] == reference.departures,
        "departure grid optimum differs from direct device enumeration",
    )
    mixture = row["coordinated_mixture"]
    require(1 <= len(mixture["support"]) <= 2, "invalid mixture support size")
    lookup = {f"d{plan.index:04d}": plan.values for plan in reference.plans}
    mixture_mass = ZERO
    mixed_values = [ZERO, ZERO]
    seen_support: set[str] = set()
    for member in mixture["support"]:
        identifier = member["plan_id"]
        require(identifier not in seen_support, "duplicate mixture support")
        seen_support.add(identifier)
        weight = _fraction(member["weight"])
        require(weight > 0, "mixture weights must be positive")
        mixture_mass += weight
        for r in range(2):
            mixed_values[r] += weight * lookup[identifier][r]
    require(mixture_mass == 1, "mixture weights do not sum to one")
    require(
        _vector_read(mixture["by_regime"]) == (mixed_values[0], mixed_values[1]),
        "saved mixed payoff does not execute the saved mixture",
    )
    value = _fraction(mixture["worst_case"])
    require(value == min(mixed_values), "mixture worst-regime payoff mismatch")
    certificate = mixture["certificate"]
    prior = _fraction(certificate["regime_a_weight"])
    upper = _fraction(certificate["upper_bound"])
    require(0 <= prior <= 1, "invalid adversarial-prior certificate")
    require(certificate["policy_count"] == len(reference.plans), "dual coverage count mismatch")
    require(certificate["support_size"] == len(mixture["support"]), "support count mismatch")
    require(
        all(
            prior * plan.values[0] + (1 - prior) * plan.values[1] <= upper
            for plan in reference.plans
        ),
        "dual inequality fails for an admissible plan",
    )
    require(upper == value, "dual bound and attaining mixture disagree")
    expected_known = []
    for known in settings.priors:
        selected = max(
            reference.plans, key=lambda plan: known * plan.values[0] + (1 - known) * plan.values[1]
        )
        expected_value = known * selected.values[0] + (1 - known) * selected.values[1]
        expected_known.append(
            {
                "prior_a": _text(known),
                **_v_choice(selected),
                "expected_success": _text(expected_value),
            }
        )
        require(
            known * mixed_values[0] + (1 - known) * mixed_values[1] <= expected_value,
            "known-prior deterministic sufficiency violated",
        )
        for departure in reference.departures.values():
            depart_vector = _vector_read(departure["by_regime"])
            require(
                known * depart_vector[0] + (1 - known) * depart_vector[1] <= expected_value,
                "departure policy exceeds known-prior deterministic optimum",
            )
    require(row["known_prior"] == expected_known, "known-prior optimum/tie rule mismatch")
    homogeneous = _fraction(reference.departures["homogeneous"]["worst_case"])
    heterogeneous = _fraction(reference.departures["heterogeneous"]["worst_case"])
    require(homogeneous <= heterogeneous <= value, "nested randomized policy classes disagree")
    require(value >= min(pure.values), "mixture class fails to include pure plans")
    gap = value - min(pure.values)
    if cell.diagnostic == "perfect":
        require(gap == 0, "perfect diagnostic leaves a robust-randomization gap")
    require(
        row["contrasts"]
        == {
            "mixture_minus_deterministic": _text(gap),
            "homogeneous_departure_minus_deterministic": _text(homogeneous - min(pure.values)),
            "heterogeneous_departure_minus_deterministic": _text(heterogeneous - min(pure.values)),
        },
        "saved contrasts mismatch independently checked policies",
    )
    for i, values in enumerate(reference.profiles):
        first, second = divmod(i, 6)
        require(values == reference.profiles[6 * second + first], "agent exchange failed")
        for permutation in itertools.permutations(range(3)):
            relabeled = tuple(
                role if role < 3 else 3 + permutation[role - 3] for role in (first, second)
            )
            require(
                values == reference.profiles[6 * relabeled[0] + relabeled[1]],
                "target relabeling failed",
            )
    for r, (p, q) in enumerate(settings.accuracies):
        independent = 1 - (1 - p) ** 2 if cell.threshold == 1 else p**2
        require(
            reference.profiles[0][r] == cell.rho * p + (1 - cell.rho) * independent,
            "private-following source endpoint identity failed",
        )
        require(reference.profiles[7][r] == q, "shared-following threshold identity failed")
    return problems, gap


def _check_result(
    config: dict[str, Any],
    settings: _Settings,
    references: tuple[_Reference, ...],
    result: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    try:
        if result["schema_version"] != "dd-024-robustness-result-v1":
            errors.append("result schema mismatch")
        if (result["study_id"], result["track_id"]) != ("DD-024", "track-02"):
            errors.append("result identity mismatch")
        if result["input_config"] != config:
            errors.append("embedded configuration mismatch")
        rows = result["rows"]
        if len(rows) != len(references):
            errors.append("incomplete or extra cell rows")
        gaps: list[Fraction] = []
        for reference, row in zip(references, rows, strict=True):
            row_errors, gap = _v_row(settings, reference, row)
            errors.extend(row_errors)
            gaps.append(gap)
        expected_summary = {
            "cell_count": len(references),
            "deterministic_plan_count": sum(len(reference.plans) for reference in references),
            "positive_mixture_gap_cells": [
                reference.cell.identifier
                for reference, gap in zip(references, gaps, strict=True)
                if gap > 0
            ],
            "zero_mixture_gap_cells": [
                reference.cell.identifier
                for reference, gap in zip(references, gaps, strict=True)
                if gap == 0
            ],
            "maximum_mixture_gap": _text(max(gaps)),
            "evidence_scope": "exact-finite-six-role-class-not-unrestricted-policies",
        }
        if result["summary"] != expected_summary:
            errors.append("summary differs from independently checked cells")
        paired = {
            (ref.cell.rho, ref.cell.diagnostic, ref.cell.threshold): ref for ref in references
        }
        for reference in references:
            if reference.cell.threshold == 2:
                other = paired.get((reference.cell.rho, reference.cell.diagnostic, 1))
                if other is not None and any(
                    reference.profiles[i][r] > other.profiles[i][r]
                    for i in range(36)
                    for r in range(2)
                ):
                    errors.append("two-success event exceeds the matching one-success event")
    except (KeyError, TypeError, ValueError, IndexError, AttributeError, ZeroDivisionError) as exc:
        errors.append(f"malformed or incomplete result: {type(exc).__name__}: {exc}")
    return errors


def verify(config: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Independently verify all cells and require four corruptions to be rejected.

    The returned corruption booleans are true exactly when the modified result
    was rejected. Reference enumeration is performed once and reused only for
    checking mutations; no primary optimizer or probability evaluator is called.
    """
    try:
        settings = _parse(config)
        references = tuple(_reference(settings, cell) for cell in settings.cells)
        errors = _check_result(config, settings, references, result)
    except (ValueError, ArithmeticError) as exc:
        return {"passed": False, "checks": {}, "errors": [str(exc)], "corruptions": {}}
    checks = {
        "method": "direct-joint-state-enumeration-and-all-policy-dual-inequalities",
        "cell_count": len(references),
        "plan_vectors_checked": sum(len(reference.plans) for reference in references),
        "normalization_checks": sum(reference.mass_checks for reference in references),
        "primary_scientific_helpers_called": False,
        "source_scope": "six-role-library-with-diagnostic-only-role-assignment",
        "checks_include": [
            "complete-policy-coverage",
            "probability-bounds",
            "saved-policy-execution",
            "primal-dual-equality",
            "same-diagnostic-budget",
            "known-prior-purification",
            "independent-device-enumeration",
            "agent-and-target-permutations",
            "source-endpoint-identities",
            "perfect-diagnostic-limit",
            "threshold-event-containment-when-paired",
            "summary-reconciliation",
        ],
    }
    corruptions: dict[str, bool] = {}
    if not errors:
        for name in (
            "mixture_weight",
            "source_branch_probability",
            "diagnostic_probability",
            "dual_upper_bound",
        ):
            damaged = copy.deepcopy(result)
            first_row = damaged["rows"][0]
            if name == "mixture_weight":
                member = first_row["coordinated_mixture"]["support"][0]
                member["weight"] = _text(_fraction(member["weight"]) + Fraction(1, 7))
            elif name == "source_branch_probability":
                source = first_row["source_branch_probabilities"]
                source["shared"] = _text(_fraction(source["shared"]) + Fraction(1, 7))
            elif name == "diagnostic_probability":
                law = first_row["diagnostic_probabilities"]["A"]
                symbol = next(iter(law))
                law[symbol] = _text(_fraction(law[symbol]) + Fraction(1, 7))
            else:
                certificate = first_row["coordinated_mixture"]["certificate"]
                certificate["upper_bound"] = _text(
                    _fraction(certificate["upper_bound"]) + Fraction(1, 7)
                )
            corruptions[name] = bool(_check_result(config, settings, references, damaged))
        errors.extend(
            f"corruption was not rejected: {name}"
            for name, rejected in corruptions.items()
            if not rejected
        )
    return {"passed": not errors, "checks": checks, "errors": errors, "corruptions": corruptions}
