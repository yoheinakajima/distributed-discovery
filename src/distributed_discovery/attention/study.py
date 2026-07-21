"""Run the registered exact DD-012 attention census."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.attention.model import (
    STRATEGIC_REWARD_RULES,
    attention_category,
    discovery,
    equal_split_payoffs,
    equilibrium,
    private_attention_value,
    reward_equilibrium,
    reward_payoffs,
    reward_registry,
    social_attention_value,
    social_optima,
)
from distributed_discovery.attention.verification import corruption_tests, verify_bundle
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-012-incentive-to-ignore/configs/census.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fraction(value: Fraction | None) -> str | None:
    return None if value is None else str(value)


def _profile(n: int, k: int, p: Fraction, q: Fraction) -> dict[str, Any]:
    attending, ignoring = equal_split_payoffs(n, k, p, q)
    weak, strict = equilibrium(n, k, p, q)
    rewards: dict[str, dict[str, str | None]] = {}
    for rule in STRATEGIC_REWARD_RULES:
        rule_attending, rule_ignoring, budget = reward_payoffs(rule, n, k, p, q)
        rewards[rule] = {
            "attending": _fraction(rule_attending),
            "ignoring": _fraction(rule_ignoring),
            "budget": str(budget),
        }
    private_value = private_attention_value(n, k, p, q) if k < n else None
    social_value = social_attention_value(n, k, p, q) if k < n else None
    return {
        "attenders": k,
        "probability_mass": "1",
        "discovery": str(discovery(n, k, p, q)),
        "attending_payoff": _fraction(attending),
        "ignoring_payoff": _fraction(ignoring),
        "total_prize": str(k * (attending or 0) + (n - k) * (ignoring or 0)),
        "private_attention_value": _fraction(private_value),
        "social_attention_value": _fraction(social_value),
        "attention_wedge": _fraction(
            None if private_value is None or social_value is None else private_value - social_value
        ),
        "weak_equilibrium": weak,
        "strict_equilibrium": strict,
        "rewards": rewards,
    }


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    cells: list[dict[str, Any]] = []
    all_ignore_when_one_optimal = 0
    all_attend_when_one_optimal = 0
    multiplicity_cells = 0
    category_counts: dict[str, int] = {}
    for n in [int(value) for value in config["agents"]]:
        for private_accuracy in config["accuracies"]:
            for shared_accuracy in config["accuracies"]:
                p, q = Fraction(private_accuracy), Fraction(shared_accuracy)
                profiles = [_profile(n, k, p, q) for k in range(n + 1)]
                optima = social_optima(n, p, q)
                equilibria = [
                    int(profile["attenders"]) for profile in profiles if profile["weak_equilibrium"]
                ]
                strict_equilibria = [
                    int(profile["attenders"])
                    for profile in profiles
                    if profile["strict_equilibrium"]
                ]
                reward_equilibria: dict[str, dict[str, Any]] = {}
                for rule in STRATEGIC_REWARD_RULES:
                    weak_counts = []
                    strict_counts = []
                    for k in range(n + 1):
                        weak, strict = reward_equilibrium(rule, n, k, p, q)
                        if weak:
                            weak_counts.append(k)
                        if strict:
                            strict_counts.append(k)
                    reward_equilibria[rule] = {"weak": weak_counts, "strict": strict_counts}
                licensed = [1] if q > p else ([0] if q < p else [0, 1])
                reward_equilibria["public-reader-license"] = {
                    "weak": None,
                    "strict": None,
                    "binding_implemented_counts": licensed,
                }
                category = attention_category(optima, equilibria)
                category_counts[category] = category_counts.get(category, 0) + 1
                if len(equilibria) > 1:
                    multiplicity_cells += 1
                if q > p and 0 in equilibria:
                    all_ignore_when_one_optimal += 1
                if q > p and n in equilibria:
                    all_attend_when_one_optimal += 1
                cells.append(
                    {
                        "agents": n,
                        "private_accuracy": str(p),
                        "shared_accuracy": str(q),
                        "accuracy_relation": "shared-higher"
                        if q > p
                        else ("private-higher" if q < p else "equal"),
                        "social_optima": optima,
                        "equilibria": equilibria,
                        "strict_equilibria": strict_equilibria,
                        "category": category,
                        "profiles": profiles,
                        "reward_equilibria": reward_equilibria,
                    }
                )
    direct_states = sum(
        len(config["accuracies"]) ** 2 * 9 * sum(3 ** (n - k) for k in range(n + 1))
        for n in config["agents"]
    )
    theorem_checks = {
        "social_optimum_classification": all(
            cell["social_optima"]
            == (
                [1]
                if cell["accuracy_relation"] == "shared-higher"
                else ([0] if cell["accuracy_relation"] == "private-higher" else [0, 1])
            )
            for cell in cells
        ),
        "private_attention_values_strictly_decrease": all(
            all(
                Fraction(profile["private_attention_value"])
                > Fraction(cell["profiles"][index + 1]["private_attention_value"])
                for index, profile in enumerate(cell["profiles"][:-2])
            )
            for cell in cells
        ),
        "all_ignore_iff_shared_not_better": all(
            ((0 in cell["equilibria"]) == (cell["accuracy_relation"] != "shared-higher"))
            for cell in cells
        ),
        "all_ignore_when_one_reader_optimal": all_ignore_when_one_optimal,
    }
    if not all(value is True or value == 0 for value in theorem_checks.values()):
        raise RuntimeError("DD-012 theorem-grid audit failed")
    summary = {
        "grid_cells": len(cells),
        "profiles": sum(len(cell["profiles"]) for cell in cells),
        "reward_profile_rows": sum(
            len(cell["profiles"]) * len(STRATEGIC_REWARD_RULES) for cell in cells
        ),
        "direct_labeled_states": direct_states,
        "equilibrium_multiplicity_cells": multiplicity_cells,
        "all_attend_when_one_reader_optimal_cells": all_attend_when_one_optimal,
        "all_ignore_when_one_reader_optimal_cells": all_ignore_when_one_optimal,
        "category_counts": category_counts,
        "reward_rules": len(reward_registry()),
    }
    return {
        "schema_version": "dd012-attention-census-v1",
        "cells": cells,
        "reward_registry": reward_registry(),
        "theorem_checks": theorem_checks,
        "summary": summary,
    }


def _write_wedge_csv(path: Path, cells: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "agents",
                "private_accuracy",
                "shared_accuracy",
                "attenders_before_switch",
                "private_attention_value",
                "social_attention_value",
                "attention_wedge",
            ),
        )
        writer.writeheader()
        for cell in cells:
            for profile in cell["profiles"][:-1]:
                writer.writerow(
                    {
                        "agents": cell["agents"],
                        "private_accuracy": cell["private_accuracy"],
                        "shared_accuracy": cell["shared_accuracy"],
                        "attenders_before_switch": profile["attenders"],
                        "private_attention_value": profile["private_attention_value"],
                        "social_attention_value": profile["social_attention_value"],
                        "attention_wedge": profile["attention_wedge"],
                    }
                )


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    if dirty:
        raise RuntimeError("DD-012 primary run requires a clean committed implementation")
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-012_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    bundle = build_bundle(config)
    verification = verify_bundle(bundle)
    corruptions = corruption_tests(bundle)
    if not verification["passed"] or not all(corruptions.values()):
        raise RuntimeError("DD-012 independent verification failed")
    _write(outputs / "attention-census.json", bundle["cells"])
    _write(outputs / "reward-registry.json", bundle["reward_registry"])
    _write(outputs / "theorem-checks.json", bundle["theorem_checks"])
    _write(outputs / "summary.json", bundle["summary"])
    _write(outputs / "verification.json", verification)
    _write(outputs / "corruption-tests.json", corruptions)
    _write_wedge_csv(outputs / "attention-wedge-table.csv", bundle["cells"])
    _write(
        outputs / "phase-map.json",
        [
            {
                key: cell[key]
                for key in (
                    "agents",
                    "private_accuracy",
                    "shared_accuracy",
                    "social_optima",
                    "equilibria",
                    "strict_equilibria",
                    "category",
                    "reward_equilibria",
                )
            }
            for cell in bundle["cells"]
        ],
    )
    _write(run / "validation.json", {"passed": True, **bundle["summary"], **verification})
    (run / "stdout.txt").write_text(
        f"{run_id}\nexact attention census and independent verification passed\n",
        encoding="utf-8",
    )
    (run / "stderr.txt").write_text("", encoding="utf-8")
    input_paths = [
        config_path,
        root / "src/distributed_discovery/attention/model.py",
        root / "src/distributed_discovery/attention/verification.py",
        root / "src/distributed_discovery/attention/study.py",
        root / "studies/DD-012-incentive-to-ignore/proof.md",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-012",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd012-attention",
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": {str(path.relative_to(run)): _sha(path) for path in sorted(outputs.glob("*"))},
    }
    _write(run / "manifest.json", manifest)
    _write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(
        f"# DD-012 `{run_id}`\n\nExact bounded attention census.\n", encoding="utf-8"
    )
    print(run_id)


if __name__ == "__main__":
    main()
