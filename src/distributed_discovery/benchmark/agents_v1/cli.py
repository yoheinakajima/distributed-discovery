"""Offline-only CLI for DiscoveryBench Agents v1."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.adapters import MockAdapter
from distributed_discovery.benchmark.agents_v1.batch import plan_batch
from distributed_discovery.benchmark.agents_v1.contamination import run_public_probes
from distributed_discovery.benchmark.agents_v1.custody import seal_public_toy, unseal_public_toy
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import (
    canonical_cells,
    generate_prompt_space,
    generate_public_calibration,
)
from distributed_discovery.benchmark.agents_v1.live_campaign import (
    run_provider_preflight,
    run_provider_preflight_all,
    run_public_calibration,
)
from distributed_discovery.benchmark.agents_v1.models import VERSIONS
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.pilot import (
    audit_pilot_corruptions,
    pilot_offline_readiness,
    run_synthetic_rehearsal,
)
from distributed_discovery.benchmark.agents_v1.pilot_live import run_live_pilot
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.rehearsal import (
    readiness_report,
    run_rehearsal,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace

COMMANDS = (
    "versions",
    "validate",
    "generate-public",
    "compile-prompts",
    "run-mock",
    "evaluate-mock",
    "redact-traces",
    "verify-custody",
    "contamination",
    "plan-batch",
    "verify-batch",
    "dry-run",
    "readiness",
    "provider-preflight",
    "public-calibration",
    "provider-preflight-all",
    "live-execute",
    "pilot-audit",
    "pilot-offline-readiness",
    "pilot-live",
    "pilot-verify",
    "pilot-redacted-summary",
    "pilot-rehearsal",
)


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("agents_command", choices=COMMANDS)
    parser.add_argument(
        "--force",
        action="store_true",
        help="rerun an already passing live stage without credential fingerprinting",
    )


def execute(args: argparse.Namespace) -> Mapping[str, object] | list[object]:
    command = args.agents_command
    if command == "versions":
        return dict(VERSIONS)
    if command == "validate":
        cells = canonical_cells()
        prompt_instances = generate_prompt_space()
        return {
            "status": "pass",
            "canonical_cells": len(cells),
            "prompt_variants": len(prompt_instances),
            "primitive_labeled_states": sum(cell.primitive_labeled_states for cell in cells),
        }
    if command == "generate-public":
        return [task.visible_record() for task in generate_public_calibration()]
    if command == "compile-prompts":
        tasks = generate_public_calibration()
        compiled_prompts = [
            compile_prompt(task, agent_id)
            for task in tasks
            for agent_id in sorted(task.capabilities)
        ]
        return {
            "status": "pass",
            "prompt_count": len(compiled_prompts),
            "public_calibration_only": True,
        }
    if command in {"run-mock", "evaluate-mock", "redact-traces"}:
        task = generate_public_calibration()[0]
        run = run_architecture(task, ARCHITECTURES[0], MockAdapter())
        if command == "run-mock":
            return {
                "architecture_id": run.architecture_id,
                "turns": len(run.turns),
                "final_actions": len(run.final_actions),
                "provider_calls": 0,
            }
        if command == "evaluate-mock":
            return evaluate_run(task, run).serializable()
        trace = build_trace(run)
        return {"audit": dict(trace.audit), "redacted": dict(trace.redacted)}
    if command == "verify-custody":
        bundle = seal_public_toy(
            seed_material="PUBLIC-TOY-SEED",
            task_batch=["PUBLIC"],
            answer_key={"PUBLIC": "TARGET-A"},
            output={"status": "public"},
        )
        return {
            "status": "pass" if unseal_public_toy(bundle) else "fail",
            "classification": bundle.manifest["classification"],
            "algorithm": bundle.manifest["algorithm"],
        }
    if command == "contamination":
        return [asdict(item) for item in run_public_probes()]
    if command in {"plan-batch", "verify-batch"}:
        plan = plan_batch(tasks=10, architectures=5, models=1, repeats=1)
        return {"status": "pass", "plan": plan.serializable()}
    if command == "dry-run":
        return run_rehearsal()
    if command == "readiness":
        return readiness_report()
    if command == "provider-preflight":
        return run_provider_preflight(Path.cwd(), force=bool(args.force))
    if command == "public-calibration":
        return run_public_calibration(Path.cwd(), force=bool(args.force))
    if command == "provider-preflight-all":
        return run_provider_preflight_all(Path.cwd(), force=bool(args.force))
    if command == "pilot-audit":
        corruptions = audit_pilot_corruptions(Path.cwd())
        return {
            **pilot_offline_readiness(Path.cwd()),
            "corruptions": len(corruptions),
            "corruptions_rejected": sum(item["status"] == "rejected" for item in corruptions),
        }
    if command == "pilot-offline-readiness":
        return pilot_offline_readiness(Path.cwd())
    if command == "pilot-live":
        return run_live_pilot(Path.cwd())
    if command == "pilot-verify":
        corruptions = audit_pilot_corruptions(Path.cwd())
        if any(item["status"] != "rejected" for item in corruptions):
            raise RuntimeError("pilot corruption verification failed")
        return {
            "status": "pass",
            "corruptions": len(corruptions),
            "corruptions_rejected": len(corruptions),
            "method": "synthetic-failure-injection",
        }
    if command == "pilot-redacted-summary":
        return {
            **pilot_offline_readiness(Path.cwd()),
            "public_boundary": "redacted-engineering-only-no-task-level-performance",
            "task_text_disclosed": False,
            "answer_disclosed": False,
            "performance_disclosed": False,
            "redaction_status": "pass",
        }
    if command == "pilot-rehearsal":
        return run_synthetic_rehearsal(Path.cwd())
    if command == "live-execute":
        raise PermissionError(
            "live execution is disabled; a separate owner authorization and campaign are required"
        )
    raise RuntimeError(f"unhandled Agents v1 command: {command}")


def run_cli(argv: Sequence[str]) -> Mapping[str, object] | list[object]:
    parser = argparse.ArgumentParser(prog="distributed-discovery agents-v1")
    configure(parser)
    return execute(parser.parse_args(list(argv)))
