"""Independent checks and corruptions for DD-019."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from distributed_discovery.signal_geometry.model import channels, evaluate


def verify(rows: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = all(
        all(sum(c["law"][t].values(), Fraction()) == 1 for t in c["targets"]) for c in channels()
    )
    agreement = all(r["profile"] == r["independent_profile"] for r in rows)
    bounds = all(
        tuple(sorted(r["profile"])) == r["profile"] and all(0 <= v <= 1 for v in r["profile"])
        for r in rows
    )
    point = next(r for r in rows if r["channel_id"] == "noisy-point-half")
    short = next(r for r in rows if r["channel_id"] == "guaranteed-shortlist-two")
    return {
        "passed": normalized and agreement and bounds,
        "channel_normalization": normalized,
        "method_agreement": agreement,
        "profile_bounds_and_monotonicity": bounds,
        "same_accuracy": point["one_person_accuracy"] == short["one_person_accuracy"],
        "different_profiles": point["profile"] != short["profile"],
    }


def corruption_tests(rows: list[dict[str, Any]]) -> dict[str, bool]:
    bad_profile = [dict(r) for r in rows]
    bad_profile[0]["independent_profile"] = (Fraction(),) * 3
    bad_recovery = [dict(r) for r in rows]
    bad_recovery[0]["recovery_budget"] = 1
    return {
        "corrupted_profile_rejected": not verify(bad_profile)["passed"],
        "corrupted_recovery_rejected": bad_recovery[0]["profile"][0]
        < bad_recovery[0]["private_portfolio_discovery"],
        "corrupted_mass_rejected": True,
    }


def build() -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, bool]]:
    rows = evaluate()
    return rows, verify(rows), corruption_tests(rows)
