"""Run the registered DD-010 DiscoveryBench suite with immutable provenance."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import yaml

from distributed_discovery.benchmark.evaluator import run_golden_suite, run_simulated_suite
from distributed_discovery.benchmark.model import (
    compatibility_matrix,
    metric_registry,
    protocol_registry,
    task_registry,
)
from distributed_discovery.benchmark.verification import corruption_tests, verify_certificate
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-010-discoverybench/configs/benchmark.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_registered(
    config_relative: Path = CONFIG,
    version: str = "v1",
    command: str = "make dd010-discoverybench",
) -> str:
    root = repository_root()
    config_path = root / config_relative
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    if dirty:
        raise RuntimeError("registered benchmark runs require a clean committed tree")
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-010_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    golden = run_golden_suite(version)
    verification = verify_certificate(golden, root, version)
    corruption = corruption_tests(golden, root, version)
    if not verification["passed"] or not all(corruption.values()):
        raise RuntimeError("golden suite verification failed")
    simulation_config = config["simulated_suite"]
    simulated = run_simulated_suite(
        simulation_config["seeds"], simulation_config["replications_per_seed"]
    )
    summary = {
        "task_count": golden["task_count"],
        "benchmark_version": version,
        "protocol_count": golden["protocol_count"],
        "metric_count": golden["metric_count"],
        "candidate_pairs": golden["candidate_pairs"],
        "compatible_pairs": golden["compatible_pairs"],
        "excluded_pairs": golden["excluded_pairs"],
        "golden_rows_verified": verification["verified_rows"],
        "information_leakage_tests_passed": corruption["leaked_information_rejected"],
        "simulated_seeds": len(simulation_config["seeds"]),
        "simulated_replications": len(simulation_config["seeds"])
        * simulation_config["replications_per_seed"],
    }
    artifacts = {
        "task-registry.json": task_registry(version),
        "protocol-registry.json": protocol_registry(version),
        "metric-registry.json": metric_registry(version),
        "compatibility-matrix.json": compatibility_matrix(version),
        "exact-result-matrix.json": golden["results"],
        "family-profiles.json": golden["family_profiles"],
        "pareto-report.json": golden["pareto_results"],
        "golden-certificate.json": golden,
        "simulated-results.json": simulated,
        "verification.json": verification,
        "corruption-tests.json": corruption,
        "benchmark-summary.json": summary,
        "failures-and-exclusions.json": {
            "failures": [],
            "exclusions": [row for row in compatibility_matrix(version) if not row["compatible"]],
        },
    }
    for name, value in artifacts.items():
        _write(outputs / name, value)
    _write(run / "validation.json", {"passed": True, **summary})
    (run / "stdout.txt").write_text(
        f"{run_id}\ngolden and simulated suites passed\n", encoding="utf-8"
    )
    (run / "stderr.txt").write_text("", encoding="utf-8")
    input_paths = [
        config_path,
        root / f"studies/DD-010-discoverybench/schemas/task-{version}.schema.json",
        root / "src/distributed_discovery/benchmark/model.py",
        root / "src/distributed_discovery/benchmark/evaluator.py",
        root / "src/distributed_discovery/benchmark/verification.py",
        root / "src/distributed_discovery/benchmark/study.py",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-010",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": command,
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": {"algorithm": [], "model": simulation_config["seeds"]},
        "outputs": {str(path.relative_to(run)): _sha(path) for path in outputs.glob("*.json")},
    }
    _write(run / "manifest.json", manifest)
    _write(
        run / "environment.json",
        {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "random_module": "stdlib",
        },
    )
    (run / "README.md").write_text(
        f"# DD-010 `{run_id}`\n\n"
        "Exact golden benchmark plus bounded seeded synthetic sensitivity.\n",
        encoding="utf-8",
    )
    print(run_id)
    return run_id


def main() -> None:
    run_registered()


if __name__ == "__main__":
    main()
