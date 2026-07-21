"""Run the immutable DD-003 heterogeneous colored-source census."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import os
import platform
import subprocess
import time
from collections import defaultdict
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.source_networks.heterogeneous import (
    ColoredNetwork,
    accuracies,
    adjacency,
    colored_label,
    complete_moment_signature,
    enumerate_colored_networks,
    exact_colored_metrics,
    independent_colored_orbit_count,
    labeled_colored_networks,
    pairwise_agreement_signature,
)
from distributed_discovery.source_networks.heterogeneous_verification import (
    verify_colored_registry,
    verify_pairwise_counterexample,
)
from distributed_discovery.source_networks.model import graph_label
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-003-source-networks/configs/heterogeneous-source-accuracy.yml")


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
        raise RuntimeError(f"invalid homogeneous source artifact: {run_id}/{relative}")
    return path


def _specs(config: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for profile, raw_levels in config["accuracy_profiles"].items():
        levels = tuple(Fraction(value) for value in raw_levels)
        for sources in config["source_counts"]:
            source_count = int(sources)
            if len(levels) <= source_count:
                result.append(
                    {
                        "key": f"base:{profile}:K{source_count}",
                        "scope": "base",
                        "profile": profile,
                        "sources": source_count,
                        "levels": levels,
                    }
                )
    expansion = config["controlled_expansion"]
    result.append(
        {
            "key": f"expansion:{expansion['name']}:K{expansion['source_count']}",
            "scope": "controlled-expansion",
            "profile": expansion["name"],
            "sources": int(expansion["source_count"]),
            "levels": tuple(Fraction(value) for value in expansion["accuracies"]),
        }
    )
    return result


def _entry(network: ColoredNetwork, spec: dict[str, Any], index: int) -> dict[str, Any]:
    signature = complete_moment_signature(network)
    agreement = pairwise_agreement_signature(network)
    return {
        "network_id": f"C{index:03d}",
        "spec_key": spec["key"],
        "scope": spec["scope"],
        "profile": spec["profile"],
        "canonical_label": colored_label(network),
        "accuracies": accuracies(network),
        "adjacency": adjacency(network),
        **exact_colored_metrics(network),
        "first_action_moments": signature[:12],
        "pairwise_second_action_moments": tuple(
            signature[offset : offset + 9] for offset in range(12, len(signature), 9)
        ),
        "complete_moment_signature": signature,
        "pairwise_agreement_signature": agreement,
    }


def _matched_groups(registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Fraction, ...], list[dict[str, Any]]] = defaultdict(list)
    for entry in registry:
        groups[tuple(entry["complete_moment_signature"])].append(entry)
    return [
        {
            "group_id": f"M{index:03d}",
            "network_ids": [entry["network_id"] for entry in group],
            "canonical_labels": [entry["canonical_label"] for entry in group],
            "profiles": [entry["profile"] for entry in group],
            "scopes": [entry["scope"] for entry in group],
            "complete_moment_signature": signature,
            "private_discovery_values": sorted({entry["private_discovery"] for entry in group}),
            "different_private_discovery": (
                len({entry["private_discovery"] for entry in group}) > 1
            ),
        }
        for index, (signature, group) in enumerate(sorted(groups.items(), key=lambda item: item[0]))
        if len(group) > 1
    ]


def _counterexample(registry: list[dict[str, Any]]) -> dict[str, Any]:
    left_label = "K2N4:1-2@0001;2-3@1111"
    right_label = "K2N4:1-2@1111;2-3@0001"
    left = next(entry for entry in registry if entry["canonical_label"] == left_label)
    right = next(entry for entry in registry if entry["canonical_label"] == right_label)
    return {
        "left": {
            "network_id": left["network_id"],
            "canonical_label": left["canonical_label"],
            "accuracies": left["accuracies"],
            "adjacency": left["adjacency"],
        },
        "right": {
            "network_id": right["network_id"],
            "canonical_label": right["canonical_label"],
            "accuracies": right["accuracies"],
            "adjacency": right["adjacency"],
        },
        "profile": "modest",
        "complete_first_and_pairwise_moments_equal": (
            left["complete_moment_signature"] == right["complete_moment_signature"]
        ),
        "complete_moment_signature": left["complete_moment_signature"],
        "pairwise_agreement_signature": left["pairwise_agreement_signature"],
        "left_private_discovery": left["private_discovery"],
        "right_private_discovery": right["private_discovery"],
        "private_discovery_difference": (left["private_discovery"] - right["private_discovery"]),
        "interpretation": (
            "swapping which accuracy color occupies the degree-four source preserves every "
            "first and pairwise scalar-report moment but changes four-searcher union discovery"
        ),
    }


def _diagnostic_summary(registry: list[dict[str, Any]], fields: tuple[str, ...]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for field in fields:
        groups: dict[Fraction, list[dict[str, Any]]] = defaultdict(list)
        for entry in registry:
            groups[entry[field]].append(entry)
        matched = [group for group in groups.values() if len(group) > 1]
        differing = [
            group for group in matched if len({entry["private_discovery"] for entry in group}) > 1
        ]
        summary[field] = {
            "matched_value_group_count": len(matched),
            "matched_groups_with_different_private_discovery": len(differing),
            "different_private_discovery_pair_count": sum(
                left["private_discovery"] != right["private_discovery"]
                for group in differing
                for index, left in enumerate(group)
                for right in group[index + 1 :]
            ),
        }
    return summary


def _homogeneous_regression(
    registry: list[dict[str, Any]], old_registry_path: Path
) -> dict[str, Any]:
    old = json.loads(old_registry_path.read_text(encoding="utf-8"))
    old_by_label = {
        entry["canonical_label"]: entry for entry in old if int(entry["sources"]) in (2, 3)
    }
    current = [entry for entry in registry if entry["profile"] == "equal-baseline"]
    checks = [
        graph_label(tuple(tuple(row) for row in entry["adjacency"])) in old_by_label
        and entry["private_discovery"]
        == Fraction(
            old_by_label[graph_label(tuple(tuple(row) for row in entry["adjacency"]))][
                "private_discovery"
            ]
        )
        and tuple(entry["pairwise_agreement_signature"])
        == tuple(
            Fraction(value)
            for value in old_by_label[graph_label(tuple(tuple(row) for row in entry["adjacency"]))][
                "pairwise_signature"
            ]
        )
        for entry in current
    ]
    return {
        "expected_network_count": 50,
        "network_count": len(current),
        "all_private_discovery_and_agreement_signatures_match": all(checks),
    }


def _write_csv(path: Path, registry: list[dict[str, Any]]) -> None:
    fields = [
        "network_id",
        "spec_key",
        "scope",
        "profile",
        "canonical_label",
        "sources",
        "edges",
        "mean_source_accuracy",
        "exposure_weighted_accuracy",
        "source_hhi",
        "mean_pair_source_overlap",
        "mean_pair_agreement",
        "private_discovery",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: str(entry[field]) for field in fields} for entry in registry)


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
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-003_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"))

    source_run = str(config["source_run"])
    old_registry = _checked_artifact(root, source_run, "outputs/graph-registry.json")
    specs = _specs(config)
    registry: list[dict[str, Any]] = []
    census: list[dict[str, Any]] = []
    for spec in specs:
        levels = tuple(spec["levels"])
        sources = int(spec["sources"])
        labeled_count = len(labeled_colored_networks(levels, sources, int(config["searchers"])))
        networks = enumerate_colored_networks(levels, sources, int(config["searchers"]))
        independent_count = independent_colored_orbit_count(
            levels, sources, int(config["searchers"])
        )
        census.append(
            {
                **spec,
                "labeled_colored_object_count": labeled_count,
                "canonical_orbit_count": len(networks),
                "independent_orbit_count": independent_count,
            }
        )
        for network in networks:
            registry.append(_entry(network, spec, len(registry)))
        if time.monotonic() > deadline:
            raise RuntimeError("colored-source census exceeded the declared time budget")

    matched = _matched_groups(registry)
    witness = _counterexample(registry)
    diagnostics = _diagnostic_summary(
        registry,
        (
            "mean_pair_agreement",
            "source_hhi",
            "mean_pair_source_overlap",
            "mean_source_accuracy",
            "exposure_weighted_accuracy",
        ),
    )
    homogeneous = _homogeneous_regression(registry, old_registry)
    _json(outputs / "colored-network-registry.json", registry)
    _json(outputs / "complete-moment-matched-groups.json", matched)
    _json(outputs / "pairwise-moment-counterexample.json", witness)
    _json(outputs / "scalar-diagnostic-summary.json", diagnostics)
    _write_csv(outputs / "colored-network-summary.csv", registry)

    verification = verify_colored_registry(registry, specs, witness)
    corrupted = copy.deepcopy(witness)
    corrupted["private_discovery_difference"] = "0"
    corruption_rejected = not verify_pairwise_counterexample(corrupted)
    verification_output = {
        "schema_version": 1,
        "method": (
            "independent labeled colored-object traversal, direct color-preserving "
            "isomorphism, target/signal/action enumeration, and full moment reconstruction; "
            "no primary heterogeneous-model import"
        ),
        **verification,
        "corruption_test": {
            "mutation": "replace the counterexample discovery difference by zero",
            "rejected": corruption_rejected,
        },
    }
    _json(outputs / "independent-verification.json", verification_output)

    base_census = [entry for entry in census if entry["scope"] == "base"]
    expansion_census = [entry for entry in census if entry["scope"] == "controlled-expansion"]
    differing_matches = [entry for entry in matched if entry["different_private_discovery"]]
    certificate = {
        "schema_version": 1,
        "method": "exact color-preserving enumeration with Fraction probabilities",
        "claim_ids": [],
        "census": census,
        "base_labeled_colored_object_count": sum(
            entry["labeled_colored_object_count"] for entry in base_census
        ),
        "base_orbit_count": sum(entry["canonical_orbit_count"] for entry in base_census),
        "expansion_labeled_colored_object_count": sum(
            entry["labeled_colored_object_count"] for entry in expansion_census
        ),
        "expansion_orbit_count": sum(entry["canonical_orbit_count"] for entry in expansion_census),
        "total_orbit_count": len(registry),
        "matched_complete_moment_group_count": len(matched),
        "networks_in_matched_complete_moment_groups": sum(
            len(entry["network_ids"]) for entry in matched
        ),
        "matched_groups_with_different_private_discovery": len(differing_matches),
        "homogeneous_regression": homogeneous,
        "controlled_expansion_count": 1,
        "bounded_conclusion": (
            "complete first and pairwise scalar-report moments are insufficient for private "
            "discovery in the registered heterogeneous colored-source class"
        ),
    }
    _json(outputs / "colored-census-certificate.json", certificate)

    elapsed = time.monotonic() - start
    total_output_bytes = sum(path.stat().st_size for path in outputs.iterdir() if path.is_file())
    cost = {
        "schema_version": 1,
        "bounded_before_execution": True,
        "declared_time_budget_seconds": config["time_budget_seconds"],
        "declared_memory_budget_mb": config["memory_budget_mb"],
        "labeled_colored_object_count": sum(
            entry["labeled_colored_object_count"] for entry in census
        ),
        "canonical_orbit_count": len(registry),
        "maximum_target_signal_states_per_orbit": 81,
        "maximum_primary_probability_state_count": len(registry) * 81,
        "independent_registry_entry_checks": verification["stored_entry_checks"],
        "output_bytes_before_manifest": total_output_bytes,
        "elapsed_seconds": elapsed,
        "checkpoint_strategy": (
            "atomic immutable outputs; the audited finite census is below the resume threshold"
        ),
        "interruption_outcome": "no substantive claim; preserve a failed run if manifested",
        "randomness": None,
    }
    _json(outputs / "cost-audit.json", cost)

    expected = config["expected_state_size"]
    passed = bool(
        not dirty
        and certificate["base_labeled_colored_object_count"]
        == int(expected["base_labeled_colored_objects"])
        and certificate["base_orbit_count"] == int(expected["base_orbits"])
        and certificate["expansion_labeled_colored_object_count"]
        == int(expected["expansion_labeled_colored_objects"])
        and certificate["expansion_orbit_count"] == int(expected["expansion_orbits"])
        and certificate["total_orbit_count"] == int(expected["total_orbits"])
        and all(
            entry["canonical_orbit_count"] == entry["independent_orbit_count"] for entry in census
        )
        and homogeneous["network_count"] == homogeneous["expected_network_count"]
        and homogeneous["all_private_discovery_and_agreement_signatures_match"]
        and witness["complete_first_and_pairwise_moments_equal"]
        and witness["left_private_discovery"] == Fraction(3, 4)
        and witness["right_private_discovery"] == Fraction(2, 3)
        and witness["private_discovery_difference"] == Fraction(1, 12)
        and len(differing_matches) > 0
        and verification["passed"]
        and corruption_rejected
        and all(
            value == Fraction(1, 3) for entry in registry for value in entry["first_action_moments"]
        )
        and elapsed <= float(config["time_budget_seconds"])
        and total_output_bytes < int(config["memory_budget_mb"]) * 1024 * 1024
    )
    validation = {
        "passed": passed,
        "git_clean_at_start": not dirty,
        "state_size_matches_registered_audit": (
            certificate["base_labeled_colored_object_count"]
            == int(expected["base_labeled_colored_objects"])
            and certificate["base_orbit_count"] == int(expected["base_orbits"])
            and certificate["expansion_labeled_colored_object_count"]
            == int(expected["expansion_labeled_colored_objects"])
            and certificate["expansion_orbit_count"] == int(expected["expansion_orbits"])
        ),
        "primary_and_independent_orbit_counts_match": all(
            entry["canonical_orbit_count"] == entry["independent_orbit_count"] for entry in census
        ),
        "homogeneous_fixture_reproduced": homogeneous[
            "all_private_discovery_and_agreement_signatures_match"
        ],
        "all_first_action_moments_equal_one_third": all(
            value == Fraction(1, 3) for entry in registry for value in entry["first_action_moments"]
        ),
        "full_pairwise_moment_counterexample_verified": (
            witness["complete_first_and_pairwise_moments_equal"]
            and witness["private_discovery_difference"] == Fraction(1, 12)
        ),
        "independent_verifier_passed": verification["passed"],
        "corruption_test_rejected_modified_difference": corruption_rejected,
        "controlled_expansion_count": 1,
        "elapsed_seconds": elapsed,
        "time_budget_seconds": config["time_budget_seconds"],
        "output_bytes": total_output_bytes,
        "memory_budget_mb": config["memory_budget_mb"],
    }
    _json(run_dir / "validation.json", validation)
    _json(
        run_dir / "metrics.json",
        {
            "base_labeled_colored_object_count": certificate["base_labeled_colored_object_count"],
            "base_orbit_count": certificate["base_orbit_count"],
            "expansion_orbit_count": certificate["expansion_orbit_count"],
            "total_orbit_count": len(registry),
            "matched_complete_moment_group_count": len(matched),
            "networks_in_matched_complete_moment_groups": sum(
                len(entry["network_ids"]) for entry in matched
            ),
            "matched_groups_with_different_private_discovery": len(differing_matches),
            "primary_counterexample": {
                "left_private_discovery": witness["left_private_discovery"],
                "right_private_discovery": witness["right_private_discovery"],
                "difference": witness["private_discovery_difference"],
            },
            "diagnostic_summary": diagnostics,
        },
    )
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\n"
        f"colored_orbit_count={len(registry)}\n"
        f"different_moment_match_count={len(differing_matches)}\n"
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
        old_registry,
        root / "docs/decisions/ADR-0011-dd003-colored-source-census.md",
        root / "src/distributed_discovery/source_networks/model.py",
        root / "src/distributed_discovery/source_networks/heterogeneous.py",
        root / "src/distributed_discovery/source_networks/heterogeneous_verification.py",
        root / "src/distributed_discovery/source_networks/heterogeneous_study.py",
    ]
    command = "make dd003-heterogeneous-sources"
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-003",
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
        "#!/bin/sh\nset -eu\nexec make dd003-heterogeneous-sources\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-003 heterogeneous-source run {run_id}\n\n"
        "Exact color-preserving source-network census, complete first/pairwise action moments, "
        "private discovery, scalar diagnostics, and independently verified counterexample.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
