"""Shared immutable records and canonical serialization."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from types import MappingProxyType

VERSIONS: Mapping[str, str] = MappingProxyType(
    {
        "instrument": "discoverybench-agents-v1",
        "content": "v3",
        "protocol": "agents-v1",
        "generator": "agents-task-generator-v1",
        "prompt": "agents-prompt-v1",
        "architecture": "agents-architecture-v1",
        "action": "agents-action-v1",
        "trace": "agents-trace-v1",
        "metric": "agents-metric-v1",
        "result": "agents-result-v1",
        "custody": "agents-custody-v1",
        "contamination": "agents-contamination-v1",
        "verification": "agents-verification-v1",
        "corruption": "agents-corruption-v1",
        "batch_plan": "agents-batch-plan-v1",
        "analysis": "agents-statistical-analysis-v1",
    }
)


def canonical_json(value: object) -> bytes:
    """Serialize JSON using the commitment-stable representation."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fraction_text(value: Fraction | int | str) -> str:
    return str(Fraction(value))


@dataclass(frozen=True)
class GeneratorCell:
    family_id: str
    cell_index: int
    parameters: Mapping[str, object]
    primitive_labeled_states: int

    @property
    def cell_id(self) -> str:
        return f"CELL-{self.family_id.upper()}-{self.cell_index:03d}"


@dataclass(frozen=True)
class CapabilityView:
    agent_id: str
    public_state: Mapping[str, object]
    private_observation: str
    visible_messages: tuple[str, ...] = ()
    portfolio_slot: str | None = None

    def serializable(self) -> dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "public_state": dict(self.public_state),
            "private_observation": self.private_observation,
            "visible_messages": list(self.visible_messages),
            "portfolio_slot": self.portfolio_slot,
        }


@dataclass(frozen=True)
class BaselineObject:
    private_discovery: str
    planner_discovery: str
    recovery_budget: int | None
    best_equilibrium: str | None = None
    worst_equilibrium: str | None = None


@dataclass(frozen=True)
class TaskInstance:
    task_id: str
    family_id: str
    cell_id: str
    public_fixture: bool
    variant: int
    action_vocabulary: tuple[str, ...]
    source_vocabulary: tuple[str, ...]
    capabilities: Mapping[str, CapabilityView]
    primitive_state: Mapping[str, object] = field(repr=False)
    baseline: BaselineObject = field(repr=False)
    commitment: str = ""

    def visible_record(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "public_fixture": self.public_fixture,
            "task_id": self.task_id,
            "family_id": self.family_id,
            "cell_id": self.cell_id,
            "variant": self.variant,
            "versions": dict(VERSIONS),
            "action_vocabulary": list(self.action_vocabulary),
            "source_vocabulary": list(self.source_vocabulary),
            "capabilities": {
                key: value.serializable() for key, value in sorted(self.capabilities.items())
            },
            "commitment": self.commitment,
        }

    def evaluator_record(self) -> dict[str, object]:
        return {
            "visible": self.visible_record(),
            "primitive_state": dict(self.primitive_state),
            "baseline": asdict(self.baseline),
        }


@dataclass(frozen=True)
class StructuredAction:
    task_commitment: str
    agent_id: str
    round_number: int
    final: bool
    actions: tuple[str, ...]
    visible_message: str = ""
    source_choice: str = "none"
    declared_metadata: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": VERSIONS["action"],
            "task_instance_commitment": f"sha256:{self.task_commitment}",
            "agent_id": self.agent_id,
            "round": self.round_number,
            "final": self.final,
            "visible_message": self.visible_message,
            "source_choice": self.source_choice,
            "actions": list(self.actions),
            "declared_metadata": dict(self.declared_metadata),
        }


def task_from_records(
    visible: Mapping[str, object],
    evaluator: Mapping[str, object],
) -> TaskInstance:
    """Round-trip a task from the separated visible and evaluator records."""
    capabilities_raw = visible["capabilities"]
    if not isinstance(capabilities_raw, Mapping):
        raise ValueError("capabilities must be an object")
    capabilities: dict[str, CapabilityView] = {}
    for agent_id, raw in capabilities_raw.items():
        if not isinstance(agent_id, str) or not isinstance(raw, Mapping):
            raise ValueError("invalid capability record")
        capabilities[agent_id] = CapabilityView(
            agent_id=agent_id,
            public_state=MappingProxyType(dict(_mapping(raw["public_state"]))),
            private_observation=str(raw["private_observation"]),
            visible_messages=tuple(str(item) for item in _sequence(raw["visible_messages"])),
            portfolio_slot=(
                str(raw["portfolio_slot"]) if raw.get("portfolio_slot") is not None else None
            ),
        )
    baseline_raw = _mapping(evaluator["baseline"])
    return TaskInstance(
        task_id=str(visible["task_id"]),
        family_id=str(visible["family_id"]),
        cell_id=str(visible["cell_id"]),
        public_fixture=bool(visible["public_fixture"]),
        variant=int(str(visible["variant"])),
        action_vocabulary=tuple(str(item) for item in _sequence(visible["action_vocabulary"])),
        source_vocabulary=tuple(str(item) for item in _sequence(visible["source_vocabulary"])),
        capabilities=MappingProxyType(capabilities),
        primitive_state=MappingProxyType(dict(_mapping(evaluator["primitive_state"]))),
        baseline=BaselineObject(
            private_discovery=str(baseline_raw["private_discovery"]),
            planner_discovery=str(baseline_raw["planner_discovery"]),
            recovery_budget=(
                int(str(baseline_raw["recovery_budget"]))
                if baseline_raw.get("recovery_budget") is not None
                else None
            ),
            best_equilibrium=(
                str(baseline_raw["best_equilibrium"])
                if baseline_raw.get("best_equilibrium") is not None
                else None
            ),
            worst_equilibrium=(
                str(baseline_raw["worst_equilibrium"])
                if baseline_raw.get("worst_equilibrium") is not None
                else None
            ),
        ),
        commitment=str(visible["commitment"]),
    )


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("expected object")
    return value


def _sequence(value: object) -> tuple[object, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("expected array")
    return tuple(value)
