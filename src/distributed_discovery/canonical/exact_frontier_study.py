"""Run the immutable exact canonical pooled-frontier certificate."""

from __future__ import annotations

import copy
import csv
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

from distributed_discovery.canonical.exact_frontier import (
    expected_labeled_count_vectors,
    histogram_orbit_frontier,
    labeled_count_frontier,
)
from distributed_discovery.canonical.exact_frontier_verification import verify_certificate
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-000-foundations/configs/exact-frontier.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config_hash = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    commit = _git(root, "rev-parse", "HEAD")
    dirty = bool(_git(root, "status", "--porcelain"))
    started = datetime.now(UTC)
    start = time.monotonic()
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-000_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"))

    parameters = config["parameters"]
    candidates = int(parameters["candidates"])
    reports = int(parameters["reports"])
    accuracy = Fraction(str(parameters["accuracy"]))
    budgets = [int(value) for value in parameters["budgets"]]
    if budgets != list(range(1, reports + 1)):
        raise ValueError("budgets must enumerate 1 through reports")

    method_a_start = time.monotonic()
    method_a = labeled_count_frontier(candidates, reports, accuracy)
    method_a_seconds = time.monotonic() - method_a_start
    method_b_start = time.monotonic()
    method_b = histogram_orbit_frontier(candidates, reports, accuracy)
    method_b_seconds = time.monotonic() - method_b_start
    private_lower = Fraction(str(config["private_team_lower_fraction"]))
    recovery_budget = next(
        budget
        for budget, value in zip(budgets, method_a.values, strict=True)
        if value >= private_lower
    )
    upper = method_a.values[-1]
    rows = [
        {
            "budget": budget,
            "numerator": value.numerator,
            "denominator": value.denominator,
            "exact_fraction": str(value),
            "decimal_16": f"{float(value):.16f}",
            "method_a_fraction": str(value),
            "method_b_fraction": str(method_b.values[budget - 1]),
        }
        for budget, value in zip(budgets, method_a.values, strict=True)
    ]
    with (outputs / "exact-frontier.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    certificate: dict[str, Any] = {
        "schema_version": 1,
        "parameters": {
            "candidates": candidates,
            "reports": reports,
            "accuracy": str(accuracy),
            "false_label_accuracy": str((1 - accuracy) / (candidates - 1)),
            "fixed_target_label": 0,
            "cutoff_rule": "uniform inclusion among labels tied at the top-L cutoff",
        },
        "formula": {
            "method_a": (
                "sum over labeled count vectors: multinomial probability times cutoff "
                "inclusion share"
            ),
            "method_b": (
                "sum over target count k and false-count histogram h_j with exact orbit "
                "multiplicity"
            ),
            "posterior_order_basis": (
                "accuracy exceeds false-label probability, so posterior order equals "
                "report-count order"
            ),
        },
        "method_a": {
            "representation": "labeled weak compositions",
            "labeled_count_vector_count": method_a.state_count,
            "expected_labeled_count_vector_count": expected_labeled_count_vectors(
                candidates, reports
            ),
            "probability_mass_fraction": str(method_a.probability_mass),
        },
        "method_b": {
            "representation": "target count plus false-label occupancy histogram",
            "histogram_orbit_count": method_b.state_count,
            "probability_mass_fraction": str(method_b.probability_mass),
        },
        "frontier": rows,
        "agreement": {
            "all_budgets_exact": method_a.values == method_b.values,
            "probability_mass_one_both_methods": (
                method_a.probability_mass == method_b.probability_mass == 1
            ),
        },
        "recovery_budget": recovery_budget,
        "private_team_interval": {
            "lower_fraction": str(private_lower),
            "upper_fraction": str(upper),
            "gap_fraction": str(upper - private_lower),
            "gap_decimal_16": f"{float(upper - private_lower):.16f}",
            "basis": config["claim_boundaries"]["upper_bound_basis"],
            "upper_attainability_claimed": False,
            "global_tightness_claimed": False,
            "canonical_private_team_optimum_status": "unresolved",
        },
    }
    _json(outputs / "canonical-exact-frontier-certificate.json", certificate)

    verification_errors = verify_certificate(certificate)
    corrupted = copy.deepcopy(certificate)
    corrupted["frontier"][-1]["numerator"] += 1
    corruption_errors = verify_certificate(corrupted)
    corruption_rejected = bool(corruption_errors)
    _json(
        outputs / "independent-verification.json",
        {
            "schema_version": 1,
            "method": "independent decreasing-integer-partition enumeration",
            "certificate_errors": verification_errors,
            "corruption_test": {
                "mutation": "increment final frontier numerator by one",
                "rejected": corruption_rejected,
                "errors": corruption_errors,
            },
        },
    )

    elapsed = time.monotonic() - start
    _json(
        outputs / "cost-audit.json",
        {
            "schema_version": 1,
            "declared_time_budget_seconds": config["time_budget_seconds"],
            "method_a_expected_states": expected_labeled_count_vectors(candidates, reports),
            "method_a_elapsed_seconds": method_a_seconds,
            "method_b_elapsed_seconds": method_b_seconds,
            "total_elapsed_seconds": elapsed,
            "bounded_before_execution": True,
            "randomness": None,
        },
    )

    expected = config["expected"]
    validation = {
        "passed": bool(
            not dirty
            and method_a.state_count == int(expected["labeled_count_vectors"])
            and method_b.state_count == int(expected["histogram_orbits"])
            and method_a.probability_mass == method_b.probability_mass == 1
            and method_a.values == method_b.values
            and upper == Fraction(str(expected["budget_8_fraction"]))
            and recovery_budget == int(expected["recovery_budget"])
            and not verification_errors
            and corruption_rejected
            and elapsed <= float(config["time_budget_seconds"])
        ),
        "git_clean_at_start": not dirty,
        "method_a_state_count_passed": method_a.state_count
        == int(expected["labeled_count_vectors"]),
        "method_b_orbit_count_passed": method_b.state_count == int(expected["histogram_orbits"]),
        "probability_mass_one_both_methods": method_a.probability_mass
        == method_b.probability_mass
        == 1,
        "all_budget_values_agree_exactly": method_a.values == method_b.values,
        "independent_partition_verifier_passed": not verification_errors,
        "corruption_test_rejected_modified_certificate": corruption_rejected,
        "expected_endpoint_passed": upper == Fraction(str(expected["budget_8_fraction"])),
        "recovery_budget_passed": recovery_budget == int(expected["recovery_budget"]),
        "upper_endpoint_attainability_claimed": False,
        "global_private_team_optimality_claimed": False,
        "elapsed_seconds": elapsed,
        "time_budget_seconds": config["time_budget_seconds"],
    }
    _json(run_dir / "validation.json", validation)
    _json(
        run_dir / "metrics.json",
        {
            "labeled_count_vectors": method_a.state_count,
            "histogram_orbits": method_b.state_count,
            "frontier_budget_8_fraction": str(upper),
            "frontier_budget_8_decimal": float(upper),
            "private_team_lower_fraction": str(private_lower),
            "private_team_interval_gap_fraction": str(upper - private_lower),
            "private_team_interval_gap_decimal": float(upper - private_lower),
            "recovery_budget": recovery_budget,
        },
    )
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\n"
        f"method_a_states={method_a.state_count}\n"
        f"method_b_orbits={method_b.state_count}\n"
        f"frontier_L8={upper}\n"
        f"validation_status={'passed' if validation['passed'] else 'failed'}\n",
        encoding="utf-8",
    )
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    packages = subprocess.check_output(["uv", "pip", "freeze"], cwd=root, text=True).splitlines()
    _json(
        run_dir / "environment.json",
        {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "packages": sorted(
                line
                for line in packages
                if not line.lower().startswith("distributed-discovery @ file:")
            ),
        },
    )
    output_hashes = {
        str(path.relative_to(run_dir)): _sha(path)
        for path in sorted(outputs.iterdir())
        if path.is_file()
    }
    _json(run_dir / "output-checksums.json", output_hashes)
    ended = datetime.now(UTC)
    input_paths = [
        config_path,
        root / "src/distributed_discovery/canonical/exact_frontier.py",
        root / "src/distributed_discovery/canonical/exact_frontier_verification.py",
        root / "src/distributed_discovery/canonical/exact_frontier_study.py",
    ]
    command = "make canonical-exact-frontier"
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-000",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": ended.isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": command,
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": {"algorithm": None, "model": None},
        "outputs": output_hashes,
    }
    _json(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make canonical-exact-frontier\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# Exact canonical frontier run {run_id}\n\n"
        "Two exact exhaustive representations plus an independent partition verifier "
        "certify budgets one through eight. The pooled endpoint is not claimed attainable "
        "or globally tight for the private-team problem.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
