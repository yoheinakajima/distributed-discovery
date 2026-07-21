"""Run the registered exact DD-009 architecture atlas."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import cast

import yaml

from distributed_discovery.atlas.model import cartesian_registry, dominance, evaluate, validity
from distributed_discovery.atlas.verification import verify_row
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-009-discovery-architecture-atlas/configs/atlas.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text())
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-009_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text())

    registry = []
    rows = []
    for index, cell in enumerate(cartesian_registry(), start=1):
        valid, reason = validity(cell)
        registry.append({"cell_id": f"A{index:03d}", **cell, "valid": valid, "reason": reason})
        if valid:
            rows.append({"architecture_id": f"A{index:03d}", **evaluate(cell)})
    checks = [verify_row(row) for row in rows]
    pareto = dominance(rows)
    summary = {
        "cartesian_cells": len(registry),
        "valid_cells": len(rows),
        "invalid_cells": len(registry) - len(rows),
        "independent_rows_verified": sum(checks),
        "pareto_cells": len(cast(list[int], pareto["pareto_indices"])),
        "maximum_discovery": str(max(Fraction(str(row["discovery"])) for row in rows)),
        "maximum_social_net_value": str(
            max(Fraction(str(row["social_net_value"])) for row in rows)
        ),
    }
    passed = (
        all(checks)
        and len(registry) == config["cartesian_cells"]
        and len(rows) == config["registered_valid_cells"]
    )
    _write(outputs / "validity-registry.json", registry)
    _write(outputs / "architectures.json", rows)
    _write(outputs / "dominance.json", pareto)
    _write(outputs / "atlas-summary.json", summary)
    _write(outputs / "verification.json", {"passed": passed, "row_checks": checks})
    _write(run / "validation.json", {"passed": passed, **summary})

    output_hashes = {str(path.relative_to(run)): _sha(path) for path in outputs.glob("*.json")}
    input_paths = [
        config_path,
        root / "src/distributed_discovery/atlas/model.py",
        root / "src/distributed_discovery/atlas/verification.py",
        root / "src/distributed_discovery/atlas/study.py",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-009",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if passed else 1,
        "validation_status": "passed" if passed else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": "make dd009-atlas",
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": output_hashes,
    }
    _write(run / "manifest.json", manifest)
    _write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(f"# DD-009 `{run_id}`\n\nExact bounded architecture atlas.\n")
    print(run_id)


if __name__ == "__main__":
    main()
