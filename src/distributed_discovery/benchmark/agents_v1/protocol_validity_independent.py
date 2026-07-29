"""Independent reconstruction for protocol-validity policy v2 bounds.

This module intentionally does not import the primary bound constructor. It
consumes only serialized interval records and rederives contrast endpoints
with a separate grouping and reduction path.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from fractions import Fraction


def _fraction(value: object) -> Fraction:
    return Fraction(str(value))


def reconstruct_contrast_bounds(
    records: Sequence[Mapping[str, object]],
    contrasts: Sequence[tuple[str, str]],
) -> tuple[dict[str, object], ...]:
    """Reconstruct all-eligible-pairing contrast bounds independently."""

    cells: dict[tuple[str, str, str, str], tuple[Fraction, Fraction]] = {}
    task_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    for record in records:
        model = str(record["model"])
        task = str(record["task_commitment"])
        architecture = str(record["architecture_id"])
        metric = str(record["metric_id"])
        key = (model, task, architecture, metric)
        if key in cells:
            raise ValueError("independent reconstruction found a duplicate interval")
        lower = _fraction(record["lower"])
        upper = _fraction(record["upper"])
        if lower > upper:
            raise ValueError("independent reconstruction found an inverted interval")
        cells[key] = (lower, upper)
        task_sets[(model, metric)].add(task)

    reconstructed: list[dict[str, object]] = []
    for (model, metric), task_set in sorted(task_sets.items()):
        for left, right in contrasts:
            pair_endpoints: list[tuple[Fraction, Fraction]] = []
            for task in sorted(task_set):
                left_interval = cells.get((model, task, left, metric))
                right_interval = cells.get((model, task, right, metric))
                if left_interval is None and right_interval is None:
                    continue
                if left_interval is None or right_interval is None:
                    raise ValueError("independent reconstruction found an incomplete intended pair")
                pair_endpoints.append(
                    (
                        left_interval[0] - right_interval[1],
                        left_interval[1] - right_interval[0],
                    )
                )
            if not pair_endpoints:
                continue
            denominator = len(pair_endpoints)
            reconstructed.append(
                {
                    "model": model,
                    "metric_id": metric,
                    "left_architecture": left,
                    "right_architecture": right,
                    "intended_eligible_pairs": denominator,
                    "lower": str(
                        sum((item[0] for item in pair_endpoints), Fraction(0)) / denominator
                    ),
                    "upper": str(
                        sum((item[1] for item in pair_endpoints), Fraction(0)) / denominator
                    ),
                }
            )
    return tuple(reconstructed)


def require_bound_agreement(
    primary: Sequence[Mapping[str, object]],
    independent: Sequence[Mapping[str, object]],
) -> None:
    """Reject any endpoint, denominator, or identity disagreement."""

    def normalize(
        values: Sequence[Mapping[str, object]],
    ) -> dict[tuple[str, str, str, str], tuple[int, Fraction, Fraction]]:
        output: dict[tuple[str, str, str, str], tuple[int, Fraction, Fraction]] = {}
        for value in values:
            key = (
                str(value["model"]),
                str(value["metric_id"]),
                str(value["left_architecture"]),
                str(value["right_architecture"]),
            )
            if key in output:
                raise ValueError("duplicate reconstructed contrast")
            output[key] = (
                int(str(value["intended_eligible_pairs"])),
                _fraction(value["lower"]),
                _fraction(value["upper"]),
            )
        return output

    if normalize(primary) != normalize(independent):
        raise ValueError("independent metric-bound reconstruction disagrees")
