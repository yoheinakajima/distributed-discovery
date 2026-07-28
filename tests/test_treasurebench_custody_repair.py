from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from distributed_discovery.agent_ops.core import (
    authorization_challenge,
    hash_path,
    sha256_file,
)
from distributed_discovery.benchmark.agents_v1 import custody_repair
from distributed_discovery.benchmark.agents_v1.custody_conformance import (
    REQUIRED_COVERAGE,
    audit_conformance_framework,
    run_live_mode_custody_conformance,
)
from distributed_discovery.benchmark.agents_v1.custody_repair import (
    BATCH_ID,
    BRANCH,
    CAMPAIGN_ID,
    CONTRACT_PATH,
    EXECUTION_COMMIT,
    GATE_ID,
    ISSUE,
    RetainedDiagnostic,
    audit_execution_source,
    inspect_retained_custody_failure,
    run_read_only_custody_diagnostic,
    validate_diagnostic_authorization,
    validate_public_diagnostic,
)
from distributed_discovery.benchmark.agents_v1.models import canonical_json
from distributed_discovery.benchmark.agents_v1.pilot import (
    AppendOnlyLedger,
    atomic_private_write,
    create_output_lock,
)

REPO = Path(__file__).resolve().parents[1]


def _write(path: Path, payload: bytes) -> None:
    atomic_private_write(path, payload)


def _failure_fixture(root: Path) -> str:
    root.mkdir(parents=True, mode=0o700)
    root.chmod(0o700)
    for directory in (
        root / "encrypted-traces",
        root / "encrypted-provider-responses" / "openai",
        root / "encrypted-provider-responses" / "anthropic",
    ):
        directory.mkdir(parents=True, mode=0o700)
        directory.chmod(0o700)
    for directory in root.rglob("*"):
        if directory.is_dir():
            directory.chmod(0o700)
    for name, byte in (
        ("operational-key.bin", b"o"),
        ("seed.bin", b"s"),
        ("task-key.bin", b"t"),
        ("answer-key.bin", b"a"),
    ):
        _write(root / name, byte * 32)
    manifest = {
        "schema_version": "treasurebench-fresh-pilot-v2-private-state-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "classification": "real-authorized-private",
        "symbolic_root": custody_repair.SYMBOLIC_PRIVATE_ROOT,
    }
    identity = {
        "schema_version": "treasurebench-fresh-pilot-v2-execution-identity-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "execution_commit": EXECUTION_COMMIT,
    }
    state = {
        "schema_version": "treasurebench-fresh-pilot-v2-stage-state-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "public_canary_complete": True,
        "custody_complete": False,
        "private_prefix_complete": False,
        "fixed_full_batch_complete": False,
        "quarantined": True,
        "quarantine_stage": "custody",
        "quarantine_failure_class": "custody-creation-failure",
    }
    _write(root / "manifest.json", canonical_json(manifest) + b"\n")
    _write(root / "execution-identity.json", canonical_json(identity) + b"\n")
    _write(root / "provider-stage-state.json", canonical_json(state) + b"\n")
    access = AppendOnlyLedger(root / "access-log.jsonl")
    access.append(
        {
            "event_type": "custody-access",
            "status": "success",
            "operation": "fresh-public-exact-route-canary-pass",
            "private_material": False,
        }
    )
    usage = AppendOnlyLedger(root / "usage-cost-ledger.jsonl")
    usage.append(
        {
            "event_type": "provider-call",
            "status": "success",
            "provider": "OpenAI",
            "input_tokens": 700,
            "output_tokens": 120,
            "cost_usd": "0.003",
        }
    )
    usage.append(
        {
            "event_type": "provider-call",
            "status": "success",
            "provider": "Anthropic",
            "input_tokens": 649,
            "output_tokens": 133,
            "cost_usd": "0.0046095",
        }
    )
    usage.append(
        {
            "event_type": "batch-quarantine",
            "status": "quarantined",
            "stage": "custody",
            "failure_class": "custody-creation-failure",
        }
    )
    usage.close_provider_phase()
    trace_a = root / "encrypted-traces" / "a.sealed"
    trace_b = root / "encrypted-traces" / "b.sealed"
    response_a = root / "encrypted-provider-responses" / "openai" / "a.sealed.json"
    response_b = root / "encrypted-provider-responses" / "anthropic" / "b.sealed.json"
    for path, payload in (
        (trace_a, b"encrypted-trace-a"),
        (trace_b, b"encrypted-trace-b"),
        (response_a, b"encrypted-response-a"),
        (response_b, b"encrypted-response-b"),
    ):
        _write(path, payload)
    objects = {
        "execution-identity": (root / "execution-identity.json").read_bytes(),
        "access-log": (root / "access-log.jsonl").read_bytes(),
        "usage-cost-ledger": (root / "usage-cost-ledger.jsonl").read_bytes(),
        "provider-stage-state": (root / "provider-stage-state.json").read_bytes(),
        "trace/a.sealed": trace_a.read_bytes(),
        "trace/b.sealed": trace_b.read_bytes(),
        "provider-response/openai/a.sealed.json": response_a.read_bytes(),
        "provider-response/anthropic/b.sealed.json": response_b.read_bytes(),
    }
    lock = create_output_lock(
        objects,
        ledger=usage,
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    _write(root / "output-lock.json", canonical_json(lock) + b"\n")
    summary = {
        "schema_version": "treasurebench-fresh-pilot-v2-quarantine-closeout-v1",
        "decision": "fresh-pilot-v2-quarantined-engineering-only",
        "stage": "custody",
        "failure_class": "custody-creation-failure",
        "calls": 2,
        "input_tokens": 1349,
        "output_tokens": 253,
        "cost_usd": "0.0076095",
        "minimum_unseal_performed": False,
    }
    _write(root / "redacted-summary.json", canonical_json(summary) + b"\n")
    return str(lock["lock_hash"])


def _gate(now: datetime) -> dict[str, object]:
    commit = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    tree_hashes = {CONTRACT_PATH.as_posix(): hash_path(REPO / CONTRACT_PATH)}
    return {
        "schema_version": "agent-ops-owner-gate-v1",
        "kind": "owner-gate",
        "synthetic": False,
        "gate_id": GATE_ID,
        "task_contract": {
            "path": CONTRACT_PATH.as_posix(),
            "sha256": sha256_file(REPO / CONTRACT_PATH),
        },
        "issue": ISSUE,
        "pull_request": {"number": 203, "expected_state": "OPEN", "head_sha": commit},
        "branch": BRANCH,
        "commit": commit,
        "tree_hashes": tree_hashes,
        "purpose": "Authorize one exact read-only AO-0006 custody diagnostic.",
        "irreversible_actions": [],
        "private_actions": [
            {
                "permission": "private_data_permissions.read",
                "description": "Read only the exact bounded retained diagnostic allowlist.",
            }
        ],
        "external_actions": [],
        "cumulative_state": {"currency": "USD", "spend": "0", "calls": 0, "category_spend": {}},
        "hard_caps": {"currency": "USD", "spend": "0", "calls": 0, "category_spend": {}},
        "remaining_caps": {"currency": "USD", "spend": "0", "calls": 0, "category_spend": {}},
        "owner_confirmation_statements": ["I authorize the exact one-read diagnostic only."],
        "explicit_prohibitions": sorted(custody_repair.REQUIRED_PROHIBITIONS),
        "expires_at_utc": (now + timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        "authorization_output_symbolic_path": (
            f"XDG_CONFIG_HOME/distributed-discovery/agent-ops/authorizations/{GATE_ID}.yml"
        ),
        "next_milestone": "Run the one-use read-only diagnostic.",
        "generated_resume_message": "Resume AO-0007 and run only the exact diagnostic command.",
    }


def _authorization(gate: dict[str, object], now: datetime) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": "agent-ops-owner-authorization-v1",
        "kind": "owner-authorization",
        "synthetic": False,
        "gate_id": GATE_ID,
        "issue": ISSUE,
        "pull_request": gate["pull_request"]["number"],  # type: ignore[index]
        "branch": BRANCH,
        "commit": gate["commit"],
        "task_contract_sha256": gate["task_contract"]["sha256"],  # type: ignore[index]
        "tree_hashes": gate["tree_hashes"],
        "authorized_at_utc": now.isoformat().replace("+00:00", "Z"),
        "expires_at_utc": gate["expires_at_utc"],
        "challenge": authorization_challenge(gate),
        "owner_confirmation_statements": gate["owner_confirmation_statements"],
    }
    value["authorization_digest"] = custody_repair._authorization_digest(value)
    return value


def test_public_source_candidate_is_exactly_bounded() -> None:
    result = audit_execution_source(REPO)
    assert result["candidate"] == "private-task-generation-campaign-permit-rejection"
    assert result["material_created_before_generation"] is True
    assert result["synthetic_rehearsal_bypasses_private_gate"] is True


def test_read_only_fixture_adjudication_preserves_state(tmp_path: Path) -> None:
    root = tmp_path / "retained"
    expected_lock = _failure_fixture(root)
    before = {
        path.relative_to(root).as_posix(): (path.stat().st_mtime_ns, path.read_bytes())
        for path in root.rglob("*")
        if path.is_file()
    }
    result = inspect_retained_custody_failure(REPO, root, expected_lock=expected_lock)
    after = {
        path.relative_to(root).as_posix(): (path.stat().st_mtime_ns, path.read_bytes())
        for path in root.rglob("*")
        if path.is_file()
    }
    assert result.exact_failure_stage == "private-task-generation"
    assert result.exact_cause == "v2-campaign-absent-from-private-generation-permit-allowlist"
    assert result.private_values_read is False
    assert result.retained_state_mutated is False
    assert before == after


def test_read_only_fixture_rejects_inventory_expansion(tmp_path: Path) -> None:
    root = tmp_path / "retained"
    expected_lock = _failure_fixture(root)
    _write(root / "unrelated-private-object.bin", b"forbidden")
    with pytest.raises(ValueError, match="inventory differs"):
        inspect_retained_custody_failure(REPO, root, expected_lock=expected_lock)


def test_generic_authorization_is_exact_and_zero_cap() -> None:
    now = datetime.now(UTC)
    gate = _gate(now)
    value = _authorization(gate, now)
    assert (
        validate_diagnostic_authorization(
            value,
            gate=gate,
            repo=REPO,
            now=now,
            current_branch=BRANCH,
            current_tree_hashes=gate["tree_hashes"],  # type: ignore[arg-type]
        )
        == value
    )
    bad = json.loads(json.dumps(gate))
    bad["hard_caps"]["calls"] = 1
    with pytest.raises(PermissionError, match="zero spend and calls"):
        validate_diagnostic_authorization(
            value,
            gate=bad,
            repo=REPO,
            now=now,
            current_branch=BRANCH,
            current_tree_hashes=gate["tree_hashes"],  # type: ignore[arg-type]
        )


def test_one_use_marker_closes_private_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    monkeypatch.setattr(
        custody_repair,
        "load_diagnostic_authorization",
        lambda _repo: {"commit": "a" * 40},
    )
    diagnosis = RetainedDiagnostic(
        task_id="AO-0007",
        source_task_id="AO-0006",
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
        execution_commit=EXECUTION_COMMIT,
        output_lock_verified=True,
        output_lock_commitment="sha256:" + "0" * 64,
        locked_objects=8,
        inventory_verified=True,
        append_only_logs_verified=True,
        retained_state_mutated=False,
        public_canary_complete=True,
        custody_complete=False,
        quarantine_stage="custody",
        failure_class="custody-creation-failure",
        metadata_only_secret_files=(),
        ciphertext_files_present=(),
        ciphertext_files_absent=(),
        minimum_event_types=(),
        source_candidate="private-task-generation-campaign-permit-rejection",
        exact_failure_stage="private-task-generation",
        exact_cause="v2-campaign-absent-from-private-generation-permit-allowlist",
        private_values_read=False,
        provider_calls=0,
        credential_reads=0,
        private_paths_disclosed=False,
    )
    monkeypatch.setattr(custody_repair, "inspect_retained_custody_failure", lambda *_: diagnosis)
    first = run_read_only_custody_diagnostic(REPO)
    assert first["private_read_authority_closed"] is True
    with pytest.raises(PermissionError, match="already consumed"):
        run_read_only_custody_diagnostic(REPO)


def test_public_redaction_rejects_paths_and_secret_fields() -> None:
    validate_public_diagnostic({"status": "pass", "private_paths_disclosed": False})
    with pytest.raises(ValueError, match="forbidden field"):
        validate_public_diagnostic({"seed": "secret"})
    with pytest.raises(ValueError, match="host or private path"):
        validate_public_diagnostic({"detail": "/Users/example/private"})


def test_repaired_live_mode_conformance_preserves_failure_regression() -> None:
    framework = audit_conformance_framework(REPO)
    assert framework["status"] == "pass"
    gaps = framework["registered_pre_repair_gaps"]
    assert isinstance(gaps, Sequence)
    assert list(gaps) == []
    result = run_live_mode_custody_conformance(REPO)
    assert result["status"] == "pass"
    assert result["failed_stage"] is None
    coverage = result["coverage"]
    assert isinstance(coverage, Mapping)
    assert set(coverage) == set(REQUIRED_COVERAGE)
    assert set(coverage.values()) == {"pass"}
    assert result["cleanup"] == "pass"
