"""Method A exact-rational evaluator for structured team actions."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from distributed_discovery.benchmark.agents_v1.models import TaskInstance
from distributed_discovery.benchmark.agents_v1.orchestration import ArchitectureRun


@dataclass(frozen=True)
class Evaluation:
    group_discovery: Fraction
    distinct_action_coverage: Fraction
    duplication: Fraction
    planner_regret: Fraction
    private_baseline_regret: Fraction
    recovery_budget_attainment: Fraction | None
    source_diversity: Fraction
    communication_action_compression: Fraction
    best_equilibrium_distance: Fraction | None
    worst_equilibrium_distance: Fraction | None
    invalid_action_rate: Fraction
    protocol_compliance: Fraction
    calls: int
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal

    def serializable(self) -> dict[str, object]:
        return {
            key: (str(value) if isinstance(value, (Fraction, Decimal)) else value)
            for key, value in self.__dict__.items()
        }


def evaluate_run(
    task: TaskInstance,
    run: ArchitectureRun,
    *,
    isolated_distinct_actions: int | None = None,
) -> Evaluation:
    finals = run.final_actions
    flat = tuple(item for action in finals for item in action.actions)
    distinct = frozenset(flat)
    target = str(task.primitive_state["target"])
    if task.family_id == "threshold-team-formation":
        parameters = task.primitive_state["parameters"]
        if not isinstance(parameters, Mapping):
            raise ValueError("task parameters must be a mapping")
        threshold = int(str(parameters["threshold"]))
        discovery = Fraction(int(Counter(flat)[target] >= threshold), 1)
    else:
        discovery = Fraction(int(target in distinct), 1)
    action_capacity = min(len(task.capabilities), len(task.action_vocabulary))
    coverage = Fraction(len(distinct), action_capacity)
    duplication = Fraction(max(0, len(flat) - len(distinct)), max(1, len(flat)))
    planner = Fraction(task.baseline.planner_discovery)
    private = Fraction(task.baseline.private_discovery)
    recovery = (
        Fraction(
            int(len(distinct) >= task.baseline.recovery_budget and discovery == 1),
            1,
        )
        if task.baseline.recovery_budget is not None
        else None
    )
    source_counts = Counter(
        action.source_choice for action in finals if action.source_choice != "none"
    )
    source_total = sum(source_counts.values())
    source_diversity = (
        1
        - sum(
            (Fraction(count, source_total) ** 2 for count in source_counts.values()),
            Fraction(0),
        )
        if source_total
        else Fraction(0)
    )
    isolated_coverage = Fraction(
        isolated_distinct_actions if isolated_distinct_actions is not None else len(distinct),
        action_capacity,
    )
    compression = isolated_coverage - coverage
    invalid = len(task.capabilities) - len(finals)
    calls = len(run.turns) + sum(record.retry_count for record in run.turns)
    input_tokens = sum(record.response.usage.input_tokens for record in run.turns)
    output_tokens = sum(record.response.usage.output_tokens for record in run.turns)
    cost = sum((record.response.usage.cost_usd for record in run.turns), Decimal("0"))
    return Evaluation(
        group_discovery=discovery,
        distinct_action_coverage=coverage,
        duplication=duplication,
        planner_regret=planner - discovery,
        private_baseline_regret=private - discovery,
        recovery_budget_attainment=recovery,
        source_diversity=source_diversity,
        communication_action_compression=compression,
        best_equilibrium_distance=(
            abs(Fraction(task.baseline.best_equilibrium) - discovery)
            if task.baseline.best_equilibrium is not None
            else None
        ),
        worst_equilibrium_distance=(
            abs(Fraction(task.baseline.worst_equilibrium) - discovery)
            if task.baseline.worst_equilibrium is not None
            else None
        ),
        invalid_action_rate=Fraction(invalid, max(1, len(task.capabilities))),
        protocol_compliance=Fraction(int(not run.protocol_errors), 1),
        calls=calls,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost,
    )
