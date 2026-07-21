"""Run the registered exact DD-014 conditional-attention census."""

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

from distributed_discovery.conditional.model import (
    POLICY_TYPES,
    anonymous_profiles,
    evaluate_profile,
    evaluate_raw_ordered,
    raw_policy_table,
)
from distributed_discovery.conditional.verification import corruption_tests, verify_bundle
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-014-conditional-attention/configs/census.yml")
PRIVATE_RAW_POLICY = 12
PUBLIC_RAW_POLICY = 10


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _flags(
    profiles: dict[tuple[int, int, int], dict[str, Any]], counts: tuple[int, int, int]
) -> tuple[bool, bool]:
    weak = strict = True
    for source, count in enumerate(counts):
        if count == 0:
            continue
        current = profiles[counts]["payoffs"][POLICY_TYPES[source]]
        assert current is not None
        for target in range(3):
            if target == source:
                continue
            changed = list(counts)
            changed[source] -= 1
            changed[target] += 1
            changed_key = (changed[0], changed[1], changed[2])
            deviation = profiles[changed_key]["payoffs"][POLICY_TYPES[target]]
            assert deviation is not None
            weak = weak and current >= deviation
            strict = strict and current > deviation
    return weak, strict


def _profile_row(
    counts: tuple[int, int, int], metrics: dict[str, Any], weak: bool, strict: bool
) -> dict[str, Any]:
    return {
        "counts": dict(zip(POLICY_TYPES, counts, strict=True)),
        "probability_mass": str(metrics["probability_mass"]),
        "discovery": str(metrics["discovery"]),
        "action_quality": str(metrics["action_quality"]),
        "expected_distinct_actions": str(metrics["expected_distinct_actions"]),
        "payoffs": {
            policy: None if metrics["payoffs"][policy] is None else str(metrics["payoffs"][policy])
            for policy in POLICY_TYPES
        },
        "weak_equilibrium": weak,
        "strict_equilibrium": strict,
    }


def _main_cell(n: int, p: Fraction, q: Fraction) -> dict[str, Any]:
    profiles = {counts: evaluate_profile(counts, p, q) for counts in anonymous_profiles(n)}
    flags = {counts: _flags(profiles, counts) for counts in profiles}
    optimum = max(row["discovery"] for row in profiles.values())
    planners = sorted(
        [list(counts) for counts, row in profiles.items() if row["discovery"] == optimum]
    )
    equilibria = sorted([list(counts) for counts, flag in flags.items() if flag[0]])
    strict = sorted([list(counts) for counts, flag in flags.items() if flag[1]])
    unconditional_counts = [
        (private, public, 0) for private in range(n + 1) for public in [n - private]
    ]
    unconditional_optimum = max(profiles[counts]["discovery"] for counts in unconditional_counts)
    unconditional_planners = sorted(
        [
            list(counts)
            for counts in unconditional_counts
            if profiles[counts]["discovery"] == unconditional_optimum
        ]
    )
    equilibrium_best = max(
        profiles[(counts[0], counts[1], counts[2])]["discovery"] for counts in equilibria
    )
    return {
        "agents": n,
        "private_accuracy": str(p),
        "shared_accuracy": str(q),
        "accuracy_relation": "shared-higher" if q > p else ("private-higher" if q < p else "equal"),
        "profiles": [_profile_row(counts, profiles[counts], *flags[counts]) for counts in profiles],
        "planner_discovery": str(optimum),
        "planner_profiles": planners,
        "weak_equilibrium_profiles": equilibria,
        "strict_equilibrium_profiles": strict,
        "best_equilibrium_discovery": str(equilibrium_best),
        "unconditional_planner_discovery": str(unconditional_optimum),
        "unconditional_planner_profiles": unconditional_planners,
        "conditional_gain": str(optimum - unconditional_optimum),
        "contrarian_is_planner_optimal": any(counts[2] > 0 for counts in planners),
        "all_equilibria_planner_optimal": all(
            profiles[(counts[0], counts[1], counts[2])]["discovery"] == optimum
            for counts in equilibria
        ),
        "equilibrium_wedge": str(optimum - equilibrium_best),
    }


def _raw_flags(
    profiles: dict[tuple[int, int], dict[str, Any]], policies: tuple[int, int]
) -> tuple[bool, bool]:
    weak = strict = True
    row = profiles[policies]
    for role in range(2):
        for deviation in range(16):
            if deviation == policies[role]:
                continue
            changed = list(policies)
            changed[role] = deviation
            payoff = profiles[(changed[0], changed[1])]["payoffs"][role]
            weak = weak and row["payoffs"][role] >= payoff
            strict = strict and row["payoffs"][role] > payoff
    return weak, strict


def _raw_cell(p: Fraction, q: Fraction) -> dict[str, Any]:
    profiles = {
        (first, second): evaluate_raw_ordered((first, second), p, q)
        for first in range(16)
        for second in range(16)
    }
    flags = {policies: _raw_flags(profiles, policies) for policies in profiles}
    optimum = max(row["discovery"] for row in profiles.values())
    planners = sorted(
        [list(policies) for policies, row in profiles.items() if row["discovery"] == optimum]
    )
    equilibria = sorted([list(policies) for policies, flag in flags.items() if flag[0]])
    strict = sorted([list(policies) for policies, flag in flags.items() if flag[1]])
    equilibrium_best = max(
        profiles[(policies[0], policies[1])]["discovery"] for policies in equilibria
    )
    restricted = [
        (PRIVATE_RAW_POLICY, PRIVATE_RAW_POLICY),
        (PRIVATE_RAW_POLICY, PUBLIC_RAW_POLICY),
        (PUBLIC_RAW_POLICY, PRIVATE_RAW_POLICY),
        (PUBLIC_RAW_POLICY, PUBLIC_RAW_POLICY),
    ]
    restricted_optimum = max(profiles[policies]["discovery"] for policies in restricted)
    return {
        "private_accuracy": str(p),
        "shared_accuracy": str(q),
        "raw_optimum_discovery": str(optimum),
        "raw_planner_profiles": planners,
        "raw_equilibrium_profiles": equilibria,
        "raw_strict_equilibrium_profiles": strict,
        "raw_best_equilibrium_discovery": str(equilibrium_best),
        "restricted_unconditional_optimum_discovery": str(restricted_optimum),
        "unrestricted_gain": str(optimum - restricted_optimum),
        "raw_optimum_attained_by_complementary_constants": [0, 15] in planners
        and [15, 0] in planners,
    }


def policy_registry() -> dict[str, Any]:
    return {
        "labels": 3,
        "class": "complete deterministic label-equivariant agreement-respecting disagreement class",
        "unrestricted": False,
        "policies": [
            {"policy": "private-dominant", "agreement": "common", "disagreement": "private"},
            {"policy": "public-dominant", "agreement": "common", "disagreement": "shared"},
            {"policy": "contrarian", "agreement": "common", "disagreement": "third-label"},
        ],
        "raw_two_label_audit": {
            "labels": 2,
            "agents": 2,
            "policy_count": 16,
            "ordered_profile_count": 256,
            "purpose": "scope audit only; not the registered M=3 class",
            "private_policy_id": PRIVATE_RAW_POLICY,
            "public_policy_id": PUBLIC_RAW_POLICY,
            "tables": {str(policy): raw_policy_table(policy) for policy in range(16)},
        },
    }


def build_bundle(config: dict[str, Any]) -> dict[str, Any]:
    accuracies = [Fraction(str(value)) for value in config["accuracies"]]
    cells = [
        _main_cell(int(n), p, q) for n in config["agents"] for p in accuracies for q in accuracies
    ]
    raw_accuracies = [Fraction(str(value)) for value in config["raw_audit_accuracies"]]
    raw = [_raw_cell(p, q) for p in raw_accuracies for q in raw_accuracies]
    theorem_checks = {
        "restricted_policy_count_is_three": len(POLICY_TYPES) == 3,
        "probabilities_normalize": all(
            row["probability_mass"] == "1" for cell in cells for row in cell["profiles"]
        ),
        "conditional_weakly_expands_unconditional": all(
            Fraction(cell["conditional_gain"]) >= 0 for cell in cells
        ),
        "raw_optimum_is_full_discovery": all(cell["raw_optimum_discovery"] == "1" for cell in raw),
        "raw_complementary_constants_are_optimal": all(
            cell["raw_optimum_attained_by_complementary_constants"] for cell in raw
        ),
        "raw_audit_exposes_restricted_class_gap": all(
            Fraction(cell["unrestricted_gain"]) > 0 for cell in raw
        ),
    }
    if not all(theorem_checks.values()):
        raise RuntimeError("DD-014 theorem-grid audit failed")
    summary = {
        "grid_cells": len(cells),
        "anonymous_profiles": sum(len(cell["profiles"]) for cell in cells),
        "weak_equilibrium_profiles": sum(len(cell["weak_equilibrium_profiles"]) for cell in cells),
        "strict_equilibrium_profiles": sum(
            len(cell["strict_equilibrium_profiles"]) for cell in cells
        ),
        "cells_with_positive_conditional_gain": sum(
            Fraction(cell["conditional_gain"]) > 0 for cell in cells
        ),
        "cells_with_contrarian_planner": sum(
            cell["contrarian_is_planner_optimal"] for cell in cells
        ),
        "cells_all_equilibria_planner_optimal": sum(
            cell["all_equilibria_planner_optimal"] for cell in cells
        ),
        "cells_with_positive_equilibrium_wedge": sum(
            Fraction(cell["equilibrium_wedge"]) > 0 for cell in cells
        ),
        "raw_audit_cells": len(raw),
        "raw_ordered_profiles": 256 * len(raw),
        "raw_cells_with_restricted_class_gap": sum(
            Fraction(cell["unrestricted_gain"]) > 0 for cell in raw
        ),
    }
    return {
        "schema_version": "dd014-conditional-attention-v1",
        "policy_registry": policy_registry(),
        "cells": cells,
        "raw_audit": raw,
        "theorem_checks": theorem_checks,
        "summary": summary,
    }


def _write_csv(path: Path, cells: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        fields = (
            "agents",
            "private_accuracy",
            "shared_accuracy",
            "private_dominant",
            "public_dominant",
            "contrarian",
            "discovery",
            "action_quality",
            "expected_distinct_actions",
            "weak_equilibrium",
            "strict_equilibrium",
            "planner_optimal",
        )
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for cell in cells:
            planners = cell["planner_profiles"]
            for row in cell["profiles"]:
                counts = [row["counts"][policy] for policy in POLICY_TYPES]
                writer.writerow(
                    {
                        "agents": cell["agents"],
                        "private_accuracy": cell["private_accuracy"],
                        "shared_accuracy": cell["shared_accuracy"],
                        "private_dominant": counts[0],
                        "public_dominant": counts[1],
                        "contrarian": counts[2],
                        "discovery": row["discovery"],
                        "action_quality": row["action_quality"],
                        "expected_distinct_actions": row["expected_distinct_actions"],
                        "weak_equilibrium": row["weak_equilibrium"],
                        "strict_equilibrium": row["strict_equilibrium"],
                        "planner_optimal": counts in planners,
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
        raise RuntimeError("DD-014 primary run requires a clean committed implementation")
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-014_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / run_id
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    bundle = build_bundle(config)
    verification = verify_bundle(bundle)
    corruptions = corruption_tests(bundle)
    if not verification["passed"] or not all(corruptions.values()):
        raise RuntimeError("DD-014 independent verification failed")
    _write(outputs / "policy-census.json", bundle["cells"])
    _write_csv(outputs / "policy-census.csv", bundle["cells"])
    _write(
        outputs / "policy-phase-map.json",
        [
            {key: value for key, value in cell.items() if key != "profiles"}
            for cell in bundle["cells"]
        ],
    )
    _write(outputs / "raw-policy-audit.json", bundle["raw_audit"])
    _write(outputs / "policy-registry.json", bundle["policy_registry"])
    _write(outputs / "theorem-checks.json", bundle["theorem_checks"])
    _write(outputs / "summary.json", bundle["summary"])
    _write(outputs / "verification.json", verification)
    _write(outputs / "corruption-tests.json", corruptions)
    _write(run / "validation.json", {"passed": True, **bundle["summary"], **verification})
    (run / "stdout.txt").write_text(
        f"{run_id}\nexact conditional-attention census and independent verification passed\n",
        encoding="utf-8",
    )
    (run / "stderr.txt").write_text("", encoding="utf-8")
    inputs = [
        config_path,
        root / "src/distributed_discovery/conditional/model.py",
        root / "src/distributed_discovery/conditional/verification.py",
        root / "src/distributed_discovery/conditional/study.py",
        root / "studies/DD-014-conditional-attention/proof.md",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-014",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd014-conditional",
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
        f"# DD-014 `{run_id}`\n\nExact bounded conditional-attention census.\n",
        encoding="utf-8",
    )
    print(run_id)


if __name__ == "__main__":
    main()
