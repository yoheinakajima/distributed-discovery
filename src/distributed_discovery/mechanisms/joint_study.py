"""Execute the registered DD-006B exact mechanism frontier."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import cast

import yaml

from distributed_discovery.mechanisms.joint import REGIMES, coefficient_vectors, frontier_row
from distributed_discovery.mechanisms.joint_verification import verify_row
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-006-discovery-mechanisms/configs/joint-mechanism.yml")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def row_fraction(row: dict[str, object], key: str) -> Fraction:
    return Fraction(str(row[key]))


def accounting_values(row: dict[str, object], key: str) -> list[Fraction]:
    accounting = cast(list[dict[str, object]], row["accounting_by_tie_role"])
    return [Fraction(str(item[key])) for item in accounting]


def main() -> None:
    root = repository_root()
    cp = root / CONFIG
    cfg = yaml.safe_load(cp.read_text())
    digest = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
    )
    started = datetime.now(UTC)
    rid = f"{started:%Y%m%dT%H%M%SZ}_DD-006B_{commit[:8]}_{digest[:10]}"
    run = root / "results/verified" / rid
    out = run / "outputs"
    out.mkdir(parents=True)
    (run / "config.yml").write_text(cp.read_text())
    rows = [frontier_row(regime, vector) for regime in REGIMES for vector in coefficient_vectors()]
    valid = all(verify_row(row) for row in rows)
    strict = [row for row in rows if bool(row["strict"])]
    regime_results = []
    for regime in REGIMES:
        subset = [row for row in rows if row["regime"] == regime]
        strict_subset = [row for row in subset if bool(row["strict"])]
        regime_results.append(
            {
                "regime": regime,
                "weak_rows": sum(bool(row["weak"]) for row in subset),
                "strict_rows": len(strict_subset),
                "maximum_margin": str(max(row_fraction(row, "all_tie_margin") for row in subset)),
                "minimum_strict_transfer_bound": (
                    str(
                        min(
                            max(accounting_values(row, "worst_case_abs_transfer"))
                            for row in strict_subset
                        )
                    )
                    if strict_subset
                    else None
                ),
                "minimum_strict_expected_subsidy": (
                    str(
                        min(
                            max(accounting_values(row, "expected_total_transfer"))
                            for row in strict_subset
                        )
                    )
                    if strict_subset
                    else None
                ),
                "best_implementable_discovery": (
                    max(
                        cast(list[str], row["truthful_discovery_by_tie_role"])[0]
                        for row in strict_subset
                    )
                    if strict_subset
                    else None
                ),
                "strict_profile_best_response_multiplicity": 1 if strict_subset else None,
            }
        )
    summary = {
        "frontier_rows": len(rows),
        "weak_rows": sum(bool(r["weak"]) for r in rows),
        "strict_rows": sum(bool(r["strict"]) for r in rows),
        "maximum_margin": str(max(Fraction(str(r["all_tie_margin"])) for r in rows)),
        "strict_rows_with_positive_information_weight": sum(
            bool(r["strict"])
            and Fraction(str(cast(list[object], r["coefficients"])[0])) > 0
            for r in rows
        ),
        "all_rows_participation": all(
            bool(accounting["participation"])
            for row in rows
            for accounting in cast(
                list[dict[str, object]], row["accounting_by_tie_role"]
            )
        ),
        "independent_verifier": valid,
        "regime_results": regime_results,
        "minimum_strict_transfer_bound": str(
            min(max(accounting_values(row, "worst_case_abs_transfer")) for row in strict)
        ),
        "minimum_strict_expected_subsidy": str(
            min(max(accounting_values(row, "expected_total_transfer")) for row in strict)
        ),
        "best_strict_discovery": max(
            cast(list[str], row["truthful_discovery_by_tie_role"])[0] for row in strict
        ),
    }
    write(out / "joint-mechanism-frontier.json", rows)
    write(out / "joint-mechanism-summary.json", summary)
    write(
        out / "mechanism-registry.json",
        [
            {
                "mechanism_id": f"DD006B-{index:02d}",
                "regime": row["regime"],
                "coefficients": row["coefficients"],
                "normalization": "nonnegative coefficients sum to one",
            }
            for index, row in enumerate(rows, start=1)
        ],
    )
    write(
        out / "incentive-slacks.json",
        [
            {
                "regime": row["regime"],
                "coefficients": row["coefficients"],
                "tie_roles": row["deviation_certificates_by_tie_role"],
            }
            for row in rows
        ],
    )
    write(
        out / "certificates.json",
        {
            "format": "exact-fraction exhaustive-deviation-and-accounting-certificate-v1",
            "verified_rows": sum(verify_row(row) for row in rows),
            "corruption_test": "tests/unit/test_joint_mechanisms.py",
        },
    )
    write(
        out / "comparison.json",
        {
            "DD-006": {
                "rows": 9,
                "strict_rows": 0,
                "reference": "20260721T051457Z_DD-006_d49a50ea_068bce4af3",
            },
            "DD-006A": {
                "rows": 123,
                "weak_rows": 31,
                "strict_rows": 0,
                "maximum_margin": "0",
                "reference": "20260721T140745Z_DD-006_401ad624_c942f43e42",
            },
            "DD-006B": {
                "rows": len(rows),
                "weak_rows": summary["weak_rows"],
                "strict_rows": summary["strict_rows"],
                "maximum_margin": summary["maximum_margin"],
            },
        },
    )
    write(run / "validation.json", {"passed": valid, **summary})
    outputs = {str(p.relative_to(run)): sha(p) for p in out.glob("*")}
    inputs = [
        cp,
        root / "src/distributed_discovery/mechanisms/joint.py",
        root / "src/distributed_discovery/mechanisms/joint_verification.py",
        root / "src/distributed_discovery/mechanisms/joint_study.py",
    ]
    manifest = {
        "schema_version": 1,
        "run_id": rid,
        "study_id": "DD-006B",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if valid else 1,
        "validation_status": "passed" if valid else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": "make dd006b-joint-mechanism",
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": sha(root / "uv.lock"),
        "input_hashes": {str(p.relative_to(root)): sha(p) for p in inputs},
        "random_seeds": {"algorithm": [], "model": None},
        "outputs": outputs,
    }
    write(run / "manifest.json", manifest)
    write(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(
        f"# DD-006B `{rid}`\n\nExact bounded joint-mechanism frontier.\n"
    )
    print(rid)


if __name__ == "__main__":
    main()
