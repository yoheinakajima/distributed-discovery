"""Run or preview the registered bounded DD-017 equilibrium registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from copy import deepcopy
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml

from distributed_discovery.threshold_equilibrium.model import evaluate_registry
from distributed_discovery.threshold_equilibrium.verification import verify_registry
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-017-threshold-equilibrium-selection/configs/small-games.yml")


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
    if config["study_id"] != "DD-017":
        raise ValueError("wrong study id")
    agents = [int(value) for value in config["agent_grid"]]
    if agents != list(range(2, 7)):
        raise ValueError("registered agent grid changed")
    fixtures = config["posterior_fixtures"]
    if len(fixtures) != 8:
        raise ValueError("registered fixture count changed")
    for fixture in fixtures:
        posterior = tuple(Fraction(value) for value in fixture["posterior"])
        if any(value <= 0 for value in posterior) or sum(posterior, Fraction(0)) != 1:
            raise ValueError(f"invalid posterior fixture: {fixture['name']}")
    if int(config["expected_games"]) != len(fixtures) * sum(agents):
        raise ValueError("registered game count changed")
    if int(config["runtime_estimate_seconds"]) >= int(config["time_cap_seconds"]):
        raise ValueError("runtime estimate must remain below time cap")
    if int(config["memory_estimate_mb"]) >= int(config["memory_cap_mb"]):
        raise ValueError("memory estimate must remain below memory cap")


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    validate_config(config)
    registry = evaluate_registry(config["posterior_fixtures"], config["agent_grid"])
    if registry["game_count"] != int(config["expected_games"]):
        raise RuntimeError("game count differs from registration")
    if registry["occupancy_state_count"] != int(config["expected_occupancy_states"]):
        raise RuntimeError("occupancy state count differs from registration")
    verification = verify_registry(registry)
    if verification["labeled_profiles"] != int(config["expected_labeled_profiles"]):
        raise RuntimeError("labeled verification count differs from registration")
    if not verification["passed"]:
        raise RuntimeError("independent labeled verification failed")
    corruptions = corruption_tests(registry)
    if not all(corruptions.values()):
        raise RuntimeError("registered corruption test failed")
    return {
        "registry": registry,
        "verification": verification,
        "corruption_tests": corruptions,
    }


def corruption_tests(registry: dict[str, Any]) -> dict[str, bool]:
    tests = {}

    corrupt = deepcopy(registry)
    corrupt["games"][0]["pure_nash"].pop()
    tests["removed_equilibrium_rejected"] = not verify_registry(corrupt)["passed"]

    corrupt = deepcopy(registry)
    corrupt["games"][0]["best_equilibrium_discovery"] += Fraction(1, 10**9)
    tests["altered_best_discovery_rejected"] = not verify_registry(corrupt)["passed"]

    corrupt = deepcopy(registry)
    corrupt["games"][0]["tied_mode_mixed"]["is_equilibrium"] = not corrupt["games"][0][
        "tied_mode_mixed"
    ]["is_equilibrium"]
    tests["altered_tied_mode_classification_rejected"] = not verify_registry(corrupt)["passed"]

    corrupt = deepcopy(registry)
    corrupt["games"][0]["pure_nash"][0]["pairwise_strict_stable"] = not corrupt["games"][0][
        "pure_nash"
    ][0]["pairwise_strict_stable"]
    tests["altered_pair_stability_rejected"] = not verify_registry(corrupt)["passed"]
    return tests


def _summary(bundle: dict[str, Any]) -> dict[str, Any]:
    registry = bundle["registry"]
    return {
        "game_count": registry["game_count"],
        "occupancy_state_count": registry["occupancy_state_count"],
        "labeled_profiles": bundle["verification"]["labeled_profiles"],
        "zero_worst_equilibrium_games": registry["zero_worst_equilibrium_games"],
        "no_pairwise_stable_equilibrium_games": registry["no_pairwise_stable_equilibrium_games"],
        "no_tau_stable_equilibrium_games": registry["no_tau_stable_equilibrium_games"],
        "tied_mode_mixed_failures": registry["tied_mode_mixed_failures"],
        "all_corruptions_rejected": all(bundle["corruption_tests"].values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    started_clock = perf_counter()
    if args.preview:
        bundle = build_bundle(config)
        print(json.dumps(_serialize(_summary(bundle)), indent=2, sort_keys=True))
        return

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    if dirty:
        raise RuntimeError("DD-017 primary run requires a clean committed implementation")
    digest = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-017_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    if run.exists():
        raise RuntimeError(f"refusing to overwrite {run_id}")
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    bundle = build_bundle(config)
    elapsed = perf_counter() - started_clock
    if elapsed > int(config["time_cap_seconds"]):
        raise RuntimeError("DD-017 exceeded its registered time cap")
    _write(outputs / "summary.json", _summary(bundle))
    _write(outputs / "small-game-registry.json", bundle["registry"])
    _write(outputs / "verification.json", bundle["verification"])
    _write(outputs / "corruption-tests.json", bundle["corruption_tests"])
    validation = {
        "passed": True,
        "elapsed_seconds": round(elapsed, 6),
        "time_cap_seconds": int(config["time_cap_seconds"]),
        "all_corruptions_rejected": all(bundle["corruption_tests"].values()),
        **bundle["verification"],
    }
    _write(run / "validation.json", validation)
    (run / "stdout.txt").write_text(f"{run_id}\n", encoding="utf-8")
    (run / "stderr.txt").write_text("", encoding="utf-8")
    input_paths = [
        config_path,
        root / "src/distributed_discovery/threshold_equilibrium/model.py",
        root / "src/distributed_discovery/threshold_equilibrium/verification.py",
        root / "src/distributed_discovery/threshold_equilibrium/study.py",
        root / "studies/DD-017-threshold-equilibrium-selection/model.md",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-017",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd017-equilibrium",
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
        f"# DD-017 {run_id}\n\nBounded exact threshold-equilibrium registry.\n",
        encoding="utf-8",
    )
    print(run_id)


if __name__ == "__main__":
    main()
