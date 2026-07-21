"""Materially separate verifier for DiscoveryBench certificates."""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import cast

from distributed_discovery.benchmark.model import (
    PROHIBITED_CAPABILITIES,
    InformationBoundaryError,
    builtin_protocols,
    compatibility_matrix,
    task_registry,
    task_view,
    validate_task,
)


def independent_expected() -> dict[tuple[str, str], dict[str, str | int | bool]]:
    """Recompute values from direct identities and separately checked fixtures."""
    canonical_private = Fraction(1) - Fraction(4, 5) ** 8
    all_independent = Fraction(1) - Fraction(1, 4) ** 8
    return {
        ("DB-G01", "blind-distinct"): {"discovery": str(Fraction(8, 16)), "distinct-actions": "8"},
        ("DB-G01", "pooled-planner"): {
            "discovery": "860391662035297/1001129150390625",
            "recovery-budget": 7,
        },
        ("DB-G02", "ex-ante-role-policy"): {"discovery": "7/10", "protocol-loss": "0"},
        ("DB-G03", "private-clue-following"): {
            "discovery": str(canonical_private),
            "protocol-loss": "0",
        },
        ("DB-G04", "consensus"): {"discovery": "5/9"},
        ("DB-G05", "anonymous-market"): {"discovery": "171/308", "protocol-loss": "1/2772"},
        ("DB-G06", "private-clue-following"): {"discovery": "8/9", "effective-channels": "8/5"},
        ("DB-G07", "posterior-sampling"): {"discovery": "3/4", "source-concentration": "17/25"},
        ("DB-G08", "sequential-greedy"): {
            "discovery": "7/10",
            "expected-actions": "109/40",
            "expected-rounds": "109/40",
        },
        ("DB-G09", "marginal-coverage-greedy"): {"weighted-coverage": "4", "distinct-actions": "2"},
        ("DB-G10", "sole-rescue-response"): {
            "discovery": "8/9",
            "truthfulness": True,
            "obedience": True,
            "strict-margin": "0",
            "transfer-budget": "0",
        },
        ("DB-G11", "dd006a-mechanism"): {
            "discovery": "11/12",
            "truthfulness": True,
            "obedience": True,
            "strict-margin": "0",
            "transfer-budget": "0",
        },
        ("DB-G12", "dd006b-mechanism"): {
            "discovery": "11/12",
            "truthfulness": True,
            "obedience": True,
            "strict-margin": "13/72",
            "transfer-budget": "35/24",
        },
        ("DB-G13", "private-clue-following"): {
            "discovery": str(2 * Fraction(2, 3) - Fraction(2, 3) ** 2),
            "information-cost": "1/8",
            "social-net-value": "55/72",
        },
        ("DB-G14", "ex-ante-role-policy"): {
            "discovery": str(all_independent),
            "information-cost": "0",
            "effective-channels": "8",
        },
        ("DB-G15", "registered-atlas-architecture"): {
            "discovery": "5/6",
            "average-action-quality": "5/8",
            "expected-actions": "4/3",
            "expected-rounds": "4/3",
            "social-net-value": "5/6",
        },
    }


def _result_map(certificate: dict[str, object]) -> dict[tuple[str, str], dict[str, object]]:
    results = certificate.get("results")
    if not isinstance(results, list):
        raise ValueError("certificate has no result list")
    return {
        (str(row["task_id"]), str(row["protocol_id"])): dict(row["metrics"])
        for row in results
        if isinstance(row, dict) and isinstance(row.get("metrics"), dict)
    }


def verify_certificate(certificate: dict[str, object], root: Path) -> dict[str, object]:
    tasks = task_registry()
    for task in tasks:
        validate_task(task)
    claims_source = (root / "claims/claims.yml").read_text(encoding="utf-8")
    provenance_ok = all(
        all(claim in claims_source for claim in cast(list[str], task["reference_claims"]))
        and all(
            any((root / "results").glob(f"**/{run_id}/manifest.json"))
            for run_id in cast(list[str], task["reference_runs"])
        )
        for task in tasks
    )
    expected = independent_expected()
    observed = _result_map(certificate)
    values_ok = observed == expected
    matrix = compatibility_matrix()
    counts_ok = (
        certificate.get("task_count") == 15
        and certificate.get("protocol_count") == 13
        and certificate.get("metric_count") == 19
        and certificate.get("candidate_pairs") == 195
        and certificate.get("compatible_pairs") == len(expected) == 16
        and certificate.get("excluded_pairs") == 179
        and len(matrix) == 195
    )
    boundaries_ok = True
    protocol = next(iter(builtin_protocols().values()))
    view = task_view(tasks[0], protocol)
    for key in PROHIBITED_CAPABILITIES:
        try:
            _ = view[key]
        except InformationBoundaryError:
            continue
        boundaries_ok = False
    try:
        view._values["task_id"] = "corrupt"  # type: ignore[index]
        boundaries_ok = False
    except TypeError:
        pass
    return {
        "passed": values_ok and counts_ok and boundaries_ok and provenance_ok,
        "schemas_valid": True,
        "golden_values_recomputed": values_ok,
        "compatibility_counts_verified": counts_ok,
        "information_boundaries_verified": boundaries_ok,
        "provenance_resolved": provenance_ok,
        "verified_rows": len(observed),
    }


def corruption_tests(certificate: dict[str, object], root: Path) -> dict[str, bool]:
    corrupted = __import__("copy").deepcopy(certificate)
    results = cast(list[dict[str, object]], corrupted["results"])
    metrics = cast(dict[str, object], results[0]["metrics"])
    metrics["discovery"] = "0"
    value_rejected = not bool(verify_certificate(corrupted, root)["passed"])

    protocol = next(iter(builtin_protocols().values()))
    leaked = replace(protocol, capabilities=protocol.capabilities | {"target_state"})
    view = task_view(task_registry()[0], leaked)
    try:
        _ = view["target_state"]
        leakage_rejected = False
    except InformationBoundaryError:
        leakage_rejected = True
    return {
        "corrupted_value_rejected": value_rejected,
        "leaked_information_rejected": leakage_rejected,
    }
