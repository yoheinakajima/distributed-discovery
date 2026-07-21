"""Independent checks for DD-008B analytic source-choice thresholds."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from distributed_discovery.acquisition.n_agent import equilibrium, planner
from distributed_discovery.acquisition.n_agent_verification import direct


def direct_private_threshold(n: int, k: int, p: Fraction) -> Fraction:
    """Reconstruct a deviation threshold from exhaustive state enumeration."""
    _, _, common_before = direct(n, k, p, Fraction())
    _, independent_after, _ = direct(n, k + 1, p, Fraction())
    return independent_after - common_before


def direct_planner_threshold(n: int, k: int, p: Fraction) -> Fraction:
    before, _, _ = direct(n, k, p, Fraction())
    after, _, _ = direct(n, k + 1, p, Fraction())
    return after - before


def direct_equilibrium_counts(n: int, p: Fraction, cost: Fraction) -> list[int]:
    return [k for k in range(n + 1) if equilibrium(n, k, p, cost)[0]]


def verify_frozen_census(
    census_path: Path,
    analytic_equilibria: dict[tuple[int, Fraction, Fraction], list[int]],
    analytic_planners: dict[tuple[int, Fraction, Fraction], list[int]],
) -> int:
    rows: list[dict[str, Any]] = json.loads(census_path.read_text())
    for row in rows:
        key = (int(row["agents"]), Fraction(row["accuracy"]), Fraction(row["cost"]))
        expected_equilibria = [int(cell["k"]) for cell in row["cells"] if cell["weak_equilibrium"]]
        if analytic_equilibria[key] != expected_equilibria:
            raise ValueError(f"equilibrium mismatch for {key}")
        if analytic_planners[key] != [int(k) for k in row["planner_k"]]:
            raise ValueError(f"planner mismatch for {key}")
        if planner(*key) != analytic_planners[key]:
            raise ValueError(f"legacy planner mismatch for {key}")
    return len(rows)


def verify_threshold_rows(rows: list[dict[str, object]]) -> int:
    """Reject any threshold table that differs from direct enumeration."""
    for row in rows:
        n = int(str(row["agents"]))
        k = int(str(row["k"]))
        p = Fraction(str(row["accuracy"]))
        if Fraction(str(row["private_threshold"])) != direct_private_threshold(n, k, p):
            raise ValueError(f"private threshold mismatch for {(n, k, p)}")
        if Fraction(str(row["planner_threshold"])) != direct_planner_threshold(n, k, p):
            raise ValueError(f"planner threshold mismatch for {(n, k, p)}")
    return len(rows)
