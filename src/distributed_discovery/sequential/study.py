"""Execute the immutable DD-004 perfect-elimination baseline."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import time
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.sequential.model import (
    dynamic_optimum,
    evaluate_schedule,
    ordered_compositions,
)
from distributed_discovery.sequential.verification import enumerate_sequences
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-004-sequential-discovery/configs/perfect-elimination.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _prior(values: list[str]) -> tuple[Fraction, ...]:
    return tuple(Fraction(value) for value in values)


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    commit = _git(root, "rev-parse", "HEAD")
    started = datetime.now(UTC)
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-004_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    outputs = run_dir / "outputs"
    run_dir.mkdir(parents=True, exist_ok=False)
    outputs.mkdir()
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    deadline = time.monotonic() + float(config["time_budget_seconds"])
    rows: list[dict[str, str]] = []
    checks: list[dict[str, Any]] = []
    for case in config["primary_cases"]:
        prior = _prior(case["prior"])
        budget = int(case["budget"])
        for schedule in ordered_compositions(budget):
            if time.monotonic() > deadline:
                raise RuntimeError("DD-004 time budget exhausted")
            direct = evaluate_schedule(prior, budget, schedule)
            dp = dynamic_optimum(prior, budget, schedule)
            if direct != dp:
                raise RuntimeError("top-prior schedule disagrees with exact DP")
            rows.append(
                {
                    "case": case["name"],
                    "schedule": "+".join(map(str, schedule)),
                    **{key: str(value) for key, value in direct.items()},
                }
            )
    for case in config["tiny_cases"]:
        prior = _prior(case["prior"])
        budget = int(case["budget"])
        for schedule in ordered_compositions(budget):
            dp = dynamic_optimum(prior, budget, schedule)
            tree = enumerate_sequences(prior, budget, schedule)
            checks.append(
                {
                    "case": case["name"],
                    "schedule": list(schedule),
                    "dp": {key: str(value) for key, value in dp.items()},
                    "policy_tree": {key: str(value) for key, value in tree.items()},
                    "passed": dp == tree,
                }
            )
    terminal_values = {row["terminal_discovery"] for row in rows}
    validation = {
        "passed": all(item["passed"] for item in checks) and len(terminal_values) == 2,
        "independent_tiny_policy_trees_agree": all(item["passed"] for item in checks),
        "terminal_value_schedule_invariant_per_case": len(terminal_values) == 2,
        "time_budget_seconds": config["time_budget_seconds"],
        "elapsed_seconds": time.monotonic() - (deadline - float(config["time_budget_seconds"])),
    }
    _write(outputs / "schedule-frontier.json", rows)
    _write(outputs / "tiny-policy-tree-certificate.json", checks)
    _write(run_dir / "validation.json", validation)
    _write(
        run_dir / "metrics.json",
        {
            "primary_schedule_count": len(rows),
            "tiny_policy_tree_checks": len(checks),
            "model": config["model"],
        },
    )
    (run_dir / "stdout.log").write_text(f"run_id={run_id}\nrows={len(rows)}\n", encoding="utf-8")
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    _write(
        run_dir / "environment.json",
        {"platform": platform.platform(), "python": platform.python_version()},
    )
    output_hashes = {
        str(path.relative_to(run_dir)): _sha(path) for path in outputs.rglob("*") if path.is_file()
    }
    _write(run_dir / "output-checksums.json", output_hashes)
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-004",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": bool(_git(root, "status", "--porcelain")),
        "upstream_commit": None,
        "command": "make dd004-sequential",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {
            str(path.relative_to(root)): _sha(path)
            for path in [
                config_path,
                root / "src/distributed_discovery/sequential/model.py",
                root / "src/distributed_discovery/sequential/verification.py",
                root / "src/distributed_discovery/sequential/study.py",
            ]
        },
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": output_hashes,
    }
    _write(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text("make dd004-sequential\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd004-sequential\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-004 run `{run_id}`\n\nExact perfect-elimination baseline; no noisy-test claim.\n",
        encoding="utf-8",
    )
    print(run_id)
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
