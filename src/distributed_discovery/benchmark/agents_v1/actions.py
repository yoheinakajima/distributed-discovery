"""Strict structured-action parsing and validation."""

from __future__ import annotations

import json
from collections.abc import Mapping

from distributed_discovery.benchmark.agents_v1.models import VERSIONS, StructuredAction

PROHIBITED_ACTION_FIELDS = frozenset(
    {
        "answer",
        "answer_key",
        "expected_metrics",
        "baseline",
        "target_state",
        "primitive_state",
        "evaluator",
        "hidden_reasoning",
        "chain_of_thought",
        "instructions_to_evaluator",
        "tool_calls",
    }
)
REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "task_instance_commitment",
        "agent_id",
        "round",
        "final",
        "visible_message",
        "source_choice",
        "actions",
        "declared_metadata",
    }
)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate field: {key}")
        result[key] = value
    return result


def parse_action(
    raw_output: str,
    *,
    task_commitment: str,
    agent_id: str,
    round_number: int,
    action_vocabulary: tuple[str, ...],
    source_vocabulary: tuple[str, ...],
    final_required: bool = False,
) -> StructuredAction:
    try:
        value = json.loads(raw_output, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as error:
        raise ValueError("malformed JSON") from error
    if not isinstance(value, Mapping):
        raise ValueError("action output must be an object")
    unknown = set(value) - REQUIRED_FIELDS
    prohibited = set(value) & PROHIBITED_ACTION_FIELDS
    if prohibited:
        raise ValueError(f"hidden/evaluator fields prohibited: {sorted(prohibited)}")
    if unknown:
        raise ValueError(f"undeclared fields: {sorted(unknown)}")
    missing = REQUIRED_FIELDS - set(value)
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    if value["schema_version"] != VERSIONS["action"]:
        raise ValueError("action version mismatch")
    if value["task_instance_commitment"] != f"sha256:{task_commitment}":
        raise ValueError("task commitment mismatch")
    if value["agent_id"] != agent_id:
        raise ValueError("agent identity mismatch")
    if value["round"] != round_number or round_number not in (0, 1, 2):
        raise ValueError("round mismatch")
    if not isinstance(value["final"], bool) or (final_required and not value["final"]):
        raise ValueError("invalid final flag")
    message = value["visible_message"]
    if not isinstance(message, str) or len(message) > 1024:
        raise ValueError("visible message exceeds the registered 256-token ceiling")
    source = value["source_choice"]
    if source not in source_vocabulary:
        raise ValueError("out-of-domain source choice")
    actions = value["actions"]
    if not isinstance(actions, list) or not actions:
        raise ValueError("missing actions")
    if len(actions) != len(set(str(item) for item in actions)):
        raise ValueError("duplicate actions")
    if any(not isinstance(item, str) or item not in action_vocabulary for item in actions):
        raise ValueError("out-of-domain action")
    metadata = value["declared_metadata"]
    if not isinstance(metadata, Mapping):
        raise ValueError("declared metadata must be an object")
    if set(metadata) & PROHIBITED_ACTION_FIELDS:
        raise ValueError("hidden/evaluator metadata prohibited")
    return StructuredAction(
        task_commitment=task_commitment,
        agent_id=agent_id,
        round_number=round_number,
        final=bool(value["final"]),
        actions=tuple(actions),
        visible_message=message,
        source_choice=str(source),
        declared_metadata=dict(metadata),
    )
