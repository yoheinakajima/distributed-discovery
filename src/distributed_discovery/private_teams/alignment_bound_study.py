"""Run the immutable DD-001 alignment-preserving upper-bound study."""

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

from distributed_discovery.private_teams.alignment_bound import (
    alignment_bound_certificate,
    alignment_count_bound,
)
from distributed_discovery.private_teams.alignment_bound_verification import (
    verify_alignment_bound_certificate,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-001-private-information-teams/configs/alignment-upper-bound.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _checked_artifact(root: Path, run_id: str, relative: str) -> Path:
    run = root / "results/verified" / run_id
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    expected = manifest.get("outputs", {}).get(relative)
    artifact = run / relative
    if (
        manifest.get("run_id") != run_id
        or manifest.get("validation_status") != "passed"
        or manifest.get("exit_status") != 0
        or not isinstance(expected, str)
        or not artifact.is_file()
        or _sha(artifact) != expected
    ):
        raise RuntimeError(f"invalid benchmark artifact: {run_id}/{relative}")
    return artifact


def _benchmark_rows(source: Path, deadline: float) -> tuple[list[dict[str, Any]], bool, bool]:
    rows: list[dict[str, Any]] = []
    all_upper_valid = True
    all_certificates_valid = True
    with source.open(encoding="utf-8") as handle:
        for record in csv.DictReader(handle):
            if time.monotonic() > deadline:
                raise RuntimeError("tiny-case validation exceeded the time budget")
            candidates = int(record["candidates"])
            searchers = int(record["searchers"])
            accuracy = Fraction(record["accuracy"])
            optimum = Fraction(record["optimum_fraction"])
            result = alignment_count_bound(candidates, searchers, accuracy)
            certificate_errors = verify_alignment_bound_certificate(
                alignment_bound_certificate(result)
            )
            upper_valid = result.discovery_upper_bound >= optimum
            rows.append(
                {
                    "case": record["case"],
                    "candidates": candidates,
                    "searchers": searchers,
                    "accuracy": str(accuracy),
                    "exact_optimum": str(optimum),
                    "alignment_upper_bound": str(result.discovery_upper_bound),
                    "relaxation_gap": str(result.discovery_upper_bound - optimum),
                    "relaxation_exact": result.discovery_upper_bound == optimum,
                    "upper_valid": upper_valid,
                    "certificate_valid": not certificate_errors,
                }
            )
            all_upper_valid = all_upper_valid and upper_valid
            all_certificates_valid = all_certificates_valid and not certificate_errors
    return rows, all_upper_valid, all_certificates_valid


def _anti_informative_rows(
    source: Path, deadline: float
) -> tuple[list[dict[str, Any]], bool, bool]:
    records = json.loads(source.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    all_upper_valid = True
    all_certificates_valid = True
    for record in records:
        if time.monotonic() > deadline:
            raise RuntimeError("anti-informative validation exceeded the time budget")
        candidates = int(record["candidates"])
        searchers = 2
        accuracy = Fraction(str(record["accuracy"]))
        optimum = Fraction(str(record["unrestricted_optimum"]))
        result = alignment_count_bound(candidates, searchers, accuracy)
        certificate_errors = verify_alignment_bound_certificate(alignment_bound_certificate(result))
        upper_valid = result.discovery_upper_bound >= optimum
        rows.append(
            {
                "case": f"M{candidates}_N2_p0",
                "candidates": candidates,
                "searchers": searchers,
                "accuracy": str(accuracy),
                "exact_optimum": str(optimum),
                "alignment_upper_bound": str(result.discovery_upper_bound),
                "relaxation_gap": str(result.discovery_upper_bound - optimum),
                "relaxation_exact": result.discovery_upper_bound == optimum,
                "upper_valid": upper_valid,
                "certificate_valid": not certificate_errors,
            }
        )
        all_upper_valid = all_upper_valid and upper_valid
        all_certificates_valid = all_certificates_valid and not certificate_errors
    return rows, all_upper_valid, all_certificates_valid


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


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
    deadline = start + float(config["time_budget_seconds"])
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-001_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"))

    tiny_config = config["tiny_source"]
    tiny_path = _checked_artifact(root, tiny_config["run_id"], tiny_config["artifact"])
    anti_config = config["anti_informative_source"]
    anti_path = _checked_artifact(root, anti_config["run_id"], anti_config["artifact"])
    tiny_rows, tiny_upper_valid, tiny_certificates_valid = _benchmark_rows(tiny_path, deadline)
    anti_rows, anti_upper_valid, anti_certificates_valid = _anti_informative_rows(
        anti_path, deadline
    )
    _write_csv(outputs / "tiny-alignment-bounds.csv", tiny_rows)
    _write_csv(outputs / "anti-informative-alignment-bounds.csv", anti_rows)

    canonical = config["canonical"]
    candidates = int(canonical["candidates"])
    searchers = int(canonical["searchers"])
    accuracy = Fraction(str(canonical["accuracy"]))
    direct_lower = Fraction(str(canonical["direct_lower_fraction"]))
    pooled_upper = Fraction(str(canonical["pooled_upper_fraction"]))
    canonical_start = time.monotonic()
    result = alignment_count_bound(candidates, searchers, accuracy)
    canonical_seconds = time.monotonic() - canonical_start
    certificate = alignment_bound_certificate(result)
    certificate["claim_ids"] = ["DD-C-0037", "DD-C-0038"]
    certificate["comparison"] = {
        "attainable_direct_lower_fraction": str(direct_lower),
        "prior_pooled_upper_fraction": str(pooled_upper),
        "strictly_below_pooled": result.discovery_upper_bound < pooled_upper,
        "matches_attainable_direct_lower": result.discovery_upper_bound == direct_lower,
        "private_team_optimum_fraction": (
            str(direct_lower) if result.discovery_upper_bound == direct_lower else None
        ),
    }
    _json(outputs / "canonical-alignment-bound-certificate.json", certificate)

    verification_errors = verify_alignment_bound_certificate(certificate)
    corrupted = copy.deepcopy(certificate)
    corrupted["target_dp"]["values"][-1][-1] = "0"
    corruption_errors = verify_alignment_bound_certificate(corrupted)
    corruption_rejected = bool(corruption_errors)
    _json(
        outputs / "independent-verification.json",
        {
            "schema_version": 1,
            "method": (
                "Bellman lower inequalities plus one exact equality witness per state; "
                "no minimization call"
            ),
            "certificate_errors": verification_errors,
            "corruption_test": {
                "mutation": "replace final target-DP value with zero",
                "rejected": corruption_rejected,
                "errors": corruption_errors,
            },
        },
    )

    certificate_size = (outputs / "canonical-alignment-bound-certificate.json").stat().st_size
    elapsed = time.monotonic() - start
    _json(
        outputs / "cost-audit.json",
        {
            "schema_version": 1,
            "bounded_before_execution": True,
            "declared_time_budget_seconds": config["time_budget_seconds"],
            "declared_memory_budget_mb": config["memory_budget_mb"],
            "column_state_slots": len(result.column_values) * len(result.column_values[0]),
            "target_state_slots": len(result.target_values) * len(result.target_values[0]),
            "column_transition_count": result.column_transition_count,
            "target_transition_count": result.target_transition_count,
            "canonical_elapsed_seconds": canonical_seconds,
            "total_elapsed_seconds": elapsed,
            "certificate_bytes": certificate_size,
            "checkpoint_strategy": (
                "atomic immutable run outputs; state space is bounded below the resume threshold"
            ),
            "interruption_outcome": "no substantive claim; preserve a failed run if manifested",
            "randomness": None,
        },
    )

    validation_config = config["validation"]
    expected_canonical = Fraction(str(validation_config["regression_canonical_upper_fraction"]))
    validation = {
        "passed": bool(
            not dirty
            and len(tiny_rows) == int(validation_config["expected_tiny_cases"])
            and len(anti_rows) == int(validation_config["expected_anti_informative_cases"])
            and tiny_upper_valid
            and anti_upper_valid
            and tiny_certificates_valid
            and anti_certificates_valid
            and not verification_errors
            and corruption_rejected
            and result.discovery_upper_bound == expected_canonical == direct_lower
            and result.discovery_upper_bound < pooled_upper
            and elapsed <= float(config["time_budget_seconds"])
            and certificate_size < int(config["memory_budget_mb"]) * 1024 * 1024
        ),
        "git_clean_at_start": not dirty,
        "tiny_case_count_passed": len(tiny_rows) == int(validation_config["expected_tiny_cases"]),
        "anti_informative_case_count_passed": len(anti_rows)
        == int(validation_config["expected_anti_informative_cases"]),
        "upper_valid_all_tiny_cases": tiny_upper_valid,
        "upper_valid_all_anti_informative_cases": anti_upper_valid,
        "all_tiny_and_anti_certificates_passed": tiny_certificates_valid
        and anti_certificates_valid,
        "independent_bellman_verifier_passed": not verification_errors,
        "corruption_test_rejected_modified_certificate": corruption_rejected,
        "canonical_upper_matches_regression": result.discovery_upper_bound == expected_canonical,
        "canonical_upper_matches_attainable_direct_lower": result.discovery_upper_bound
        == direct_lower,
        "canonical_strictly_improves_pooled_upper": result.discovery_upper_bound < pooled_upper,
        "canonical_global_private_team_optimality_certified": (
            result.discovery_upper_bound == direct_lower
        ),
        "elapsed_seconds": elapsed,
        "time_budget_seconds": config["time_budget_seconds"],
        "certificate_bytes": certificate_size,
        "memory_budget_mb": config["memory_budget_mb"],
    }
    _json(run_dir / "validation.json", validation)
    _json(
        run_dir / "metrics.json",
        {
            "tiny_case_count": len(tiny_rows),
            "tiny_exact_count": sum(row["relaxation_exact"] for row in tiny_rows),
            "anti_informative_case_count": len(anti_rows),
            "anti_informative_exact_count": sum(row["relaxation_exact"] for row in anti_rows),
            "canonical_alignment_upper_fraction": str(result.discovery_upper_bound),
            "canonical_direct_lower_fraction": str(direct_lower),
            "prior_pooled_upper_fraction": str(pooled_upper),
            "prior_interval_gap_closed_fraction": str(pooled_upper - direct_lower),
            "canonical_target_resource_pattern": list(result.target_resource_pattern),
        },
    )
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\n"
        f"tiny_cases={len(tiny_rows)}\n"
        f"anti_informative_cases={len(anti_rows)}\n"
        f"canonical_upper={result.discovery_upper_bound}\n"
        f"direct_lower={direct_lower}\n"
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
        tiny_path,
        anti_path,
        root / "docs/decisions/ADR-0009-alignment-bound-relaxation.md",
        root / "src/distributed_discovery/private_teams/alignment_bound.py",
        root / "src/distributed_discovery/private_teams/alignment_bound_verification.py",
        root / "src/distributed_discovery/private_teams/alignment_bound_study.py",
    ]
    command = "make dd001-alignment-bound"
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-001",
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
        "#!/bin/sh\nset -eu\nexec make dd001-alignment-bound\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-001 alignment-bound run {run_id}\n\n"
        "Exact joint-column global-count relaxation, complete prior tiny-case and "
        "anti-informative validation, and an independently checked canonical Bellman "
        "certificate. Claim scope is controlled by DD-C-0037 and DD-C-0038.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"canonical_upper={result.discovery_upper_bound}")
    print(f"validation_status={manifest['validation_status']}")
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
