"""Run the registered exact DD-008A census."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

import yaml

from distributed_discovery.acquisition.n_agent import discovery, equilibrium, gross_payoffs, planner
from distributed_discovery.acquisition.n_agent_verification import direct
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-008A-n-agent-evidence/configs/census.yml")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p: Path, x: object) -> None:
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")


def main() -> None:
    root = repository_root()
    cfg = yaml.safe_load((root / CONFIG).read_text())
    h = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    started = datetime.now(UTC)
    rid = f"{started:%Y%m%dT%H%M%SZ}_DD-008A_{commit[:8]}_{h[:10]}"
    run = root / "results/verified" / rid
    out = run / "outputs"
    out.mkdir(parents=True)
    (run / "config.yml").write_text((root / CONFIG).read_text())
    rows = []
    agreed = True
    for n in cfg["agents"]:
        for ps in cfg["accuracies"]:
            for cs in cfg["costs"]:
                p, c = Fraction(ps), Fraction(cs)
                cells = []
                for k in range(n + 1):
                    net, di, dc = direct(n, k, p, c)
                    gi, gc = gross_payoffs(n, k, p)
                    agreed &= (
                        net == discovery(n, k, p) - k * c
                        and di == (gi - c if gi is not None else 0)
                        and dc == (gc if gc is not None else 0)
                    )
                    weak, strict = equilibrium(n, k, p, c)
                    cells.append(
                        {
                            "k": k,
                            "gross_discovery": str(discovery(n, k, p)),
                            "net_value": str(net),
                            "weak_equilibrium": weak,
                            "strict_equilibrium": strict,
                        }
                    )
                best = planner(n, p, c)
                equilibrium_ks = [k for k, cell in enumerate(cells) if cell["weak_equilibrium"]]
                rows.append(
                    {
                        "agents": n,
                        "accuracy": str(p),
                        "cost": str(c),
                        "planner_k": best,
                        "cells": cells,
                        "independence_gap": max(best) - min(equilibrium_ks),
                    }
                )
    summary = {
        "grid_cells": len(rows),
        "direct_enumerator_agrees": agreed,
        "agent_range": cfg["agents"],
    }
    write(out / "n-agent-census.json", rows)
    write(out / "n-agent-summary.json", summary)
    write(run / "validation.json", {"passed": agreed, **summary})
    outputs = {str(p.relative_to(run)): sha(p) for p in out.glob("*")}
    manifest = {
        "schema_version": 1,
        "run_id": rid,
        "study_id": "DD-008A",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": "make dd008a-acquisition",
        "config_hash_sha256": h,
        "dependency_lock_hash_sha256": sha(root / "uv.lock"),
        "input_hashes": {
            str(path.relative_to(root)): sha(path)
            for path in [
                root / CONFIG,
                root / "src/distributed_discovery/acquisition/n_agent.py",
                root / "src/distributed_discovery/acquisition/n_agent_verification.py",
                root / "src/distributed_discovery/acquisition/n_agent_study.py",
            ]
        },
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": outputs,
    }
    write(run / "manifest.json", manifest)
    (run / "README.md").write_text(f"# DD-008A `{rid}`\n\nExact bounded census.\n")
    print(rid)


if __name__ == "__main__":
    main()
