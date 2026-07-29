"""Exact-scale nonsecret fixture for the AO-0009 bounded diagnostic."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.fixed_batch_diagnostic import (
    BATCH_ID,
    CAMPAIGN_ID,
    EXECUTION_COMMIT,
    EXPECTED_RESPONSES,
    inspect_retained_fixed_batch,
    public_result,
)
from distributed_discovery.benchmark.agents_v1.models import canonical_json, sha256_hex
from distributed_discovery.benchmark.agents_v1.pilot import seal_object


def _secure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)


def _write(path: Path, payload: bytes, *, mtime_ns: int | None = None) -> None:
    _secure_directory(path.parent)
    path.write_bytes(payload)
    path.chmod(0o600)
    if mtime_ns is not None:
        os.utime(path, ns=(mtime_ns, mtime_ns))


def _ledger(events: Sequence[Mapping[str, object]]) -> tuple[bytes, tuple[dict[str, object], ...]]:
    records: list[dict[str, object]] = []
    previous = "GENESIS"
    for sequence, event in enumerate(events, 1):
        record = {
            "sequence": sequence,
            "previous_hash": previous,
            **{str(name): value for name, value in event.items()},
        }
        record["record_hash"] = f"sha256:{sha256_hex(canonical_json(record))}"
        previous = str(record["record_hash"])
        records.append(record)
    return b"".join(canonical_json(record) + b"\n" for record in records), tuple(records)


def _envelope(
    *,
    domain: str,
    value: object,
    key: bytes,
    nonce_number: int,
) -> bytes:
    sealed = seal_object(
        domain=domain,
        value=value,
        key=key,
        nonce=nonce_number.to_bytes(12, "big"),
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    return (
        canonical_json(
            {
                "ciphertext_hex": sealed.ciphertext.hex(),
                "manifest": sealed.manifest(),
            }
        )
        + b"\n"
    )


def _trace(
    *,
    model: str,
    retry_count: int,
    errors: Sequence[str],
    visible_output: str = "",
) -> Mapping[str, object]:
    event: dict[str, object] = {
        "sequence": 0,
        "architecture_id": "isolated-private-agents",
        "agent_id": "AGENT-1",
        "round": 0,
        "visible_inputs": [],
        "visible_output": visible_output,
        "structured_action": None,
        "declared_tool_calls": [],
        "usage": {"input_tokens": 1, "output_tokens": 1, "cost_usd": "0.001"},
        "retry_count": retry_count,
        "errors": list(errors),
        "operational_metadata": {"model": model, "hidden_reasoning_stored": False},
    }
    event["event_hash"] = f"sha256:{sha256_hex(canonical_json(event))}"
    trace: dict[str, object] = {
        "schema_version": "treasurebench-agents-v1-trace-v1",
        "task_instance_commitment": f"sha256:{'1' * 64}",
        "architecture_id": "isolated-private-agents",
        "events": [event],
    }
    trace["trace_hash"] = f"sha256:{sha256_hex(canonical_json(trace))}"
    return trace


def _response(*, model: str) -> Mapping[str, object]:
    return {
        "raw_output": "{}",
        "usage": {"input_tokens": 1, "output_tokens": 1, "cost_usd": "0.001"},
        "error_class": None,
        "declared_tool_calls": [],
        "operational_metadata": {"model": model, "hidden_reasoning_stored": False},
    }


def run_exact_scale_synthetic_fixture(
    repo: Path,
    *,
    event_kind: str = "contamination",
    event_index: int = 0,
) -> Mapping[str, object]:
    """Exercise the live inspector at exact retained counts with disposable data."""

    if event_kind not in {"contamination", "protocol", "none"}:
        raise ValueError("unknown synthetic aggregate event")
    if not 0 <= event_index < 450:
        raise ValueError("synthetic aggregate event index is outside the full batch")

    with tempfile.TemporaryDirectory(prefix="ao0009-fixed-batch-diagnostic-") as temporary:
        root = Path(temporary) / "repair-confirmation-v3"
        _secure_directory(root)
        response_root = root / "encrypted-provider-responses"
        trace_root = root / "encrypted-traces"
        _secure_directory(response_root)
        _secure_directory(trace_root)
        key = bytes.fromhex("42" * 32)
        objects: dict[str, bytes] = {}

        events: list[Mapping[str, object]] = []
        for index in range(EXPECTED_RESPONSES):
            schema_retry = index >= 3016
            call_key = f"call-{index:064x}"
            provider = "OpenAI" if index % 2 == 0 else "Anthropic"
            model = "gpt-5.4-2026-03-05" if provider == "OpenAI" else "claude-sonnet-4-6"
            events.append(
                {
                    "event_type": "provider-call",
                    "idempotency_key": f"{call_key}/attempt-0",
                    "call_key": call_key,
                    "transport_attempt": 0,
                    "status": "success",
                    "provider": provider,
                    "model": model,
                    "input_tokens": 1,
                    "output_tokens": 1,
                    "cost_usd": "0.001",
                    "error_class": None,
                    "schema_retry": schema_retry,
                }
            )
            relative = f"{provider}/{call_key}-attempt-0.sealed.json"
            payload = _envelope(
                domain=f"provider-response/{call_key}/attempt-0",
                value=_response(model=model),
                key=key,
                nonce_number=index + 1,
            )
            _write(response_root / relative, payload)
            objects[f"provider-response/{relative}"] = payload
        events.extend(
            (
                {
                    "event_type": "batch-quarantine",
                    "status": "quarantined",
                    "stage": "fixed-full-batch",
                    "failure_class": "fixed-full-batch-failure",
                },
                {
                    "event_type": "provider-phase-closed",
                    "status": "locked",
                    "idempotency_key": "provider-phase-closed",
                },
            )
        )
        usage_payload, usage_records = _ledger(events)

        trace_specs: list[tuple[str, str, int, tuple[str, ...], str]] = []
        for model in ("gpt-5.4-2026-03-05", "claude-sonnet-4-6"):
            trace_specs.append((f"fresh-raw-trace/public-canary/{model}", model, 0, (), ""))
        for index in range(50):
            model = "gpt-5.4-2026-03-05" if index % 2 == 0 else "claude-sonnet-4-6"
            trace_specs.append(
                (
                    f"raw-trace/private-prefix/{model}/task-{index:03d}/architecture-{index % 5}",
                    model,
                    0,
                    (),
                    "",
                )
            )
        for index in range(450):
            model = "gpt-5.4-2026-03-05" if index % 2 == 0 else "claude-sonnet-4-6"
            errors: tuple[str, ...] = ()
            retry_count = 0
            visible_output = ""
            if index == event_index and event_kind == "contamination":
                visible_output = "answer_key from private holdout"
            elif index == event_index and event_kind == "protocol":
                errors = ("agent identity mismatch",)
            trace_specs.append(
                (
                    f"raw-trace/fixed-full-batch/{model}/task-{index:03d}/architecture-{index % 5}",
                    model,
                    retry_count,
                    errors,
                    visible_output,
                )
            )
        for index, (domain, model, retry_count, errors, visible_output) in enumerate(trace_specs):
            filename = f"{sha256_hex(domain.encode())}.sealed"
            payload = _envelope(
                domain=domain,
                value=_trace(
                    model=model,
                    retry_count=retry_count,
                    errors=errors,
                    visible_output=visible_output,
                ),
                key=key,
                nonce_number=10_000 + index,
            )
            _write(trace_root / filename, payload, mtime_ns=1_000_000 + index)
            objects[f"trace/{filename}"] = payload

        access_payload, _access_records = _ledger(
            (
                {
                    "event_type": "access",
                    "operation": "fresh-public-exact-route-canary-pass",
                    "private_material": False,
                },
                {
                    "event_type": "access",
                    "operation": "fresh-private-custody-created",
                    "private_material": True,
                },
                {
                    "event_type": "access",
                    "operation": "fresh-private-ten-percent-prefix-pass",
                    "private_material": True,
                },
            )
        )
        fixed = {
            "task-ciphertext": b"synthetic-opaque-task-ciphertext\n",
            "answer-ciphertext": b"synthetic-opaque-answer-ciphertext\n",
            "custody-manifest": b"synthetic-opaque-custody-manifest\n",
            "execution-identity": canonical_json(
                {
                    "campaign_id": CAMPAIGN_ID,
                    "batch_id": BATCH_ID,
                    "execution_commit": EXECUTION_COMMIT,
                }
            )
            + b"\n",
            "access-log": access_payload,
            "usage-cost-ledger": usage_payload,
            "provider-stage-state": canonical_json(
                {
                    "campaign_id": CAMPAIGN_ID,
                    "batch_id": BATCH_ID,
                    "public_canary_complete": True,
                    "custody_complete": True,
                    "private_prefix_complete": True,
                    "fixed_full_batch_complete": False,
                    "quarantined": True,
                    "quarantine_stage": "fixed-full-batch",
                    "quarantine_failure_class": "fixed-full-batch-failure",
                }
            )
            + b"\n",
        }
        fixed_paths = {
            "task-ciphertext": "task-custody.json",
            "answer-ciphertext": "answer-custody.json",
            "custody-manifest": "custody-manifest.json",
            "execution-identity": "execution-identity.json",
            "access-log": "access-log.jsonl",
            "usage-cost-ledger": "usage-cost-ledger.jsonl",
            "provider-stage-state": "provider-stage-state.json",
        }
        for name, payload in fixed.items():
            _write(root / fixed_paths[name], payload)
            objects[name] = payload

        lock: dict[str, object] = {
            "schema_version": "treasurebench-agents-v1-output-lock-v1",
            "campaign_id": CAMPAIGN_ID,
            "batch_id": BATCH_ID,
            "objects": {
                name: f"sha256:{sha256_hex(payload)}" for name, payload in sorted(objects.items())
            },
            "ledger_head": usage_records[-1]["record_hash"],
            "provider_phase_closed": True,
        }
        lock["lock_hash"] = f"sha256:{sha256_hex(canonical_json(lock))}"
        _write(root / "output-lock.json", canonical_json(lock) + b"\n")
        _write(root / "manifest.json", b"synthetic-opaque-private-manifest\n")
        _write(root / "redacted-summary.json", b"synthetic-opaque-redacted-summary\n")
        for name, value in (
            ("operational-key.bin", key),
            ("seed.bin", bytes.fromhex("11" * 32)),
            ("task-key.bin", bytes.fromhex("22" * 32)),
            ("answer-key.bin", bytes.fromhex("33" * 32)),
        ):
            _write(root / name, value)

        diagnosis = inspect_retained_fixed_batch(
            repo,
            root,
            expected_lock=str(lock["lock_hash"]),
        )
        observed = public_result(diagnosis, repo=repo)
        expected_cause = {
            "contamination": "contamination-policy-trigger",
            "protocol": "protocol-contract-nonconformance",
            "none": "state-transition-or-completion-marker-failure",
        }[event_kind]
        if observed["causal_class"] != expected_cause:
            raise AssertionError("exact-scale fixture did not classify the aggregate failure")
        return {
            "status": "pass",
            "locked_objects": diagnosis.locked_objects,
            "response_envelopes": EXPECTED_RESPONSES,
            "trace_envelopes": len(trace_specs),
            "actual_attempts": diagnosis.reconstruction.actual_attempts,
            "unique_logical_calls": diagnosis.reconstruction.unique_logical_calls,
            "completed_logical_calls": diagnosis.reconstruction.completed_logical_calls,
            "completed_private_pairings": diagnosis.reconstruction.completed_private_pairings,
            "all_500_pairing_records_exist": (
                diagnosis.reconstruction.all_500_pairing_records_exist
            ),
            "fixed_full_batch_completion_marker": (
                diagnosis.reconstruction.fixed_full_batch_completion_marker
            ),
            "causal_class": diagnosis.causal_class,
            "one_selected_logical_call": diagnosis.selected_attempt_records == 1,
            "bounded_neighbor_records": diagnosis.bounded_neighbor_records,
            "selected_response_objects": diagnosis.selected_response_objects,
            "selected_trace_objects": diagnosis.selected_trace_objects,
            "authenticated_fixed_batch_traces": diagnosis.authenticated_fixed_batch_traces,
            "protocol_nonconformance_traces": diagnosis.protocol_nonconformance_traces,
            "direct_or_probable_contamination_traces": (
                diagnosis.direct_or_probable_contamination_traces
            ),
            "retained_state_mutated": diagnosis.retained_state_mutated,
            "private_content_published": diagnosis.private_content_published,
            "operational_key_retained": diagnosis.operational_key_retained,
            "provider_calls": 0,
            "credential_reads": 0,
            "spend_usd": "0",
            "cleanup": "pass",
        }
