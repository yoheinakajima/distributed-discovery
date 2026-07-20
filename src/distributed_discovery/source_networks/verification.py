"""Independent exact verifier for the DD-003 bounded graph census."""

from __future__ import annotations

import itertools
from collections import defaultdict
from fractions import Fraction
from typing import Any


def _valid(matrix: tuple[tuple[int, ...], ...]) -> bool:
    return all(sum(row) > 0 for row in matrix) and all(
        sum(row[column] for row in matrix) > 0 for column in range(4)
    )


def _equivalent(left: tuple[tuple[int, ...], ...], right: tuple[tuple[int, ...], ...]) -> bool:
    if len(left) != len(right):
        return False
    for rows in itertools.permutations(range(len(left))):
        for columns in itertools.permutations(range(4)):
            if tuple(tuple(left[row][column] for column in columns) for row in rows) == right:
                return True
    return False


def _summary(labels: tuple[int, ...]) -> int:
    counts = [labels.count(target) for target in range(3)]
    maximum = max(counts)
    return sum(1 << target for target, count in enumerate(counts) if count == maximum)


def _profiles(matrix: tuple[tuple[int, ...], ...], signals: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        _summary(
            tuple(signals[source] for source in range(len(matrix)) if matrix[source][searcher])
        )
        for searcher in range(4)
    )


def _weight(target: int, signals: tuple[int, ...]) -> Fraction:
    result = Fraction(1, 3)
    for signal in signals:
        result *= Fraction(2, 3) if signal == target else Fraction(1, 6)
    return result


def _private(matrix: tuple[tuple[int, ...], ...]) -> Fraction:
    result = Fraction(0)
    for target in range(3):
        for signals in itertools.product(range(3), repeat=len(matrix)):
            miss = Fraction(1)
            for report in _profiles(matrix, signals):
                hit = Fraction(1, report.bit_count()) if report & (1 << target) else Fraction(0)
                miss *= 1 - hit
            result += _weight(target, signals) * (1 - miss)
    return result


def _agreement(left: int, right: int) -> Fraction:
    return Fraction((left & right).bit_count(), left.bit_count() * right.bit_count())


def _signature(matrix: tuple[tuple[int, ...], ...]) -> tuple[Fraction, ...]:
    moments = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for target in range(3):
        for signals in itertools.product(range(3), repeat=len(matrix)):
            weight = _weight(target, signals)
            reports = _profiles(matrix, signals)
            for left in range(4):
                for right in range(left + 1, 4):
                    moments[left][right] += weight * _agreement(reports[left], reports[right])
    candidates = []
    for order in itertools.permutations(range(4)):
        candidates.append(
            tuple(
                moments[min(order[left], order[right])][max(order[left], order[right])]
                for left in range(4)
                for right in range(left + 1, 4)
            )
        )
    return min(candidates)


def verify_registry(
    registry: list[dict[str, Any]], scalar_witness: dict[str, Any]
) -> dict[str, Any]:
    matrices = [
        tuple(tuple(int(value) for value in row) for row in entry["adjacency"])
        for entry in registry
    ]
    valid = all(_valid(matrix) for matrix in matrices)
    pairwise_nonisomorphic = all(
        not _equivalent(left, right)
        for index, left in enumerate(matrices)
        for right in matrices[index + 1 :]
    )
    counts = {sources: sum(len(matrix) == sources for matrix in matrices) for sources in (1, 2, 3)}
    count_check = counts == {1: 1, 2: 8, 3: 42}
    stored_check = all(
        _private(matrix) == Fraction(entry["private_discovery"])
        and _signature(matrix) == tuple(Fraction(value) for value in entry["pairwise_signature"])
        for matrix, entry in zip(matrices, registry, strict=True)
    )
    groups: dict[tuple[Fraction, ...], list[tuple[tuple[int, ...], ...]]] = defaultdict(list)
    for matrix in matrices:
        groups[_signature(matrix)].append(matrix)
    matched = [group for group in groups.values() if len(group) > 1]
    null_check = (
        len(matched) == 10
        and sum(len(group) for group in matched) == 20
        and all(len({_private(matrix) for matrix in group}) == 1 for group in matched)
    )
    witness_matrices = [
        tuple(tuple(int(value) for value in row) for row in adjacency)
        for adjacency in (scalar_witness["left_adjacency"], scalar_witness["right_adjacency"])
    ]
    witness_signatures = [_signature(matrix) for matrix in witness_matrices]
    witness_private = [_private(matrix) for matrix in witness_matrices]
    scalar_check = (
        sum(witness_signatures[0], Fraction(0)) / 6
        == sum(witness_signatures[1], Fraction(0)) / 6
        == Fraction(3, 4)
        and witness_private == [Fraction(8, 9), Fraction(31, 36)]
        and witness_private[0] - witness_private[1] == Fraction(1, 36)
    )
    passed = (
        valid
        and pairwise_nonisomorphic
        and count_check
        and stored_check
        and null_check
        and scalar_check
    )
    return {
        "passed": passed,
        "all_graphs_model_valid": valid,
        "all_registry_graphs_pairwise_nonisomorphic": pairwise_nonisomorphic,
        "independent_counts": counts,
        "counts_match": count_check,
        "stored_metrics_and_signatures_recomputed": stored_check,
        "matched_pairwise_group_count": len(matched),
        "graphs_in_matched_pairwise_groups": sum(len(group) for group in matched),
        "pairwise_matrix_bounded_null_recomputed": null_check,
        "mean_pair_agreement_counterexample_recomputed": scalar_check,
    }
