"""Execute the pinned upstream verifier and record an immutable DD-000 run."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.canonical.model import (
    blind_discovery,
    independent_count_frontier,
    private_discovery,
    private_expected_distinct,
    tiny_consensus_bruteforce,
)
from distributed_discovery.validation.bootstrap import repository_root

UPSTREAM_RELATIVE = Path(".cache/upstream/shared-discovery-paradox")
CONFIG_RELATIVE = Path("experiments/configs/canonical-baseline.yml")
LOCK_RELATIVE = Path("integrations/shared-discovery-paradox/upstream-requirements.lock")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _parse_metrics(stdout: str) -> dict[str, float | int]:
    patterns = {
        "consensus": r"^  consensus\s+([0-9.]+)$",
        "market": r"^  symmetric market\s+([0-9.]+)$",
        "private": r"^  private clue-following\s+([0-9.]+)$",
        "planner": r"^  planner portfolio\s+([0-9.]+)$",
        "market_distinct": r"^  E distinct \(market\)\s+([0-9.]+)$",
        "private_distinct": r"^  E distinct \(private\)\s+([0-9.]+)$",
        "crossover": r"^  crossover c\*\s+([0-9.]+)",
    }
    metrics: dict[str, float | int] = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, stdout, flags=re.MULTILINE)
        if match is None:
            raise RuntimeError(f"could not parse upstream metric {name}")
        metrics[name] = float(match.group(1))
    metrics["blind"] = 0.5
    return metrics


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    root = repository_root()
    upstream = root / UPSTREAM_RELATIVE
    config_path = root / CONFIG_RELATIVE
    dependency_lock = root / LOCK_RELATIVE
    config_bytes = config_path.read_bytes()
    config = yaml.safe_load(config_bytes)
    config_hash = hashlib.sha256(config_bytes).hexdigest()
    upstream_commit = _git(upstream, "rev-parse", "HEAD")
    if upstream_commit != config["upstream_commit"]:
        raise RuntimeError("cached upstream does not match the configured pinned commit")
    commit = _git(root, "rev-parse", "HEAD")
    dirty = bool(_git(root, "status", "--porcelain"))
    started = datetime.now(UTC)
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-000_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/baseline" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    output_dir = run_dir / "outputs"
    output_dir.mkdir()
    shutil.copy2(config_path, run_dir / "config.yml")

    environment_dir = root / ".cache/upstream/reproduction-venv"
    if not (environment_dir / "bin/python").is_file():
        subprocess.run(["uv", "venv", str(environment_dir), "--python", "3.11"], check=True)
    subprocess.run(
        [
            "uv",
            "pip",
            "sync",
            "--python",
            str(environment_dir / "bin/python"),
            str(dependency_lock),
        ],
        cwd=root,
        check=True,
    )
    command = [
        str(Path(".cache/upstream/reproduction-venv/bin/python")),
        str(UPSTREAM_RELATIVE / config["verification_script"]),
        "--out-dir",
        str(output_dir.relative_to(root)),
    ]
    portable_command = (
        ".cache/upstream/reproduction-venv/bin/python "
        ".cache/upstream/shared-discovery-paradox/verify_shared_discovery_v8_6.py "
        f"--out-dir results/baseline/{run_id}/outputs"
    )
    (run_dir / "command.txt").write_text(portable_command + "\n", encoding="utf-8")
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    (run_dir / "stdout.log").write_text(completed.stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(completed.stderr, encoding="utf-8")
    ended = datetime.now(UTC)

    metrics: dict[str, float | int] = {}
    validation: dict[str, Any] = {"upstream_exit_zero": completed.returncode == 0}
    if completed.returncode == 0:
        metrics = _parse_metrics(completed.stdout)
        frontier, normalization = independent_count_frontier(16, 8, 0.2)
        independent = {
            "blind": float(blind_discovery(16, 8)),
            "private": float(private_discovery(8, Fraction(1, 5))),
            "private_distinct": float(private_expected_distinct(16, 8, Fraction(1, 5))),
            "consensus": frontier[0],
            "planner": frontier[-1],
            "count_probability_sum": normalization,
            "tiny_consensus_M3_N2_p0.5": float(tiny_consensus_bruteforce(3, 2, Fraction(1, 2))),
            "recovery_budget": next(
                budget
                for budget, value in enumerate(frontier, start=1)
                if value >= float(metrics["private"])
            ),
        }
        metrics["recovery_budget"] = independent["recovery_budget"]
        metrics.update({f"independent_{key}": value for key, value in independent.items()})
        expected = config["expected_rounded_sanity_checks"]
        validation.update(
            {
                "completion_marker": "All v8.6 checks passed." in completed.stdout,
                "rounded_sanity_checks": {
                    name: round(float(metrics[name]), len(str(value).split(".")[-1])) == value
                    for name, value in expected.items()
                },
                "independent_matches": {
                    "blind": abs(independent["blind"] - float(metrics["blind"])) < 1e-15,
                    "private": abs(independent["private"] - float(metrics["private"])) < 5e-12,
                    "private_distinct": abs(
                        independent["private_distinct"] - float(metrics["private_distinct"])
                    )
                    < 5e-12,
                    "consensus": abs(independent["consensus"] - float(metrics["consensus"]))
                    < 5e-12,
                    "planner": abs(independent["planner"] - float(metrics["planner"])) < 5e-12,
                    "normalization": abs(independent["count_probability_sum"] - 1.0) < 3e-12,
                },
            }
        )
    validation["passed"] = bool(
        completed.returncode == 0
        and validation.get("completion_marker")
        and all(validation.get("rounded_sanity_checks", {}).values())
        and all(validation.get("independent_matches", {}).values())
    )
    _write_json(run_dir / "metrics.json", metrics)
    _write_json(run_dir / "validation.json", validation)

    package_lines = subprocess.check_output(
        ["uv", "pip", "freeze", "--python", str(environment_dir / "bin/python")], text=True
    ).splitlines()
    _write_json(
        run_dir / "environment.json",
        {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": subprocess.check_output(
                [str(environment_dir / "bin/python"), "--version"], text=True
            ).strip(),
            "packages": sorted(package_lines),
        },
    )
    outputs = sorted(path for path in output_dir.rglob("*") if path.is_file())
    output_hashes = {str(path.relative_to(run_dir)): _sha256(path) for path in outputs}
    _write_json(run_dir / "output-checksums.json", output_hashes)
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-000",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": ended.isoformat().replace("+00:00", "Z"),
        "exit_status": completed.returncode,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": upstream_commit,
        "command": portable_command,
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha256(dependency_lock),
        "input_hashes": {
            str(CONFIG_RELATIVE): hashlib.sha256(config_bytes).hexdigest(),
            str(UPSTREAM_RELATIVE / config["verification_script"]): _sha256(
                upstream / config["verification_script"]
            ),
        },
        "random_seeds": {
            "upstream_script": "fixed internally; inspect pinned script",
            "independent_checks": None,
        },
        "outputs": output_hashes,
    }
    _write_json(run_dir / "manifest.json", manifest)
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make reproduce-baseline\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# Canonical reproduction run `{run_id}`\n\n"
        "Executed the pinned upstream verifier and independent finite-model checks. "
        "See `validation.json` for evidence categories and `manifest.json` for provenance.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    if not validation["passed"]:
        print(completed.stdout)
        print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode or 1)


if __name__ == "__main__":
    main()
