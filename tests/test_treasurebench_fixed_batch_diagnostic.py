from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from distributed_discovery.benchmark.agents_v1 import fixed_batch_diagnostic as diagnostic
from distributed_discovery.benchmark.agents_v1.fixed_batch_diagnostic import (
    CausalEvidence,
    EnvelopeMetadata,
    RetainedFixedBatchDiagnostic,
    StructuralReconstruction,
    classify_cause,
    public_result,
    reconstruct_structure,
    run_read_only_fixed_batch_diagnostic,
    select_bounded_context,
    validate_public_contracts,
    validate_public_diagnostic,
    verify_response_ledger_correspondence,
    verify_trace_partition,
)
from distributed_discovery.benchmark.agents_v1.fixed_batch_diagnostic_fixture import (
    run_exact_scale_synthetic_fixture,
)

ROOT = Path(__file__).resolve().parents[1]


def _envelope(domain: str, index: int, object_class: str = "trace") -> EnvelopeMetadata:
    return EnvelopeMetadata(
        relative_path=f"encrypted-{object_class}s/{index}.sealed",
        object_name=f"{object_class}/{index}.sealed",
        object_class=object_class,
        mode="0600",
        size=100,
        mtime_ns=index,
        domain=domain,
        nonce_bytes=12,
        ciphertext_sha256=f"sha256:{index:064x}",
        associated_data_sha256=f"sha256:{index + 1:064x}",
        locked_commitment=f"sha256:{index + 2:064x}",
    )


def _record(
    sequence: int,
    *,
    key: str,
    attempt: int = 0,
    status: str = "success",
    error: str | None = None,
    provider: str = "OpenAI",
) -> dict[str, object]:
    return {
        "sequence": sequence,
        "event_type": "provider-call",
        "idempotency_key": f"{key}/attempt-{attempt}",
        "call_key": key,
        "transport_attempt": attempt,
        "status": status,
        "error_class": error,
        "provider": provider,
        "input_tokens": 1,
        "output_tokens": 1,
        "cost_usd": "0.01",
    }


def _reconstruction() -> StructuralReconstruction:
    return StructuralReconstruction(
        planned_logical_calls=3016,
        actual_attempts=3067,
        unique_logical_calls=3016,
        completed_logical_calls=3016,
        recovered_attempts_by_provider={"OpenAI": 1, "Anthropic": 0},
        terminal_attempts_by_provider={"OpenAI": 0, "Anthropic": 0},
        completed_private_pairings=500,
        private_prefix_pairings=50,
        fixed_full_batch_pairings=450,
        public_canary_traces=2,
        all_500_pairing_records_exist=True,
        fixed_full_batch_completion_marker=False,
        exact_last_durable_stage=(
            "fixed-full-batch-quarantined-after-prefix-before-completion-marker"
        ),
        all_selected_run_outputs_exist=True,
    )


def _diagnosis() -> RetainedFixedBatchDiagnostic:
    return RetainedFixedBatchDiagnostic(
        task_id="AO-0009",
        source_task_id="AO-0008",
        campaign_id=diagnostic.CAMPAIGN_ID,
        batch_id=diagnostic.BATCH_ID,
        execution_commit=diagnostic.EXECUTION_COMMIT,
        output_lock_verified_within_allowlist=True,
        output_lock_commitment=diagnostic.EXPECTED_OUTPUT_LOCK,
        locked_objects=3576,
        inventory_verified=True,
        append_only_ledgers_verified=True,
        retained_state_mutated=False,
        reconstruction=_reconstruction(),
        selected_call_key_hash=f"sha256:{'a' * 64}",
        selected_attempt_records=1,
        bounded_neighbor_records=4,
        selected_response_objects=1,
        selected_trace_objects=1,
        selected_trace_domain_hash=f"sha256:{'b' * 64}",
        response_ledger_correspondence_exact=True,
        cap_guards_triggered=False,
        authenticated_fixed_batch_traces=450,
        protocol_nonconformance_traces=0,
        invalid_final_cardinality_traces=0,
        direct_or_probable_contamination_traces=0,
        parse_or_schema_repair_exhaustion_traces=0,
        aggregate_retry_count=0,
        private_trace_identity_hashes=tuple(f"sha256:{index:064x}" for index in range(450)),
        exception_stage="fixed-full-batch",
        safe_error_code="bounded-evidence-unknown",
        causal_class="unknown-within-retained-evidence",
        causal_actor="undetermined",
        private_content_published=False,
        operational_key_retained=False,
        provider_calls=0,
        credential_reads=0,
        spend_usd="0",
        private_paths_disclosed=False,
    )


def test_public_contracts_freeze_exact_taxonomy_and_ceilings() -> None:
    observed = validate_public_contracts(ROOT)
    assert observed["taxonomy_classes"] == 15
    assert observed["response_envelopes"] == 3067
    assert observed["trace_envelopes"] == 502
    assert observed["aggregate_fixed_batch_trace_decryptions"] == 450
    assert observed["selected_encrypted_objects_maximum"] == 452
    assert observed["private_state_reads"] == 0


@pytest.mark.parametrize(
    ("evidence", "expected"),
    [
        (
            CausalEvidence(
                selected_provider_error="timeout",
                selected_call_terminal=True,
            ),
            "provider-transport-terminal",
        ),
        (
            CausalEvidence(
                selected_provider_error="provider-http-500",
                selected_call_terminal=True,
            ),
            "provider-http-terminal",
        ),
        (
            CausalEvidence(protocol_nonconformance_traces=1),
            "protocol-contract-nonconformance",
        ),
        (
            CausalEvidence(
                protocol_nonconformance_traces=1,
                invalid_final_cardinality_traces=1,
            ),
            "final-action-cardinality-failure",
        ),
        (
            CausalEvidence(
                protocol_nonconformance_traces=1,
                invalid_final_cardinality_traces=1,
                direct_or_probable_contamination_traces=1,
            ),
            "contamination-policy-trigger",
        ),
        (
            CausalEvidence(
                all_outputs_exist=True,
                safe_exception_code_persisted=True,
            ),
            "state-transition-or-completion-marker-failure",
        ),
        (CausalEvidence(), "unknown-within-retained-evidence"),
    ],
)
def test_classifier_preserves_causal_distinctions(evidence: CausalEvidence, expected: str) -> None:
    assert classify_cause(evidence)[0] == expected


def test_reconstruction_proves_all_500_pairing_records_without_content() -> None:
    traces = [
        _envelope(f"fresh-raw-trace/public-canary/model-{index}", index) for index in range(2)
    ]
    traces.extend(
        _envelope(
            f"raw-trace/private-prefix/model/task-{index}/architecture",
            index + 2,
        )
        for index in range(50)
    )
    traces.extend(
        _envelope(
            f"raw-trace/fixed-full-batch/model/task-{index}/architecture",
            index + 52,
        )
        for index in range(450)
    )
    records = (
        _record(1, key="call-a", status="error", error="timeout"),
        _record(2, key="call-a", attempt=1),
        _record(3, key="call-b", provider="Anthropic"),
    )
    observed = reconstruct_structure(
        records,
        {
            "fixed_full_batch_complete": False,
            "quarantine_stage": "fixed-full-batch",
        },
        traces,
        (
            {
                "operation": "fresh-private-ten-percent-prefix-pass",
            },
        ),
    )
    assert observed.actual_attempts == 3
    assert observed.unique_logical_calls == 2
    assert observed.completed_logical_calls == 2
    assert observed.recovered_attempts_by_provider["OpenAI"] == 1
    assert observed.completed_private_pairings == 500
    assert observed.all_500_pairing_records_exist is True
    assert observed.fixed_full_batch_completion_marker is False


def test_bounded_context_selects_unique_terminal_and_four_neighbors_maximum() -> None:
    records = (
        _record(1, key="call-a"),
        _record(2, key="call-b"),
        _record(3, key="call-terminal", status="error", error="provider-http-400"),
        _record(4, key="call-c"),
        {
            "sequence": 5,
            "event_type": "batch-quarantine",
            "stage": "fixed-full-batch",
        },
        {"sequence": 6, "event_type": "provider-phase-closed"},
    )
    key, selected, neighbors = select_bounded_context(records)
    assert key == "call-terminal"
    assert len(selected) == 1
    assert len(neighbors) == 4
    assert tuple(record["sequence"] for record in neighbors) == (1, 2, 4, 5)


def test_bounded_context_rejects_more_than_two_selected_attempts() -> None:
    records = tuple(
        _record(
            index + 1,
            key="call-a",
            attempt=index,
            status="error",
            error="timeout",
        )
        for index in range(3)
    )
    with pytest.raises(PermissionError, match="two-attempt"):
        select_bounded_context(records)


def test_public_result_excludes_selected_private_identifiers() -> None:
    observed = public_result(_diagnosis())
    assert observed["causal_class"] == "unknown-within-retained-evidence"
    assert observed["all_500_pairing_records_exist"] is True
    assert "selected_call_key_hash" not in observed
    assert "selected_trace_domain_hash" not in observed
    assert "private_trace_identity_hashes" not in observed
    assert "recovered_attempts_by_provider" not in observed
    validate_public_diagnostic(observed)


def test_public_redaction_rejects_private_paths_and_performance() -> None:
    with pytest.raises(ValueError, match="forbidden"):
        validate_public_diagnostic({"task_level_metrics": {"score": 1}})
    with pytest.raises(ValueError, match="host path"):
        validate_public_diagnostic({"detail": "/Users/example/private"})
    for leaked in (
        {"raw_output": "private"},
        {"model": "snapshot"},
        {"architecture_id": "isolated"},
        {"trace_identity_hashes": ["sha256:" + "a" * 64]},
    ):
        with pytest.raises(ValueError, match="forbidden"):
            validate_public_diagnostic(leaked)


def test_prohibited_custody_and_key_reads_fail_closed(tmp_path: Path) -> None:
    for name in ("seed.bin", "task-key.bin", "answer-key.bin", "task-custody.json"):
        path = tmp_path / name
        path.write_bytes(b"x" * 32)
        path.chmod(0o600)
        with pytest.raises(PermissionError, match="non-allowlisted"):
            diagnostic._secure_read(tmp_path, name, allowed=frozenset({name}))


def test_one_use_marker_precedes_access_and_second_invocation_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "diagnostic-output"
    retained = tmp_path / "retained"
    retained.mkdir()
    observed_marker: list[bool] = []

    monkeypatch.setattr(
        diagnostic,
        "load_diagnostic_authorization",
        lambda _repo: {"commit": "execution-commit"},
    )
    monkeypatch.setattr(diagnostic, "diagnostic_output_root", lambda: output)
    monkeypatch.setattr(diagnostic, "private_state_root", lambda: retained)

    def inspect(_repo: Path, _root: Path) -> RetainedFixedBatchDiagnostic:
        observed_marker.append((output / "read-intent.json").is_file())
        return _diagnosis()

    monkeypatch.setattr(diagnostic, "inspect_retained_fixed_batch", inspect)
    first = run_read_only_fixed_batch_diagnostic(ROOT)
    assert first["private_read_authority_closed"] is True
    assert observed_marker == [True]
    assert (output / "read-intent.json").stat().st_mode & 0o777 == 0o600
    assert (output / "diagnostic.json").stat().st_mode & 0o777 == 0o600
    with pytest.raises(PermissionError, match="already consumed"):
        run_read_only_fixed_batch_diagnostic(ROOT)


def test_in_read_integrity_failure_writes_redacted_stop_and_consumes_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "integrity-stop"
    retained = tmp_path / "retained"
    retained.mkdir()
    monkeypatch.setattr(
        diagnostic,
        "load_diagnostic_authorization",
        lambda _repo: {"commit": "execution-commit"},
    )
    monkeypatch.setattr(diagnostic, "diagnostic_output_root", lambda: output)
    monkeypatch.setattr(diagnostic, "private_state_root", lambda: retained)
    monkeypatch.setattr(
        diagnostic,
        "inspect_retained_fixed_batch",
        lambda _repo, _root: (_ for _ in ()).throw(ValueError("private detail omitted")),
    )
    observed = run_read_only_fixed_batch_diagnostic(ROOT)
    assert observed["status"] == "stop"
    assert observed["causal_class"] == "retained-state-integrity-mismatch-stop"
    assert observed["private_read_authority_closed"] is True
    assert "private detail omitted" not in json.dumps(observed)
    assert (output / "diagnostic.json").is_file()
    with pytest.raises(PermissionError, match="already consumed"):
        run_read_only_fixed_batch_diagnostic(ROOT)


def test_hash_chained_ledger_rejects_mutation() -> None:
    previous = "GENESIS"
    lines: list[bytes] = []
    for sequence in range(1, 4):
        value: dict[str, object] = {
            "sequence": sequence,
            "previous_hash": previous,
            "event_type": "provider-call",
            "call_key": f"call-{sequence}",
        }
        value["record_hash"] = (
            f"sha256:{hashlib.sha256(diagnostic.canonical_json(value)).hexdigest()}"
        )
        previous = str(value["record_hash"])
        lines.append(diagnostic.canonical_json(value))
    assert len(diagnostic._validate_ledger(b"\n".join(lines) + b"\n")) == 3
    corrupted = json.loads(lines[1])
    corrupted["call_key"] = "changed"
    lines[1] = diagnostic.canonical_json(corrupted)
    with pytest.raises(ValueError, match="hash mismatch"):
        diagnostic._validate_ledger(b"\n".join(lines) + b"\n")


def _exact_attempt_fixture() -> tuple[list[dict[str, object]], list[EnvelopeMetadata]]:
    records: list[dict[str, object]] = []
    envelopes: list[EnvelopeMetadata] = []
    for index in range(3067):
        key = f"call-{index:064x}"
        records.append(_record(index + 1, key=key))
        envelopes.append(
            _envelope(
                f"provider-response/{key}/attempt-0",
                index,
                object_class="response",
            )
        )
    return records, envelopes


def test_response_correspondence_rejects_substitution_orphan_and_duplicate() -> None:
    records, envelopes = _exact_attempt_fixture()
    assert verify_response_ledger_correspondence(records, envelopes) is True

    substituted = list(envelopes)
    substituted[-1] = _envelope(
        "provider-response/call-orphan/attempt-0",
        len(substituted),
        object_class="response",
    )
    assert verify_response_ledger_correspondence(records, substituted) is False

    orphaned = [*envelopes, _envelope("provider-response/call-orphan/attempt-0", 4000, "response")]
    assert verify_response_ledger_correspondence(records, orphaned) is False

    duplicated = list(envelopes)
    duplicated[-1] = duplicated[0]
    assert verify_response_ledger_correspondence(records, duplicated) is False

    conflicting = list(records)
    conflicting[-1] = {**conflicting[-1], "idempotency_key": "conflict/attempt-0"}
    with pytest.raises(ValueError, match="conflicts"):
        verify_response_ledger_correspondence(conflicting, envelopes)


def test_trace_partition_rejects_one_missing_domain() -> None:
    traces = [
        *(_envelope(f"fresh-raw-trace/public-canary/model-{index}", index) for index in range(2)),
        *(
            _envelope(f"raw-trace/private-prefix/model/task-{index}/architecture", index + 2)
            for index in range(50)
        ),
        *(
            _envelope(
                f"raw-trace/fixed-full-batch/model/task-{index}/architecture",
                index + 52,
            )
            for index in range(450)
        ),
    ]
    assert verify_trace_partition(traces) is True
    assert verify_trace_partition(traces[:-1]) is False


@pytest.mark.parametrize("event_kind", ["contamination", "protocol"])
@pytest.mark.parametrize("event_index", [0, 225, 449])
def test_exact_scale_aggregate_event_is_found_at_any_trace_position(
    event_kind: str,
    event_index: int,
) -> None:
    observed = run_exact_scale_synthetic_fixture(
        ROOT,
        event_kind=event_kind,
        event_index=event_index,
    )
    expected = (
        "contamination-policy-trigger"
        if event_kind == "contamination"
        else "protocol-contract-nonconformance"
    )
    assert observed["causal_class"] == expected
    assert observed["selected_trace_objects"] == 450
    assert observed["authenticated_fixed_batch_traces"] == 450
