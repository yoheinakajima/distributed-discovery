"""Independent checker for the finite DD-001 signature-reduction certificate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from distributed_discovery.private_teams.signatures import (
    feasible_signature_count,
    signature_reduced_profile_count,
    target_orbit_signature_count,
)


def verify_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if certificate.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if certificate.get("study_id") != "DD-001":
        errors.append("study_id must equal DD-001")
    if certificate.get("result_type") != "lossless-structural-reduction":
        errors.append("result_type must identify the structural reduction")

    canonical = certificate.get("canonical")
    if not isinstance(canonical, dict):
        errors.append("canonical record is missing")
    else:
        candidates = int(canonical.get("candidates", -1))
        searchers = int(canonical.get("searchers", -1))
        if candidates >= 2 and searchers >= 1:
            expected = {
                "raw_policies_per_agent": candidates**candidates,
                "feasible_signatures_before_target_quotient": feasible_signature_count(candidates),
                "individual_signature_target_orbits": target_orbit_signature_count(candidates),
                "agent_multiset_search_without_target_quotient": signature_reduced_profile_count(
                    candidates, searchers
                ),
            }
            for key, value in expected.items():
                if canonical.get(key) != value:
                    errors.append(f"canonical {key} mismatch")
            minimum_bytes = (
                expected["agent_multiset_search_without_target_quotient"] * candidates * 8
            )
            if canonical.get("minimum_failure_vector_bytes") != minimum_bytes:
                errors.append("canonical minimum_failure_vector_bytes mismatch")
        else:
            errors.append("canonical dimensions are invalid")
        if canonical.get("global_optimum_status") != "unresolved":
            errors.append("certificate must leave the canonical global optimum unresolved")

    audits = certificate.get("small_feasibility_audits")
    if not isinstance(audits, list) or not audits:
        errors.append("small feasibility audits are missing")
    else:
        for audit in audits:
            candidates = int(audit.get("candidates", -1))
            if candidates < 2:
                errors.append("small feasibility audit has invalid dimension")
                continue
            if audit.get("raw_policy_count") != candidates**candidates:
                errors.append(f"M={candidates} raw policy count mismatch")
            if audit.get("feasible_signature_count") != feasible_signature_count(candidates):
                errors.append(f"M={candidates} feasible signature count mismatch")
            if audit.get("target_orbit_count") != target_orbit_signature_count(candidates):
                errors.append(f"M={candidates} target orbit count mismatch")
            for key in (
                "reference_equals_reduced",
                "raw_equals_generated",
                "all_reconstructions_exact",
            ):
                if audit.get(key) is not True:
                    errors.append(f"M={candidates} {key} is not true")

    return {
        "passed": not errors,
        "error_count": len(errors),
        "errors": errors,
        "checker": "independent-formula-and-small-audit-certificate-checker",
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m ...signature_certificate CERTIFICATE.json")
    path = Path(sys.argv[1])
    certificate = json.loads(path.read_text(encoding="utf-8"))
    result = verify_certificate(certificate)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
