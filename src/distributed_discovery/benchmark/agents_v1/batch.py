"""Offline batch/resource planner with a hard zero-spend default."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BatchPlan:
    tasks: int
    architectures: int
    models: int
    repeats: int
    rounds: int
    calls: int
    turns: int
    token_ceiling: int
    storage_bytes: int
    cost_low_usd: Decimal
    cost_base_usd: Decimal
    cost_high_usd: Decimal
    provider_model_costs: tuple[tuple[str, Decimal], ...]
    maximum_exposure_usd: Decimal
    registered_recommendation_usd: Decimal = Decimal("750")

    def serializable(self) -> dict[str, object]:
        return {
            key: str(value) if isinstance(value, Decimal) else value
            for key, value in self.__dict__.items()
        }


def plan_batch(
    *,
    tasks: int,
    architectures: int,
    models: int,
    repeats: int,
    agents_per_task: int = 1,
    total_agent_slots: int | None = None,
    rounds: int = 2,
    tokens_per_turn: int = 512,
    bytes_per_turn: int = 4096,
    provider_model_costs: tuple[tuple[str, Decimal], ...] = (),
    authorized_max_spend_usd: Decimal = Decimal("0"),
) -> BatchPlan:
    if min(tasks, architectures, models, repeats, rounds, agents_per_task) < 1:
        raise ValueError("batch dimensions must be positive")
    agent_slots = total_agent_slots if total_agent_slots is not None else tasks * agents_per_task
    if agent_slots < 1:
        raise ValueError("total agent slots must be positive")
    turns = agent_slots * architectures * models * repeats * rounds
    calls = turns
    token_ceiling = turns * tokens_per_turn
    maximum = sum((cost for _, cost in provider_model_costs), Decimal("0"))
    if maximum > authorized_max_spend_usd:
        raise PermissionError(
            f"projected ${maximum} exceeds authorized ${authorized_max_spend_usd}"
        )
    return BatchPlan(
        tasks,
        architectures,
        models,
        repeats,
        rounds,
        calls,
        turns,
        token_ceiling,
        turns * bytes_per_turn,
        maximum * Decimal("0.75"),
        maximum,
        maximum * Decimal("1.25"),
        provider_model_costs,
        maximum,
    )
