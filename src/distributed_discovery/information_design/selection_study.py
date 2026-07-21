"""Run the immutable DD-002 equilibrium-selection robustness census."""

from __future__ import annotations

import copy
import csv
import hashlib
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

from distributed_discovery.information_design.game import Likelihood, Partition
from distributed_discovery.information_design.selection import (
    RULES,
    PartitionSelection,
    evaluate_catalogue,
    refinement_comparisons,
    selection_certificate,
)
from distributed_discovery.information_design.selection_verification import (
    verify_selection_certificate,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-002-information-design/configs/selection-robustness.yml")


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


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(_jsonable(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _checked_artifact(root: Path, run_id: str, relative: str) -> Path:
    run = root / "results/verified" / run_id
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    expected = manifest.get("outputs", {}).get(relative)
    path = run / relative
    if (
        manifest.get("run_id") != run_id
        or manifest.get("validation_status") != "passed"
        or manifest.get("exit_status") != 0
        or not isinstance(expected, str)
        or not path.is_file()
        or _sha(path) != expected
    ):
        raise RuntimeError(f"invalid frozen-game artifact: {run_id}/{relative}")
    return path


def _partition_key(partition: Partition) -> str:
    return "|".join(",".join(str(state) for state in block) for block in partition)


def _write_summary(path: Path, catalogue: tuple[PartitionSelection, ...]) -> None:
    rows = [
        {
            "partition_id": item.partition_id,
            "partition": _partition_key(item.partition),
            **{rule: str(item.values[rule]) for rule in RULES},
            "potential_tied_profile_count": item.potential_tied_profile_count,
            "potential_multiple_discovery_values": item.potential_multiple_discovery_values,
            "basin_branch_dependent": item.basin_branch_dependent,
        }
        for item in catalogue
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _frozen_regression(
    catalogue: tuple[PartitionSelection, ...], summary_path: Path, registry_path: Path
) -> dict[str, Any]:
    previous_rows = {
        row["partition_id"]: row for row in csv.DictReader(summary_path.open(encoding="utf-8"))
    }
    row_matches = []
    for item in catalogue:
        previous = previous_rows[item.partition_id]
        row_matches.append(
            previous["partition"] == _partition_key(item.partition)
            and Fraction(previous["selected_discovery"]) == item.values["anonymous_symmetric"]
            and Fraction(previous["worst_pure_discovery"]) == item.values["worst_pure"]
            and Fraction(previous["best_pure_discovery"]) == item.values["best_pure"]
            and Fraction(previous["planner_discovery"]) == item.values["planner"]
        )
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    return {
        "partition_rows_match": all(row_matches) and len(previous_rows) == len(catalogue),
        "partition_count": len(registry),
        "posterior_game_count": sum(len(item["messages"]) for item in registry),
        "global_pure_equilibrium_count": sum(
            int(item["global_pure_equilibrium_count"]) for item in registry
        ),
    }


def _known_witness(
    catalogue: tuple[PartitionSelection, ...], config: dict[str, Any]
) -> dict[str, Any]:
    less_partition: Partition = tuple(
        tuple(block) for block in config["known_witness"]["less_informative_partition"]
    )
    more_partition: Partition = tuple(
        tuple(block) for block in config["known_witness"]["more_informative_partition"]
    )
    less = next(item for item in catalogue if item.partition == less_partition)
    more = next(item for item in catalogue if item.partition == more_partition)
    return {
        "less_informative": less.partition_id,
        "more_informative": more.partition_id,
        "rules": {
            rule: {
                "less_discovery": less.values[rule],
                "more_discovery": more.values[rule],
                "difference": more.values[rule] - less.values[rule],
                "reversal": more.values[rule] < less.values[rule],
            }
            for rule in RULES
        },
        "selection_robustness_conclusion": (
            "the known reversal occurs only under the anonymous-symmetric selection; "
            "best pure, worst pure, uniform potential maximum, uniform strict-best-response "
            "basin, and planner values all improve"
        ),
    }


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config_hash = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    commit = _git(root, "rev-parse", "HEAD")
    dirty = bool(_git(root, "status", "--porcelain"))
    started = datetime.now(UTC)
    start = time.monotonic()
    deadline = start + float(config["time_budget_seconds"])
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-002_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"))

    source_run = str(config["source_run"])
    prior_summary = _checked_artifact(root, source_run, "outputs/partition-summary.csv")
    prior_registry = _checked_artifact(root, source_run, "outputs/equilibrium-registry.json")
    prior_comparisons = _checked_artifact(root, source_run, "outputs/refinement-comparisons.json")
    prior_witness = _checked_artifact(root, source_run, "outputs/selection-reversal-witness.json")
    likelihood: Likelihood = tuple(
        tuple(Fraction(value) for value in row) for row in config["likelihood"]
    )

    catalogue = evaluate_catalogue(likelihood)
    if time.monotonic() > deadline:
        raise RuntimeError("selection catalogue exceeded the declared time budget")
    comparisons = refinement_comparisons(catalogue)
    certificate = selection_certificate(likelihood, catalogue, comparisons)
    certificate["claim_ids"] = ["DD-C-0039", "DD-C-0040", "DD-C-0041"]
    _json(outputs / "selection-certificate.json", certificate)
    _write_summary(outputs / "partition-selection-summary.csv", catalogue)
    _json(outputs / "selection-refinement-comparisons.json", comparisons)
    witness = _known_witness(catalogue, config)
    _json(outputs / "known-witness-robustness.json", witness)
    _json(
        outputs / "selection-catalogue.json",
        {
            "schema_version": 1,
            "rules": {
                "anonymous_symmetric": "existing exact anonymous symmetric Nash selection",
                "best_pure": "maximum discovery over the full pure Nash correspondence",
                "worst_pure": "minimum discovery over the full pure Nash correspondence",
                "uniform_potential_maximum": (
                    "uniform over every labeled global maximizer of the exact Rosenthal potential"
                ),
                "uniform_strict_best_response_basin": (
                    "uniform initial pure profile and uniform strict payoff-maximizing "
                    "player-action move"
                ),
                "planner": "top-two posterior mass comparator",
            },
            "randomized_disclosure_implemented": False,
        },
    )

    verification_errors = verify_selection_certificate(certificate)
    corrupted = copy.deepcopy(certificate)
    corrupted["partitions"][0]["messages"][0]["absorption_by_initial"][0]["absorption"][0][
        "probability"
    ] = "0"
    corruption_errors = verify_selection_certificate(corrupted)
    _json(
        outputs / "independent-verification.json",
        {
            "schema_version": 1,
            "method": (
                "direct posterior/game reconstruction, exact-potential deviation identities, "
                "and absorption Bellman equations; no primary selection import"
            ),
            "certificate_errors": verification_errors,
            "corruption_test": {
                "mutation": "replace one initial-state absorption probability with zero",
                "rejected": bool(corruption_errors),
                "errors": corruption_errors,
            },
        },
    )

    frozen = _frozen_regression(catalogue, prior_summary, prior_registry)
    prior_comparison_count = len(json.loads(prior_comparisons.read_text(encoding="utf-8")))
    prior_witness_record = json.loads(prior_witness.read_text(encoding="utf-8"))
    known_rules = witness["rules"]
    non_symmetric_rules = (
        "best_pure",
        "worst_pure",
        "uniform_potential_maximum",
        "uniform_strict_best_response_basin",
        "planner",
    )
    counts = certificate["refinement_counts"]
    potential_basin_equal = all(
        item.values["uniform_potential_maximum"]
        == item.values["uniform_strict_best_response_basin"]
        for item in catalogue
    )
    certificate_bytes = (outputs / "selection-certificate.json").stat().st_size
    elapsed = time.monotonic() - start
    cost = {
        "schema_version": 1,
        "bounded_before_execution": True,
        "declared_time_budget_seconds": config["time_budget_seconds"],
        "declared_memory_budget_mb": config["memory_budget_mb"],
        "partition_count": len(catalogue),
        "posterior_game_count": sum(len(item.messages) for item in catalogue),
        "action_profile_state_count": sum(9 * len(item.messages) for item in catalogue),
        "unilateral_deviation_checks": sum(54 * len(item.messages) for item in catalogue),
        "absorption_bellman_state_count": sum(9 * len(item.messages) for item in catalogue),
        "refinement_rule_comparison_count": len(comparisons) * len(RULES),
        "certificate_bytes": certificate_bytes,
        "elapsed_seconds": elapsed,
        "checkpoint_strategy": (
            "atomic immutable run outputs; the finite state space is below the resume threshold"
        ),
        "interruption_outcome": "no substantive claim; preserve a failed run if manifested",
        "randomness": None,
    }
    _json(outputs / "cost-audit.json", cost)

    passed = bool(
        not dirty
        and frozen["partition_rows_match"]
        and frozen["partition_count"] == int(config["partition_limit"])
        and frozen["posterior_game_count"] == int(config["posterior_game_limit"])
        and frozen["global_pure_equilibrium_count"] == 256
        and len(comparisons) == int(config["refinement_pair_limit"]) == prior_comparison_count
        and not verification_errors
        and bool(corruption_errors)
        and known_rules["anonymous_symmetric"]["less_discovery"]
        == Fraction(prior_witness_record["selected_less"])
        and known_rules["anonymous_symmetric"]["more_discovery"]
        == Fraction(prior_witness_record["selected_more"])
        and known_rules["anonymous_symmetric"]["reversal"]
        and all(known_rules[rule]["difference"] > 0 for rule in non_symmetric_rules)
        and counts["planner"]["harmful"] == 0
        and elapsed <= float(config["time_budget_seconds"])
        and certificate_bytes < int(config["memory_budget_mb"]) * 1024 * 1024
        and not config["randomized_disclosure_implemented"]
    )
    validation = {
        "passed": passed,
        "git_clean_at_start": not dirty,
        "frozen_game_partition_values_match": frozen["partition_rows_match"],
        "all_15_partitions_enumerated": len(catalogue) == 15,
        "all_37_posterior_games_evaluated": sum(len(item.messages) for item in catalogue) == 37,
        "all_256_global_pure_selections_preserved": (
            frozen["global_pure_equilibrium_count"] == 256
        ),
        "all_45_refinements_compared": len(comparisons) == 45,
        "independent_certificate_verifier_passed": not verification_errors,
        "corruption_test_rejected_modified_absorption": bool(corruption_errors),
        "known_witness_anonymous_symmetric_reversal_reproduced": (
            known_rules["anonymous_symmetric"]["reversal"]
        ),
        "known_witness_all_other_declared_rules_improve": all(
            known_rules[rule]["difference"] > 0 for rule in non_symmetric_rules
        ),
        "potential_and_basin_values_equal_all_partitions": potential_basin_equal,
        "planner_monotone_all_refinements": counts["planner"]["harmful"] == 0,
        "randomized_disclosure_implemented": False,
        "elapsed_seconds": elapsed,
        "time_budget_seconds": config["time_budget_seconds"],
        "certificate_bytes": certificate_bytes,
        "memory_budget_mb": config["memory_budget_mb"],
    }
    _json(run_dir / "validation.json", validation)
    _json(
        run_dir / "metrics.json",
        {
            "partition_count": len(catalogue),
            "posterior_game_count": sum(len(item.messages) for item in catalogue),
            "strict_refinement_pair_count": len(comparisons),
            "known_witness": witness["rules"],
            "refinement_counts": counts,
            "potential_and_basin_values_equal_all_partitions": potential_basin_equal,
            "partitions_with_potential_discovery_ties": sum(
                item.potential_multiple_discovery_values for item in catalogue
            ),
            "partitions_with_basin_branch_dependence": sum(
                item.basin_branch_dependent for item in catalogue
            ),
        },
    )
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\n"
        f"partition_count={len(catalogue)}\n"
        f"refinement_count={len(comparisons)}\n"
        f"validation_status={'passed' if passed else 'failed'}\n",
        encoding="utf-8",
    )
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    packages = subprocess.check_output(["uv", "pip", "freeze"], cwd=root, text=True).splitlines()
    _json(
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
    _json(run_dir / "output-checksums.json", output_hashes)
    ended = datetime.now(UTC)
    input_paths = [
        config_path,
        prior_summary,
        prior_registry,
        prior_comparisons,
        prior_witness,
        root / "docs/decisions/ADR-0010-dd002-selection-catalogue.md",
        root / "src/distributed_discovery/information_design/game.py",
        root / "src/distributed_discovery/information_design/selection.py",
        root / "src/distributed_discovery/information_design/selection_verification.py",
        root / "src/distributed_discovery/information_design/selection_study.py",
    ]
    command = "make dd002-selection-robustness"
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-002",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": ended.isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if passed else 1,
        "validation_status": "passed" if passed else "failed",
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
    _json(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd002-selection-robustness\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-002 selection-robustness run {run_id}\n\n"
        "Exact best/worst-pure, uniform-potential, and strict-best-response-basin "
        "catalogue for all frozen deterministic disclosures and refinements, with "
        "independently checked absorption certificates.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
