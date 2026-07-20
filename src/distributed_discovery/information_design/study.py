"""Run the immutable DD-002 bounded public-disclosure fixture."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import os
import platform
import subprocess
import time
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.information_design.game import (
    Likelihood,
    Partition,
    canonical_partitions,
    message_posterior,
    planner_discovery,
    pure_equilibria,
    refines,
    symmetric_equilibrium,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-002-information-design/configs/bounded-disclosure.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(_jsonable(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _partition_key(partition: Partition) -> str:
    return "|".join(",".join(str(item) for item in block) for block in partition)


def _direct_symmetric_discovery(
    posterior: tuple[Fraction, ...], strategy: tuple[Fraction, ...]
) -> Fraction:
    total = Fraction(0)
    for target, target_probability in enumerate(posterior):
        discovered = Fraction(0)
        for first, second in itertools.product(range(len(posterior)), repeat=2):
            probability = strategy[first] * strategy[second]
            if target in (first, second):
                discovered += probability
        total += target_probability * discovered
    return total


def _verify_symmetric_best_response(
    posterior: tuple[Fraction, ...], strategy: tuple[Fraction, ...]
) -> bool:
    payoffs = tuple(
        posterior[action] * (1 - strategy[action] / 2) for action in range(len(posterior))
    )
    maximum = max(payoffs)
    return all(
        payoffs[action] == maximum if probability > 0 else payoffs[action] <= maximum
        for action, probability in enumerate(strategy)
    )


def _evaluate_partition(
    partition_id: str, partition: Partition, likelihood: Likelihood, pure_limit: int
) -> dict[str, Any]:
    messages: list[dict[str, Any]] = []
    pure_lists = []
    for message_id, block in enumerate(partition):
        weight, posterior = message_posterior(likelihood, block)
        pure = pure_equilibria(posterior)
        symmetric = symmetric_equilibrium(posterior)
        direct_symmetric = _direct_symmetric_discovery(posterior, symmetric.strategy)
        messages.append(
            {
                "message_id": message_id,
                "evidence_block": block,
                "probability": weight,
                "posterior": posterior,
                "pure_equilibria": [
                    {
                        "actions": equilibrium.actions,
                        "payoffs": equilibrium.payoffs,
                        "discovery": equilibrium.discovery,
                    }
                    for equilibrium in pure
                ],
                "anonymous_symmetric_equilibrium": {
                    "strategy": symmetric.strategy,
                    "discovery": symmetric.discovery,
                    "direct_state_discovery": direct_symmetric,
                    "best_response_verified": _verify_symmetric_best_response(
                        posterior, symmetric.strategy
                    ),
                },
                "planner_discovery": planner_discovery(posterior),
            }
        )
        pure_lists.append(pure)

    pure_count = 1
    for pure in pure_lists:
        pure_count *= len(pure)
    if pure_count > pure_limit:
        raise RuntimeError(f"{partition_id} pure correspondence exceeds configured limit")
    global_pure: list[dict[str, Any]] = []
    for choices in itertools.product(*(range(len(pure)) for pure in pure_lists)):
        discovery = sum(
            (
                messages[index]["probability"] * pure_lists[index][choice].discovery
                for index, choice in enumerate(choices)
            ),
            start=Fraction(0),
        )
        global_pure.append(
            {
                "message_equilibrium_indices": choices,
                "message_action_profiles": tuple(
                    pure_lists[index][choice].actions for index, choice in enumerate(choices)
                ),
                "discovery": discovery,
            }
        )
    selected = sum(
        (
            message["probability"] * message["anonymous_symmetric_equilibrium"]["discovery"]
            for message in messages
        ),
        start=Fraction(0),
    )
    planner = sum(
        (message["probability"] * message["planner_discovery"] for message in messages),
        start=Fraction(0),
    )
    concentration = sum(
        (
            message["probability"]
            * sum(
                (
                    probability * probability
                    for probability in message["anonymous_symmetric_equilibrium"]["strategy"]
                ),
                start=Fraction(0),
            )
            for message in messages
        ),
        start=Fraction(0),
    )
    discoveries = [item["discovery"] for item in global_pure]
    return {
        "partition_id": partition_id,
        "partition": partition,
        "messages": messages,
        "selected_equilibrium": "anonymous-symmetric",
        "selected_discovery": selected,
        "selected_action_hhi": concentration,
        "selected_expected_distinct_actions": 2 - concentration,
        "planner_discovery": planner,
        "protocol_loss": planner - selected,
        "global_pure_equilibrium_count": pure_count,
        "global_pure_equilibria": global_pure,
        "worst_pure_discovery": min(discoveries),
        "best_pure_discovery": max(discoveries),
        "pure_discovery_values": tuple(sorted(set(discoveries))),
    }


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    config_hash = hashlib.sha256(canonical_config).hexdigest()
    commit = _git(root, "rev-parse", "HEAD")
    dirty = bool(_git(root, "status", "--porcelain"))
    started = datetime.now(UTC)
    start = time.monotonic()
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-002_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"))

    likelihood: Likelihood = tuple(
        tuple(Fraction(value) for value in row) for row in config["likelihood"]
    )
    row_normalization = all(sum(row, start=Fraction(0)) == 1 for row in likelihood)
    partitions = canonical_partitions(int(config["evidence_states"]))
    if len(partitions) > int(config["partition_limit"]):
        raise RuntimeError("partition count exceeds configured pre-run limit")
    registry = [
        {
            "partition_id": f"P{index:02d}",
            "canonical_key": _partition_key(partition),
            "blocks": partition,
            "message_count": len(partition),
        }
        for index, partition in enumerate(partitions)
    ]
    _write_json(outputs / "partition-registry.json", registry)

    evaluations = [
        _evaluate_partition(
            f"P{index:02d}",
            partition,
            likelihood,
            int(config["global_pure_equilibrium_limit_per_partition"]),
        )
        for index, partition in enumerate(partitions)
    ]
    by_key = {_partition_key(item["partition"]): item for item in evaluations}
    _write_json(outputs / "equilibrium-registry.json", evaluations)

    summary_rows = [
        {
            "partition_id": item["partition_id"],
            "partition": _partition_key(item["partition"]),
            "message_count": len(item["partition"]),
            "selected_discovery": str(item["selected_discovery"]),
            "worst_pure_discovery": str(item["worst_pure_discovery"]),
            "best_pure_discovery": str(item["best_pure_discovery"]),
            "planner_discovery": str(item["planner_discovery"]),
            "selected_action_hhi": str(item["selected_action_hhi"]),
            "pure_equilibrium_count": item["global_pure_equilibrium_count"],
        }
        for item in evaluations
    ]
    with (outputs / "partition-summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)

    comparisons = []
    planner_monotone = True
    for fine, coarse in itertools.permutations(evaluations, 2):
        if not refines(fine["partition"], coarse["partition"]):
            continue
        coarse_membership = {
            evidence: block_index
            for block_index, block in enumerate(coarse["partition"])
            for evidence in block
        }
        garbling = tuple(coarse_membership[block[0]] for block in fine["partition"])
        planner_relation = fine["planner_discovery"] >= coarse["planner_discovery"]
        planner_monotone &= planner_relation
        comparisons.append(
            {
                "more_informative": fine["partition_id"],
                "less_informative": coarse["partition_id"],
                "fine_partition": fine["partition"],
                "coarse_partition": coarse["partition"],
                "deterministic_garbling": garbling,
                "selected_difference": fine["selected_discovery"] - coarse["selected_discovery"],
                "worst_pure_difference": fine["worst_pure_discovery"]
                - coarse["worst_pure_discovery"],
                "best_pure_difference": fine["best_pure_discovery"] - coarse["best_pure_discovery"],
                "planner_difference": fine["planner_discovery"] - coarse["planner_discovery"],
                "planner_monotone": planner_relation,
            }
        )
    _write_json(outputs / "refinement-comparisons.json", comparisons)

    configured_fine = tuple(
        tuple(block) for block in config["comparison"]["more_informative_partition"]
    )
    configured_coarse = tuple(
        tuple(block) for block in config["comparison"]["less_informative_partition"]
    )
    fine = by_key[_partition_key(configured_fine)]
    coarse = by_key[_partition_key(configured_coarse)]
    witness = {
        "more_informative_partition_id": fine["partition_id"],
        "less_informative_partition_id": coarse["partition_id"],
        "more_informative_partition": configured_fine,
        "less_informative_partition": configured_coarse,
        "deterministic_garbling": [0, 0],
        "selected_more": fine["selected_discovery"],
        "selected_less": coarse["selected_discovery"],
        "selected_difference": fine["selected_discovery"] - coarse["selected_discovery"],
        "pure_more_values": fine["pure_discovery_values"],
        "pure_less_values": coarse["pure_discovery_values"],
        "planner_more": fine["planner_discovery"],
        "planner_less": coarse["planner_discovery"],
        "selection_dependent_reversal": (
            fine["selected_discovery"] < coarse["selected_discovery"]
            and fine["worst_pure_discovery"] > coarse["best_pure_discovery"]
        ),
        "messages_more": fine["messages"],
        "messages_less": coarse["messages"],
    }
    _write_json(outputs / "selection-reversal-witness.json", witness)

    all_symmetric_checks = all(
        message["anonymous_symmetric_equilibrium"]["best_response_verified"]
        and message["anonymous_symmetric_equilibrium"]["discovery"]
        == message["anonymous_symmetric_equilibrium"]["direct_state_discovery"]
        for item in evaluations
        for message in item["messages"]
    )
    expected = config["comparison"]
    witness_expected = (
        fine["selected_discovery"] == Fraction(expected["expected_more_selected_discovery"])
        and coarse["selected_discovery"] == Fraction(expected["expected_less_selected_discovery"])
        and fine["worst_pure_discovery"] == Fraction(expected["expected_more_pure_discovery"])
        and coarse["worst_pure_discovery"] == Fraction(expected["expected_less_pure_discovery"])
    )
    elapsed = time.monotonic() - start
    validation = {
        "passed": bool(
            not dirty
            and row_normalization
            and len(partitions) == 15
            and len({_partition_key(partition) for partition in partitions}) == 15
            and all_symmetric_checks
            and planner_monotone
            and witness["selection_dependent_reversal"]
            and witness_expected
            and not config["randomized_disclosure_implemented"]
            and elapsed <= float(config["time_budget_seconds"])
        ),
        "git_clean_at_start": not dirty,
        "likelihood_rows_normalized": row_normalization,
        "all_15_partitions_enumerated": len(partitions) == 15,
        "message_label_equivalence_quotiented": len(
            {_partition_key(partition) for partition in partitions}
        )
        == 15,
        "full_pure_correspondence_stored": all(
            len(item["global_pure_equilibria"]) == item["global_pure_equilibrium_count"]
            for item in evaluations
        ),
        "anonymous_symmetric_equilibria_independently_checked": all_symmetric_checks,
        "all_refinement_planner_values_monotone": planner_monotone,
        "selection_dependent_reversal_verified": witness["selection_dependent_reversal"],
        "configured_exact_values_reproduced": witness_expected,
        "randomized_disclosure_implemented": False,
        "elapsed_seconds": elapsed,
        "time_budget_seconds": config["time_budget_seconds"],
    }
    _write_json(run_dir / "validation.json", validation)
    _write_json(
        run_dir / "metrics.json",
        {
            "partition_count": len(partitions),
            "strict_refinement_pair_count": len(comparisons),
            "posterior_game_count": sum(len(item["messages"]) for item in evaluations),
            "global_pure_equilibrium_count": sum(
                item["global_pure_equilibrium_count"] for item in evaluations
            ),
            "selected_reversal_count": sum(
                comparison["selected_difference"] < 0 for comparison in comparisons
            ),
            "worst_pure_reversal_count": sum(
                comparison["worst_pure_difference"] < 0 for comparison in comparisons
            ),
        },
    )
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\npartition_count={len(partitions)}\n"
        f"validation_status={'passed' if validation['passed'] else 'failed'}\n",
        encoding="utf-8",
    )
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    packages = subprocess.check_output(["uv", "pip", "freeze"], cwd=root, text=True).splitlines()
    _write_json(
        run_dir / "environment.json",
        {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "packages": sorted(
                line
                for line in packages
                if not line.lower().startswith("distributed-discovery @ file:")
            ),
        },
    )
    output_hashes = {
        str(path.relative_to(run_dir)): _sha(path)
        for path in sorted(outputs.iterdir())
        if path.is_file()
    }
    _write_json(run_dir / "output-checksums.json", output_hashes)
    ended = datetime.now(UTC)
    input_paths = [
        config_path,
        root / "src/distributed_discovery/information_design/game.py",
        root / "src/distributed_discovery/information_design/study.py",
    ]
    command = "make dd002-disclosure"
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-002",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": ended.isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": command,
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": {"algorithm": None, "model": None},
        "outputs": output_hashes,
    }
    _write_json(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd002-disclosure\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-002 bounded disclosure run {run_id}\n\n"
        "Complete deterministic-partition registry, exact pure/anonymous-symmetric "
        "equilibrium correspondence, refinement comparisons, and selection-dependent "
        "reversal witness. Randomized disclosure is not implemented.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
