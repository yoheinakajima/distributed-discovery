"""Run the registered exact DD-022 study with immutable provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml

from distributed_discovery.coordination_free_sharing.model import serialize
from distributed_discovery.coordination_free_sharing.verification import build
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-022-coordination-free-positive-sharing/configs/registry.yml")
SOURCE_PATHS = (
    CONFIG,
    Path("src/distributed_discovery/coordination_free_sharing/model.py"),
    Path("src/distributed_discovery/coordination_free_sharing/private_game.py"),
    Path("src/distributed_discovery/coordination_free_sharing/shared_game.py"),
    Path("src/distributed_discovery/coordination_free_sharing/equilibrium.py"),
    Path("src/distributed_discovery/coordination_free_sharing/exact.py"),
    Path("src/distributed_discovery/coordination_free_sharing/thresholds.py"),
    Path("src/distributed_discovery/coordination_free_sharing/verification.py"),
    Path("src/distributed_discovery/coordination_free_sharing/study.py"),
    Path("src/distributed_discovery/coordination_free_sharing/cli.py"),
    Path("studies/DD-022-coordination-free-positive-sharing/model.md"),
    Path("studies/DD-022-coordination-free-positive-sharing/literature.md"),
    Path("studies/DD-022-coordination-free-positive-sharing/proof.md"),
    Path("studies/DD-022-coordination-free-positive-sharing/proof-audit.md"),
)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serialize(value), indent=2, sort_keys=True) + "\n")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SOURCE_PATHS:
        digest.update(str(relative).encode())
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def bundle(config: dict[str, Any], root: Path) -> dict[str, Any]:
    if config["study_id"] != "DD-022" or config["schema_version"] != (
        "dd022-coordination-free-positive-sharing-v1"
    ):
        raise ValueError("DD-022 config identity mismatch")
    data = build(config, source_fingerprint(root))
    if not data["verification"]["passed"] or not all(data["corruptions"].values()):
        raise RuntimeError("DD-022 exact verification failed")
    return data


def _peak_memory_mb() -> float:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value / (1024 * 1024) if sys.platform == "darwin" else value / 1024


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text())
    start = perf_counter()
    data = bundle(config, root)
    elapsed = perf_counter() - start
    peak = _peak_memory_mb()
    if elapsed > config["time_cap_seconds"] or peak > config["memory_cap_mb"]:
        raise RuntimeError("DD-022 exceeded a registered resource cap")
    preview = {
        **data["summary"],
        "verification_passed": data["verification"]["passed"],
        "all_corruptions_rejected": all(data["corruptions"].values()),
        "elapsed_seconds": round(elapsed, 6),
        "peak_memory_mb": round(peak, 3),
    }
    if args.preview:
        print(json.dumps(serialize(preview), indent=2, sort_keys=True))
        return
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip():
        raise RuntimeError("DD-022 primary run requires clean committed source")
    config_hash = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-022_{commit[:8]}_{config_hash[:10]}"
    run = root / "results/verified" / run_id
    if run.exists():
        raise RuntimeError("refusing overwrite")
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text())
    _write_json(outputs / "registry.json", data["rows"])
    _write_json(outputs / "summary.json", data["summary"])
    _write_json(outputs / "threshold-certificate.json", data["threshold_certificate"])
    _write_json(outputs / "verification.json", data["verification"])
    _write_json(outputs / "corruption-tests.json", data["corruptions"])
    ended = datetime.now(UTC)
    validation = {
        **data["verification"],
        "all_corruptions_rejected": all(data["corruptions"].values()),
        "elapsed_seconds": round(elapsed, 6),
        "peak_memory_mb": round(peak, 3),
        "time_cap_seconds": config["time_cap_seconds"],
        "memory_cap_mb": config["memory_cap_mb"],
    }
    _write_json(run / "validation.json", validation)
    (run / "stdout.txt").write_text(f"{run_id}\nexact DD-022 verification passed\n")
    (run / "stderr.txt").write_text("")
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-022",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": ended.isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd022-coordination-free-positive-sharing",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _hash(root / "uv.lock"),
        "input_hashes": {str(path): _hash(root / path) for path in SOURCE_PATHS},
        "random_seeds": config["random_seeds"],
        "outputs": {str(path.relative_to(run)): _hash(path) for path in sorted(outputs.glob("*"))},
        "resource_usage": {"elapsed_seconds": round(elapsed, 6), "peak_memory_mb": round(peak, 3)},
    }
    _write_json(run / "manifest.json", manifest)
    _write_json(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(f"# DD-022 {run_id}\n\nExact bounded equilibrium registry.\n")
    print(run_id)


if __name__ == "__main__":
    main()
