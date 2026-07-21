"""Execute the immutable DD-005 weighted-coverage frontier census."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.coverage.model import exact_frontier, greedy, top_individual
from distributed_discovery.coverage.verification import verify_exact
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-005-overlapping-coverage/configs/frontiers.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    commit = _git(root, "rev-parse", "HEAD")
    started = datetime.now(UTC)
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-005_{commit[:8]}_{config_hash[:10]}"
    run_dir, output_dir = (
        root / "results/verified" / run_id,
        root / "results/verified" / run_id / "outputs",
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir()
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    rows: list[dict[str, Any]] = []
    for fixture in config["fixtures"]:
        weights = tuple(Fraction(value) for value in fixture["weights"])
        actions = tuple(frozenset(action) for action in fixture["actions"])
        budget = int(fixture["budget"])
        exact_choice, exact_value = exact_frontier(weights, actions, budget)
        checked_choice, checked_value = verify_exact(weights, actions, budget)
        top_choice, top_value = top_individual(weights, actions, budget)
        greedy_choice, greedy_value = greedy(weights, actions, budget)
        if (exact_choice, exact_value) != (checked_choice, checked_value):
            raise RuntimeError("independent exact verifier disagreement")
        rows.append(
            {
                "fixture": fixture["name"],
                "budget": budget,
                "exact_portfolio": list(exact_choice),
                "exact_value": str(exact_value),
                "top_individual_portfolio": list(top_choice),
                "top_individual_value": str(top_value),
                "greedy_portfolio": list(greedy_choice),
                "greedy_value": str(greedy_value),
                "independent_verifier_passed": True,
            }
        )
    witnesses = {
        row["fixture"]: row
        for row in rows
        if row["exact_value"] != row["top_individual_value"]
        or row["exact_value"] != row["greedy_value"]
    }
    validation = {
        "passed": len(rows) == 3
        and all(row["independent_verifier_passed"] for row in rows)
        and "duplicated-ranking-witness" in witnesses
        and "greedy-recovery-witness" in witnesses,
        "independent_exact_verifier": True,
        "top_individual_failure_witness": "duplicated-ranking-witness",
        "greedy_failure_witness": "greedy-recovery-witness",
    }
    _write(output_dir / "coverage-frontiers.json", rows)
    _write(output_dir / "coverage-witnesses.json", witnesses)
    _write(run_dir / "validation.json", validation)
    _write(run_dir / "metrics.json", {"fixture_count": len(rows), "witness_count": len(witnesses)})
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\nfixtures={len(rows)}\n", encoding="utf-8"
    )
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    _write(
        run_dir / "environment.json",
        {"platform": platform.platform(), "python": platform.python_version()},
    )
    outputs = {
        str(path.relative_to(run_dir)): _sha(path)
        for path in output_dir.rglob("*")
        if path.is_file()
    }
    _write(run_dir / "output-checksums.json", outputs)
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-005",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": bool(_git(root, "status", "--porcelain")),
        "upstream_commit": None,
        "command": "make dd005-coverage",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {
            str(path.relative_to(root)): _sha(path)
            for path in [
                config_path,
                root / "src/distributed_discovery/coverage/model.py",
                root / "src/distributed_discovery/coverage/verification.py",
                root / "src/distributed_discovery/coverage/study.py",
            ]
        },
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": outputs,
    }
    _write(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text("make dd005-coverage\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd005-coverage\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-005 run `{run_id}`\n\nExact deterministic weighted-union coverage census.\n",
        encoding="utf-8",
    )
    print(run_id)
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
