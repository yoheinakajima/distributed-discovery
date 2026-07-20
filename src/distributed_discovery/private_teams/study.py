"""Execute the bounded initial DD-001 exact grid and canonical lower-bound search."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import time
from collections.abc import Iterable
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.private_teams.model import (
    Profile,
    direct_profile,
    direct_value,
    evaluate_direct,
    evaluate_formula,
    pooled_planner_value,
    territorial_profile,
    territorial_value,
)
from distributed_discovery.private_teams.optimize import (
    coordinate_ascent,
    direct_is_coordinate_fixed,
    exhaustive_optimum,
    random_profile,
    reduced_profile_count,
)
from distributed_discovery.site.build import _canonical_data, _passing_baseline
from distributed_discovery.validation.bootstrap import repository_root

CONFIG_RELATIVE = Path("studies/DD-001-private-information-teams/configs/initial-grid.yml")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sanitize_package_snapshot(lines: Iterable[str]) -> list[str]:
    """Omit the local project URL because its commit and lock are recorded separately."""
    return sorted(
        line for line in lines if not line.lower().startswith("distributed-discovery @ file:")
    )


def _package_snapshot(root: Path) -> list[str]:
    """Capture third-party versions without serializing a private checkout path."""
    lines = subprocess.check_output(["uv", "pip", "freeze"], cwd=root, text=True).splitlines()
    return _sanitize_package_snapshot(lines)


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def _profile_json(profile: Profile) -> list[list[int]]:
    return [list(policy) for policy in profile]


def _classify(profile: Profile, candidates: int) -> str:
    identity = tuple(range(candidates))
    if all(policy == identity for policy in profile):
        return "direct"
    if all(len(set(policy)) == 1 for policy in profile):
        return "territorial"
    return "hybrid"


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _phase_svg(rows: list[dict[str, Any]]) -> str:
    """Render exact role-gain points without adding a plotting dependency."""
    width, height = 760, 430
    left, right, top, bottom = 78, 24, 42, 66
    plot_width = width - left - right
    plot_height = height - top - bottom
    maximum_gain = max(float(Fraction(str(row["role_gain_fraction"]))) for row in rows)
    y_max = max(0.12, math.ceil(maximum_gain * 100) / 100)
    series: dict[tuple[int, int], list[tuple[float, float, bool]]] = {}
    for row in rows:
        key = (int(row["candidates"]), int(row["searchers"]))
        accuracy = float(Fraction(str(row["accuracy"])))
        gain = float(Fraction(str(row["role_gain_fraction"])))
        series.setdefault(key, []).append((accuracy, gain, bool(row["direct_is_optimal"])))
    colors = ["#2a78d6", "#087d26", "#a76900", "#b4476f", "#6b5fb5"]

    def x_position(value: float) -> float:
        return left + value * plot_width

    def y_position(value: float) -> float:
        return top + plot_height * (1 - value / y_max)

    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 430" role="img">',
        "<title>Certified tiny-case role gains over direct clue-following</title>",
        "<desc>Lines show exact optimal discovery minus direct clue-following "
        "by clue accuracy.</desc>",
        '<rect width="760" height="430" fill="white"/>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" '
        f'y2="{top + plot_height}" stroke="#222"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#222"/>',
    ]
    for tick in range(6):
        x_value = tick / 5
        x = x_position(x_value)
        elements.append(
            f'<line x1="{x:.1f}" y1="{top + plot_height}" x2="{x:.1f}" '
            f'y2="{top + plot_height + 5}" stroke="#222"/>'
        )
        elements.append(
            f'<text x="{x:.1f}" y="{top + plot_height + 23}" text-anchor="middle" '
            f'font-family="system-ui" font-size="12">{x_value:.1f}</text>'
        )
    for tick in range(5):
        y_value = y_max * tick / 4
        y = y_position(y_value)
        elements.append(
            f'<line x1="{left - 5}" y1="{y:.1f}" x2="{left + plot_width}" '
            f'y2="{y:.1f}" stroke="#ddd"/>'
        )
        elements.append(
            f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-family="system-ui" font-size="12">{y_value:.3f}</text>'
        )
    elements.extend(
        [
            f'<text x="{left + plot_width / 2:.1f}" y="{height - 18}" text-anchor="middle" '
            'font-family="system-ui" font-size="14">clue accuracy p</text>',
            f'<text transform="translate(20 {top + plot_height / 2:.1f}) rotate(-90)" '
            'text-anchor="middle" font-family="system-ui" font-size="14">'
            "role gain over direct</text>",
        ]
    )
    legend_x = left + 8
    for index, (key, points) in enumerate(sorted(series.items())):
        color = colors[index % len(colors)]
        points.sort()
        coordinates = " ".join(
            f"{x_position(accuracy):.1f},{y_position(gain):.1f}" for accuracy, gain, _ in points
        )
        elements.append(
            f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="2"/>'
        )
        for accuracy, gain, direct_optimal in points:
            fill = "white" if direct_optimal else color
            elements.append(
                f'<circle cx="{x_position(accuracy):.1f}" cy="{y_position(gain):.1f}" '
                f'r="4" fill="{fill}" stroke="{color}" stroke-width="2"/>'
            )
        legend_y = 19 + index * 18
        elements.append(
            f'<line x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 20}" '
            f'y2="{legend_y}" stroke="{color}" stroke-width="2"/>'
        )
        elements.append(
            f'<text x="{legend_x + 26}" y="{legend_y + 4}" font-family="system-ui" '
            f'font-size="12">M={key[0]}, N={key[1]}</text>'
        )
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def _complexity(config: dict[str, Any]) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    limit = int(config["max_reduced_profiles_per_case"])
    for case in config["tiny_cases"]:
        candidates = int(case["candidates"])
        searchers = int(case["searchers"])
        policies = candidates**candidates
        labeled = policies**searchers
        reduced = reduced_profile_count(candidates, searchers)
        if reduced > limit:
            raise RuntimeError(f"configured case M={candidates}, N={searchers} exceeds cost limit")
        rows.append(
            {
                "candidates": candidates,
                "searchers": searchers,
                "signal_profiles": candidates**searchers,
                "policies_per_agent": policies,
                "labeled_profiles": labeled,
                "agent_symmetric_profiles": reduced,
                "accuracy_count": len(case["accuracies"]),
            }
        )
    return rows


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG_RELATIVE
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    config_hash = hashlib.sha256(canonical_config).hexdigest()
    complexity = _complexity(config)
    commit = _git(root, "rev-parse", "HEAD")
    dirty = bool(_git(root, "status", "--porcelain"))
    started = datetime.now(UTC)
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-001_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    output_dir = run_dir / "outputs"
    run_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir()
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    _write_json(output_dir / "complexity.json", complexity)
    budget_seconds = float(config["time_budget_seconds"])
    deadline = time.monotonic() + budget_seconds
    log_lines = [
        f"run_id={run_id}",
        f"cost_audit_cases={len(complexity)}",
        f"max_reduced_profiles={max(row['agent_symmetric_profiles'] for row in complexity)}",
    ]

    phase_rows: list[dict[str, Any]] = []
    optimal_profiles: dict[str, Any] = {}
    all_direct_matches = True
    all_normalized = True
    all_bounds = True
    all_counts = True
    for case in config["tiny_cases"]:
        candidates = int(case["candidates"])
        searchers = int(case["searchers"])
        for accuracy_text in case["accuracies"]:
            if time.monotonic() > deadline:
                raise RuntimeError("configured time budget exhausted during exact grid")
            accuracy = _fraction(str(accuracy_text))
            exhaustive_result = exhaustive_optimum(candidates, searchers, accuracy)
            direct_baseline = direct_value(searchers, accuracy)
            territorial = territorial_value(candidates, searchers)
            pooled = pooled_planner_value(candidates, searchers, accuracy)
            direct_check, normalization = evaluate_direct(
                exhaustive_result.profile, candidates, accuracy
            )
            formula_check = evaluate_formula(exhaustive_result.profile, candidates, accuracy)
            all_direct_matches &= direct_check == formula_check == exhaustive_result.value
            all_normalized &= normalization == 1
            all_bounds &= direct_baseline <= exhaustive_result.value <= pooled
            all_counts &= exhaustive_result.reduced_profile_count == reduced_profile_count(
                candidates, searchers
            )
            key = f"M{candidates}_N{searchers}_p{accuracy.numerator}-{accuracy.denominator}"
            optimal_profiles[key] = {
                "action_indexing": "zero-based",
                "profile": _profile_json(exhaustive_result.profile),
                "classification": _classify(exhaustive_result.profile, candidates),
                "tie_count_in_agent-symmetric_enumeration": exhaustive_result.ties,
            }
            phase_rows.append(
                {
                    "case": key,
                    "candidates": candidates,
                    "searchers": searchers,
                    "accuracy": str(accuracy),
                    "policy_count": exhaustive_result.policy_count,
                    "reduced_profile_count": exhaustive_result.reduced_profile_count,
                    "optimum_fraction": str(exhaustive_result.value),
                    "optimum_decimal": f"{float(exhaustive_result.value):.12f}",
                    "direct_fraction": str(direct_baseline),
                    "direct_decimal": f"{float(direct_baseline):.12f}",
                    "territorial_fraction": str(territorial),
                    "pooled_fraction": str(pooled),
                    "role_gain_fraction": str(exhaustive_result.value - direct_baseline),
                    "direct_is_optimal": exhaustive_result.value == direct_baseline,
                    "selected_policy_type": _classify(exhaustive_result.profile, candidates),
                    "direct_evaluator_match": direct_check == formula_check,
                    "normalization_exact": normalization == 1,
                }
            )
            log_lines.append(
                f"[exact] {key} optimum={exhaustive_result.value} direct={direct_baseline} "
                f"profiles={exhaustive_result.reduced_profile_count}"
            )

    phase_fields = list(phase_rows[0])
    _write_csv(output_dir / "tiny-phase-grid.csv", phase_rows, phase_fields)
    (output_dir / "phase-grid.svg").write_text(_phase_svg(phase_rows), encoding="utf-8")
    _write_json(output_dir / "optimal-policies.json", optimal_profiles)

    canonical = config["canonical"]
    candidates = int(canonical["candidates"])
    searchers = int(canonical["searchers"])
    accuracy = _fraction(str(canonical["accuracy"]))
    canonical_direct_profile = direct_profile(candidates, searchers)
    starts: list[tuple[str, int | None, Profile]] = [
        ("direct", None, canonical_direct_profile),
        ("territorial", None, territorial_profile(candidates, searchers)),
    ]
    starts.extend(
        ("random", int(seed), random_profile(candidates, searchers, int(seed)))
        for seed in canonical["seeds"]
    )
    restart_rows: list[dict[str, Any]] = []
    best_value = Fraction(-1)
    best_profile: Profile | None = None
    for start_type, seed, initial in starts:
        if time.monotonic() > deadline:
            raise RuntimeError("configured time budget exhausted during canonical search")
        initial_value = evaluate_formula(initial, candidates, accuracy)
        ascent_result = coordinate_ascent(
            initial, candidates, accuracy, int(canonical["max_sweeps"])
        )
        if ascent_result.value > best_value:
            best_value = ascent_result.value
            best_profile = ascent_result.profile
        restart_rows.append(
            {
                "start_type": start_type,
                "seed": "" if seed is None else seed,
                "initial_value_fraction": str(initial_value),
                "final_value_fraction": str(ascent_result.value),
                "final_value_decimal": f"{float(ascent_result.value):.12f}",
                "sweeps": ascent_result.sweeps,
                "termination": ascent_result.termination,
                "policy_type": _classify(ascent_result.profile, candidates),
            }
        )
    if best_profile is None:
        raise RuntimeError("canonical search produced no profile")
    _write_csv(output_dir / "canonical-restarts.csv", restart_rows, list(restart_rows[0]))
    _write_json(
        output_dir / "canonical-best-policy.json",
        {
            "action_indexing": "zero-based",
            "profile": _profile_json(best_profile),
            "value_fraction": str(best_value),
            "value_decimal": f"{float(best_value):.15f}",
            "classification": _classify(best_profile, candidates),
            "global_optimality": "not claimed",
        },
    )
    baseline = _canonical_data(_passing_baseline(root))
    pooled_upper = float(baseline["metrics"]["planner"])
    canonical_direct = direct_value(searchers, accuracy)
    fixed = direct_is_coordinate_fixed(candidates, searchers, accuracy)
    canonical_metrics = {
        "candidates": candidates,
        "searchers": searchers,
        "accuracy": str(accuracy),
        "direct_fraction": str(canonical_direct),
        "direct_decimal": f"{float(canonical_direct):.15f}",
        "best_known_fraction": str(best_value),
        "best_known_decimal": f"{float(best_value):.15f}",
        "role_gain_over_direct_fraction": str(best_value - canonical_direct),
        "pooled_planner_numerical_upper": pooled_upper,
        "universal_exact_upper": 1,
        "direct_coordinate_fixed": fixed,
        "restart_count": len(starts),
        "global_optimality": "unresolved",
    }
    _write_json(output_dir / "canonical-metrics.json", canonical_metrics)
    log_lines.append(
        f"[bounded] canonical best={best_value} direct={canonical_direct} "
        f"pooled_upper={pooled_upper:.15f} restarts={len(starts)}"
    )

    validation = {
        "passed": bool(
            all_direct_matches
            and all_normalized
            and all_bounds
            and all_counts
            and best_value >= canonical_direct
            and float(best_value) <= pooled_upper
            and fixed
            and (output_dir / "phase-grid.svg").is_file()
        ),
        "tiny_formula_equals_direct": all_direct_matches,
        "tiny_probability_normalization_exact": all_normalized,
        "tiny_direct_le_optimum_le_pooled": all_bounds,
        "exhaustive_profile_counts_complete": all_counts,
        "phase_figure_created": (output_dir / "phase-grid.svg").is_file(),
        "canonical_lower_bound_at_least_direct": best_value >= canonical_direct,
        "canonical_lower_bound_below_pooled_upper": float(best_value) <= pooled_upper,
        "canonical_direct_coordinate_fixed": fixed,
        "canonical_global_optimality_claimed": False,
        "termination_reason": "completed-configured-grid-and-restarts",
        "elapsed_seconds": time.monotonic() - (deadline - budget_seconds),
        "time_budget_seconds": budget_seconds,
    }
    _write_json(run_dir / "validation.json", validation)
    _write_json(
        run_dir / "metrics.json",
        {
            "tiny_case_count": len(phase_rows),
            "tiny_role_improvement_count": sum(
                Fraction(str(row["role_gain_fraction"])) > 0 for row in phase_rows
            ),
            "tiny_direct_optimal_count": sum(bool(row["direct_is_optimal"]) for row in phase_rows),
            "canonical": canonical_metrics,
        },
    )
    (run_dir / "stdout.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    _write_json(
        run_dir / "environment.json",
        {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "packages": _package_snapshot(root),
        },
    )
    outputs = sorted(path for path in output_dir.rglob("*") if path.is_file())
    output_hashes = {str(path.relative_to(run_dir)): _sha256(path) for path in outputs}
    _write_json(run_dir / "output-checksums.json", output_hashes)
    ended = datetime.now(UTC)
    command = "make dd001"
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-001",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": ended.isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": command,
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha256(root / "uv.lock"),
        "input_hashes": {
            str(path.relative_to(root)): _sha256(path)
            for path in [
                config_path,
                root / "src/distributed_discovery/private_teams/model.py",
                root / "src/distributed_discovery/private_teams/optimize.py",
                root / "src/distributed_discovery/private_teams/study.py",
            ]
        },
        "random_seeds": {
            "algorithm": list(canonical["seeds"]),
            "model": None,
        },
        "outputs": output_hashes,
    }
    _write_json(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text("#!/bin/sh\nset -eu\nexec make dd001\n", encoding="utf-8")
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-001 initial run `{run_id}`\n\n"
        "Certified exact tiny-grid optima and a bounded canonical coordinate-ascent lower-bound "
        "search. Canonical global optimality is explicitly unresolved.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    print(f"tiny_cases={len(phase_rows)} canonical_best={float(best_value):.12f}")
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
