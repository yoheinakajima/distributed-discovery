"""Method B verification, independent of Method A result classification."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from fractions import Fraction

from distributed_discovery.benchmark.agents_v1.custody import (
    ToyCustodyBundle,
    domain_commitment,
    unseal_public_toy,
    verify_output_lock,
)
from distributed_discovery.benchmark.agents_v1.generation import (
    FAMILY_BASELINES,
    instance_commitment,
)
from distributed_discovery.benchmark.agents_v1.models import VERSIONS, TaskInstance
from distributed_discovery.benchmark.agents_v1.orchestration import ArchitectureRun
from distributed_discovery.benchmark.agents_v1.traces import verify_trace_hashes


def reconstruct_metrics(
    task: TaskInstance,
    run: ArchitectureRun,
    *,
    isolated_distinct_actions: int | None = None,
) -> dict[str, object]:
    """Recompute metrics from primitive task/action records without importing Method A."""
    final_records = run.final_actions
    selected = [item for record in final_records for item in record.actions]
    distinct = set(selected)
    discovery = Fraction(int(str(task.primitive_state["target"]) in distinct), 1)
    planner = Fraction(task.baseline.planner_discovery)
    private = Fraction(task.baseline.private_discovery)
    invalid_count = sum(record.action is None for record in run.turns)
    sources = {record.source_choice for record in final_records if record.source_choice != "none"}
    denominator = (
        isolated_distinct_actions if isolated_distinct_actions is not None else len(distinct)
    )
    return {
        "group_discovery": discovery,
        "distinct_action_coverage": Fraction(len(distinct), len(task.action_vocabulary)),
        "duplication": Fraction(max(0, len(selected) - len(distinct)), max(1, len(selected))),
        "planner_regret": planner - discovery,
        "private_baseline_regret": private - discovery,
        "recovery_budget_attainment": (
            Fraction(int(len(distinct) >= task.baseline.recovery_budget), 1)
            if task.baseline.recovery_budget is not None
            else None
        ),
        "source_diversity": Fraction(
            len(sources), max(1, len(task.source_vocabulary) - 1)
        ),
        "communication_action_compression": Fraction(
            max(0, denominator - len(distinct)), max(1, denominator)
        ),
        "best_equilibrium_distance": (
            abs(Fraction(task.baseline.best_equilibrium) - discovery)
            if task.baseline.best_equilibrium is not None
            else None
        ),
        "worst_equilibrium_distance": (
            abs(Fraction(task.baseline.worst_equilibrium) - discovery)
            if task.baseline.worst_equilibrium is not None
            else None
        ),
        "invalid_action_rate": Fraction(invalid_count, max(1, len(run.turns))),
        "protocol_compliance": Fraction(int(not run.protocol_errors), 1),
        "calls": len(run.turns) + sum(record.retry_count for record in run.turns),
        "input_tokens": sum(record.response.usage.input_tokens for record in run.turns),
        "output_tokens": sum(record.response.usage.output_tokens for record in run.turns),
        "cost_usd": sum(
            (record.response.usage.cost_usd for record in run.turns), Decimal("0")
        ),
    }


def verify_task(task: TaskInstance) -> tuple[str, ...]:
    errors: list[str] = []
    if task.commitment != instance_commitment(task):
        errors.append("task-commitment")
    expected = FAMILY_BASELINES.get(task.family_id)
    if expected is None or task.baseline != expected:
        errors.append("baseline")
    if task.visible_record()["versions"] != dict(VERSIONS):
        errors.append("version-manifest")
    for agent_id, capability in task.capabilities.items():
        if agent_id != capability.agent_id:
            errors.append("information-rights")
        if "target" in capability.public_state or "primitive_state" in capability.public_state:
            errors.append("information-rights")
    return tuple(sorted(set(errors)))


def verify_method_agreement(
    method_a: Mapping[str, object],
    task: TaskInstance,
    run: ArchitectureRun,
) -> tuple[str, ...]:
    method_b = reconstruct_metrics(task, run)
    return tuple(
        key for key, expected in method_b.items() if method_a.get(key) != expected
    )


def verify_custody(
    bundle: ToyCustodyBundle,
    *,
    task_batch: object,
    output: object,
) -> tuple[str, ...]:
    errors: list[str] = []
    try:
        unsealed = unseal_public_toy(bundle)
    except (ValueError, PermissionError):
        return ("custody-unseal",)
    if bundle.manifest.get("task_batch_commitment") != domain_commitment(
        "agents-v1/task-batch", task_batch
    ):
        errors.append("task-batch-commitment")
    if not verify_output_lock(bundle, output):
        errors.append("output-lock")
    if not unsealed:
        errors.append("empty-unseal")
    return tuple(errors)


def verify_offline_bundle(
    *,
    task: TaskInstance,
    run: ArchitectureRun,
    method_a: Mapping[str, object],
    raw_trace: Mapping[str, object],
    custody: ToyCustodyBundle,
    task_batch: object,
    output: object,
    provider_calls: int,
    model_invocations: int,
    external_cost_usd: Decimal,
    network_enabled: bool,
) -> tuple[str, ...]:
    errors = list(verify_task(task))
    errors.extend(f"metric:{key}" for key in verify_method_agreement(method_a, task, run))
    if not verify_trace_hashes(raw_trace):
        errors.append("trace-hash")
    errors.extend(verify_custody(custody, task_batch=task_batch, output=output))
    if provider_calls != 0:
        errors.append("provider-calls")
    if model_invocations != 0:
        errors.append("model-invocations")
    if external_cost_usd != Decimal("0"):
        errors.append("external-cost")
    if network_enabled:
        errors.append("network")
    return tuple(sorted(set(errors)))
