"""Run the registered exact DD-013 audience-design census."""

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

from distributed_discovery.attention.model import discovery
from distributed_discovery.audience.model import (
    binding_metrics,
    binding_optima,
    institution_registry,
    mechanism_results,
    voluntary_equilibria,
    voluntary_equilibrium,
)
from distributed_discovery.audience.verification import corruption_tests, verify_bundle
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-013-audience-design/configs/frontier.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _binding_rows(n: int, p: Fraction, q: Fraction) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for audience in range(n + 1):
        metrics = binding_metrics(n, audience, p, q)
        rows.append(
            {
                "audience": audience,
                "discovery": str(metrics["discovery"]),
                "action_quality": str(metrics["action_quality"]),
                "expected_distinct_actions": str(metrics["expected_distinct_actions"]),
                "information_access_count": metrics["information_access_count"],
                "effective_action_channels": metrics["effective_action_channels"],
            }
        )
    return rows


def _voluntary_rows(n: int, p: Fraction, q: Fraction) -> list[dict[str, Any]]:
    audiences: list[dict[str, Any]] = []
    optimum = binding_optima(n, p, q)
    for audience in range(n + 1):
        equilibrium_counts = voluntary_equilibria(n, audience, p, q)
        profiles = []
        for readers in range(audience + 1):
            is_weak, is_strict = voluntary_equilibrium(n, audience, readers, p, q)
            profiles.append(
                {
                    "readers": readers,
                    "discovery": str(discovery(n, readers, p, q)),
                    "weak_equilibrium": is_weak,
                    "strict_equilibrium": is_strict,
                    "information_access_count": audience,
                    "effective_action_channels": n if readers == 0 else n - readers + 1,
                }
            )
        weak_counts = equilibrium_counts["weak"]
        audiences.append(
            {
                "audience": audience,
                "profiles": profiles,
                "weak_equilibria": weak_counts,
                "strict_equilibria": equilibrium_counts["strict"],
                "all_equilibria_socially_optimal": bool(weak_counts)
                and set(weak_counts) <= set(optimum),
                "has_excessive_use": any(count > max(optimum) for count in weak_counts),
                "has_insufficient_use": any(count < min(optimum) for count in weak_counts),
                "binding_use_implemented": weak_counts == [audience],
                "has_binding_implementation_gap": weak_counts != [audience],
                "has_welfare_multiplicity": len(
                    {discovery(n, count, p, q) for count in weak_counts}
                )
                > 1,
            }
        )
    return audiences


def _garbling_rows(n: int, p: Fraction, q: Fraction, accuracies: list[str]) -> list[dict[str, Any]]:
    optimum = max(discovery(n, audience, p, q) for audience in range(n + 1))
    rows: list[dict[str, Any]] = []
    for delivered_text in accuracies:
        delivered = Fraction(delivered_text)
        if delivered > q:
            continue
        for audience in range(1, n + 1):
            value = discovery(n, audience, p, delivered)
            rows.append(
                {
                    "original_accuracy": str(q),
                    "delivered_accuracy": str(delivered),
                    "audience": audience,
                    "discovery": str(value),
                    "weakly_dominated_by_binding_optimum": value <= optimum,
                    "strictly_dominated_by_binding_optimum": value < optimum,
                }
            )
    return rows


def _expected_optima(relation: str) -> list[int]:
    if relation == "shared-higher":
        return [1]
    if relation == "private-higher":
        return [0]
    return [0, 1]


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    accuracies = [str(value) for value in config["accuracies"]]
    cells: list[dict[str, Any]] = []
    for n in [int(value) for value in config["agents"]]:
        for private_text in accuracies:
            for shared_text in accuracies:
                p, q = Fraction(private_text), Fraction(shared_text)
                binding = _binding_rows(n, p, q)
                optimum = binding_optima(n, p, q)
                voluntary = _voluntary_rows(n, p, q)
                garbling = _garbling_rows(n, p, q, accuracies)
                cells.append(
                    {
                        "agents": n,
                        "private_accuracy": str(p),
                        "shared_accuracy": str(q),
                        "accuracy_relation": "shared-higher"
                        if q > p
                        else ("private-higher" if q < p else "equal"),
                        "binding_optima": optimum,
                        "binding_audiences": binding,
                        "voluntary_audiences": voluntary,
                        "garbling_rows": garbling,
                        "mechanisms": mechanism_results(n, p, q),
                    }
                )
    theorem_checks = {
        "binding_audience_classification": all(
            cell["binding_optima"] == _expected_optima(cell["accuracy_relation"]) for cell in cells
        ),
        "garbling_weakly_dominated": all(
            row["weakly_dominated_by_binding_optimum"]
            for cell in cells
            for row in cell["garbling_rows"]
        ),
        "garbling_equality_only_at_optimal_one_reader_design": all(
            row["strictly_dominated_by_binding_optimum"]
            or (
                row["audience"] == 1
                and row["delivered_accuracy"] == cell["shared_accuracy"]
                and cell["accuracy_relation"] != "private-higher"
            )
            for cell in cells
            for row in cell["garbling_rows"]
        ),
        "exclusive_recipient_voluntary_correspondence": all(
            cell["voluntary_audiences"][1]["weak_equilibria"] == cell["binding_optima"]
            for cell in cells
        ),
        "universal_pooling_implements_binding_optima": all(
            cell["mechanisms"]["public_universal_pooling"]["count_correspondence_matches_optimum"]
            for cell in cells
        ),
    }
    if not all(theorem_checks.values()):
        raise RuntimeError("DD-013 theorem-grid audit failed")
    voluntary_settings = [audience for cell in cells for audience in cell["voluntary_audiences"]]
    garbling_rows = [row for cell in cells for row in cell["garbling_rows"]]
    summary = {
        "grid_cells": len(cells),
        "binding_audience_rows": sum(len(cell["binding_audiences"]) for cell in cells),
        "voluntary_audience_settings": len(voluntary_settings),
        "voluntary_profile_rows": sum(len(row["profiles"]) for row in voluntary_settings),
        "garbling_rows": len(garbling_rows),
        "institution_count": len(institution_registry()),
        "full_broadcast_suboptimal_cells": sum(
            cell["agents"] not in cell["binding_optima"] for cell in cells
        ),
        "voluntary_settings_with_excessive_use": sum(
            row["has_excessive_use"] for row in voluntary_settings
        ),
        "voluntary_settings_with_insufficient_use": sum(
            row["has_insufficient_use"] for row in voluntary_settings
        ),
        "positive_audience_settings_with_insufficient_use": sum(
            row["has_insufficient_use"] and row["audience"] > 0 for row in voluntary_settings
        ),
        "voluntary_binding_implementation_gap_settings": sum(
            row["has_binding_implementation_gap"] for row in voluntary_settings
        ),
        "voluntary_settings_all_equilibria_socially_optimal": sum(
            row["all_equilibria_socially_optimal"] for row in voluntary_settings
        ),
        "voluntary_settings_with_welfare_multiplicity": sum(
            row["has_welfare_multiplicity"] for row in voluntary_settings
        ),
        "garbling_rows_equal_to_optimum": sum(
            not row["strictly_dominated_by_binding_optimum"] for row in garbling_rows
        ),
        "universal_pooling_implementation_cells": sum(
            cell["mechanisms"]["public_universal_pooling"]["count_correspondence_matches_optimum"]
            for cell in cells
        ),
    }
    return {
        "schema_version": "dd013-audience-frontier-v1",
        "cells": cells,
        "institution_registry": institution_registry(),
        "theorem_checks": theorem_checks,
        "summary": summary,
    }


def _write_frontier_csv(path: Path, cells: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        fields = (
            "agents",
            "private_accuracy",
            "shared_accuracy",
            "audience",
            "discovery",
            "action_quality",
            "expected_distinct_actions",
            "information_access_count",
            "effective_action_channels",
            "socially_optimal",
        )
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for cell in cells:
            for row in cell["binding_audiences"]:
                writer.writerow(
                    {
                        "agents": cell["agents"],
                        "private_accuracy": cell["private_accuracy"],
                        "shared_accuracy": cell["shared_accuracy"],
                        **row,
                        "socially_optimal": row["audience"] in cell["binding_optima"],
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
        raise RuntimeError("DD-013 primary run requires a clean committed implementation")
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-013_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    bundle = build_bundle(config)
    verification = verify_bundle(bundle)
    corruptions = corruption_tests(bundle)
    if not verification["passed"] or not all(corruptions.values()):
        raise RuntimeError("DD-013 independent verification failed")
    _write(outputs / "audience-frontier.json", bundle["cells"])
    _write_frontier_csv(outputs / "audience-frontier.csv", bundle["cells"])
    _write(
        outputs / "voluntary-audiences.json",
        [
            {
                "agents": cell["agents"],
                "private_accuracy": cell["private_accuracy"],
                "shared_accuracy": cell["shared_accuracy"],
                "binding_optima": cell["binding_optima"],
                "voluntary_audiences": cell["voluntary_audiences"],
            }
            for cell in bundle["cells"]
        ],
    )
    _write(
        outputs / "garbling-frontier.json",
        [
            {
                "agents": cell["agents"],
                "private_accuracy": cell["private_accuracy"],
                "shared_accuracy": cell["shared_accuracy"],
                "binding_optima": cell["binding_optima"],
                "rows": cell["garbling_rows"],
            }
            for cell in bundle["cells"]
        ],
    )
    _write(
        outputs / "mechanism-results.json",
        [
            {
                "agents": cell["agents"],
                "private_accuracy": cell["private_accuracy"],
                "shared_accuracy": cell["shared_accuracy"],
                "binding_optima": cell["binding_optima"],
                "mechanisms": cell["mechanisms"],
            }
            for cell in bundle["cells"]
        ],
    )
    _write(outputs / "institution-registry.json", bundle["institution_registry"])
    _write(outputs / "theorem-checks.json", bundle["theorem_checks"])
    _write(outputs / "summary.json", bundle["summary"])
    _write(outputs / "verification.json", verification)
    _write(outputs / "corruption-tests.json", corruptions)
    _write(run / "validation.json", {"passed": True, **bundle["summary"], **verification})
    (run / "stdout.txt").write_text(
        f"{run_id}\nexact audience frontier and independent verification passed\n",
        encoding="utf-8",
    )
    (run / "stderr.txt").write_text("", encoding="utf-8")
    inputs = [
        config_path,
        root / "src/distributed_discovery/attention/model.py",
        root / "src/distributed_discovery/audience/model.py",
        root / "src/distributed_discovery/audience/verification.py",
        root / "src/distributed_discovery/audience/study.py",
        root / "studies/DD-013-audience-design/proof.md",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-013",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd013-audience",
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in inputs},
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": {str(path.relative_to(run)): _sha(path) for path in sorted(outputs.glob("*"))},
    }
    _write(run / "manifest.json", manifest)
    _write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(
        f"# DD-013 `{run_id}`\n\nExact bounded audience-design census.\n",
        encoding="utf-8",
    )
    print(run_id)


if __name__ == "__main__":
    main()
