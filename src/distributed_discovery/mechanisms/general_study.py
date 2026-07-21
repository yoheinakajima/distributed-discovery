"""Execute the immutable DD-006A normalized transfer frontier census."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.mechanisms.general import coefficient_vectors, frontier_row
from distributed_discovery.mechanisms.general_verification import verify_row
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-006-discovery-mechanisms/configs/general-transfer-frontier.yml")


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
    commit, started = _git(root, "rev-parse", "HEAD"), datetime.now(UTC)
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-006A_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    output_dir = run_dir / "outputs"
    run_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir()
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    rows = [
        frontier_row(regime, vector)
        for regime in config["observability_regimes"]
        for vector in coefficient_vectors()
    ]
    verified = all(verify_row(row) for row in rows)
    margins = [Fraction(str(row["all_tie_rules_margin"])) for row in rows]
    corrupted = dict(rows[0])
    corrupted["coefficients"] = ["2", "0", "0", "0"]
    summary = {
        "registered_vectors": len(coefficient_vectors()),
        "frontier_rows": len(rows),
        "weak_all_tie_rules": sum(bool(row["weak_implements_all_ties"]) for row in rows),
        "strict_all_tie_rules": sum(bool(row["strictly_implements_all_ties"]) for row in rows),
        "maximum_all_tie_margin": str(max(margins)),
        "independent_balance_verifier": verified,
        "corruption_rejected": not verify_row(corrupted),
    }
    validation = {
        "passed": verified and summary["corruption_rejected"] and len(rows) == 123,
        **summary,
    }
    _write(output_dir / "general-transfer-frontier.json", rows)
    _write(output_dir / "general-transfer-summary.json", summary)
    _write(run_dir / "validation.json", validation)
    _write(run_dir / "metrics.json", {"frontier_rows": len(rows)})
    (run_dir / "stdout.log").write_text(f"run_id={run_id}\nrows={len(rows)}\n", encoding="utf-8")
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
        "command": "make dd006-general-frontier",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {
            str(item.relative_to(root)): _sha(item)
            for item in [
                config_path,
                root / "src/distributed_discovery/mechanisms/general.py",
                root / "src/distributed_discovery/mechanisms/general_verification.py",
                root / "src/distributed_discovery/mechanisms/general_study.py",
            ]
        },
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": outputs,
    }
    _write(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text("make dd006-general-frontier\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd006-general-frontier\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-006A run `{run_id}`\n\nExact normalized linear transfer frontier.\n",
        encoding="utf-8",
    )
    print(run_id)
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
