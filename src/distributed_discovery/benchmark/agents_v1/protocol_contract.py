"""Independent Method C verification of the registered agent protocol contract.

This module deliberately imports neither Method A nor Method B. It reconstructs
the action, information, round, message, source, and metric-range rules from the
authoritative Agents v1 architecture and protocol registrations.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from distributed_discovery.benchmark.agents_v1.models import StructuredAction, TaskInstance
from distributed_discovery.benchmark.agents_v1.orchestration import ArchitectureRun, TurnRecord

REGISTERED_ARCHITECTURE_TURNS = {
    "isolated-private-agents": 1,
    "full-broadcast-shared-transcript": 2,
    "designated-reader-selective-sharing": 2,
    "pooled-consensus": 2,
    "portfolio-preserving-structured": 2,
    "provider-native-smoke": 1,
}
MAX_PROPOSAL_ACTIONS = 6
MAX_VISIBLE_MESSAGE_CHARS = 1024

UNIT_INTERVAL_METRICS = frozenset(
    {
        "group_discovery",
        "distinct_action_coverage",
        "duplication",
        "recovery_budget_attainment",
        "source_diversity",
        "best_equilibrium_distance",
        "worst_equilibrium_distance",
        "invalid_action_rate",
        "protocol_compliance",
    }
)
SIGNED_UNIT_INTERVAL_METRICS = frozenset(
    {
        "planner_regret",
        "private_baseline_regret",
        "communication_action_compression",
    }
)
NONNEGATIVE_METRICS = frozenset(
    {
        "calls",
        "input_tokens",
        "output_tokens",
        "cost_usd",
    }
)
OPTIONAL_UNIT_INTERVAL_METRICS = frozenset(
    {
        "recovery_budget_attainment",
        "best_equilibrium_distance",
        "worst_equilibrium_distance",
    }
)


@dataclass(frozen=True)
class ProtocolContractVerification:
    """Method C result emitted before performance interpretation."""

    errors: tuple[str, ...]
    required_final_records: int
    observed_final_records: int
    valid_final_records: int
    invalid_final_records: int

    @property
    def compliant(self) -> bool:
        return not self.errors


def _expected_turn_count(task: TaskInstance, architecture_id: str) -> int:
    if architecture_id not in REGISTERED_ARCHITECTURE_TURNS:
        raise ValueError("unregistered architecture")
    return max(
        REGISTERED_ARCHITECTURE_TURNS[architecture_id],
        2 if task.family_id == "common-source-acquisition" else 1,
    )


def _portfolio_slot(agent_id: str, agent_ids: tuple[str, ...]) -> str:
    return f"SLOT-{agent_ids.index(agent_id) % 2 + 1}"


def _information_rights(
    architecture_id: str,
    agent_ids: tuple[str, ...],
    prior_messages: tuple[tuple[str, str], ...],
) -> Mapping[str, tuple[str, ...]]:
    if architecture_id in {"isolated-private-agents", "provider-native-smoke"}:
        return {agent: () for agent in agent_ids}
    if architecture_id == "full-broadcast-shared-transcript":
        messages = tuple(message for _, message in prior_messages)
        return {agent: messages for agent in agent_ids}
    if architecture_id == "designated-reader-selective-sharing":
        reader = agent_ids[0]
        messages = tuple(message for source, message in prior_messages if source == reader)
        return {agent: messages for agent in agent_ids}
    if architecture_id == "pooled-consensus":
        messages = tuple(sorted({message for _, message in prior_messages}))
        return {agent: messages for agent in agent_ids}
    if architecture_id == "portfolio-preserving-structured":
        return {
            agent: tuple(
                message
                for source, message in prior_messages
                if source == agent
                or _portfolio_slot(source, agent_ids) == _portfolio_slot(agent, agent_ids)
            )
            for agent in agent_ids
        }
    raise ValueError("unregistered architecture")


def _action_errors(
    action: StructuredAction,
    *,
    task: TaskInstance,
    turn: TurnRecord,
    final_required: bool,
) -> tuple[str, ...]:
    prefix = f"{turn.agent_id}:r{turn.round_number}"
    errors: list[str] = []
    if action.task_commitment != task.commitment:
        errors.append(f"{prefix}:task-commitment")
    if action.agent_id != turn.agent_id:
        errors.append(f"{prefix}:agent-identity")
    if action.round_number != turn.round_number:
        errors.append(f"{prefix}:round-identity")
    if action.final is not final_required:
        errors.append(f"{prefix}:final-flag")
    count = len(action.actions)
    if count < 1 or count > MAX_PROPOSAL_ACTIONS:
        errors.append(f"{prefix}:action-count")
    if final_required and count != 1:
        errors.append(f"{prefix}:final-action-count")
    if len(set(action.actions)) != count:
        errors.append(f"{prefix}:duplicate-action")
    if any(item not in task.action_vocabulary for item in action.actions):
        errors.append(f"{prefix}:action-vocabulary")
    if action.source_choice not in task.source_vocabulary:
        errors.append(f"{prefix}:source-choice-rights")
    if len(action.visible_message) > MAX_VISIBLE_MESSAGE_CHARS:
        errors.append(f"{prefix}:message-budget")
    if turn.response.declared_tool_calls:
        errors.append(f"{prefix}:tool-rights")
    return tuple(errors)


def verify_protocol_contract(
    task: TaskInstance,
    run: ArchitectureRun,
) -> ProtocolContractVerification:
    """Verify architecture and action rights without Method A/B classifications."""
    errors: list[str] = []
    agent_ids = (
        tuple(sorted({turn.agent_id for turn in run.turns}))
        if run.architecture_id == "provider-native-smoke"
        else tuple(sorted(task.capabilities))
    )
    agent_set = frozenset(agent_ids)
    try:
        expected_turns = _expected_turn_count(task, run.architecture_id)
    except ValueError:
        return ProtocolContractVerification(
            ("architecture-unregistered",),
            len(agent_ids),
            len(run.final_actions),
            0,
            len(run.final_actions),
        )
    if run.task_commitment != task.commitment:
        errors.append("run-task-commitment")

    indexed: dict[tuple[int, str], list[TurnRecord]] = {}
    for turn in run.turns:
        indexed.setdefault((turn.round_number, turn.agent_id), []).append(turn)
        if turn.architecture_id != run.architecture_id:
            errors.append(f"{turn.agent_id}:r{turn.round_number}:architecture-identity")
        if turn.agent_id not in agent_set:
            errors.append(f"{turn.agent_id}:r{turn.round_number}:undeclared-agent")
        if turn.round_number < 0 or turn.round_number >= expected_turns:
            errors.append(f"{turn.agent_id}:r{turn.round_number}:round-limit")

    prior_messages: tuple[tuple[str, str], ...] = ()
    observed_final_records: list[StructuredAction] = []
    valid_final_records: list[StructuredAction] = []
    for round_number in range(expected_turns):
        rights = _information_rights(run.architecture_id, agent_ids, prior_messages)
        next_messages: list[tuple[str, str]] = []
        final_required = round_number == expected_turns - 1
        for agent_id in agent_ids:
            turns = indexed.get((round_number, agent_id), [])
            if len(turns) != 1:
                errors.append(
                    f"{agent_id}:r{round_number}:final-record-count"
                    if final_required
                    else f"{agent_id}:r{round_number}:turn-record-count"
                )
                continue
            turn = turns[0]
            if turn.visible_inputs != rights[agent_id]:
                errors.append(f"{agent_id}:r{round_number}:information-rights")
            action = turn.action
            if action is None:
                errors.append(
                    f"{agent_id}:r{round_number}:missing-final-action"
                    if final_required
                    else f"{agent_id}:r{round_number}:missing-proposal"
                )
                continue
            action_errors = _action_errors(
                action,
                task=task,
                turn=turn,
                final_required=final_required,
            )
            errors.extend(action_errors)
            if action.final:
                observed_final_records.append(action)
            if final_required and not action_errors:
                valid_final_records.append(action)
            if len(action.visible_message) <= MAX_VISIBLE_MESSAGE_CHARS:
                next_messages.append((agent_id, action.visible_message))
        prior_messages = tuple(next_messages)

    final_counts = Counter(action.agent_id for action in observed_final_records)
    for agent_id in agent_ids:
        if final_counts[agent_id] != 1:
            errors.append(f"{agent_id}:final-record-count")
    if any(agent_id not in agent_set for agent_id in final_counts):
        errors.append("undeclared-agent-final-record")

    listed_counts = Counter(action.agent_id for action in run.final_actions)
    if listed_counts != final_counts:
        errors.append("final-action-extraction")
    for action in run.final_actions:
        if not action.final:
            errors.append(f"{action.agent_id}:nonfinal-in-final-actions")

    action_capacity = min(len(agent_ids), len(task.action_vocabulary))
    if action_capacity <= 0:
        errors.append("action-capacity")
    if (
        run.architecture_id != "provider-native-smoke"
        and task.baseline.recovery_budget is not None
        and task.baseline.recovery_budget > action_capacity
    ):
        errors.append("comparator-action-capacity")
    if run.protocol_errors:
        errors.append("recorded-protocol-error")

    invalid_final_records = max(
        len(agent_ids) - len(valid_final_records),
        len(observed_final_records) - len(valid_final_records),
    )
    return ProtocolContractVerification(
        tuple(sorted(set(errors))),
        len(agent_ids),
        len(observed_final_records),
        len(valid_final_records),
        invalid_final_records,
    )


def verify_metric_ranges(metrics: Mapping[str, object]) -> tuple[str, ...]:
    """Reject values outside registered exact metric ranges."""
    errors: list[str] = []
    for name in UNIT_INTERVAL_METRICS:
        value = metrics.get(name)
        if value is None and name in OPTIONAL_UNIT_INTERVAL_METRICS:
            continue
        if not _between(value, Fraction(0), Fraction(1)):
            errors.append(f"{name}:range")
    for name in SIGNED_UNIT_INTERVAL_METRICS:
        if not _between(metrics.get(name), Fraction(-1), Fraction(1)):
            errors.append(f"{name}:range")
    for name in NONNEGATIVE_METRICS:
        value = metrics.get(name)
        if not _nonnegative(value):
            errors.append(f"{name}:range")
    return tuple(sorted(errors))


def _between(value: object, lower: Fraction, upper: Fraction) -> bool:
    if isinstance(value, Decimal):
        return (
            Decimal(lower.numerator) / Decimal(lower.denominator)
            <= value
            <= (Decimal(upper.numerator) / Decimal(upper.denominator))
        )
    rational = _as_fraction(value)
    if rational is None:
        return False
    return lower <= rational <= upper


def _nonnegative(value: object) -> bool:
    if isinstance(value, Decimal):
        return value >= 0
    rational = _as_fraction(value)
    if rational is None:
        return False
    return rational >= 0


def _as_fraction(value: object) -> Fraction | None:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, (int, float, str)):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError):
            return None
    return None


def final_action_cardinalities(
    events: Sequence[Mapping[str, object]],
) -> tuple[tuple[str, int, int], ...]:
    """Extract public-safe ``(agent, round, count)`` records from trace events."""
    records: list[tuple[str, int, int]] = []
    for event in events:
        action = event.get("structured_action")
        if not isinstance(action, Mapping) or action.get("final") is not True:
            continue
        values = action.get("actions")
        count = (
            len(values)
            if isinstance(values, Sequence) and not isinstance(values, (str, bytes))
            else 0
        )
        records.append(
            (
                str(action.get("agent_id", event.get("agent_id", ""))),
                int(str(action.get("round", event.get("round", -1)))),
                count,
            )
        )
    return tuple(records)
