#!/usr/bin/env python3
"""Audit AO-0009 public contracts, classifier fixtures, and optional rehearsal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.fixed_batch_diagnostic import (
    CausalEvidence,
    classify_cause,
    validate_public_contracts,
)
from distributed_discovery.benchmark.agents_v1.fixed_batch_diagnostic_fixture import (
    run_exact_scale_synthetic_fixture,
)
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v3 import (
    run_synthetic_rehearsal,
)

ROOT = Path(__file__).resolve().parents[1]


def classifier_fixtures() -> tuple[dict[str, str], ...]:
    """Exercise every causal class with deterministic nonsecret evidence."""

    fixtures = {
        "provider-transport-terminal": CausalEvidence(
            selected_provider_error="timeout", selected_call_terminal=True
        ),
        "provider-http-terminal": CausalEvidence(
            selected_provider_error="provider-http-500", selected_call_terminal=True
        ),
        "protocol-contract-nonconformance": CausalEvidence(protocol_nonconformance_traces=1),
        "final-action-cardinality-failure": CausalEvidence(
            protocol_nonconformance_traces=1,
            invalid_final_cardinality_traces=1,
        ),
        "contamination-policy-trigger": CausalEvidence(
            protocol_nonconformance_traces=1,
            direct_or_probable_contamination_traces=1,
        ),
        "trace-encryption-or-persistence-failure": CausalEvidence(
            selected_trace_authenticated=False
        ),
        "response-ledger-append-failure": CausalEvidence(response_ledger_one_to_one=False),
        "cost-or-token-cap-guard": CausalEvidence(cap_guard=True),
        "pairing-completeness-failure": CausalEvidence(pairing_complete=False),
        "state-transition-or-completion-marker-failure": CausalEvidence(
            all_outputs_exist=True,
            fixed_full_batch_marker=False,
            safe_exception_code_persisted=True,
        ),
        "post-batch-verification-failure": CausalEvidence(
            fixed_full_batch_marker=True,
            post_batch_verification_failed=True,
        ),
        "unknown-within-retained-evidence": CausalEvidence(),
    }
    outcomes: list[dict[str, str]] = []
    for expected, evidence in fixtures.items():
        observed, actor, safe_code = classify_cause(evidence)
        if observed != expected:
            raise AssertionError(f"classifier fixture {expected} produced {observed}")
        outcomes.append(
            {
                "causal_class": observed,
                "actor": actor,
                "safe_error_code": safe_code,
                "status": "pass",
            }
        )
    integrity, actor, safe_code = classify_cause(CausalEvidence(integrity_ok=False))
    if integrity != "retained-state-integrity-mismatch-stop":
        raise AssertionError("integrity-stop fixture was not fail-closed")
    outcomes.append(
        {
            "causal_class": integrity,
            "actor": actor,
            "safe_error_code": safe_code,
            "status": "pass",
        }
    )
    return tuple(outcomes)


def audit(*, rehearsal: bool = False) -> dict[str, object]:
    contracts = validate_public_contracts(ROOT)
    fixtures = classifier_fixtures()
    result: dict[str, object] = {
        "task_id": "AO-0009",
        "status": "pass",
        "contracts": contracts,
        "classifier_fixtures": fixtures,
        "provider_calls": 0,
        "credential_reads": 0,
        "retained_private_state_reads": 0,
        "spend_usd": "0",
    }
    if rehearsal:
        exact_scale = run_exact_scale_synthetic_fixture(ROOT)
        full = run_synthetic_rehearsal(ROOT)
        if (
            full["status"] != "pass"
            or full["tasks"] != 50
            or full["runs"] != 500
            or full["exact_pairings_verified"] != 500
            or full["method_a_b_errors"] != 0
            or full["method_c_errors"] != 0
            or full["invalid_final_action_cardinalities"] != 0
            or full["incomplete_pairings"] != 0
            or full["contamination_findings"] != 0
            or full["metric_range_errors"] != 0
            or full["output_lock_verified"] is not True
        ):
            raise AssertionError("full 50-task/500-pairing rehearsal failed")
        result["exact_scale_diagnostic_fixture"] = exact_scale
        result["full_rehearsal"] = full
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rehearsal", action="store_true")
    args = parser.parse_args()
    print(json.dumps(audit(rehearsal=args.rehearsal), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
