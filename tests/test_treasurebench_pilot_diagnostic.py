from __future__ import annotations

import json
import os
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from distributed_discovery.benchmark.agents_v1 import pilot_diagnostic as diagnostic
from distributed_discovery.benchmark.agents_v1.adapters import MockAdapter
from distributed_discovery.benchmark.agents_v1.generation import (
    generate_public_calibration,
)
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs/benchmark/agents-v1"
FIXTURE = DOCS / "fixtures/pilot-diagnostic-synthetic-cases.yml"
COMMIT = "a" * 40
TREE_HASH = f"sha256:{'b' * 64}"


def _schema(name: str) -> dict[str, object]:
    value = json.loads((DOCS / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _yaml(name: str) -> dict[str, object]:
    value = yaml.safe_load((DOCS / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _authorized(now: datetime) -> dict[str, object]:
    value = _yaml("pilot-diagnostic-authorization-template.yml")
    value.update(
        {
            "authorization_id": "tb-pilot-diagnostic-00000000-0000-0000-0000-000000000000",
            "authorization_status": "authorized",
            "authorized_at_utc": now.isoformat(),
            "expires_at_utc": (now + timedelta(hours=24)).isoformat(),
            "synthetic": False,
            "owner_attestation": (
                "I explicitly authorize this exact nonsynthetic read-only diagnosis "
                "of two retained provider errors and aggregate action-cardinality "
                "inspection across exactly 500 traces with no call or mutation."
            ),
            "diagnostic_commit": COMMIT,
            "diagnostic_tree_hash": TREE_HASH,
            "private_detail_output_symbolic_path": (
                "XDG_STATE_HOME/distributed-discovery/treasurebench-agents-v1/"
                "diagnostics/pilot-repair/test-authorization.json"
            ),
            "owner_confirmations": {
                "retained_audit_read_only": True,
                "verify_original_lock_and_custody": True,
                "inspect_exactly_500_run_traces_for_action_cardinality": True,
                "diagnose_exactly_two_provider_errors_with_minimum_context": True,
                "private_metric_sensitivity_only": True,
                "no_provider_call_spend_or_new_private_material": True,
                "no_private_state_mutation": True,
                "no_raw_private_publication_and_redacted_output_only": True,
            },
            "permissions": {
                "read_retained_state": True,
                "verify_output_lock": True,
                "verify_custody_and_logs": True,
                "decrypt_final_audit_package": True,
                "decrypt_two_error_records": True,
                "decrypt_exactly_500_private_run_traces": True,
                "decrypt_locked_task_answer_for_sensitivity": True,
                "aggregate_action_cardinalities": True,
                "compute_private_metric_sensitivity": True,
                "write_private_detail_outside_retained_root": True,
                "emit_redacted_public_candidate": True,
                "provider_calls": False,
                "credential_access": False,
                "generate_seed_task_answer_key_or_batch": False,
                "mutate_retained_private_state": False,
                "publish_raw_private_content": False,
            },
        }
    )
    return value


def _fake_git(_repo: Path, *arguments: str) -> str:
    if arguments == ("branch", "--show-current"):
        return diagnostic.REPAIR_BRANCH
    if arguments == ("status", "--porcelain", "--untracked-files=no"):
        return ""
    if arguments == ("rev-parse", "HEAD"):
        return COMMIT
    if arguments == ("rev-parse", f"origin/{diagnostic.REPAIR_BRANCH}"):
        return COMMIT
    raise AssertionError(arguments)


def _ledger(records: list[dict[str, object]]) -> bytes:
    previous = "GENESIS"
    lines: list[bytes] = []
    for sequence, event in enumerate(records, start=1):
        record = {
            "sequence": sequence,
            "previous_hash": previous,
            **event,
        }
        record_hash = diagnostic.sha256_commitment(diagnostic.canonical_json(record))
        record["record_hash"] = record_hash
        lines.append(diagnostic.canonical_json(record))
        previous = record_hash
    return b"\n".join(lines) + b"\n"


def _sealed_record(value: object, *, key: bytes, domain: str) -> dict[str, object]:
    associated = diagnostic.canonical_json(
        {
            "campaign_id": diagnostic.CAMPAIGN_ID,
            "batch_id": diagnostic.BATCH_ID,
            "domain": domain,
        }
    )
    nonce = bytes(range(12))
    ciphertext = AESGCM(key).encrypt(nonce, diagnostic.canonical_json(value), associated)
    return {
        "manifest": {
            "algorithm": "AES-256-GCM",
            "domain": domain,
            "nonce_hex": nonce.hex(),
            "ciphertext_sha256": diagnostic.sha256_commitment(ciphertext),
            "associated_data_sha256": diagnostic.sha256_commitment(associated),
        },
        "ciphertext_hex": ciphertext.hex(),
    }


def test_taxonomy_policy_and_template_validate_after_adjudication() -> None:
    result = diagnostic.validate_phase_a_documents(REPO)
    assert result["status"] == "pass"
    assert result["taxonomy_classes"] == 13
    assert result["policy_status"] == "prospective-final"
    assert result["provider_calls"] == 0
    assert result["private_state_read"] is False


def test_taxonomy_has_exact_required_classes_and_event_fields() -> None:
    taxonomy = _yaml("provider-error-taxonomy.yml")
    classes = {str(item["id"]) for item in taxonomy["classes"]}  # type: ignore[index]
    assert classes == {
        "transport-transient-recovered",
        "transport-transient-terminal",
        "provider-service-recovered",
        "provider-service-terminal",
        "request-parameter-invalid",
        "request-parameter-unsupported",
        "structured-output-provider-rejection",
        "structured-output-model-nonconformance",
        "parser-rejection-valid-response",
        "parser-rejection-invalid-response",
        "orchestration-protocol-error",
        "evaluator-missingness",
        "unknown-terminal",
    }
    assert set(taxonomy["required_event_fields"]) == {  # type: ignore[arg-type]
        "taxonomy_class",
        "attempt_status",
        "retry_status",
        "run_status",
        "task_status",
        "recoverability",
        "ownership",
        "public_safe_summary",
        "private_evidence_reference",
        "prospective_disposition",
    }


def test_prospective_policy_is_nonretroactive_and_zero_tolerance() -> None:
    policy = _yaml("prospective-failure-policy.yml")
    assert policy["status"] == "prospective-final"
    assert policy["original_pilot"] == {  # type: ignore[comparison-overlap]
        "decision": "sealed-pilot-quarantined-provider-failure",
        "retroactive_reclassification_allowed": False,
        "retroactive_rescoring_allowed": False,
    }
    retry = policy["retry"]
    tolerances = policy["tolerances"]
    assert isinstance(retry, dict) and isinstance(tolerances, dict)
    assert retry["transport"]["maximum_attempts"] == 2  # type: ignore[index]
    assert retry["schema"]["maximum_repairs"] == 1  # type: ignore[index]
    assert tolerances["terminal_failures_per_provider"] == 0
    assert tolerances["terminal_failures_overall"] == 0
    assert tolerances["protocol_errors_overall"] == 0
    assert tolerances["incomplete_pairings_allowed"] == 0
    assert tolerances["any_terminal_run_failure_quarantines_batch"] is True
    assert policy["decision_fields_pending"] == []
    assert policy["action_budget"] == {
        "final_action_cardinality": "exactly-one-per-required-agent",
        "non_final_proposal_cardinality": "1-6",
        "invalid_final_output_treatment": ("no-action-credited-and-conservative-missingness"),
        "method_c_required_before_performance": True,
        "metric_range_invariants_required": True,
    }
    assert policy["fresh_pilot_requirement"]["required_after_instrument_repair"] is True
    assert policy["fresh_pilot_requirement"]["execution_authorized_here"] is False


def test_authorization_template_is_inactive_and_synthetic() -> None:
    template = _yaml("pilot-diagnostic-authorization-template.yml")
    Draft202012Validator(
        _schema("pilot-diagnostic-authorization.schema.json"),
        format_checker=FormatChecker(),
    ).validate(template)
    assert template["authorization_status"] == "inactive"
    assert template["synthetic"] is True
    assert template["permissions"]["read_retained_state"] is False  # type: ignore[index]


def test_exact_authorization_accepts_only_frozen_commit_and_tree(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = datetime(2026, 7, 25, tzinfo=UTC)
    authorization = _authorized(now)
    monkeypatch.setattr(diagnostic, "_git", _fake_git)
    monkeypatch.setattr(diagnostic, "diagnostic_tree_hash", lambda _repo: TREE_HASH)
    assert (
        diagnostic.validate_diagnostic_authorization(
            authorization, repo=REPO, now=now + timedelta(minutes=1)
        )
        == authorization
    )

    wrong_commit = dict(authorization)
    wrong_commit["diagnostic_commit"] = "c" * 40
    with pytest.raises(PermissionError, match="commit"):
        diagnostic.validate_diagnostic_authorization(
            wrong_commit, repo=REPO, now=now + timedelta(minutes=1)
        )

    wrong_tree = dict(authorization)
    wrong_tree["diagnostic_tree_hash"] = f"sha256:{'d' * 64}"
    with pytest.raises(PermissionError, match="tree"):
        diagnostic.validate_diagnostic_authorization(
            wrong_tree, repo=REPO, now=now + timedelta(minutes=1)
        )


def test_expired_and_synthetic_authorizations_reject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = datetime(2026, 7, 25, tzinfo=UTC)
    monkeypatch.setattr(diagnostic, "_git", _fake_git)
    monkeypatch.setattr(diagnostic, "diagnostic_tree_hash", lambda _repo: TREE_HASH)
    expired = _authorized(now)
    with pytest.raises(PermissionError, match="active interval"):
        diagnostic.validate_diagnostic_authorization(
            expired, repo=REPO, now=now + timedelta(days=2)
        )
    synthetic = _authorized(now)
    synthetic["synthetic"] = True
    with pytest.raises((PermissionError, ValidationError)):
        diagnostic.validate_diagnostic_authorization(
            synthetic, repo=REPO, now=now + timedelta(minutes=1)
        )


def test_authorization_wrong_campaign_batch_and_lock_reject_schema() -> None:
    now = datetime(2026, 7, 25, tzinfo=UTC)
    schema = Draft202012Validator(
        _schema("pilot-diagnostic-authorization.schema.json"),
        format_checker=FormatChecker(),
    )
    for field, replacement in (
        ("original_campaign", "wrong"),
        ("original_batch", "wrong"),
        ("original_output_lock", f"sha256:{'0' * 64}"),
    ):
        authorization = _authorized(now)
        authorization[field] = replacement
        assert list(schema.iter_errors(authorization))


def test_interactive_helper_has_eight_separate_confirmations_and_zero_call_caps() -> None:
    helper = (REPO / "scripts/create_treasurebench_pilot_diagnostic_authorization.sh").read_text(
        encoding="utf-8"
    )
    assert helper.count('confirm_yes "') == 8
    assert "exactly 500 private run traces" in helper.lower()
    assert "no provider call" in helper.lower()
    assert "create no new private material" in helper.lower()
    assert "mutate no retained private-state" in helper.lower()
    assert "redacted candidate" in helper.lower()
    assert "status --porcelain --untracked-files=no" in helper
    assert 'git -C "$diagnostic_repo" rev-parse "origin/$diagnostic_branch"' in helper


def test_secure_read_requires_regular_nonsymlink_0600(tmp_path: Path) -> None:
    secure = tmp_path / "secure.json"
    secure.write_text('{"ok":true}', encoding="utf-8")
    secure.chmod(0o600)
    assert diagnostic.secure_read_json(secure) == {"ok": True}
    secure.chmod(0o644)
    with pytest.raises(PermissionError, match="permissions"):
        diagnostic.secure_read_bytes(secure)
    secure.chmod(0o600)
    link = tmp_path / "link.json"
    link.symlink_to(secure)
    with pytest.raises(OSError):
        diagnostic.secure_read_bytes(link)


def test_append_only_ledger_validates_and_corruption_rejects() -> None:
    payload = _ledger(
        [
            {"event_type": "provider-call", "status": "success"},
            {"event_type": "provider-phase-closed", "status": "locked"},
        ]
    )
    records = diagnostic.validate_append_only_ledger(payload)
    assert len(records) == 2
    corrupted = payload.replace(b'"status":"success"', b'"status":"failure"', 1)
    with pytest.raises(ValueError, match="hash"):
        diagnostic.validate_append_only_ledger(corrupted)


def test_independent_output_lock_verifier_accepts_exact_bytes_and_rejects_mutation() -> None:
    objects = {"one": b"alpha", "two": b"beta"}
    manifest: dict[str, object] = {
        "schema_version": "synthetic-lock-v1",
        "campaign_id": diagnostic.CAMPAIGN_ID,
        "batch_id": diagnostic.BATCH_ID,
        "objects": {
            name: diagnostic.sha256_commitment(payload) for name, payload in sorted(objects.items())
        },
        "ledger_head": "sha256:ledger",
        "provider_phase_closed": True,
    }
    manifest["lock_hash"] = diagnostic.sha256_commitment(diagnostic.canonical_json(manifest))
    diagnostic.verify_output_lock_manifest(
        manifest,
        objects,
        ledger_head="sha256:ledger",
        expected_lock=str(manifest["lock_hash"]),
        expected_objects=2,
    )
    with pytest.raises(ValueError, match="object"):
        diagnostic.verify_output_lock_manifest(
            manifest,
            {"one": b"mutated", "two": b"beta"},
            ledger_head="sha256:ledger",
        )


def test_synthetic_sealed_record_decrypts_and_tamper_rejects() -> None:
    key = bytes(range(32))
    record = _sealed_record(
        {"error_class": "transient-provider"}, key=key, domain="synthetic-error"
    )
    assert diagnostic._unseal_record(record, key=key) == {"error_class": "transient-provider"}
    tampered = json.loads(json.dumps(record))
    tampered["ciphertext_hex"] = str(tampered["ciphertext_hex"]) + "00"
    with pytest.raises(ValueError, match="ciphertext"):
        diagnostic._unseal_record(tampered, key=key)


def test_exact_two_error_selection_and_recovered_terminal_classification() -> None:
    ledger = (
        {
            "sequence": 1,
            "event_type": "provider-call",
            "status": "error",
            "provider": "Anthropic",
            "error_class": "transient-provider",
            "call_key": "call-one",
            "transport_attempt": 0,
        },
        {
            "sequence": 2,
            "event_type": "provider-call",
            "status": "success",
            "provider": "Anthropic",
            "error_class": None,
            "call_key": "call-one",
            "transport_attempt": 1,
        },
        {
            "sequence": 3,
            "event_type": "provider-call",
            "status": "error",
            "provider": "Anthropic",
            "error_class": "schema-or-parameter",
            "call_key": "call-two",
            "transport_attempt": 0,
        },
    )
    selected = diagnostic.select_exact_error_records(ledger)
    assert len(selected) == 2
    recovered = diagnostic.classify_error_record(
        selected[0], ledger=ledger, evidence_hash=f"sha256:{'1' * 64}"
    )
    terminal = diagnostic.classify_error_record(
        selected[1], ledger=ledger, evidence_hash=f"sha256:{'2' * 64}"
    )
    assert recovered["taxonomy_class"] == "provider-service-recovered"
    assert recovered["terminal_run_missing"] is False
    assert terminal["taxonomy_class"] == "unknown-terminal"
    assert terminal["terminal_run_missing"] is True


def test_excess_error_selection_rejects() -> None:
    with pytest.raises(PermissionError, match="exactly two"):
        diagnostic.ensure_exact_error_selection(({}, {}, {}))


def test_frozen_ledger_order_maps_every_primary_call_without_private_tasks() -> None:
    records: list[dict[str, object]] = []
    sequence = 0
    for provider, model in zip(diagnostic.PROVIDERS, diagnostic.MODELS, strict=True):
        sequence += 1
        records.append(
            {
                "sequence": sequence,
                "event_type": "provider-call",
                "provider": provider,
                "model": model,
                "call_key": f"call-canary-{sequence}",
                "schema_retry": False,
            }
        )
    contexts = diagnostic._private_call_contexts(REPO)
    schema_retry_key = ""
    for index, context in enumerate(contexts):
        sequence += 1
        call_key = f"call-primary-{index}"
        records.append(
            {
                "sequence": sequence,
                "event_type": "provider-call",
                "provider": context.provider,
                "model": context.model,
                "call_key": call_key,
                "schema_retry": False,
            }
        )
        if index == 10:
            sequence += 1
            schema_retry_key = "call-schema-retry"
            records.append(
                {
                    "sequence": sequence,
                    "event_type": "provider-call",
                    "provider": context.provider,
                    "model": context.model,
                    "call_key": schema_retry_key,
                    "schema_retry": True,
                }
            )
        if index == 20:
            sequence += 1
            records.append(
                {
                    "sequence": sequence,
                    "event_type": "provider-call",
                    "provider": context.provider,
                    "model": context.model,
                    "call_key": call_key,
                    "schema_retry": False,
                }
            )
    assignments = diagnostic.map_call_contexts(REPO, records)
    assert assignments["call-primary-0"] == contexts[0]
    assert assignments[schema_retry_key] == contexts[10]
    assert assignments["call-primary-20"] == contexts[20]
    assert assignments["call-canary-1"].stage == "public-canary"
    assert len(contexts) > 3000


def test_exact_500_trace_action_budget_diagnostic_is_aggregate_and_conservative(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    task = generate_public_calibration()[0]
    tasks = tuple(task for _ in range(50))
    contexts: list[diagnostic.RunContext] = []
    traces: list[dict[str, object]] = []
    run_ordinal = 0
    for provider, model in zip(diagnostic.PROVIDERS, diagnostic.MODELS, strict=True):
        for slot_ordinal in range(1, 51):
            for architecture in ARCHITECTURES:
                run = run_architecture(task, architecture, MockAdapter())
                if run_ordinal == 0:
                    original = run.final_actions[0]
                    over_budget = replace(
                        original,
                        actions=tuple(task.action_vocabulary[:2]),
                    )
                    run = replace(
                        run,
                        turns=tuple(
                            replace(turn, action=over_budget) if turn.action is original else turn
                            for turn in run.turns
                        ),
                        final_actions=tuple(
                            over_budget if action is original else action
                            for action in run.final_actions
                        ),
                    )
                trace = build_trace(run)
                traces.append(dict(trace.raw))
                contexts.append(
                    diagnostic.RunContext(
                        run_ordinal,
                        "synthetic-private-shape",
                        provider,
                        model,
                        slot_ordinal,
                        task.family_id,
                        architecture,
                        len(task.capabilities),
                    )
                )
                run_ordinal += 1
    paths = tuple(tmp_path / str(index) for index in range(500))

    monkeypatch.setattr(diagnostic, "_load_locked_tasks", lambda _root: tasks)
    monkeypatch.setattr(
        diagnostic,
        "_private_run_contexts",
        lambda _repo: tuple(contexts),
    )
    monkeypatch.setattr(diagnostic, "_private_trace_paths", lambda _root: paths)
    monkeypatch.setattr(
        diagnostic,
        "secure_read_json",
        lambda path: {"synthetic_index": int(path.name)},
    )
    monkeypatch.setattr(
        diagnostic,
        "_unseal_record",
        lambda record, *, key: traces[int(str(record["synthetic_index"]))],
    )

    result = diagnostic.diagnose_action_budget_contract(
        REPO,
        tmp_path,
        operational_key=b"synthetic",
    )
    assert result.public_aggregate["private_run_traces_inspected"] == 500
    assert result.public_aggregate["runs_with_invalid_final_cardinality"] == 1
    assert result.public_aggregate["over_budget_final_agent_outputs"] == 1
    assert result.public_aggregate["multiple_action_outputs_all_rounds"] == 1
    assert result.public_aggregate["metric_records_changed_by_extra_action_credit"] >= 1
    assert result.invalid_final_by_run[0] is True
    assert sum(result.invalid_final_by_run.values()) == 1


def test_redaction_allows_coarse_fields_and_rejects_private_content() -> None:
    safe = {
        "provider": "Anthropic",
        "taxonomy_class": "unknown-terminal",
        "stage": "fixed-full-batch",
        "terminal_run_missing": True,
    }
    diagnostic.validate_redacted_public(safe)
    with pytest.raises(PermissionError, match="prohibited key"):
        diagnostic.validate_redacted_public({**safe, "raw_output": "private"})
    with pytest.raises(PermissionError, match="prohibited text"):
        diagnostic.validate_redacted_public({**safe, "note": "/Users/example/private-state"})


def test_private_write_and_provider_call_paths_unconditionally_refuse(
    tmp_path: Path,
) -> None:
    with pytest.raises(PermissionError, match="Provider calls|provider calls"):
        diagnostic.refuse_provider_call()
    with pytest.raises(PermissionError, match="mutation"):
        diagnostic.refuse_retained_private_write(tmp_path / "state", b"x")


def test_private_snapshot_detects_mutation_without_writing_itself(tmp_path: Path) -> None:
    root = tmp_path / "retained"
    root.mkdir(mode=0o700)
    value = root / "value.bin"
    value.write_bytes(b"before")
    value.chmod(0o600)
    before = diagnostic.snapshot_private_state(root)
    assert before == diagnostic.snapshot_private_state(root)
    value.write_bytes(b"after")
    value.chmod(0o600)
    assert before != diagnostic.snapshot_private_state(root)


def test_private_snapshot_reads_metadata_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = tmp_path / "retained"
    root.mkdir(mode=0o700)
    unauthorized = root / "seed.bin"
    unauthorized.write_bytes(b"must-not-be-read")
    unauthorized.chmod(0o600)

    def refuse_content_read(_path: Path) -> bytes:
        raise AssertionError("snapshot attempted to read retained content")

    monkeypatch.setattr(diagnostic, "secure_read_bytes", refuse_content_read)
    snapshot = diagnostic.snapshot_private_state(root)
    assert snapshot["seed.bin"].size == len(b"must-not-be-read")


def test_private_detail_writer_is_outside_retained_root_and_exclusive(
    tmp_path: Path,
) -> None:
    retained = tmp_path / "retained"
    retained.mkdir(mode=0o700)
    output = tmp_path / "diagnostic" / "detail.json"
    diagnostic._secure_exclusive_private_write(output, b"{}\n", retained_root=retained)
    assert output.read_bytes() == b"{}\n"
    assert output.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        diagnostic._secure_exclusive_private_write(output, b"replacement\n", retained_root=retained)
    with pytest.raises(PermissionError, match="retained"):
        diagnostic._secure_exclusive_private_write(
            retained / "detail.json", b"{}\n", retained_root=retained
        )


def test_synthetic_fixture_covers_required_shapes_without_private_access() -> None:
    fixture = diagnostic.load_public_yaml(FIXTURE)
    result = diagnostic.diagnose_synthetic_cases(fixture)
    case_ids = {str(item["case_id"]) for item in fixture["cases"]}  # type: ignore[index]
    assert {
        "recovered-transient-provider-error",
        "terminal-schema-parameter-error",
        "request-side-invalid-parameter",
        "response-side-structured-output-nonconformance",
        "parser-rejects-valid-response",
        "malformed-error-record",
        "output-lock-mismatch",
        "unauthorized-extra-record-access",
        "private-disclosure-attempt",
        "private-mutation-attempt",
        "provider-call-attempt",
        "multiple-final-actions",
        "coverage-above-one",
        "parser-cardinality-omission",
        "shared-method-a-b-semantic-defect",
        "wrong-private-trace-count",
    } <= case_ids
    assert result["status"] == "pass"
    assert result["provider_calls"] == 0
    assert result["private_state_read"] is False
    assert result["private_state_mutated"] is False


def test_registered_corruptions_all_reject() -> None:
    results = diagnostic.audit_diagnostic_corruptions()
    assert len(results) >= 10
    assert all(item["status"] == "rejected" for item in results)
    ids = {str(item["corruption_id"]) for item in results}
    assert {
        "DIAG-01-wrong-campaign",
        "DIAG-02-wrong-batch",
        "DIAG-03-wrong-output-lock",
        "DIAG-04-wrong-diagnostic-commit",
        "DIAG-05-expired-authorization",
        "DIAG-06-synthetic-private-authorization",
        "DIAG-07-excessive-record-selection",
        "DIAG-08-private-write",
        "DIAG-09-provider-call",
        "DIAG-10-raw-error-publication",
        "DIAG-13-wrong-private-trace-count",
        "DIAG-14-multiple-final-actions",
        "DIAG-15-coverage-above-one",
        "DIAG-16-parser-cardinality-omission",
        "DIAG-17-shared-method-semantic-defect",
    } <= ids


def test_diagnostic_runtime_has_no_provider_or_credential_import() -> None:
    source = (REPO / "src/distributed_discovery/benchmark/agents_v1/pilot_diagnostic.py").read_text(
        encoding="utf-8"
    )
    wrapper = (REPO / "scripts/diagnose_treasurebench_pilot_errors.py").read_text(encoding="utf-8")
    import_lines = "\n".join(
        line
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )
    for prohibited in ("live_providers", "live_inputs", ".env.txt", "urllib", "requests"):
        assert prohibited not in import_lines
        assert prohibited not in wrapper
    assert "refuse_provider_call" in source


def test_historical_synthetic_rehearsal_is_portable_but_real_branch_gate_remains() -> None:
    source = (REPO / "src/distributed_discovery/benchmark/agents_v1/pilot.py").read_text(
        encoding="utf-8"
    )
    assert (
        'if not bool(value["synthetic"]) and _git(repo, "branch", "--show-current") != BRANCH:'
        in source
    )
    assert "synthetic authorization cannot authorize live execution" in source


def test_diagnostic_tree_inventory_is_explicit_and_has_no_private_path() -> None:
    assert len(diagnostic.DIAGNOSTIC_TREE_PATHS) == len(set(diagnostic.DIAGNOSTIC_TREE_PATHS))
    assert all(not item.startswith("/") for item in diagnostic.DIAGNOSTIC_TREE_PATHS)
    assert "tests/test_treasurebench_pilot_diagnostic.py" in diagnostic.DIAGNOSTIC_TREE_PATHS
    assert diagnostic.PRIVATE_ROOT_SYMBOLIC.startswith("XDG_STATE_HOME/")


def test_authorization_file_secure_read_rejects_broad_mode(tmp_path: Path) -> None:
    now = datetime(2026, 7, 25, tzinfo=UTC)
    target = tmp_path / "authorization.yml"
    target.write_text(yaml.safe_dump(_authorized(now)), encoding="utf-8")
    target.chmod(0o644)
    with pytest.raises(PermissionError, match="permissions"):
        diagnostic.secure_read_bytes(target)


def test_public_registration_preserves_original_pilot_and_scientific_boundary() -> None:
    registration = yaml.safe_load(
        (
            REPO / "reports/benchmark/treasurebench-agents-v1-pilot-repair-registration.yml"
        ).read_text(encoding="utf-8")
    )
    assert (
        registration["decision"]
        == "register-read-only-provider-and-protocol-adjudication-under-dd010"
    )
    assert registration["original_pilot"]["decision"] == (
        "sealed-pilot-quarantined-provider-failure"
    )
    assert registration["original_pilot"]["immutable"] is True
    boundary = registration["scientific_boundary"]
    assert all(value is False for value in boundary.values())
    assert registration["phase_a"]["provider_calls"] == 0
    assert registration["phase_a"]["private_state_read"] is False


def test_redacted_adjudication_records_only_aggregate_repair_evidence() -> None:
    adjudication = yaml.safe_load(
        (
            REPO / "reports/benchmark/treasurebench-agents-v1-pilot-repair-adjudication.yml"
        ).read_text(encoding="utf-8")
    )
    assert adjudication["status"] == "complete-redacted-engineering-adjudication"
    assert adjudication["original_pilot"]["decision"] == (
        "sealed-pilot-quarantined-provider-failure"
    )
    assert adjudication["verification"]["private_run_traces_inspected"] == 500
    assert adjudication["verification"]["retained_private_writes"] == 0
    assert adjudication["protocol_relationship"] == {
        "action_budget_and_provider_records_are_distinct": True,
        "frozen_protocol_invalid_runs": 2,
        "protocol_invalid_runs_attributable_to_terminal_provider_missingness": 1,
        "recovered_provider_event_created_terminal_run": False,
        "separate_downstream_protocol_invalid_runs": 1,
        "terminal_provider_event_created_protocol_invalid_run": True,
    }
    budget = adjudication["action_budget"]
    assert budget["runs_with_invalid_final_cardinality"] == 137
    assert budget["invalid_final_agent_outputs"] == 266
    assert budget["over_budget_final_agent_outputs"] == 265
    assert budget["metric_records_changed_by_extra_action_credit"] == 138
    assert budget["legacy_coverage_range_violations"] == 57
    assert budget["dimension_breakdowns_published"] is False
    assert adjudication["private_boundary"]["performance_results_published"] is False
    assert adjudication["decision"]["fresh_pilot_authorized_here"] is False


def test_repaired_rehearsal_and_fresh_pilot_budget_are_separately_gated() -> None:
    rehearsal = yaml.safe_load(
        (REPO / "reports/benchmark/treasurebench-agents-v1-pilot-repair-rehearsal.yml").read_text(
            encoding="utf-8"
        )
    )
    assert rehearsal["status"] == "pass"
    assert rehearsal["cases"] == 50
    assert rehearsal["corruptions_rejected"] == 28
    assert rehearsal["stable_rehearsal_hash"] == (
        "sha256:d13d925886b96015812ffd79e59faa89e2672a0efe7774652e3436b0c8c70d75"
    )
    assert rehearsal["provider_calls"] == 0

    options = yaml.safe_load(
        (REPO / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-options.yml").read_text(
            encoding="utf-8"
        )
    )
    selected = next(item for item in options["options"] if item["selected"])
    assert selected["id"] == "full-fresh-repair-confirmation"
    assert selected["private_runs"] == 500
    assert selected["expected_cost_usd"] == "15.00"
    assert selected["proposed_total_hard_cap_usd"] == "25.00"
    assert options["fresh_identity"]["original_or_future_base_instance_reuse"] == "prohibited"
    assert options["authorization"]["provider_calls_authorized_here"] is False


def test_symbolic_output_resolution_cannot_escape_state_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    resolved = diagnostic._resolve_symbolic_output(
        "XDG_STATE_HOME/distributed-discovery/diagnostic.json"
    )
    assert resolved == tmp_path / "distributed-discovery/diagnostic.json"
    with pytest.raises(PermissionError, match="unsafe"):
        diagnostic._resolve_symbolic_output("XDG_STATE_HOME/../escape.json")


def test_output_path_permissions_are_private(tmp_path: Path) -> None:
    retained = tmp_path / "retained"
    retained.mkdir(mode=0o700)
    output = tmp_path / "outside" / "detail.json"
    diagnostic._secure_exclusive_private_write(output, b"{}", retained_root=retained)
    assert os.stat(output).st_mode & 0o077 == 0
