from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from distributed_discovery.benchmark.agents_v1.adapters import MockAdapter
from distributed_discovery.benchmark.agents_v1.authorization import (
    guard_live_execution,
    validate_authorization,
)
from distributed_discovery.benchmark.agents_v1.batch import plan_batch
from distributed_discovery.benchmark.agents_v1.contamination import (
    PROBE_CLASSES,
    classify_text,
)
from distributed_discovery.benchmark.agents_v1.corruptions import execute_corruption_suite
from distributed_discovery.benchmark.agents_v1.custody import (
    seal_public_toy,
    unseal_public_toy,
    verify_output_lock,
)
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.orchestration import run_architecture
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.traces import build_trace, verify_trace_hashes
from distributed_discovery.benchmark.agents_v1.verification import (
    reconstruct_metrics,
    verify_offline_bundle,
)

ROOT = Path(__file__).resolve().parents[1]


def _public_run() -> tuple[object, object, object]:
    task = generate_public_calibration()[0]
    run = run_architecture(task, "full-broadcast-shared-transcript", MockAdapter())
    evaluation = evaluate_run(task, run)
    return task, run, evaluation


def test_method_a_and_method_b_agree_without_composite() -> None:
    task, run, evaluation = _public_run()
    method_b = reconstruct_metrics(task, run)
    assert method_b == evaluation.__dict__
    assert "composite" not in evaluation.__dict__


def test_trace_hash_and_redaction_layers() -> None:
    task, run, _ = _public_run()
    modified_turns = list(run.turns)
    response = replace(
        modified_turns[0].response,
        operational_metadata={
            "token": "token=SECRET",
            "path": "/Users/example/private",
            "email": "person@example.com",
            "hidden_reasoning": "never store",
        },
    )
    modified_turns[0] = replace(modified_turns[0], response=response)
    trace = build_trace(replace(run, turns=tuple(modified_turns)))
    assert verify_trace_hashes(trace.raw)
    assert trace.audit["hidden_reasoning_stored"] is False
    assert "SECRET" not in json.dumps(trace.redacted)
    assert "/Users/" not in json.dumps(trace.redacted)
    tampered = dict(trace.raw)
    tampered["architecture_id"] = "tampered"
    assert not verify_trace_hashes(tampered)


def test_aes_gcm_public_toy_custody_and_output_lock() -> None:
    bundle = seal_public_toy(
        seed_material="PUBLIC-TOY-SEED",
        task_batch=["PUBLIC-TASK"],
        answer_key={"answer": "PUBLIC"},
        output={"value": 1},
    )
    assert bundle.manifest["algorithm"] == "AES-256-GCM"
    assert unseal_public_toy(bundle)["seed_material"] == "PUBLIC-TOY-SEED"
    assert verify_output_lock(bundle, {"value": 1})
    with pytest.raises(ValueError, match="ciphertext"):
        unseal_public_toy(replace(bundle, ciphertext=bundle.ciphertext + b"x"))


def test_contamination_requires_more_than_lexical_similarity() -> None:
    assert len(PROBE_CLASSES) == 12
    assert classify_text("ordinary overlap").quarantine is False
    assert classify_text("TARGET-A", expected_public_solution=True).classification == (
        "ordinary-correct-reasoning"
    )
    direct = classify_text("private answer_key")
    assert direct.classification == "direct-leakage"
    assert direct.stop_campaign is True


def test_zero_cost_planner_refuses_projected_external_cost() -> None:
    plan = plan_batch(tasks=10, architectures=5, models=1, repeats=1)
    assert plan.calls == 100
    assert plan.maximum_exposure_usd == Decimal("0")
    assert plan.registered_recommendation_usd == Decimal("750")
    with pytest.raises(PermissionError, match="exceeds authorized"):
        plan_batch(
            tasks=1,
            architectures=1,
            models=1,
            repeats=1,
            provider_model_costs=(("example/model", Decimal("0.01")),),
        )


def test_authorization_schema_and_positive_spend_refusal() -> None:
    fixture_dir = ROOT / "docs/benchmark/agents-v1/fixtures"
    valid = yaml.safe_load((fixture_dir / "valid-zero-spend-authorization.yml").read_text())
    assert validate_authorization(
        valid,
        now=datetime(2026, 7, 23, tzinfo=UTC),
    ) == valid
    invalid = yaml.safe_load(
        (fixture_dir / "invalid-positive-spend-authorization.yml").read_text()
    )
    with pytest.raises(PermissionError, match="positive spend"):
        validate_authorization(invalid, now=datetime(2026, 7, 23, tzinfo=UTC))
    with pytest.raises(PermissionError, match="explicit"):
        guard_live_execution(None, explicit_execute=False, expected_commit="0" * 40)


def test_independent_offline_verifier_and_all_corruptions() -> None:
    task, run, evaluation = _public_run()
    trace = build_trace(run)
    output = evaluation.serializable()
    task_batch = [task.visible_record()]
    custody = seal_public_toy(
        seed_material="PUBLIC-TOY-SEED",
        task_batch=task_batch,
        answer_key={"target": task.primitive_state["target"]},
        output=output,
    )
    assert (
        verify_offline_bundle(
            task=task,
            run=run,
            method_a=evaluation.__dict__,
            raw_trace=trace.raw,
            custody=custody,
            task_batch=task_batch,
            output=output,
            provider_calls=0,
            model_invocations=0,
            external_cost_usd=Decimal("0"),
            network_enabled=False,
        )
        == ()
    )
    agent_id = sorted(task.capabilities)[0]
    prompt = compile_prompt(task, agent_id)
    raw_action = run.final_actions[0].to_dict()
    raw_action["agent_id"] = agent_id
    results = execute_corruption_suite(
        task=task,
        prompt=prompt,
        raw_action=json.dumps(raw_action),
        raw_trace=dict(trace.raw),
        custody=custody,
    )
    assert [result.corruption_id for result in results] == [
        f"C{index:02d}" for index in range(1, 25)
    ]
    assert all(result.rejected for result in results)
