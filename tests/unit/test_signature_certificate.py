from copy import deepcopy

from distributed_discovery.private_teams.signature_certificate import verify_certificate
from distributed_discovery.private_teams.signatures import (
    feasible_signature_count,
    signature_reduced_profile_count,
    target_orbit_signature_count,
)


def _certificate() -> dict[str, object]:
    candidates = 3
    searchers = 2
    agent_multisets = signature_reduced_profile_count(candidates, searchers)
    audit = {
        "candidates": candidates,
        "raw_policy_count": candidates**candidates,
        "feasible_signature_count": feasible_signature_count(candidates),
        "target_orbit_count": target_orbit_signature_count(candidates),
        "reference_equals_reduced": True,
        "raw_equals_generated": True,
        "all_reconstructions_exact": True,
    }
    return {
        "schema_version": 1,
        "study_id": "DD-001",
        "result_type": "lossless-structural-reduction",
        "canonical": {
            "candidates": candidates,
            "searchers": searchers,
            "raw_policies_per_agent": candidates**candidates,
            "feasible_signatures_before_target_quotient": feasible_signature_count(candidates),
            "individual_signature_target_orbits": target_orbit_signature_count(candidates),
            "agent_multiset_search_without_target_quotient": agent_multisets,
            "minimum_failure_vector_bytes": agent_multisets * candidates * 8,
            "global_optimum_status": "unresolved",
        },
        "small_feasibility_audits": [audit],
    }


def test_certificate_verifier_accepts_exact_counts() -> None:
    assert verify_certificate(_certificate())["passed"] is True


def test_certificate_verifier_detects_corruption() -> None:
    corrupted = deepcopy(_certificate())
    canonical = corrupted["canonical"]
    assert isinstance(canonical, dict)
    canonical["feasible_signatures_before_target_quotient"] = 1
    result = verify_certificate(corrupted)
    assert result["passed"] is False
    assert "canonical feasible_signatures_before_target_quotient mismatch" in result["errors"]
