"""Execute the bounded DD-008B audit of the general-N analytic results."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.acquisition.common_source_analysis import (
    all_common_trap_interval,
    equilibrium_counts,
    fixed_k_large_n_limit,
    monotonicity_kernel,
    overacquisition_counterexample,
    planner_counts,
    planner_threshold,
    private_threshold,
)
from distributed_discovery.acquisition.common_source_verification import (
    direct_planner_threshold,
    direct_private_threshold,
    verify_frozen_census,
    verify_threshold_rows,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-008B-common-source-analysis/configs/audit.yml")
FROZEN_CENSUS = Path(
    "results/verified/20260721T163030Z_DD-008A_8b70668b_06307caab4/outputs/n-agent-census.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _corruption_checks(
    rows: list[dict[str, object]],
    census: Path,
    equilibria: dict[tuple[int, Fraction, Fraction], list[int]],
    planners: dict[tuple[int, Fraction, Fraction], list[int]],
) -> dict[str, bool]:
    altered_rows = [dict(row) for row in rows]
    altered_rows[0]["private_threshold"] = str(
        Fraction(str(altered_rows[0]["private_threshold"])) + Fraction(1, 10_000)
    )
    threshold_rejected = False
    try:
        verify_threshold_rows(altered_rows)
    except ValueError:
        threshold_rejected = True

    altered_equilibria = {key: list(value) for key, value in equilibria.items()}
    first_key = next(iter(altered_equilibria))
    altered_equilibria[first_key] = [999]
    census_rejected = False
    try:
        verify_frozen_census(census, altered_equilibria, planners)
    except ValueError:
        census_rejected = True
    return {
        "altered_threshold_rejected": threshold_rejected,
        "altered_frozen_census_classification_rejected": census_rejected,
    }


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    cfg: dict[str, Any] = yaml.safe_load(config_path.read_text())
    normalized = json.dumps(cfg, sort_keys=True)
    config_hash = hashlib.sha256(normalized.encode()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-008B_{commit[:8]}_{config_hash[:10]}"
    run = root / "results/verified" / run_id
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text())

    accuracies = [Fraction(value) for value in cfg["accuracies"]]
    costs = [Fraction(value) for value in cfg["costs"]]
    threshold_rows: list[dict[str, object]] = []
    direct_checks = 0
    for n in cfg["agents"]:
        for p in accuracies:
            thresholds = [private_threshold(n, k, p) for k in range(n)]
            if not all(
                left > right for left, right in zip(thresholds, thresholds[1:], strict=False)
            ):
                raise RuntimeError(f"private thresholds are not strictly decreasing for {(n, p)}")
            for k in range(n):
                row: dict[str, object] = {
                    "agents": n,
                    "k": k,
                    "accuracy": str(p),
                    "private_threshold": str(thresholds[k]),
                    "planner_threshold": str(planner_threshold(n, k, p)),
                }
                if n in cfg["direct_agents"]:
                    if thresholds[k] != direct_private_threshold(n, k, p):
                        raise RuntimeError(f"direct private-threshold mismatch for {(n, k, p)}")
                    if planner_threshold(n, k, p) != direct_planner_threshold(n, k, p):
                        raise RuntimeError(f"direct planner-threshold mismatch for {(n, k, p)}")
                    row["direct_enumeration"] = "agrees"
                    direct_checks += 2
                threshold_rows.append(row)

    equilibria: dict[tuple[int, Fraction, Fraction], list[int]] = {}
    planners: dict[tuple[int, Fraction, Fraction], list[int]] = {}
    classification_rows: list[dict[str, object]] = []
    for n in cfg["agents"]:
        for p in accuracies:
            for cost in costs:
                key = (n, p, cost)
                equilibria[key] = equilibrium_counts(n, p, cost)
                planners[key] = planner_counts(n, p, cost)
                classification_rows.append(
                    {
                        "agents": n,
                        "accuracy": str(p),
                        "cost": str(cost),
                        "equilibrium_k": equilibria[key],
                        "planner_k": planners[key],
                        "gap": max(planners[key]) - min(equilibria[key]),
                    }
                )
    census_path = root / FROZEN_CENSUS
    frozen_rows = verify_frozen_census(census_path, equilibria, planners)

    kernel_checks = 0
    for n in range(2, int(cfg["symbolic_audit_agents"]) + 1):
        for p in accuracies:
            for k in range(n - 1):
                m = n - k
                for x in range(k + 1):
                    direct_value, numerator, denominator = monotonicity_kernel(x, m, p)
                    if numerator <= 0 or direct_value != numerator / denominator:
                        raise RuntimeError(f"monotonicity identity failed for {(n, k, x, p)}")
                    kernel_checks += 1

    boundaries = []
    for n in cfg["boundary_agents"]:
        for p in accuracies:
            lower, upper = all_common_trap_interval(n, p)
            boundaries.append(
                {
                    "agents": n,
                    "accuracy": str(p),
                    "lower_inclusive": str(lower),
                    "upper_exclusive": str(upper),
                    "width": str(upper - lower),
                }
            )

    large_n_limits = [
        {
            "k": k,
            "accuracy": str(p),
            "private_threshold_limit": str(fixed_k_large_n_limit(k, p)),
        }
        for k in cfg["fixed_k_limits"]
        for p in accuracies
    ]
    counterexample = overacquisition_counterexample()
    corruption = _corruption_checks(threshold_rows, census_path, equilibria, planners)
    passed = all(corruption.values())

    _write(outputs / "thresholds.json", threshold_rows)
    _write(outputs / "classifications.json", classification_rows)
    _write(outputs / "all-common-boundaries.json", boundaries)
    _write(outputs / "large-n-limits.json", large_n_limits)
    _write(outputs / "counterexamples.json", [counterexample])
    _write(outputs / "corruption-tests.json", corruption)
    summary = {
        "threshold_rows": len(threshold_rows),
        "classification_rows": len(classification_rows),
        "frozen_dd008a_rows_reproduced": frozen_rows,
        "direct_payoff_checks": direct_checks,
        "monotonicity_kernel_checks": kernel_checks,
        "general_n_result": "strict-private-threshold-monotonicity-and-count-characterization",
        "all_common_trap_width": "p*(1-p)/N",
        "universal_underacquisition": "refuted-by-exact-interior-counterexample",
        "passed": passed,
    }
    _write(outputs / "summary.json", summary)
    _write(outputs / "verification.json", {"passed": passed, **summary})
    _write(run / "validation.json", {"passed": passed, **summary})

    output_hashes = {
        str(path.relative_to(run)): _sha256(path) for path in sorted(outputs.glob("*.json"))
    }
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-008B",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if passed else 1,
        "validation_status": "passed" if passed else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": "make dd008b-analysis",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha256(root / "uv.lock"),
        "input_hashes": {
            str(path.relative_to(root)): _sha256(path)
            for path in [
                config_path,
                census_path,
                root / "src/distributed_discovery/acquisition/common_source_analysis.py",
                root / "src/distributed_discovery/acquisition/common_source_verification.py",
                root / "src/distributed_discovery/acquisition/common_source_study.py",
            ]
        },
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": output_hashes,
    }
    _write(run / "manifest.json", manifest)
    (run / "README.md").write_text(
        f"# DD-008B `{run_id}`\n\nExact analytic-threshold audit; no random draws.\n"
    )
    print(run_id)


if __name__ == "__main__":
    main()
