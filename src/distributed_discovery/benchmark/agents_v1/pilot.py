"""Fail-closed runtime primitives for the TreasureBench Agents v1 sealed pilot.

This module owns engineering controls only. It cannot create a study, claim,
scientific run, ranking, composite score, or public task-level result.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import stat
import subprocess
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import yaml
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jsonschema import Draft202012Validator, FormatChecker

from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    AgentAdapter,
    MockAdapter,
    ModelManifest,
    Usage,
)
from distributed_discovery.benchmark.agents_v1.contamination import classify_text, run_public_probes
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import (
    canonical_cells,
    generate_instance,
)
from distributed_discovery.benchmark.agents_v1.models import (
    TaskInstance,
    canonical_json,
    sha256_hex,
)
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    ArchitectureRun,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace, verify_trace_hashes
from distributed_discovery.benchmark.agents_v1.verification import verify_method_agreement

CAMPAIGN_ID = "treasurebench-agents-v1-pilot-v1"
BATCH_ID = "tb-agents-v1-pilot-v1-b01"
BRANCH = "benchmark/treasurebench-agents-v1-sealed-pilot"
BASE_COMMIT = "0d3757caf322402c0c47117b3aff0490926a133d"
MODELS = ("gpt-5.4-2026-03-05", "claude-sonnet-4-6")
PROVIDERS = ("OpenAI", "Anthropic")
TOTAL_CAP = Decimal("100")
PROVIDER_CAP = Decimal("50")
MAX_CALLS = 5200
MAX_INPUT_TOKENS = 10_600_000
MAX_OUTPUT_TOKENS = 1_400_000
MAX_CONCURRENCY = 2
REQUIRED_TRUE_PERMISSIONS = frozenset(
    {
        "live_provider_calls",
        "private_generation",
        "encryption",
        "unsealing_after_output_lock",
        "trace_retention",
        "public_redacted_summary",
    }
)
REQUIRED_FALSE_PERMISSIONS = frozenset(
    {"claim", "study", "scientific_run", "package", "arxiv", "journal"}
)
REQUIRED_CONTAMINATION_PROBES = frozenset(
    {
        "public-value-recall",
        "public-wording-recall",
        "public-task-id-recall",
        "theorem-name-recall",
        "result-name-recall",
        "solution-pattern-recall",
        "generator-leakage",
        "answer-key-leakage",
        "cross-batch-leakage",
        "prompt-injection",
        "benchmark-self-identification",
        "ordinary-reasoning-control",
    }
)


def _load_yaml(path: Path) -> Mapping[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{path.name} must contain a mapping")
    return {str(key): item for key, item in value.items()}


def _validate_schema(value: Mapping[str, object], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    if errors:
        path = ".".join(str(item) for item in errors[0].absolute_path) or "$"
        raise ValueError(f"{schema_path.name}:{path}: {errors[0].message}")


def load_request(repo: Path) -> Mapping[str, object]:
    base = repo / "docs/benchmark/agents-v1"
    value = _load_yaml(base / "treasurebench-pilot-request.yml")
    _validate_schema(value, base / "treasurebench-pilot-request.schema.json")
    return value


def load_allocation(repo: Path) -> Mapping[str, object]:
    base = repo / "docs/benchmark/agents-v1"
    value = _load_yaml(base / "treasurebench-pilot-allocation.yml")
    _validate_schema(value, base / "treasurebench-pilot-allocation.schema.json")
    slots = value["slots"]
    if not isinstance(slots, list) or len(slots) != 50:
        raise ValueError("allocation must contain exactly 50 slots")
    families: dict[str, int] = {}
    targets = {"target-A": 0, "target-B": 0}
    agents = {"agent-A": 0, "agent-B": 0}
    cells = {(cell.family_id, cell.cell_index) for cell in canonical_cells()}
    for raw in slots:
        if not isinstance(raw, Mapping):
            raise ValueError("allocation slot must be a mapping")
        family = str(raw["family_id"])
        index = int(str(raw["cell_index"]))
        if (family, index) not in cells:
            raise ValueError(f"unknown generator cell: {family}/{index}")
        families[family] = families.get(family, 0) + 1
        targets[str(raw["target_relabeling_class"])] += 1
        agents[str(raw["agent_relabeling_class"])] += 1
        if raw["public_calibration_instance_reuse"] is not False:
            raise ValueError("public calibration reuse is prohibited")
        if raw["future_base_instance_reuse"] is not False:
            raise ValueError("future base reuse is prohibited")
    if sorted(families.values()) != [10, 10, 10, 10, 10]:
        raise ValueError("allocation must contain ten slots per family")
    if set(targets.values()) != {25} or set(agents.values()) != {25}:
        raise ValueError("target and agent relabeling must each balance 25/25")
    return value


def authorization_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return root / "distributed-discovery" / "treasurebench-agents-v1-pilot-authorization.yml"


def private_state_root() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "distributed-discovery/treasurebench-agents-v1/pilot-v1"


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def execution_tree_files(repo: Path, request: Mapping[str, object]) -> tuple[Path, ...]:
    raw_paths = request["execution_sensitive_paths"]
    if not isinstance(raw_paths, Sequence) or isinstance(raw_paths, str):
        raise ValueError("execution_sensitive_paths must be a sequence")
    result = _git(
        repo,
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
        *(str(item) for item in raw_paths),
    )
    paths = tuple(sorted({repo / line for line in result.splitlines() if line}))
    if not paths or any(not path.is_file() or path.is_symlink() for path in paths):
        raise ValueError("execution-sensitive path set is empty or unsafe")
    return paths


def execution_tree_hash(repo: Path, request: Mapping[str, object] | None = None) -> str:
    request_value = request or load_request(repo)
    digest = hashlib.sha256()
    for path in execution_tree_files(repo, request_value):
        relative = path.relative_to(repo).as_posix().encode()
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return f"sha256:{digest.hexdigest()}"


def current_execution_identity(repo: Path) -> Mapping[str, object]:
    request = load_request(repo)
    return {
        "base_commit": BASE_COMMIT,
        "execution_commit": _git(repo, "rev-parse", "HEAD"),
        "branch": _git(repo, "branch", "--show-current"),
        "tree_hash": execution_tree_hash(repo, request),
        "remote_contains_head": bool(
            _git(repo, "branch", "-r", "--contains", _git(repo, "rev-parse", "HEAD"))
        ),
    }


def _require_secure_regular_file(path: Path) -> None:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise PermissionError("authorization must be a regular non-symlink file")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise PermissionError("authorization permissions must be 0600 or stricter")


def validate_pilot_authorization(
    value: Mapping[str, object],
    *,
    repo: Path,
    now: datetime | None = None,
    allow_synthetic: bool = False,
    expected_commit: str | None = None,
    expected_tree_hash: str | None = None,
) -> Mapping[str, object]:
    base = repo / "docs/benchmark/agents-v1"
    _validate_schema(value, base / "treasurebench-pilot-authorization.schema.json")
    if value["authorization_status"] != "authorized" or value["revoked"] is not False:
        raise PermissionError("authorization is not active")
    if bool(value["synthetic"]) and not allow_synthetic:
        raise PermissionError("synthetic authorization cannot authorize live execution")
    current = now or datetime.now(UTC)
    authorized = datetime.fromisoformat(str(value["authorized_at_utc"]).replace("Z", "+00:00"))
    expires = datetime.fromisoformat(str(value["expires_at_utc"]).replace("Z", "+00:00"))
    if authorized > current or expires <= current:
        raise PermissionError("authorization is not within its active interval")
    if value["authorized_base_commit"] != BASE_COMMIT:
        raise PermissionError("authorized base commit mismatch")
    authorized_commit = str(value["authorized_execution_commit"])
    commit = expected_commit or authorized_commit
    tree_hash = expected_tree_hash or execution_tree_hash(repo)
    if value["authorized_execution_commit"] != commit:
        raise PermissionError("authorized execution commit mismatch")
    ancestor = subprocess.run(
        ("git", "merge-base", "--is-ancestor", authorized_commit, "HEAD"),
        cwd=repo,
        check=False,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        raise PermissionError("authorized execution commit is not an ancestor of HEAD")
    if value["execution_tree_hash"] != tree_hash:
        raise PermissionError("authorized execution tree hash mismatch")
    if _git(repo, "branch", "--show-current") != BRANCH:
        raise PermissionError("authorized branch mismatch")
    caps = value["caps"]
    permissions = value["permissions"]
    if not isinstance(caps, Mapping) or not isinstance(permissions, Mapping):
        raise ValueError("caps and permissions must be mappings")
    expected_caps = {
        "total_usd": TOTAL_CAP,
        "OpenAI": PROVIDER_CAP,
        "Anthropic": PROVIDER_CAP,
        "calls": MAX_CALLS,
        "input_tokens": MAX_INPUT_TOKENS,
        "output_tokens": MAX_OUTPUT_TOKENS,
        "live_concurrency": MAX_CONCURRENCY,
    }
    provider_caps = caps["provider_usd"]
    if not isinstance(provider_caps, Mapping):
        raise ValueError("provider_usd must be a mapping")
    actual_caps = {
        "total_usd": Decimal(str(caps["total_usd"])),
        "OpenAI": Decimal(str(provider_caps["OpenAI"])),
        "Anthropic": Decimal(str(provider_caps["Anthropic"])),
        "calls": int(str(caps["calls"])),
        "input_tokens": int(str(caps["input_tokens"])),
        "output_tokens": int(str(caps["output_tokens"])),
        "live_concurrency": int(str(caps["live_concurrency"])),
    }
    if actual_caps != expected_caps:
        raise PermissionError("authorization caps do not match the frozen pilot maxima")
    if any(permissions.get(name) is not True for name in REQUIRED_TRUE_PERMISSIONS):
        raise PermissionError("all engineering permissions must be true")
    if any(permissions.get(name) is not False for name in REQUIRED_FALSE_PERMISSIONS):
        raise PermissionError("scientific and publication permissions must be false")
    attestation = value["owner_attestation"]
    if not isinstance(attestation, str) or len(attestation.strip()) < 40:
        raise PermissionError("a meaningful owner attestation is required")
    return value


def load_pilot_authorization(repo: Path, path: Path | None = None) -> Mapping[str, object]:
    resolved = path or authorization_path()
    if not resolved.exists():
        raise PermissionError("owner authorization is required before live execution")
    _require_secure_regular_file(resolved)
    value = _load_yaml(resolved)
    return validate_pilot_authorization(value, repo=repo)


@dataclass(frozen=True)
class GenerationPermit:
    campaign_id: str
    allows_private_generation: bool
    synthetic: bool


def generation_permit(authorization: Mapping[str, object]) -> GenerationPermit:
    permissions = authorization.get("permissions")
    if not isinstance(permissions, Mapping) or permissions.get("private_generation") is not True:
        raise PermissionError("private generation is not authorized")
    return GenerationPermit(CAMPAIGN_ID, True, bool(authorization["synthetic"]))


def _secure_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink() or not path.is_dir():
        raise PermissionError("private-state directory is unsafe")
    path.chmod(0o700)


def atomic_private_write(path: Path, payload: bytes) -> None:
    _secure_mkdir(path.parent)
    if path.exists() and path.is_symlink():
        raise PermissionError("refusing to replace a symlink")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temporary)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
        path.chmod(0o600)
    finally:
        if temp_path.exists():
            temp_path.unlink()


PRIVATE_OBJECTS = (
    "seed",
    "seed-commitment-input",
    "execution-identity",
    "operational-key",
    "task-key",
    "answer-key",
    "encrypted-tasks",
    "encrypted-answer-key",
    "custody-manifest",
    "encrypted-provider-responses",
    "access-log",
    "raw-traces",
    "usage-cost-ledger",
    "provider-stage-state",
    "output-lock",
    "unsealed-audit-working-set",
    "encrypted-final-audit-package",
    "redacted-summary",
)


def initialize_private_state(
    root: Path, *, repo: Path, synthetic: bool = False
) -> Mapping[str, object]:
    resolved_repo = repo.resolve()
    resolved_root = root.resolve()
    if resolved_root == resolved_repo or resolved_repo in resolved_root.parents:
        raise PermissionError("private state must be outside the repository")
    _secure_mkdir(resolved_root)
    _secure_mkdir(resolved_root / "encrypted-traces")
    manifest = {
        "schema_version": "treasurebench-pilot-private-state-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "classification": "synthetic-phase-a" if synthetic else "real-authorized-private",
        "symbolic_root": ("XDG_STATE_HOME/distributed-discovery/treasurebench-agents-v1/pilot-v1"),
        "directory_mode": "0700",
        "file_mode": "0600",
        "symlinks_allowed": False,
        "atomic_writes": True,
        "retention_days": 365,
        "objects": list(PRIVATE_OBJECTS),
        "deletion_authorization_required": True,
    }
    schema = repo / "docs/benchmark/agents-v1/treasurebench-pilot-private-state.schema.json"
    _validate_schema(manifest, schema)
    manifest_path = resolved_root / "manifest.json"
    if manifest_path.exists():
        _require_secure_regular_file(manifest_path)
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing != manifest:
            raise PermissionError("private-state manifest mismatch requires quarantine")
    else:
        atomic_private_write(manifest_path, canonical_json(manifest) + b"\n")
    return manifest


def create_real_custody_material(root: Path) -> Mapping[str, bytes]:
    """Create independent CSPRNG seed/keys only after live authorization."""
    material = {
        "seed": secrets.token_bytes(32),
        "task_key": secrets.token_bytes(32),
        "answer_key": secrets.token_bytes(32),
    }
    for name, value in material.items():
        atomic_private_write(root / f"{name.replace('_', '-')}.bin", value)
    return material


def load_or_create_real_custody_material(root: Path) -> Mapping[str, bytes]:
    paths = {
        "seed": root / "seed.bin",
        "task_key": root / "task-key.bin",
        "answer_key": root / "answer-key.bin",
    }
    present = {name: path.exists() for name, path in paths.items()}
    if any(present.values()) and not all(present.values()):
        raise PermissionError("partial custody material requires quarantine")
    if all(present.values()):
        material: dict[str, bytes] = {}
        for name, path in paths.items():
            _require_secure_regular_file(path)
            value = path.read_bytes()
            if len(value) != 32:
                raise ValueError("custody material has invalid length")
            material[name] = value
        return material
    return create_real_custody_material(root)


@dataclass(frozen=True)
class SealedObject:
    domain: str
    nonce_hex: str
    ciphertext: bytes
    ciphertext_sha256: str
    associated_data_sha256: str

    def manifest(self) -> Mapping[str, object]:
        return {
            "algorithm": "AES-256-GCM",
            "domain": self.domain,
            "nonce_hex": self.nonce_hex,
            "ciphertext_sha256": self.ciphertext_sha256,
            "associated_data_sha256": self.associated_data_sha256,
        }


def seal_object(*, domain: str, value: object, key: bytes, nonce: bytes) -> SealedObject:
    if len(key) != 32 or len(nonce) != 12:
        raise ValueError("AES-256-GCM requires a 32-byte key and 12-byte nonce")
    associated = canonical_json(
        {"campaign_id": CAMPAIGN_ID, "batch_id": BATCH_ID, "domain": domain}
    )
    ciphertext = AESGCM(key).encrypt(nonce, canonical_json(value), associated)
    return SealedObject(
        domain,
        nonce.hex(),
        ciphertext,
        f"sha256:{sha256_hex(ciphertext)}",
        f"sha256:{sha256_hex(associated)}",
    )


def unseal_object(sealed: SealedObject, *, key: bytes) -> object:
    if sealed.ciphertext_sha256 != f"sha256:{sha256_hex(sealed.ciphertext)}":
        raise ValueError("ciphertext hash mismatch")
    associated = canonical_json(
        {"campaign_id": CAMPAIGN_ID, "batch_id": BATCH_ID, "domain": sealed.domain}
    )
    if sealed.associated_data_sha256 != f"sha256:{sha256_hex(associated)}":
        raise ValueError("associated-data hash mismatch")
    plaintext = AESGCM(key).decrypt(bytes.fromhex(sealed.nonce_hex), sealed.ciphertext, associated)
    return json.loads(plaintext)


class AppendOnlyLedger:
    """Hash-chained, idempotent, append-only private JSONL ledger."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.records = self._read_and_validate()

    def _read_and_validate(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        _require_secure_regular_file(self.path)
        records: list[dict[str, object]] = []
        previous = "GENESIS"
        for index, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("ledger record must be an object")
            actual = record.pop("record_hash", None)
            if record.get("sequence") != index or record.get("previous_hash") != previous:
                raise ValueError("ledger sequence or chain mismatch")
            expected = f"sha256:{sha256_hex(canonical_json(record))}"
            if actual != expected:
                raise ValueError("ledger record hash mismatch")
            record["record_hash"] = actual
            records.append(record)
            previous = str(actual)
        return records

    def append(self, event: Mapping[str, object]) -> Mapping[str, object]:
        if any(record.get("event_type") == "provider-phase-closed" for record in self.records):
            raise PermissionError("provider phase is closed")
        key = event.get("idempotency_key")
        if key and any(
            record.get("idempotency_key") == key and record.get("status") == "success"
            for record in self.records
        ):
            raise PermissionError("successful idempotency key already exists")
        record = {
            "sequence": len(self.records) + 1,
            "previous_hash": (self.records[-1]["record_hash"] if self.records else "GENESIS"),
            **{str(name): value for name, value in event.items()},
        }
        record["record_hash"] = f"sha256:{sha256_hex(canonical_json(record))}"
        existing = self.path.read_bytes() if self.path.exists() else b""
        atomic_private_write(self.path, existing + canonical_json(record) + b"\n")
        self.records.append(record)
        return record

    def close_provider_phase(self) -> Mapping[str, object]:
        return self.append(
            {
                "event_type": "provider-phase-closed",
                "status": "locked",
                "idempotency_key": "provider-phase-closed",
            }
        )

    def totals(self) -> Mapping[str, object]:
        successes = [
            record
            for record in self.records
            if record.get("status") == "success"
            or (
                record.get("event_type") == "provider-call"
                and record.get("status") in {"error", "invalid"}
            )
        ]
        return {
            "calls": len(successes),
            "input_tokens": sum(int(str(item.get("input_tokens", 0))) for item in successes),
            "output_tokens": sum(int(str(item.get("output_tokens", 0))) for item in successes),
            "cost_usd": sum(
                (Decimal(str(item.get("cost_usd", "0"))) for item in successes),
                Decimal("0"),
            ),
            "provider_usd": {
                provider: sum(
                    (
                        Decimal(str(item.get("cost_usd", "0")))
                        for item in successes
                        if item.get("provider") == provider
                    ),
                    Decimal("0"),
                )
                for provider in PROVIDERS
            },
        }

    def guard_next(
        self,
        *,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: Decimal,
    ) -> None:
        if provider not in PROVIDERS:
            raise PermissionError("provider is outside the pilot")
        if any(record.get("event_type") == "provider-phase-closed" for record in self.records):
            raise PermissionError("provider phase is closed")
        totals = self.totals()
        provider_totals = totals["provider_usd"]
        assert isinstance(provider_totals, Mapping)
        if int(str(totals["calls"])) + 1 > MAX_CALLS:
            raise PermissionError("projected call cap exceeded")
        if int(str(totals["input_tokens"])) + input_tokens > MAX_INPUT_TOKENS:
            raise PermissionError("projected input-token cap exceeded")
        if int(str(totals["output_tokens"])) + output_tokens > MAX_OUTPUT_TOKENS:
            raise PermissionError("projected output-token cap exceeded")
        if Decimal(str(totals["cost_usd"])) + cost_usd > TOTAL_CAP:
            raise PermissionError("projected total-cost cap exceeded")
        if Decimal(str(provider_totals[provider])) + cost_usd > PROVIDER_CAP:
            raise PermissionError("projected provider-cost cap exceeded")


class ResumablePilotAdapter:
    """Guard and persist each adapter call without exposing raw responses."""

    def __init__(
        self,
        adapter: AgentAdapter,
        *,
        provider: str,
        model: str,
        ledger: AppendOnlyLedger,
        response_root: Path,
        response_key: bytes,
    ) -> None:
        validate_provider_route(provider, model)
        if adapter.manifest.exact_snapshot not in {model, "deterministic-mock-v1"}:
            raise PermissionError("adapter manifest does not match the frozen route")
        self.adapter = adapter
        self.provider = provider
        self.model = model
        self.ledger = ledger
        self.response_root = response_root
        self.response_key = response_key
        self.manifest = ModelManifest(
            provider=adapter.manifest.provider,
            model_id=adapter.manifest.model_id,
            exact_snapshot=adapter.manifest.exact_snapshot,
            adapter_version=f"pilot-resume-v1/{adapter.manifest.adapter_version}",
            moving_alias=False,
            live_capable=adapter.manifest.live_capable,
        )
        _secure_mkdir(response_root)

    def _key(self, request: AdapterRequest) -> str:
        identity = {
            "provider": self.provider,
            "model": self.model,
            "task": request.prompt.task_commitment,
            "agent": request.prompt.agent_id,
            "round": request.round_number,
            "schema_retry": request.schema_retry,
            "final_required": request.final_required,
            "prompt_hash": f"sha256:{sha256_hex(request.prompt.user.encode())}",
        }
        return f"call-{sha256_hex(canonical_json(identity))}"

    def _response_path(self, call_key: str, attempt: int) -> Path:
        return self.response_root / f"{call_key}-attempt-{attempt}.sealed.json"

    def _serialize_response(self, response: AdapterResponse) -> Mapping[str, object]:
        return {
            "raw_output": response.raw_output,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cost_usd": str(response.usage.cost_usd),
            },
            "error_class": response.error_class,
            "declared_tool_calls": [dict(item) for item in response.declared_tool_calls],
            "operational_metadata": dict(response.operational_metadata),
        }

    def _deserialize_response(self, value: object) -> AdapterResponse:
        if not isinstance(value, Mapping):
            raise ValueError("stored adapter response must be a mapping")
        usage = value["usage"]
        if not isinstance(usage, Mapping):
            raise ValueError("stored adapter usage must be a mapping")
        tools = value.get("declared_tool_calls", [])
        metadata = value.get("operational_metadata", {})
        if not isinstance(tools, Sequence) or not isinstance(metadata, Mapping):
            raise ValueError("stored adapter metadata is malformed")
        return AdapterResponse(
            raw_output=str(value["raw_output"]),
            usage=Usage(
                input_tokens=int(str(usage["input_tokens"])),
                output_tokens=int(str(usage["output_tokens"])),
                cost_usd=Decimal(str(usage["cost_usd"])),
            ),
            error_class=(
                str(value["error_class"]) if value.get("error_class") is not None else None
            ),
            declared_tool_calls=tuple(dict(item) for item in tools if isinstance(item, Mapping)),
            operational_metadata={str(name): item for name, item in metadata.items()},
        )

    def _load_recorded(
        self, call_key: str
    ) -> tuple[AdapterResponse | None, tuple[Mapping[str, object], ...]]:
        records = tuple(
            item
            for item in self.ledger.records
            if item.get("call_key") == call_key and "transport_attempt" in item
        )
        recorded_attempts = {int(str(item["transport_attempt"])) for item in records}
        for path in self.response_root.glob(f"{call_key}-attempt-*.sealed.json"):
            attempt = int(path.stem.rsplit("-", 1)[-1].split(".", 1)[0])
            if attempt not in recorded_attempts:
                raise PermissionError("orphaned encrypted response requires quarantine")
        if not records:
            return None, records
        retryable = {
            "timeout",
            "transient-transport",
            "invalid-provider-json",
            "rate-limit",
            "transient-provider",
        }
        record = records[-1]
        terminal = (
            record.get("status") == "success"
            or record.get("error_class") not in retryable
            or len(records) >= 2
        )
        if not terminal:
            return None, records
        attempt = int(str(record["transport_attempt"]))
        path = self._response_path(call_key, attempt)
        _require_secure_regular_file(path)
        stored = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(stored, Mapping):
            raise ValueError("stored sealed response must be a mapping")
        manifest = stored["manifest"]
        if not isinstance(manifest, Mapping):
            raise ValueError("stored response manifest must be a mapping")
        sealed = SealedObject(
            domain=str(manifest["domain"]),
            nonce_hex=str(manifest["nonce_hex"]),
            ciphertext=bytes.fromhex(str(stored["ciphertext_hex"])),
            ciphertext_sha256=str(manifest["ciphertext_sha256"]),
            associated_data_sha256=str(manifest["associated_data_sha256"]),
        )
        return (
            self._deserialize_response(unseal_object(sealed, key=self.response_key)),
            records,
        )

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        call_key = self._key(request)
        resumed, records = self._load_recorded(call_key)
        if resumed is not None:
            return resumed
        maximum_cost = (
            Decimal("0")
            if self.provider not in PROVIDERS
            else (
                (Decimal("3") if self.provider == "Anthropic" else Decimal("2.5")) * Decimal(4_000)
                + Decimal("15") * Decimal(request.max_output_tokens)
            )
            / Decimal(1_000_000)
        )
        prior_attempts = len(records)
        if prior_attempts >= 2:
            raise PermissionError("registered transport retry budget is exhausted")
        retryable = {
            "timeout",
            "transient-transport",
            "invalid-provider-json",
            "rate-limit",
            "transient-provider",
        }
        for attempt in range(prior_attempts, 2):
            self.ledger.guard_next(
                provider=self.provider,
                input_tokens=4_000,
                output_tokens=request.max_output_tokens,
                cost_usd=maximum_cost,
            )
            response = self.adapter.respond(request)
            if (
                response.error_class is None
                and self.adapter.manifest.live_capable
                and response.operational_metadata.get("model") != self.model
            ):
                response = AdapterResponse(
                    raw_output=response.raw_output,
                    usage=response.usage,
                    error_class="exact-model-mismatch",
                    declared_tool_calls=response.declared_tool_calls,
                    operational_metadata=response.operational_metadata,
                )
            if (
                response.error_class is None
                and self.adapter.manifest.live_capable
                and response.operational_metadata.get("hidden_reasoning_stored") is not False
            ):
                response = AdapterResponse(
                    raw_output=response.raw_output,
                    usage=response.usage,
                    error_class="hidden-reasoning-boundary",
                    declared_tool_calls=response.declared_tool_calls,
                    operational_metadata=response.operational_metadata,
                )
            sealed = seal_object(
                domain=f"provider-response/{call_key}/attempt-{attempt}",
                value=self._serialize_response(response),
                key=self.response_key,
                nonce=secrets.token_bytes(12),
            )
            atomic_private_write(
                self._response_path(call_key, attempt),
                canonical_json(
                    {
                        "manifest": sealed.manifest(),
                        "ciphertext_hex": sealed.ciphertext.hex(),
                    }
                )
                + b"\n",
            )
            self.ledger.append(
                {
                    "event_type": "provider-call",
                    "idempotency_key": f"{call_key}/attempt-{attempt}",
                    "call_key": call_key,
                    "transport_attempt": attempt,
                    "status": "success" if response.error_class is None else "error",
                    "provider": self.provider,
                    "model": self.model,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cost_usd": str(response.usage.cost_usd),
                    "error_class": response.error_class,
                    "schema_retry": request.schema_retry,
                }
            )
            if response.error_class not in retryable:
                return response
        return response


class PilotBatchRunner:
    """Provider-neutral staged runner used by mocks and exact direct adapters."""

    def __init__(
        self,
        *,
        state_root: Path,
        ledger: AppendOnlyLedger,
        trace_key: bytes,
    ) -> None:
        self.state_root = state_root
        self.ledger = ledger
        self.trace_key = trace_key
        self.trace_root = state_root / "encrypted-traces"
        _secure_mkdir(self.trace_root)

    def run_stage(
        self,
        *,
        stage: str,
        tasks: Sequence[TaskInstance],
        adapters: Mapping[str, AgentAdapter],
        verify_metrics: bool = True,
        persist_traces: bool = True,
    ) -> Mapping[str, object]:
        if stage not in {"public-canary", "private-prefix", "fixed-full-batch"}:
            raise ValueError("unknown pilot stage")
        if set(adapters) != set(MODELS):
            raise PermissionError("both exact frozen model routes are required")
        runs = 0
        disagreements = 0
        protocol_errors = 0
        contamination_findings = 0
        for model, adapter in adapters.items():
            validate_provider_route(PROVIDERS[MODELS.index(model)], model)
            for task in tasks:
                for architecture in ARCHITECTURES:
                    run = run_architecture(task, architecture, adapter)
                    contamination_findings += sum(
                        classify_text(turn.response.raw_output).classification
                        in {"direct-leakage", "probable-memorization"}
                        for turn in run.turns
                    )
                    if verify_metrics:
                        metrics = asdict(evaluate_run(task, run))
                        disagreements += len(verify_method_agreement(metrics, task, run))
                    protocol_errors += len(run.protocol_errors)
                    trace = build_trace(run)
                    if trace.audit["hidden_reasoning_stored"] is not False:
                        raise PermissionError("hidden reasoning storage is prohibited")
                    if persist_traces:
                        trace_id = f"{stage}/{model}/{task.task_id}/{architecture}"
                        sealed = seal_object(
                            domain=f"raw-trace/{trace_id}",
                            value=trace.raw,
                            key=self.trace_key,
                            nonce=secrets.token_bytes(12),
                        )
                        trace_path = self.trace_root / f"{sha256_hex(trace_id.encode())}.sealed"
                        atomic_private_write(
                            trace_path,
                            canonical_json(
                                {
                                    "manifest": sealed.manifest(),
                                    "ciphertext_hex": sealed.ciphertext.hex(),
                                }
                            )
                            + b"\n",
                        )
                    runs += 1
        if disagreements:
            raise RuntimeError("Method A/B disagreement requires quarantine")
        if contamination_findings:
            raise RuntimeError("direct or probable contamination requires quarantine")
        if stage in {"public-canary", "private-prefix"} and protocol_errors:
            raise RuntimeError(f"{stage} protocol gate failed")
        return {
            "stage": stage,
            "tasks": len(tasks),
            "runs": runs,
            "method_disagreements": disagreements,
            "protocol_errors": protocol_errors,
            "contamination_findings": contamination_findings,
        }


def create_output_lock(
    objects: Mapping[str, bytes], *, ledger: AppendOnlyLedger
) -> Mapping[str, object]:
    if not objects:
        raise ValueError("output lock requires at least one object")
    if not any(record.get("event_type") == "provider-phase-closed" for record in ledger.records):
        raise PermissionError("provider phase must be closed before output lock")
    manifest: dict[str, object] = {
        "schema_version": "treasurebench-agents-v1-output-lock-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "objects": {
            name: f"sha256:{sha256_hex(payload)}" for name, payload in sorted(objects.items())
        },
        "ledger_head": ledger.records[-1]["record_hash"] if ledger.records else "GENESIS",
        "provider_phase_closed": True,
    }
    manifest["lock_hash"] = f"sha256:{sha256_hex(canonical_json(manifest))}"
    return manifest


def verify_output_lock(
    lock: Mapping[str, object], objects: Mapping[str, bytes], *, ledger: AppendOnlyLedger
) -> None:
    mutable = dict(lock)
    actual = mutable.pop("lock_hash", None)
    if actual != f"sha256:{sha256_hex(canonical_json(mutable))}":
        raise ValueError("output-lock hash mismatch")
    expected = {name: f"sha256:{sha256_hex(payload)}" for name, payload in sorted(objects.items())}
    if mutable.get("objects") != expected:
        raise ValueError("output-lock object mismatch")
    head = ledger.records[-1]["record_hash"] if ledger.records else "GENESIS"
    if mutable.get("ledger_head") != head:
        raise ValueError("output-lock ledger mismatch")


def unseal_answer_after_lock(
    sealed: SealedObject,
    *,
    key: bytes,
    lock: Mapping[str, object] | None,
    objects: Mapping[str, bytes],
    ledger: AppendOnlyLedger,
) -> object:
    if lock is None:
        raise PermissionError("answer unseal requires an output lock")
    verify_output_lock(lock, objects, ledger=ledger)
    return unseal_object(sealed, key=key)


def require_commitment(expected: str, actual: str, *, domain: str) -> None:
    if expected != actual:
        raise ValueError(f"{domain} commitment mismatch")


def validate_agent_visible_record(record: Mapping[str, object]) -> None:
    forbidden = {
        "answer",
        "answer_key",
        "baseline",
        "primitive_state",
        "seed",
        "task_key",
        "generator_parameters",
    }
    if forbidden.intersection(record):
        raise PermissionError("undeclared private signal or evaluator field")


def validate_provider_route(provider: str, model: str) -> None:
    allowed = dict(zip(PROVIDERS, MODELS, strict=True))
    if provider not in allowed or allowed[provider] != model:
        raise PermissionError("provider/model route is outside the frozen pilot")


def validate_lock_inventory(objects: Mapping[str, bytes]) -> None:
    required = {
        "task-ciphertext",
        "answer-ciphertext",
        "access-log",
        "usage-cost-ledger",
    }
    if not required.issubset(objects) or not any(name.startswith("trace/") for name in objects):
        raise ValueError("output-lock inventory is incomplete")


def validate_contamination_probe_set(probe_names: Iterable[str]) -> None:
    if frozenset(probe_names) != REQUIRED_CONTAMINATION_PROBES:
        raise ValueError("contamination probe set is incomplete")


def validate_public_pilot_summary(summary: Mapping[str, object]) -> None:
    forbidden_keys = {
        "private_path",
        "raw_trace",
        "task_text",
        "answer",
        "ranking",
        "composite",
        "task_level_metrics",
    }
    if forbidden_keys.intersection(summary):
        raise PermissionError("public pilot summary crosses the redaction boundary")
    if summary.get("study_id") == "DD-023":
        raise PermissionError("DD-023 allocation is prohibited")
    if summary.get("claim_id") is not None:
        raise PermissionError("claim creation is prohibited")
    if summary.get("redaction_status") != "pass":
        raise PermissionError("public pilot summary requires passing redaction")


def variant_for_slot(slot: Mapping[str, object]) -> int:
    target = 0 if slot["target_relabeling_class"] == "target-A" else 1
    agent = 0 if slot["agent_relabeling_class"] == "agent-A" else 2
    return target + agent


def generate_allocated_tasks(
    repo: Path,
    *,
    authorization: Mapping[str, object],
    material: str,
) -> tuple[TaskInstance, ...]:
    allocation = load_allocation(repo)
    slots = allocation["slots"]
    assert isinstance(slots, list)
    cells = {(cell.family_id, cell.cell_index): cell for cell in canonical_cells()}
    permit = generation_permit(authorization)
    tasks = []
    for slot in slots:
        assert isinstance(slot, Mapping)
        cell = cells[(str(slot["family_id"]), int(str(slot["cell_index"])))]
        task = generate_instance(
            cell,
            variant=variant_for_slot(slot),
            public_fixture=False,
            material=f"{material}/{slot['slot_id']}",
            hidden_labels=False,
            authorization=authorization,
            custody_context=permit,
        )
        tasks.append(task)
    return tuple(tasks)


def synthetic_authorization(repo: Path) -> Mapping[str, object]:
    now = datetime.now(UTC)
    value: dict[str, object] = {
        "schema_version": "treasurebench-agents-v1-pilot-authorization-v1",
        "authorization_id": "SYNTHETIC-OFFLINE-REHEARSAL-ONLY",
        "authorization_status": "authorized",
        "authorized_at_utc": now.isoformat(),
        "expires_at_utc": datetime.max.replace(tzinfo=UTC).isoformat(),
        "revoked": False,
        "revocation_reason": None,
        "purpose": "treasurebench-agents-v1-sealed-engineering-pilot",
        "synthetic": True,
        "owner_attestation": (
            "Synthetic fixture for offline testing only; it grants no live or private authority."
        ),
        "authorized_base_commit": BASE_COMMIT,
        "authorized_execution_commit": _git(repo, "rev-parse", "HEAD"),
        "execution_tree_hash": execution_tree_hash(repo),
        "issue": 187,
        "branch": BRANCH,
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "models": list(MODELS),
        "architectures": list(ARCHITECTURES),
        "counts": {
            "tasks": 50,
            "batches": 1,
            "repeats": 1,
            "architectures": 5,
            "cloud_models": 2,
        },
        "caps": {
            "total_usd": 100,
            "provider_usd": {"OpenAI": 50, "Anthropic": 50},
            "calls": 5200,
            "input_tokens": 10_600_000,
            "output_tokens": 1_400_000,
            "live_concurrency": 2,
        },
        "permissions": {
            **{name: True for name in REQUIRED_TRUE_PERMISSIONS},
            **{name: False for name in REQUIRED_FALSE_PERMISSIONS},
        },
        "retention_days": 365,
        "public_summary_boundary": "redacted-engineering-only-no-task-level-performance",
    }
    return validate_pilot_authorization(
        value,
        repo=repo,
        allow_synthetic=True,
        expected_commit=str(value["authorized_execution_commit"]),
        expected_tree_hash=str(value["execution_tree_hash"]),
    )


def run_synthetic_rehearsal(repo: Path) -> Mapping[str, object]:
    """Run all 50 slots × five architectures × two synthetic route labels."""
    request = load_request(repo)
    allocation = load_allocation(repo)
    authorization = synthetic_authorization(repo)
    material = "SYNTHETIC-PUBLIC-NONSECRET-PILOT-MATERIAL-V1"
    tasks = generate_allocated_tasks(repo, authorization=authorization, material=material)
    key_task = hashlib.sha256(b"synthetic/task-key").digest()
    key_answer = hashlib.sha256(b"synthetic/answer-key").digest()
    task_payload = [task.visible_record() for task in tasks]
    answer_payload = [task.evaluator_record() for task in tasks]
    task_seal = seal_object(
        domain="synthetic-task-batch",
        value=task_payload,
        key=key_task,
        nonce=hashlib.sha256(b"synthetic/task-nonce").digest()[:12],
    )
    answer_seal = seal_object(
        domain="synthetic-answer-key",
        value=answer_payload,
        key=key_answer,
        nonce=hashlib.sha256(b"synthetic/answer-nonce").digest()[:12],
    )
    with tempfile.TemporaryDirectory(prefix="treasurebench-pilot-rehearsal-") as temporary:
        root = Path(temporary)
        _secure_mkdir(root)
        ledger = AppendOnlyLedger(root / "usage-cost-ledger.jsonl")
        access_ledger = AppendOnlyLedger(root / "access-log.jsonl")
        access_ledger.append(
            {
                "event_type": "custody-access",
                "status": "success",
                "operation": "synthetic-seal",
                "private_material": False,
            }
        )
        encrypted_traces: dict[str, bytes] = {}
        disagreement_count = 0
        run_count = 0
        turn_count = 0
        redacted_trace_count = 0
        for model_index, model in enumerate(MODELS):
            for task in tasks:
                for architecture in ARCHITECTURES:
                    run = run_architecture(task, architecture, MockAdapter())
                    metrics = asdict(evaluate_run(task, run))
                    disagreement_count += len(verify_method_agreement(metrics, task, run))
                    trace = build_trace(run)
                    if trace.audit["hidden_reasoning_stored"] is not False:
                        raise ValueError("hidden reasoning trace boundary failed")
                    redacted_trace_count += 1
                    trace_id = f"{model_index}-{task.task_id}-{architecture}"
                    trace_key = hashlib.sha256(f"synthetic/trace/{trace_id}".encode()).digest()
                    trace_nonce = hashlib.sha256(
                        f"synthetic/trace-nonce/{trace_id}".encode()
                    ).digest()[:12]
                    sealed_trace = seal_object(
                        domain=f"synthetic-trace/{trace_id}",
                        value=trace.raw,
                        key=trace_key,
                        nonce=trace_nonce,
                    )
                    encrypted_traces[trace_id] = sealed_trace.ciphertext
                    ledger.append(
                        {
                            "idempotency_key": trace_id,
                            "status": "success",
                            "provider": PROVIDERS[model_index],
                            "model": model,
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "cost_usd": "0",
                            "synthetic": True,
                        }
                    )
                    run_count += 1
                    turn_count += len(run.turns)
        access_ledger.append(
            {
                "event_type": "custody-access",
                "status": "success",
                "operation": "answer-unseal-approved-after-provider-close",
                "private_material": False,
            }
        )
        ledger.close_provider_phase()
        objects = {
            "task-ciphertext": task_seal.ciphertext,
            "answer-ciphertext": answer_seal.ciphertext,
            "access-log": access_ledger.path.read_bytes(),
            "usage-cost-ledger": ledger.path.read_bytes(),
            **{f"trace/{name}": value for name, value in encrypted_traces.items()},
        }
        validate_lock_inventory(objects)
        lock = create_output_lock(objects, ledger=ledger)
        verify_output_lock(lock, objects, ledger=ledger)
        unsealed_answers = unseal_answer_after_lock(
            answer_seal,
            key=key_answer,
            lock=lock,
            objects=objects,
            ledger=ledger,
        )
        if canonical_json(unsealed_answers) != canonical_json(answer_payload):
            raise ValueError("synthetic answer unseal mismatch")
        contamination = [asdict(item) for item in run_public_probes()]
        direct = sum(
            item["finding"]["classification"] == "direct-leakage" for item in contamination
        )
        probable = sum(
            item["finding"]["classification"] == "probable-memorization" for item in contamination
        )
        if disagreement_count or direct != 2 or probable != 2:
            raise ValueError("synthetic verification or contamination gate failed")
        summary: dict[str, object] = {
            "schema_version": "treasurebench-agents-v1-pilot-rehearsal-v1",
            "status": "pass",
            "classification": "public-synthetic-only",
            "campaign_id": CAMPAIGN_ID,
            "batch_id": BATCH_ID,
            "tasks": len(tasks),
            "families": len({task.family_id for task in tasks}),
            "architectures": len(ARCHITECTURES),
            "synthetic_route_labels": len(MODELS),
            "runs": run_count,
            "turns": turn_count,
            "method_disagreements": disagreement_count,
            "contamination_probes": len(contamination),
            "contamination_probe_classification": "pass",
            "encrypted_traces": len(encrypted_traces),
            "redacted_traces_verified": redacted_trace_count,
            "output_lock_verified": True,
            "provider_calls": 0,
            "external_cost_usd": "0",
            "credential_reads": 0,
            "network_enabled": False,
            "private_material": False,
            "redaction_status": "pass",
            "allocation_commitment": f"sha256:{sha256_hex(canonical_json(allocation))}",
            "request_commitment": f"sha256:{sha256_hex(canonical_json(request))}",
        }
        summary["rehearsal_hash"] = f"sha256:{sha256_hex(canonical_json(summary))}"
        validate_public_pilot_summary(summary)
        return summary


def _expect_rejection(name: str, operation: object) -> Mapping[str, object]:
    try:
        assert callable(operation)
        operation()
    except (
        AssertionError,
        InvalidTag,
        KeyError,
        OSError,
        PermissionError,
        TypeError,
        ValueError,
    ):
        return {"corruption_id": name, "status": "rejected"}
    return {"corruption_id": name, "status": "accepted"}


def audit_pilot_corruptions(repo: Path) -> tuple[Mapping[str, object], ...]:
    """Exercise 40 synthetic mutations at their authorization/custody/lock boundaries."""
    base = synthetic_authorization(repo)
    commit = str(base["authorized_execution_commit"])
    tree_hash = str(base["execution_tree_hash"])
    cases: list[Mapping[str, object]] = []

    def auth_case(name: str, mutate: object, *, live: bool = False) -> None:
        def operation() -> None:
            candidate = deepcopy(dict(base))
            assert callable(mutate)
            mutate(candidate)
            validate_pilot_authorization(
                candidate,
                repo=repo,
                allow_synthetic=not live,
                expected_commit=commit,
                expected_tree_hash=tree_hash,
            )

        cases.append(_expect_rejection(name, operation))

    auth_case("AUTH-01-synthetic-live", lambda _: None, live=True)
    auth_case("AUTH-02-inactive", lambda item: item.update(authorization_status="inactive"))
    auth_case("AUTH-03-revoked", lambda item: item.update(revoked=True))
    auth_case(
        "AUTH-04-expired",
        lambda item: item.update(expires_at_utc="2000-01-01T00:00:00+00:00"),
    )
    auth_case(
        "AUTH-05-future",
        lambda item: item.update(authorized_at_utc="9999-01-01T00:00:00+00:00"),
    )
    auth_case("AUTH-06-base", lambda item: item.update(authorized_base_commit="0" * 40))
    auth_case("AUTH-07-commit", lambda item: item.update(authorized_execution_commit="1" * 40))
    auth_case("AUTH-08-tree", lambda item: item.update(execution_tree_hash=f"sha256:{'2' * 64}"))
    auth_case("AUTH-09-issue", lambda item: item.update(issue=188))
    auth_case("AUTH-10-branch", lambda item: item.update(branch="main"))
    auth_case("AUTH-11-campaign", lambda item: item.update(campaign_id="wrong"))
    auth_case("AUTH-12-batch", lambda item: item.update(batch_id="wrong"))
    auth_case("AUTH-13-model", lambda item: item.update(models=["gpt-latest", MODELS[1]]))
    auth_case("AUTH-14-architecture", lambda item: item.update(architectures=[]))
    auth_case("AUTH-15-counts", lambda item: item["counts"].update(tasks=49))
    auth_case("AUTH-16-total-cap", lambda item: item["caps"].update(total_usd=99))
    auth_case(
        "AUTH-17-openai-cap",
        lambda item: item["caps"]["provider_usd"].update(OpenAI=49),
    )
    auth_case(
        "AUTH-18-anthropic-cap",
        lambda item: item["caps"]["provider_usd"].update(Anthropic=49),
    )
    auth_case("AUTH-19-call-cap", lambda item: item["caps"].update(calls=5199))
    auth_case("AUTH-20-input-cap", lambda item: item["caps"].update(input_tokens=10_599_999))
    auth_case("AUTH-21-output-cap", lambda item: item["caps"].update(output_tokens=1_399_999))
    auth_case("AUTH-22-concurrency", lambda item: item["caps"].update(live_concurrency=1))
    auth_case(
        "AUTH-23-live-permission",
        lambda item: item["permissions"].update(live_provider_calls=False),
    )
    auth_case(
        "AUTH-24-private-permission",
        lambda item: item["permissions"].update(private_generation=False),
    )
    auth_case(
        "AUTH-25-claim-permission",
        lambda item: item["permissions"].update(claim=True),
    )
    auth_case("AUTH-26-attestation", lambda item: item.update(owner_attestation="short"))
    auth_case("AUTH-27-missing-field", lambda item: item.pop("authorization_id"))

    key = hashlib.sha256(b"corruption-key").digest()
    nonce = hashlib.sha256(b"corruption-nonce").digest()[:12]
    sealed = seal_object(domain="corruption", value={"ok": True}, key=key, nonce=nonce)
    cases.append(
        _expect_rejection(
            "CUSTODY-01-ciphertext",
            lambda: unseal_object(
                SealedObject(
                    sealed.domain,
                    sealed.nonce_hex,
                    sealed.ciphertext[:-1] + bytes([sealed.ciphertext[-1] ^ 1]),
                    sealed.ciphertext_sha256,
                    sealed.associated_data_sha256,
                ),
                key=key,
            ),
        )
    )
    cases.append(
        _expect_rejection(
            "CUSTODY-02-associated-data",
            lambda: unseal_object(
                SealedObject(
                    sealed.domain,
                    sealed.nonce_hex,
                    sealed.ciphertext,
                    sealed.ciphertext_sha256,
                    f"sha256:{'0' * 64}",
                ),
                key=key,
            ),
        )
    )
    cases.append(
        _expect_rejection(
            "CUSTODY-03-wrong-key",
            lambda: unseal_object(sealed, key=hashlib.sha256(b"wrong").digest()),
        )
    )
    cases.append(
        _expect_rejection(
            "CUSTODY-04-bad-key-length",
            lambda: seal_object(domain="bad", value={}, key=b"x", nonce=nonce),
        )
    )
    cases.append(
        _expect_rejection(
            "CUSTODY-05-private-generation",
            lambda: generate_instance(canonical_cells()[0], variant=0, public_fixture=False),
        )
    )

    with tempfile.TemporaryDirectory(prefix="pilot-corruptions-") as temporary:
        root = Path(temporary)
        ledger = AppendOnlyLedger(root / "ledger.jsonl")
        ledger.append(
            {
                "idempotency_key": "call-1",
                "status": "success",
                "provider": "OpenAI",
                "input_tokens": 1,
                "output_tokens": 1,
                "cost_usd": "1",
            }
        )
        cases.append(
            _expect_rejection(
                "LEDGER-01-duplicate",
                lambda: ledger.append({"idempotency_key": "call-1", "status": "success"}),
            )
        )
        tampered = root / "tampered.jsonl"
        tampered_payload = ledger.path.read_bytes().replace(b'"cost_usd":"1"', b'"cost_usd":"2"')
        atomic_private_write(tampered, tampered_payload)
        cases.append(_expect_rejection("LEDGER-02-hash-chain", lambda: AppendOnlyLedger(tampered)))
        cases.append(
            _expect_rejection(
                "LEDGER-03-provider",
                lambda: ledger.guard_next(
                    provider="OpenRouter",
                    input_tokens=1,
                    output_tokens=1,
                    cost_usd=Decimal("0"),
                ),
            )
        )
        cases.append(
            _expect_rejection(
                "LEDGER-04-provider-cap",
                lambda: ledger.guard_next(
                    provider="OpenAI",
                    input_tokens=1,
                    output_tokens=1,
                    cost_usd=Decimal("50"),
                ),
            )
        )
        cases.append(
            _expect_rejection(
                "LOCK-01-before-close",
                lambda: create_output_lock({"a": b"a"}, ledger=ledger),
            )
        )
        ledger.close_provider_phase()
        objects = {"a": b"a", "ledger": ledger.path.read_bytes()}
        lock = create_output_lock(objects, ledger=ledger)
        cases.append(
            _expect_rejection(
                "LEDGER-05-after-close",
                lambda: ledger.append({"idempotency_key": "call-2", "status": "success"}),
            )
        )
        cases.append(
            _expect_rejection(
                "LOCK-02-object",
                lambda: verify_output_lock(lock, {"a": b"b"}, ledger=ledger),
            )
        )
        bad_lock = dict(lock)
        bad_lock["provider_phase_closed"] = False
        cases.append(
            _expect_rejection(
                "LOCK-03-manifest", lambda: verify_output_lock(bad_lock, objects, ledger=ledger)
            )
        )

    task = generate_instance(canonical_cells()[0], variant=0, public_fixture=True)
    run = run_architecture(task, ARCHITECTURES[0], MockAdapter())
    trace = dict(build_trace(run).raw)
    events = trace["events"]
    assert isinstance(events, list)
    assert isinstance(events[0], dict)
    events[0]["agent_id"] = "CORRUPTED"
    cases.append(
        _expect_rejection(
            "TRACE-01-event-hash",
            lambda: (_ for _ in ()).throw(ValueError()) if not verify_trace_hashes(trace) else None,
        )
    )
    cases.extend(_audit_required_pilot_corruptions(repo, base, sealed, key, task, run, trace))
    return tuple(cases)


def _reject_true(condition: bool, message: str) -> None:
    if condition:
        raise ValueError(message)


def _audit_required_pilot_corruptions(
    repo: Path,
    base: Mapping[str, object],
    sealed: SealedObject,
    key: bytes,
    task: TaskInstance,
    run: ArchitectureRun,
    mutated_trace: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    """Implement the 35 corruption names fixed in the owner brief."""
    required: list[Mapping[str, object]] = []
    commit = str(base["authorized_execution_commit"])
    tree_hash = str(base["execution_tree_hash"])

    def auth(name: str, mutate: object) -> None:
        def operation() -> None:
            value = deepcopy(dict(base))
            assert callable(mutate)
            mutate(value)
            validate_pilot_authorization(
                value,
                repo=repo,
                allow_synthetic=True,
                expected_commit=commit,
                expected_tree_hash=tree_hash,
            )

        required.append(_expect_rejection(name, operation))

    auth(
        "PILOT-01-execution-tree-mutation-after-authorization",
        lambda item: item.update(execution_tree_hash=f"sha256:{'f' * 64}"),
    )
    auth(
        "PILOT-02-wrong-base-commit",
        lambda item: item.update(authorized_base_commit="f" * 40),
    )
    auth(
        "PILOT-03-wrong-execution-commit",
        lambda item: item.update(authorized_execution_commit="e" * 40),
    )
    auth("PILOT-04-wrong-issue", lambda item: item.update(issue=999))
    auth("PILOT-05-wrong-branch", lambda item: item.update(branch="main"))
    auth("PILOT-06-wrong-batch-id", lambda item: item.update(batch_id="wrong"))
    required.extend(
        (
            _expect_rejection(
                "PILOT-07-wrong-provider-model",
                lambda: validate_provider_route("OpenAI", "gpt-wrong"),
            ),
            _expect_rejection(
                "PILOT-08-moving-alias",
                lambda: validate_provider_route("OpenAI", "gpt-5.4-latest"),
            ),
            _expect_rejection(
                "PILOT-09-fallback-route",
                lambda: validate_provider_route("OpenRouter", MODELS[0]),
            ),
        )
    )

    with tempfile.TemporaryDirectory(prefix="pilot-required-corruptions-") as temporary:
        root = Path(temporary)
        cap_ledger = AppendOnlyLedger(root / "caps.jsonl")
        cap_ledger.records = [
            {
                "record_hash": "synthetic",
                "status": "success",
                "provider": "OpenAI",
                "cost_usd": "50",
                "input_tokens": MAX_INPUT_TOKENS,
                "output_tokens": MAX_OUTPUT_TOKENS,
            },
            {
                "record_hash": "synthetic",
                "status": "success",
                "provider": "Anthropic",
                "cost_usd": "50",
            },
        ]
        required.append(
            _expect_rejection(
                "PILOT-10-spend-cap-breach",
                lambda: cap_ledger.guard_next(
                    provider="OpenAI",
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=Decimal("0.01"),
                ),
            )
        )
        provider_ledger = AppendOnlyLedger(root / "provider.jsonl")
        provider_ledger.records = [
            {
                "record_hash": "synthetic",
                "status": "success",
                "provider": "OpenAI",
                "cost_usd": "50",
            }
        ]
        required.append(
            _expect_rejection(
                "PILOT-11-provider-cap-breach",
                lambda: provider_ledger.guard_next(
                    provider="OpenAI",
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=Decimal("0.01"),
                ),
            )
        )
        call_ledger = AppendOnlyLedger(root / "calls.jsonl")
        call_ledger.records = [
            {
                "record_hash": "synthetic",
                "status": "success",
                "provider": "OpenAI",
            }
            for _ in range(MAX_CALLS)
        ]
        required.append(
            _expect_rejection(
                "PILOT-12-call-cap-breach",
                lambda: call_ledger.guard_next(
                    provider="OpenAI",
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=Decimal("0"),
                ),
            )
        )
        required.append(
            _expect_rejection(
                "PILOT-13-token-cap-breach",
                lambda: cap_ledger.guard_next(
                    provider="OpenAI",
                    input_tokens=1,
                    output_tokens=0,
                    cost_usd=Decimal("0"),
                ),
            )
        )
        duplicate = AppendOnlyLedger(root / "duplicate.jsonl")
        duplicate.append({"idempotency_key": "paid", "status": "success"})
        required.append(
            _expect_rejection(
                "PILOT-20-duplicate-paid-call-resume",
                lambda: duplicate.append({"idempotency_key": "paid", "status": "success"}),
            )
        )
        lock_ledger = AppendOnlyLedger(root / "lock.jsonl")
        lock_ledger.close_provider_phase()
        objects = {
            "task-ciphertext": b"task",
            "answer-ciphertext": b"answer",
            "access-log": b"access",
            "usage-cost-ledger": lock_ledger.path.read_bytes(),
            "trace/one": b"trace",
        }
        lock = create_output_lock(objects, ledger=lock_ledger)
        bad_lock = dict(lock)
        bad_lock["provider_phase_closed"] = False
        required.append(
            _expect_rejection(
                "PILOT-24-output-lock-mutation",
                lambda: verify_output_lock(bad_lock, objects, ledger=lock_ledger),
            )
        )
        for name in (
            "PILOT-22-answer-key-access-before-lock",
            "PILOT-25-unseal-before-lock",
        ):
            required.append(
                _expect_rejection(
                    name,
                    lambda: unseal_answer_after_lock(
                        sealed,
                        key=key,
                        lock=None,
                        objects=objects,
                        ledger=lock_ledger,
                    ),
                )
            )

    required.append(
        _expect_rejection(
            "PILOT-14-seed-commitment-mutation",
            lambda: require_commitment("sha256:expected", "sha256:mutated", domain="seed"),
        )
    )
    for name, ciphertext in (
        ("PILOT-15-task-ciphertext-mutation", sealed.ciphertext + b"x"),
        ("PILOT-16-answer-ciphertext-mutation", b"x" + sealed.ciphertext),
    ):
        required.append(
            _expect_rejection(
                name,
                lambda payload=ciphertext: unseal_object(
                    SealedObject(
                        sealed.domain,
                        sealed.nonce_hex,
                        payload,
                        sealed.ciphertext_sha256,
                        sealed.associated_data_sha256,
                    ),
                    key=key,
                ),
            )
        )
    for name, label in (
        ("PILOT-17-task-key-substitution", b"task-wrong"),
        ("PILOT-18-answer-key-substitution", b"answer-wrong"),
    ):
        required.append(
            _expect_rejection(
                name,
                lambda material=label: unseal_object(sealed, key=hashlib.sha256(material).digest()),
            )
        )
    required.extend(
        (
            _expect_rejection(
                "PILOT-19-access-log-deletion",
                lambda: validate_lock_inventory(
                    {
                        "task-ciphertext": b"task",
                        "answer-ciphertext": b"answer",
                        "usage-cost-ledger": b"ledger",
                        "trace/one": b"trace",
                    }
                ),
            ),
            _expect_rejection(
                "PILOT-21-undeclared-private-signal-access",
                lambda: validate_agent_visible_record({"primitive_state": {"target": "A"}}),
            ),
            _expect_rejection(
                "PILOT-23-trace-mutation",
                lambda: _reject_true(not verify_trace_hashes(mutated_trace), "trace mutation"),
            ),
            _expect_rejection(
                "PILOT-26-redaction-omission",
                lambda: validate_public_pilot_summary({"redaction_status": "fail"}),
            ),
            _expect_rejection(
                "PILOT-27-baseline-mutation",
                lambda: require_commitment("sha256:baseline", "sha256:mutated", domain="baseline"),
            ),
        )
    )
    method_a = asdict(evaluate_run(task, run))
    method_a["group_discovery"] = "mutated"
    required.extend(
        (
            _expect_rejection(
                "PILOT-28-metric-mutation",
                lambda: _reject_true(
                    bool(verify_method_agreement(method_a, task, run)),
                    "metric mutation",
                ),
            ),
            _expect_rejection(
                "PILOT-29-method-a-b-disagreement",
                lambda: _reject_true(
                    bool(verify_method_agreement({}, task, run)),
                    "Method A/B disagreement",
                ),
            ),
            _expect_rejection(
                "PILOT-30-contamination-probe-suppression",
                lambda: validate_contamination_probe_set(
                    REQUIRED_CONTAMINATION_PROBES - {"answer-key-leakage"}
                ),
            ),
            _expect_rejection(
                "PILOT-31-private-path-committed",
                lambda: validate_public_pilot_summary(
                    {"redaction_status": "pass", "private_path": "/private"}
                ),
            ),
            _expect_rejection(
                "PILOT-32-raw-trace-committed",
                lambda: validate_public_pilot_summary(
                    {"redaction_status": "pass", "raw_trace": {}}
                ),
            ),
            _expect_rejection(
                "PILOT-33-detailed-pilot-ranking-published",
                lambda: validate_public_pilot_summary({"redaction_status": "pass", "ranking": []}),
            ),
            _expect_rejection(
                "PILOT-34-dd-023-allocation",
                lambda: validate_public_pilot_summary(
                    {"redaction_status": "pass", "study_id": "DD-023"}
                ),
            ),
            _expect_rejection(
                "PILOT-35-claim-creation",
                lambda: validate_public_pilot_summary(
                    {"redaction_status": "pass", "claim_id": "DD-C-0111"}
                ),
            ),
        )
    )
    if len(required) != 35:
        raise AssertionError("required pilot corruption inventory must contain 35 cases")
    return tuple(required)


def pilot_offline_readiness(repo: Path) -> Mapping[str, object]:
    request = load_request(repo)
    allocation = load_allocation(repo)
    return {
        "status": "pass",
        "phase": "A",
        "campaign_id": request["campaign_id"],
        "batch_id": request["batch_id"],
        "allocation_slots": len(allocation["slots"]),  # type: ignore[arg-type]
        "authorization_present": authorization_path().exists(),
        "live_authorized": False,
        "provider_calls": 0,
        "credential_reads": 0,
        "private_material": False,
        "execution_tree_hash": execution_tree_hash(repo, request),
    }


def pilot_live_guard(repo: Path) -> Mapping[str, object]:
    """Validate live authority before credentials or private state may be touched."""
    authorization = load_pilot_authorization(repo)
    identity = current_execution_identity(repo)
    if identity["remote_contains_head"] is not True:
        raise PermissionError("execution commit is not present on a remote branch")
    return {
        "status": "authorized",
        "authorization_id": authorization["authorization_id"],
        "execution_commit": identity["execution_commit"],
        "tree_hash": identity["tree_hash"],
        "next_stage": "public-exact-route-canaries",
    }
