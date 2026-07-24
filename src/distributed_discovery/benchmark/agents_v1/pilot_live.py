"""Authorized, staged, resumable Phase B driver for the sealed pilot."""

from __future__ import annotations

import json
import secrets
import subprocess
from collections.abc import Mapping
from dataclasses import asdict, replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import yaml

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
    ArchitectureRun,
    TurnRecord,
)
from distributed_discovery.benchmark.agents_v1.pilot import (
    BASE_COMMIT,
    BATCH_ID,
    BRANCH,
    CAMPAIGN_ID,
    MAX_CALLS,
    MODELS,
    PROVIDERS,
    AppendOnlyLedger,
    PilotBatchRunner,
    ResumablePilotAdapter,
    SealedObject,
    atomic_private_write,
    create_output_lock,
    current_execution_identity,
    generate_allocated_tasks,
    initialize_private_state,
    load_or_create_real_custody_material,
    load_pilot_authorization,
    private_state_root,
    require_commitment,
    seal_object,
    unseal_answer_after_lock,
    unseal_object,
    validate_lock_inventory,
    validate_public_pilot_summary,
    verify_output_lock,
)
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import verify_method_agreement

PREFIX_INDICES = (0, 10, 20, 30, 40)
CALL_STAGES = frozenset({"public-canary", "private-prefix", "fixed-full-batch"})
CUSTODY_REPORT = Path("reports/benchmark/treasurebench-agents-v1-pilot-custody-commitment.yml")
LOCK_REPORT = Path("reports/benchmark/treasurebench-agents-v1-pilot-output-lock-commitment.yml")


def _secure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink() or not path.is_dir():
        raise PermissionError("private runtime directory is unsafe")
    path.chmod(0o700)


def _load_or_create_key(path: Path) -> bytes:
    if path.exists():
        if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
            raise PermissionError("private operational key is unsafe")
        value = path.read_bytes()
        if len(value) != 32:
            raise ValueError("private operational key has invalid length")
        return value
    value = secrets.token_bytes(32)
    atomic_private_write(path, value)
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    atomic_private_write(path, canonical_json(value) + b"\n")


def _read_json(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o077:
        raise PermissionError("private JSON state is unsafe")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("private JSON state must be an object")
    return {str(name): item for name, item in value.items()}


def _load_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "schema_version": "treasurebench-agents-v1-provider-stage-state-v1",
            "campaign_id": CAMPAIGN_ID,
            "batch_id": BATCH_ID,
            "public_canary_complete": False,
            "custody_complete": False,
            "private_prefix_complete": False,
            "fixed_full_batch_complete": False,
            "quarantined": False,
        }
    return _read_json(path)


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


def _sealed_record(sealed: SealedObject) -> Mapping[str, object]:
    return {"manifest": sealed.manifest(), "ciphertext_hex": sealed.ciphertext.hex()}


def _sealed_from_record(record: Mapping[str, object]) -> SealedObject:
    manifest = record.get("manifest")
    if not isinstance(manifest, Mapping):
        raise ValueError("sealed-object manifest is missing")
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
            raise ValueError("sealed-object domain mismatch")
        if sealed.ciphertext_sha256 != f"sha256:{sha256_hex(sealed.ciphertext)}":
            raise PermissionError("sealed-object ciphertext mismatch requires quarantine")
        return sealed
    sealed = seal_object(domain=domain, value=value, key=key, nonce=secrets.token_bytes(12))
    _write_json(path, _sealed_record(sealed))
    return sealed


def _execution_identity(repo: Path, authorization: Mapping[str, object]) -> Mapping[str, object]:
    current = current_execution_identity(repo)
    execution_commit = str(authorization["authorized_execution_commit"])
    remote = subprocess.run(
        ("git", "branch", "-r", "--contains", execution_commit),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not remote:
        raise PermissionError("authorized execution commit is not present remotely")
    if current["tree_hash"] != authorization["execution_tree_hash"]:
        raise PermissionError("execution-sensitive tree changed after authorization")
    return {
        "schema_version": "treasurebench-agents-v1-execution-identity-v1",
        "authorization_id": authorization["authorization_id"],
        "base_commit": BASE_COMMIT,
        "execution_commit": execution_commit,
        "execution_tree_hash": current["tree_hash"],
        "branch": BRANCH,
        "issue": 187,
        "pull_request": 188,
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "models": list(MODELS),
    }


def _bind_private_state(
    repo: Path, root: Path, authorization: Mapping[str, object]
) -> Mapping[str, object]:
    identity = _execution_identity(repo, authorization)
    path = root / "execution-identity.json"
    if path.exists():
        if _read_json(path) != identity:
            raise PermissionError("private state belongs to a different execution checkpoint")
    else:
        _write_json(path, identity)
    return identity


def _preflight_authorization(
    authorization: Mapping[str, object],
) -> PreflightAuthorization:
    caps = cast(Mapping[str, object], authorization["caps"])
    provider_caps = cast(Mapping[str, object], caps["provider_usd"])
    return PreflightAuthorization(
        authorization_id=str(authorization["authorization_id"]),
        authorized_base_commit=str(authorization["authorized_base_commit"]),
        allowed_branch=BRANCH,
        expires_utc=datetime.fromisoformat(
            str(authorization["expires_at_utc"]).replace("Z", "+00:00")
        ),
        total_cap_usd=Decimal(str(caps["total_usd"])),
        gateway_caps_usd={
            "openai_direct": Decimal(str(provider_caps["OpenAI"])),
            "anthropic_direct": Decimal(str(provider_caps["Anthropic"])),
        },
        route_caps_usd={
            "openai_direct": Decimal(str(provider_caps["OpenAI"])),
            "anthropic_direct": Decimal(str(provider_caps["Anthropic"])),
        },
        max_calls_per_route=MAX_CALLS,
        max_total_calls=MAX_CALLS,
        max_live_concurrency=int(str(caps["live_concurrency"])),
        private_tasks_allowed=True,
        scientific_evidence_allowed=False,
        raw=authorization,
    )


def _live_adapters(
    repo: Path,
    authorization: Mapping[str, object],
    ledger: AppendOnlyLedger,
    response_key: bytes,
    response_root: Path,
) -> tuple[dict[str, AgentAdapter], CredentialSet, tuple[object, ...]]:
    credentials = load_credentials(repo / ".env.txt", explicit_live_mode=True)
    openai_key = credentials.get_secret("OPENAI_API_KEY")
    anthropic_key = credentials.get_secret("ANTHROPIC_API_KEY")
    if not openai_key or not anthropic_key:
        credentials.clear()
        raise PermissionError("both exact direct provider credentials are required")
    cost_ledger = CostLedger(_preflight_authorization(authorization))
    transport = UrllibTransport()
    openai = OpenAIResponsesAdapter(
        api_key=openai_key, transport=transport, network_enabled=True, ledger=cost_ledger
    )
    anthropic = AnthropicMessagesAdapter(
        api_key=anthropic_key,
        transport=transport,
        network_enabled=True,
        ledger=cost_ledger,
    )
    underlying = (openai, anthropic)
    adapters: dict[str, AgentAdapter] = {
        model: ResumablePilotAdapter(
            underlying[index],
            provider=PROVIDERS[index],
            model=model,
            ledger=ledger,
            response_root=response_root / PROVIDERS[index].lower(),
            response_key=response_key,
        )
        for index, model in enumerate(MODELS)
    }
    return adapters, credentials, underlying


class _ReplayOnlyAdapter:
    def __init__(self, *, provider: str, model: str) -> None:
        self.manifest = ModelManifest(
            provider=provider,
            model_id=model,
            exact_snapshot=model,
            adapter_version="sealed-pilot-replay-only-v1",
            moving_alias=False,
            live_capable=False,
        )

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        raise PermissionError("a missing replay response cannot trigger a provider call")


def _replay_adapters(
    ledger: AppendOnlyLedger, response_key: bytes, response_root: Path
) -> dict[str, AgentAdapter]:
    return {
        model: ResumablePilotAdapter(
            _ReplayOnlyAdapter(provider=PROVIDERS[index], model=model),
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
    adapters: dict[str, AgentAdapter] = {
        model: ResumablePilotAdapter(
            underlying[model],
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
        domain=f"raw-trace/{trace_id}",
        value=value,
        key=key,
        nonce=secrets.token_bytes(12),
    )
    path = root / "encrypted-traces" / f"{sha256_hex(trace_id.encode())}.sealed"
    _write_json(path, _sealed_record(sealed))


def _run_public_canary(
    *, root: Path, adapters: Mapping[str, AgentAdapter], key: bytes
) -> Mapping[str, object]:
    task = generate_public_calibration()[2]
    agent_id = sorted(task.capabilities)[0]
    for model, adapter in adapters.items():
        prompt = compile_prompt(task, agent_id, architecture_id="provider-native-smoke")
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
        metrics = asdict(evaluate_run(task, run))
        errors.extend(verify_method_agreement(metrics, task, run))
        if errors:
            raise RuntimeError("public exact-route canary failed")
        _seal_trace(root, f"public-canary/{model}", trace.raw, key)
    return {"status": "pass", "routes": len(adapters), "requests_per_route": 1}


def _custody(
    repo: Path,
    root: Path,
    authorization: Mapping[str, object],
) -> tuple[
    tuple[TaskInstance, ...],
    Mapping[str, bytes],
    SealedObject,
    SealedObject,
    Mapping[str, object],
]:
    material = load_or_create_real_custody_material(root)
    tasks = generate_allocated_tasks(
        repo, authorization=authorization, material=material["seed"].hex()
    )
    task_payload = [task.visible_record() for task in tasks]
    answer_payload = [task.evaluator_record() for task in tasks]
    task_sealed = _load_or_create_sealed(
        root / "task-custody.json",
        domain="real-private-task-batch",
        value=task_payload,
        key=material["task_key"],
    )
    answer_sealed = _load_or_create_sealed(
        root / "answer-custody.json",
        domain="real-private-answer-key",
        value=answer_payload,
        key=material["answer_key"],
    )
    manifest: Mapping[str, object] = {
        "schema_version": "treasurebench-agents-v1-custody-manifest-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "seed_commitment": domain_commitment(
            "treasurebench-agents-v1/pilot-seed", material["seed"].hex()
        ),
        "task_plaintext_commitment": domain_commitment(
            "treasurebench-agents-v1/task-batch", task_payload
        ),
        "answer_plaintext_commitment": domain_commitment(
            "treasurebench-agents-v1/answer-key", answer_payload
        ),
        "task_ciphertext_commitment": task_sealed.ciphertext_sha256,
        "answer_ciphertext_commitment": answer_sealed.ciphertext_sha256,
        "tasks": len(tasks),
    }
    path = root / "custody-manifest.json"
    if path.exists() and _read_json(path) != manifest:
        raise PermissionError("custody manifest mismatch requires quarantine")
    if not path.exists():
        _write_json(path, manifest)
    return tuple(tasks), material, task_sealed, answer_sealed, manifest


def _output_objects(root: Path, ledger: AppendOnlyLedger) -> dict[str, bytes]:
    objects = {
        "task-ciphertext": (root / "task-custody.json").read_bytes(),
        "answer-ciphertext": (root / "answer-custody.json").read_bytes(),
        "custody-manifest": (root / "custody-manifest.json").read_bytes(),
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


def _require_public_record(repo: Path, relative: Path, expected: Mapping[str, object]) -> None:
    path = repo / relative
    if not path.is_file() or path.is_symlink():
        raise PermissionError(f"{relative.name} must be published before the next stage")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    mismatch = isinstance(value, Mapping) and any(
        value.get(key) != item for key, item in expected.items()
    )
    if not isinstance(value, Mapping) or mismatch:
        raise PermissionError(f"{relative.name} does not match private commitments")
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
    remote = subprocess.run(
        ("git", "branch", "-r", "--contains", head),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not remote:
        raise PermissionError("the public commitment commit must be pushed")


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
    initialize_private_state(root, repo=repo, synthetic=bool(authorization["synthetic"]))
    identity = _bind_private_state(repo, root, authorization)
    access = AppendOnlyLedger(root / "access-log.jsonl")
    state_path = root / "provider-stage-state.json"
    state = _load_state(state_path)
    runner = PilotBatchRunner(state_root=root, ledger=ledger, trace_key=operational_key)

    if stage == "public-canary":
        if state["public_canary_complete"]:
            return {"stage": stage, "status": "already-complete"}
        if adapters is None:
            raise RuntimeError("canary adapters are required")
        result = _run_public_canary(root=root, adapters=adapters, key=operational_key)
        _append_access_once(
            access, operation="public-exact-route-canary-pass", private_material=False
        )
        _mark_state(state_path, state, "public_canary_complete")
        return {**result, "stage": stage, "private_material_created": False}

    if not state["public_canary_complete"]:
        raise PermissionError("public canary must pass before private generation")
    tasks, material, task_sealed, answer_sealed, custody = _custody(repo, root, authorization)
    if stage == "custody":
        _append_access_once(access, operation="real-private-custody-created", private_material=True)
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
        raise PermissionError("custody stage must be committed before private calls")

    prefix = tuple(tasks[index] for index in PREFIX_INDICES)
    if stage == "private-prefix":
        if state["private_prefix_complete"]:
            return {"stage": stage, "status": "already-complete"}
        if adapters is None:
            raise RuntimeError("prefix adapters are required")
        result = runner.run_stage(
            stage=stage, tasks=prefix, adapters=adapters, verify_metrics=False
        )
        _append_access_once(
            access, operation="private-ten-percent-prefix-pass", private_material=True
        )
        _mark_state(state_path, state, "private_prefix_complete")
        return {"status": "pass", **result, "usage": dict(_public_totals(ledger))}
    if not state["private_prefix_complete"]:
        raise PermissionError("private prefix must pass before full execution")

    remaining = tuple(task for index, task in enumerate(tasks) if index not in PREFIX_INDICES)
    if stage == "fixed-full-batch":
        if state["fixed_full_batch_complete"]:
            return {"stage": stage, "status": "already-complete"}
        if adapters is None:
            raise RuntimeError("full-batch adapters are required")
        result = runner.run_stage(
            stage=stage, tasks=remaining, adapters=adapters, verify_metrics=False
        )
        _append_access_once(access, operation="fixed-full-batch-complete", private_material=True)
        _mark_state(state_path, state, "fixed_full_batch_complete")
        return {"status": "pass", **result, "usage": dict(_public_totals(ledger))}
    if not state["fixed_full_batch_complete"]:
        raise PermissionError("fixed full batch must finish before output lock")

    if stage == "output-lock":
        if not any(
            record.get("event_type") == "provider-phase-closed" for record in ledger.records
        ):
            _append_access_once(
                access,
                operation="answer-unseal-approved-after-provider-close",
                private_material=True,
            )
            ledger.close_provider_phase()
        objects = _output_objects(root, ledger)
        lock_path = root / "output-lock.json"
        if lock_path.exists():
            lock = _read_json(lock_path)
            verify_output_lock(lock, objects, ledger=ledger)
        else:
            lock = dict(create_output_lock(objects, ledger=ledger))
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
        raise ValueError(f"unknown live stage: {stage}")

    objects = _output_objects(root, ledger)
    lock = _read_json(root / "output-lock.json")
    verify_output_lock(lock, objects, ledger=ledger)
    unsealed_tasks = unseal_object(task_sealed, key=material["task_key"])
    unsealed_answers = unseal_answer_after_lock(
        answer_sealed,
        key=material["answer_key"],
        lock=lock,
        objects=objects,
        ledger=ledger,
    )
    require_commitment(
        str(custody["task_plaintext_commitment"]),
        domain_commitment("treasurebench-agents-v1/task-batch", unsealed_tasks),
        domain="task-batch",
    )
    require_commitment(
        str(custody["answer_plaintext_commitment"]),
        domain_commitment("treasurebench-agents-v1/answer-key", unsealed_answers),
        domain="answer-key",
    )
    if adapters is None:
        raise RuntimeError("replay adapters are required")
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
    totals = _public_totals(ledger)
    provider_errors = {
        provider: sum(
            record.get("event_type") == "provider-call"
            and record.get("provider") == provider
            and record.get("status") != "success"
            for record in ledger.records
        )
        for provider in PROVIDERS
    }
    summary: dict[str, object] = {
        "schema_version": "treasurebench-agents-v1-sealed-pilot-summary-v1",
        "status": "pass",
        "decision": "sealed-pilot-complete-base-campaign-registration-ready",
        "classification": "redacted-engineering-only-no-task-level-performance",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "authorization_id": authorization["authorization_id"],
        "execution_commit": identity["execution_commit"],
        "execution_tree_hash": identity["execution_tree_hash"],
        "tasks": len(tasks),
        "families": 5,
        "architectures": 5,
        "models": list(MODELS),
        "private_runs": len(tasks) * 5 * 2,
        "prefix_tasks": len(prefix),
        "output_lock_hash": lock["lock_hash"],
        "seed_commitment": custody["seed_commitment"],
        "task_ciphertext_commitment": task_sealed.ciphertext_sha256,
        "answer_ciphertext_commitment": answer_sealed.ciphertext_sha256,
        "method_a_b_disagreements": 0,
        "contamination_findings": 0,
        "protocol_errors": (
            int(str(prefix_verification["protocol_errors"]))
            + int(str(full_verification["protocol_errors"]))
        ),
        "provider_error_counts": provider_errors,
        "usage": dict(totals),
        "retention_days": 365,
        "provider_phase_closed": True,
        "output_lock_verified": True,
        "unseal_after_lock_verified": True,
        "redaction_status": "pass",
        "task_text_disclosed": False,
        "answer_disclosed": False,
        "task_level_performance_disclosed": False,
        "claim_created": False,
        "study_created": False,
        "scientific_run_created": False,
    }
    validate_public_pilot_summary(summary)
    audit_sealed = seal_object(
        domain="final-private-audit-package",
        value={
            "summary": summary,
            "prefix_verification": prefix_verification,
            "full_verification": full_verification,
        },
        key=material["answer_key"],
        nonce=secrets.token_bytes(12),
    )
    _write_json(root / "final-audit-package.sealed.json", _sealed_record(audit_sealed))
    _write_json(root / "redacted-summary.json", summary)
    return summary


def run_live_pilot(repo: Path) -> Mapping[str, object]:
    """Advance exactly one authorized stage, enforcing public commit gates."""
    authorization = load_pilot_authorization(repo)
    root = private_state_root()
    _secure_directory(root)
    initialize_private_state(root, repo=repo, synthetic=False)
    _bind_private_state(repo, root, authorization)
    operational_key = _load_or_create_key(root / "operational-key.bin")
    response_root = root / "encrypted-provider-responses"
    _secure_directory(response_root)
    ledger = AppendOnlyLedger(root / "usage-cost-ledger.jsonl")
    state = _load_state(root / "provider-stage-state.json")
    stage = _next_stage(repo, root, state)
    credentials: CredentialSet | None = None
    live_underlying: tuple[object, ...] = ()
    if stage in CALL_STAGES:
        adapters, credentials, live_underlying = _live_adapters(
            repo, authorization, ledger, operational_key, response_root
        )
    elif stage == "verify":
        adapters = _replay_adapters(ledger, operational_key, response_root)
    else:
        adapters = None
    try:
        return _execute_stage(
            repo,
            authorization=authorization,
            root=root,
            stage=stage,
            adapters=adapters,
            operational_key=operational_key,
            ledger=ledger,
        )
    finally:
        for adapter in live_underlying:
            clear = getattr(adapter, "clear_secret", None)
            if callable(clear):
                clear()
        if credentials is not None:
            credentials.clear()


def run_mock_pilot(
    repo: Path, *, authorization: Mapping[str, object], root: Path
) -> tuple[Mapping[str, object], Mapping[str, MockAdapter]]:
    """Exercise every staged Phase B transition with deterministic mocks."""
    _secure_directory(root)
    initialize_private_state(root, repo=repo, synthetic=True)
    _bind_private_state(repo, root, authorization)
    operational_key = _load_or_create_key(root / "operational-key.bin")
    response_root = root / "encrypted-provider-responses"
    _secure_directory(response_root)
    ledger = AppendOnlyLedger(root / "usage-cost-ledger.jsonl")
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
