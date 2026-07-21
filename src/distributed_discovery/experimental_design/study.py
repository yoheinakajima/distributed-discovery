"""Run the registered DD-011 synthetic design and power study."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.experimental_design.model import design_registry
from distributed_discovery.experimental_design.power import (
    calibration_report,
    exact_model_checks,
    generate_assignments,
    simulate_power_table,
    synthetic_sample,
)
from distributed_discovery.experimental_design.verification import corruption_tests, verify_bundle
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-011-experimental-design/configs/power.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    randomization = generate_assignments(
        int(config["randomization_seed"]),
        int(config["participants_per_cell"]),
        int(config["session_size"]),
    )
    table = simulate_power_table(
        [int(seed) for seed in config["scenario_seeds"]],
        [int(size) for size in config["sample_sizes"]],
        int(config["replications"]),
        int(config["session_size"]),
    )
    return {
        "design": design_registry(),
        "randomization": randomization,
        "power_table": table,
        "calibration": calibration_report(table),
        "exact_model_checks": exact_model_checks(),
        "synthetic_sample": synthetic_sample(
            randomization, int(config["sample_seed"]), int(config["sample_rows"])
        ),
    }


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-011_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    bundle = build_bundle(config)
    verification = verify_bundle(bundle, root)
    corruptions = corruption_tests(bundle, root)
    if not verification["passed"] or not all(corruptions.values()):
        raise RuntimeError("DD-011 independent verification failed")
    artifacts = {
        "design-registry.json": bundle["design"],
        "treatment-matrix.json": bundle["design"]["treatment_cells"],
        "hypotheses.json": bundle["design"]["hypotheses"],
        "outcomes.json": bundle["design"]["outcomes"],
        "response-scenarios.json": bundle["design"]["response_scenarios"],
        "randomization-manifest.json": bundle["randomization"],
        "synthetic-sample.json": bundle["synthetic_sample"],
        "power-table.json": bundle["power_table"],
        "mde-table.json": [
            {
                key: row[key]
                for key in (
                    "scenario_id",
                    "hypothesis_id",
                    "sample_size",
                    "minimum_detectable_effect",
                )
            }
            for row in bundle["power_table"]
        ],
        "calibration-report.json": bundle["calibration"],
        "exact-model-checks.json": bundle["exact_model_checks"],
        "verification.json": verification,
        "corruption-tests.json": corruptions,
    }
    for name, value in artifacts.items():
        _write(outputs / name, value)
    summary = {
        "treatment_cells": len(bundle["design"]["treatment_cells"]),
        "hypotheses": len(bundle["design"]["hypotheses"]),
        "outcomes": len(bundle["design"]["outcomes"]),
        "response_scenarios": len(bundle["design"]["response_scenarios"]),
        "sample_sizes": len(config["sample_sizes"]),
        "power_rows": len(bundle["power_table"]),
        "monte_carlo_draws": len(bundle["power_table"]) * int(config["replications"]),
        "synthetic_assignments": len(bundle["randomization"]["assignments"]),
        "calibration_failures_retained": bundle["calibration"]["failure_count"],
        "no_human_data": True,
    }
    _write(outputs / "synthetic-summary.json", summary)
    _write(run / "validation.json", {"passed": True, **verification, **summary})
    (run / "stdout.txt").write_text(
        f"{run_id}\nsynthetic design and power verification passed\n", encoding="utf-8"
    )
    (run / "stderr.txt").write_text("", encoding="utf-8")
    input_paths = [
        config_path,
        root / "studies/DD-011-experimental-design/schemas/design-v1.schema.json",
        root / "src/distributed_discovery/experimental_design/model.py",
        root / "src/distributed_discovery/experimental_design/power.py",
        root / "src/distributed_discovery/experimental_design/verification.py",
        root / "src/distributed_discovery/experimental_design/study.py",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-011",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": "make dd011-experiment",
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": {
            "algorithm": [config["randomization_seed"]],
            "model": [*config["scenario_seeds"], config["sample_seed"]],
        },
        "outputs": {str(path.relative_to(run)): _sha(path) for path in outputs.glob("*.json")},
    }
    _write(run / "manifest.json", manifest)
    _write(
        run / "environment.json",
        {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "random_module": "stdlib.MersenneTwister",
        },
    )
    (run / "README.md").write_text(
        f"# DD-011 `{run_id}`\n\nSynthetic power evidence only; no participants or human data.\n",
        encoding="utf-8",
    )
    print(run_id)


if __name__ == "__main__":
    main()
