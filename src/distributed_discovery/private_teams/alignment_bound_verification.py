"""Independent Bellman-potential verifier for DD-001 alignment-bound certificates."""

from __future__ import annotations

from fractions import Fraction
from typing import Any


def _parse_fraction(value: object, label: str, errors: list[str]) -> Fraction | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an exact fraction string")
        return None
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError):
        errors.append(f"{label} is not a valid exact fraction")
        return None


def _parse_table(value: object, label: str, errors: list[str]) -> list[list[Fraction | None]]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    table: list[list[Fraction | None]] = []
    for row_index, raw_row in enumerate(value):
        if not isinstance(raw_row, list):
            errors.append(f"{label}[{row_index}] must be a list")
            return []
        row = [
            None
            if cell is None
            else _parse_fraction(cell, f"{label}[{row_index}][{column}]", errors)
            for column, cell in enumerate(raw_row)
        ]
        table.append(row)
    return table


def _parse_predecessors(value: object, label: str, errors: list[str]) -> list[list[int | None]]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    parsed: list[list[int | None]] = []
    for row_index, raw_row in enumerate(value):
        if not isinstance(raw_row, list):
            errors.append(f"{label}[{row_index}] must be a list")
            return []
        row: list[int | None] = []
        for column, cell in enumerate(raw_row):
            if cell is not None and (not isinstance(cell, int) or isinstance(cell, bool)):
                errors.append(f"{label}[{row_index}][{column}] must be an integer or null")
                row.append(None)
            else:
                row.append(cell)
        parsed.append(row)
    return parsed


def _local_floors(candidates: int, accuracy: Fraction) -> list[Fraction]:
    false_accuracy = (1 - accuracy) / (candidates - 1)
    floors = []
    for incoming_count in range(candidates + 1):
        fixed_values: tuple[int, ...]
        if incoming_count == 0:
            fixed_values = (0,)
        elif incoming_count == candidates:
            fixed_values = (1,)
        else:
            fixed_values = (0, 1)
        floors.append(
            min(
                1
                - (false_accuracy * incoming_count + (accuracy - false_accuracy) * fixed_indicator)
                for fixed_indicator in fixed_values
            )
        )
    return floors


def verify_alignment_bound_certificate(certificate: dict[str, Any]) -> list[str]:
    """Check exact Bellman inequalities and equality witnesses without optimizing."""

    errors: list[str] = []
    if certificate.get("schema_version") != 1:
        errors.append("unsupported schema version")
    parameters = certificate.get("parameters")
    if not isinstance(parameters, dict):
        return [*errors, "parameters must be an object"]
    candidates = parameters.get("candidates")
    searchers = parameters.get("searchers")
    if not isinstance(candidates, int) or isinstance(candidates, bool) or candidates < 2:
        return [*errors, "candidates must be an integer at least two"]
    if not isinstance(searchers, int) or isinstance(searchers, bool) or searchers < 1:
        return [*errors, "searchers must be a positive integer"]
    accuracy = _parse_fraction(parameters.get("accuracy"), "accuracy", errors)
    false_accuracy = _parse_fraction(
        parameters.get("false_label_accuracy"), "false_label_accuracy", errors
    )
    if accuracy is None or false_accuracy is None:
        return errors
    if not 0 <= accuracy <= 1:
        errors.append("accuracy must lie in [0,1]")
        return errors
    expected_false_accuracy = (1 - accuracy) / (candidates - 1)
    if false_accuracy != expected_false_accuracy:
        errors.append("false-label accuracy does not match the model")
    total_resource = candidates * searchers
    if parameters.get("total_incoming_count") != total_resource:
        errors.append("total incoming count must equal candidates times searchers")

    expected_floors = _local_floors(candidates, accuracy)
    raw_floors = certificate.get("local_failure_floors")
    if not isinstance(raw_floors, list) or len(raw_floors) != candidates + 1:
        errors.append("local failure floor vector has the wrong length")
        return errors
    floors = [
        _parse_fraction(value, f"local_failure_floors[{index}]", errors)
        for index, value in enumerate(raw_floors)
    ]
    if any(value is None for value in floors):
        return errors
    exact_floors = [value for value in floors if value is not None]
    if exact_floors != expected_floors:
        errors.append("local failure floors do not match the signal law")

    column = certificate.get("column_dp")
    target = certificate.get("target_dp")
    if not isinstance(column, dict) or not isinstance(target, dict):
        return [*errors, "column_dp and target_dp must be objects"]
    column_values = _parse_table(column.get("values"), "column values", errors)
    column_predecessors = _parse_predecessors(
        column.get("predecessor_incoming_counts"), "column predecessors", errors
    )
    target_values = _parse_table(target.get("values"), "target values", errors)
    target_predecessors = _parse_predecessors(
        target.get("predecessor_column_resources"), "target predecessors", errors
    )
    expected_width = total_resource + 1
    if (
        len(column_values) != searchers + 1
        or len(column_predecessors) != searchers + 1
        or any(len(row) != expected_width for row in column_values)
        or any(len(row) != expected_width for row in column_predecessors)
    ):
        errors.append("column Bellman tables have invalid dimensions")
        return errors
    if (
        len(target_values) != candidates + 1
        or len(target_predecessors) != candidates + 1
        or any(len(row) != expected_width for row in target_values)
        or any(len(row) != expected_width for row in target_predecessors)
    ):
        errors.append("target Bellman tables have invalid dimensions")
        return errors

    for resource in range(expected_width):
        expected = Fraction(1) if resource == 0 else None
        if column_values[0][resource] != expected or column_predecessors[0][resource] is not None:
            errors.append(f"invalid column base state at resource {resource}")
    for used_searchers in range(1, searchers + 1):
        for resource in range(expected_width):
            value = column_values[used_searchers][resource]
            predecessor = column_predecessors[used_searchers][resource]
            reachable = resource <= used_searchers * candidates
            if not reachable:
                if value is not None or predecessor is not None:
                    errors.append(
                        f"unreachable column state is populated at {used_searchers},{resource}"
                    )
                continue
            if value is None or predecessor is None:
                errors.append(f"reachable column state is missing at {used_searchers},{resource}")
                continue
            candidates_for_state: list[tuple[int, Fraction]] = []
            for incoming_count in range(candidates + 1):
                prior_resource = resource - incoming_count
                if prior_resource < 0:
                    continue
                prior = column_values[used_searchers - 1][prior_resource]
                if prior is not None:
                    candidates_for_state.append(
                        (incoming_count, prior * expected_floors[incoming_count])
                    )
            if any(value > candidate for _, candidate in candidates_for_state):
                errors.append(
                    f"column Bellman lower inequality fails at {used_searchers},{resource}"
                )
            witness_values = [
                candidate for count, candidate in candidates_for_state if count == predecessor
            ]
            if not witness_values or value != witness_values[0]:
                errors.append(
                    f"column Bellman equality witness fails at {used_searchers},{resource}"
                )

    column_frontier = column_values[searchers]
    for resource in range(expected_width):
        expected = Fraction(0) if resource == 0 else None
        if target_values[0][resource] != expected or target_predecessors[0][resource] is not None:
            errors.append(f"invalid target base state at resource {resource}")
    for used_targets in range(1, candidates + 1):
        for resource in range(expected_width):
            value = target_values[used_targets][resource]
            predecessor = target_predecessors[used_targets][resource]
            if value is None or predecessor is None:
                errors.append(f"reachable target state is missing at {used_targets},{resource}")
                continue
            candidates_for_state = []
            for column_resource in range(resource + 1):
                prior = target_values[used_targets - 1][resource - column_resource]
                column_failure = column_frontier[column_resource]
                if prior is not None and column_failure is not None:
                    candidates_for_state.append((column_resource, prior + column_failure))
            if any(value > candidate for _, candidate in candidates_for_state):
                errors.append(f"target Bellman lower inequality fails at {used_targets},{resource}")
            witness_values = [
                candidate for count, candidate in candidates_for_state if count == predecessor
            ]
            if not witness_values or value != witness_values[0]:
                errors.append(f"target Bellman equality witness fails at {used_targets},{resource}")

    witness = certificate.get("witness")
    if not isinstance(witness, dict):
        errors.append("witness must be an object")
    else:
        pattern = witness.get("target_resource_pattern")
        if (
            not isinstance(pattern, list)
            or len(pattern) != candidates
            or any(not isinstance(value, int) or isinstance(value, bool) for value in pattern)
            or any(not 0 <= value <= total_resource for value in pattern)
        ):
            errors.append("target resource pattern is invalid")
        else:
            if sum(pattern) != total_resource or witness.get("resource_sum") != total_resource:
                errors.append("target resource witness has the wrong total")
            witness_failure = Fraction(0)
            for value in pattern:
                column_failure = column_frontier[value]
                if column_failure is None:
                    errors.append("target resource witness uses an unreachable column resource")
                    break
                witness_failure += column_failure
            if witness_failure != target_values[candidates][total_resource]:
                errors.append("target resource witness does not attain the certified failure")

    result = certificate.get("result")
    if not isinstance(result, dict):
        errors.append("result must be an object")
        return errors
    failure = _parse_fraction(
        result.get("average_failure_lower_bound"), "average failure lower bound", errors
    )
    upper = _parse_fraction(result.get("discovery_upper_bound"), "discovery upper bound", errors)
    final_sum = target_values[candidates][total_resource]
    if failure is not None and final_sum is not None and failure != final_sum / candidates:
        errors.append("average failure bound does not match the target Bellman table")
    if failure is not None and upper is not None and upper != 1 - failure:
        errors.append("discovery upper bound is not one minus the failure bound")
    return errors
