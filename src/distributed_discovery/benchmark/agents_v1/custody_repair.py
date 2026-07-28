"""AO-0007 read-only custody adjudication and prospective conformance controls.

Ordinary imports and tests never resolve or read retained AO-0006 state. The
single live diagnostic entry point first validates the generic Agent
Operations authorization, creates a one-use marker outside the retained root,
and then reads only the exact encrypted/redacted allowlist required here.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from distributed_discovery.agent_ops.core import (
    authorization_challenge,
    hash_path,
    load_yaml,
    sha256_file,
    validate,
)
from distributed_discovery.benchmark.agents_v1.models import canonical_json, sha256_hex

TASK_ID = "AO-0007"
SOURCE_TASK_ID = "AO-0006"
ISSUE = 202
BRANCH = "codex/treasurebench-ao0006-custody-repair"
GATE_ID = "AOG-AO-0007-AO0006-CUSTODY-DIAGNOSTIC"
CAMPAIGN_ID = "treasurebench-agents-v1-repair-confirmation-v2"
BATCH_ID = "tb-agents-v1-repair-confirmation-v2-b01"
EXECUTION_COMMIT = "d210b0653677859c79a1fb87d871aaf45f4a81d4"
EXPECTED_OUTPUT_LOCK = "sha256:127a9c796459c7627f6fd90b92ef1587ad0f6b1910b4ff255c2ceb976f3ab25f"
CONTRACT_PATH = Path("tasks/treasurebench-ao0006-custody-repair.yml")
GATE_PATH = Path("reports/agent-ops/AO-0007-treasurebench-ao0006-custody-diagnostic-owner-gate.yml")
SYMBOLIC_PRIVATE_ROOT = (
    "XDG_STATE_HOME/distributed-discovery/treasurebench-agents-v1/repair-confirmation-v2"
)
SYMBOLIC_DIAGNOSTIC_ROOT = (
    "XDG_STATE_HOME/distributed-discovery/agent-ops/private-diagnostics/AO-0007"
)
SECRET_METADATA_ONLY = frozenset(
    {"operational-key.bin", "seed.bin", "task-key.bin", "answer-key.bin"}
)
READABLE_FIXED = frozenset(
    {
        "manifest.json",
        "execution-identity.json",
        "access-log.jsonl",
        "usage-cost-ledger.jsonl",
        "provider-stage-state.json",
        "output-lock.json",
        "redacted-summary.json",
    }
)
FORBIDDEN_RETAINED = frozenset(
    {
        "task-custody.json",
        "answer-custody.json",
        "custody-manifest.json",
    }
)
REQUIRED_PROHIBITIONS = frozenset(
    {
        "provider-calls-outside-manifest",
        "credential-read-outside-manifest",
        "unauthorized-private-access",
        "scientific-mutation-outside-contract",
        "cap-increase",
        "consequential-action-by-gate-engine",
        "ao-0006-retained-state-mutation",
        "second-ao-0006-private-read",
        "seed-key-task-answer-provider-output-or-credential-disclosure",
    }
)


@dataclass(frozen=True)
class FileSnapshot:
    """Metadata for every file, with hashes only for the explicit read allowlist."""

    relative_path: str
    mode: str
    size: int
    mtime_ns: int
    inode: int
    sha256: str | None


@dataclass(frozen=True)
class RetainedDiagnostic:
    """Detailed private-safe operational diagnosis; contains no secret values or host paths."""

    task_id: str
    source_task_id: str
    campaign_id: str
    batch_id: str
    execution_commit: str
    output_lock_verified: bool
    output_lock_commitment: str
    locked_objects: int
    inventory_verified: bool
    append_only_logs_verified: bool
    retained_state_mutated: bool
    public_canary_complete: bool
    custody_complete: bool
    quarantine_stage: str
    failure_class: str
    metadata_only_secret_files: tuple[Mapping[str, object], ...]
    ciphertext_files_present: tuple[str, ...]
    ciphertext_files_absent: tuple[str, ...]
    minimum_event_types: tuple[str, ...]
    source_candidate: str
    exact_failure_stage: str
    exact_cause: str
    private_values_read: bool
    provider_calls: int
    credential_reads: int
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
    return root / "distributed-discovery" / "treasurebench-agents-v1" / "repair-confirmation-v2"


def diagnostic_output_root() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "distributed-discovery" / "agent-ops" / "private-diagnostics" / TASK_ID


def _git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ("git", *arguments),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _require_secure_file(path: Path) -> None:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise PermissionError("diagnostic input must be a regular non-symlink file")
    if stat.S_IMODE(info.st_mode) != 0o600:
        raise PermissionError("diagnostic input file must have mode 0600")


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
    """Bind a generic authorization to the frozen one-read AO-0007 diagnostic."""

    validate(value, "owner-authorization.schema.json")
    validate(gate, "owner-gate.schema.json")
    if value["authorization_digest"] != _authorization_digest(value):
        raise PermissionError("owner authorization digest mismatch")
    if gate["gate_id"] != GATE_ID or gate["issue"] != ISSUE or gate["branch"] != BRANCH:
        raise PermissionError("owner gate is not the frozen AO-0007 diagnostic gate")
    if gate["task_contract"]["path"] != CONTRACT_PATH.as_posix():
        raise PermissionError("owner gate task contract path mismatch")
    if gate["task_contract"]["sha256"] != sha256_file(repo / CONTRACT_PATH):
        raise PermissionError("owner gate task contract hash mismatch")
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
    branch = (
        current_branch if current_branch is not None else _git(repo, "branch", "--show-current")
    )
    if branch != BRANCH:
        raise PermissionError("diagnostic branch mismatch")
    if subprocess.run(
        ("git", "merge-base", "--is-ancestor", str(value["commit"]), "HEAD"),
        cwd=repo,
        check=False,
        capture_output=True,
    ).returncode:
        raise PermissionError("authorized diagnostic commit is not an ancestor")
    observed_hashes = (
        dict(current_tree_hashes)
        if current_tree_hashes is not None
        else {str(path): hash_path(repo / str(path)) for path in gate["tree_hashes"]}
    )
    if observed_hashes != gate["tree_hashes"]:
        raise PermissionError("diagnostic execution-sensitive tree changed")
    return value


def load_diagnostic_authorization(repo: Path) -> dict[str, Any]:
    """Load only the generic AO-0007 authorization; never resolve retained state first."""

    gate_path = repo / GATE_PATH
    if not gate_path.is_file() or gate_path.is_symlink():
        raise PermissionError("committed AO-0007 owner gate is required")
    gate = load_yaml(gate_path)
    resolved = authorization_path()
    _require_secure_file(resolved)
    return validate_diagnostic_authorization(load_yaml(resolved), gate=gate, repo=repo)


def _secure_directories(root: Path) -> tuple[Path, ...]:
    if root.is_symlink() or not root.is_dir():
        raise PermissionError("retained private-state root is unsafe")
    directories = [root]
    for current, names, _files in os.walk(root, followlinks=False):
        base = Path(current)
        for name in names:
            path = base / name
            if path.is_symlink() or not path.is_dir():
                raise PermissionError("symlink or non-directory in retained state")
            directories.append(path)
    for directory in directories:
        if stat.S_IMODE(directory.lstat().st_mode) != 0o700:
            raise PermissionError("retained private-state directory mode is not 0700")
    return tuple(sorted(directories))


def _inventory(root: Path) -> tuple[str, ...]:
    _secure_directories(root)
    files: list[str] = []
    for current, names, filenames in os.walk(root, followlinks=False):
        base = Path(current)
        for name in names:
            if (base / name).is_symlink():
                raise PermissionError("symlink in retained private-state inventory")
        for filename in filenames:
            path = base / filename
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
                raise PermissionError("unsafe retained private-state object")
            if stat.S_IMODE(info.st_mode) != 0o600:
                raise PermissionError("retained private-state file mode is not 0600")
            files.append(path.relative_to(root).as_posix())
    return tuple(sorted(files))


def _secure_read(root: Path, relative: str, *, allowed: frozenset[str]) -> bytes:
    if relative not in allowed:
        raise PermissionError("diagnostic attempted to read a non-allowlisted retained object")
    path = root / relative
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise PermissionError("diagnostic retained input is not a mode-0600 regular file")
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
        raise ValueError("diagnostic retained JSON must be an object")
    return {str(name): item for name, item in value.items()}


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
        "execution-identity": "execution-identity.json",
        "access-log": "access-log.jsonl",
        "usage-cost-ledger": "usage-cost-ledger.jsonl",
        "provider-stage-state": "provider-stage-state.json",
        "task-ciphertext": "task-custody.json",
        "answer-ciphertext": "answer-custody.json",
        "custody-manifest": "custody-manifest.json",
    }
    if name in fixed:
        return fixed[name]
    if name.startswith("trace/"):
        return f"encrypted-traces/{name.removeprefix('trace/')}"
    if name.startswith("provider-response/"):
        return f"encrypted-provider-responses/{name.removeprefix('provider-response/')}"
    raise PermissionError("output lock names an undeclared retained object class")


def _verify_lock(
    root: Path,
    lock: Mapping[str, object],
    *,
    expected_lock: str,
    allowed: frozenset[str],
) -> tuple[dict[str, bytes], tuple[dict[str, object], ...]]:
    mutable = dict(lock)
    actual_lock = mutable.pop("lock_hash", None)
    if actual_lock != f"sha256:{sha256_hex(canonical_json(mutable))}":
        raise ValueError("output-lock self-hash mismatch")
    if actual_lock != expected_lock:
        raise ValueError("output lock differs from the permanent public commitment")
    if mutable.get("campaign_id") != CAMPAIGN_ID or mutable.get("batch_id") != BATCH_ID:
        raise ValueError("output-lock identity mismatch")
    objects_raw = mutable.get("objects")
    if not isinstance(objects_raw, Mapping) or len(objects_raw) != 8:
        raise ValueError("output lock must contain the exact eight-object quarantine inventory")
    objects: dict[str, bytes] = {}
    for raw_name, expected in sorted(objects_raw.items()):
        name = str(raw_name)
        relative = _locked_relative(name)
        payload = _secure_read(root, relative, allowed=allowed)
        if expected != f"sha256:{sha256_hex(payload)}":
            raise ValueError("output-lock object commitment mismatch")
        objects[name] = payload
    ledger = _validate_ledger(objects["usage-cost-ledger"])
    head = ledger[-1]["record_hash"] if ledger else "GENESIS"
    if mutable.get("ledger_head") != head:
        raise ValueError("output-lock ledger head mismatch")
    if mutable.get("provider_phase_closed") is not True:
        raise ValueError("output lock does not close the provider phase")
    return objects, ledger


def _snapshot(
    root: Path,
    inventory: Sequence[str],
    *,
    readable: frozenset[str],
) -> tuple[FileSnapshot, ...]:
    values: list[FileSnapshot] = []
    for relative in inventory:
        path = root / relative
        info = path.lstat()
        digest = (
            f"sha256:{sha256_hex(_secure_read(root, relative, allowed=readable))}"
            if relative in readable
            else None
        )
        values.append(
            FileSnapshot(
                relative_path=relative,
                mode=f"{stat.S_IMODE(info.st_mode):04o}",
                size=info.st_size,
                mtime_ns=info.st_mtime_ns,
                inode=info.st_ino,
                sha256=digest,
            )
        )
    return tuple(values)


def _git_show(repo: Path, commit: str, relative: str) -> str:
    return _git(repo, "show", f"{commit}:{relative}")


def audit_execution_source(repo: Path) -> Mapping[str, object]:
    """Prove the public deterministic v2 permit candidate at the frozen commit."""

    generation = _git_show(
        repo, EXECUTION_COMMIT, "src/distributed_discovery/benchmark/agents_v1/generation.py"
    )
    v2 = _git_show(
        repo,
        EXECUTION_COMMIT,
        "src/distributed_discovery/benchmark/agents_v1/fresh_pilot_v2_live.py",
    )
    controls = _git_show(
        repo, EXECUTION_COMMIT, "src/distributed_discovery/benchmark/agents_v1/fresh_pilot_v2.py"
    )
    required_generation = (
        '"treasurebench-agents-v1-pilot-v1"',
        '"treasurebench-agents-v1-repair-confirmation-v1"',
        "private generation is disabled",
    )
    if any(fragment not in generation for fragment in required_generation):
        raise ValueError("frozen generator does not match the audited allowlist shape")
    if CAMPAIGN_ID in generation:
        raise ValueError("frozen generator unexpectedly includes the v2 campaign")
    required_order = (
        "load_or_create_real_custody_material(root)",
        "tasks = generate_tasks(",
        "task_payload = [task.visible_record()",
        'root / "task-custody.json"',
        'root / "answer-custody.json"',
        'root / "custody-manifest.json"',
    )
    positions = tuple(v2.index(fragment) for fragment in required_order)
    if tuple(sorted(positions)) != positions:
        raise ValueError("frozen custody production order differs from the audited shape")
    if "public_fixture=synthetic" not in v2:
        raise ValueError("frozen rehearsal/live switch is absent")
    if 'CAMPAIGN_ID = "treasurebench-agents-v1-repair-confirmation-v2"' not in controls:
        raise ValueError("frozen v2 campaign constant differs")
    return {
        "execution_commit": EXECUTION_COMMIT,
        "candidate": "private-task-generation-campaign-permit-rejection",
        "v2_campaign_absent_from_private_generation_allowlist": True,
        "material_created_before_generation": True,
        "first_ciphertext_persisted_after_generation": True,
        "synthetic_rehearsal_bypasses_private_gate": True,
    }


def _event_types(records: Sequence[Mapping[str, object]]) -> tuple[str, ...]:
    return tuple(str(record.get("event_type", "")) for record in records)


def inspect_retained_custody_failure(
    repo: Path,
    root: Path,
    *,
    expected_lock: str = EXPECTED_OUTPUT_LOCK,
) -> RetainedDiagnostic:
    """Read the exact allowlist and prove no retained mutation."""

    initial_inventory = _inventory(root)
    if FORBIDDEN_RETAINED.intersection(initial_inventory):
        raise ValueError("retained state contradicts the permanent no-ciphertext boundary")
    preliminary_allowed = frozenset(READABLE_FIXED)
    lock = _secure_json(root, "output-lock.json", allowed=preliminary_allowed)
    objects_raw = lock.get("objects")
    if not isinstance(objects_raw, Mapping):
        raise ValueError("output-lock objects are missing")
    locked_relatives = frozenset(_locked_relative(str(name)) for name in objects_raw)
    readable = frozenset(set(READABLE_FIXED) | set(locked_relatives))
    expected_inventory = frozenset(
        set(locked_relatives)
        | set(SECRET_METADATA_ONLY)
        | {"manifest.json", "output-lock.json", "redacted-summary.json"}
    )
    if frozenset(initial_inventory) != expected_inventory:
        raise ValueError("retained private-state inventory differs from the exact declared shape")
    before = _snapshot(root, initial_inventory, readable=readable)
    objects, usage = _verify_lock(
        root,
        lock,
        expected_lock=expected_lock,
        allowed=readable,
    )
    access = _validate_ledger(objects["access-log"])
    manifest = _secure_json(root, "manifest.json", allowed=readable)
    state = json.loads(objects["provider-stage-state"])
    summary = _secure_json(root, "redacted-summary.json", allowed=readable)
    identity = json.loads(objects["execution-identity"])
    if not isinstance(state, dict) or not isinstance(identity, dict):
        raise ValueError("retained state or execution identity is malformed")
    if (
        manifest.get("campaign_id") != CAMPAIGN_ID
        or manifest.get("batch_id") != BATCH_ID
        or manifest.get("symbolic_root") != SYMBOLIC_PRIVATE_ROOT
    ):
        raise ValueError("retained private-state manifest identity mismatch")
    if (
        identity.get("campaign_id") != CAMPAIGN_ID
        or identity.get("batch_id") != BATCH_ID
        or identity.get("execution_commit") != EXECUTION_COMMIT
    ):
        raise ValueError("retained execution identity mismatch")
    if (
        state.get("public_canary_complete") is not True
        or state.get("custody_complete") is not False
        or state.get("private_prefix_complete") is not False
        or state.get("fixed_full_batch_complete") is not False
        or state.get("quarantined") is not True
        or state.get("quarantine_stage") != "custody"
        or state.get("quarantine_failure_class") != "custody-creation-failure"
    ):
        raise ValueError("retained custody failure stage does not match the public boundary")
    if (
        summary.get("decision") != "fresh-pilot-v2-quarantined-engineering-only"
        or summary.get("stage") != "custody"
        or summary.get("failure_class") != "custody-creation-failure"
        or summary.get("calls") != 2
        or summary.get("input_tokens") != 1349
        or summary.get("output_tokens") != 253
        or str(summary.get("cost_usd")) != "0.0076095"
        or summary.get("minimum_unseal_performed") is not False
    ):
        raise ValueError("redacted retained summary differs from the permanent boundary")
    usage_types = _event_types(usage)
    access_types = _event_types(access)
    if usage_types[-2:] != ("batch-quarantine", "provider-phase-closed"):
        raise ValueError("minimum quarantine event ordering is not preserved")
    if any(record.get("operation") == "fresh-private-custody-created" for record in access):
        raise ValueError("custody-created event contradicts the failed stage")
    secret_metadata: list[Mapping[str, object]] = []
    for relative in sorted(SECRET_METADATA_ONLY):
        info = (root / relative).lstat()
        if info.st_size != 32 or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError("metadata-only secret object has invalid size or mode")
        secret_metadata.append({"filename": relative, "mode": "0600", "size_bytes": 32})
    source = audit_execution_source(repo)
    after_inventory = _inventory(root)
    after = _snapshot(root, after_inventory, readable=readable)
    if initial_inventory != after_inventory or before != after:
        raise PermissionError("retained private state mutated during the read-only diagnostic")
    return RetainedDiagnostic(
        task_id=TASK_ID,
        source_task_id=SOURCE_TASK_ID,
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
        execution_commit=EXECUTION_COMMIT,
        output_lock_verified=True,
        output_lock_commitment=expected_lock,
        locked_objects=len(objects),
        inventory_verified=True,
        append_only_logs_verified=True,
        retained_state_mutated=False,
        public_canary_complete=True,
        custody_complete=False,
        quarantine_stage="custody",
        failure_class="custody-creation-failure",
        metadata_only_secret_files=tuple(secret_metadata),
        ciphertext_files_present=(),
        ciphertext_files_absent=tuple(sorted(FORBIDDEN_RETAINED)),
        minimum_event_types=tuple((*access_types, *usage_types[-2:])),
        source_candidate=str(source["candidate"]),
        exact_failure_stage="private-task-generation",
        exact_cause="v2-campaign-absent-from-private-generation-permit-allowlist",
        private_values_read=False,
        provider_calls=0,
        credential_reads=0,
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
    """Reject host paths, secret-bearing fields, or non-redacted content."""

    forbidden_keys = {
        "seed",
        "seed_value",
        "task_key",
        "answer_key",
        "operational_key",
        "task_text",
        "answer",
        "raw_output",
        "credential",
        "private_path",
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
            raise ValueError("public diagnostic contains a host or private path")

    visit(value)


def run_read_only_custody_diagnostic(repo: Path) -> Mapping[str, object]:
    """Execute the exact one-use diagnostic after generic owner authorization."""

    authorization = load_diagnostic_authorization(repo)
    output_root = diagnostic_output_root()
    marker = output_root / "read-intent.json"
    detailed = output_root / "diagnostic.json"
    if marker.exists() or detailed.exists():
        raise PermissionError("AO-0007 private-read authority is already consumed")
    marker_payload = {
        "schema_version": "ao-0007-custody-diagnostic-read-intent-v1",
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "gate_id": GATE_ID,
        "execution_commit": authorization["commit"],
        "single_use": True,
        "retained_state_mutation_authorized": False,
    }
    _exclusive_create(marker, canonical_json(marker_payload) + b"\n")
    diagnosis = inspect_retained_custody_failure(repo, private_state_root())
    _exclusive_create(detailed, canonical_json(asdict(diagnosis)) + b"\n")
    public = {
        "status": "pass",
        "task_id": TASK_ID,
        "source_task_id": SOURCE_TASK_ID,
        "output_lock_verified": diagnosis.output_lock_verified,
        "inventory_verified": diagnosis.inventory_verified,
        "append_only_logs_verified": diagnosis.append_only_logs_verified,
        "retained_state_mutated": diagnosis.retained_state_mutated,
        "exact_failure_stage": diagnosis.exact_failure_stage,
        "exact_cause": diagnosis.exact_cause,
        "private_diagnostic_written": True,
        "private_values_read": False,
        "provider_calls": 0,
        "credential_reads": 0,
        "private_paths_disclosed": False,
        "private_read_authority_closed": True,
    }
    validate_public_diagnostic(public)
    return public
