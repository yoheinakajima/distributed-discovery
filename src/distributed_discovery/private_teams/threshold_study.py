"""Run the immutable DD-001B two-searcher threshold study."""

from __future__ import annotations

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

from distributed_discovery.private_teams.model import evaluate_direct, evaluate_formula
from distributed_discovery.private_teams.optimize import exhaustive_optimum
from distributed_discovery.private_teams.signatures import signature_from_policy
from distributed_discovery.private_teams.thresholds import (
    certify_informative_envelope,
    direct_two_value,
    distinct_territorial_value,
    evaluate_quadratic,
    exact_signature_optimum_fast,
    one_reroute_hybrid_profile,
    one_reroute_hybrid_value,
    restricted_winners,
    signature_profile_polynomial,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-001-private-information-teams/configs/two-agent-thresholds.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _phase_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for raw_m in config["phase_candidates"]:
        m = int(raw_m)
        lower, upper = Fraction(1, m), Fraction(1, m - 1)
        for region, p in [
            ("lower-boundary", lower),
            ("hybrid-interior", (lower + upper) / 2),
            ("upper-boundary", upper),
            ("direct-interior", (upper + 1) / 2),
        ]:
            rows.append(
                {
                    "candidates": m,
                    "region": region,
                    "accuracy": str(p),
                    "direct": str(direct_two_value(p)),
                    "territorial": str(distinct_territorial_value(m)),
                    "hybrid": str(one_reroute_hybrid_value(m, p)),
                    "winners": "|".join(restricted_winners(m, p)),
                }
            )
    return rows


def _svg(path: Path, rows: list[dict[str, Any]]) -> None:
    height = 78 + 30 * len(rows)
    content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="{height}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        "<style>text{font-family:monospace;fill:#172033}.h{font-size:18px;font-weight:700}"
        ".r{font-size:13px}</style>",
        '<text class="h" x="24" y="32">DD-001B exact restricted threshold samples</text>',
    ]
    for index, row in enumerate(rows):
        label = f"M={row['candidates']} p={row['accuracy']} {row['region']} winner={row['winners']}"
        content.append(f'<text class="r" x="24" y="{64 + 30 * index}">{label}</text>')
    content.append("</svg>")
    path.write_text("\n".join(content) + "\n", encoding="utf-8")


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
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-001_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"))

    certificates = []
    for raw_m in config["certificate_candidates"]:
        if time.monotonic() > deadline:
            raise RuntimeError("threshold certificate exceeded its time budget")
        result = certify_informative_envelope(int(raw_m))
        certificates.append(
            {
                "candidates": result.candidates,
                "signature_count": result.signature_count,
                "profile_count": result.profile_count,
                "hybrid_interval": [f"1/{result.candidates}", f"1/{result.candidates - 1}"],
                "direct_interval": [f"1/{result.candidates - 1}", "1"],
                "hybrid_interval_passed": result.hybrid_interval_passed,
                "direct_interval_passed": result.direct_interval_passed,
                "minimum_hybrid_margin": str(result.minimum_hybrid_margin),
                "minimum_direct_margin": str(result.minimum_direct_margin),
            }
        )
    _json(
        outputs / "threshold-certificate.json",
        {
            "schema_version": 1,
            "restricted_theorem": {
                "territorial": "p < 1/M",
                "one-reroute-hybrid": "1/M < p < 1/(M-1)",
                "direct": "p > 1/(M-1)",
            },
            "bounded_unrestricted_informative_certificates": certificates,
            "global_all_M_status": "conjectured for p>=1/M; certified only for listed M",
            "all_p_extension": "refuted",
        },
    )

    phase = _phase_rows(config)
    with (outputs / "restricted-phase-table.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(phase[0]))
        writer.writeheader()
        writer.writerows(phase)
    _svg(outputs / "restricted-phase-table.svg", phase)

    witnesses = []
    for item in config["known_witnesses"]:
        m, p, expected = (
            int(item["candidates"]),
            Fraction(str(item["accuracy"])),
            Fraction(str(item["expected"])),
        )
        hybrid_profile = one_reroute_hybrid_profile(m)
        formula = evaluate_formula(hybrid_profile, m, p)
        direct, normalization = evaluate_direct(hybrid_profile, m, p)
        signature_profile = tuple(signature_from_policy(policy) for policy in hybrid_profile)
        signature_optimum, _ = exact_signature_optimum_fast(m, p)
        raw_optimum = exhaustive_optimum(m, 2, p).value
        passed = (
            expected
            == one_reroute_hybrid_value(m, p)
            == formula
            == direct
            == signature_optimum
            == raw_optimum
            and normalization == 1
            and formula == evaluate_quadratic(signature_profile_polynomial(signature_profile), p)
        )
        witnesses.append(
            {
                "candidates": m,
                "accuracy": str(p),
                "expected": str(expected),
                "profile": [list(policy) for policy in hybrid_profile],
                "formula": str(formula),
                "direct_enumeration": str(direct),
                "signature_optimum": str(signature_optimum),
                "raw_optimum": str(raw_optimum),
                "normalization": str(normalization),
                "passed": bool(passed),
            }
        )
    _json(outputs / "known-witnesses.json", witnesses)

    anti = []
    for raw_m in config["raw_audit_candidates"]:
        m = int(raw_m)
        optimum, anti_profile = exact_signature_optimum_fast(m, Fraction(0))
        benchmark = max(
            direct_two_value(Fraction(0)),
            distinct_territorial_value(m),
            one_reroute_hybrid_value(m, Fraction(0)),
        )
        anti.append(
            {
                "candidates": m,
                "accuracy": "0",
                "unrestricted_optimum": str(optimum),
                "three_family_benchmark": str(benchmark),
                "strict_counterexample": optimum > benchmark,
                "signature_profile": [
                    [[count, fixed] for count, fixed in signature] for signature in anti_profile
                ],
            }
        )
    _json(outputs / "anti-informative-counterexamples.json", anti)

    elapsed = time.monotonic() - start
    validation = {
        "passed": bool(
            not dirty
            and all(
                row["hybrid_interval_passed"] and row["direct_interval_passed"]
                for row in certificates
            )
            and all(row["passed"] for row in witnesses)
            and all(row["strict_counterexample"] for row in anti)
            and elapsed <= float(config["time_budget_seconds"])
        ),
        "git_clean_at_start": not dirty,
        "continuous_informative_certificates_passed": all(
            row["hybrid_interval_passed"] and row["direct_interval_passed"] for row in certificates
        ),
        "known_witnesses_reproduced_by_raw_and_signature_enumeration": all(
            row["passed"] for row in witnesses
        ),
        "anti_informative_extension_refuted": all(row["strict_counterexample"] for row in anti),
        "global_all_M_informative_theorem_claimed": False,
        "elapsed_seconds": elapsed,
        "time_budget_seconds": config["time_budget_seconds"],
    }
    _json(run_dir / "validation.json", validation)
    _json(
        run_dir / "metrics.json",
        {
            "certified_M": [row["candidates"] for row in certificates],
            "certified_profile_count": sum(row["profile_count"] for row in certificates),
            "known_witness_count": len(witnesses),
            "phase_row_count": len(phase),
        },
    )
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\nvalidation_status={'passed' if validation['passed'] else 'failed'}\n"
    )
    (run_dir / "stderr.log").write_text("")
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
        root / "src/distributed_discovery/private_teams/model.py",
        root / "src/distributed_discovery/private_teams/optimize.py",
        root / "src/distributed_discovery/private_teams/signatures.py",
        root / "src/distributed_discovery/private_teams/thresholds.py",
        root / "src/distributed_discovery/private_teams/threshold_study.py",
    ]
    command = "make dd001-thresholds"
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
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": {"algorithm": None, "model": None},
        "outputs": output_hashes,
    }
    _json(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text(command + "\n")
    (run_dir / "reproduce.sh").write_text("#!/bin/sh\nset -eu\nexec make dd001-thresholds\n")
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-001B threshold run {run_id}\n\n"
        "Exact restricted theorem audit, bounded continuous unrestricted classification, "
        "and anti-informative counterexamples.\n"
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
