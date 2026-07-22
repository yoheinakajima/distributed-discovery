"""Run the registered exact DD-015 dynamic-attention study."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any, cast

import yaml

from distributed_discovery.dynamic_attention.model import solve_protocol
from distributed_discovery.dynamic_attention.verification import (
    corruption_tests,
    enumerate_policy,
    enumerate_simple_policy,
    verify_bundle,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-015-dynamic-attention/configs/baseline.yml")


def _serialize(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_serialize(value), indent=2, sort_keys=True) + "\n")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_config(config: dict[str, Any]) -> None:
    if int(config["candidates"]) != 3 or list(config["agents"]) != [2, 3]:
        raise ValueError("DD-015 dimensions changed from the registered boundary")
    cells = (
        len(config["agents"]) * len(config["private_accuracies"]) * len(config["shared_accuracies"])
    )
    if cells != int(config["grid_cells"]):
        raise ValueError("registered grid-cell count is inconsistent")
    paths = sum(
        3 ** (int(agents) + 2)
        for agents in config["agents"]
        for _ in config["private_accuracies"]
        for _ in config["shared_accuracies"]
    )
    if paths != int(config["labeled_target_signal_paths"]):
        raise ValueError("registered labeled-path count is inconsistent")
    if int(config["runtime_estimate_seconds"]) >= int(config["time_cap_seconds"]):
        raise ValueError("runtime estimate must be below the cap")


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    validate_config(config)
    rows: list[dict[str, Any]] = []
    for agents in config["agents"]:
        for private_accuracy in config["private_accuracies"]:
            for shared_accuracy in config["shared_accuracies"]:
                p = Fraction(private_accuracy)
                q = Fraction(shared_accuracy)
                for objective in config["objectives"]:
                    autonomous = solve_protocol(agents, p, q, objective, "autonomous")
                    planner = solve_protocol(agents, p, q, objective, "planner")
                    autonomous_policy = cast(dict[str, tuple[int, int, int]], autonomous["policy"])
                    planner_policy = cast(dict[str, tuple[int, int, int]], planner["policy"])
                    autonomous_metrics = enumerate_policy(
                        agents, p, q, objective, autonomous_policy
                    )
                    planner_metrics = enumerate_policy(agents, p, q, objective, planner_policy)
                    autonomous.update(
                        {
                            key: value
                            for key, value in autonomous_metrics.items()
                            if key not in ("probability_mass", "discovery", "expected_actions")
                        }
                    )
                    planner.update(
                        {
                            key: value
                            for key, value in planner_metrics.items()
                            if key not in ("probability_mass", "discovery", "expected_actions")
                        }
                    )
                    rows.append(
                        {
                            "cell_id": f"N{agents}-p{p}-q{q}-{objective}",
                            "agents": agents,
                            "private_accuracy": p,
                            "shared_accuracy": q,
                            "objective": objective,
                            "autonomous": autonomous,
                            "planner": planner,
                            "private_only": enumerate_simple_policy(
                                agents, p, q, objective, "private-only"
                            ),
                            "public_only": enumerate_simple_policy(
                                agents, p, q, objective, "public-only"
                            ),
                            "history_hidden_bayes": enumerate_simple_policy(
                                agents, p, q, objective, "history-hidden-bayes"
                            ),
                        }
                    )
    bundle = {"schema_version": config["schema_version"], "rows": rows}
    bundle["verification"] = verify_bundle(bundle)
    bundle["corruption_tests"] = corruption_tests(bundle)
    if not bundle["verification"]["passed"] or not all(bundle["corruption_tests"].values()):
        raise RuntimeError("DD-015 verification failed")
    fixed = [row for row in rows if row["objective"] == "fixed-budget"]
    stopping = [row for row in rows if row["objective"] == "stopping-on-success"]
    bundle["summary"] = {
        "grid_cells": int(config["grid_cells"]),
        "objective_rows": len(rows),
        "labeled_target_signal_paths": int(config["labeled_target_signal_paths"]),
        "planner_strictly_better_rows": sum(
            row["planner"]["discovery"] > row["autonomous"]["discovery"] for row in rows
        ),
        "visibility_increases_discovery_fixed_rows": sum(
            row["autonomous"]["discovery"] > row["history_hidden_bayes"]["discovery"]
            for row in fixed
        ),
        "visibility_reduces_discovery_fixed_rows": sum(
            row["autonomous"]["discovery"] < row["history_hidden_bayes"]["discovery"]
            for row in fixed
        ),
        "visibility_increases_dispersion_fixed_rows": sum(
            row["autonomous"]["expected_distinct_actions"]
            > row["history_hidden_bayes"]["expected_distinct_actions"]
            for row in fixed
        ),
        "visibility_increases_herding_fixed_rows": sum(
            row["autonomous"]["expected_distinct_actions"]
            < row["history_hidden_bayes"]["expected_distinct_actions"]
            for row in fixed
        ),
        "stopping_reduces_expected_actions_rows": sum(
            stop["autonomous"]["expected_actions"]
            < next(
                row["autonomous"]["expected_actions"]
                for row in fixed
                if row["agents"] == stop["agents"]
                and row["private_accuracy"] == stop["private_accuracy"]
                and row["shared_accuracy"] == stop["shared_accuracy"]
            )
            for stop in stopping
        ),
        "autonomous_follow_previous_positive_rows": sum(
            row["autonomous"]["previous_action_follow_rate"] > 0 for row in rows
        ),
        "autonomous_lean_against_positive_rows": sum(
            row["autonomous"]["lean_against_repeat_rate"] > 0 for row in rows
        ),
        "verification_checks": bundle["verification"]["check_count"],
        "corruption_gates": len(bundle["corruption_tests"]),
    }
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text())
    commit = ""
    digest = ""
    started = datetime.now(UTC)
    if not args.preview:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        dirty = bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
        )
        if dirty:
            raise RuntimeError("DD-015 primary run requires a clean committed implementation")
        digest = hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    started_clock = perf_counter()
    bundle = build_bundle(config)
    elapsed = perf_counter() - started_clock
    if args.preview:
        print(json.dumps(_serialize(bundle["summary"]), indent=2, sort_keys=True))
        return
    if elapsed > int(config["time_cap_seconds"]):
        raise RuntimeError("DD-015 exceeded its registered time cap")
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-015_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    if run.exists():
        raise RuntimeError(f"refusing to overwrite {run_id}")
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text())
    _write(outputs / "summary.json", bundle["summary"])
    _write(outputs / "dynamic-profile.json", bundle["rows"])
    _write(outputs / "verification.json", bundle["verification"])
    _write(outputs / "corruption-tests.json", bundle["corruption_tests"])
    validation = {
        "passed": True,
        "elapsed_seconds": round(elapsed, 6),
        "time_cap_seconds": int(config["time_cap_seconds"]),
        "independent_verification": True,
        "all_corruptions_rejected": True,
    }
    _write(run / "validation.json", validation)
    input_paths = [
        config_path,
        root / "src/distributed_discovery/dynamic_attention/model.py",
        root / "src/distributed_discovery/dynamic_attention/verification.py",
        root / "src/distributed_discovery/dynamic_attention/study.py",
        root / "studies/DD-015-dynamic-attention/model.md",
    ]
    output_hashes = {str(path.relative_to(run)): _sha(path) for path in sorted(outputs.glob("*"))}
    _write(
        run / "manifest.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "study_id": "DD-015",
            "started_utc": started.isoformat().replace("+00:00", "Z"),
            "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "exit_status": 0,
            "validation_status": "passed",
            "git_commit": commit,
            "git_dirty": False,
            "upstream_commit": None,
            "command": "make dd015-dynamic",
            "config_hash_sha256": digest,
            "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
            "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
            "random_seeds": config["random_seeds"],
            "outputs": output_hashes,
        },
    )
    _write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "stdout.txt").write_text(f"{run_id}\nDD-015 exact verification passed\n")
    (run / "stderr.txt").write_text("")
    (run / "README.md").write_text(f"# DD-015 `{run_id}`\n\nExact bounded dynamic-attention run.\n")
    print(run_id)


if __name__ == "__main__":
    main()
