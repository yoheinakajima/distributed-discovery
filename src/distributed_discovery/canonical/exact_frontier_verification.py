"""Independent partition-based verification of exact frontier certificates."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from fractions import Fraction
from math import factorial
from typing import Any


def _partitions(total: int, maximum: int | None = None) -> Iterator[tuple[int, ...]]:
    """Yield decreasing positive integer partitions of total."""

    if total == 0:
        yield ()
        return
    ceiling = min(total, total if maximum is None else maximum)
    for first in range(ceiling, 0, -1):
        for rest in _partitions(total - first, first):
            yield (first, *rest)


def partition_reference_frontier(
    candidates: int, reports: int, accuracy: Fraction
) -> tuple[tuple[Fraction, ...], Fraction, int]:
    """Recompute the frontier from integer partitions, without either primary walker."""

    false_accuracy = (1 - accuracy) / (candidates - 1)
    values = [Fraction(0) for _ in range(reports)]
    mass = Fraction(0)
    orbit_count = 0
    for target_count in range(reports + 1):
        false_reports = reports - target_count
        for partition in _partitions(false_reports):
            if len(partition) > candidates - 1:
                continue
            frequencies = Counter(partition)
            frequencies[0] = candidates - 1 - len(partition)
            multiplicity_numerator = factorial(reports) * factorial(candidates - 1)
            multiplicity_denominator = factorial(target_count)
            for count, label_count in frequencies.items():
                multiplicity_denominator *= factorial(count) ** label_count
                multiplicity_denominator *= factorial(label_count)
            if multiplicity_numerator % multiplicity_denominator:
                raise ArithmeticError("partition multiplicity is not integral")
            multiplicity = multiplicity_numerator // multiplicity_denominator
            weight = (
                multiplicity * accuracy**target_count * false_accuracy ** (reports - target_count)
            )
            mass += weight
            orbit_count += 1
            strictly_above = sum(
                label_count for count, label_count in frequencies.items() if count > target_count
            )
            tied = frequencies[target_count] + 1
            for budget in range(1, reports + 1):
                if strictly_above < budget:
                    values[budget - 1] += weight * Fraction(
                        min(tied, budget - strictly_above), tied
                    )
    return tuple(values), mass, orbit_count


def verify_certificate(certificate: dict[str, Any]) -> list[str]:
    """Return all independent certificate errors; an empty list means acceptance."""

    errors: list[str] = []
    parameters = certificate.get("parameters", {})
    try:
        candidates = int(parameters["candidates"])
        reports = int(parameters["reports"])
        accuracy = Fraction(str(parameters["accuracy"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return ["invalid certificate parameters"]
    reference, mass, orbit_count = partition_reference_frontier(candidates, reports, accuracy)
    if mass != 1:
        errors.append("independent probability mass is not one")
    method_a = certificate.get("method_a", {})
    method_b = certificate.get("method_b", {})
    if method_a.get("probability_mass_fraction") != "1":
        errors.append("method A probability mass mismatch")
    if method_b.get("probability_mass_fraction") != "1":
        errors.append("method B probability mass mismatch")
    if method_b.get("histogram_orbit_count") != orbit_count:
        errors.append("histogram orbit count mismatch")
    rows = certificate.get("frontier")
    if not isinstance(rows, list) or len(rows) != reports:
        return [*errors, "frontier row count mismatch"]
    for budget, expected in enumerate(reference, start=1):
        row = rows[budget - 1]
        try:
            recorded = Fraction(int(row["numerator"]), int(row["denominator"]))
            method_a_value = Fraction(str(row["method_a_fraction"]))
            method_b_value = Fraction(str(row["method_b_fraction"]))
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            errors.append(f"budget {budget} has invalid rational fields")
            continue
        if row.get("budget") != budget:
            errors.append(f"budget {budget} label mismatch")
        if not recorded == method_a_value == method_b_value == expected:
            errors.append(f"budget {budget} exact value mismatch")
    boundary = certificate.get("private_team_interval", {})
    try:
        lower = Fraction(str(boundary["lower_fraction"]))
        upper = Fraction(str(boundary["upper_fraction"]))
        gap = Fraction(str(boundary["gap_fraction"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        errors.append("private-team interval fields are invalid")
    else:
        if upper != reference[-1] or gap != upper - lower or lower > upper:
            errors.append("private-team interval arithmetic mismatch")
    if boundary.get("upper_attainability_claimed") is not False:
        errors.append("certificate must not claim upper-endpoint attainability")
    if boundary.get("global_tightness_claimed") is not False:
        errors.append("certificate must not claim global tightness")
    return errors
