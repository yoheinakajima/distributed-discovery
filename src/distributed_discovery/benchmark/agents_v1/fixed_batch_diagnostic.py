"""AO-0009 bounded read-only adjudication of AO-0008's fixed-batch failure.

Ordinary imports, audits, and tests never resolve retained AO-0008 state. The
live entry point validates the exact generic Agent Operations authorization,
creates a one-use marker outside the retained root, and then reads only the
frozen allowlist. Encrypted envelopes may be inspected structurally, but only
the selected logical call's responses and one directly corresponding trace
may be decrypted.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from distributed_discovery.agent_ops.core import (
    authorization_challenge,
    hash_path,
    load_yaml,
    sha256_file,
    validate,
)
from distributed_discovery.benchmark.agents_v1.models import canonical_json, sha256_hex
from distributed_discovery.benchmark.agents_v1.pilot import SealedObject, unseal_object
from distributed_discovery.benchmark.agents_v1.traces import verify_trace_hashes

TASK_ID = "AO-0009"
SOURCE_TASK_ID = "AO-0008"
ISSUE = 206
BRANCH = "codex/treasurebench-ao0008-fixed-batch-adjudication"
GATE_ID = "AOG-AO-0009-AO0008-FIXED-BATCH-DIAGNOSTIC"
CAMPAIGN_ID = "treasurebench-agents-v1-repair-confirmation-v3"
BATCH_ID = "tb-agents-v1-repair-confirmation-v3-b01"
EXECUTION_COMMIT = "0f9d82bb50cbb334bea47e24448831faf0cdbed8"
EXPECTED_OUTPUT_LOCK = "sha256:e52055b08ca3a8acb1cfb6ac608c6e601f3c618352900f92bf91c5ffc4718dbb"
EXPECTED_LOCKED_OBJECTS = 3576
EXPECTED_RESPONSES = 3067
EXPECTED_TRACES = 502
EXPECTED_PRIVATE_PAIRINGS = 500
CONTRACT_PATH = Path("tasks/treasurebench-ao0008-fixed-batch-adjudication.yml")
GATE_PATH = Path(
    "reports/agent-ops/AO-0009-treasurebench-ao0008-fixed-batch-diagnostic-owner-gate.yml"
)
ALLOWLIST_PATH = Path("reports/benchmark/treasurebench-ao0008-fixed-batch-diagnostic-allowlist.yml")
TAXONOMY_PATH = Path("docs/benchmark/agents-v1/treasurebench-fixed-batch-causal-taxonomy.yml")
PUBLIC_RESULT_SCHEMA_PATH = Path(
    "docs/benchmark/agents-v1/treasurebench-fixed-batch-public-diagnostic.schema.json"
)
SYMBOLIC_PRIVATE_ROOT = (
    "XDG_STATE_HOME/distributed-discovery/treasurebench-agents-v1/repair-confirmation-v3"
)
READABLE_FIXED = frozenset(
    {
        "output-lock.json",
        "execution-identity.json",
        "provider-stage-state.json",
        "access-log.jsonl",
        "usage-cost-ledger.jsonl",
    }
)
EXPECTED_NONLOCKED = frozenset(
    {
        "manifest.json",
        "operational-key.bin",
        "seed.bin",
        "task-key.bin",
        "answer-key.bin",
        "output-lock.json",
        "redacted-summary.json",
    }
)
PROHIBITED_READS = frozenset(
    {
        "manifest.json",
        "seed.bin",
        "task-key.bin",
        "answer-key.bin",
        "task-custody.json",
        "answer-custody.json",
        "custody-manifest.json",
        "redacted-summary.json",
    }
)
RETRYABLE_ERRORS = frozenset(
    {
        "timeout",
        "transient-transport",
        "invalid-provider-json",
        "rate-limit",
        "transient-provider",
    }
)
TRANSPORT_ERRORS = frozenset({"timeout", "transient-transport", "invalid-provider-json"})
TAXONOMY_IDS = (
    "provider-transport-terminal",
    "provider-http-terminal",
    "schema-repair-exhausted",
    "returned-output-parse-failure",
    "protocol-contract-nonconformance",
    "final-action-cardinality-failure",
    "trace-encryption-or-persistence-failure",
    "response-ledger-append-failure",
    "duplicate-or-conflicting-call-key",
    "cost-or-token-cap-guard",
    "pairing-completeness-failure",
    "state-transition-or-completion-marker-failure",
    "post-batch-verification-failure",
    "unknown-within-retained-evidence",
)
REQUIRED_PROHIBITIONS = frozenset(
    {
        "provider-calls-outside-manifest",
        "credential-read-outside-manifest",
        "unauthorized-private-access",
        "scientific-mutation-outside-contract",
        "cap-increase",
        "consequential-action-by-gate-engine",
        "ao-0008-retained-state-mutation",
        "second-ao-0008-private-read",
        "bulk-unseal",
        "seed-task-key-answer-key-task-answer-or-credential-access",
    }
)


@dataclass(frozen=True)
class FileMetadata:
    relative_path: str
    mode: str
    size: int
    mtime_ns: int
    inode: int
    byte_sha256: str | None
    locked_commitment: str | None


@dataclass(frozen=True)
class EnvelopeMetadata:
    relative_path: str
    object_name: str
    object_class: str
    mode: str
    size: int
    mtime_ns: int
    domain: str
    nonce_bytes: int
    ciphertext_sha256: str
    associated_data_sha256: str
    locked_commitment: str


@dataclass(frozen=True)
class StructuralReconstruction:
    planned_logical_calls: int
    actual_attempts: int
    unique_logical_calls: int
    completed_logical_calls: int
    recovered_attempts_by_provider: Mapping[str, int]
    terminal_attempts_by_provider: Mapping[str, int]
    completed_private_pairings: int
    private_prefix_pairings: int
    fixed_full_batch_pairings: int
    public_canary_traces: int
    all_500_pairing_records_exist: bool
    fixed_full_batch_completion_marker: bool
    exact_last_durable_stage: str
    all_selected_run_outputs_exist: bool


@dataclass(frozen=True)
class CausalEvidence:
    integrity_ok: bool = True
    response_ledger_one_to_one: bool = True
    duplicate_or_conflicting_call_key: bool = False
    cap_guard: bool = False
    pairing_complete: bool = True
    fixed_full_batch_marker: bool = False
    post_batch_verification_failed: bool = False
    selected_trace_authenticated: bool = True
    selected_trace_errors: tuple[str, ...] = ()
    selected_trace_retry_count: int = 0
    selected_provider_error: str | None = None
    selected_call_terminal: bool = False
    all_outputs_exist: bool = True
    direct_trace_correspondence: bool = False
    safe_exception_code_persisted: bool = False


@dataclass(frozen=True)
class RetainedFixedBatchDiagnostic:
    task_id: str
    source_task_id: str
    campaign_id: str
    batch_id: str
    execution_commit: str
    output_lock_verified_within_allowlist: bool
    output_lock_commitment: str
    locked_objects: int
    inventory_verified: bool
    append_only_ledgers_verified: bool
    retained_state_mutated: bool
    reconstruction: StructuralReconstruction
    selected_call_key_hash: str
    selected_attempt_records: int
    bounded_neighbor_records: int
    selected_response_objects: int
    selected_trace_objects: int
    selected_trace_domain_hash: str | None
    exception_stage: str
    safe_error_code: str
    causal_class: str
    causal_actor: str
    private_content_published: bool
    operational_key_retained: bool
    provider_calls: int
    credential_reads: int
    spend_usd: str
    private_paths_disclosed: bool


def _authorization_digest(value: Mapping[str, object]) -> str:
    unsigned = dict(value)
    unsigned.pop("authorization_digest", None)
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def authorization_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return root / "distributed-discovery" / "agent-ops" / "authorizations" / f"{GATE_ID}.yml"


def private_state_root() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "distributed-discovery" / "treasurebench-agents-v1" / "repair-confirmation-v3"


def diagnostic_output_root() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "distributed-discovery" / "agent-ops" / "private-diagnostics" / TASK_ID


def _git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ("git", *arguments),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _require_secure_regular(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise PermissionError("diagnostic input must be a regular non-symlink file")
    if stat.S_IMODE(info.st_mode) != 0o600:
        raise PermissionError("diagnostic input must have mode 0600")
    return info


def _secure_read(root: Path, relative: str, *, allowed: frozenset[str]) -> bytes:
    if relative not in allowed or relative in PROHIBITED_READS:
        raise PermissionError("diagnostic attempted a non-allowlisted retained read")
    path = root / relative
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise PermissionError("diagnostic retained input is unsafe")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _secure_json(root: Path, relative: str, *, allowed: frozenset[str]) -> dict[str, object]:
    value = json.loads(_secure_read(root, relative, allowed=allowed))
    if not isinstance(value, dict):
        raise ValueError("diagnostic JSON input must be an object")
    return {str(name): item for name, item in value.items()}


def _require_zero_gate_caps(gate: Mapping[str, object]) -> None:
    for name in ("cumulative_state", "hard_caps", "remaining_caps"):
        raw = gate.get(name)
        if not isinstance(raw, Mapping):
            raise PermissionError(f"{name} must be a mapping")
        if raw.get("currency") != "USD" or raw.get("spend") != "0" or raw.get("calls") != 0:
            raise PermissionError("diagnostic gate must retain exact zero spend and calls")
        category = raw.get("category_spend")
        if not isinstance(category, Mapping) or category:
            raise PermissionError("diagnostic gate category caps must be empty")


def validate_diagnostic_authorization(
    value: dict[str, Any],
    *,
    gate: dict[str, Any],
    repo: Path,
    now: datetime | None = None,
    current_branch: str | None = None,
    current_tree_hashes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Bind one generic authorization to the frozen AO-0009 diagnostic."""

    validate(value, "owner-authorization.schema.json")
    validate(gate, "owner-gate.schema.json")
    if value["authorization_digest"] != _authorization_digest(value):
        raise PermissionError("owner authorization digest mismatch")
    if gate["gate_id"] != GATE_ID or gate["issue"] != ISSUE or gate["branch"] != BRANCH:
        raise PermissionError("owner gate is not the frozen AO-0009 gate")
    if gate["task_contract"]["path"] != CONTRACT_PATH.as_posix():
        raise PermissionError("owner gate contract path mismatch")
    if gate["task_contract"]["sha256"] != sha256_file(repo / CONTRACT_PATH):
        raise PermissionError("owner gate contract hash mismatch")
    expected = {
        "gate_id": GATE_ID,
        "issue": ISSUE,
        "pull_request": gate["pull_request"]["number"],
        "branch": BRANCH,
        "commit": gate["commit"],
        "task_contract_sha256": sha256_file(repo / CONTRACT_PATH),
        "tree_hashes": gate["tree_hashes"],
        "challenge": authorization_challenge(gate),
    }
    if any(value.get(name) != item for name, item in expected.items()):
        raise PermissionError("owner authorization does not bind the diagnostic surface")
    current = now or datetime.now(UTC)
    authorized = datetime.fromisoformat(str(value["authorized_at_utc"]).replace("Z", "+00:00"))
    expires = datetime.fromisoformat(str(value["expires_at_utc"]).replace("Z", "+00:00"))
    gate_expires = datetime.fromisoformat(str(gate["expires_at_utc"]).replace("Z", "+00:00"))
    if authorized > current or expires <= current or gate_expires <= current:
        raise PermissionError("diagnostic authorization is outside its active interval")
    if expires != gate_expires:
        raise PermissionError("diagnostic authorization expiry differs from the gate")
    _require_zero_gate_caps(gate)
    prohibitions = gate.get("explicit_prohibitions")
    if not isinstance(prohibitions, Sequence) or isinstance(prohibitions, str):
        raise PermissionError("diagnostic prohibitions are malformed")
    if not REQUIRED_PROHIBITIONS.issubset({str(item) for item in prohibitions}):
        raise PermissionError("diagnostic gate is missing a required prohibition")
    branch = current_branch or _git(repo, "branch", "--show-current")
    if branch != BRANCH:
        raise PermissionError("diagnostic branch mismatch")
    if subprocess.run(
        ("git", "merge-base", "--is-ancestor", str(value["commit"]), "HEAD"),
        cwd=repo,
        check=False,
        capture_output=True,
    ).returncode:
        raise PermissionError("authorized diagnostic commit is not an ancestor")
    observed = (
        dict(current_tree_hashes)
        if current_tree_hashes is not None
        else {str(path): hash_path(repo / str(path)) for path in gate["tree_hashes"]}
    )
    if observed != gate["tree_hashes"]:
        raise PermissionError("diagnostic execution-sensitive tree changed")
    return value


def load_diagnostic_authorization(repo: Path) -> dict[str, Any]:
    """Load only the exact generic authorization before resolving retained state."""

    gate_file = repo / GATE_PATH
    if not gate_file.is_file() or gate_file.is_symlink():
        raise PermissionError("committed AO-0009 owner gate is required")
    auth_file = authorization_path()
    _require_secure_regular(auth_file)
    return validate_diagnostic_authorization(
        load_yaml(auth_file), gate=load_yaml(gate_file), repo=repo
    )


def validate_public_contracts(repo: Path) -> Mapping[str, object]:
    """Validate the frozen taxonomy and read allowlist without private access."""

    taxonomy = load_yaml(repo / TAXONOMY_PATH)
    classes = taxonomy.get("classes")
    if not isinstance(classes, list):
        raise ValueError("causal taxonomy classes are missing")
    observed = tuple(str(item.get("id")) for item in classes if isinstance(item, Mapping))
    if observed != TAXONOMY_IDS:
        raise ValueError("causal taxonomy order or membership changed")
    allowlist = load_yaml(repo / ALLOWLIST_PATH)
    if (
        allowlist.get("task_id") != TASK_ID
        or allowlist.get("source_task_id") != SOURCE_TASK_ID
        or allowlist.get("output_lock") != EXPECTED_OUTPUT_LOCK
        or allowlist.get("locked_objects") != EXPECTED_LOCKED_OBJECTS
        or allowlist.get("second_read") != "fail-closed"
        or allowlist.get("bulk_unseal") != "prohibited"
    ):
        raise ValueError("fixed-batch diagnostic allowlist changed")
    structural = allowlist.get("structural_encrypted_metadata")
    bounded = allowlist.get("bounded_failure_context")
    if not isinstance(structural, Mapping) or not isinstance(bounded, Mapping):
        raise ValueError("diagnostic structural or bounded allowlist is malformed")
    responses = structural.get("encrypted-provider-responses")
    traces = structural.get("encrypted-traces")
    if (
        not isinstance(responses, Mapping)
        or not isinstance(traces, Mapping)
        or responses.get("exact_files") != EXPECTED_RESPONSES
        or traces.get("exact_files") != EXPECTED_TRACES
        or bounded.get("exact_failed_logical_calls") != 1
        or bounded.get("preceding_attempt_or_orchestration_records_maximum") != 2
        or bounded.get("following_attempt_or_orchestration_records_maximum") != 2
        or bounded.get("selected_provider_response_objects_maximum") != 2
        or bounded.get("selected_trace_objects_maximum") != 1
        or bounded.get("selected_encrypted_objects_total_maximum") != 3
    ):
        raise ValueError("diagnostic object or record ceilings changed")
    schema = json.loads((repo / PUBLIC_RESULT_SCHEMA_PATH).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return {
        "status": "pass",
        "taxonomy_classes": len(observed),
        "fixed_records": len(READABLE_FIXED),
        "response_envelopes": EXPECTED_RESPONSES,
        "trace_envelopes": EXPECTED_TRACES,
        "selected_logical_calls": 1,
        "neighbor_records_maximum": 4,
        "selected_encrypted_objects_maximum": 3,
        "provider_calls": 0,
        "credential_reads": 0,
        "private_state_reads": 0,
        "spend_usd": "0",
    }


def _validate_ledger(payload: bytes) -> tuple[dict[str, object], ...]:
    records: list[dict[str, object]] = []
    previous = "GENESIS"
    for index, line in enumerate(payload.splitlines(), 1):
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError("append-only record must be an object")
        record = {str(name): item for name, item in value.items()}
        actual = record.pop("record_hash", None)
        if record.get("sequence") != index or record.get("previous_hash") != previous:
            raise ValueError("append-only record sequence or chain mismatch")
        expected = f"sha256:{sha256_hex(canonical_json(record))}"
        if actual != expected:
            raise ValueError("append-only record hash mismatch")
        record["record_hash"] = actual
        records.append(record)
        previous = str(actual)
    return tuple(records)


def _locked_relative(name: str) -> str:
    fixed = {
        "task-ciphertext": "task-custody.json",
        "answer-ciphertext": "answer-custody.json",
        "custody-manifest": "custody-manifest.json",
        "execution-identity": "execution-identity.json",
        "access-log": "access-log.jsonl",
        "usage-cost-ledger": "usage-cost-ledger.jsonl",
        "provider-stage-state": "provider-stage-state.json",
    }
    if name in fixed:
        return fixed[name]
    if name.startswith("trace/"):
        return f"encrypted-traces/{name.removeprefix('trace/')}"
    if name.startswith("provider-response/"):
        return f"encrypted-provider-responses/{name.removeprefix('provider-response/')}"
    raise PermissionError("output lock names an undeclared object class")


def _secure_inventory(root: Path) -> tuple[str, ...]:
    if root.is_symlink() or not root.is_dir() or stat.S_IMODE(root.lstat().st_mode) != 0o700:
        raise PermissionError("retained private-state root is unsafe")
    files: list[str] = []
    for current, names, filenames in os.walk(root, followlinks=False):
        base = Path(current)
        if stat.S_IMODE(base.lstat().st_mode) != 0o700:
            raise PermissionError("retained private-state directory mode changed")
        for name in names:
            child = base / name
            if child.is_symlink() or not child.is_dir():
                raise PermissionError("unsafe retained subdirectory")
        for filename in filenames:
            path = base / filename
            _require_secure_regular(path)
            files.append(path.relative_to(root).as_posix())
    return tuple(sorted(files))


def _snapshot(
    root: Path,
    inventory: Sequence[str],
    *,
    byte_readable: frozenset[str],
    commitments: Mapping[str, str],
) -> tuple[FileMetadata, ...]:
    reverse = {_locked_relative(name): str(value) for name, value in commitments.items()}
    values: list[FileMetadata] = []
    for relative in inventory:
        path = root / relative
        info = path.lstat()
        digest = (
            f"sha256:{sha256_hex(_secure_read(root, relative, allowed=byte_readable))}"
            if relative in byte_readable
            else None
        )
        values.append(
            FileMetadata(
                relative_path=relative,
                mode=f"{stat.S_IMODE(info.st_mode):04o}",
                size=info.st_size,
                mtime_ns=info.st_mtime_ns,
                inode=info.st_ino,
                byte_sha256=digest,
                locked_commitment=reverse.get(relative),
            )
        )
    return tuple(values)


def _load_envelope_metadata(
    root: Path,
    relative: str,
    *,
    object_name: str,
    locked_commitment: str,
) -> EnvelopeMetadata:
    if not (
        relative.startswith("encrypted-provider-responses/")
        or relative.startswith("encrypted-traces/")
    ):
        raise PermissionError("envelope metadata read is outside the frozen classes")
    path = root / relative
    info = _require_secure_regular(path)
    payload = path.read_bytes()
    if f"sha256:{sha256_hex(payload)}" != locked_commitment:
        raise ValueError("encrypted envelope differs from its output-lock commitment")
    outer = json.loads(payload)
    if not isinstance(outer, Mapping) or set(outer) != {"ciphertext_hex", "manifest"}:
        raise ValueError("encrypted envelope shape is malformed")
    manifest = outer["manifest"]
    if not isinstance(manifest, Mapping):
        raise ValueError("encrypted envelope manifest is malformed")
    ciphertext_hex = str(outer["ciphertext_hex"])
    if len(ciphertext_hex) % 2 or any(char not in "0123456789abcdef" for char in ciphertext_hex):
        raise ValueError("encrypted envelope ciphertext encoding is malformed")
    if f"sha256:{hashlib.sha256(bytes.fromhex(ciphertext_hex)).hexdigest()}" != manifest.get(
        "ciphertext_sha256"
    ):
        raise ValueError("encrypted envelope ciphertext commitment mismatch")
    try:
        nonce_bytes = len(bytes.fromhex(str(manifest["nonce_hex"])))
    except ValueError as error:
        raise ValueError("encrypted envelope nonce encoding is malformed") from error
    if nonce_bytes != 12:
        raise ValueError("encrypted envelope nonce length changed")
    return EnvelopeMetadata(
        relative_path=relative,
        object_name=object_name,
        object_class=("response" if relative.startswith("encrypted-provider") else "trace"),
        mode=f"{stat.S_IMODE(info.st_mode):04o}",
        size=info.st_size,
        mtime_ns=info.st_mtime_ns,
        domain=str(manifest["domain"]),
        nonce_bytes=nonce_bytes,
        ciphertext_sha256=str(manifest["ciphertext_sha256"]),
        associated_data_sha256=str(manifest["associated_data_sha256"]),
        locked_commitment=locked_commitment,
    )


def _trace_stage(domain: str) -> str:
    if domain.startswith("fresh-raw-trace/public-canary/"):
        return "public-canary"
    if domain.startswith("raw-trace/private-prefix/"):
        return "private-prefix"
    if domain.startswith("raw-trace/fixed-full-batch/"):
        return "fixed-full-batch"
    return "unknown"


def reconstruct_structure(
    usage: Sequence[Mapping[str, object]],
    state: Mapping[str, object],
    envelopes: Sequence[EnvelopeMetadata],
) -> StructuralReconstruction:
    """Reconstruct operational counts without private task or performance data."""

    calls = tuple(record for record in usage if record.get("event_type") == "provider-call")
    groups: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for record in calls:
        groups[str(record.get("call_key"))].append(record)
    recovered = Counter({"OpenAI": 0, "Anthropic": 0})
    terminal = Counter({"OpenAI": 0, "Anthropic": 0})
    base_logical_calls = 0
    completed = 0
    for records in groups.values():
        ordered = sorted(records, key=lambda item: int(str(item["transport_attempt"])))
        provider = str(ordered[-1].get("provider"))
        schema_repair = ordered[-1].get("schema_retry") is True
        if not schema_repair:
            base_logical_calls += 1
        if ordered[-1].get("status") == "success":
            if not schema_repair:
                completed += 1
            if len(ordered) > 1 and ordered[0].get("status") == "error":
                recovered[provider] += 1
            if schema_repair:
                recovered[provider] += 1
        else:
            error_class = str(ordered[-1].get("error_class"))
            if error_class not in RETRYABLE_ERRORS or len(ordered) >= 2:
                terminal[provider] += 1
    trace_stages = Counter(
        _trace_stage(item.domain) for item in envelopes if item.object_class == "trace"
    )
    private_pairings = trace_stages["private-prefix"] + trace_stages["fixed-full-batch"]
    return StructuralReconstruction(
        planned_logical_calls=3016,
        actual_attempts=len(calls),
        unique_logical_calls=base_logical_calls,
        completed_logical_calls=completed,
        recovered_attempts_by_provider=dict(recovered),
        terminal_attempts_by_provider=dict(terminal),
        completed_private_pairings=private_pairings,
        private_prefix_pairings=trace_stages["private-prefix"],
        fixed_full_batch_pairings=trace_stages["fixed-full-batch"],
        public_canary_traces=trace_stages["public-canary"],
        all_500_pairing_records_exist=(
            private_pairings == EXPECTED_PRIVATE_PAIRINGS
            and trace_stages["private-prefix"] == 50
            and trace_stages["fixed-full-batch"] == 450
        ),
        fixed_full_batch_completion_marker=state.get("fixed_full_batch_complete") is True,
        exact_last_durable_stage=(
            "fixed-full-batch-quarantined-before-completion-marker"
            if state.get("quarantine_stage") == "fixed-full-batch"
            and state.get("fixed_full_batch_complete") is False
            else "state-boundary-mismatch"
        ),
        all_selected_run_outputs_exist=False,
    )


def _terminal_call_keys(
    records: Sequence[Mapping[str, object]],
) -> tuple[str, ...]:
    groups: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for record in records:
        if record.get("event_type") == "provider-call":
            groups[str(record.get("call_key"))].append(record)
    terminal: list[str] = []
    for key, attempts in groups.items():
        ordered = sorted(attempts, key=lambda item: int(str(item["transport_attempt"])))
        last = ordered[-1]
        if last.get("status") == "error" and (
            last.get("error_class") not in RETRYABLE_ERRORS or len(ordered) >= 2
        ):
            terminal.append(key)
    return tuple(sorted(terminal))


def select_bounded_context(
    records: Sequence[Mapping[str, object]],
) -> tuple[str, tuple[Mapping[str, object], ...], tuple[Mapping[str, object], ...]]:
    """Select one logical call and at most two records on either side."""

    calls = [record for record in records if record.get("event_type") == "provider-call"]
    terminals = _terminal_call_keys(records)
    selected = terminals[0] if len(terminals) == 1 else str(calls[-1]["call_key"])
    selected_records = tuple(record for record in calls if record.get("call_key") == selected)
    if not 1 <= len(selected_records) <= 2:
        raise PermissionError("selected logical call exceeds the two-attempt ceiling")
    anchor_sequence = int(str(selected_records[-1]["sequence"]))
    operational = [
        record
        for record in records
        if record.get("event_type")
        in {"provider-call", "batch-quarantine", "provider-phase-closed"}
    ]
    anchor = next(
        index
        for index, record in enumerate(operational)
        if int(str(record["sequence"])) == anchor_sequence
    )
    neighbors = tuple(
        operational[max(0, anchor - 2) : anchor] + operational[anchor + 1 : anchor + 3]
    )
    if len(neighbors) > 4:
        raise PermissionError("bounded neighbor record ceiling exceeded")
    return selected, selected_records, neighbors


def _sealed_from_path(path: Path) -> SealedObject:
    _require_secure_regular(path)
    outer = json.loads(path.read_bytes())
    if not isinstance(outer, Mapping) or not isinstance(outer.get("manifest"), Mapping):
        raise ValueError("selected encrypted envelope is malformed")
    manifest = outer["manifest"]
    assert isinstance(manifest, Mapping)
    return SealedObject(
        domain=str(manifest["domain"]),
        nonce_hex=str(manifest["nonce_hex"]),
        ciphertext=bytes.fromhex(str(outer["ciphertext_hex"])),
        ciphertext_sha256=str(manifest["ciphertext_sha256"]),
        associated_data_sha256=str(manifest["associated_data_sha256"]),
    )


def _decrypt_selected(path: Path, key: bytearray) -> object:
    transient_key = bytes(key)
    return unseal_object(
        _sealed_from_path(path),
        key=transient_key,
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )


def classify_cause(evidence: CausalEvidence) -> tuple[str, str, str]:
    """Return causal class, actor, and public-safe error code."""

    if not evidence.integrity_ok:
        return (
            "retained-state-integrity-mismatch-stop",
            "retained-integrity",
            "retained-integrity-mismatch",
        )
    if not evidence.response_ledger_one_to_one:
        return (
            "response-ledger-append-failure",
            "local-runtime",
            "response-ledger-one-to-one-failure",
        )
    if evidence.duplicate_or_conflicting_call_key:
        return (
            "duplicate-or-conflicting-call-key",
            "local-runtime",
            "duplicate-or-conflicting-call-key",
        )
    if evidence.cap_guard:
        return ("cost-or-token-cap-guard", "registered-policy", "cap-guard")
    if not evidence.pairing_complete:
        return (
            "pairing-completeness-failure",
            "local-orchestration",
            "pairing-completeness",
        )
    if not evidence.selected_trace_authenticated:
        return (
            "trace-encryption-or-persistence-failure",
            "local-runtime",
            "selected-trace-authentication",
        )
    if evidence.selected_call_terminal and evidence.selected_provider_error:
        causal = (
            "provider-transport-terminal"
            if evidence.selected_provider_error in TRANSPORT_ERRORS
            else "provider-http-terminal"
        )
        return causal, "provider", evidence.selected_provider_error
    lowered = tuple(error.lower() for error in evidence.selected_trace_errors)
    if any(
        "final action cardinality" in error or "final-action-count" in error for error in lowered
    ):
        return (
            "final-action-cardinality-failure",
            "evaluated-agent",
            "final-action-cardinality",
        )
    if lowered and evidence.selected_trace_retry_count > 0:
        return (
            "schema-repair-exhausted",
            "evaluated-agent-output",
            "schema-repair-exhausted",
        )
    if any(
        token in error
        for error in lowered
        for token in ("malformed json", "missing fields", "undeclared fields", "action output")
    ):
        return (
            "returned-output-parse-failure",
            "evaluated-agent-output",
            "returned-output-parse",
        )
    if lowered:
        return (
            "protocol-contract-nonconformance",
            "evaluated-agent",
            "protocol-contract-nonconformance",
        )
    if (
        evidence.all_outputs_exist
        and not evidence.fixed_full_batch_marker
        and evidence.direct_trace_correspondence
        and evidence.safe_exception_code_persisted
    ):
        return (
            "state-transition-or-completion-marker-failure",
            "local-bookkeeping",
            "completion-marker",
        )
    if evidence.post_batch_verification_failed:
        return (
            "post-batch-verification-failure",
            "local-verification",
            "post-batch-verification",
        )
    return (
        "unknown-within-retained-evidence",
        "undetermined",
        "bounded-evidence-unknown",
    )


def _safe_trace_details(trace: object) -> tuple[tuple[str, ...], int, Mapping[str, object]]:
    if not isinstance(trace, Mapping) or not verify_trace_hashes(trace):
        raise ValueError("selected trace authentication failed")
    events = trace.get("events")
    if not isinstance(events, list) or not events or not isinstance(events[-1], Mapping):
        raise ValueError("selected trace events are malformed")
    last = events[-1]
    errors = last.get("errors", [])
    usage = last.get("usage")
    if not isinstance(errors, list) or not isinstance(usage, Mapping):
        raise ValueError("selected trace safe fields are malformed")
    return tuple(str(item) for item in errors), int(str(last.get("retry_count", 0))), usage


def _response_safe_details(response: object) -> tuple[str | None, Mapping[str, object]]:
    if not isinstance(response, Mapping) or not isinstance(response.get("usage"), Mapping):
        raise ValueError("selected provider response safe fields are malformed")
    error = str(response["error_class"]) if response.get("error_class") is not None else None
    usage = response["usage"]
    assert isinstance(usage, Mapping)
    return error, usage


def _usage_equal(left: Mapping[str, object], right: Mapping[str, object]) -> bool:
    return all(
        str(left.get(name)) == str(right.get(name))
        for name in ("input_tokens", "output_tokens", "cost_usd")
    )


def inspect_retained_fixed_batch(
    repo: Path,
    root: Path,
    *,
    expected_lock: str = EXPECTED_OUTPUT_LOCK,
) -> RetainedFixedBatchDiagnostic:
    """Perform the exact bounded read and prove retained-state immutability."""

    inventory = _secure_inventory(root)
    lock = _secure_json(root, "output-lock.json", allowed=READABLE_FIXED)
    mutable_lock = dict(lock)
    actual_lock = mutable_lock.pop("lock_hash", None)
    if actual_lock != f"sha256:{sha256_hex(canonical_json(mutable_lock))}":
        raise ValueError("output-lock self-commitment mismatch")
    if actual_lock != expected_lock:
        raise ValueError("output lock differs from the permanent public commitment")
    if (
        mutable_lock.get("campaign_id") != CAMPAIGN_ID
        or mutable_lock.get("batch_id") != BATCH_ID
        or mutable_lock.get("provider_phase_closed") is not True
    ):
        raise ValueError("output-lock identity or provider closure mismatch")
    raw_commitments = mutable_lock.get("objects")
    if not isinstance(raw_commitments, Mapping) or len(raw_commitments) != EXPECTED_LOCKED_OBJECTS:
        raise ValueError("output-lock object count differs")
    commitments = {str(name): str(value) for name, value in raw_commitments.items()}
    locked_relatives = frozenset(_locked_relative(name) for name in commitments)
    if frozenset(inventory) != locked_relatives | EXPECTED_NONLOCKED:
        raise ValueError("retained inventory differs from the exact frozen shape")
    envelope_relatives = frozenset(
        _locked_relative(name)
        for name in commitments
        if name.startswith("trace/") or name.startswith("provider-response/")
    )
    byte_readable = frozenset(READABLE_FIXED - {"output-lock.json"}) | envelope_relatives
    before = _snapshot(
        root,
        inventory,
        byte_readable=byte_readable | {"output-lock.json"},
        commitments=commitments,
    )
    identity = _secure_json(root, "execution-identity.json", allowed=READABLE_FIXED)
    state = _secure_json(root, "provider-stage-state.json", allowed=READABLE_FIXED)
    access = _validate_ledger(_secure_read(root, "access-log.jsonl", allowed=READABLE_FIXED))
    usage = _validate_ledger(_secure_read(root, "usage-cost-ledger.jsonl", allowed=READABLE_FIXED))
    if (
        identity.get("campaign_id") != CAMPAIGN_ID
        or identity.get("batch_id") != BATCH_ID
        or identity.get("execution_commit") != EXECUTION_COMMIT
    ):
        raise ValueError("execution identity mismatch")
    if (
        state.get("public_canary_complete") is not True
        or state.get("custody_complete") is not True
        or state.get("private_prefix_complete") is not True
        or state.get("fixed_full_batch_complete") is not False
        or state.get("quarantined") is not True
        or state.get("quarantine_stage") != "fixed-full-batch"
        or state.get("quarantine_failure_class") != "fixed-full-batch-failure"
    ):
        raise ValueError("provider-stage state differs from the permanent boundary")
    if tuple(record.get("event_type") for record in usage[-2:]) != (
        "batch-quarantine",
        "provider-phase-closed",
    ):
        raise ValueError("quarantine and provider-close ordering changed")
    if lock.get("ledger_head") != usage[-1].get("record_hash"):
        raise ValueError("output-lock ledger head mismatch")
    if not any(
        record.get("operation") == "fresh-private-ten-percent-prefix-pass" for record in access
    ):
        raise ValueError("private-prefix access record is absent")

    envelopes: list[EnvelopeMetadata] = []
    for name, commitment in sorted(commitments.items()):
        if not (name.startswith("trace/") or name.startswith("provider-response/")):
            continue
        relative = _locked_relative(name)
        envelopes.append(
            _load_envelope_metadata(
                root,
                relative,
                object_name=name,
                locked_commitment=commitment,
            )
        )
    response_envelopes = tuple(item for item in envelopes if item.object_class == "response")
    trace_envelopes = tuple(item for item in envelopes if item.object_class == "trace")
    if len(response_envelopes) != EXPECTED_RESPONSES or len(trace_envelopes) != EXPECTED_TRACES:
        raise ValueError("encrypted response or trace structural count differs")
    response_domains = Counter(item.domain for item in response_envelopes)
    trace_domains = Counter(item.domain for item in trace_envelopes)
    if any(count != 1 for count in (*response_domains.values(), *trace_domains.values())):
        raise ValueError("duplicate encrypted response or trace domain")

    reconstruction = reconstruct_structure(usage, state, envelopes)
    selected_key, selected_records, neighbors = select_bounded_context(usage)
    expected_response_domains = {
        f"provider-response/{selected_key}/attempt-{int(str(record['transport_attempt']))}"
        for record in selected_records
    }
    selected_responses = tuple(
        item for item in response_envelopes if item.domain in expected_response_domains
    )
    if len(selected_responses) != len(selected_records) or len(selected_responses) > 2:
        raise ValueError("selected response objects do not match the bounded ledger context")

    full_traces = tuple(
        item for item in trace_envelopes if _trace_stage(item.domain) == "fixed-full-batch"
    )
    latest_mtime = max(item.mtime_ns for item in full_traces)
    latest_traces = tuple(item for item in full_traces if item.mtime_ns == latest_mtime)
    selected_trace = latest_traces[0] if len(latest_traces) == 1 else None
    key_path = root / "operational-key.bin"
    _require_secure_regular(key_path)
    key = bytearray(key_path.read_bytes())
    if len(key) != 32:
        raise ValueError("operational key length changed")
    selected_trace_errors: tuple[str, ...] = ()
    selected_trace_retry_count = 0
    trace_usage: Mapping[str, object] | None = None
    trace_authenticated = True
    response_details: list[tuple[str | None, Mapping[str, object]]] = []
    try:
        for item in selected_responses:
            value = _decrypt_selected(root / item.relative_path, key)
            response_details.append(_response_safe_details(value))
            value = None
        if selected_trace is not None:
            trace_value = _decrypt_selected(root / selected_trace.relative_path, key)
            selected_trace_errors, selected_trace_retry_count, trace_usage = _safe_trace_details(
                trace_value
            )
            trace_value = None
    finally:
        for index in range(len(key)):
            key[index] = 0

    final_record = selected_records[-1]
    direct_trace = (
        trace_usage is not None
        and _usage_equal(trace_usage, final_record)
        and bool(response_details)
        and _usage_equal(trace_usage, response_details[-1][1])
        and selected_trace is not None
        and f"/{final_record.get('model')}/" in selected_trace.domain
    )
    selected_provider_error = (
        str(final_record["error_class"]) if final_record.get("error_class") is not None else None
    )
    terminal_keys = _terminal_call_keys(usage)
    reconstruction = StructuralReconstruction(
        **{
            **asdict(reconstruction),
            "all_selected_run_outputs_exist": (
                len(selected_responses) == len(selected_records) and selected_trace is not None
            ),
        }
    )
    evidence = CausalEvidence(
        integrity_ok=True,
        response_ledger_one_to_one=(
            len(response_envelopes)
            == sum(record.get("event_type") == "provider-call" for record in usage)
        ),
        duplicate_or_conflicting_call_key=False,
        cap_guard=False,
        pairing_complete=reconstruction.all_500_pairing_records_exist,
        fixed_full_batch_marker=reconstruction.fixed_full_batch_completion_marker,
        selected_trace_authenticated=trace_authenticated,
        selected_trace_errors=selected_trace_errors,
        selected_trace_retry_count=selected_trace_retry_count,
        selected_provider_error=selected_provider_error,
        selected_call_terminal=selected_key in terminal_keys,
        all_outputs_exist=reconstruction.all_selected_run_outputs_exist,
        direct_trace_correspondence=direct_trace,
        safe_exception_code_persisted=False,
    )
    causal_class, actor, safe_code = classify_cause(evidence)

    after_inventory = _secure_inventory(root)
    after = _snapshot(
        root,
        after_inventory,
        byte_readable=byte_readable | {"output-lock.json"},
        commitments=commitments,
    )
    if inventory != after_inventory or before != after:
        raise PermissionError("retained state mutated during the diagnostic")
    return RetainedFixedBatchDiagnostic(
        task_id=TASK_ID,
        source_task_id=SOURCE_TASK_ID,
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
        execution_commit=EXECUTION_COMMIT,
        output_lock_verified_within_allowlist=True,
        output_lock_commitment=expected_lock,
        locked_objects=len(commitments),
        inventory_verified=True,
        append_only_ledgers_verified=True,
        retained_state_mutated=False,
        reconstruction=reconstruction,
        selected_call_key_hash=f"sha256:{sha256_hex(selected_key.encode())}",
        selected_attempt_records=len(selected_records),
        bounded_neighbor_records=len(neighbors),
        selected_response_objects=len(selected_responses),
        selected_trace_objects=int(selected_trace is not None),
        selected_trace_domain_hash=(
            f"sha256:{sha256_hex(selected_trace.domain.encode())}"
            if selected_trace is not None
            else None
        ),
        exception_stage="fixed-full-batch",
        safe_error_code=safe_code,
        causal_class=causal_class,
        causal_actor=actor,
        private_content_published=False,
        operational_key_retained=False,
        provider_calls=0,
        credential_reads=0,
        spend_usd="0",
        private_paths_disclosed=False,
    )


def _secure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink() or not path.is_dir():
        raise PermissionError("diagnostic output directory is unsafe")
    path.chmod(0o700)


def _exclusive_create(path: Path, payload: bytes) -> None:
    _secure_directory(path.parent)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        offset = 0
        while offset < len(payload):
            offset += os.write(descriptor, payload[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def validate_public_diagnostic(value: Mapping[str, object]) -> None:
    """Reject private content, host paths, identifiers, and performance fields."""

    forbidden_keys = {
        "seed",
        "task_key",
        "answer_key",
        "operational_key",
        "task_text",
        "answer",
        "raw_output",
        "credential",
        "private_path",
        "task_level_metrics",
        "architecture_comparison",
        "model_comparison",
        "selected_call_key",
        "selected_trace_domain",
    }

    def visit(item: object) -> None:
        if isinstance(item, Mapping):
            for name, child in item.items():
                if str(name).lower() in forbidden_keys:
                    raise ValueError("public diagnostic contains a forbidden field")
                visit(child)
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
            for child in item:
                visit(child)
        elif isinstance(item, str) and (
            item.startswith(("/", "file://")) or "/Users/" in item or "\\Users\\" in item
        ):
            raise ValueError("public diagnostic contains a host path")

    visit(value)


def public_result(
    diagnosis: RetainedFixedBatchDiagnostic, *, repo: Path | None = None
) -> Mapping[str, object]:
    """Render the only public-safe diagnostic surface."""

    reconstruction = diagnosis.reconstruction
    value: dict[str, object] = {
        "status": (
            "stop" if diagnosis.causal_class == "retained-state-integrity-mismatch-stop" else "pass"
        ),
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "output_lock_verified_within_allowlist": diagnosis.output_lock_verified_within_allowlist,
        "inventory_verified": diagnosis.inventory_verified,
        "append_only_ledgers_verified": diagnosis.append_only_ledgers_verified,
        "retained_state_mutated": diagnosis.retained_state_mutated,
        "planned_logical_calls": reconstruction.planned_logical_calls,
        "actual_attempts": reconstruction.actual_attempts,
        "unique_logical_calls": reconstruction.unique_logical_calls,
        "completed_logical_calls": reconstruction.completed_logical_calls,
        "recovered_attempts_by_provider": dict(reconstruction.recovered_attempts_by_provider),
        "terminal_attempts_by_provider": dict(reconstruction.terminal_attempts_by_provider),
        "completed_private_pairings": reconstruction.completed_private_pairings,
        "all_500_pairing_records_exist": reconstruction.all_500_pairing_records_exist,
        "fixed_full_batch_completion_marker": reconstruction.fixed_full_batch_completion_marker,
        "last_durable_stage": reconstruction.exact_last_durable_stage,
        "selected_run_outputs_exist": reconstruction.all_selected_run_outputs_exist,
        "exception_stage": diagnosis.exception_stage,
        "safe_error_code": diagnosis.safe_error_code,
        "causal_class": diagnosis.causal_class,
        "causal_actor": diagnosis.causal_actor,
        "private_content_published": False,
        "operational_key_retained": False,
        "private_read_authority_closed": True,
        "provider_calls": 0,
        "credential_reads": 0,
        "spend_usd": "0",
        "private_paths_disclosed": False,
        "performance_evidence_created": False,
    }
    validate_public_diagnostic(value)
    schema_root = repo or Path.cwd()
    schema = json.loads((schema_root / PUBLIC_RESULT_SCHEMA_PATH).read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    if errors:
        raise ValueError(f"public fixed-batch diagnostic schema failed: {errors[0].message}")
    return value


def _integrity_stop_diagnosis() -> RetainedFixedBatchDiagnostic:
    """Produce a content-free stop record after an in-read integrity failure."""

    return RetainedFixedBatchDiagnostic(
        task_id=TASK_ID,
        source_task_id=SOURCE_TASK_ID,
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
        execution_commit=EXECUTION_COMMIT,
        output_lock_verified_within_allowlist=False,
        output_lock_commitment=EXPECTED_OUTPUT_LOCK,
        locked_objects=0,
        inventory_verified=False,
        append_only_ledgers_verified=False,
        retained_state_mutated=False,
        reconstruction=StructuralReconstruction(
            planned_logical_calls=3016,
            actual_attempts=0,
            unique_logical_calls=0,
            completed_logical_calls=0,
            recovered_attempts_by_provider={"OpenAI": 0, "Anthropic": 0},
            terminal_attempts_by_provider={"OpenAI": 0, "Anthropic": 0},
            completed_private_pairings=0,
            private_prefix_pairings=0,
            fixed_full_batch_pairings=0,
            public_canary_traces=0,
            all_500_pairing_records_exist=False,
            fixed_full_batch_completion_marker=False,
            exact_last_durable_stage="not-established-integrity-stop",
            all_selected_run_outputs_exist=False,
        ),
        selected_call_key_hash="not-selected",
        selected_attempt_records=0,
        bounded_neighbor_records=0,
        selected_response_objects=0,
        selected_trace_objects=0,
        selected_trace_domain_hash=None,
        exception_stage="fixed-full-batch",
        safe_error_code="retained-integrity-mismatch",
        causal_class="retained-state-integrity-mismatch-stop",
        causal_actor="retained-integrity",
        private_content_published=False,
        operational_key_retained=False,
        provider_calls=0,
        credential_reads=0,
        spend_usd="0",
        private_paths_disclosed=False,
    )


def run_read_only_fixed_batch_diagnostic(repo: Path) -> Mapping[str, object]:
    """Execute the one-use diagnostic after exact generic owner authorization."""

    authorization = load_diagnostic_authorization(repo)
    output_root = diagnostic_output_root()
    marker = output_root / "read-intent.json"
    detailed = output_root / "diagnostic.json"
    if marker.exists() or detailed.exists():
        raise PermissionError("AO-0009 private-read authority is already consumed")
    marker_payload = {
        "schema_version": "ao-0009-fixed-batch-diagnostic-read-intent-v1",
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "gate_id": GATE_ID,
        "execution_commit": authorization["commit"],
        "single_use": True,
        "retained_state_mutation_authorized": False,
        "second_read_authorized": False,
    }
    _exclusive_create(marker, canonical_json(marker_payload) + b"\n")
    try:
        diagnosis = inspect_retained_fixed_batch(repo, private_state_root())
    except (OSError, PermissionError, ValueError):
        diagnosis = _integrity_stop_diagnosis()
    _exclusive_create(detailed, canonical_json(asdict(diagnosis)) + b"\n")
    return public_result(diagnosis, repo=repo)
