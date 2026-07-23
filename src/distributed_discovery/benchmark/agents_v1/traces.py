"""Canonical raw, redacted, and audit trace layers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from distributed_discovery.benchmark.agents_v1.models import VERSIONS, canonical_json, sha256_hex
from distributed_discovery.benchmark.agents_v1.orchestration import ArchitectureRun

SECRET = re.compile(
    r"(?i)(?:api[_-]?key|authorization|bearer|token|secret|password)\s*[:=]\s*\S+"
)
HOST_PATH = re.compile(r"(?:/Users|/home|C:\\Users)[/\\][^\s\"']+")
PII_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PROPRIETARY = re.compile(r"(?i)\bproprietary[_ -]field\b[^,}\n]*")
CHAIN_FIELDS = frozenset({"chain_of_thought", "hidden_reasoning", "reasoning_tokens"})


@dataclass(frozen=True)
class TraceBundle:
    raw: Mapping[str, object]
    redacted: Mapping[str, object]
    audit: Mapping[str, object]


def _redact(value: object, path: str, records: list[str]) -> object:
    if isinstance(value, Mapping):
        output: dict[str, object] = {}
        for key, item in value.items():
            if key in CHAIN_FIELDS:
                records.append(f"{path}.{key}:removed-hidden-reasoning")
                continue
            output[str(key)] = _redact(item, f"{path}.{key}", records)
        return output
    if isinstance(value, list):
        return [_redact(item, f"{path}[{index}]", records) for index, item in enumerate(value)]
    if isinstance(value, str):
        redacted = value
        for name, pattern in (
            ("secret", SECRET),
            ("host-path", HOST_PATH),
            ("pii-email", PII_EMAIL),
            ("proprietary", PROPRIETARY),
        ):
            replaced = pattern.sub("[REDACTED]", redacted)
            if replaced != redacted:
                records.append(f"{path}:{name}")
                redacted = replaced
        return redacted
    return value


def build_trace(run: ArchitectureRun) -> TraceBundle:
    events: list[dict[str, object]] = []
    for sequence, turn in enumerate(run.turns):
        event = {
            "sequence": sequence,
            "architecture_id": turn.architecture_id,
            "agent_id": turn.agent_id,
            "round": turn.round_number,
            "visible_inputs": list(turn.visible_inputs),
            "visible_output": turn.action.visible_message if turn.action else "",
            "structured_action": turn.action.to_dict() if turn.action else None,
            "declared_tool_calls": [dict(item) for item in turn.response.declared_tool_calls],
            "usage": {
                "input_tokens": turn.response.usage.input_tokens,
                "output_tokens": turn.response.usage.output_tokens,
                "cost_usd": str(turn.response.usage.cost_usd),
            },
            "retry_count": turn.retry_count,
            "errors": list(turn.validation_errors),
            "operational_metadata": dict(turn.response.operational_metadata),
        }
        event["event_hash"] = f"sha256:{sha256_hex(canonical_json(event))}"
        events.append(event)
    raw: dict[str, object] = {
        "schema_version": VERSIONS["trace"],
        "task_instance_commitment": f"sha256:{run.task_commitment}",
        "architecture_id": run.architecture_id,
        "events": events,
    }
    raw["trace_hash"] = f"sha256:{sha256_hex(canonical_json(raw))}"
    records: list[str] = []
    redacted = _redact(raw, "$", records)
    assert isinstance(redacted, dict)
    redacted["redacted_trace_hash"] = f"sha256:{sha256_hex(canonical_json(redacted))}"
    audit = {
        "schema_version": VERSIONS["trace"],
        "raw_trace_hash": raw["trace_hash"],
        "redacted_trace_hash": redacted["redacted_trace_hash"],
        "event_count": len(events),
        "redactions": sorted(records),
        "hidden_reasoning_stored": False,
    }
    return TraceBundle(raw, redacted, audit)


def verify_trace_hashes(trace: Mapping[str, object]) -> bool:
    mutable = dict(trace)
    actual = mutable.pop("trace_hash", None)
    if actual != f"sha256:{sha256_hex(canonical_json(mutable))}":
        return False
    events = mutable.get("events")
    if not isinstance(events, list):
        return False
    for event in events:
        if not isinstance(event, Mapping):
            return False
        item = dict(event)
        event_hash = item.pop("event_hash", None)
        if event_hash != f"sha256:{sha256_hex(canonical_json(item))}":
            return False
    return True
