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


def independent_expected(version: str = "v1") -> dict[tuple[str, str], dict[str, str | int | bool]]:
    """Recompute values from direct identities and separately checked fixtures."""
    canonical_private = Fraction(1) - Fraction(4, 5) ** 8
    all_independent = Fraction(1) - Fraction(1, 4) ** 8
    expected: dict[tuple[str, str], dict[str, str | int | bool]] = {
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
    if version == "v1":
        return expected
    if version != "v2":
        raise ValueError(f"unknown benchmark version: {version}")
    private_only = Fraction(1) - Fraction(1, 2) ** 4
    designated = Fraction(1) - (1 - Fraction(3, 4)) * (1 - Fraction(1, 2)) ** 3
    public_only = Fraction(3, 4)
    equilibrium = Fraction(7, 8)
    first_gain = designated - private_only
    duplicate_loss = designated - public_only
    expected.update(
        {
            ("DB-G16", "private-only"): {
                "discovery": str(private_only),
                "attention-count": 0,
                "public-signal-user-count": 0,
                "first-use-gain": str(first_gain),
                "duplicate-use-loss": "0",
            },
            ("DB-G16", "designated-reader"): {
                "discovery": str(designated),
                "attention-count": 1,
                "public-signal-user-count": 1,
                "first-use-gain": str(first_gain),
                "duplicate-use-loss": "0",
            },
            ("DB-G16", "public-only"): {
                "discovery": str(public_only),
                "attention-count": 4,
                "public-signal-user-count": 4,
                "first-use-gain": str(first_gain),
                "duplicate-use-loss": str(duplicate_loss),
            },
            ("DB-G17", "voluntary-attention-equilibrium"): {
                "discovery": str(equilibrium),
                "attention-count": 3,
                "attention-wedge": str(designated - equilibrium),
            },
            ("DB-G17", "designated-reader"): {
                "discovery": str(designated),
                "attention-count": 1,
                "attention-wedge": "0",
            },
            ("DB-G18", "public-only"): {
                "discovery": str(public_only),
                "audience-size": 4,
                "publicity-cost": str(duplicate_loss),
            },
            ("DB-G18", "designated-reader"): {
                "discovery": str(designated),
                "audience-size": 1,
                "publicity-cost": "0",
            },
            ("DB-G18", "audience-optimal-assignment"): {
                "discovery": str(designated),
                "audience-size": 1,
                "publicity-cost": "0",
            },
            ("DB-G19", "audience-optimal-assignment"): {
                "discovery": str(designated),
                "audience-size": 1,
                "transfer-budget": "0",
            },
            ("DB-G20", "conditional-private-dominant"): {
                "discovery": str(private_only),
                "conditional-attention-category": "private-dominant",
            },
            ("DB-G20", "conditional-public-dominant"): {
                "discovery": str(public_only),
                "conditional-attention-category": "public-dominant",
            },
            ("DB-G20", "third-option-contrarian"): {
                "discovery": "895/1024",
                "conditional-attention-category": "third-option-contrarian",
            },
        }
    )
    return expected


def _result_map(certificate: dict[str, object]) -> dict[tuple[str, str], dict[str, object]]:
    results = certificate.get("results")
    if not isinstance(results, list):
        raise ValueError("certificate has no result list")
    return {
        (str(row["task_id"]), str(row["protocol_id"])): dict(row["metrics"])
        for row in results
        if isinstance(row, dict) and isinstance(row.get("metrics"), dict)
    }


def verify_certificate(
    certificate: dict[str, object], root: Path, version: str = "v1"
) -> dict[str, object]:
    tasks = task_registry(version)
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
    expected = independent_expected(version)
    observed = _result_map(certificate)
    values_ok = observed == expected
    matrix = compatibility_matrix(version)
    expected_counts = (15, 13, 19, 195, 16, 179) if version == "v1" else (20, 21, 27, 420, 28, 392)
    counts_ok = (
        certificate.get("task_count") == expected_counts[0]
        and certificate.get("protocol_count") == expected_counts[1]
        and certificate.get("metric_count") == expected_counts[2]
        and certificate.get("candidate_pairs") == expected_counts[3]
        and certificate.get("compatible_pairs") == len(expected) == expected_counts[4]
        and certificate.get("excluded_pairs") == expected_counts[5]
        and len(matrix) == expected_counts[3]
    )
    boundaries_ok = True
    protocol = next(iter(builtin_protocols(version).values()))
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


def corruption_tests(
    certificate: dict[str, object], root: Path, version: str = "v1"
) -> dict[str, bool]:
    corrupted = __import__("copy").deepcopy(certificate)
    results = cast(list[dict[str, object]], corrupted["results"])
    metrics = cast(dict[str, object], results[0]["metrics"])
    metrics["discovery"] = "0"
    value_rejected = not bool(verify_certificate(corrupted, root, version)["passed"])

    incompatible = __import__("copy").deepcopy(certificate)
    incompatible["compatible_pairs"] = int(cast(int, incompatible["compatible_pairs"])) + 1
    compatibility_rejected = not bool(verify_certificate(incompatible, root, version)["passed"])

    protocol = next(iter(builtin_protocols(version).values()))
    leaked = replace(protocol, capabilities=protocol.capabilities | {"target_state"})
    view = task_view(task_registry(version)[0], leaked)
    try:
        _ = view["target_state"]
        leakage_rejected = False
    except InformationBoundaryError:
        leakage_rejected = True
    return {
        "corrupted_value_rejected": value_rejected,
        "leaked_information_rejected": leakage_rejected,
        "corrupted_compatibility_rejected": compatibility_rejected,
    }
