"""Run the registered exact DD-016 threshold-discovery study."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from math import comb
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml

from distributed_discovery.threshold_discovery.model import (
    labeled_canonical_evaluation,
)
from distributed_discovery.threshold_discovery.verification import (
    corruption_tests,
    histogram_canonical_evaluation,
    planner_audit,
    strategic_payoff_audit,
    verify_bundle,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-016-threshold-discovery/configs/canonical.yml")


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
    candidates = int(config["candidates"])
    agents = int(config["agents"])
    accuracy = Fraction(config["clue_accuracy"])
    wrong = Fraction(config["wrong_clue_probability"])
    if wrong != (1 - accuracy) / (candidates - 1):
        raise ValueError("wrong-clue probability is inconsistent")
    expected = comb(candidates + agents - 1, candidates - 1)
    if int(config["labeled_count_vectors"]) != expected:
        raise ValueError("registered labeled count-vector count is inconsistent")
    if list(config["thresholds"]) != list(range(1, agents + 1)):
        raise ValueError("threshold grid must be 1 through N")
    if int(config["runtime_estimate_seconds"]) >= int(config["time_cap_seconds"]):
        raise ValueError("runtime estimate must be below the hard cap")
    if int(config["memory_estimate_mb"]) >= int(config["memory_cap_mb"]):
        raise ValueError("memory estimate must be below the hard cap")


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    validate_config(config)
    candidates = int(config["candidates"])
    agents = int(config["agents"])
    accuracy = Fraction(config["clue_accuracy"])
    thresholds = [int(value) for value in config["thresholds"]]
    method_a = labeled_canonical_evaluation(candidates, agents, accuracy, thresholds)
    method_b = histogram_canonical_evaluation(candidates, agents, accuracy, thresholds)
    bundle: dict[str, Any] = {
        "schema_version": config["schema_version"],
        "config": config,
        "method_a": method_a,
        "method_b": method_b,
        "planner_audit": planner_audit(),
        "strategic_payoff_audit": strategic_payoff_audit(),
    }
    bundle["verification"] = verify_bundle(bundle)
    bundle["corruption_tests"] = corruption_tests(bundle)
    if not bundle["verification"]["passed"] or not all(bundle["corruption_tests"].values()):
        raise RuntimeError("DD-016 exact verification failed")
    canonical = method_a["rows"][1]
    bundle["summary"] = {
        "labeled_count_vectors": method_a["state_count"],
        "histogram_orbits": method_b["state_count"],
        "signal_classes": method_a["signal_classes"],
        "threshold_rows": len(method_a["rows"]),
        "method_rows_equal": method_a["rows"] == method_b["rows"],
        "common_deterministic_mode": canonical["common_deterministic_mode_discovery"],
        "tied_mode_mixed": canonical["tied_mode_mixed_discovery"],
        "private_hard_discovery": canonical["private_clue_following"],
        "paired_planner": canonical["planner_discovery"],
        "expected_distinct_candidates": canonical["expected_distinct_candidates"],
        "expected_viable_candidates": canonical["expected_viable_candidates"],
        "expected_largest_crowd": canonical["expected_largest_crowd"],
        "pair_collision": canonical["pair_collision"],
        "target_selected_at_least_one": canonical["target_selected_at_least_one"],
        "target_selected_exactly_one": canonical["target_selected_exactly_one"],
        "target_opens": canonical["tied_mode_mixed_discovery"],
    }
    return bundle


def _tiny_config(config: dict[str, Any]) -> dict[str, Any]:
    tiny = dict(config)
    tiny.update(
        {
            "candidates": 3,
            "agents": 3,
            "clue_accuracy": "1/2",
            "wrong_clue_probability": "1/4",
            "thresholds": [1, 2, 3],
            "labeled_count_vectors": 10,
        }
    )
    return tiny


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preview",
        action="store_true",
        help="evaluate without writing an immutable run",
    )
    parser.add_argument(
        "--tiny",
        action="store_true",
        help="use the hand-checkable M=3, N=3 preview fixture",
    )
    args = parser.parse_args()

    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if args.tiny:
        config = _tiny_config(config)
    if args.tiny and not args.preview:
        raise RuntimeError("the tiny fixture is preview-only")

    started_clock = perf_counter()
    if args.preview:
        bundle = build_bundle(config)
        print(json.dumps(_serialize(bundle["summary"]), indent=2, sort_keys=True))
        return

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    if dirty:
        raise RuntimeError("DD-016 primary run requires a clean committed implementation")
    digest = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-016_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    if run.exists():
        raise RuntimeError(f"refusing to overwrite {run_id}")
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    bundle = build_bundle(config)
    elapsed = perf_counter() - started_clock
    if elapsed > int(config["time_cap_seconds"]):
        raise RuntimeError("DD-016 exceeded its registered time cap")
    _write(outputs / "canonical-metrics.json", bundle["summary"])
    _write(outputs / "threshold-phase-diagram.json", bundle["method_a"]["rows"])
    _write(
        outputs / "method-agreement.json",
        {
            "method_a": {
                key: bundle["method_a"][key]
                for key in ("method", "state_count", "probability_mass", "signal_classes")
            },
            "method_b": {
                key: bundle["method_b"][key]
                for key in ("method", "state_count", "probability_mass", "signal_classes")
            },
            "rows_equal": bundle["method_a"]["rows"] == bundle["method_b"]["rows"],
        },
    )
    _write(outputs / "planner-audit.json", bundle["planner_audit"])
    _write(outputs / "strategic-payoff-audit.json", bundle["strategic_payoff_audit"])
    _write(outputs / "verification.json", bundle["verification"])
    _write(outputs / "corruption-tests.json", bundle["corruption_tests"])
    validation = {
        **bundle["verification"],
        "all_corruptions_rejected": all(bundle["corruption_tests"].values()),
        "elapsed_seconds": round(elapsed, 6),
        "time_cap_seconds": int(config["time_cap_seconds"]),
    }
    _write(run / "validation.json", validation)
    (run / "stdout.txt").write_text(
        f"{run_id}\nexact threshold census and independent verification passed\n",
        encoding="utf-8",
    )
    (run / "stderr.txt").write_text("", encoding="utf-8")
    input_paths = [
        config_path,
        root / "src/distributed_discovery/threshold_discovery/model.py",
        root / "src/distributed_discovery/threshold_discovery/verification.py",
        root / "src/distributed_discovery/threshold_discovery/study.py",
        root / "studies/DD-016-threshold-discovery/proof.md",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-016",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd016-threshold",
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
        f"# DD-016 {run_id}\n\nExact bounded threshold-discovery census.\n",
        encoding="utf-8",
    )
    print(run_id)


if __name__ == "__main__":
    main()
