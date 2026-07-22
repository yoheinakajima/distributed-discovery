"""Run the registered exact DD-019 signal-geometry study."""

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

from distributed_discovery.signal_geometry.verification import build
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-019-signal-geometry/configs/baseline.yml")


def serial(v: Any) -> Any:
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, dict):
        return {k: serial(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [serial(x) for x in v]
    return v


def write(path: Path, v: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serial(v), indent=2, sort_keys=True) + "\n")


def bundle(config: dict[str, Any]) -> dict[str, Any]:
    if config["study_id"] != "DD-019" or config["schema_version"] != "dd019-signal-geometry-v1":
        raise ValueError("config identity mismatch")
    rows, verification, corruptions = build()
    if [r["channel_id"] for r in rows] != config["channel_ids"]:
        raise ValueError("channel registry mismatch")
    if not verification["passed"] or not all(corruptions.values()):
        raise RuntimeError("verification failed")
    point = rows[0]
    short = rows[2]
    return {
        "rows": rows,
        "verification": verification,
        "corruptions": corruptions,
        "summary": {
            "channels": len(rows),
            "same_accuracy_witness": verification["same_accuracy"],
            "different_profile_witness": verification["different_profiles"],
            "witness_accuracy": point["one_person_accuracy"],
            "point_profile": point["profile"],
            "shortlist_profile": short["profile"],
            "point_recovery_budget": point["recovery_budget"],
            "shortlist_recovery_budget": short["recovery_budget"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text())
    start_clock = perf_counter()
    data = bundle(config)
    if args.preview:
        print(json.dumps(serial(data["summary"]), indent=2, sort_keys=True))
        return
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip():
        raise RuntimeError("DD-019 primary run requires clean committed source")
    digest = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-019_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    if run.exists():
        raise RuntimeError("refusing overwrite")
    out = run / "outputs"
    out.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text())
    write(out / "summary.json", data["summary"])
    write(out / "profiles.json", data["rows"])
    write(out / "verification.json", data["verification"])
    write(out / "corruption-tests.json", data["corruptions"])
    elapsed = perf_counter() - start_clock
    write(
        run / "validation.json",
        {
            **data["verification"],
            "all_corruptions_rejected": all(data["corruptions"].values()),
            "elapsed_seconds": round(elapsed, 6),
            "time_cap_seconds": config["time_cap_seconds"],
        },
    )
    (run / "stdout.txt").write_text(
        f"{run_id}\nexact signal profiles and independent verification passed\n"
    )
    (run / "stderr.txt").write_text("")

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    inputs = [
        config_path,
        root / "src/distributed_discovery/signal_geometry/model.py",
        root / "src/distributed_discovery/signal_geometry/verification.py",
        root / "src/distributed_discovery/signal_geometry/study.py",
        root / "studies/DD-019-signal-geometry/model.md",
        root / "studies/DD-019-signal-geometry/schemas/channel-v1.schema.json",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-019",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd019-signal-geometry",
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": sha(root / "uv.lock"),
        "input_hashes": {str(p.relative_to(root)): sha(p) for p in inputs},
        "random_seeds": config["random_seeds"],
        "outputs": {str(p.relative_to(run)): sha(p) for p in sorted(out.glob("*"))},
    }
    write(run / "manifest.json", manifest)
    write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(
        f"# DD-019 {run_id}\n\nExact bounded signal-geometry profiles.\n"
    )
    print(run_id)


if __name__ == "__main__":
    main()
