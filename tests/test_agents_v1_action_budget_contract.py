from __future__ import annotations

import json
from dataclasses import asdict, replace
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from distributed_discovery.benchmark.agents_v1.actions import parse_action
from distributed_discovery.benchmark.agents_v1.adapters import MockAdapter
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.orchestration import (
    run_architecture,
    validate_orchestrated_action,
)
from distributed_discovery.benchmark.agents_v1.protocol_contract import (
    final_action_cardinalities,
    verify_metric_ranges,
    verify_protocol_contract,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import (
    reconstruct_metrics,
    verify_method_agreement,
)

ROOT = Path(__file__).resolve().parents[1]


def _over_budget_run() -> tuple[object, object]:
    task = generate_public_calibration()[0]
    run = run_architecture(task, "full-broadcast-shared-transcript", MockAdapter())
    original = run.final_actions[0]
    choices = tuple(task.action_vocabulary[:2])
    assert len(choices) == 2
    corrupted = replace(original, actions=choices)
    turns = tuple(
        replace(turn, action=corrupted) if turn.action is original else turn for turn in run.turns
    )
    finals = tuple(corrupted if action is original else action for action in run.final_actions)
    return task, replace(run, turns=turns, final_actions=finals)


def test_static_schema_allows_proposals_but_requires_one_final_action() -> None:
    schema = json.loads(
        (ROOT / "docs/benchmark/agents-v1/structured-output.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validator = Draft202012Validator(schema)
    task = generate_public_calibration()[0]
    agent_id = sorted(task.capabilities)[0]
    payload = {
        "schema_version": "agents-action-v1",
        "task_instance_commitment": f"sha256:{task.commitment}",
        "agent_id": agent_id,
        "round": 0,
        "final": False,
        "visible_message": "two proposals",
        "source_choice": task.source_vocabulary[0],
        "actions": list(task.action_vocabulary[:2]),
        "declared_metadata": {},
    }
    validator.validate(payload)
    payload["final"] = True
    with pytest.raises(ValidationError):
        validator.validate(payload)


def test_parser_distinguishes_nonfinal_proposals_from_final_actions() -> None:
    task = generate_public_calibration()[0]
    agent_id = sorted(task.capabilities)[0]
    payload = {
        "schema_version": "agents-action-v1",
        "task_instance_commitment": f"sha256:{task.commitment}",
        "agent_id": agent_id,
        "round": 0,
        "final": False,
        "visible_message": "proposal candidates",
        "source_choice": task.source_vocabulary[0],
        "actions": list(task.action_vocabulary[:2]),
        "declared_metadata": {},
    }
    proposal = parse_action(
        json.dumps(payload),
        task_commitment=task.commitment,
        agent_id=agent_id,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        final_required=False,
    )
    assert proposal.final is False
    assert len(proposal.actions) == 2

    payload["final"] = True
    with pytest.raises(ValueError, match="cardinality"):
        parse_action(
            json.dumps(payload),
            task_commitment=task.commitment,
            agent_id=agent_id,
            round_number=0,
            action_vocabulary=task.action_vocabulary,
            source_vocabulary=task.source_vocabulary,
            final_required=True,
        )


def test_method_c_rejects_shared_over_budget_final_semantics() -> None:
    task, run = _over_budget_run()
    assert validate_orchestrated_action(
        run.final_actions[0],  # type: ignore[attr-defined]
        final_required=True,
    ) == ("extra-action",)
    contract = verify_protocol_contract(task, run)  # type: ignore[arg-type]
    assert any("final-action-count" in error for error in contract.errors)
    assert contract.compliant is False

    method_a = evaluate_run(task, run)  # type: ignore[arg-type]
    method_b = reconstruct_metrics(task, run)  # type: ignore[arg-type]
    assert method_b == asdict(method_a)
    assert method_a.protocol_compliance == 0
    assert method_a.invalid_action_rate > 0
    assert 0 <= method_a.distinct_action_coverage <= 1
    assert verify_method_agreement(asdict(method_a), task, run) == ()  # type: ignore[arg-type]


def test_method_c_checks_trace_cardinality_and_metric_ranges() -> None:
    task, run = _over_budget_run()
    trace = build_trace(run)  # type: ignore[arg-type]
    events = trace.raw["events"]
    assert isinstance(events, list)
    cardinalities = final_action_cardinalities(events)
    assert any(count == 2 for _, _, count in cardinalities)

    evaluation = evaluate_run(task, run)  # type: ignore[arg-type]
    metrics = asdict(evaluation)
    assert verify_metric_ranges(metrics) == ()
    metrics["distinct_action_coverage"] = Fraction(2)
    assert "distinct_action_coverage:range" in verify_metric_ranges(metrics)
    metrics["distinct_action_coverage"] = Fraction(1)
    metrics["cost_usd"] = Decimal("-0.01")
    assert "cost_usd:range" in verify_metric_ranges(metrics)
