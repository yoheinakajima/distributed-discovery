"""Exact joint-column count-budget relaxation for private discovery teams."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

FractionTable = tuple[tuple[Fraction | None, ...], ...]
PredecessorTable = tuple[tuple[int | None, ...], ...]


@dataclass(frozen=True)
class AlignmentBoundResult:
    """Exact dynamic-program result and its Bellman certificate tables."""

    candidates: int
    searchers: int
    accuracy: Fraction
    false_label_accuracy: Fraction
    local_failure_floors: tuple[Fraction, ...]
    column_values: FractionTable
    column_predecessors: PredecessorTable
    target_values: FractionTable
    target_predecessors: PredecessorTable
    target_resource_pattern: tuple[int, ...]
    average_failure_lower_bound: Fraction
    discovery_upper_bound: Fraction
    column_transition_count: int
    target_transition_count: int


def _validate_parameters(candidates: int, searchers: int, accuracy: Fraction) -> None:
    if candidates < 2:
        raise ValueError("candidates must be at least two")
    if searchers < 1:
        raise ValueError("searchers must be positive")
    if not 0 <= accuracy <= 1:
        raise ValueError("accuracy must lie in [0,1]")


def local_failure_floor(candidates: int, accuracy: Fraction, incoming_count: int) -> Fraction:
    """Return the smallest locally possible failure factor for one target column.

    The fixed-point indicator is forced to zero at count zero and one at count M.
    At intermediate counts either value is locally possible. Dropping all other
    single-policy feasibility constraints is an admissible relaxation.
    """

    _validate_parameters(candidates, 1, accuracy)
    if not 0 <= incoming_count <= candidates:
        raise ValueError("incoming_count must lie in [0,candidates]")
    false_accuracy = (1 - accuracy) / (candidates - 1)
    fixed_values: tuple[int, ...]
    if incoming_count == 0:
        fixed_values = (0,)
    elif incoming_count == candidates:
        fixed_values = (1,)
    else:
        fixed_values = (0, 1)
    failures = tuple(
        1 - (false_accuracy * incoming_count + (accuracy - false_accuracy) * fixed_indicator)
        for fixed_indicator in fixed_values
    )
    if any(not 0 <= value <= 1 for value in failures):
        raise AssertionError("local conditional failure must be a probability")
    return min(failures)


def alignment_count_bound(
    candidates: int, searchers: int, accuracy: Fraction
) -> AlignmentBoundResult:
    """Compute the exact alignment-preserving global count-budget upper bound.

    For each target, the first dynamic program minimizes its joint failure over
    the searchers at every total incoming-count resource. The second allocates the
    globally necessary ``M*N`` incoming counts across the ``M`` target columns.
    Per-agent cross-target budgets and Hall feasibility are deliberately relaxed,
    so every feasible deterministic team embeds in the optimized superset.
    """

    _validate_parameters(candidates, searchers, accuracy)
    total_resource = candidates * searchers
    false_accuracy = (1 - accuracy) / (candidates - 1)
    floors = tuple(
        local_failure_floor(candidates, accuracy, count) for count in range(candidates + 1)
    )

    column_values: list[list[Fraction | None]] = [
        [None for _ in range(total_resource + 1)] for _ in range(searchers + 1)
    ]
    column_predecessors: list[list[int | None]] = [
        [None for _ in range(total_resource + 1)] for _ in range(searchers + 1)
    ]
    column_values[0][0] = Fraction(1)
    column_transitions = 0
    for used_searchers in range(1, searchers + 1):
        maximum_resource = used_searchers * candidates
        for resource in range(maximum_resource + 1):
            best: Fraction | None = None
            best_count: int | None = None
            for count in range(candidates + 1):
                prior_resource = resource - count
                if prior_resource < 0:
                    continue
                prior = column_values[used_searchers - 1][prior_resource]
                if prior is None:
                    continue
                column_transitions += 1
                candidate = prior * floors[count]
                if best is None or candidate < best:
                    best = candidate
                    best_count = count
            column_values[used_searchers][resource] = best
            column_predecessors[used_searchers][resource] = best_count

    column_frontier = column_values[searchers]
    if any(value is None for value in column_frontier):
        raise AssertionError("every joint-column resource must be reachable")

    target_values: list[list[Fraction | None]] = [
        [None for _ in range(total_resource + 1)] for _ in range(candidates + 1)
    ]
    target_predecessors: list[list[int | None]] = [
        [None for _ in range(total_resource + 1)] for _ in range(candidates + 1)
    ]
    target_values[0][0] = Fraction(0)
    target_transitions = 0
    for used_targets in range(1, candidates + 1):
        for resource in range(total_resource + 1):
            target_best: Fraction | None = None
            best_column_resource: int | None = None
            for column_resource, column_failure in enumerate(column_frontier):
                prior_resource = resource - column_resource
                if prior_resource < 0:
                    break
                prior = target_values[used_targets - 1][prior_resource]
                if prior is None or column_failure is None:
                    continue
                target_transitions += 1
                candidate = prior + column_failure
                if target_best is None or candidate < target_best:
                    target_best = candidate
                    best_column_resource = column_resource
            target_values[used_targets][resource] = target_best
            target_predecessors[used_targets][resource] = best_column_resource

    total_failure = target_values[candidates][total_resource]
    if total_failure is None:
        raise AssertionError("canonical total incoming-count resource must be reachable")
    target_pattern: list[int] = []
    remaining = total_resource
    for used_targets in range(candidates, 0, -1):
        witness_resource = target_predecessors[used_targets][remaining]
        if witness_resource is None:
            raise AssertionError("missing target-allocation predecessor")
        target_pattern.append(witness_resource)
        remaining -= witness_resource
    if remaining != 0:
        raise AssertionError("target-allocation witness did not consume the resource")
    target_pattern.reverse()

    average_failure = total_failure / candidates
    return AlignmentBoundResult(
        candidates=candidates,
        searchers=searchers,
        accuracy=accuracy,
        false_label_accuracy=false_accuracy,
        local_failure_floors=floors,
        column_values=tuple(tuple(row) for row in column_values),
        column_predecessors=tuple(tuple(row) for row in column_predecessors),
        target_values=tuple(tuple(row) for row in target_values),
        target_predecessors=tuple(tuple(row) for row in target_predecessors),
        target_resource_pattern=tuple(target_pattern),
        average_failure_lower_bound=average_failure,
        discovery_upper_bound=1 - average_failure,
        column_transition_count=column_transitions,
        target_transition_count=target_transitions,
    )


def _fraction_table(table: FractionTable) -> list[list[str | None]]:
    return [[None if value is None else str(value) for value in row] for row in table]


def alignment_bound_certificate(result: AlignmentBoundResult) -> dict[str, Any]:
    """Serialize a complete exact Bellman certificate for independent checking."""

    total_resource = result.candidates * result.searchers
    return {
        "schema_version": 1,
        "method": "joint-target-column global-count-budget relaxation",
        "parameters": {
            "candidates": result.candidates,
            "searchers": result.searchers,
            "accuracy": str(result.accuracy),
            "false_label_accuracy": str(result.false_label_accuracy),
            "total_incoming_count": total_resource,
        },
        "relaxation": {
            "retained": "joint searcher incoming counts within every target column",
            "relaxed": (
                "per-searcher cross-target count budgets, fixed-point patterns, and residual "
                "Hall feasibility; only their globally necessary incoming-count total remains"
            ),
            "embedding_basis": (
                "every deterministic policy has nonnegative incoming counts summing to M; "
                "therefore every N-policy profile has global total M*N"
            ),
        },
        "local_failure_floors": [str(value) for value in result.local_failure_floors],
        "column_dp": {
            "values": _fraction_table(result.column_values),
            "predecessor_incoming_counts": [list(row) for row in result.column_predecessors],
            "transition_count": result.column_transition_count,
        },
        "target_dp": {
            "values": _fraction_table(result.target_values),
            "predecessor_column_resources": [list(row) for row in result.target_predecessors],
            "transition_count": result.target_transition_count,
        },
        "witness": {
            "target_resource_pattern": list(result.target_resource_pattern),
            "resource_sum": sum(result.target_resource_pattern),
        },
        "result": {
            "average_failure_lower_bound": str(result.average_failure_lower_bound),
            "discovery_upper_bound": str(result.discovery_upper_bound),
            "upper_bound_attained_by_relaxation": True,
        },
    }
