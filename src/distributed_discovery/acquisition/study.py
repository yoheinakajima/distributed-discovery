"""Execute the immutable DD-008 exact source-choice grid."""

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

from distributed_discovery.acquisition.model import PROFILES, equilibria, planner, values
from distributed_discovery.acquisition.verification import agrees
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-008-endogenous-evidence-acquisition/configs/baseline.yml")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _write(p: Path, v: Any) -> None:
    p.write_text(json.dumps(v, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def main() -> None:
    root = repository_root()
    cp = root / CONFIG
    cfg = yaml.safe_load(cp.read_text())
    h = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    commit = _git(root, "rev-parse", "HEAD")
    started = datetime.now(UTC)
    rid = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-008_{commit[:8]}_{h[:10]}"
    run = root / "results/verified" / rid
    out = run / "outputs"
    run.mkdir(parents=True)
    out.mkdir()
    (run / "config.yml").write_text(cp.read_text())
    rows = []
    all_agree = True
    trap_cells = 0
    for ps, cs in __import__("itertools").product(cfg["accuracies"], cfg["costs"]):
        p, c = Fraction(ps), Fraction(cs)
        eq = equilibria(p, c)
        pl = planner(p, c)
        trap = eq == ["CC"] and set(pl) == {"CI", "IC"}
        agreement = {x: agrees(x, p, c) for x in PROFILES}
        all_agree = all_agree and all(agreement.values())
        trap_cells += int(trap)
        rows.append(
            {
                "accuracy": str(p),
                "cost": str(c),
                "equilibria": eq,
                "planner": pl,
                "common_source_trap": trap,
                "profiles": {
                    x: {
                        "social_net_value": str(values(x, p, c)[0]),
                        "payoffs": [str(y) for y in values(x, p, c)[1]],
                        "direct_enumerator_agrees": agreement[x],
                    }
                    for x in PROFILES
                },
            }
        )
    summary = {
        "grid_cells": len(rows),
        "direct_enumerator_agrees": all_agree,
        "common_source_trap_cells": trap_cells,
    }
    validation = {
        "passed": summary["direct_enumerator_agrees"] and summary["common_source_trap_cells"] > 0,
        **summary,
    }
    _write(out / "source-choice-grid.json", rows)
    _write(out / "source-choice-summary.json", summary)
    _write(run / "validation.json", validation)
    _write(run / "metrics.json", {"grid_cells": len(rows)})
    (run / "stdout.log").write_text(f"run_id={rid}\n", encoding="utf-8")
    (run / "stderr.log").write_text("")
    _write(
        run / "environment.json",
        {"platform": platform.platform(), "python": platform.python_version()},
    )
    outputs = {str(x.relative_to(run)): _sha(x) for x in out.rglob("*") if x.is_file()}
    _write(run / "output-checksums.json", outputs)
    manifest = {
        "schema_version": 1,
        "run_id": rid,
        "study_id": "DD-008",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": bool(_git(root, "status", "--porcelain")),
        "upstream_commit": None,
        "command": "make dd008-acquisition",
        "config_hash_sha256": h,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {
            str(x.relative_to(root)): _sha(x)
            for x in [
                cp,
                root / "src/distributed_discovery/acquisition/model.py",
                root / "src/distributed_discovery/acquisition/verification.py",
                root / "src/distributed_discovery/acquisition/study.py",
            ]
        },
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": outputs,
    }
    _write(run / "manifest.json", manifest)
    (run / "command.txt").write_text("make dd008-acquisition\n")
    (run / "reproduce.sh").write_text("#!/bin/sh\nset -eu\nexec make dd008-acquisition\n")
    os.chmod(run / "reproduce.sh", 0o755)
    (run / "README.md").write_text(f"# DD-008 `{rid}`\n\nExact synthetic source-choice grid.\n")
    print(rid)
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
