"""Deterministic no-network public-fixture end-to-end rehearsal."""

from __future__ import annotations

import json
from decimal import Decimal

from distributed_discovery.benchmark.agents_v1.adapters import MockAdapter
from distributed_discovery.benchmark.agents_v1.batch import plan_batch
from distributed_discovery.benchmark.agents_v1.contamination import run_public_probes
from distributed_discovery.benchmark.agents_v1.corruptions import execute_corruption_suite
from distributed_discovery.benchmark.agents_v1.custody import (
    ToyCustodyBundle,
    seal_public_toy,
)
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.models import (
    VERSIONS,
    TaskInstance,
    canonical_json,
    sha256_hex,
)
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.prompts import (
    ClosedCapabilityView,
    CompiledPrompt,
    compile_prompt,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import verify_offline_bundle


def run_rehearsal() -> dict[str, object]:
    tasks = generate_public_calibration()
    case_records: list[dict[str, object]] = []
    method_disagreements: list[str] = []
    trace_hashes: list[str] = []
    first_context: (
        tuple[TaskInstance, CompiledPrompt, str, dict[str, object], ToyCustodyBundle] | None
    ) = None
    for task in tasks:
        for architecture in ARCHITECTURES:
            adapter = MockAdapter()
            run = run_architecture(task, architecture, adapter)
            evaluation = evaluate_run(task, run)
            trace = build_trace(run)
            output = evaluation.serializable()
            custody = seal_public_toy(
                seed_material="PUBLIC-TOY-SEED",
                task_batch=[task.visible_record()],
                answer_key={"target": task.primitive_state["target"]},
                output=output,
            )
            errors = verify_offline_bundle(
                task=task,
                run=run,
                method_a=evaluation.__dict__,
                raw_trace=trace.raw,
                custody=custody,
                task_batch=[task.visible_record()],
                output=output,
                provider_calls=0,
                model_invocations=0,
                external_cost_usd=Decimal("0"),
                network_enabled=False,
            )
            method_disagreements.extend(
                f"{task.task_id}:{architecture}:{error}" for error in errors
            )
            trace_hashes.append(str(trace.raw["trace_hash"]))
            case_records.append(
                {
                    "task_id": task.task_id,
                    "family_id": task.family_id,
                    "architecture_id": architecture,
                    "final_action_count": len(run.final_actions),
                    "protocol_error_count": len(run.protocol_errors),
                    "trace_hash": trace.raw["trace_hash"],
                    "group_discovery": str(evaluation.group_discovery),
                }
            )
            if first_context is None:
                prompt = compile_prompt(task, sorted(task.capabilities)[0])
                final_action = run.final_actions[0].to_dict()
                final_action["agent_id"] = prompt.agent_id
                first_context = (
                    task,
                    prompt,
                    json.dumps(final_action, sort_keys=True),
                    dict(trace.raw),
                    custody,
                )
    malformed_run = run_architecture(tasks[0], ARCHITECTURES[0], MockAdapter("malformed"))
    error_run = run_architecture(tasks[0], ARCHITECTURES[0], MockAdapter("error"))
    sandbox_rejected = False
    try:
        ClosedCapabilityView(tasks[0].capabilities[sorted(tasks[0].capabilities)[0]])[
            "primitive_state"
        ]
    except PermissionError:
        sandbox_rejected = True
    if first_context is None:
        raise AssertionError("rehearsal produced no cases")
    corruption_results = execute_corruption_suite(
        task=first_context[0],
        prompt=first_context[1],
        raw_action=first_context[2],
        raw_trace=first_context[3],
        custody=first_context[4],
    )
    batch = plan_batch(
        tasks=len(tasks),
        architectures=len(ARCHITECTURES),
        models=1,
        repeats=1,
    )
    probes = run_public_probes()
    stable_payload = {
        "schema_version": "agents-v1-offline-rehearsal-v1",
        "versions": dict(VERSIONS),
        "public_task_count": len(tasks),
        "architecture_count": len(ARCHITECTURES),
        "case_count": len(case_records),
        "case_records": case_records,
        "method_b_errors": method_disagreements,
        "corruptions_rejected": sum(result.rejected for result in corruption_results),
        "corruption_count": len(corruption_results),
        "sandbox_rejected": sandbox_rejected,
        "malformed_schema_retry_observed": any(
            turn.retry_count == 1 for turn in malformed_run.turns
        ),
        "error_mock_errors_observed": len(error_run.protocol_errors),
        "contamination_probe_class_count": 12,
        "contamination_fixture_count": len(probes),
        "batch": batch.serializable(),
        "provider_calls": 0,
        "model_invocations": 0,
        "model_downloads": 0,
        "network_calls": 0,
        "external_cost_usd": "0",
        "private_material_created": False,
        "scientific_evidence_created": False,
        "trace_hashes": trace_hashes,
    }
    stable_payload["rehearsal_hash"] = (
        f"sha256:{sha256_hex(canonical_json(stable_payload))}"
    )
    stable_payload["status"] = (
        "pass"
        if not method_disagreements
        and stable_payload["corruptions_rejected"] == 24
        and sandbox_rejected
        else "fail"
    )
    return stable_payload


def readiness_report() -> dict[str, object]:
    rehearsal = run_rehearsal()
    ready = rehearsal["status"] == "pass"
    return {
        "decision": "ready-for-evaluation-registration" if ready else "stopped",
        "offline_rehearsal_status": rehearsal["status"],
        "rehearsal_hash": rehearsal["rehearsal_hash"],
        "provider_calls": 0,
        "model_invocations": 0,
        "external_cost_usd": "0",
        "private_material": "absent",
        "future_authorization_required": True,
        "next_gate": (
            "DiscoveryBench Agents v1 evaluation campaign registration and cost authorization"
        ),
        "next_file": "plans/DISCOVERYBENCH_AGENTS_V1_EVALUATION.md",
    }
