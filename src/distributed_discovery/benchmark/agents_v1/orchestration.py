"""Registered two-round team-architecture orchestrators."""

from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType

from distributed_discovery.benchmark.agents_v1.actions import parse_action
from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    AgentAdapter,
    Usage,
)
from distributed_discovery.benchmark.agents_v1.models import (
    CapabilityView,
    StructuredAction,
    TaskInstance,
)
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt

ARCHITECTURES = (
    "isolated-private-agents",
    "full-broadcast-shared-transcript",
    "designated-reader-selective-sharing",
    "pooled-consensus",
    "portfolio-preserving-structured",
)
ARCHITECTURE_MESSAGE_ROUNDS = {
    "isolated-private-agents": 0,
    "full-broadcast-shared-transcript": 2,
    "designated-reader-selective-sharing": 1,
    "pooled-consensus": 2,
    "portfolio-preserving-structured": 2,
}
ARCHITECTURE_TURNS = {
    "isolated-private-agents": 1,
    "full-broadcast-shared-transcript": 2,
    "designated-reader-selective-sharing": 2,
    "pooled-consensus": 2,
    "portfolio-preserving-structured": 2,
}
MAX_ROUNDS = 2
MAX_MESSAGE_CHARS = 1024
SCHEMA_RETRIES = 1


@dataclass(frozen=True)
class TurnRecord:
    architecture_id: str
    agent_id: str
    round_number: int
    visible_inputs: tuple[str, ...]
    response: AdapterResponse
    action: StructuredAction | None
    validation_errors: tuple[str, ...] = ()
    retry_count: int = 0


@dataclass(frozen=True)
class ArchitectureRun:
    architecture_id: str
    task_commitment: str
    turns: tuple[TurnRecord, ...]
    final_actions: tuple[StructuredAction, ...]
    protocol_errors: tuple[str, ...]


def information_rights(
    architecture_id: str,
    agent_ids: tuple[str, ...],
    messages: tuple[tuple[str, str], ...],
) -> dict[str, tuple[str, ...]]:
    if architecture_id not in ARCHITECTURES:
        raise ValueError(f"unknown architecture: {architecture_id}")
    if architecture_id == "isolated-private-agents":
        return {agent: () for agent in agent_ids}
    if architecture_id == "full-broadcast-shared-transcript":
        all_messages = tuple(message for _, message in messages)
        return {agent: all_messages for agent in agent_ids}
    if architecture_id == "designated-reader-selective-sharing":
        reader = agent_ids[0]
        selected = tuple(message for source, message in messages if source == reader)
        return {agent: selected for agent in agent_ids}
    if architecture_id == "pooled-consensus":
        pooled = tuple(sorted({message for _, message in messages}))
        return {agent: pooled for agent in agent_ids}
    return {
        agent: tuple(
            message
            for source, message in messages
            if source == agent
            or _portfolio_slot(source, agent_ids) == _portfolio_slot(agent, agent_ids)
        )
        for agent in agent_ids
    }


def _portfolio_slot(agent_id: str, agent_ids: tuple[str, ...]) -> str:
    return f"SLOT-{agent_ids.index(agent_id) % 2 + 1}"


def _task_with_messages(
    task: TaskInstance,
    rights: dict[str, tuple[str, ...]],
    architecture_id: str,
    selected_sources: dict[str, str],
) -> TaskInstance:
    source_signals = task.primitive_state.get("source_signals", {})
    capabilities: dict[str, CapabilityView] = {}
    for agent, capability in task.capabilities.items():
        observation = capability.private_observation
        if task.family_id == "common-source-acquisition" and agent in selected_sources:
            if not isinstance(source_signals, dict):
                raise ValueError("acquisition source signals must be a mapping")
            agent_signals = source_signals.get(agent)
            if not isinstance(agent_signals, dict):
                raise ValueError("agent source signals must be a mapping")
            observation = str(agent_signals[selected_sources[agent]])
        capabilities[agent] = replace(
            capability,
            private_observation=observation,
            visible_messages=rights[agent],
            portfolio_slot=(
                _portfolio_slot(agent, tuple(sorted(task.capabilities)))
                if architecture_id == "portfolio-preserving-structured"
                else None
            ),
        )
    return replace(task, capabilities=MappingProxyType(capabilities))


def run_architecture(
    task: TaskInstance,
    architecture_id: str,
    adapter: AgentAdapter,
) -> ArchitectureRun:
    agent_ids = tuple(sorted(task.capabilities))
    if architecture_id not in ARCHITECTURES:
        raise ValueError(f"unknown architecture: {architecture_id}")
    turn_count = max(
        ARCHITECTURE_TURNS[architecture_id],
        2 if task.family_id == "common-source-acquisition" else 1,
    )
    messages: tuple[tuple[str, str], ...] = ()
    turns: list[TurnRecord] = []
    errors: list[str] = []
    final_actions: dict[str, StructuredAction] = {}
    selected_sources: dict[str, str] = {}
    for round_number in range(turn_count):
        rights = information_rights(architecture_id, agent_ids, messages)
        round_task = _task_with_messages(
            task, rights, architecture_id, selected_sources
        )
        new_messages: list[tuple[str, str]] = []
        for agent_id in agent_ids:
            final_required = round_number == turn_count - 1
            prompt = compile_prompt(
                round_task,
                agent_id,
                architecture_id=architecture_id,
                rounds_remaining=max(
                    0, ARCHITECTURE_MESSAGE_ROUNDS[architecture_id] - round_number
                ),
            )
            request = AdapterRequest(
                prompt=prompt,
                manifest=adapter.manifest,
                round_number=round_number,
                action_vocabulary=task.action_vocabulary,
                source_vocabulary=task.source_vocabulary,
                final_required=final_required,
            )
            response = adapter.respond(request)
            action: StructuredAction | None = None
            validation_errors: list[str] = []
            retry_count = 0
            if response.error_class is None:
                try:
                    action = parse_action(
                        response.raw_output,
                        task_commitment=task.commitment,
                        agent_id=agent_id,
                        round_number=round_number,
                        action_vocabulary=task.action_vocabulary,
                        source_vocabulary=task.source_vocabulary,
                        final_required=final_required,
                    )
                except ValueError as first_error:
                    validation_errors.append(str(first_error))
                    retry_count = 1
                    retry_request = replace(
                        request,
                        schema_retry=True,
                        repair_errors=tuple(validation_errors),
                    )
                    response = adapter.respond(retry_request)
                    if response.error_class is None:
                        try:
                            action = parse_action(
                                response.raw_output,
                                task_commitment=task.commitment,
                                agent_id=agent_id,
                                round_number=round_number,
                                action_vocabulary=task.action_vocabulary,
                                source_vocabulary=task.source_vocabulary,
                                final_required=final_required,
                            )
                        except ValueError as second_error:
                            validation_errors.append(str(second_error))
            if response.error_class:
                validation_errors.append(response.error_class)
            if action is not None:
                if (
                    task.family_id == "common-source-acquisition"
                    and round_number == 0
                    and action.source_choice in {"common", "independent"}
                ):
                    selected_sources[agent_id] = action.source_choice
                if len(action.visible_message) > MAX_MESSAGE_CHARS:
                    validation_errors.append("message-budget")
                    action = None
                else:
                    new_messages.append((agent_id, action.visible_message))
                    if action.final:
                        final_actions[agent_id] = action
            if validation_errors and action is None:
                errors.append(f"{agent_id}:r{round_number}:{'|'.join(validation_errors)}")
            turns.append(
                TurnRecord(
                    architecture_id,
                    agent_id,
                    round_number,
                    rights[agent_id],
                    response,
                    action,
                    tuple(validation_errors),
                    retry_count,
                )
            )
        messages = tuple(new_messages)
    return ArchitectureRun(
        architecture_id,
        task.commitment,
        tuple(turns),
        tuple(final_actions[agent] for agent in sorted(final_actions)),
        tuple(errors),
    )


def empty_usage() -> Usage:
    return Usage()
