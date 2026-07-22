"""Separately labeled exact threshold-two planner extension for DD-015."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from functools import cache
from itertools import product
from pathlib import Path
from time import perf_counter
from typing import Any, cast

import yaml

from distributed_discovery.dynamic_attention.model import (
    Objective,
    Prescription,
    _branches,
    initial_belief,
    normalize,
    prescriptions,
    signal_probability,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-015-dynamic-attention/configs/threshold-two.yml")


@dataclass(frozen=True)
class ThresholdValue:
    discovery: Fraction
    expected_actions: Fraction


def solve_threshold_planner(
    private_accuracy: Fraction, shared_accuracy: Fraction, objective: Objective
) -> dict[str, Any]:
    choices: dict[tuple[int, tuple[Fraction, ...], tuple[int, int, int]], Prescription] = {}
    policy: dict[str, Prescription] = {}
    states = 0

    @cache
    def solve(
        stage: int,
        belief: tuple[Fraction, ...],
        occupancy: tuple[int, int, int],
    ) -> ThresholdValue:
        nonlocal states
        states += 1
        if stage == 3:
            return ThresholdValue(
                sum(
                    (belief[target] for target, count in enumerate(occupancy) if count >= 2),
                    Fraction(),
                ),
                Fraction(),
            )
        best: ThresholdValue | None = None
        best_rule: Prescription | None = None
        for rule in prescriptions():
            discovery = Fraction()
            future_actions = Fraction()
            for action, branch_mass, action_belief in _branches(belief, private_accuracy, rule):
                next_occupancy = list(occupancy)
                next_occupancy[action] += 1
                next_counts = tuple(next_occupancy)
                becomes_viable = next_counts[action] >= 2
                if objective == "fixed-budget":
                    future = solve(stage + 1, action_belief, next_counts)
                    discovery += branch_mass * future.discovery
                    future_actions += branch_mass * future.expected_actions
                elif becomes_viable:
                    success_mass = branch_mass * action_belief[action]
                    failure_weights = tuple(
                        value if target != action else Fraction()
                        for target, value in enumerate(action_belief)
                    )
                    failure_mass = sum(failure_weights, Fraction())
                    discovery += success_mass
                    if failure_mass and stage + 1 < 3:
                        future = solve(stage + 1, normalize(failure_weights), next_counts)
                        discovery += branch_mass * failure_mass * future.discovery
                        future_actions += branch_mass * failure_mass * future.expected_actions
                else:
                    future = solve(stage + 1, action_belief, next_counts)
                    discovery += branch_mass * future.discovery
                    future_actions += branch_mass * future.expected_actions
            value = ThresholdValue(discovery, Fraction(1) + future_actions)
            if (
                best is None
                or value.discovery > best.discovery
                or (
                    value.discovery == best.discovery
                    and value.expected_actions < best.expected_actions
                )
                or (value == best and best_rule is not None and rule < best_rule)
            ):
                best, best_rule = value, rule
        if best is None or best_rule is None:
            raise RuntimeError("threshold planner found no prescription")
        choices[(stage, belief, occupancy)] = best_rule
        return best

    roots = [solve(0, initial_belief(shared, shared_accuracy), (0, 0, 0)) for shared in range(3)]

    def materialize(
        stage: int,
        shared: int,
        history: tuple[int, ...],
        belief: tuple[Fraction, ...],
        occupancy: tuple[int, int, int],
    ) -> None:
        if stage == 3:
            return
        rule = choices[(stage, belief, occupancy)]
        policy[f"{objective}|{shared}|{','.join(map(str, history))}"] = rule
        for action, _, action_belief in _branches(belief, private_accuracy, rule):
            next_counts = list(occupancy)
            next_counts[action] += 1
            counts = cast(tuple[int, int, int], tuple(next_counts))
            if objective == "stopping-on-success" and counts[action] >= 2:
                failure = tuple(
                    value if target != action else Fraction()
                    for target, value in enumerate(action_belief)
                )
                if sum(failure, Fraction()) and stage + 1 < 3:
                    materialize(
                        stage + 1,
                        shared,
                        (*history, action),
                        normalize(failure),
                        counts,
                    )
            else:
                materialize(
                    stage + 1,
                    shared,
                    (*history, action),
                    action_belief,
                    counts,
                )

    for shared in range(3):
        materialize(
            0,
            shared,
            (),
            initial_belief(shared, shared_accuracy),
            (0, 0, 0),
        )
    return {
        "discovery": sum((root.discovery for root in roots), Fraction()) / 3,
        "expected_actions": sum((root.expected_actions for root in roots), Fraction()) / 3,
        "expected_rounds": sum((root.expected_actions for root in roots), Fraction()) / 3,
        "policy": policy,
        "state_evaluations": states,
    }


def enumerate_threshold_policy(
    private_accuracy: Fraction,
    shared_accuracy: Fraction,
    objective: Objective,
    policy: dict[str, Prescription],
) -> dict[str, Any]:
    mass = Fraction()
    discovery = Fraction()
    actions_used = Fraction()
    categories = {
        "start-new-singleton": Fraction(),
        "join-singleton": Fraction(),
        "join-viable-team": Fraction(),
        "follow-shared-clue": Fraction(),
        "oppose-shared-clue": Fraction(),
    }
    for target, shared, clues in product(range(3), range(3), product(range(3), repeat=3)):
        probability = Fraction(1, 3) * signal_probability(shared, target, shared_accuracy)
        for clue in clues:
            probability *= signal_probability(clue, target, private_accuracy)
        mass += probability
        history: tuple[int, ...] = ()
        counts = [0, 0, 0]
        hit = False
        for clue in clues:
            if objective == "stopping-on-success" and hit:
                break
            key = f"{objective}|{shared}|{','.join(map(str, history))}"
            action = policy[key][clue]
            if counts[action] == 0:
                categories["start-new-singleton"] += probability
            elif counts[action] == 1:
                categories["join-singleton"] += probability
            else:
                categories["join-viable-team"] += probability
            categories["follow-shared-clue" if action == shared else "oppose-shared-clue"] += (
                probability
            )
            counts[action] += 1
            history = (*history, action)
            hit = hit or (counts[action] >= 2 and action == target)
        discovery += probability * int(hit)
        actions_used += probability * len(history)
    return {
        "probability_mass": mass,
        "discovery": discovery,
        "expected_actions": actions_used,
        "expected_rounds": actions_used,
        "category_mass": categories,
        "labeled_paths": 243,
    }


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    if config["scope"] != "planner-only-separately-labeled-extension":
        raise ValueError("threshold extension scope changed")
    rows = []
    for private_accuracy in config["private_accuracies"]:
        for shared_accuracy in config["shared_accuracies"]:
            p, q = Fraction(private_accuracy), Fraction(shared_accuracy)
            for objective in config["objectives"]:
                planner = solve_threshold_planner(p, q, objective)
                direct = enumerate_threshold_policy(p, q, objective, planner["policy"])
                if (
                    direct["probability_mass"] != 1
                    or direct["discovery"] != planner["discovery"]
                    or direct["expected_actions"] != planner["expected_actions"]
                ):
                    raise RuntimeError("threshold extension policy-tree mismatch")
                planner["category_mass"] = direct["category_mass"]
                rows.append(
                    {
                        "cell_id": f"p{p}-q{q}-{objective}",
                        "private_accuracy": p,
                        "shared_accuracy": q,
                        "objective": objective,
                        "planner": planner,
                    }
                )
    corruptions = {}
    for name, field in (
        ("altered-discovery", "discovery"),
        ("altered-actions", "expected_actions"),
    ):
        changed = copy.deepcopy(rows[0])
        changed["planner"][field] += Fraction(1, 100)
        direct = enumerate_threshold_policy(
            changed["private_accuracy"],
            changed["shared_accuracy"],
            changed["objective"],
            changed["planner"]["policy"],
        )
        corruptions[f"{name}-rejected"] = direct[field] != changed["planner"][field]
    summary = {
        "parameter_cells": 16,
        "objective_rows": len(rows),
        "labeled_target_signal_paths": 3888,
        "start_new_singleton_rows": sum(
            row["planner"]["category_mass"]["start-new-singleton"] > 0 for row in rows
        ),
        "join_singleton_rows": sum(
            row["planner"]["category_mass"]["join-singleton"] > 0 for row in rows
        ),
        "join_viable_team_rows": sum(
            row["planner"]["category_mass"]["join-viable-team"] > 0 for row in rows
        ),
        "follow_shared_rows": sum(
            row["planner"]["category_mass"]["follow-shared-clue"] > 0 for row in rows
        ),
        "oppose_shared_rows": sum(
            row["planner"]["category_mass"]["oppose-shared-clue"] > 0 for row in rows
        ),
        "corruption_gates": len(corruptions),
    }
    return {"rows": rows, "summary": summary, "corruption_tests": corruptions}


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
    path.write_text(json.dumps(_serialize(value), indent=2, sort_keys=True) + "\n")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text())
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if (
        not args.preview
        and subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    ):
        raise RuntimeError("DD-015 threshold extension requires a clean tree")
    digest = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    started = datetime.now(UTC)
    clock = perf_counter()
    bundle = build_bundle(config)
    elapsed = perf_counter() - clock
    if args.preview:
        print(json.dumps(_serialize(bundle["summary"]), indent=2, sort_keys=True))
        return
    if elapsed > int(config["time_cap_seconds"]):
        raise RuntimeError("DD-015 threshold extension exceeded its cap")
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-015_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text())
    _write(outputs / "threshold-two-summary.json", bundle["summary"])
    _write(outputs / "threshold-two-profile.json", bundle["rows"])
    _write(outputs / "corruption-tests.json", bundle["corruption_tests"])
    _write(
        run / "validation.json",
        {
            "passed": True,
            "elapsed_seconds": round(elapsed, 6),
            "time_cap_seconds": config["time_cap_seconds"],
        },
    )
    output_hashes = {str(path.relative_to(run)): _sha(path) for path in sorted(outputs.glob("*"))}
    _write(
        run / "manifest.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "study_id": "DD-015",
            "started_utc": started.isoformat().replace("+00:00", "Z"),
            "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "exit_status": 0,
            "validation_status": "passed",
            "git_commit": commit,
            "git_dirty": False,
            "upstream_commit": None,
            "command": "make dd015-threshold-extension",
            "config_hash_sha256": digest,
            "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
            "input_hashes": {
                str(CONFIG): _sha(config_path),
                "src/distributed_discovery/dynamic_attention/threshold_extension.py": _sha(
                    Path(__file__)
                ),
            },
            "random_seeds": config["random_seeds"],
            "outputs": output_hashes,
        },
    )
    _write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "stdout.txt").write_text(f"{run_id}\nthreshold-two extension passed\n")
    (run / "stderr.txt").write_text("")
    (run / "README.md").write_text(
        f"# DD-015 `{run_id}`\n\nSecondary threshold-two planner extension.\n"
    )
    print(run_id)


if __name__ == "__main__":
    main()
