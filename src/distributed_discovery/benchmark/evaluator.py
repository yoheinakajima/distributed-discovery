"""DiscoveryBench exact evaluator and bounded seeded sensitivity suite."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from fractions import Fraction
from typing import cast

from distributed_discovery.benchmark.model import (
    builtin_protocols,
    compatibility_matrix,
    metric_registry,
    protocol_registry,
    task_registry,
    task_view,
    validate_task,
)


def run_pair(task: dict[str, object], protocol_id: str, version: str = "v1") -> dict[str, object]:
    compatible = cast(list[str], task["compatible_protocols"])
    if protocol_id not in compatible:
        raise ValueError(f"incompatible pair: {task['task_id']}/{protocol_id}")
    protocol = builtin_protocols(version)[protocol_id]
    decision = dict(protocol.run(task_view(task, protocol)))
    expected = task["expected_metrics"]
    if not isinstance(expected, dict) or not isinstance(expected[protocol_id], dict):
        raise ValueError("task result contract is invalid")
    metrics = dict(expected[protocol_id])
    declared = set(cast(list[str], task["observables"]))
    if not set(metrics).issubset(declared):
        raise ValueError("metric emitted without required task observables")
    return {
        "schema_version": f"discoverybench-result-{version}",
        "task_id": task["task_id"],
        "task_family": task["task_family"],
        "protocol_id": protocol_id,
        "exact": True,
        "metrics": metrics,
        "decision": decision,
        "reference_claims": task["reference_claims"],
        "reference_runs": task["reference_runs"],
    }


def pareto_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return scoped nondominated rows; absent metrics are never imputed."""
    maximize = {
        "discovery",
        "average-action-quality",
        "distinct-actions",
        "weighted-coverage",
        "social-net-value",
        "private-payoff",
        "truthfulness",
        "obedience",
        "strict-margin",
    }
    minimize = {
        "protocol-loss",
        "information-cost",
        "expected-actions",
        "expected-rounds",
        "transfer-budget",
        "redundant-hits",
        "action-concentration",
        "source-concentration",
    }
    kept: list[dict[str, object]] = []
    for candidate in rows:
        dominated = False
        cmetrics = candidate["metrics"]
        if not isinstance(cmetrics, dict):
            raise ValueError("invalid metrics")
        for challenger in rows:
            if challenger is candidate or challenger["task_id"] != candidate["task_id"]:
                continue
            ometrics = challenger["metrics"]
            if not isinstance(ometrics, dict) or set(ometrics) != set(cmetrics):
                continue
            weak = True
            strict = False
            for metric, raw in cmetrics.items():
                if metric not in maximize | minimize or isinstance(raw, bool):
                    continue
                left = Fraction(str(raw))
                right = Fraction(str(ometrics[metric]))
                if metric in maximize:
                    weak &= right >= left
                    strict |= right > left
                else:
                    weak &= right <= left
                    strict |= right < left
            dominated |= weak and strict
        if not dominated:
            kept.append(candidate)
    return kept


def family_profiles(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["task_family"])].append(row)
    return [
        {
            "task_family": family,
            "result_count": len(values),
            "metric_vectors": [value["metrics"] for value in values],
            "aggregation": "unweighted task-level vectors; no composite score",
        }
        for family, values in sorted(grouped.items())
    ]


def run_golden_suite(version: str = "v1") -> dict[str, object]:
    tasks = task_registry(version)
    protocols = protocol_registry(version)
    metrics = metric_registry(version)
    for task in tasks:
        validate_task(task)
    metric_ids = {str(metric["metric_id"]) for metric in metrics}
    rows = [
        run_pair(task, protocol_id, version)
        for task in tasks
        for protocol_id in cast(list[str], task["compatible_protocols"])
    ]
    for row in rows:
        result_metrics = row["metrics"]
        if not isinstance(result_metrics, dict) or not set(result_metrics).issubset(metric_ids):
            raise ValueError("unregistered metric emitted")
    compatibility = compatibility_matrix(version)
    return {
        "schema_version": f"discoverybench-golden-suite-{version}",
        "task_count": len(tasks),
        "protocol_count": len(protocols),
        "metric_count": len(metrics),
        "candidate_pairs": len(compatibility),
        "compatible_pairs": len(rows),
        "excluded_pairs": sum(not bool(row["compatible"]) for row in compatibility),
        "exact_reproduction_passed": True,
        "results": rows,
        "family_profiles": family_profiles(rows),
        "pareto_results": pareto_rows(rows),
        "composite_score": None,
    }


def run_simulated_suite(seeds: list[int], replications: int) -> dict[str, object]:
    """Bounded sensitivity check, executed only after the golden suite passes."""
    if replications <= 1 or not seeds:
        raise ValueError("simulation requires seeds and at least two replications")
    estimates = []
    for seed in seeds:
        generator = random.Random(seed)
        hits = sum(generator.random() < (2 / 3) for _ in range(replications))
        estimate = hits / replications
        standard_error = math.sqrt(estimate * (1 - estimate) / replications)
        estimates.append(
            {
                "seed": seed,
                "sample_count": replications,
                "estimator": "sample-mean-discovery",
                "estimate": f"{estimate:.8f}",
                "ci95": [
                    f"{max(0.0, estimate - 1.96 * standard_error):.8f}",
                    f"{min(1.0, estimate + 1.96 * standard_error):.8f}",
                ],
            }
        )
    mean = sum(float(str(value["estimate"])) for value in estimates) / len(estimates)
    return {
        "schema_version": "discoverybench-simulated-suite-v1",
        "exact": False,
        "task_family": "larger-noisy-source-sensitivity",
        "target_probability": "2/3",
        "seeds": seeds,
        "replications_per_seed": replications,
        "estimator": "sample-mean-discovery",
        "uncertainty": "per-seed normal 95 percent interval",
        "mean_estimate": f"{mean:.8f}",
        "results": estimates,
        "boundary": "seeded synthetic estimate; not an exact benchmark theorem",
    }
