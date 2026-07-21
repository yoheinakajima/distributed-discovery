"""Execute the registered DD-006B exact mechanism frontier."""

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

from distributed_discovery.mechanisms.joint import REGIMES, coefficient_vectors, frontier_row
from distributed_discovery.mechanisms.joint_verification import verify_row
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-006-discovery-mechanisms/configs/joint-mechanism.yml")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    root = repository_root()
    cp = root / CONFIG
    cfg = yaml.safe_load(cp.read_text())
    digest = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    started = datetime.now(UTC)
    rid = f"{started:%Y%m%dT%H%M%SZ}_DD-006B_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / rid
    out = run / "outputs"
    out.mkdir(parents=True)
    (run / "config.yml").write_text(cp.read_text())
    rows = [frontier_row(regime, vector) for regime in REGIMES for vector in coefficient_vectors()]
    valid = all(verify_row(row) for row in rows)
    summary = {
        "frontier_rows": len(rows),
        "weak_rows": sum(bool(r["weak"]) for r in rows),
        "strict_rows": sum(bool(r["strict"]) for r in rows),
        "maximum_margin": str(max(Fraction(str(r["all_tie_margin"])) for r in rows)),
        "strict_rows_with_positive_information_weight": sum(
            bool(r["strict"])
            and Fraction(str(cast(list[object], r["coefficients"])[0])) > 0
            for r in rows
        ),
        "all_rows_participation": all(
            bool(accounting["participation"])
            for row in rows
            for accounting in cast(
                list[dict[str, object]], row["accounting_by_tie_role"]
            )
        ),
        "independent_verifier": valid,
    }
    write(out / "joint-mechanism-frontier.json", rows)
    write(out / "joint-mechanism-summary.json", summary)
    write(run / "validation.json", {"passed": valid, **summary})
    outputs = {str(p.relative_to(run)): sha(p) for p in out.glob("*")}
    inputs = [
        cp,
        root / "src/distributed_discovery/mechanisms/joint.py",
        root / "src/distributed_discovery/mechanisms/joint_verification.py",
        root / "src/distributed_discovery/mechanisms/joint_study.py",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": rid,
        "study_id": "DD-006B",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if valid else 1,
        "validation_status": "passed" if valid else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": "make dd006b-joint-mechanism",
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": sha(root / "uv.lock"),
        "input_hashes": {str(p.relative_to(root)): sha(p) for p in inputs},
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": outputs,
    }
    write(run / "manifest.json", manifest)
    write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(
        f"# DD-006B `{rid}`\n\nExact bounded joint-mechanism frontier.\n"
    )
    print(rid)


if __name__ == "__main__":
    main()
