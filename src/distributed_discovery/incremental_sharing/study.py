"""Run the registered exact DD-020 incremental-sharing census."""

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
from typing import Any

import yaml

from distributed_discovery.incremental_sharing.verification import build
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-020-incremental-sharing/configs/census.yml")


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serial(value), indent=2, sort_keys=True) + "\n")


def bundle(config: dict[str, Any]) -> dict[str, Any]:
    if config["study_id"] != "DD-020" or config["schema_version"] != (
        "dd020-incremental-sharing-v1"
    ):
        raise ValueError("config identity mismatch")
    point_rows, channel_rows, verification, corruptions = build(config)
    if not verification["passed"] or not all(corruptions.values()):
        raise RuntimeError("DD-020 verification failed")
    point = next(row for row in channel_rows if row["channel_id"] == "noisy-point-half")
    shortlist = next(row for row in channel_rows if row["channel_id"] == "guaranteed-shortlist-two")
    increments = [row["increment"] for row in point_rows if row["increment"] is not None]
    return {
        "point_rows": point_rows,
        "channel_rows": channel_rows,
        "verification": verification,
        "corruptions": corruptions,
        "summary": {
            "parameter_cells": config["parameter_cells"],
            "protocol_rows": len(point_rows),
            "strictly_negative_point_increments": sum(value < 0 for value in increments),
            "zero_point_increments": sum(value == 0 for value in increments),
            "positive_point_increments": sum(value > 0 for value in increments),
            "dd019_channels": len(channel_rows),
            "same_accuracy_witness": point["one_person_accuracy"],
            "noisy_point_profile": point["profile"],
            "guaranteed_shortlist_profile": shortlist["profile"],
            "profiles_differ": point["profile"] != shortlist["profile"],
        },
    }


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text())
    start_clock = perf_counter()
    data = bundle(config)
    elapsed = perf_counter() - start_clock
    if elapsed > config["time_cap_seconds"]:
        raise RuntimeError("DD-020 exceeded its registered time cap")
    if args.preview:
        print(json.dumps(serial(data["summary"]), indent=2, sort_keys=True))
        return

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip():
        raise RuntimeError("DD-020 primary run requires clean committed source")
    config_hash = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-020_{commit[:8]}_{config_hash[:10]}"
    run = root / "results/verified" / run_id
    if run.exists():
        raise RuntimeError("refusing overwrite")
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text())
    write_json(outputs / "summary.json", data["summary"])
    write_json(outputs / "point-census.json", data["point_rows"])
    write_json(outputs / "channel-profiles.json", data["channel_rows"])
    write_json(outputs / "verification.json", data["verification"])
    write_json(outputs / "corruption-tests.json", data["corruptions"])
    validation = {
        **data["verification"],
        "all_corruptions_rejected": all(data["corruptions"].values()),
        "elapsed_seconds": round(elapsed, 6),
        "time_cap_seconds": config["time_cap_seconds"],
        "memory_cap_mb": config["memory_cap_mb"],
    }
    write_json(run / "validation.json", validation)
    (run / "stdout.txt").write_text(
        f"{run_id}\nexact incremental-sharing census and verification passed\n"
    )
    (run / "stderr.txt").write_text("")

    input_paths = [
        config_path,
        root / "src/distributed_discovery/incremental_sharing/model.py",
        root / "src/distributed_discovery/incremental_sharing/verification.py",
        root / "src/distributed_discovery/incremental_sharing/study.py",
        root / "src/distributed_discovery/signal_geometry/model.py",
        root / "studies/DD-020-incremental-sharing/model.md",
        root / "studies/DD-020-incremental-sharing/proof.md",
        root / "studies/DD-020-incremental-sharing/proof-audit.md",
        root / "studies/DD-020-incremental-sharing/literature.md",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-020",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd020-incremental-sharing",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": file_hash(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): file_hash(path) for path in input_paths},
        "random_seeds": config["random_seeds"],
        "outputs": {
            str(path.relative_to(run)): file_hash(path) for path in sorted(outputs.glob("*"))
        },
    }
    write_json(run / "manifest.json", manifest)
    write_json(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(
        f"# DD-020 {run_id}\n\nExact bounded incremental-sharing census.\n"
    )
    print(run_id)


if __name__ == "__main__":
    main()
