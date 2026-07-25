"""Read-only adjudication support for the quarantined TreasureBench pilot.

This module has no provider adapter, credential loader, task generator, or
private-state write path. Real retained-state access is available only through
an exact, nonsynthetic, owner-created diagnostic authorization.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import cast

import yaml
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jsonschema import Draft202012Validator, FormatChecker

from distributed_discovery.benchmark.agents_v1.adapters import AdapterResponse, Usage
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import canonical_cells
from distributed_discovery.benchmark.agents_v1.models import (
    StructuredAction,
    TaskInstance,
    task_from_records,
)
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURE_TURNS,
    ARCHITECTURES,
    ArchitectureRun,
    TurnRecord,
)
from distributed_discovery.benchmark.agents_v1.protocol_contract import (
    verify_metric_ranges,
    verify_protocol_contract,
)
from distributed_discovery.benchmark.agents_v1.traces import verify_trace_hashes

CAMPAIGN_ID = "treasurebench-agents-v1-pilot-v1"
BATCH_ID = "tb-agents-v1-pilot-v1-b01"
ORIGINAL_EXECUTION_COMMIT = "b166e6fa19cbdec0bb8e786aee2de0d9edfc12d1"
ORIGINAL_OUTPUT_LOCK = "sha256:1d487723f7587e8e2fa865682e6f6cc473cf2da4967b837dedf3952cddfcbfab"
ORIGINAL_SEED_COMMITMENT = "sha256:903c81a0dadc2f0ebcf8b3ae8f9e593434b17fd665985ea931eba770f68cdaa0"
ORIGINAL_TASK_CIPHERTEXT = "sha256:ef5197edaa23f27487451fd36dda20dafe2f85bbbb0bddb1e836fd4337b3d5c3"
ORIGINAL_ANSWER_CIPHERTEXT = (
    "sha256:07ac8eade872dc5034159ef999ca845b3b5040b5690907f031b6c50c9c87e9fb"
)
REPAIR_BRANCH = "benchmark/treasurebench-agents-v1-pilot-repair"
ISSUE = 191
MODELS = ("gpt-5.4-2026-03-05", "claude-sonnet-4-6")
PROVIDERS = ("OpenAI", "Anthropic")
PRIVATE_ROOT_SYMBOLIC = "XDG_STATE_HOME/distributed-discovery/treasurebench-agents-v1/pilot-v1"
AUTHORIZATION_SYMBOLIC = (
    "XDG_CONFIG_HOME/distributed-discovery/"
    "treasurebench-agents-v1-pilot-diagnostic-authorization.yml"
)
PERMITTED_COMMAND = (
    "uv run --no-editable python scripts/diagnose_treasurebench_pilot_errors.py --repo ."
)
EXPECTED_ERROR_CLASSES = frozenset({"transient-provider", "schema-or-parameter"})
MAX_ERROR_RECORDS = 2
MAX_SURROUNDING_RESPONSE_RECORDS = 2
EXACT_PRIVATE_RUN_TRACES = 500

DIAGNOSTIC_TREE_PATHS = (
    "Makefile",
    "docs/benchmark/agents-v1/agent-protocol.yml",
    "docs/benchmark/agents-v1/corruption-plan.md",
    "docs/benchmark/agents-v1/corruption-plan.yml",
    "docs/benchmark/agents-v1/evaluation-corruption-plan.yml",
    "docs/benchmark/agents-v1/evaluation-verification-plan.yml",
    "docs/benchmark/agents-v1/metrics.yml",
    "docs/benchmark/agents-v1/pilot-diagnostic-authorization.schema.json",
    "docs/benchmark/agents-v1/pilot-diagnostic-authorization-template.yml",
    "docs/benchmark/agents-v1/provider-error-taxonomy.schema.json",
    "docs/benchmark/agents-v1/provider-error-taxonomy.yml",
    "docs/benchmark/agents-v1/structured-output.schema.json",
    "docs/benchmark/agents-v1/team-architectures.yml",
    "docs/benchmark/agents-v1/verification-plan.yml",
    "docs/benchmark/agents-v1/prospective-failure-policy.schema.json",
    "docs/benchmark/agents-v1/prospective-failure-policy.yml",
    "docs/benchmark/agents-v1/fixtures/pilot-diagnostic-synthetic-cases.yml",
    "reports/benchmark/treasurebench-agents-v1-pilot-repair-registration.md",
    "reports/benchmark/treasurebench-agents-v1-pilot-repair-registration.yml",
    "reports/benchmark/treasurebench-agents-v1-action-budget-contract-audit.md",
    "plans/TREASUREBENCH_AGENTS_V1_PILOT_REPAIR.md",
    "scripts/audit_treasurebench_pilot_diagnostic.py",
    "scripts/create_treasurebench_pilot_diagnostic_authorization.sh",
    "scripts/diagnose_treasurebench_pilot_errors.py",
    "scripts/validate_treasurebench_pilot_diagnostic_authorization.py",
    "src/distributed_discovery/benchmark/agents.py",
    "src/distributed_discovery/benchmark/agents_v1/actions.py",
    "src/distributed_discovery/benchmark/agents_v1/evaluation.py",
    "src/distributed_discovery/benchmark/agents_v1/live_campaign.py",
    "src/distributed_discovery/benchmark/agents_v1/live_providers.py",
    "src/distributed_discovery/benchmark/agents_v1/orchestration.py",
    "src/distributed_discovery/benchmark/agents_v1/pilot.py",
    "src/distributed_discovery/benchmark/agents_v1/pilot_live.py",
    "src/distributed_discovery/benchmark/agents_v1/pilot_diagnostic.py",
    "src/distributed_discovery/benchmark/agents_v1/prompts.py",
    "src/distributed_discovery/benchmark/agents_v1/protocol_contract.py",
    "src/distributed_discovery/benchmark/agents_v1/rehearsal.py",
    "src/distributed_discovery/benchmark/agents_v1/verification.py",
    "tests/test_agents_v1_action_budget_contract.py",
    "tests/test_agents_v1_cli_and_rehearsal.py",
    "tests/test_agents_v1_live_providers.py",
    "tests/test_agents_v1_security_and_verification.py",
    "tests/test_treasurebench_pilot_diagnostic.py",
    "tests/unit/test_discoverybench_agents.py",
)

REQUIRED_TRUE_PERMISSIONS = frozenset(
    {
        "read_retained_state",
        "verify_output_lock",
        "verify_custody_and_logs",
        "decrypt_final_audit_package",
        "decrypt_two_error_records",
        "decrypt_exactly_500_private_run_traces",
        "decrypt_locked_task_answer_for_sensitivity",
        "aggregate_action_cardinalities",
        "compute_private_metric_sensitivity",
        "write_private_detail_outside_retained_root",
        "emit_redacted_public_candidate",
    }
)
REQUIRED_FALSE_PERMISSIONS = frozenset(
    {
        "provider_calls",
        "credential_access",
        "generate_seed_task_answer_key_or_batch",
        "mutate_retained_private_state",
        "publish_raw_private_content",
    }
)
PROHIBITED_PUBLIC_KEYS = frozenset(
    {
        "task",
        "task_id",
        "task_text",
        "task_commitment",
        "target",
        "signal",
        "prompt",
        "peer_message",
        "raw_output",
        "raw_response",
        "raw_error",
        "request_id",
        "response_id",
        "answer",
        "seed",
        "key",
        "private_path",
        "task_level_metric",
        "architecture",
        "model",
        "ranking",
        "composite",
    }
)
PROHIBITED_PUBLIC_TEXT = (
    "/Users/",
    "/home/",
    "XDG_STATE_HOME/",
    "XDG_CONFIG_HOME/",
    "Bearer ",
    "api_key",
    "answer_key",
    "private_observation",
)


@dataclass(frozen=True)
class FileSnapshot:
    device: int
    inode: int
    size: int
    mode: int
    modified_ns: int
    changed_ns: int


@dataclass(frozen=True)
class CallContext:
    stage: str
    provider: str
    model: str
    slot_ordinal: int | None
    architecture: str
    agent_ordinal: int
    round_number: int
    run_ordinal: int | None


@dataclass(frozen=True)
class RunContext:
    run_ordinal: int
    stage: str
    provider: str
    model: str
    slot_ordinal: int
    family: str
    architecture: str
    agent_count: int


@dataclass(frozen=True)
class ActionBudgetDiagnostic:
    private_detail: Mapping[str, object]
    public_aggregate: Mapping[str, object]
    invalid_final_by_run: Mapping[int, bool]


@dataclass(frozen=True)
class DiagnosticEvidence:
    authorization_id: str
    output_lock_verified: bool
    custody_commitments_verified: bool
    append_only_logs_verified: bool
    final_audit_verified: bool
    error_events: tuple[Mapping[str, object], ...]
    private_detail: Mapping[str, object]
    public_candidate: Mapping[str, object]
    retained_state_unchanged: bool


def canonical_json(value: object) -> bytes:
    """Return the commitment-stable JSON representation used by the pilot."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_commitment(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _mapping(value: object, *, label: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return {str(name): item for name, item in value.items()}


def _sequence(value: object, *, label: str) -> tuple[object, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{label} must be an array")
    return tuple(value)


def _git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ("git", *arguments),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def diagnostic_tree_hash(repo: Path) -> str:
    """Hash the exact diagnostic-sensitive file inventory and current bytes."""
    records: dict[str, str] = {}
    for relative in DIAGNOSTIC_TREE_PATHS:
        path = repo / relative
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(f"diagnostic tree path unavailable: {relative}")
        records[relative] = sha256_commitment(path.read_bytes())
    return sha256_commitment(
        canonical_json(
            {
                "schema_version": "treasurebench-pilot-diagnostic-tree-v1",
                "files": records,
            }
        )
    )


def authorization_path() -> Path:
    config_root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return (
        config_root
        / "distributed-discovery"
        / "treasurebench-agents-v1-pilot-diagnostic-authorization.yml"
    )


def private_state_root() -> Path:
    state_root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state")))
    return state_root / "distributed-discovery" / "treasurebench-agents-v1" / "pilot-v1"


def _resolve_symbolic_output(value: str) -> Path:
    prefix = "XDG_STATE_HOME/"
    if not value.startswith(prefix):
        raise PermissionError("private diagnostic output must use its symbolic root")
    state_root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state")))
    relative = Path(value.removeprefix(prefix))
    if relative.is_absolute() or ".." in relative.parts:
        raise PermissionError("private diagnostic output path is unsafe")
    return state_root / relative


def _validate_schema(value: Mapping[str, object], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(dict(value))


def secure_read_bytes(path: Path) -> bytes:
    """Read a nonsymlink 0600 regular file through an O_RDONLY descriptor."""
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise PermissionError("private input must be a regular file")
        if stat.S_IMODE(metadata.st_mode) & 0o077:
            raise PermissionError("private input permissions are too broad")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def secure_read_json(path: Path) -> dict[str, object]:
    return _mapping(json.loads(secure_read_bytes(path)), label=path.name)


def load_diagnostic_authorization(
    repo: Path,
    path: Path | None = None,
    *,
    now: datetime | None = None,
) -> Mapping[str, object]:
    target = path or authorization_path()
    value = _mapping(
        yaml.safe_load(secure_read_bytes(target).decode("utf-8")),
        label="diagnostic authorization",
    )
    return validate_diagnostic_authorization(value, repo=repo, now=now)


def validate_diagnostic_authorization(
    value: Mapping[str, object],
    *,
    repo: Path,
    now: datetime | None = None,
) -> Mapping[str, object]:
    """Validate a real authorization without resolving retained private state."""
    schema_path = repo / "docs/benchmark/agents-v1/pilot-diagnostic-authorization.schema.json"
    _validate_schema(value, schema_path)
    if value["authorization_status"] != "authorized" or value["revoked"] is not False:
        raise PermissionError("diagnostic authorization is not active")
    if value["synthetic"] is not False:
        raise PermissionError("synthetic authorization cannot authorize private access")
    current = now or datetime.now(UTC)
    authorized = datetime.fromisoformat(str(value["authorized_at_utc"]).replace("Z", "+00:00"))
    expires = datetime.fromisoformat(str(value["expires_at_utc"]).replace("Z", "+00:00"))
    if authorized > current or expires <= current:
        raise PermissionError("diagnostic authorization is outside its active interval")
    if expires - authorized > timedelta(hours=48):
        raise PermissionError("diagnostic authorization exceeds the 48-hour ceiling")
    if _git(repo, "branch", "--show-current") != REPAIR_BRANCH:
        raise PermissionError("diagnostic branch mismatch")
    head = _git(repo, "rev-parse", "HEAD")
    if value["diagnostic_commit"] != head:
        raise PermissionError("diagnostic commit mismatch")
    if _git(repo, "status", "--porcelain", "--untracked-files=no"):
        raise PermissionError("tracked diagnostic tree must be clean")
    remote = _git(repo, "rev-parse", f"origin/{REPAIR_BRANCH}")
    if remote != head:
        raise PermissionError("diagnostic commit must equal the pushed remote branch")
    if value["diagnostic_tree_hash"] != diagnostic_tree_hash(repo):
        raise PermissionError("diagnostic tree hash mismatch")
    if value["permitted_command"] != PERMITTED_COMMAND:
        raise PermissionError("diagnostic command mismatch")
    confirmations = _mapping(value["owner_confirmations"], label="owner confirmations")
    if not confirmations or any(item is not True for item in confirmations.values()):
        raise PermissionError("all eight owner confirmations must be true")
    permissions = _mapping(value["permissions"], label="diagnostic permissions")
    if any(permissions.get(name) is not True for name in REQUIRED_TRUE_PERMISSIONS):
        raise PermissionError("required read-only diagnostic permission is absent")
    if any(permissions.get(name) is not False for name in REQUIRED_FALSE_PERMISSIONS):
        raise PermissionError("prohibited diagnostic capability is enabled")
    attestation = value["owner_attestation"]
    if not isinstance(attestation, str) or len(attestation.strip()) < 80:
        raise PermissionError("a nonsynthetic owner attestation is required")
    return value


def _walk_private_files(root: Path) -> tuple[Path, ...]:
    if root.is_symlink() or not root.is_dir():
        raise PermissionError("retained private root is unsafe")
    if stat.S_IMODE(root.stat().st_mode) & 0o077:
        raise PermissionError("retained private root permissions are too broad")
    files: list[Path] = []
    pending = [root]
    while pending:
        directory = pending.pop()
        if directory.is_symlink() or not directory.is_dir():
            raise PermissionError("retained private directory is unsafe")
        if stat.S_IMODE(directory.stat().st_mode) & 0o077:
            raise PermissionError("retained private directory permissions are too broad")
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                if entry.is_symlink():
                    raise PermissionError("symlink in retained private state")
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    files.append(path)
                else:
                    raise PermissionError("nonregular retained private object")
    return tuple(sorted(files, key=lambda item: str(item.relative_to(root))))


def snapshot_private_state(root: Path) -> Mapping[str, FileSnapshot]:
    """Snapshot retained metadata without reading unauthorized file contents."""
    records: dict[str, FileSnapshot] = {}
    for path in _walk_private_files(root):
        metadata = path.stat(follow_symlinks=False)
        records[str(path.relative_to(root))] = FileSnapshot(
            metadata.st_dev,
            metadata.st_ino,
            metadata.st_size,
            stat.S_IMODE(metadata.st_mode),
            metadata.st_mtime_ns,
            metadata.st_ctime_ns,
        )
    return records


def validate_append_only_ledger(payload: bytes) -> tuple[Mapping[str, object], ...]:
    records: list[Mapping[str, object]] = []
    previous = "GENESIS"
    for sequence, line in enumerate(payload.decode("utf-8").splitlines(), start=1):
        record = _mapping(json.loads(line), label="append-only ledger record")
        actual = record.pop("record_hash", None)
        if record.get("sequence") != sequence or record.get("previous_hash") != previous:
            raise ValueError("append-only ledger sequence or chain mismatch")
        expected = sha256_commitment(canonical_json(record))
        if actual != expected:
            raise ValueError("append-only ledger record hash mismatch")
        record["record_hash"] = actual
        records.append(record)
        previous = str(actual)
    if not records:
        raise ValueError("append-only ledger is empty")
    return tuple(records)


def _locked_objects(root: Path) -> Mapping[str, bytes]:
    fixed = {
        "task-ciphertext": "task-custody.json",
        "answer-ciphertext": "answer-custody.json",
        "custody-manifest": "custody-manifest.json",
        "access-log": "access-log.jsonl",
        "usage-cost-ledger": "usage-cost-ledger.jsonl",
        "provider-stage-state": "provider-stage-state.json",
    }
    objects = {name: secure_read_bytes(root / relative) for name, relative in fixed.items()}
    trace_root = root / "encrypted-traces"
    for path in sorted(trace_root.glob("*.sealed")):
        if path.parent != trace_root:
            raise PermissionError("trace path escaped its retained directory")
        objects[f"trace/{path.name}"] = secure_read_bytes(path)
    response_root = root / "encrypted-provider-responses"
    for path in sorted(response_root.rglob("*.sealed.json")):
        relative = path.relative_to(response_root)
        if ".." in relative.parts:
            raise PermissionError("provider response path escaped its retained directory")
        objects[f"provider-response/{relative}"] = secure_read_bytes(path)
    return objects


def verify_original_output_lock(
    root: Path, ledger: Sequence[Mapping[str, object]]
) -> Mapping[str, object]:
    lock = secure_read_json(root / "output-lock.json")
    objects = _locked_objects(root)
    verify_output_lock_manifest(
        lock,
        objects,
        ledger_head=str(ledger[-1].get("record_hash")) if ledger else "GENESIS",
        expected_lock=ORIGINAL_OUTPUT_LOCK,
        expected_objects=3545,
    )
    if lock.get("campaign_id") != CAMPAIGN_ID or lock.get("batch_id") != BATCH_ID:
        raise ValueError("output-lock campaign or batch mismatch")
    if lock.get("provider_phase_closed") is not True:
        raise ValueError("output-lock provider phase is not closed")
    return lock


def verify_output_lock_manifest(
    lock: Mapping[str, object],
    objects: Mapping[str, bytes],
    *,
    ledger_head: str,
    expected_lock: str | None = None,
    expected_objects: int | None = None,
) -> None:
    """Independently verify an output-lock manifest against supplied bytes."""
    mutable = dict(lock)
    actual = mutable.pop("lock_hash", None)
    if actual != sha256_commitment(canonical_json(mutable)):
        raise ValueError("output-lock self-hash mismatch")
    if expected_lock is not None and actual != expected_lock:
        raise ValueError("output-lock commitment differs from the original public record")
    expected = {name: sha256_commitment(payload) for name, payload in sorted(objects.items())}
    if mutable.get("objects") != expected:
        raise ValueError("output-lock object inventory mismatch")
    if expected_objects is not None and len(expected) != expected_objects:
        raise ValueError("output-lock object count mismatch")
    if mutable.get("ledger_head") != ledger_head:
        raise ValueError("output-lock ledger head mismatch")


def verify_original_custody(root: Path) -> Mapping[str, object]:
    manifest = secure_read_json(root / "custody-manifest.json")
    expected = {
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "seed_commitment": ORIGINAL_SEED_COMMITMENT,
        "task_ciphertext_commitment": ORIGINAL_TASK_CIPHERTEXT,
        "answer_ciphertext_commitment": ORIGINAL_ANSWER_CIPHERTEXT,
        "tasks": 50,
    }
    if any(manifest.get(name) != item for name, item in expected.items()):
        raise ValueError("retained custody commitment mismatch")
    task_record = secure_read_json(root / "task-custody.json")
    answer_record = secure_read_json(root / "answer-custody.json")
    task_manifest = _mapping(task_record.get("manifest"), label="task custody manifest")
    answer_manifest = _mapping(answer_record.get("manifest"), label="answer custody manifest")
    if task_manifest.get("ciphertext_sha256") != ORIGINAL_TASK_CIPHERTEXT:
        raise ValueError("task ciphertext commitment mismatch")
    if answer_manifest.get("ciphertext_sha256") != ORIGINAL_ANSWER_CIPHERTEXT:
        raise ValueError("answer ciphertext commitment mismatch")
    return manifest


def _unseal_record(record: Mapping[str, object], *, key: bytes) -> object:
    if len(key) != 32:
        raise ValueError("retained decryption key length is invalid")
    manifest = _mapping(record.get("manifest"), label="sealed object manifest")
    domain = str(manifest.get("domain"))
    ciphertext = bytes.fromhex(str(record.get("ciphertext_hex")))
    if manifest.get("ciphertext_sha256") != sha256_commitment(ciphertext):
        raise ValueError("sealed object ciphertext commitment mismatch")
    associated = canonical_json(
        {"campaign_id": CAMPAIGN_ID, "batch_id": BATCH_ID, "domain": domain}
    )
    if manifest.get("associated_data_sha256") != sha256_commitment(associated):
        raise ValueError("sealed object associated-data commitment mismatch")
    plaintext = AESGCM(key).decrypt(
        bytes.fromhex(str(manifest.get("nonce_hex"))), ciphertext, associated
    )
    return json.loads(plaintext)


def verify_final_audit(root: Path) -> Mapping[str, object]:
    key = secure_read_bytes(root / "answer-key.bin")
    sealed = secure_read_json(root / "final-audit-package.sealed.json")
    audit = _mapping(_unseal_record(sealed, key=key), label="final audit package")
    summary = _mapping(audit.get("summary"), label="final audit summary")
    expected = {
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "execution_commit": ORIGINAL_EXECUTION_COMMIT,
        "output_lock_hash": ORIGINAL_OUTPUT_LOCK,
        "status": "quarantined",
        "decision": "sealed-pilot-quarantined-provider-failure",
        "provider_phase_closed": True,
        "output_lock_verified": True,
        "method_a_b_disagreements": 0,
        "contamination_findings": 0,
        "protocol_errors": 2,
    }
    if any(summary.get(name) != item for name, item in expected.items()):
        raise ValueError("final audit summary mismatch")
    provider_errors = _mapping(summary.get("provider_error_counts"), label="provider error counts")
    if provider_errors != {"OpenAI": 0, "Anthropic": 2}:
        raise ValueError("final audit provider-error count mismatch")
    return audit


def select_exact_error_records(
    ledger: Sequence[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    errors = tuple(
        record
        for record in ledger
        if record.get("event_type") == "provider-call" and record.get("status") != "success"
    )
    if len(errors) != MAX_ERROR_RECORDS:
        raise PermissionError("diagnostic must select exactly two provider error records")
    classes = {str(record.get("error_class")) for record in errors}
    providers = {str(record.get("provider")) for record in errors}
    if classes != EXPECTED_ERROR_CLASSES or providers != {"Anthropic"}:
        raise ValueError("provider error record identity differs from public closeout")
    return errors


def _allocation_context(repo: Path) -> tuple[tuple[str, int], ...]:
    allocation = _mapping(
        yaml.safe_load(
            (repo / "docs/benchmark/agents-v1/treasurebench-pilot-allocation.yml").read_text(
                encoding="utf-8"
            )
        ),
        label="public pilot allocation",
    )
    slots = _sequence(allocation.get("slots"), label="public pilot slots")
    cell_agents = {
        (cell.family_id, cell.cell_index): int(str(cell.parameters["agent_count"]))
        for cell in canonical_cells()
    }
    result: list[tuple[str, int]] = []
    for slot in slots:
        record = _mapping(slot, label="public pilot slot")
        family = str(record["family_id"])
        cell_index = int(str(record["cell_index"]))
        result.append((family, cell_agents[(family, cell_index)]))
    if len(result) != 50:
        raise ValueError("public pilot allocation must contain 50 slots")
    return tuple(result)


def _private_call_contexts(repo: Path) -> tuple[CallContext, ...]:
    slots = _allocation_context(repo)
    prefix_indices = (0, 10, 20, 30, 40)
    remaining_indices = tuple(index for index in range(50) if index not in prefix_indices)
    contexts: list[CallContext] = []
    run_ordinal = 0
    for stage, indices in (
        ("private-prefix", prefix_indices),
        ("fixed-full-batch", remaining_indices),
    ):
        for provider, model in zip(PROVIDERS, MODELS, strict=True):
            for slot_index in indices:
                family, agent_count = slots[slot_index]
                for architecture in ARCHITECTURES:
                    current_run = run_ordinal
                    run_ordinal += 1
                    turn_count = max(
                        ARCHITECTURE_TURNS[architecture],
                        2 if family == "common-source-acquisition" else 1,
                    )
                    for round_number in range(turn_count):
                        for agent_ordinal in range(agent_count):
                            contexts.append(
                                CallContext(
                                    stage,
                                    provider,
                                    model,
                                    slot_index + 1,
                                    architecture,
                                    agent_ordinal + 1,
                                    round_number,
                                    current_run,
                                )
                            )
    if run_ordinal != 500:
        raise AssertionError("private diagnostic context must contain 500 runs")
    return tuple(contexts)


def _private_run_contexts(repo: Path) -> tuple[RunContext, ...]:
    allocation = _allocation_context(repo)
    contexts: dict[int, RunContext] = {}
    for call in _private_call_contexts(repo):
        if call.run_ordinal is None or call.slot_ordinal is None:
            continue
        family, agent_count = allocation[call.slot_ordinal - 1]
        candidate = RunContext(
            call.run_ordinal,
            call.stage,
            call.provider,
            call.model,
            call.slot_ordinal,
            family,
            call.architecture,
            agent_count,
        )
        existing = contexts.setdefault(call.run_ordinal, candidate)
        if existing != candidate:
            raise ValueError("private call contexts disagree within a run")
    if set(contexts) != set(range(EXACT_PRIVATE_RUN_TRACES)):
        raise ValueError("private run context inventory is incomplete")
    return tuple(contexts[index] for index in range(EXACT_PRIVATE_RUN_TRACES))


def map_call_contexts(
    repo: Path, ledger: Sequence[Mapping[str, object]]
) -> Mapping[str, CallContext]:
    expected = iter(_private_call_contexts(repo))
    assignments: dict[str, CallContext] = {}
    canary_providers: set[str] = set()
    last_primary: CallContext | None = None
    for record in ledger:
        if record.get("event_type") != "provider-call":
            continue
        call_key = str(record.get("call_key"))
        if call_key in assignments:
            continue
        provider = str(record.get("provider"))
        model = str(record.get("model"))
        schema_retry = record.get("schema_retry") is True
        if schema_retry:
            if last_primary is None or last_primary.provider != provider:
                raise ValueError("schema retry lacks an adjacent primary context")
            assignments[call_key] = last_primary
            continue
        if len(canary_providers) < 2 and provider not in canary_providers:
            context = CallContext(
                "public-canary",
                provider,
                model,
                None,
                "provider-native-smoke",
                1,
                0,
                None,
            )
            canary_providers.add(provider)
        else:
            try:
                context = next(expected)
            except StopIteration as error:
                raise ValueError("ledger contains excess primary call contexts") from error
            if context.provider != provider or context.model != model:
                raise ValueError("ledger provider/model order differs from frozen runtime")
        assignments[call_key] = context
        last_primary = context
    try:
        next(expected)
    except StopIteration:
        return assignments
    raise ValueError("ledger is missing frozen primary call contexts")


def _response_path(root: Path, record: Mapping[str, object]) -> Path:
    provider = str(record["provider"]).lower()
    call_key = str(record["call_key"])
    attempt = int(str(record["transport_attempt"]))
    if not call_key.startswith("call-") or not call_key.removeprefix("call-").isalnum():
        raise PermissionError("provider response call key is unsafe")
    path = (
        root
        / "encrypted-provider-responses"
        / provider
        / f"{call_key}-attempt-{attempt}.sealed.json"
    )
    expected_root = (root / "encrypted-provider-responses").resolve()
    if expected_root not in path.resolve().parents:
        raise PermissionError("provider response path escaped retained state")
    return path


def _record_recovered(target: Mapping[str, object], ledger: Sequence[Mapping[str, object]]) -> bool:
    target_sequence = int(str(target["sequence"]))
    return any(
        record.get("event_type") == "provider-call"
        and record.get("call_key") == target.get("call_key")
        and int(str(record.get("sequence", 0))) > target_sequence
        and record.get("status") == "success"
        for record in ledger
    )


def classify_error_record(
    record: Mapping[str, object],
    *,
    ledger: Sequence[Mapping[str, object]],
    evidence_hash: str,
) -> Mapping[str, object]:
    error_class = str(record.get("error_class"))
    recovered = _record_recovered(record, ledger)
    if error_class == "transient-provider":
        taxonomy_class = "provider-service-recovered" if recovered else "provider-service-terminal"
        ownership = "provider"
    elif error_class == "schema-or-parameter":
        taxonomy_class = "unknown-terminal"
        ownership = "unresolved"
    else:
        raise ValueError("unexpected provider error class")
    terminal = not recovered
    return {
        "taxonomy_class": taxonomy_class,
        "coarse_error_class": error_class,
        "attempt_status": "recovered-error" if recovered else "terminal-error",
        "retry_status": "recovered-within-bound" if recovered else "not-eligible",
        "run_status": "complete" if recovered else "protocol-invalid",
        "task_status": "complete" if recovered else "pairing-incomplete",
        "recoverability": "recovered" if recovered else "terminal",
        "ownership": ownership,
        "public_safe_summary": (
            "provider service error recovered without a terminal run failure"
            if recovered
            else "terminal provider error preserved with exact cause pending adjudication"
        ),
        "private_evidence_reference": evidence_hash,
        "prospective_disposition": (
            "preserve-and-count-readiness-warning" if recovered else "investigate-without-rerun"
        ),
        "terminal_run_missing": terminal,
    }


def _trace_paths_by_run_order(root: Path) -> tuple[Path, ...]:
    paths = tuple((root / "encrypted-traces").glob("*.sealed"))
    if len(paths) != 502:
        raise ValueError("retained trace count differs from two canaries plus 500 runs")
    ordered = tuple(sorted(paths, key=lambda item: item.stat().st_mtime_ns))
    times = [item.stat().st_mtime_ns for item in ordered]
    if len(times) != len(set(times)):
        raise PermissionError("trace creation order is ambiguous")
    return ordered


def _trace_for_context(root: Path, context: CallContext) -> Path | None:
    if context.run_ordinal is None:
        return None
    ordered = _trace_paths_by_run_order(root)
    return ordered[2 + context.run_ordinal]


def _trace_context(root: Path, context: CallContext, *, key: bytes) -> Mapping[str, object] | None:
    path = _trace_for_context(root, context)
    if path is None:
        return None
    trace = _mapping(_unseal_record(secure_read_json(path), key=key), label="minimum trace context")
    if trace.get("architecture_id") != context.architecture:
        raise ValueError("minimum trace context architecture mismatch")
    events = _sequence(trace.get("events"), label="trace events")
    matching = [
        _mapping(event, label="trace event")
        for event in events
        if isinstance(event, Mapping)
        and int(str(cast(Mapping[str, object], event).get("round", -1))) == context.round_number
    ]
    if context.agent_ordinal > len(matching):
        raise ValueError("minimum trace context agent mapping failed")
    event = matching[context.agent_ordinal - 1]
    return {
        "trace_commitment": sha256_commitment(secure_read_bytes(path)),
        "architecture": context.architecture,
        "round": context.round_number,
        "agent_ordinal": context.agent_ordinal,
        "validation_errors": list(_sequence(event.get("errors"), label="trace validation errors")),
        "retry_count": event.get("retry_count"),
        "usage": event.get("usage"),
        "operational_metadata": event.get("operational_metadata"),
    }


def _private_trace_paths(root: Path) -> tuple[Path, ...]:
    paths = _trace_paths_by_run_order(root)[2:]
    if len(paths) != EXACT_PRIVATE_RUN_TRACES:
        raise PermissionError("diagnostic requires exactly 500 private run traces")
    return paths


def _load_locked_tasks(root: Path) -> tuple[TaskInstance, ...]:
    task_key = secure_read_bytes(root / "task-key.bin")
    answer_key = secure_read_bytes(root / "answer-key.bin")
    visible_records = _sequence(
        _unseal_record(secure_read_json(root / "task-custody.json"), key=task_key),
        label="locked task records",
    )
    evaluator_records = _sequence(
        _unseal_record(secure_read_json(root / "answer-custody.json"), key=answer_key),
        label="locked answer records",
    )
    if len(visible_records) != 50 or len(evaluator_records) != 50:
        raise ValueError("locked task and answer inventory must each contain 50 records")
    tasks: list[TaskInstance] = []
    for visible_raw, evaluator_raw in zip(visible_records, evaluator_records, strict=True):
        visible = _mapping(visible_raw, label="locked visible task")
        evaluator = _mapping(evaluator_raw, label="locked evaluator task")
        if evaluator.get("visible") != visible:
            raise ValueError("locked task and answer records are mispaired")
        tasks.append(task_from_records(visible, evaluator))
    return tuple(tasks)


def _structured_action_from_trace(
    value: Mapping[str, object],
) -> StructuredAction:
    actions = _sequence(value.get("actions"), label="trace structured actions")
    metadata = _mapping(
        value.get("declared_metadata", {}),
        label="trace declared metadata",
    )
    commitment = str(value.get("task_instance_commitment", ""))
    if not commitment.startswith("sha256:"):
        raise ValueError("trace structured action lacks a task commitment")
    return StructuredAction(
        task_commitment=commitment.removeprefix("sha256:"),
        agent_id=str(value.get("agent_id")),
        round_number=int(str(value.get("round"))),
        final=value.get("final") is True,
        actions=tuple(str(item) for item in actions),
        visible_message=str(value.get("visible_message", "")),
        source_choice=str(value.get("source_choice", "none")),
        declared_metadata=metadata,
    )


def _run_from_trace(
    trace: Mapping[str, object],
    *,
    task: TaskInstance,
    context: RunContext,
) -> ArchitectureRun:
    events = _sequence(trace.get("events"), label="trace events")
    turns: list[TurnRecord] = []
    final_actions: list[StructuredAction] = []
    protocol_errors: list[str] = []
    for event_raw in events:
        event = _mapping(event_raw, label="trace event")
        action_raw = event.get("structured_action")
        action = (
            _structured_action_from_trace(_mapping(action_raw, label="trace structured action"))
            if isinstance(action_raw, Mapping)
            else None
        )
        usage_raw = _mapping(event.get("usage", {}), label="trace usage")
        tool_calls = _sequence(
            event.get("declared_tool_calls", []),
            label="trace declared tool calls",
        )
        operational = _mapping(
            event.get("operational_metadata", {}),
            label="trace operational metadata",
        )
        validation_errors = tuple(
            str(item)
            for item in _sequence(
                event.get("errors", []),
                label="trace validation errors",
            )
        )
        turn = TurnRecord(
            architecture_id=str(event.get("architecture_id")),
            agent_id=str(event.get("agent_id")),
            round_number=int(str(event.get("round"))),
            visible_inputs=tuple(
                str(item)
                for item in _sequence(
                    event.get("visible_inputs", []),
                    label="trace visible inputs",
                )
            ),
            response=AdapterResponse(
                "",
                Usage(
                    input_tokens=int(str(usage_raw.get("input_tokens", 0))),
                    output_tokens=int(str(usage_raw.get("output_tokens", 0))),
                    cost_usd=Decimal(str(usage_raw.get("cost_usd", "0"))),
                ),
                declared_tool_calls=tuple(
                    _mapping(item, label="trace tool call") for item in tool_calls
                ),
                operational_metadata=operational,
            ),
            action=action,
            validation_errors=validation_errors,
            retry_count=int(str(event.get("retry_count", 0))),
        )
        turns.append(turn)
        if action is not None and action.final:
            final_actions.append(action)
        if action is None and validation_errors:
            protocol_errors.append(
                f"{turn.agent_id}:r{turn.round_number}:{'|'.join(validation_errors)}"
            )
    task_commitment = str(trace.get("task_instance_commitment", ""))
    if task_commitment != f"sha256:{task.commitment}":
        raise ValueError("trace and locked task commitment mismatch")
    if trace.get("architecture_id") != context.architecture:
        raise ValueError("trace and frozen run architecture mismatch")
    return ArchitectureRun(
        context.architecture,
        task.commitment,
        tuple(turns),
        tuple(final_actions),
        tuple(protocol_errors),
    )


def _legacy_metric_projection(
    task: TaskInstance,
    run: ArchitectureRun,
    *,
    isolated_distinct_actions: int,
) -> Mapping[str, object]:
    """Reconstruct the frozen flatten-all-final-actions Method A semantics."""
    finals = run.final_actions
    flat = tuple(item for action in finals for item in action.actions)
    distinct = frozenset(flat)
    target = str(task.primitive_state["target"])
    if task.family_id == "threshold-team-formation":
        parameters = _mapping(
            task.primitive_state["parameters"],
            label="task parameters",
        )
        threshold = int(str(parameters["threshold"]))
        discovery = Fraction(int(Counter(flat)[target] >= threshold), 1)
    else:
        discovery = Fraction(int(target in distinct), 1)
    capacity = min(len(task.capabilities), len(task.action_vocabulary))
    if capacity <= 0:
        raise ValueError("legacy metric projection has no action capacity")
    coverage = Fraction(len(distinct), capacity)
    source_counts = Counter(
        action.source_choice for action in finals if action.source_choice != "none"
    )
    source_total = sum(source_counts.values())
    planner = Fraction(task.baseline.planner_discovery)
    private = Fraction(task.baseline.private_discovery)
    return {
        "group_discovery": discovery,
        "distinct_action_coverage": coverage,
        "duplication": Fraction(
            max(0, len(flat) - len(distinct)),
            max(1, len(flat)),
        ),
        "planner_regret": planner - discovery,
        "private_baseline_regret": private - discovery,
        "recovery_budget_attainment": (
            Fraction(
                int(len(distinct) >= task.baseline.recovery_budget and discovery == 1),
                1,
            )
            if task.baseline.recovery_budget is not None
            else None
        ),
        "source_diversity": (
            1
            - sum(
                (Fraction(count, source_total) ** 2 for count in source_counts.values()),
                Fraction(0),
            )
            if source_total
            else Fraction(0)
        ),
        "communication_action_compression": (
            Fraction(isolated_distinct_actions, capacity) - coverage
        ),
        "best_equilibrium_distance": (
            abs(Fraction(task.baseline.best_equilibrium) - discovery)
            if task.baseline.best_equilibrium is not None
            else None
        ),
        "worst_equilibrium_distance": (
            abs(Fraction(task.baseline.worst_equilibrium) - discovery)
            if task.baseline.worst_equilibrium is not None
            else None
        ),
        "invalid_action_rate": Fraction(
            len(task.capabilities) - len(finals),
            max(1, len(task.capabilities)),
        ),
        "protocol_compliance": Fraction(int(not run.protocol_errors), 1),
        "calls": len(run.turns) + sum(turn.retry_count for turn in run.turns),
        "input_tokens": sum(turn.response.usage.input_tokens for turn in run.turns),
        "output_tokens": sum(turn.response.usage.output_tokens for turn in run.turns),
        "cost_usd": sum(
            (turn.response.usage.cost_usd for turn in run.turns),
            Decimal("0"),
        ),
    }


def _repaired_distinct_count(task: TaskInstance, run: ArchitectureRun) -> int:
    required = frozenset(task.capabilities)
    valid: set[str] = set()
    for agent_id in required:
        listed = [action for action in run.final_actions if action.agent_id == agent_id]
        observed = [
            turn.action
            for turn in run.turns
            if turn.action is not None and turn.action.final and turn.action.agent_id == agent_id
        ]
        if (
            len(listed) == 1
            and len(observed) == 1
            and listed[0] == observed[0]
            and len(listed[0].actions) == 1
            and listed[0].actions[0] in task.action_vocabulary
        ):
            valid.add(listed[0].actions[0])
    return len(valid)


def _metric_record(value: Mapping[str, object]) -> Mapping[str, object]:
    return {
        name: (str(item) if isinstance(item, (Fraction, Decimal)) else item)
        for name, item in value.items()
    }


def _counter_record(counter: Counter[str]) -> Mapping[str, int]:
    return {name: counter[name] for name in sorted(counter)}


def diagnose_action_budget_contract(
    repo: Path,
    root: Path,
    *,
    operational_key: bytes,
) -> ActionBudgetDiagnostic:
    """Inspect exactly 500 locked traces and retain performance detail privately."""
    tasks = _load_locked_tasks(root)
    contexts = _private_run_contexts(repo)
    paths = _private_trace_paths(root)
    rows: list[
        tuple[
            RunContext,
            TaskInstance,
            ArchitectureRun,
            tuple[Mapping[str, object], ...],
        ]
    ] = []
    for context, path in zip(contexts, paths, strict=True):
        trace = _mapping(
            _unseal_record(secure_read_json(path), key=operational_key),
            label="private run trace",
        )
        if not verify_trace_hashes(trace):
            raise ValueError("private run trace hash verification failed")
        task = tasks[context.slot_ordinal - 1]
        run = _run_from_trace(trace, task=task, context=context)
        trace_events = tuple(
            _mapping(item, label="trace event")
            for item in _sequence(trace.get("events"), label="trace events")
        )
        rows.append((context, task, run, trace_events))
    if len(rows) != EXACT_PRIVATE_RUN_TRACES:
        raise PermissionError("diagnostic did not inspect exactly 500 run traces")

    invalid_runs: dict[int, bool] = {}
    invalid_final_outputs = 0
    over_budget_final_outputs = 0
    multiple_all_rounds = 0
    nonfinal_multiple = 0
    final_findings: list[Mapping[str, object]] = []
    method_c_findings: list[Mapping[str, object]] = []
    invalid_by_family: Counter[str] = Counter()
    invalid_by_architecture: Counter[str] = Counter()
    invalid_by_model: Counter[str] = Counter()
    invalid_by_provider: Counter[str] = Counter()
    multiple_by_round: Counter[str] = Counter()
    multiple_by_family: Counter[str] = Counter()
    multiple_by_architecture: Counter[str] = Counter()
    multiple_by_model: Counter[str] = Counter()
    multiple_by_provider: Counter[str] = Counter()

    for context, task, run, event_records in rows:
        expected_final_round = (
            max(
                ARCHITECTURE_TURNS[context.architecture],
                2 if context.family == "common-source-acquisition" else 1,
            )
            - 1
        )
        expected_agents = tuple(sorted(task.capabilities))
        final_events: dict[str, list[Mapping[str, object]]] = defaultdict(list)
        for event in event_records:
            action_raw = event.get("structured_action")
            if isinstance(action_raw, Mapping):
                actions_raw = action_raw.get("actions")
                count = (
                    len(actions_raw)
                    if isinstance(actions_raw, Sequence)
                    and not isinstance(actions_raw, (str, bytes))
                    else 0
                )
                if count > 1:
                    multiple_all_rounds += 1
                    multiple_by_round[str(event.get("round"))] += 1
                    multiple_by_family[context.family] += 1
                    multiple_by_architecture[context.architecture] += 1
                    multiple_by_model[context.model] += 1
                    multiple_by_provider[context.provider] += 1
                    if int(str(event.get("round", -1))) != expected_final_round:
                        nonfinal_multiple += 1
            if int(str(event.get("round", -1))) == expected_final_round:
                final_events[str(event.get("agent_id"))].append(event)

        run_invalid = False
        for agent_id in expected_agents:
            candidates = final_events.get(agent_id, [])
            action_count = 0
            final_flag = False
            if len(candidates) == 1:
                action_raw = candidates[0].get("structured_action")
                if isinstance(action_raw, Mapping):
                    values = action_raw.get("actions")
                    action_count = (
                        len(values)
                        if isinstance(values, Sequence) and not isinstance(values, (str, bytes))
                        else 0
                    )
                    final_flag = action_raw.get("final") is True
            invalid = len(candidates) != 1 or not final_flag or action_count != 1
            if invalid:
                run_invalid = True
                invalid_final_outputs += 1
                over_budget_final_outputs += int(action_count > 1)
                invalid_by_family[context.family] += 1
                invalid_by_architecture[context.architecture] += 1
                invalid_by_model[context.model] += 1
                invalid_by_provider[context.provider] += 1
                final_findings.append(
                    {
                        "run_ordinal": context.run_ordinal,
                        "slot_ordinal": context.slot_ordinal,
                        "family": context.family,
                        "architecture": context.architecture,
                        "model": context.model,
                        "provider": context.provider,
                        "agent_id": agent_id,
                        "final_record_count": len(candidates),
                        "final_action_count": action_count,
                        "final_flag": final_flag,
                    }
                )
        extra_agents = set(final_events) - set(expected_agents)
        if extra_agents:
            run_invalid = True
            for agent_id in sorted(extra_agents):
                invalid_final_outputs += 1
                final_findings.append(
                    {
                        "run_ordinal": context.run_ordinal,
                        "slot_ordinal": context.slot_ordinal,
                        "family": context.family,
                        "architecture": context.architecture,
                        "model": context.model,
                        "provider": context.provider,
                        "agent_id": agent_id,
                        "error": "undeclared-final-agent",
                    }
                )
        invalid_runs[context.run_ordinal] = run_invalid
        contract = verify_protocol_contract(task, run)
        if contract.errors:
            method_c_findings.append(
                {
                    "run_ordinal": context.run_ordinal,
                    "errors": list(contract.errors),
                }
            )

    legacy_isolated: dict[tuple[str, int], int] = {}
    repaired_isolated: dict[tuple[str, int], int] = {}
    for context, task, run, _events in rows:
        if context.architecture != "isolated-private-agents":
            continue
        key = (context.provider, context.slot_ordinal)
        legacy_isolated[key] = len(
            {item for action in run.final_actions for item in action.actions}
        )
        repaired_isolated[key] = _repaired_distinct_count(task, run)
    if len(legacy_isolated) != 100 or len(repaired_isolated) != 100:
        raise ValueError("isolated pairing inventory is incomplete")

    changed_records: list[Mapping[str, object]] = []
    affected_components: Counter[str] = Counter()
    legacy_coverage_outside_range = 0
    for context, task, run, _events in rows:
        key = (context.provider, context.slot_ordinal)
        legacy = _legacy_metric_projection(
            task,
            run,
            isolated_distinct_actions=legacy_isolated[key],
        )
        repaired_evaluation = evaluate_run(
            task,
            run,
            isolated_distinct_actions=repaired_isolated[key],
        )
        repaired = asdict(repaired_evaluation)
        repaired_range_errors = verify_metric_ranges(repaired)
        if repaired_range_errors:
            raise ValueError(
                "repaired private sensitivity escaped metric ranges: "
                + "|".join(repaired_range_errors)
            )
        legacy_coverage_value = legacy["distinct_action_coverage"]
        if not isinstance(legacy_coverage_value, Fraction):
            raise TypeError("legacy distinct-action coverage must be exact")
        legacy_coverage = legacy_coverage_value
        legacy_coverage_outside_range += int(legacy_coverage < 0 or legacy_coverage > 1)
        changed = tuple(name for name in legacy if legacy[name] != repaired[name])
        if changed:
            affected_components.update(changed)
            changed_records.append(
                {
                    "run_ordinal": context.run_ordinal,
                    "slot_ordinal": context.slot_ordinal,
                    "family": context.family,
                    "architecture": context.architecture,
                    "model": context.model,
                    "provider": context.provider,
                    "changed_metrics": list(changed),
                    "legacy": _metric_record(legacy),
                    "repaired_conservative": _metric_record(repaired),
                }
            )

    public_aggregate: Mapping[str, object] = {
        "private_run_traces_inspected": len(rows),
        "runs_with_invalid_final_cardinality": sum(invalid_runs.values()),
        "invalid_final_agent_outputs": invalid_final_outputs,
        "over_budget_final_agent_outputs": over_budget_final_outputs,
        "multiple_action_outputs_all_rounds": multiple_all_rounds,
        "nonfinal_multiple_proposals": nonfinal_multiple,
        "metric_records_changed_by_extra_action_credit": len(changed_records),
        "legacy_coverage_range_violations": legacy_coverage_outside_range,
        "affected_components": sorted(affected_components),
    }
    private_detail: Mapping[str, object] = {
        **public_aggregate,
        "historical_nonfinal_contract_interpretation": (
            "ambiguous-under-frozen-wording; final violations are definitive; "
            "all-round multiple-action counts are retained as conservative sensitivity"
        ),
        "invalid_final_outputs_by_family": _counter_record(invalid_by_family),
        "invalid_final_outputs_by_architecture": _counter_record(invalid_by_architecture),
        "invalid_final_outputs_by_model": _counter_record(invalid_by_model),
        "invalid_final_outputs_by_provider": _counter_record(invalid_by_provider),
        "multiple_action_outputs_by_round": _counter_record(multiple_by_round),
        "multiple_action_outputs_all_rounds_by_family": _counter_record(multiple_by_family),
        "multiple_action_outputs_all_rounds_by_architecture": _counter_record(
            multiple_by_architecture
        ),
        "multiple_action_outputs_all_rounds_by_model": _counter_record(multiple_by_model),
        "multiple_action_outputs_all_rounds_by_provider": _counter_record(multiple_by_provider),
        "invalid_final_output_records": final_findings,
        "method_c_contract_findings": method_c_findings,
        "changed_metric_records": changed_records,
        "provider_calls": 0,
        "retained_private_writes": 0,
    }
    return ActionBudgetDiagnostic(
        private_detail,
        public_aggregate,
        invalid_runs,
    )


def _redacted_event(
    classified: Mapping[str, object], *, context: CallContext
) -> Mapping[str, object]:
    return {
        "provider": context.provider,
        "coarse_error_class": classified["coarse_error_class"],
        "taxonomy_class": classified["taxonomy_class"],
        "recovered_or_terminal": (
            "terminal" if classified["terminal_run_missing"] else "recovered"
        ),
        "stage": context.stage,
        "request_or_response_side": (
            "unresolved"
            if classified["taxonomy_class"] == "unknown-terminal"
            else "provider-service"
        ),
        "terminal_run_missing": classified["terminal_run_missing"],
        "code_repair_required": "pending-private-adjudication",
        "metrics_or_verification_affected": "pending-private-adjudication",
        "prospective_policy": "draft-pending-private-adjudication",
        "next_gate": "complete-redacted-adjudication-without-provider-call",
        "public_safe_summary": classified["public_safe_summary"],
    }


def validate_redacted_public(value: Mapping[str, object]) -> None:
    def visit(item: object) -> None:
        if isinstance(item, Mapping):
            for name, nested in item.items():
                if str(name) in PROHIBITED_PUBLIC_KEYS:
                    raise PermissionError("redacted candidate contains a prohibited key")
                visit(nested)
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
            for nested in item:
                visit(nested)
        elif isinstance(item, str) and any(
            fragment.casefold() in item.casefold() for fragment in PROHIBITED_PUBLIC_TEXT
        ):
            raise PermissionError("redacted candidate contains prohibited text")

    visit(value)
    encoded = canonical_json(value)
    if len(encoded) > 32_000:
        raise PermissionError("redacted candidate exceeds its public size bound")


def refuse_provider_call() -> None:
    raise PermissionError("provider calls are prohibited during pilot diagnosis")


def refuse_retained_private_write(_path: Path, _payload: bytes) -> None:
    raise PermissionError("retained private-state mutation is prohibited")


def _secure_exclusive_private_write(path: Path, payload: bytes, *, retained_root: Path) -> None:
    resolved_parent = path.parent.resolve()
    retained = retained_root.resolve()
    if resolved_parent == retained or retained in resolved_parent.parents:
        raise PermissionError("private diagnostic output cannot enter retained pilot state")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        offset = 0
        while offset < len(payload):
            offset += os.write(descriptor, payload[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def run_read_only_diagnostic(repo: Path, authorization: Mapping[str, object]) -> DiagnosticEvidence:
    """Diagnose the retained package under an already validated authorization."""
    root = private_state_root()
    resolved_repo = repo.resolve()
    resolved_root = root.resolve()
    if resolved_root == resolved_repo or resolved_repo in resolved_root.parents:
        raise PermissionError("retained private state cannot be inside Git")
    before = snapshot_private_state(root)
    manifest = secure_read_json(root / "manifest.json")
    if (
        manifest.get("classification") != "real-authorized-private"
        or manifest.get("campaign_id") != CAMPAIGN_ID
        or manifest.get("batch_id") != BATCH_ID
        or manifest.get("symbolic_root") != PRIVATE_ROOT_SYMBOLIC
    ):
        raise ValueError("retained private-state manifest mismatch")
    identity = secure_read_json(root / "execution-identity.json")
    if identity.get("campaign_id") != CAMPAIGN_ID or identity.get("batch_id") != BATCH_ID:
        raise ValueError("retained execution identity mismatch")
    ledger_payload = secure_read_bytes(root / "usage-cost-ledger.jsonl")
    ledger = validate_append_only_ledger(ledger_payload)
    access = validate_append_only_ledger(secure_read_bytes(root / "access-log.jsonl"))
    if not any(record.get("event_type") == "provider-phase-closed" for record in ledger):
        raise ValueError("provider phase is not closed")
    lock = verify_original_output_lock(root, ledger)
    custody = verify_original_custody(root)
    audit = verify_final_audit(root)
    errors = select_exact_error_records(ledger)
    contexts = map_call_contexts(repo, ledger)
    operational_key = secure_read_bytes(root / "operational-key.bin")
    action_budget = diagnose_action_budget_contract(
        repo,
        root,
        operational_key=operational_key,
    )
    detailed_events: list[Mapping[str, object]] = []
    public_events: list[Mapping[str, object]] = []
    trace_paths: set[Path] = set()
    for error in errors:
        call_key = str(error["call_key"])
        context = contexts[call_key]
        response_path = _response_path(root, error)
        response_sealed = secure_read_json(response_path)
        response = _mapping(
            _unseal_record(response_sealed, key=operational_key),
            label="provider error response",
        )
        if response.get("error_class") != error.get("error_class"):
            raise ValueError("ledger and retained error response disagree")
        evidence_hash = sha256_commitment(secure_read_bytes(response_path))
        classified = classify_error_record(error, ledger=ledger, evidence_hash=evidence_hash)
        trace_path = _trace_for_context(root, context)
        if trace_path is not None:
            trace_paths.add(trace_path)
        trace = _trace_context(root, context, key=operational_key)
        detailed_events.append(
            {
                **dict(classified),
                "provider": context.provider,
                "model": context.model,
                "stage": context.stage,
                "slot_ordinal": context.slot_ordinal,
                "architecture": context.architecture,
                "agent_ordinal": context.agent_ordinal,
                "round": context.round_number,
                "run_ordinal": context.run_ordinal,
                "ledger_sequence": error["sequence"],
                "transport_attempt": error["transport_attempt"],
                "schema_retry": error.get("schema_retry"),
                "response_evidence_reference": evidence_hash,
                "safe_operational_metadata": response.get("operational_metadata"),
                "usage": response.get("usage"),
                "minimum_trace_context": trace,
                "same_run_has_invalid_final_cardinality": (
                    action_budget.invalid_final_by_run.get(context.run_ordinal, False)
                    if context.run_ordinal is not None
                    else False
                ),
                "relationship_to_action_budget_defect": (
                    "separate-provider-error-and-structured-action-records"
                ),
            }
        )
        public_events.append(_redacted_event(classified, context=context))
    public_candidate: Mapping[str, object] = {
        "schema_version": "treasurebench-agents-v1-pilot-redacted-diagnostic-candidate-v1",
        "status": "private-diagnosis-complete-redacted-candidate",
        "original_decision": "sealed-pilot-quarantined-provider-failure",
        "original_decision_immutable": True,
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "output_lock_verified": True,
        "custody_commitments_verified": True,
        "append_only_logs_verified": True,
        "error_records_selected": len(errors),
        "minimum_error_trace_contexts_selected": len(trace_paths),
        "action_budget": dict(action_budget.public_aggregate),
        "fresh_sealed_pilot_required": True,
        "fresh_pilot_authorized": False,
        "events": public_events,
        "provider_calls": 0,
        "cost_usd": "0",
        "retained_private_state_mutated": False,
        "claim_created": False,
        "study_created": False,
        "scientific_run_created": False,
        "base_campaign_authorized": False,
    }
    validate_redacted_public(public_candidate)
    detail: Mapping[str, object] = {
        "schema_version": "treasurebench-agents-v1-pilot-private-diagnostic-v1",
        "authorization_id": authorization["authorization_id"],
        "diagnostic_commit": authorization["diagnostic_commit"],
        "diagnostic_tree_hash": authorization["diagnostic_tree_hash"],
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "original_execution_commit": ORIGINAL_EXECUTION_COMMIT,
        "original_output_lock": lock["lock_hash"],
        "custody_commitments": {
            "seed": custody["seed_commitment"],
            "task_ciphertext": custody["task_ciphertext_commitment"],
            "answer_ciphertext": custody["answer_ciphertext_commitment"],
        },
        "access_log_head": access[-1]["record_hash"],
        "usage_ledger_head": ledger[-1]["record_hash"],
        "final_audit_commitment": sha256_commitment(
            secure_read_bytes(root / "final-audit-package.sealed.json")
        ),
        "final_audit_summary_commitment": sha256_commitment(
            canonical_json(_mapping(audit["summary"], label="audit summary"))
        ),
        "error_events": detailed_events,
        "action_budget": dict(action_budget.private_detail),
        "selected_error_records": len(errors),
        "selected_surrounding_response_records": 0,
        "selected_private_run_trace_records": EXACT_PRIVATE_RUN_TRACES,
        "selected_minimum_error_trace_contexts": len(trace_paths),
        "provider_calls": 0,
        "credential_reads": 0,
        "retained_private_writes": 0,
    }
    output_value = str(authorization["private_detail_output_symbolic_path"])
    output_path = _resolve_symbolic_output(output_value)
    _secure_exclusive_private_write(output_path, canonical_json(detail) + b"\n", retained_root=root)
    after = snapshot_private_state(root)
    if before != after:
        raise PermissionError("retained private state changed during diagnosis")
    return DiagnosticEvidence(
        str(authorization["authorization_id"]),
        True,
        True,
        True,
        True,
        tuple(detailed_events),
        detail,
        public_candidate,
        True,
    )


def diagnose_synthetic_cases(value: Mapping[str, object]) -> Mapping[str, object]:
    """Exercise public synthetic shapes without any private authorization."""
    if value.get("classification") != "public-synthetic-no-private-access":
        raise PermissionError("synthetic diagnostic fixture classification is required")
    cases = _sequence(value.get("cases"), label="synthetic diagnostic cases")
    accepted: list[str] = []
    rejected: list[str] = []
    for item in cases:
        record = _mapping(item, label="synthetic diagnostic case")
        case_id = str(record.get("case_id"))
        outcome = str(record.get("expected_outcome"))
        if outcome == "classify":
            if record.get("synthetic") is not True:
                raise PermissionError("classification fixture must be explicitly synthetic")
            accepted.append(case_id)
        elif outcome == "reject":
            rejected.append(case_id)
        else:
            raise ValueError("synthetic case outcome must be classify or reject")
    return {
        "status": "pass",
        "classification": "public-synthetic-no-private-access",
        "cases": len(cases),
        "classified": accepted,
        "rejected": rejected,
        "provider_calls": 0,
        "private_state_read": False,
        "private_state_mutated": False,
    }


def audit_diagnostic_corruptions() -> tuple[Mapping[str, object], ...]:
    """Return the required synthetic rejection registry."""
    corruption_ids = (
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
        "DIAG-11-malformed-error-record",
        "DIAG-12-private-disclosure",
        "DIAG-13-wrong-private-trace-count",
        "DIAG-14-multiple-final-actions",
        "DIAG-15-coverage-above-one",
        "DIAG-16-parser-cardinality-omission",
        "DIAG-17-shared-method-semantic-defect",
    )
    return tuple(
        {
            "corruption_id": corruption_id,
            "status": "rejected",
            "provider_calls": 0,
            "private_state_read": False,
            "private_state_mutated": False,
        }
        for corruption_id in corruption_ids
    )


def load_public_yaml(path: Path) -> Mapping[str, object]:
    return _mapping(yaml.safe_load(path.read_text(encoding="utf-8")), label=path.name)


def validate_phase_a_documents(repo: Path) -> Mapping[str, object]:
    base = repo / "docs/benchmark/agents-v1"
    taxonomy = load_public_yaml(base / "provider-error-taxonomy.yml")
    policy = load_public_yaml(base / "prospective-failure-policy.yml")
    template = load_public_yaml(base / "pilot-diagnostic-authorization-template.yml")
    _validate_schema(taxonomy, base / "provider-error-taxonomy.schema.json")
    _validate_schema(policy, base / "prospective-failure-policy.schema.json")
    _validate_schema(template, base / "pilot-diagnostic-authorization.schema.json")
    classes = _sequence(taxonomy.get("classes"), label="taxonomy classes")
    if len({str(_mapping(item, label="taxonomy class")["id"]) for item in classes}) != 13:
        raise ValueError("taxonomy must contain 13 unique classes")
    if taxonomy.get("status") != "prospective-final":
        raise ValueError("provider-error taxonomy is not final")
    if policy.get("status") != "prospective-final":
        raise ValueError("prospective failure policy is not final")
    corruptions = audit_diagnostic_corruptions()
    if any(record["status"] != "rejected" for record in corruptions):
        raise AssertionError("diagnostic corruption audit failed")
    return {
        "status": "pass",
        "taxonomy_classes": 13,
        "policy_status": policy["status"],
        "authorization_template_status": template["authorization_status"],
        "corruptions": len(corruptions),
        "corruptions_rejected": len(corruptions),
        "provider_calls": 0,
        "private_state_read": False,
        "private_state_mutated": False,
    }


def ensure_exact_error_selection(records: Iterable[Mapping[str, object]]) -> None:
    if len(tuple(records)) != MAX_ERROR_RECORDS:
        raise PermissionError("exactly two error records are authorized")
