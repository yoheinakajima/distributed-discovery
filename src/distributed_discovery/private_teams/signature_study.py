"""Execute the DD-001A signature-reduction audit and bounded canonical cost analysis."""

from __future__ import annotations

import csv
import hashlib
import itertools
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
from distributed_discovery.private_teams.optimize import exhaustive_optimum, reduced_profile_count
from distributed_discovery.private_teams.signature_certificate import verify_certificate
from distributed_discovery.private_teams.signatures import (
    Signature,
    SignatureProfile,
    all_feasible_signatures,
    evaluate_signatures_reference,
    evaluate_signatures_scaled,
    exhaustive_signature_optimum,
    feasible_signature_count,
    raw_policy_multiplicities,
    reduced_feasibility,
    reference_feasibility,
    signature_from_policy,
    signature_reduced_profile_count,
    target_orbit_signature_count,
)
from distributed_discovery.validation.bootstrap import repository_root

CONFIG_RELATIVE = Path("studies/DD-001-private-information-teams/configs/signature-certificate.yml")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _sanitize_package_snapshot(lines: Iterable[str]) -> list[str]:
    return sorted(
        line for line in lines if not line.lower().startswith("distributed-discovery @ file:")
    )


def _package_snapshot(root: Path) -> list[str]:
    lines = subprocess.check_output(["uv", "pip", "freeze"], cwd=root, text=True).splitlines()
    return _sanitize_package_snapshot(lines)


def _signature_json(signature: Signature) -> list[list[int]]:
    return [[count, fixed] for count, fixed in signature]


def _signature_profile_json(profile: SignatureProfile) -> list[list[list[int]]]:
    return [_signature_json(signature) for signature in profile]


def _reconstruct_profile(profile: SignatureProfile) -> Profile:
    reconstructed = []
    for signature in profile:
        result = reference_feasibility(signature)
        if not result.feasible or result.policy is None:
            raise RuntimeError(f"could not reconstruct feasible signature: {result.reason}")
        reconstructed.append(result.policy)
    return tuple(reconstructed)


def _comparison_grid(root: Path, run_id: str) -> dict[str, dict[str, str]]:
    path = root / "results/verified" / run_id / "outputs/tiny-phase-grid.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["case"]: row for row in csv.DictReader(handle)}


def _complexity(config: dict[str, Any]) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    limit = int(config["max_signature_profiles_per_case"])
    for case in config["tiny_cases"]:
        candidates = int(case["candidates"])
        searchers = int(case["searchers"])
        signature_profiles = signature_reduced_profile_count(candidates, searchers)
        if signature_profiles > limit:
            raise RuntimeError(
                f"configured case M={candidates}, N={searchers} exceeds signature cost limit"
            )
        rows.append(
            {
                "candidates": candidates,
                "searchers": searchers,
                "raw_policies_per_agent": candidates**candidates,
                "feasible_signatures": feasible_signature_count(candidates),
                "raw_agent_multisets": reduced_profile_count(candidates, searchers),
                "signature_agent_multisets": signature_profiles,
                "accuracy_count": len(case["accuracies"]),
            }
        )
    return rows


def _small_feasibility_audit(candidates: int) -> dict[str, Any]:
    raw = raw_policy_multiplicities(candidates)
    generated = set(all_feasible_signatures(candidates))
    reference_equals_reduced = True
    all_reconstructions_exact = True
    local_candidate_count = 0
    for counts in itertools.product(range(candidates + 1), repeat=candidates):
        if sum(counts) != candidates:
            continue
        for fixed in itertools.product((0, 1), repeat=candidates):
            signature = tuple(zip(counts, fixed, strict=True))
            reference = reference_feasibility(signature)
            reduced = reduced_feasibility(signature)
            local_candidate_count += 1
            reference_equals_reduced &= reference.feasible == reduced.feasible
            if reference.feasible:
                if reference.policy is None:
                    all_reconstructions_exact = False
                else:
                    all_reconstructions_exact &= (
                        signature_from_policy(reference.policy) == signature
                    )
    return {
        "candidates": candidates,
        "raw_policy_count": candidates**candidates,
        "locally_admissible_candidate_count": local_candidate_count,
        "feasible_signature_count": len(generated),
        "formula_signature_count": feasible_signature_count(candidates),
        "target_orbit_count": target_orbit_signature_count(candidates),
        "reference_equals_reduced": reference_equals_reduced,
        "raw_equals_generated": generated == set(raw),
        "all_reconstructions_exact": all_reconstructions_exact,
        "raw_signature_multiplicity_sum": sum(raw.values()),
    }


def _certificate(config: dict[str, Any], audits: list[dict[str, Any]]) -> dict[str, Any]:
    canonical = config["canonical"]
    candidates = int(canonical["candidates"])
    searchers = int(canonical["searchers"])
    signature_count = feasible_signature_count(candidates)
    agent_multisets = signature_reduced_profile_count(candidates, searchers)
    minimum_bytes = agent_multisets * candidates * 8
    return {
        "schema_version": 1,
        "study_id": "DD-001",
        "result_type": "lossless-structural-reduction",
        "objective_theorem": "policy profiles with identical signatures have identical discovery",
        "feasibility_theorem": (
            "local constraints plus singleton Hall residual bounds are necessary and sufficient"
        ),
        "canonical": {
            "candidates": candidates,
            "searchers": searchers,
            "accuracy": str(canonical["accuracy"]),
            "raw_policies_per_agent": candidates**candidates,
            "feasible_signatures_before_target_quotient": signature_count,
            "individual_signature_target_orbits": target_orbit_signature_count(candidates),
            "agent_multiset_search_without_target_quotient": agent_multisets,
            "minimum_failure_vector_bytes": minimum_bytes,
            "root_branching_factor": signature_count,
            "global_target_symmetry_factor_upper_bound": math.factorial(candidates),
            "individual_orbit_multiset_search_is_lossless": False,
            "global_optimum_status": "unresolved",
            "termination_reason": (
                "state-space audit proves naive exact signature enumeration infeasible"
            ),
        },
        "small_feasibility_audits": audits,
    }


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
    deadline = time.monotonic() + float(config["time_budget_seconds"])
    comparison = _comparison_grid(root, str(config["comparison_run_id"]))

    audits = [
        _small_feasibility_audit(int(candidates))
        for candidates in config["feasibility_audit_candidates"]
    ]
    _write_json(output_dir / "feasibility-audits.json", audits)

    phase_rows: list[dict[str, Any]] = []
    winners: dict[str, Any] = {}
    all_optima = True
    all_ties = True
    all_normalized = True
    all_bounds = True
    all_policy_benchmarks = True
    for case in config["tiny_cases"]:
        candidates = int(case["candidates"])
        searchers = int(case["searchers"])
        for accuracy_text in case["accuracies"]:
            if time.monotonic() > deadline:
                raise RuntimeError("configured time budget exhausted during signature grid")
            accuracy = Fraction(str(accuracy_text))
            signature_result = exhaustive_signature_optimum(candidates, searchers, accuracy)
            raw_result = exhaustive_optimum(candidates, searchers, accuracy)
            profile = _reconstruct_profile(signature_result.profile)
            raw_formula = evaluate_formula(profile, candidates, accuracy)
            raw_direct, normalization = evaluate_direct(profile, candidates, accuracy)
            reference_value = evaluate_signatures_reference(signature_result.profile, accuracy)
            scaled_value, failure_sum, scaled_denominator = evaluate_signatures_scaled(
                signature_result.profile, accuracy
            )
            direct = direct_value(searchers, accuracy)
            territorial = territorial_value(candidates, searchers)
            pooled = pooled_planner_value(candidates, searchers, accuracy)
            direct_signature = tuple(
                signature_from_policy(policy) for policy in direct_profile(candidates, searchers)
            )
            territorial_signature = tuple(
                signature_from_policy(policy)
                for policy in territorial_profile(candidates, searchers)
            )
            direct_signature_value, _, _ = evaluate_signatures_scaled(direct_signature, accuracy)
            territorial_signature_value, _, _ = evaluate_signatures_scaled(
                territorial_signature, accuracy
            )
            key = f"M{candidates}_N{searchers}_p{accuracy.numerator}-{accuracy.denominator}"
            previous = comparison[key]
            optimum_match = (
                signature_result.value
                == raw_result.value
                == raw_formula
                == raw_direct
                == reference_value
                == scaled_value
                == Fraction(previous["optimum_fraction"])
            )
            ties_match = signature_result.raw_policy_multiset_ties == raw_result.ties
            all_optima &= optimum_match
            all_ties &= ties_match
            all_normalized &= normalization == 1
            all_bounds &= direct <= signature_result.value <= pooled
            all_policy_benchmarks &= (
                direct_signature_value == direct and territorial_signature_value == territorial
            )
            winners[key] = {
                "signature_profile": _signature_profile_json(signature_result.profile),
                "reconstructed_profile": [list(policy) for policy in profile],
                "scaled_failure_sum": failure_sum,
                "scaled_objective_denominator": scaled_denominator,
                "value_fraction": str(signature_result.value),
            }
            phase_rows.append(
                {
                    "case": key,
                    "candidates": candidates,
                    "searchers": searchers,
                    "accuracy": str(accuracy),
                    "feasible_signature_count": signature_result.signature_count,
                    "signature_profile_count": signature_result.reduced_profile_count,
                    "raw_profile_count": raw_result.reduced_profile_count,
                    "optimum_fraction": str(signature_result.value),
                    "direct_fraction": str(direct),
                    "territorial_fraction": str(territorial),
                    "pooled_fraction": str(pooled),
                    "signature_tie_count": signature_result.signature_ties,
                    "reconciled_raw_tie_count": signature_result.raw_policy_multiset_ties,
                    "raw_tie_count": raw_result.ties,
                    "all_evaluators_match": optimum_match,
                    "raw_ties_reconciled": ties_match,
                    "normalization_exact": normalization == 1,
                }
            )

    _write_csv(output_dir / "tiny-signature-grid.csv", phase_rows, list(phase_rows[0]))
    _write_json(output_dir / "optimal-signatures.json", winners)
    certificate = _certificate(config, audits)
    _write_json(output_dir / "reduction-certificate.json", certificate)
    certificate_verification = verify_certificate(certificate)
    _write_json(output_dir / "certificate-verification.json", certificate_verification)

    canonical = config["canonical"]
    canonical_accuracy = Fraction(str(canonical["accuracy"]))
    canonical_direct = direct_value(int(canonical["searchers"]), canonical_accuracy)
    canonical_summary = {
        **certificate["canonical"],
        "direct_fraction": str(canonical_direct),
        "direct_decimal": f"{float(canonical_direct):.12f}",
        "pooled_planner_numerical_upper": canonical["pooled_planner_numerical_upper"],
        "certified_interval": {
            "lower_fraction": str(canonical_direct),
            "upper_numerical_benchmark": canonical["pooled_planner_numerical_upper"],
            "upper_is_private_team_certificate": False,
        },
    }
    _write_json(output_dir / "canonical-state-space.json", canonical_summary)

    known_hybrid = next(row for row in phase_rows if row["case"] == "M3_N2_p2-5")
    validation = {
        "passed": bool(
            all(audit["reference_equals_reduced"] for audit in audits)
            and all(audit["raw_equals_generated"] for audit in audits)
            and all(audit["all_reconstructions_exact"] for audit in audits)
            and all_optima
            and all_ties
            and all_normalized
            and all_bounds
            and all_policy_benchmarks
            and certificate_verification["passed"]
            and Fraction(str(known_hybrid["optimum_fraction"])) == Fraction(7, 10)
            and canonical_direct == Fraction(str(canonical["direct_fraction"]))
        ),
        "signature_objective_lossless_on_grid": all_optima,
        "reference_equals_scaled_on_grid": all_optima,
        "reference_equals_reduced_feasibility": all(
            audit["reference_equals_reduced"] for audit in audits
        ),
        "raw_equals_generated_feasible_signatures": all(
            audit["raw_equals_generated"] for audit in audits
        ),
        "all_reconstructions_exact": all(audit["all_reconstructions_exact"] for audit in audits),
        "all_21_prior_optima_reproduced": all_optima and len(phase_rows) == 21,
        "raw_tie_counts_reconciled": all_ties,
        "probability_normalization_exact": all_normalized,
        "direct_and_territorial_policies_verified": all_policy_benchmarks,
        "direct_lower_and_pooled_upper_relations_verified": all_bounds,
        "known_hybrid_witness_reproduced": Fraction(str(known_hybrid["optimum_fraction"]))
        == Fraction(7, 10),
        "certificate_verification_passed": certificate_verification["passed"],
        "canonical_global_optimality_claimed": False,
        "canonical_outcome": canonical["outcome_scope"],
        "termination_reason": "completed-lossless-reduction-audit-and-bounded-state-space-analysis",
        "elapsed_seconds": time.monotonic() - (deadline - float(config["time_budget_seconds"])),
        "time_budget_seconds": config["time_budget_seconds"],
    }
    _write_json(run_dir / "validation.json", validation)
    _write_json(
        run_dir / "metrics.json",
        {
            "tiny_case_count": len(phase_rows),
            "small_feasibility_audit_count": len(audits),
            "canonical": canonical_summary,
        },
    )
    (run_dir / "stdout.log").write_text(
        "\n".join(
            [
                f"run_id={run_id}",
                f"tiny_cases={len(phase_rows)}",
                f"feasible_signatures_M16={canonical_summary['feasible_signatures_before_target_quotient']}",
                f"target_orbits_M16={canonical_summary['individual_signature_target_orbits']}",
                f"agent_multisets_M16_N8={canonical_summary['agent_multiset_search_without_target_quotient']}",
                "canonical_global_optimum=unresolved",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
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
    command = "make dd001-signatures"
    input_paths = [
        config_path,
        root / "src/distributed_discovery/private_teams/model.py",
        root / "src/distributed_discovery/private_teams/optimize.py",
        root / "src/distributed_discovery/private_teams/signatures.py",
        root / "src/distributed_discovery/private_teams/signature_certificate.py",
        root / "src/distributed_discovery/private_teams/signature_study.py",
        root
        / "results/verified"
        / str(config["comparison_run_id"])
        / "outputs/tiny-phase-grid.csv",
    ]
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
        "input_hashes": {str(path.relative_to(root)): _sha256(path) for path in input_paths},
        "random_seeds": {"algorithm": None, "model": None},
        "outputs": output_hashes,
    }
    _write_json(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd001-signatures\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-001A signature run `{run_id}`\n\n"
        "Lossless signature/feasibility audit, exact reproduction of the 21-case tiny grid, "
        "and bounded canonical state-space measurement. The canonical global optimum remains "
        "unresolved.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    print(
        "canonical outcome=lossless structural reduction; "
        f"signature_count={canonical_summary['feasible_signatures_before_target_quotient']}"
    )
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
