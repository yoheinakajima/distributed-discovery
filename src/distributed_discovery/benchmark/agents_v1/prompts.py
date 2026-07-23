"""Prompt compilation and immutable capability sandbox."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from distributed_discovery.benchmark.agents_v1.generation import FAMILY_PUBLIC_CODES
from distributed_discovery.benchmark.agents_v1.models import CapabilityView, TaskInstance

PROHIBITED_KEYS = frozenset(
    {
        "target",
        "target_state",
        "primitive_state",
        "baseline",
        "expected_metrics",
        "answer",
        "answer_key",
        "seed",
        "holdout",
        "custody",
        "evaluator",
        "reference_claims",
        "reference_runs",
        "repository",
        "filesystem",
        "shell",
        "network",
        "environment",
        "secrets",
        "prior_batch_outputs",
        "other_agent_private_observation",
    }
)
LEAK_PATTERNS = {
    "dd-id": re.compile(r"\bDD-\d{3}[A-Z]?\b"),
    "claim-id": re.compile(r"\bDD-C-\d{4}\b"),
    "run-id": re.compile(r"\b20\d{6}T\d{6}Z_DD-"),
    "scientific-title": re.compile(
        r"\b(shared discovery paradox|common-source trap|incentive to ignore|"
        r"threshold discovery|information sharing frontier)\b",
        re.IGNORECASE,
    ),
    "answer-field": re.compile(
        r"\b(answer[_ -]?key|expected[_ -]?(?:value|metric)|planner[_ -]?baseline)\b",
        re.IGNORECASE,
    ),
    "generator-internal": re.compile(
        r"\b(generator[_ -]?parameters|primitive[_ -]?state|custody[_ -]?manifest)\b",
        re.IGNORECASE,
    ),
}


@dataclass(frozen=True)
class CompiledPrompt:
    task_commitment: str
    agent_id: str
    system: str
    user: str
    public_calibration: bool


class ClosedCapabilityView(Mapping[str, object]):
    """Read-only allow-list mapping that reports undeclared access."""

    def __init__(self, capability: CapabilityView) -> None:
        values = capability.serializable()
        self._values: Mapping[str, object] = MappingProxyType(values)
        self._allowed = frozenset(values)

    def __getitem__(self, key: str) -> object:
        if key in PROHIBITED_KEYS or key not in self._allowed:
            raise PermissionError(f"undeclared capability: {key}")
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._allowed))

    def __len__(self) -> int:
        return len(self._allowed)


def leakage_findings(value: object, *, evaluator_values: tuple[str, ...] = ()) -> tuple[str, ...]:
    text = json.dumps(value, sort_keys=True)
    findings = [name for name, pattern in LEAK_PATTERNS.items() if pattern.search(text)]
    lowered = text.lower()
    for key in PROHIBITED_KEYS:
        if f'"{key.lower()}"' in lowered:
            findings.append(f"prohibited-key:{key}")
    for exact in evaluator_values:
        if exact and exact not in {"0", "1"} and exact in text:
            findings.append("exact-evaluator-value")
    return tuple(sorted(set(findings)))


def compile_prompt(
    task: TaskInstance,
    agent_id: str,
    *,
    architecture_id: str = "unspecified-public-conformance",
    rounds_remaining: int = 2,
) -> CompiledPrompt:
    capability = task.capabilities[agent_id]
    system = (
        "Solve only the supplied finite synthetic search task. Use only the declared "
        "capabilities and visible messages. Return one schema-valid visible message and "
        "final structured action. Do not request hidden state or hidden reasoning."
    )
    payload = {
        "family": FAMILY_PUBLIC_CODES[task.family_id],
        "architecture_id": architecture_id,
        "agent": agent_id,
        "public_state": dict(capability.public_state),
        "private_observation": capability.private_observation,
        "visible_messages": list(capability.visible_messages),
        "portfolio_slot": capability.portfolio_slot,
        "actions": list(task.action_vocabulary),
        "sources": list(task.source_vocabulary),
        "rounds_remaining": rounds_remaining,
        "output_contract": {
            "agent_id": agent_id,
            "visible_message": "string",
            "source_choice": list(task.source_vocabulary),
            "actions": list(task.action_vocabulary),
        },
    }
    public_state_text = json.dumps(dict(capability.public_state), sort_keys=True)
    evaluator_values = tuple(
        value
        for value in (
            task.baseline.private_discovery,
            task.baseline.planner_discovery,
            task.baseline.best_equilibrium or "",
            task.baseline.worst_equilibrium or "",
        )
        if value not in public_state_text
    )
    findings = leakage_findings(payload, evaluator_values=evaluator_values)
    if findings:
        raise ValueError(f"prompt leakage: {', '.join(findings)}")
    return CompiledPrompt(
        task.commitment,
        agent_id,
        system,
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
        task.public_fixture,
    )
