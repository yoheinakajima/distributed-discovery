"""Authorized staged runtime for the fresh TreasureBench repair-confirmation pilot.

The runtime consumes only the generic Agent Operations owner authorization.
It is identity-separated from the quarantined pilot and fails closed before
credentials, private generation, calls, spend, unsealing, or publication when
any frozen surface changes.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import stat
import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from distributed_discovery.benchmark.agents_v1.actions import parse_action
from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    AgentAdapter,
    MockAdapter,
    ModelManifest,
)
from distributed_discovery.benchmark.agents_v1.contamination import classify_text
from distributed_discovery.benchmark.agents_v1.custody import domain_commitment
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v2 import (
    BATCH_ID,
    BRANCH,
    CALLS_PER_PROVIDER,
    CAMPAIGN_ID,
    ISSUE,
    MAX_CALLS,
    MAX_CALLS_PER_PROVIDER,
    MODELS,
    PROVIDER_CAPS,
    PROVIDERS,
    ROUTE_TOKEN_CAPS,
    TOTAL_CAP,
    execution_tree_hashes,
    generate_tasks,
    load_owner_authorization,
)
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v2_session import (
    LongSessionStopRequired,
)
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CostLedger,
    CredentialSet,
    PreflightAuthorization,
    load_credentials,
)
from distributed_discovery.benchmark.agents_v1.live_providers import (
    AnthropicMessagesAdapter,
    OpenAIResponsesAdapter,
    UrllibTransport,
)
from distributed_discovery.benchmark.agents_v1.models import (
    TaskInstance,
    canonical_json,
    sha256_hex,
)
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    ArchitectureRun,
    TurnRecord,
)
from distributed_discovery.benchmark.agents_v1.pilot import (
    AppendOnlyLedger,
    PilotBatchRunner,
    ResumablePilotAdapter,
    SealedObject,
    atomic_private_create,
    atomic_private_write,
    create_output_lock,
    load_or_create_real_custody_material,
    require_commitment,
    seal_object,
    unseal_answer_after_lock,
    unseal_object,
    validate_lock_inventory,
    validate_public_pilot_summary,
    verify_output_lock,
)
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.protocol_contract import (
    verify_protocol_contract,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import verify_method_agreement

PREFIX_INDICES = (0, 10, 20, 30, 40)
CALL_STAGES = frozenset({"public-canary", "private-prefix", "fixed-full-batch"})
CREDENTIAL_NAMES = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
CUSTODY_REPORT = Path(
    "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v2-custody-commitment.yml"
)
LOCK_REPORT = Path(
    "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v2-output-lock-commitment.yml"
)
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
PRESERVED_UNRELATED_UNTRACKED = frozenset(
    {
        "papers/information-sharing-frontier/paper-audit 2.json",
        "papers/information-sharing-frontier/visual-qa 2.md",
        "plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md",
        "reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md",
        "reports/roadmap-consolidation/post-v5-next-program-gate 2.yml",
    }
)


@dataclass(frozen=True)
class PreparedLiveStage:
    """Credential-free live-stage state validated before exact ingress."""

    authorization: Mapping[str, object]
    root: Path
    operational_key: bytes
    response_root: Path
    ledger: AppendOnlyLedger
    stage: str


class PreparedStageFailure(PermissionError):
    """A registered pre-ingress failure with enough state for quarantine."""

    def __init__(self, *, prepared: PreparedLiveStage, failure_class: str) -> None:
        self.prepared = prepared
        self.failure_class = failure_class
        super().__init__(failure_class)


def private_state_root() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "distributed-discovery" / "treasurebench-agents-v1" / "repair-confirmation-v2"


def _secure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink() or not path.is_dir():
        raise PermissionError("fresh private runtime directory is unsafe")
    path.chmod(0o700)


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    atomic_private_write(path, canonical_json(value) + b"\n")


def _create_json(path: Path, value: Mapping[str, object]) -> None:
    atomic_private_create(path, canonical_json(value) + b"\n")


def _read_json(path: Path) -> dict[str, object]:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise PermissionError("fresh private JSON state is unsafe")
    if stat.S_IMODE(info.st_mode) != 0o600:
        raise PermissionError("fresh private JSON state must have mode 0600")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("fresh private JSON state must be an object")
    return {str(name): item for name, item in value.items()}


def _load_or_create_key(path: Path) -> bytes:
    if path.exists():
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise PermissionError("fresh private operational key is unsafe")
        if stat.S_IMODE(info.st_mode) != 0o600:
            raise PermissionError("fresh private operational key must have mode 0600")
        value = path.read_bytes()
        if len(value) != 32:
            raise ValueError("fresh private operational key has invalid length")
        return value
    value = secrets.token_bytes(32)
    atomic_private_create(path, value)
    return value


def _sealed_record(sealed: SealedObject) -> Mapping[str, object]:
    return {"manifest": sealed.manifest(), "ciphertext_hex": sealed.ciphertext.hex()}


def _sealed_from_record(record: Mapping[str, object]) -> SealedObject:
    manifest = record.get("manifest")
    if not isinstance(manifest, Mapping):
        raise ValueError("fresh sealed-object manifest is missing")
    return SealedObject(
        domain=str(manifest["domain"]),
        nonce_hex=str(manifest["nonce_hex"]),
        ciphertext=bytes.fromhex(str(record["ciphertext_hex"])),
        ciphertext_sha256=str(manifest["ciphertext_sha256"]),
        associated_data_sha256=str(manifest["associated_data_sha256"]),
    )


def _load_or_create_sealed(path: Path, *, domain: str, value: object, key: bytes) -> SealedObject:
    if path.exists():
        sealed = _sealed_from_record(_read_json(path))
        if sealed.domain != domain:
            raise PermissionError("fresh sealed-object domain mismatch")
        if sealed.ciphertext_sha256 != f"sha256:{sha256_hex(sealed.ciphertext)}":
            raise PermissionError("fresh ciphertext mismatch requires quarantine")
        associated = canonical_json(
            {"campaign_id": CAMPAIGN_ID, "batch_id": BATCH_ID, "domain": domain}
        )
        if sealed.associated_data_sha256 != f"sha256:{sha256_hex(associated)}":
            raise PermissionError("fresh associated-data mismatch requires quarantine")
        if canonical_json(
            unseal_object(
                sealed,
                key=key,
                campaign_id=CAMPAIGN_ID,
                batch_id=BATCH_ID,
            )
        ) != canonical_json(value):
            raise PermissionError("fresh sealed-object plaintext mismatch requires quarantine")
        return sealed
    sealed = seal_object(
        domain=domain,
        value=value,
        key=key,
        nonce=secrets.token_bytes(12),
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    _create_json(path, _sealed_record(sealed))
    return sealed


class RouteCappedLedger(AppendOnlyLedger):
    """Apply the frozen per-route call and token ceilings as well as total caps."""

    def __init__(self, path: Path) -> None:
        super().__init__(
            path,
            providers=PROVIDERS,
            total_cap=TOTAL_CAP,
            provider_caps=PROVIDER_CAPS,
            max_calls=MAX_CALLS,
            max_input_tokens=sum(item["input"] for item in ROUTE_TOKEN_CAPS.values()),
            max_output_tokens=sum(item["output"] for item in ROUTE_TOKEN_CAPS.values()),
        )

    def _route_totals(self, provider: str) -> tuple[int, int, int]:
        records = [
            record
            for record in self.records
            if record.get("provider") == provider
            and (
                record.get("status") == "success"
                or (
                    record.get("event_type") == "provider-call"
                    and record.get("status") in {"error", "invalid"}
                )
            )
        ]
        return (
            len(records),
            sum(int(str(record.get("input_tokens", 0))) for record in records),
            sum(int(str(record.get("output_tokens", 0))) for record in records),
        )

    def guard_next(
        self,
        *,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: Decimal,
    ) -> None:
        super().guard_next(
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
        calls, route_input, route_output = self._route_totals(provider)
        if calls + 1 > MAX_CALLS_PER_PROVIDER:
            raise PermissionError("projected provider call cap exceeded")
        if route_input + input_tokens > ROUTE_TOKEN_CAPS[provider]["input"]:
            raise PermissionError("projected provider input-token cap exceeded")
        if route_output + output_tokens > ROUTE_TOKEN_CAPS[provider]["output"]:
            raise PermissionError("projected provider output-token cap exceeded")

    def append(self, event: Mapping[str, object]) -> Mapping[str, object]:
        if event.get("event_type") == "provider-call":
            self.guard_next(
                provider=str(event["provider"]),
                input_tokens=int(str(event.get("input_tokens", 0))),
                output_tokens=int(str(event.get("output_tokens", 0))),
                cost_usd=Decimal(str(event.get("cost_usd", "0"))),
            )
        return super().append(event)


def _fresh_ledger(path: Path) -> RouteCappedLedger:
    return RouteCappedLedger(path)


def _initialize_private_state(root: Path, *, repo: Path, synthetic: bool) -> Mapping[str, object]:
    resolved_repo = repo.resolve()
    resolved_root = root.resolve()
    if resolved_root == resolved_repo or resolved_repo in resolved_root.parents:
        raise PermissionError("fresh private state must remain outside the repository")
    _secure_directory(resolved_root)
    _secure_directory(resolved_root / "encrypted-traces")
    manifest: dict[str, object] = {
        "schema_version": "treasurebench-fresh-pilot-v2-private-state-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "classification": ("synthetic-offline-only" if synthetic else "real-authorized-private"),
        "symbolic_root": (
            "XDG_STATE_HOME/distributed-discovery/treasurebench-agents-v1/repair-confirmation-v2"
        ),
        "directory_mode": "0700",
        "file_mode": "0600",
        "symlinks_allowed": False,
        "atomic_writes": True,
        "retention_days": 365,
        "objects": list(PRIVATE_OBJECTS),
        "deletion_authorization_required": True,
    }
    schema = json.loads(
        (
            repo / "docs/benchmark/agents-v1/treasurebench-fresh-pilot-v2-private-state.schema.json"
        ).read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    if errors:
        raise ValueError(f"fresh private-state schema failed: {errors[0].message}")
    path = resolved_root / "manifest.json"
    if path.exists() and _read_json(path) != manifest:
        raise PermissionError("fresh private-state manifest mismatch requires quarantine")
    if not path.exists():
        _create_json(path, manifest)
    return manifest


def _load_state(path: Path) -> dict[str, object]:
    if path.exists():
        value = _read_json(path)
        if value.get("campaign_id") != CAMPAIGN_ID or value.get("batch_id") != BATCH_ID:
            raise PermissionError("fresh stage state belongs to another identity")
        return value
    return {
        "schema_version": "treasurebench-fresh-pilot-v2-stage-state-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "public_canary_complete": False,
        "custody_complete": False,
        "private_prefix_complete": False,
        "fixed_full_batch_complete": False,
        "quarantined": False,
    }


def _mark_state(path: Path, state: dict[str, object], field: str) -> None:
    state[field] = True
    _write_json(path, state)


def _append_access_once(
    ledger: AppendOnlyLedger, *, operation: str, private_material: bool
) -> None:
    if any(record.get("operation") == operation for record in ledger.records):
        return
    ledger.append(
        {
            "event_type": "custody-access",
            "status": "success",
            "operation": operation,
            "private_material": private_material,
        }
    )


def _execution_identity(repo: Path, authorization: Mapping[str, object]) -> Mapping[str, object]:
    execution_commit = str(authorization["commit"])
    remote = subprocess.run(
        ("git", "branch", "-r", "--contains", execution_commit),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not remote:
        raise PermissionError("fresh authorized execution commit is not present remotely")
    if execution_tree_hashes(repo) != authorization["tree_hashes"]:
        raise PermissionError("fresh execution-sensitive tree changed after authorization")
    return {
        "schema_version": "treasurebench-fresh-pilot-v2-execution-identity-v1",
        "authorization_digest": authorization["authorization_digest"],
        "gate_id": authorization["gate_id"],
        "execution_commit": execution_commit,
        "tree_hashes": authorization["tree_hashes"],
        "branch": BRANCH,
        "issue": ISSUE,
        "pull_request": authorization["pull_request"],
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "models": list(MODELS),
        "architectures": list(ARCHITECTURES),
        "tasks": 50,
        "repeats": 1,
    }


def _bind_private_state(
    repo: Path, root: Path, authorization: Mapping[str, object]
) -> Mapping[str, object]:
    identity = _execution_identity(repo, authorization)
    path = root / "execution-identity.json"
    if path.exists() and _read_json(path) != identity:
        raise PermissionError("fresh private state belongs to another authorization or identity")
    if not path.exists():
        _write_json(path, identity)
    return identity


def _preflight_authorization(
    authorization: Mapping[str, object],
) -> PreflightAuthorization:
    return PreflightAuthorization(
        authorization_id=str(authorization["authorization_digest"]),
        authorized_base_commit=str(authorization["commit"]),
        allowed_branch=BRANCH,
        expires_utc=datetime.fromisoformat(
            str(authorization["expires_at_utc"]).replace("Z", "+00:00")
        ),
        total_cap_usd=TOTAL_CAP,
        gateway_caps_usd={
            "openai_direct": PROVIDER_CAPS["OpenAI"],
            "anthropic_direct": PROVIDER_CAPS["Anthropic"],
        },
        route_caps_usd={
            "openai_direct": PROVIDER_CAPS["OpenAI"],
            "anthropic_direct": PROVIDER_CAPS["Anthropic"],
        },
        max_calls_per_route=MAX_CALLS_PER_PROVIDER,
        max_total_calls=MAX_CALLS,
        max_live_concurrency=2,
        private_tasks_allowed=True,
        scientific_evidence_allowed=False,
        raw=authorization,
    )


def _resumable(
    *,
    underlying: AgentAdapter,
    provider: str,
    model: str,
    ledger: AppendOnlyLedger,
    response_root: Path,
    response_key: bytes,
) -> AgentAdapter:
    return ResumablePilotAdapter(
        underlying,
        provider=provider,
        model=model,
        ledger=ledger,
        response_root=response_root,
        response_key=response_key,
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )


def _live_adapters(
    repo: Path,
    authorization: Mapping[str, object],
    ledger: AppendOnlyLedger,
    response_key: bytes,
    response_root: Path,
) -> tuple[dict[str, AgentAdapter], CredentialSet, tuple[object, ...]]:
    try:
        credentials = load_credentials(
            repo / ".env.txt",
            explicit_live_mode=True,
            requested_names=CREDENTIAL_NAMES,
        )
    except FileNotFoundError as error:
        raise PermissionError("repository-local credential file is missing") from error
    missing = [
        name
        for name in CREDENTIAL_NAMES
        if not credentials.configured.get(name) or not credentials.get_secret(name)
    ]
    if missing:
        credentials.clear()
        raise PermissionError(f"required opaque credential is not configured: {missing[0]}")
    openai: OpenAIResponsesAdapter | None = None
    anthropic: AnthropicMessagesAdapter | None = None
    try:
        openai_key = credentials.get_secret("OPENAI_API_KEY")
        anthropic_key = credentials.get_secret("ANTHROPIC_API_KEY")
        if not openai_key or not anthropic_key:
            raise PermissionError("both exact direct provider credentials are required")
        cost_ledger = CostLedger(_preflight_authorization(authorization))
        transport = UrllibTransport()
        openai = OpenAIResponsesAdapter(
            api_key=openai_key,
            transport=transport,
            network_enabled=True,
            ledger=cost_ledger,
        )
        anthropic = AnthropicMessagesAdapter(
            api_key=anthropic_key,
            transport=transport,
            network_enabled=True,
            ledger=cost_ledger,
        )
    except Exception:
        if openai is not None:
            openai.clear_secret()
        if anthropic is not None:
            anthropic.clear_secret()
        credentials.clear()
        raise
    assert openai is not None and anthropic is not None
    underlying = (openai, anthropic)
    adapters = {
        model: _resumable(
            underlying=underlying[index],
            provider=PROVIDERS[index],
            model=model,
            ledger=ledger,
            response_root=response_root / PROVIDERS[index].lower(),
            response_key=response_key,
        )
        for index, model in enumerate(MODELS)
    }
    return adapters, credentials, underlying


def _clear_stage_secrets(
    credentials: CredentialSet | None,
    adapters: tuple[object, ...],
) -> None:
    """Clear every exact selected value and provider-adapter secret."""

    for adapter in adapters:
        clear = getattr(adapter, "clear_secret", None)
        if callable(clear):
            clear()
    if credentials is not None:
        credentials.clear()


def _validate_call_stage_before_credential_ingress(
    stage: str,
    ledger: AppendOnlyLedger,
) -> None:
    """Reject invalid stage/ledger/cap state before opening repository credentials."""

    if stage not in CALL_STAGES:
        raise ValueError("credential ingress is allowed only for a provider-call stage")
    if any(record.get("event_type") == "provider-phase-closed" for record in ledger.records):
        raise PermissionError("provider phase is closed before credential ingress")
    totals = ledger.totals()
    if int(str(totals["calls"])) >= MAX_CALLS:
        raise PermissionError("projected total call cap exceeded before credential ingress")
    if Decimal(str(totals["cost_usd"])) >= TOTAL_CAP:
        raise PermissionError("projected total cost cap exceeded before credential ingress")
    provider_raw = cast(Mapping[str, object], totals["provider_usd"])
    for provider in PROVIDERS:
        provider_calls = sum(
            record.get("event_type") == "provider-call" and record.get("provider") == provider
            for record in ledger.records
        )
        if provider_calls >= MAX_CALLS_PER_PROVIDER:
            raise PermissionError(
                f"projected {provider} call cap exceeded before credential ingress"
            )
        if Decimal(str(provider_raw[provider])) >= PROVIDER_CAPS[provider]:
            raise PermissionError(
                f"projected {provider} cost cap exceeded before credential ingress"
            )


def _prepare_live_stage(repo: Path) -> PreparedLiveStage:
    """Validate authorization, identity, stage, ledger, and caps without credentials."""

    authorization = load_owner_authorization(repo)
    if not authorization.get("synthetic", False):
        status = subprocess.run(
            ("git", "status", "--porcelain"),
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        unexpected = [
            line
            for line in status
            if not (line.startswith("?? ") and line[3:].strip('"') in PRESERVED_UNRELATED_UNTRACKED)
        ]
        if unexpected:
            raise PermissionError("fresh live worktree is not clean")
    root = private_state_root()
    _secure_directory(root)
    _initialize_private_state(root, repo=repo, synthetic=False)
    _bind_private_state(repo, root, authorization)
    operational_key = _load_or_create_key(root / "operational-key.bin")
    response_root = root / "encrypted-provider-responses"
    _secure_directory(response_root)
    ledger = _fresh_ledger(root / "usage-cost-ledger.jsonl")
    state = _load_state(root / "provider-stage-state.json")
    stage = _next_stage(repo, root, state)
    prepared = PreparedLiveStage(
        authorization=authorization,
        root=root,
        operational_key=operational_key,
        response_root=response_root,
        ledger=ledger,
        stage=stage,
    )
    if stage in CALL_STAGES:
        try:
            _validate_call_stage_before_credential_ingress(stage, ledger)
        except PermissionError as error:
            raise PreparedStageFailure(
                prepared=prepared,
                failure_class="cap-guard-failure",
            ) from error
    return prepared


class _ReplayOnlyAdapter:
    def __init__(self, *, provider: str, model: str) -> None:
        self.manifest = ModelManifest(
            provider=provider,
            model_id=model,
            exact_snapshot=model,
            adapter_version="fresh-pilot-v2-replay-only-v1",
            moving_alias=False,
            live_capable=False,
        )

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        raise PermissionError("missing fresh replay response cannot trigger a provider call")


def _replay_adapters(
    ledger: AppendOnlyLedger, response_key: bytes, response_root: Path
) -> dict[str, AgentAdapter]:
    return {
        model: _resumable(
            underlying=_ReplayOnlyAdapter(provider=PROVIDERS[index], model=model),
            provider=PROVIDERS[index],
            model=model,
            ledger=ledger,
            response_root=response_root / PROVIDERS[index].lower(),
            response_key=response_key,
        )
        for index, model in enumerate(MODELS)
    }


def _mock_adapters(
    ledger: AppendOnlyLedger, response_key: bytes, response_root: Path
) -> tuple[dict[str, AgentAdapter], Mapping[str, MockAdapter]]:
    underlying = {model: MockAdapter() for model in MODELS}
    adapters = {
        model: _resumable(
            underlying=underlying[model],
            provider=PROVIDERS[index],
            model=model,
            ledger=ledger,
            response_root=response_root / PROVIDERS[index].lower(),
            response_key=response_key,
        )
        for index, model in enumerate(MODELS)
    }
    return adapters, underlying


def _seal_trace(root: Path, trace_id: str, value: object, key: bytes) -> None:
    sealed = seal_object(
        domain=f"fresh-raw-trace/{trace_id}",
        value=value,
        key=key,
        nonce=secrets.token_bytes(12),
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    path = root / "encrypted-traces" / f"{sha256_hex(trace_id.encode())}.sealed"
    _write_json(path, _sealed_record(sealed))


def _run_public_canary(
    *, root: Path, adapters: Mapping[str, AgentAdapter], key: bytes
) -> Mapping[str, object]:
    task = generate_public_calibration()[2]
    agent_id = sorted(task.capabilities)[0]
    for model, adapter in adapters.items():
        prompt = compile_prompt(
            task,
            agent_id,
            architecture_id="provider-native-smoke",
            final_required=True,
        )
        request = AdapterRequest(
            prompt=prompt,
            manifest=adapter.manifest,
            round_number=0,
            action_vocabulary=task.action_vocabulary,
            source_vocabulary=task.source_vocabulary,
            final_required=True,
        )
        response = adapter.respond(request)
        errors: list[str] = []
        action = None
        retry_count = 0
        if response.error_class is None:
            try:
                action = parse_action(
                    response.raw_output,
                    task_commitment=task.commitment,
                    agent_id=agent_id,
                    round_number=0,
                    action_vocabulary=task.action_vocabulary,
                    source_vocabulary=task.source_vocabulary,
                    final_required=True,
                )
            except ValueError as exc:
                retry_count = 1
                first_error = str(exc)
                response = adapter.respond(
                    replace(request, schema_retry=True, repair_errors=(first_error,))
                )
                if response.error_class is None:
                    try:
                        action = parse_action(
                            response.raw_output,
                            task_commitment=task.commitment,
                            agent_id=agent_id,
                            round_number=0,
                            action_vocabulary=task.action_vocabulary,
                            source_vocabulary=task.source_vocabulary,
                            final_required=True,
                        )
                    except ValueError as retry_exc:
                        errors.extend((first_error, str(retry_exc)))
        if response.error_class is not None:
            errors.append(response.error_class)
        if response.usage.input_tokens + response.usage.output_tokens <= 0:
            errors.append("missing-usage")
        if classify_text(response.raw_output).classification in {
            "direct-leakage",
            "probable-memorization",
        }:
            errors.append("contamination")
        run = ArchitectureRun(
            architecture_id="provider-native-smoke",
            task_commitment=task.commitment,
            turns=(
                TurnRecord(
                    "provider-native-smoke",
                    agent_id,
                    0,
                    (),
                    response,
                    action,
                    tuple(errors),
                    retry_count,
                ),
            ),
            final_actions=((action,) if action is not None else ()),
            protocol_errors=tuple(errors),
        )
        trace = build_trace(run)
        if trace.audit["hidden_reasoning_stored"] is not False:
            errors.append("hidden-reasoning-boundary")
        errors.extend(verify_protocol_contract(task, run).errors)
        errors.extend(verify_method_agreement(asdict(evaluate_run(task, run)), task, run))
        if errors:
            raise RuntimeError("fresh public exact-route canary failed")
        _seal_trace(root, f"public-canary/{model}", trace.raw, key)
    return {"status": "pass", "routes": len(adapters), "requests_per_route": 1}


def _custody(
    repo: Path,
    root: Path,
    authorization: Mapping[str, object],
    *,
    synthetic: bool,
) -> tuple[
    tuple[TaskInstance, ...],
    Mapping[str, bytes],
    SealedObject,
    SealedObject,
    Mapping[str, object],
]:
    material = (
        {
            "seed": hashlib.sha256(b"fresh-live-v2-synthetic-seed").digest(),
            "task_key": hashlib.sha256(b"fresh-live-v2-synthetic-task-key").digest(),
            "answer_key": hashlib.sha256(b"fresh-live-v2-synthetic-answer-key").digest(),
        }
        if synthetic
        else load_or_create_real_custody_material(root)
    )
    tasks = generate_tasks(
        repo,
        material=(
            f"fresh-live-v2-synthetic/{material['seed'].hex()}"
            if synthetic
            else f"fresh-private-v2/{material['seed'].hex()}"
        ),
        public_fixture=synthetic,
        authorization=None if synthetic else authorization,
    )
    task_payload = [task.visible_record() for task in tasks]
    answer_payload = [task.evaluator_record() for task in tasks]
    task_sealed = _load_or_create_sealed(
        root / "task-custody.json",
        domain="fresh-real-v2-private-task-batch",
        value=task_payload,
        key=material["task_key"],
    )
    answer_sealed = _load_or_create_sealed(
        root / "answer-custody.json",
        domain="fresh-real-v2-private-answer-key",
        value=answer_payload,
        key=material["answer_key"],
    )
    manifest: Mapping[str, object] = {
        "schema_version": "treasurebench-fresh-pilot-v2-custody-manifest-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "seed_commitment": domain_commitment(
            "treasurebench-agents-v1/fresh-pilot-v2-seed", material["seed"].hex()
        ),
        "task_plaintext_commitment": domain_commitment(
            "treasurebench-agents-v1/fresh-v2-task-batch", task_payload
        ),
        "answer_plaintext_commitment": domain_commitment(
            "treasurebench-agents-v1/fresh-v2-answer-key", answer_payload
        ),
        "task_ciphertext_commitment": task_sealed.ciphertext_sha256,
        "answer_ciphertext_commitment": answer_sealed.ciphertext_sha256,
        "tasks": len(tasks),
    }
    path = root / "custody-manifest.json"
    if path.exists() and _read_json(path) != manifest:
        raise PermissionError("fresh custody manifest mismatch requires quarantine")
    if not path.exists():
        _create_json(path, manifest)
    return tuple(tasks), material, task_sealed, answer_sealed, manifest


def _output_objects(root: Path, ledger: AppendOnlyLedger) -> dict[str, bytes]:
    objects = {
        "task-ciphertext": (root / "task-custody.json").read_bytes(),
        "answer-ciphertext": (root / "answer-custody.json").read_bytes(),
        "custody-manifest": (root / "custody-manifest.json").read_bytes(),
        "execution-identity": (root / "execution-identity.json").read_bytes(),
        "access-log": (root / "access-log.jsonl").read_bytes(),
        "usage-cost-ledger": ledger.path.read_bytes(),
        "provider-stage-state": (root / "provider-stage-state.json").read_bytes(),
    }
    for path in sorted((root / "encrypted-traces").glob("*.sealed")):
        objects[f"trace/{path.name}"] = path.read_bytes()
    response_root = root / "encrypted-provider-responses"
    for path in sorted(response_root.rglob("*.sealed.json")):
        objects[f"provider-response/{path.relative_to(response_root)}"] = path.read_bytes()
    validate_lock_inventory(objects)
    return objects


def _public_totals(ledger: AppendOnlyLedger) -> Mapping[str, object]:
    totals = ledger.totals()
    provider_raw = cast(Mapping[str, object], totals["provider_usd"])
    return {
        "calls": totals["calls"],
        "input_tokens": totals["input_tokens"],
        "output_tokens": totals["output_tokens"],
        "cost_usd": str(totals["cost_usd"]),
        "provider_cost_usd": {provider: str(provider_raw[provider]) for provider in PROVIDERS},
    }


def _provider_attempt_outcomes(
    ledger: AppendOnlyLedger,
) -> tuple[dict[str, int], dict[str, int]]:
    grouped: dict[str, list[Mapping[str, object]]] = {}
    for record in ledger.records:
        if record.get("event_type") != "provider-call":
            continue
        grouped.setdefault(str(record["call_key"]), []).append(record)
    terminal = {provider: 0 for provider in PROVIDERS}
    recovered = {provider: 0 for provider in PROVIDERS}
    for records in grouped.values():
        ordered = sorted(records, key=lambda record: int(str(record["sequence"])))
        provider = str(ordered[-1]["provider"])
        if ordered[-1].get("status") != "success":
            terminal[provider] += 1
        elif any(record.get("status") != "success" for record in ordered[:-1]):
            recovered[provider] += 1
    return terminal, recovered


def _validate_acceptance(
    *,
    counters: Mapping[str, int],
    flags: Mapping[str, bool],
) -> None:
    nonzero = {name: value for name, value in counters.items() if value != 0}
    false_flags = {name for name, value in flags.items() if not value}
    if nonzero or false_flags:
        raise RuntimeError("fresh v2 prospective acceptance failed; quarantine entire batch")


def _require_public_record(repo: Path, relative: Path, expected: Mapping[str, object]) -> None:
    path = repo / relative
    if not path.is_file() or path.is_symlink():
        raise PermissionError(f"{relative.name} must be published before the next stage")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    mismatch = isinstance(value, Mapping) and any(
        value.get(key) != item for key, item in expected.items()
    )
    if not isinstance(value, Mapping) or mismatch:
        raise PermissionError(f"{relative.name} does not match fresh private commitments")
    if subprocess.run(
        ("git", "status", "--porcelain", "--", str(relative)),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip():
        raise PermissionError(f"{relative.name} must be committed before the next stage")
    head = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not subprocess.run(
        ("git", "branch", "-r", "--contains", head),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip():
        raise PermissionError("fresh public commitment commit must be pushed")


def _next_stage(repo: Path, root: Path, state: Mapping[str, object]) -> str:
    if not state["public_canary_complete"]:
        return "public-canary"
    if not state["custody_complete"]:
        return "custody"
    custody = _read_json(root / "custody-manifest.json")
    if not state["private_prefix_complete"]:
        _require_public_record(
            repo,
            CUSTODY_REPORT,
            {
                "campaign_id": CAMPAIGN_ID,
                "batch_id": BATCH_ID,
                "seed_commitment": custody["seed_commitment"],
                "task_ciphertext_commitment": custody["task_ciphertext_commitment"],
                "answer_ciphertext_commitment": custody["answer_ciphertext_commitment"],
            },
        )
        return "private-prefix"
    if not state["fixed_full_batch_complete"]:
        return "fixed-full-batch"
    lock_path = root / "output-lock.json"
    if not lock_path.exists():
        return "output-lock"
    lock = _read_json(lock_path)
    _require_public_record(
        repo,
        LOCK_REPORT,
        {
            "campaign_id": CAMPAIGN_ID,
            "batch_id": BATCH_ID,
            "output_lock_commitment": lock["lock_hash"],
        },
    )
    return "verify"


def _runner(root: Path, ledger: AppendOnlyLedger, operational_key: bytes) -> PilotBatchRunner:
    return PilotBatchRunner(
        state_root=root,
        ledger=ledger,
        trace_key=operational_key,
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
        reject_protocol_errors=True,
    )


def _execute_stage(
    repo: Path,
    *,
    authorization: Mapping[str, object],
    root: Path,
    stage: str,
    adapters: Mapping[str, AgentAdapter] | None,
    operational_key: bytes,
    ledger: AppendOnlyLedger,
) -> Mapping[str, object]:
    synthetic = bool(authorization.get("synthetic", False))
    _initialize_private_state(root, repo=repo, synthetic=synthetic)
    identity = _bind_private_state(repo, root, authorization)
    access = _fresh_ledger(root / "access-log.jsonl")
    state_path = root / "provider-stage-state.json"
    state = _load_state(state_path)
    runner = _runner(root, ledger, operational_key)

    if stage == "public-canary":
        if state["public_canary_complete"]:
            return {"stage": stage, "status": "already-complete"}
        if adapters is None:
            raise RuntimeError("fresh canary adapters are required")
        result = _run_public_canary(root=root, adapters=adapters, key=operational_key)
        _append_access_once(
            access, operation="fresh-public-exact-route-canary-pass", private_material=False
        )
        _mark_state(state_path, state, "public_canary_complete")
        return {**result, "stage": stage, "private_material_created": False}

    if not state["public_canary_complete"]:
        raise PermissionError("fresh public canary must pass before private generation")
    tasks, material, task_sealed, answer_sealed, custody = _custody(
        repo, root, authorization, synthetic=synthetic
    )
    if stage == "custody":
        _append_access_once(
            access, operation="fresh-private-custody-created", private_material=True
        )
        if not state["custody_complete"]:
            _mark_state(state_path, state, "custody_complete")
        return {
            "stage": stage,
            "status": "pass",
            "tasks": len(tasks),
            "seed_commitment": custody["seed_commitment"],
            "task_ciphertext_commitment": task_sealed.ciphertext_sha256,
            "answer_ciphertext_commitment": answer_sealed.ciphertext_sha256,
            "access_log_commitment": f"sha256:{sha256_hex(access.path.read_bytes())}",
        }
    if not state["custody_complete"]:
        raise PermissionError("fresh custody must be committed before private calls")

    prefix = tuple(tasks[index] for index in PREFIX_INDICES)
    if stage == "private-prefix":
        if state["private_prefix_complete"]:
            return {"stage": stage, "status": "already-complete"}
        if adapters is None:
            raise RuntimeError("fresh prefix adapters are required")
        result = runner.run_stage(
            stage=stage, tasks=prefix, adapters=adapters, verify_metrics=False
        )
        if result["runs"] != len(prefix) * len(ARCHITECTURES) * len(MODELS):
            raise RuntimeError("fresh prefix pairing is incomplete")
        _append_access_once(
            access, operation="fresh-private-ten-percent-prefix-pass", private_material=True
        )
        _mark_state(state_path, state, "private_prefix_complete")
        return {"status": "pass", **result, "usage": dict(_public_totals(ledger))}
    if not state["private_prefix_complete"]:
        raise PermissionError("fresh prefix must pass before full execution")

    remaining = tuple(task for index, task in enumerate(tasks) if index not in PREFIX_INDICES)
    if stage == "fixed-full-batch":
        if state["fixed_full_batch_complete"]:
            return {"stage": stage, "status": "already-complete"}
        if adapters is None:
            raise RuntimeError("fresh full-batch adapters are required")
        result = runner.run_stage(
            stage=stage, tasks=remaining, adapters=adapters, verify_metrics=False
        )
        if result["runs"] != len(remaining) * len(ARCHITECTURES) * len(MODELS):
            raise RuntimeError("fresh full-batch pairing is incomplete")
        _append_access_once(
            access, operation="fresh-fixed-full-batch-complete", private_material=True
        )
        _mark_state(state_path, state, "fixed_full_batch_complete")
        return {"status": "pass", **result, "usage": dict(_public_totals(ledger))}
    if not state["fixed_full_batch_complete"]:
        raise PermissionError("fresh full batch must finish before output lock")

    if stage == "output-lock":
        if not any(
            record.get("event_type") == "provider-phase-closed" for record in ledger.records
        ):
            ledger.close_provider_phase()
            _append_access_once(
                access,
                operation="fresh-provider-outputs-locked-before-unseal",
                private_material=True,
            )
        objects = _output_objects(root, ledger)
        lock_path = root / "output-lock.json"
        if lock_path.exists():
            lock = _read_json(lock_path)
            verify_output_lock(lock, objects, ledger=ledger)
        else:
            lock = dict(
                create_output_lock(
                    objects,
                    ledger=ledger,
                    campaign_id=CAMPAIGN_ID,
                    batch_id=BATCH_ID,
                )
            )
            _write_json(lock_path, lock)
        return {
            "stage": stage,
            "status": "pass",
            "output_lock_commitment": lock["lock_hash"],
            "objects_locked": len(objects),
            "provider_phase_closed": True,
            "unsealed": False,
        }
    if stage != "verify":
        raise ValueError(f"unknown fresh live stage: {stage}")

    objects = _output_objects(root, ledger)
    lock = _read_json(root / "output-lock.json")
    verify_output_lock(lock, objects, ledger=ledger)
    unsealed_tasks = unseal_object(
        task_sealed,
        key=material["task_key"],
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    unsealed_answers = unseal_answer_after_lock(
        answer_sealed,
        key=material["answer_key"],
        lock=lock,
        objects=objects,
        ledger=ledger,
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    require_commitment(
        str(custody["task_plaintext_commitment"]),
        domain_commitment("treasurebench-agents-v1/fresh-v2-task-batch", unsealed_tasks),
        domain="fresh-v2-task-batch",
    )
    require_commitment(
        str(custody["answer_plaintext_commitment"]),
        domain_commitment("treasurebench-agents-v1/fresh-v2-answer-key", unsealed_answers),
        domain="fresh-v2-answer-key",
    )
    if adapters is None:
        raise RuntimeError("fresh replay adapters are required")
    prefix_verification = runner.run_stage(
        stage="private-prefix",
        tasks=prefix,
        adapters=adapters,
        verify_metrics=True,
        persist_traces=False,
    )
    full_verification = runner.run_stage(
        stage="fixed-full-batch",
        tasks=remaining,
        adapters=adapters,
        verify_metrics=True,
        persist_traces=False,
    )
    method_disagreements = int(str(prefix_verification["method_disagreements"])) + int(
        str(full_verification["method_disagreements"])
    )
    contamination_findings = int(str(prefix_verification["contamination_findings"])) + int(
        str(full_verification["contamination_findings"])
    )
    protocol_errors = int(str(prefix_verification["protocol_errors"])) + int(
        str(full_verification["protocol_errors"])
    )
    invalid_final_cardinalities = int(
        str(prefix_verification["invalid_final_cardinalities"])
    ) + int(str(full_verification["invalid_final_cardinalities"]))
    metric_range_errors = int(str(prefix_verification["metric_range_errors"])) + int(
        str(full_verification["metric_range_errors"])
    )
    incomplete_pairings = int(str(prefix_verification["incomplete_pairings"])) + int(
        str(full_verification["incomplete_pairings"])
    )
    terminal_provider_errors, recovered_transport_warnings = _provider_attempt_outcomes(ledger)
    provider_call_counts = {
        provider: sum(
            record.get("event_type") == "provider-call" and record.get("provider") == provider
            for record in ledger.records
        )
        for provider in PROVIDERS
    }
    totals = _public_totals(ledger)
    if int(str(totals["calls"])) > MAX_CALLS:
        raise PermissionError("fresh call cap exceeded")
    if Decimal(str(totals["cost_usd"])) > TOTAL_CAP:
        raise PermissionError("fresh cumulative cost cap exceeded")
    provider_costs = cast(Mapping[str, object], totals["provider_cost_usd"])
    if any(
        Decimal(str(provider_costs[provider])) > PROVIDER_CAPS[provider] for provider in PROVIDERS
    ):
        raise PermissionError("fresh provider cost cap exceeded")
    if any(provider_call_counts[provider] < CALLS_PER_PROVIDER for provider in PROVIDERS):
        raise RuntimeError("fresh provider call graph is incomplete")
    provider_cost_total = sum(
        (Decimal(str(provider_costs[provider])) for provider in PROVIDERS),
        Decimal("0"),
    )
    exact_cost_reconciliation = provider_cost_total == Decimal(str(totals["cost_usd"]))
    private_manifest = _read_json(root / "manifest.json")
    private_state_verified = (
        private_manifest["campaign_id"] == CAMPAIGN_ID
        and private_manifest["batch_id"] == BATCH_ID
        and private_manifest["classification"]
        in {"synthetic-offline-only", "real-authorized-private"}
    )
    _validate_acceptance(
        counters={
            "terminal_provider_failures": sum(terminal_provider_errors.values()),
            "protocol_invalid_runs": protocol_errors,
            "invalid_final_action_cardinalities": invalid_final_cardinalities,
            "incomplete_pairings": incomplete_pairings,
            "method_a_b_disagreements": method_disagreements,
            "method_c_failures": protocol_errors,
            "contamination_findings": contamination_findings,
            "metric_range_errors": metric_range_errors,
        },
        flags={
            "exact_cost_reconciliation": exact_cost_reconciliation,
            "private_state_verified": private_state_verified,
            "provider_phase_closed": True,
            "output_lock_verified": True,
            "unseal_after_lock_verified": True,
        },
    )
    summary: dict[str, object] = {
        "schema_version": "treasurebench-fresh-pilot-v2-redacted-summary-v1",
        "status": "pass",
        "decision": "repair-confirmed-engineering-only-no-further-authority",
        "classification": "redacted-engineering-only-no-task-level-performance",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "authorization_digest": authorization["authorization_digest"],
        "execution_commit": identity["execution_commit"],
        "tasks": len(tasks),
        "families": 5,
        "architectures": len(ARCHITECTURES),
        "models": list(MODELS),
        "private_runs": len(tasks) * len(ARCHITECTURES) * len(MODELS),
        "prefix_tasks": len(prefix),
        "output_lock_hash": lock["lock_hash"],
        "seed_commitment": custody["seed_commitment"],
        "task_ciphertext_commitment": task_sealed.ciphertext_sha256,
        "answer_ciphertext_commitment": answer_sealed.ciphertext_sha256,
        "method_a_b_disagreements": method_disagreements,
        "method_c_failures": protocol_errors,
        "contamination_findings": contamination_findings,
        "protocol_errors": protocol_errors,
        "invalid_final_action_cardinalities": invalid_final_cardinalities,
        "metric_range_errors": metric_range_errors,
        "incomplete_pairings": incomplete_pairings,
        "terminal_provider_error_counts": terminal_provider_errors,
        "recovered_transport_warning_counts": recovered_transport_warnings,
        "provider_call_counts": provider_call_counts,
        "usage": dict(totals),
        "exact_cost_reconciliation": exact_cost_reconciliation,
        "retention_days": 365,
        "private_state_verified": private_state_verified,
        "provider_phase_closed": True,
        "output_lock_verified": True,
        "unseal_after_lock_verified": True,
        "redaction_status": "pass",
        "task_text_disclosed": False,
        "answer_disclosed": False,
        "task_level_performance_disclosed": False,
        "ranking_created": False,
        "composite_created": False,
        "base_campaign_authorized": False,
        "claim_created": False,
        "study_created": False,
        "scientific_run_created": False,
        "paper_result_created": False,
        "release_created": False,
    }
    validate_public_pilot_summary(summary)
    audit_sealed = seal_object(
        domain="fresh-v2-final-private-audit-package",
        value={
            "summary": summary,
            "prefix_verification": prefix_verification,
            "full_verification": full_verification,
        },
        key=material["answer_key"],
        nonce=secrets.token_bytes(12),
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    _write_json(root / "final-audit-package.sealed.json", _sealed_record(audit_sealed))
    _write_json(root / "redacted-summary.json", summary)
    return summary


def _run_prepared_live_stage(
    repo: Path,
    prepared: PreparedLiveStage,
) -> Mapping[str, object]:
    """Run one prepared stage and clear its exact credential subset on every exit."""

    credentials: CredentialSet | None = None
    live_underlying: tuple[object, ...] = ()
    if prepared.stage in CALL_STAGES:
        adapters, credentials, live_underlying = _live_adapters(
            repo,
            prepared.authorization,
            prepared.ledger,
            prepared.operational_key,
            prepared.response_root,
        )
    elif prepared.stage == "verify":
        adapters = _replay_adapters(
            prepared.ledger,
            prepared.operational_key,
            prepared.response_root,
        )
    else:
        adapters = None
    try:
        return _execute_stage(
            repo,
            authorization=prepared.authorization,
            root=prepared.root,
            stage=prepared.stage,
            adapters=adapters,
            operational_key=prepared.operational_key,
            ledger=prepared.ledger,
        )
    finally:
        _clear_stage_secrets(credentials, live_underlying)


def _public_commitment_record(
    prepared: PreparedLiveStage,
    result: Mapping[str, object],
) -> tuple[Path, dict[str, object], str]:
    """Build the deterministic public-safe record for a custody or lock boundary."""

    common: dict[str, object] = {
        "task_id": "AO-0006",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "execution_commit": prepared.authorization["commit"],
        "authorization_digest": prepared.authorization["authorization_digest"],
        "classification": "public-safe-engineering-only-no-task-content",
        "task_text_disclosed": False,
        "answer_disclosed": False,
        "raw_output_disclosed": False,
        "ranking_created": False,
        "scientific_evidence_created": False,
    }
    if result.get("status") == "quarantined":
        return (
            LOCK_REPORT,
            {
                "schema_version": "treasurebench-fresh-pilot-v2-output-lock-commitment-v1",
                "status": "quarantined-output-lock-committed",
                **common,
                "output_lock_commitment": result["output_lock_commitment"],
                "objects_locked": result["objects_locked"],
                "provider_phase_closed": True,
                "unsealed_before_lock": False,
                "quarantined": True,
            },
            "Record AO-0006 v2 quarantine output lock",
        )
    if prepared.stage == "custody":
        return (
            CUSTODY_REPORT,
            {
                "schema_version": "treasurebench-fresh-pilot-v2-custody-commitment-v1",
                "status": "committed-before-private-provider-execution",
                **common,
                "seed_commitment": result["seed_commitment"],
                "task_ciphertext_commitment": result["task_ciphertext_commitment"],
                "answer_ciphertext_commitment": result["answer_ciphertext_commitment"],
                "access_log_commitment": result["access_log_commitment"],
                "tasks": result["tasks"],
            },
            "Record AO-0006 v2 custody commitment",
        )
    if prepared.stage == "output-lock":
        return (
            LOCK_REPORT,
            {
                "schema_version": "treasurebench-fresh-pilot-v2-output-lock-commitment-v1",
                "status": ("output-lock-committed-before-unseal"),
                **common,
                "output_lock_commitment": result["output_lock_commitment"],
                "objects_locked": result["objects_locked"],
                "provider_phase_closed": True,
                "unsealed_before_lock": False,
                "quarantined": False,
            },
            "Record AO-0006 v2 output lock",
        )
    raise ValueError("public commitment is not defined for this live stage")


def _publish_public_commitment(
    repo: Path,
    prepared: PreparedLiveStage,
    result: Mapping[str, object],
) -> Mapping[str, object]:
    """Write, commit, push, and revalidate one public-safe boundary record."""

    relative, record, message = _public_commitment_record(prepared, result)
    path = repo / relative
    if path.exists():
        existing = yaml.safe_load(path.read_text(encoding="utf-8"))
        if existing != record:
            raise PermissionError(f"{relative.name} conflicts with the frozen commitment")
    else:
        path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    subprocess.run(("git", "add", "--", str(relative)), cwd=repo, check=True)
    staged = subprocess.run(
        ("git", "diff", "--cached", "--quiet", "--", str(relative)),
        cwd=repo,
        check=False,
    )
    if staged.returncode == 1:
        subprocess.run(("git", "commit", "-m", message, "--", str(relative)), cwd=repo, check=True)
    elif staged.returncode != 0:
        raise PermissionError("public commitment staging could not be verified")
    subprocess.run(("git", "push", "origin", BRANCH), cwd=repo, check=True)
    expected = (
        {
            "campaign_id": CAMPAIGN_ID,
            "batch_id": BATCH_ID,
            "seed_commitment": result["seed_commitment"],
            "task_ciphertext_commitment": result["task_ciphertext_commitment"],
            "answer_ciphertext_commitment": result["answer_ciphertext_commitment"],
        }
        if prepared.stage == "custody" and result.get("status") != "quarantined"
        else {
            "campaign_id": CAMPAIGN_ID,
            "batch_id": BATCH_ID,
            "output_lock_commitment": result["output_lock_commitment"],
        }
    )
    _require_public_record(repo, relative, expected)
    return record


def _safe_existing_objects(root: Path, ledger: AppendOnlyLedger) -> dict[str, bytes]:
    """Collect every existing safely lockable object without requiring a full batch."""

    objects: dict[str, bytes] = {}
    fixed = {
        "task-ciphertext": root / "task-custody.json",
        "answer-ciphertext": root / "answer-custody.json",
        "custody-manifest": root / "custody-manifest.json",
        "execution-identity": root / "execution-identity.json",
        "access-log": root / "access-log.jsonl",
        "usage-cost-ledger": ledger.path,
        "provider-stage-state": root / "provider-stage-state.json",
    }
    for name, path in fixed.items():
        if not path.exists():
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise LongSessionStopRequired(f"unsafe retained object cannot be locked: {name}")
        objects[name] = path.read_bytes()
    for prefix, path_root, pattern in (
        ("trace", root / "encrypted-traces", "*.sealed"),
        ("provider-response", root / "encrypted-provider-responses", "*.sealed.json"),
    ):
        if not path_root.exists():
            continue
        for path in sorted(path_root.rglob(pattern)):
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
                raise LongSessionStopRequired("unsafe retained encrypted object")
            objects[f"{prefix}/{path.relative_to(path_root)}"] = path.read_bytes()
    if not objects:
        raise LongSessionStopRequired("no retained object is safely lockable")
    return objects


def _quarantine_live_failure(
    prepared: PreparedLiveStage,
    *,
    failure_class: str,
) -> Mapping[str, object]:
    """Close and lock an honest batch failure without another provider call."""

    root = prepared.root
    ledger = prepared.ledger
    lock_path = root / "output-lock.json"
    if lock_path.exists():
        objects = _safe_existing_objects(root, ledger)
        lock = _read_json(lock_path)
        try:
            verify_output_lock(lock, objects, ledger=ledger)
        except (PermissionError, ValueError) as error:
            raise LongSessionStopRequired(
                "retained private state cannot be safely verified or locked"
            ) from error
    else:
        state_path = root / "provider-stage-state.json"
        state = _load_state(state_path)
        state["quarantined"] = True
        state["quarantine_stage"] = prepared.stage
        state["quarantine_failure_class"] = failure_class
        _write_json(state_path, state)
        if not any(
            record.get("event_type") == "provider-phase-closed" for record in ledger.records
        ):
            ledger.append(
                {
                    "event_type": "batch-quarantine",
                    "status": "quarantined",
                    "stage": prepared.stage,
                    "failure_class": failure_class,
                }
            )
            ledger.close_provider_phase()
        objects = _safe_existing_objects(root, ledger)
        lock = dict(
            create_output_lock(
                objects,
                ledger=ledger,
                campaign_id=CAMPAIGN_ID,
                batch_id=BATCH_ID,
            )
        )
        _write_json(lock_path, lock)
        verify_output_lock(lock, objects, ledger=ledger)
    totals = _public_totals(ledger)
    custody_status = (
        "preserved"
        if all((root / name).exists() for name in ("task-custody.json", "answer-custody.json"))
        else "not-created"
    )
    summary: dict[str, object] = {
        "schema_version": "treasurebench-fresh-pilot-v2-quarantine-closeout-v1",
        "status": "quarantined",
        "decision": "fresh-pilot-v2-quarantined-engineering-only",
        "classification": "redacted-engineering-only-no-task-level-performance",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "stage": prepared.stage,
        "failure_class": failure_class,
        "calls": totals["calls"],
        "input_tokens": totals["input_tokens"],
        "output_tokens": totals["output_tokens"],
        "cost_usd": totals["cost_usd"],
        "provider_cost_usd": totals["provider_cost_usd"],
        "custody_status": custody_status,
        "provider_phase_closed": True,
        "output_lock_status": "pass",
        "output_lock_commitment": lock["lock_hash"],
        "objects_locked": len(objects),
        "minimum_unseal_performed": prepared.stage == "verify",
        "task_text_disclosed": False,
        "answer_disclosed": False,
        "raw_output_disclosed": False,
        "ranking_created": False,
        "performance_comparison_created": False,
        "scientific_evidence_created": False,
        "replacement_or_splice_performed": False,
        "further_provider_calls_permitted": False,
    }
    _write_json(root / "redacted-summary.json", summary)
    return summary


def _registered_failure_class(stage: str) -> str:
    return {
        "public-canary": "public-canary-failure",
        "custody": "custody-creation-failure",
        "private-prefix": "private-prefix-failure",
        "fixed-full-batch": "fixed-full-batch-failure",
        "output-lock": "output-lock-failure",
        "verify": "verification-or-acceptance-failure",
    }.get(stage, "registered-batch-failure")


def run_live_fresh_pilot(repo: Path) -> Mapping[str, object]:
    """Run the authorized staged campaign through success or honest quarantine."""

    while True:
        try:
            prepared = _prepare_live_stage(repo)
        except PreparedStageFailure as error:
            result = _quarantine_live_failure(
                error.prepared,
                failure_class=error.failure_class,
            )
            try:
                _publish_public_commitment(repo, error.prepared, result)
            except Exception as publish_error:
                raise LongSessionStopRequired(
                    "quarantine output-lock commitment could not be published"
                ) from publish_error
            return result
        try:
            result = _run_prepared_live_stage(repo, prepared)
        except LongSessionStopRequired:
            raise
        except Exception as error:
            if prepared.stage == "output-lock":
                raise LongSessionStopRequired(
                    "retained private state could not be safely output-locked"
                ) from error
            result = _quarantine_live_failure(
                prepared,
                failure_class=_registered_failure_class(prepared.stage),
            )
            try:
                _publish_public_commitment(repo, prepared, result)
            except Exception as publish_error:
                raise LongSessionStopRequired(
                    "quarantine output-lock commitment could not be published"
                ) from publish_error
            return result
        if prepared.stage in {"custody", "output-lock"}:
            try:
                _publish_public_commitment(repo, prepared, result)
            except Exception:
                quarantine = _quarantine_live_failure(
                    prepared,
                    failure_class="commitment-verification-failure",
                )
                try:
                    _publish_public_commitment(repo, prepared, quarantine)
                except Exception as quarantine_publish_error:
                    raise LongSessionStopRequired(
                        "quarantine output-lock commitment could not be published"
                    ) from quarantine_publish_error
                return quarantine
        if prepared.stage == "verify":
            return result


def run_mock_fresh_pilot(
    repo: Path, *, authorization: Mapping[str, object], root: Path
) -> tuple[Mapping[str, object], Mapping[str, MockAdapter]]:
    """Exercise every fresh staged transition with deterministic mock adapters."""
    _secure_directory(root)
    _initialize_private_state(root, repo=repo, synthetic=True)
    _bind_private_state(repo, root, authorization)
    operational_key = _load_or_create_key(root / "operational-key.bin")
    response_root = root / "encrypted-provider-responses"
    _secure_directory(response_root)
    ledger = _fresh_ledger(root / "usage-cost-ledger.jsonl")
    adapters, underlying = _mock_adapters(ledger, operational_key, response_root)
    result: Mapping[str, object] = {}
    for stage in (
        "public-canary",
        "custody",
        "private-prefix",
        "fixed-full-batch",
        "output-lock",
        "verify",
    ):
        stage_adapters = adapters if stage in CALL_STAGES or stage == "verify" else None
        result = _execute_stage(
            repo,
            authorization=authorization,
            root=root,
            stage=stage,
            adapters=stage_adapters,
            operational_key=operational_key,
            ledger=ledger,
        )
    return result, underlying


def audit_live_corruptions(repo: Path) -> tuple[dict[str, str], ...]:
    """Reject v2 private-state, output-lock, and terminal-provider corruptions."""

    outcomes: list[dict[str, str]] = []

    def reject(name: str, action: object) -> None:
        try:
            assert callable(action)
            action()
        except (OSError, PermissionError, RuntimeError, ValueError):
            outcomes.append({"corruption_id": name, "status": "rejected"})
            return
        outcomes.append({"corruption_id": name, "status": "accepted"})

    reject(
        "PRIVATE-STATE-01-inside-repository",
        lambda: _initialize_private_state(
            repo / "forbidden-fresh-private", repo=repo, synthetic=True
        ),
    )
    with tempfile.TemporaryDirectory(prefix="fresh-live-v2-corruptions-") as temporary:
        root = Path(temporary)
        _secure_directory(root)
        reject(
            "LOCK-01-before-provider-close",
            lambda: create_output_lock(
                {"trace/test": b"sealed"},
                ledger=_fresh_ledger(root / "open-ledger.jsonl"),
                campaign_id=CAMPAIGN_ID,
                batch_id=BATCH_ID,
            ),
        )
        closed = _fresh_ledger(root / "closed-ledger.jsonl")
        closed.close_provider_phase()
        reject(
            "LOCK-02-call-after-lock",
            lambda: closed.guard_next(
                provider="OpenAI",
                input_tokens=1,
                output_tokens=1,
                cost_usd=Decimal("0"),
            ),
        )
        task = generate_public_calibration()[0]
        reject(
            "PROVIDER-01-terminal-failure",
            lambda: PilotBatchRunner(
                state_root=root / "terminal-protocol",
                ledger=_fresh_ledger(root / "terminal-protocol-ledger.jsonl"),
                trace_key=b"t" * 32,
                campaign_id=CAMPAIGN_ID,
                batch_id=BATCH_ID,
                reject_protocol_errors=True,
            ).run_stage(
                stage="fixed-full-batch",
                tasks=(task,),
                adapters={model: MockAdapter(mode="error") for model in MODELS},
                verify_metrics=False,
            ),
        )
    if any(item["status"] != "rejected" for item in outcomes):
        raise ValueError("one or more fresh live corruptions were accepted")
    return tuple(outcomes)
