"""Execute the immutable, synthetic-only DD-007 recovery grid."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from distributed_discovery.audits.model import audit_events, generate_sessions
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-007-empirical-audits/configs/synthetic-recovery.yml")
SCHEMA_DIR = Path("schemas/discovery-events/v1")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _validator(root: Path, name: str) -> Draft202012Validator:
    schema = json.loads((root / SCHEMA_DIR / name).read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def _validate_records(
    root: Path,
    sessions: list[dict[str, Any]],
    events: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> None:
    for validator, records in [
        (_validator(root, "session.schema.json"), sessions),
        (_validator(root, "event.schema.json"), events),
        (_validator(root, "source.schema.json"), sources),
    ]:
        for record in records:
            validator.validate(record)


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    commit = _git(root, "rev-parse", "HEAD")
    started = datetime.now(UTC)
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-007_{commit[:8]}_{config_hash[:10]}"
    run_dir, output_dir = (
        root / "results/verified" / run_id,
        root / "results/verified" / run_id / "outputs",
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir()
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    rows: list[dict[str, Any]] = []
    all_schema_valid = True
    for copying_rate in config["copying_rates"]:
        for missing_rate in config["provenance_missing_rates"]:
            for error_rate in config["action_matching_error_rates"]:
                for seed in config["replicate_seeds"]:
                    sessions, events, sources = generate_sessions(
                        candidates=config["candidates"],
                        sessions=config["sessions_per_replicate"],
                        copying_rate=copying_rate,
                        protocol="private",
                        provenance_missing_rate=missing_rate,
                        matching_error_rate=error_rate,
                        seed=seed,
                    )
                    try:
                        _validate_records(root, sessions, events, sources)
                    except Exception:
                        all_schema_valid = False
                        raise
                    audit = audit_events(events, config["candidates"])
                    rows.append(
                        {
                            "copying_truth": copying_rate,
                            "provenance_missing_truth": missing_rate,
                            "matching_error_truth": error_rate,
                            "seed": seed,
                            "truth_in_interval": audit["ci_low"]
                            <= copying_rate
                            <= audit["ci_high"],
                            **audit,
                        }
                    )
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            f"copy={row['copying_truth']};missing={row['provenance_missing_truth']};"
            f"error={row['matching_error_truth']}"
        )
        groups[key].append(row)
    calibration = [
        {
            "condition": key,
            "replicates": len(values),
            "coverage": sum(bool(value["truth_in_interval"]) for value in values) / len(values),
            "mean_estimate": sum(float(value["copying_estimate"]) for value in values)
            / len(values),
        }
        for key, values in sorted(groups.items())
    ]
    counterexamples = [
        {
            "observable": "two-action agreement is one",
            "world_a": {"protocol": "private", "copying_rate": 1.0},
            "world_b": {"protocol": "consensus", "copying_rate": 0.0},
            "identified_copying_rate": False,
            "reason": (
                "When protocol labels are hidden, both worlds produce duplicate action pairs "
                "in every session."
            ),
        },
        {
            "observable": "source IDs are missing for every event",
            "world_a": {"source_concentration": "one shared source"},
            "world_b": {"source_concentration": "one private source per action"},
            "identified_effective_channels": False,
            "reason": "All-null provenance is compatible with both source allocations.",
        },
    ]
    validation = {
        "passed": all_schema_valid and len(rows) == 96 and len(counterexamples) == 2,
        "synthetic_only": True,
        "schema_records_valid": all_schema_valid,
        "grid_rows": len(rows),
        "counterexample_count": len(counterexamples),
    }
    _write(output_dir / "synthetic-recovery-grid.json", rows)
    _write(output_dir / "uncertainty-calibration.json", calibration)
    _write(output_dir / "identification-counterexamples.json", counterexamples)
    _write(run_dir / "validation.json", validation)
    _write(
        run_dir / "metrics.json",
        {"grid_rows": len(rows), "calibration_conditions": len(calibration)},
    )
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\ngrid_rows={len(rows)}\n", encoding="utf-8"
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
        "study_id": "DD-007",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": bool(_git(root, "status", "--porcelain")),
        "upstream_commit": None,
        "command": "make dd007-synthetic-audit",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {
            str(item.relative_to(root)): _sha(item)
            for item in [
                config_path,
                root / "src/distributed_discovery/audits/model.py",
                root / "src/distributed_discovery/audits/study.py",
                *(
                    root / SCHEMA_DIR / name
                    for name in ["event.schema.json", "session.schema.json", "source.schema.json"]
                ),
            ]
        },
        "random_seeds": {
            "algorithm": config["replicate_seeds"],
            "model": config["replicate_seeds"],
        },
        "outputs": outputs,
    }
    _write(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text("make dd007-synthetic-audit\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd007-synthetic-audit\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-007 run `{run_id}`\n\nSeeded synthetic-only estimator recovery grid.\n",
        encoding="utf-8",
    )
    print(run_id)
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
