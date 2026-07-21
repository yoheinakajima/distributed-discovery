"""Execute the immutable DD-006 score-difference mechanism catalogue."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.mechanisms.model import (
    REGIMES,
    check_truthful_direct,
    enumerate_symmetric_action_profiles,
)
from distributed_discovery.mechanisms.verification import ex_post_balance_passes
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-006-discovery-mechanisms/configs/score-difference.yml")


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
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-006_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    output_dir = run_dir / "outputs"
    run_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir()
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    catalogue: list[dict[str, object]] = []
    for regime in REGIMES:
        for coefficient in config["transfer_values"]:
            result = check_truthful_direct(regime, int(coefficient))
            catalogue.append(
                {
                    "regime": regime,
                    "coefficient": coefficient,
                    "truthful_direct_pure_bne": result["pure_bne"],
                    "strict_against_joint_deviations": result["strict"],
                    "direct_discovery_probability": result["discovery"],
                    "symmetric_action_profile_count": enumerate_symmetric_action_profiles(
                        regime, int(coefficient)
                    ),
                    "deviations": result["deviations"],
                }
            )
    balance = ex_post_balance_passes()
    positive_weak_cases = [
        row for row in catalogue if row["coefficient"] == 1 and row["truthful_direct_pure_bne"]
    ]
    validation = {
        "passed": len(catalogue) == 9
        and balance
        and len(positive_weak_cases) == 3
        and not any(row["strict_against_joint_deviations"] for row in catalogue),
        "ex_post_budget_balance": balance,
        "catalogue_entries": len(catalogue),
        "positive_weak_truthful_direct_cases": len(positive_weak_cases),
        "strict_truthful_direct_cases": sum(
            bool(row["strict_against_joint_deviations"]) for row in catalogue
        ),
    }
    _write(output_dir / "mechanism-catalogue.json", catalogue)
    _write(run_dir / "validation.json", validation)
    _write(run_dir / "metrics.json", {"mechanism_count": len(catalogue)})
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\nmechanisms={len(catalogue)}\n", encoding="utf-8"
    )
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    _write(
        run_dir / "environment.json",
        {"platform": platform.platform(), "python": platform.python_version()},
    )
    outputs = {
        str(item.relative_to(run_dir)): _sha(item)
        for item in output_dir.rglob("*")
        if item.is_file()
    }
    _write(run_dir / "output-checksums.json", outputs)
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-006",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": bool(_git(root, "status", "--porcelain")),
        "upstream_commit": None,
        "command": "make dd006-mechanisms",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {
            str(item.relative_to(root)): _sha(item)
            for item in [
                config_path,
                root / "src/distributed_discovery/mechanisms/model.py",
                root / "src/distributed_discovery/mechanisms/verification.py",
                root / "src/distributed_discovery/mechanisms/study.py",
            ]
        },
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": outputs,
    }
    _write(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text("make dd006-mechanisms\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd006-mechanisms\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-006 run `{run_id}`\n\nExact bounded score-difference mechanism catalogue.\n",
        encoding="utf-8",
    )
    print(run_id)
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
