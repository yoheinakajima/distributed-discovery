"""Run the registered exact DD-018 minimum-viable-team mechanism census."""

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

from distributed_discovery.team_mechanisms.model import MECHANISMS, evaluate_registry
from distributed_discovery.team_mechanisms.verification import (
    corruption_tests,
    verify_registry,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-018-minimum-viable-team-mechanisms/configs/baseline.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _serialize(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_serialize(value), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_config(config: dict[str, Any]) -> None:
    if config["study_id"] != "DD-018" or config["schema_version"] != "dd018-team-mechanisms-v1":
        raise ValueError("DD-018 config identity mismatch")
    if (
        int(config["candidates"]) != 3
        or int(config["agents"]) != 4
        or int(config["threshold"]) != 2
    ):
        raise ValueError("DD-018 v1 fixes M=3, N=4, tau=2")
    if tuple(config["mechanisms"]) != tuple(spec.name for spec in MECHANISMS):
        raise ValueError("mechanism registry differs from frozen source")
    if int(config["labeled_action_profiles_per_fixture"]) != int(config["candidates"]) ** int(
        config["agents"]
    ):
        raise ValueError("labeled action-profile count mismatch")
    if int(config["mechanism_fixture_rows"]) != len(MECHANISMS) * len(config["posterior_fixtures"]):
        raise ValueError("mechanism-fixture row count mismatch")
    if int(config["runtime_estimate_seconds"]) >= int(config["time_cap_seconds"]):
        raise ValueError("runtime estimate must be below the cap")
    if int(config["memory_estimate_mb"]) >= int(config["memory_cap_mb"]):
        raise ValueError("memory estimate must be below the cap")
    for fixture in config["posterior_fixtures"]:
        posterior = tuple(Fraction(value) for value in fixture["posterior"])
        if sum(posterior, Fraction()) != 1 or tuple(sorted(posterior, reverse=True)) != posterior:
            raise ValueError(f"invalid posterior fixture {fixture['name']}")


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    validate_config(config)
    registry = evaluate_registry(config)
    verification = verify_registry(registry, config)
    corruptions = corruption_tests(registry, config)
    if not verification["passed"] or not all(corruptions.values()):
        raise RuntimeError("DD-018 exact verification failed")
    rows = registry["rows"]
    unilateral_applicable = [row for row in rows if isinstance(row["obedience"], bool)]
    summary = {
        "posterior_fixtures": registry["fixture_count"],
        "mechanisms": registry["mechanism_count"],
        "mechanism_fixture_rows": registry["mechanism_fixture_rows"],
        "labeled_action_profiles_per_fixture": registry["labeled_action_profiles_per_fixture"],
        "independent_action_table_entries": verification["independent_action_table_entries"],
        "planner_portfolio_rows": sum(row["implements_planner_portfolio"] for row in rows),
        "unilateral_applicable_rows": len(unilateral_applicable),
        "obedient_unilateral_applicable_rows": sum(
            row["obedience"] is True for row in unilateral_applicable
        ),
        "pair_stable_unilateral_applicable_rows": sum(
            row["pairwise_strict_stable"] is True for row in unilateral_applicable
        ),
        "tau_stable_unilateral_applicable_rows": sum(
            row["tau_player_strict_stable"] is True for row in unilateral_applicable
        ),
        "strict_unilateral_applicable_rows": sum(
            row["strict_unilateral_obedience"] is True for row in unilateral_applicable
        ),
        "all_rows_participation": all(row["participation"] for row in rows),
        "all_rows_weak_budget_balance": all(row["weak_budget_balance"] for row in rows),
        "all_rows_zero_external_subsidy": all(row["external_subsidy"] == 0 for row in rows),
        "all_truthfulness_not_applicable": all(
            row["report_truthfulness"] == "not-applicable-common-posterior-input" for row in rows
        ),
        "universal_pooling_planner_rows": sum(
            row["implements_planner_portfolio"]
            for row in rows
            if row["name"] == "universal-pooling"
        ),
        "marginal_contribution_planner_stable_rows": sum(
            row["implements_planner_portfolio"]
            and row["obedience"] is True
            and row["pairwise_strict_stable"] is True
            and row["tau_player_strict_stable"] is True
            for row in rows
            if row["name"] == "marginal-coalition-contribution"
        ),
        "all_corruptions_rejected": all(corruptions.values()),
    }
    return {
        "registry": registry,
        "verification": verification,
        "corruption_tests": corruptions,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    started_clock = perf_counter()
    bundle = build_bundle(config)
    if args.preview:
        print(json.dumps(_serialize(bundle["summary"]), indent=2, sort_keys=True))
        return

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    if dirty:
        raise RuntimeError("DD-018 primary run requires a clean committed implementation")
    digest = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-018_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    if run.exists():
        raise RuntimeError(f"refusing to overwrite {run_id}")
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    elapsed = perf_counter() - started_clock
    if elapsed > int(config["time_cap_seconds"]):
        raise RuntimeError("DD-018 exceeded its registered time cap")
    _write(outputs / "summary.json", bundle["summary"])
    _write(outputs / "mechanism-census.json", bundle["registry"]["rows"])
    _write(outputs / "verification.json", bundle["verification"])
    _write(outputs / "corruption-tests.json", bundle["corruption_tests"])
    _write(
        outputs / "mechanism-schema.json",
        {
            "schema_version": config["schema_version"],
            "mechanisms": [_serialize(spec.__dict__) for spec in MECHANISMS],
        },
    )
    validation = {
        **bundle["verification"],
        "all_corruptions_rejected": all(bundle["corruption_tests"].values()),
        "elapsed_seconds": round(elapsed, 6),
        "time_cap_seconds": int(config["time_cap_seconds"]),
    }
    _write(run / "validation.json", validation)
    (run / "stdout.txt").write_text(
        f"{run_id}\nexact team-mechanism census and independent verification passed\n",
        encoding="utf-8",
    )
    (run / "stderr.txt").write_text("", encoding="utf-8")
    input_paths = [
        config_path,
        root / "src/distributed_discovery/team_mechanisms/model.py",
        root / "src/distributed_discovery/team_mechanisms/verification.py",
        root / "src/distributed_discovery/team_mechanisms/study.py",
        root / "studies/DD-018-minimum-viable-team-mechanisms/model.md",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-018",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd018-team-mechanisms",
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": config["random_seeds"],
        "outputs": {str(path.relative_to(run)): _sha(path) for path in sorted(outputs.glob("*"))},
    }
    _write(run / "manifest.json", manifest)
    _write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(
        f"# DD-018 {run_id}\n\nExact bounded minimum-viable-team mechanism census.\n",
        encoding="utf-8",
    )
    print(run_id)


if __name__ == "__main__":
    main()
