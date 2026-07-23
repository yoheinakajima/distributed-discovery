"""Method B verification, independent of Method A result classification."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from decimal import Decimal
from fractions import Fraction
from itertools import combinations, product
from math import comb

from distributed_discovery.benchmark.agents_v1.batch import BatchPlan
from distributed_discovery.benchmark.agents_v1.custody import (
    ToyCustodyBundle,
    domain_commitment,
    unseal_public_toy,
    verify_output_lock,
)
from distributed_discovery.benchmark.agents_v1.generation import instance_commitment
from distributed_discovery.benchmark.agents_v1.models import (
    VERSIONS,
    BaselineObject,
    TaskInstance,
)
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
    target = str(task.primitive_state["target"])
    parameters = _mapping(task.primitive_state["parameters"])
    if task.family_id == "threshold-team-formation":
        discovery = Fraction(
            int(Counter(selected)[target] >= int(str(parameters["threshold"]))),
            1,
        )
    else:
        discovery = Fraction(int(target in distinct), 1)
    planner = Fraction(task.baseline.planner_discovery)
    private = Fraction(task.baseline.private_discovery)
    invalid_count = len(task.capabilities) - len(final_records)
    source_counts = Counter(
        record.source_choice for record in final_records if record.source_choice != "none"
    )
    source_total = sum(source_counts.values())
    capacity = min(len(task.capabilities), len(task.action_vocabulary))
    isolated_coverage = Fraction(
        isolated_distinct_actions if isolated_distinct_actions is not None else len(distinct),
        capacity,
    )
    coverage = Fraction(len(distinct), capacity)
    return {
        "group_discovery": discovery,
        "distinct_action_coverage": coverage,
        "duplication": Fraction(max(0, len(selected) - len(distinct)), max(1, len(selected))),
        "planner_regret": planner - discovery,
        "private_baseline_regret": private - discovery,
        "recovery_budget_attainment": (
            Fraction(
                int(len(distinct) >= task.baseline.recovery_budget and discovery == 1),
                1,
            )
            if task.baseline.recovery_budget is not None
            else None
        ),
        "source_diversity": (
            1
            - sum(
                (Fraction(count, source_total) ** 2 for count in source_counts.values()),
                Fraction(0),
            )
            if source_total
            else Fraction(0)
        ),
        "communication_action_compression": isolated_coverage - coverage,
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
        "invalid_action_rate": Fraction(invalid_count, max(1, len(task.capabilities))),
        "protocol_compliance": Fraction(int(not run.protocol_errors), 1),
        "calls": len(run.turns) + sum(record.retry_count for record in run.turns),
        "input_tokens": sum(record.response.usage.input_tokens for record in run.turns),
        "output_tokens": sum(record.response.usage.output_tokens for record in run.turns),
        "cost_usd": sum((record.response.usage.cost_usd for record in run.turns), Decimal("0")),
    }


def verify_task(task: TaskInstance) -> tuple[str, ...]:
    errors: list[str] = []
    if task.commitment != instance_commitment(task):
        errors.append("task-commitment")
    try:
        expected = _expected_baseline(task)
    except (KeyError, ValueError):
        expected = None
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


def _mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("expected mapping")
    return value


def _sequence(value: object) -> tuple[object, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("expected sequence")
    return tuple(value)


def _expected_baseline(task: TaskInstance) -> BaselineObject:
    """Reconstruct cell comparators independently from scientific-owner formulas."""
    parameters = _mapping(task.primitive_state["parameters"])
    agents = int(str(parameters["agent_count"]))
    if task.family_id == "common-source-acquisition":
        from distributed_discovery.acquisition.common_source_analysis import (
            all_common_trap_interval,
            equilibrium_counts,
            planner_counts,
        )
        from distributed_discovery.acquisition.n_agent import discovery as acquisition_discovery

        accuracy = Fraction(str(parameters["accuracy"]))
        lower, upper = all_common_trap_interval(agents, accuracy)
        cost = {
            "below-private-threshold": lower / 2,
            "trap-interval": (lower + upper) / 2,
            "above-planner-threshold": upper + (1 - upper) / 2,
        }[str(parameters["cost_region"])]
        planner = [
            acquisition_discovery(agents, count, accuracy)
            for count in planner_counts(agents, accuracy, cost)
        ]
        equilibria = [
            acquisition_discovery(agents, count, accuracy)
            for count in equilibrium_counts(agents, accuracy, cost)
        ]
        return BaselineObject(
            str(acquisition_discovery(agents, agents, accuracy)),
            str(max(planner)),
            None,
            str(max(equilibria)),
            str(min(equilibria)),
        )
    if task.family_id == "one-reader-versus-broadcast-attention":
        from distributed_discovery.attention.model import discovery as attention_discovery

        private = Fraction(str(parameters["private_accuracy"]))
        shared = Fraction(str(parameters["shared_accuracy"]))
        values = [
            attention_discovery(agents, readers, private, shared) for readers in range(agents + 1)
        ]
        return BaselineObject(str(values[0]), str(max(values)), 1)
    if task.family_id in {
        "point-versus-shortlist-sharing",
        "consensus-collapse-versus-portfolio-recovery",
    }:
        targets = int(str(parameters["target_count"]))
        accuracy, profile = _method_b_channel_profile(targets, agents, str(parameters["channel"]))
        private = 1 - (1 - accuracy) ** agents
        budget = (
            int(str(parameters["action_budget"]))
            if "action_budget" in parameters
            else min(targets, agents)
        )
        recovery = next(
            (index + 1 for index, value in enumerate(profile) if value >= private),
            None,
        )
        return BaselineObject(str(private), str(profile[budget - 1]), recovery)
    if task.family_id == "threshold-team-formation":
        from distributed_discovery.threshold_discovery.model import (
            binomial_tail,
            planner_value,
        )
        from distributed_discovery.threshold_equilibrium.model import (
            discovery_value,
            pure_nash_occupancies,
        )

        threshold = int(str(parameters["threshold"]))
        extras = _mapping(task.primitive_state["exact_public_primitives"])
        posterior = tuple(Fraction(str(value)) for value in _sequence(extras["posterior"]))
        private = sum(
            (mass * binomial_tail(agents, mass, threshold) for mass in posterior),
            Fraction(0),
        )
        equilibria = [
            discovery_value(occupancy, posterior, threshold)
            for occupancy in pure_nash_occupancies(posterior, agents, threshold)
        ]
        return BaselineObject(
            str(private),
            str(planner_value(posterior, agents, threshold)),
            min(len(posterior), agents // threshold),
            str(max(equilibria)),
            str(min(equilibria)),
        )
    raise ValueError("unknown family")


def _method_b_channel_profile(
    targets: int,
    agents: int,
    channel_id: str,
) -> tuple[Fraction, tuple[Fraction, ...]]:
    if channel_id == "noisy-point":
        signals: tuple[object, ...] = tuple(range(targets))
        law = {
            target: {
                signal: (Fraction(1, 2) if signal == target else Fraction(1, 2 * (targets - 1)))
                for signal in signals
            }
            for target in range(targets)
        }
    else:
        signals = tuple(combinations(range(targets), 2))
        inclusion = Fraction(1) if channel_id == "guaranteed-two-shortlist" else Fraction(3, 4)
        law = {
            target: {
                signal: (
                    inclusion / (targets - 1)
                    if _signal_contains(signal, target)
                    else (1 - inclusion) / comb(targets - 1, 2)
                )
                for signal in signals
            }
            for target in range(targets)
        }
    prior = Fraction(1, targets)
    accuracy = sum(
        (max(prior * law[target][signal] for target in range(targets)) for signal in signals),
        Fraction(0),
    )
    profile = [Fraction(0) for _ in range(min(targets, agents))]
    for observations in product(signals, repeat=agents):
        weights = [
            prior * _product(law[target][signal] for signal in observations)
            for target in range(targets)
        ]
        probability = sum(weights, Fraction(0))
        if not probability:
            continue
        posterior = sorted((weight / probability for weight in weights), reverse=True)
        for index in range(len(profile)):
            profile[index] += probability * sum(posterior[: index + 1], Fraction(0))
    return accuracy, tuple(profile)


def _signal_contains(signal: object, target: int) -> bool:
    return isinstance(signal, tuple) and target in signal


def _product(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def verify_method_agreement(
    method_a: Mapping[str, object],
    task: TaskInstance,
    run: ArchitectureRun,
) -> tuple[str, ...]:
    method_b = reconstruct_metrics(task, run)
    return tuple(key for key, expected in method_b.items() if method_a.get(key) != expected)


REGISTERED_METRICS = frozenset(
    {
        "group_discovery",
        "distinct_action_coverage",
        "duplication",
        "planner_regret",
        "private_baseline_regret",
        "recovery_budget_attainment",
        "source_diversity",
        "communication_action_compression",
        "best_equilibrium_distance",
        "worst_equilibrium_distance",
        "invalid_action_rate",
        "protocol_compliance",
        "calls",
        "input_tokens",
        "output_tokens",
        "cost_usd",
    }
)


def verify_metric_vector(metrics: Mapping[str, object]) -> tuple[str, ...]:
    errors: list[str] = []
    if any("composite" in key or "ranking" in key for key in metrics):
        errors.append("composite-score")
    unknown = set(metrics) - REGISTERED_METRICS
    if unknown:
        errors.append("unregistered-metric")
    return tuple(errors)


def verify_batch_aggregation(
    plan: BatchPlan,
    *,
    observed_calls: int,
    observed_tokens: int,
    observed_cost_usd: Decimal,
) -> tuple[str, ...]:
    errors: list[str] = []
    if observed_calls > plan.calls:
        errors.append("batch-call-ceiling")
    if observed_tokens > plan.token_ceiling:
        errors.append("batch-token-ceiling")
    if observed_cost_usd > plan.maximum_exposure_usd:
        errors.append("batch-cost-ceiling")
    return tuple(errors)


def verify_exclusions(rows: tuple[Mapping[str, object], ...]) -> tuple[str, ...]:
    errors: list[str] = []
    for index, row in enumerate(rows):
        excluded = row.get("excluded")
        reason = row.get("reason")
        if excluded is True and (not isinstance(reason, str) or not reason.strip()):
            errors.append(f"exclusion-{index}-missing-reason")
        if excluded is not True and reason:
            errors.append(f"exclusion-{index}-reason-without-exclusion")
    return tuple(errors)


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
    errors.extend(f"metric-vector:{error}" for error in verify_metric_vector(method_a))
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
