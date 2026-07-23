"""Offline-only campaign registration helpers.

These helpers create public allocation metadata and validate inactive campaign
authorization. They cannot generate tasks, invoke models, or authorize spend.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from distributed_discovery.benchmark.agents_v1.generation import canonical_cells

FAMILY_ORDER = (
    "common-source-acquisition",
    "one-reader-versus-broadcast-attention",
    "point-versus-shortlist-sharing",
    "consensus-collapse-versus-portfolio-recovery",
    "threshold-team-formation",
)
EXTRA_COUNTS = {
    "common-source-acquisition": 13,
    "one-reader-versus-broadcast-attention": 13,
    "point-versus-shortlist-sharing": 10,
    "consensus-collapse-versus-portfolio-recovery": 10,
    "threshold-team-formation": 16,
}
ISOMORPHS = (
    ("target-A", "agent-A"),
    ("target-A", "agent-B"),
    ("target-B", "agent-A"),
    ("target-B", "agent-B"),
)


def _priority(cell: Any) -> tuple[int, int]:
    parameters = cell.parameters
    family = cell.family_id
    if family == "common-source-acquisition":
        region = str(parameters["cost_region"])
        return (
            {"trap-interval": 0, "below-private-threshold": 1, "above-planner-threshold": 2}[
                region
            ],
            cell.cell_index,
        )
    if family == "one-reader-versus-broadcast-attention":
        tied = parameters["private_accuracy"] == parameters["shared_accuracy"]
        return (0 if tied else 1, cell.cell_index)
    if family == "point-versus-shortlist-sharing":
        transition = int(str(parameters["shared_block_size"])) in (
            1,
            int(str(parameters["agent_count"])),
        )
        return (0 if transition else 1, cell.cell_index)
    if family == "consensus-collapse-versus-portfolio-recovery":
        budget = int(str(parameters["action_budget"]))
        agents = int(str(parameters["agent_count"]))
        return (0 if budget in (1, agents) else 1, cell.cell_index)
    profile = str(parameters["posterior_profile"])
    return ({"tied": 0, "diffuse": 1, "strict": 2}[profile], cell.cell_index)


def _boundary_category(cell: Any) -> str:
    parameters = cell.parameters
    family = cell.family_id
    if family == "common-source-acquisition":
        region = str(parameters["cost_region"])
        return (
            "trap-interval" if region == "trap-interval" else "private-planner-threshold-boundary"
        )
    if family == "one-reader-versus-broadcast-attention":
        return (
            "equality-tie-case"
            if parameters["private_accuracy"] == parameters["shared_accuracy"]
            else "private-planner-threshold-boundary"
        )
    if family == "point-versus-shortlist-sharing":
        return (
            "same-accuracy-opposite-sign"
            if str(parameters["channel"]) != "noisy-two-shortlist"
            else "shared-block-transition-boundary"
        )
    if family == "consensus-collapse-versus-portfolio-recovery":
        return (
            "selected-every-equilibrium-limitation"
            if str(parameters["channel"]) == "noisy-point"
            else "recovery-budget-equality-boundary"
        )
    profile = str(parameters["posterior_profile"])
    return (
        "strict-tied-diffuse-threshold-posterior"
        if profile in {"tied", "diffuse"}
        else "viable-team-crowding-boundary"
    )


def build_base_allocation() -> dict[str, object]:
    """Build the deterministic public 200-slot base allocation."""
    by_family: dict[str, list[Any]] = defaultdict(list)
    for cell in canonical_cells():
        by_family[cell.family_id].append(cell)

    family_rows: dict[str, list[tuple[Any, str, str]]] = {}
    for family in FAMILY_ORDER:
        cells = by_family[family]
        rows = [
            (cell, "canonical-coverage", "cover every canonical generator cell") for cell in cells
        ]
        priorities = sorted(cells, key=_priority)[: EXTRA_COUNTS[family]]
        rows.extend(
            (
                cell,
                _boundary_category(cell),
                "predeclared boundary-priority repeat",
            )
            for cell in priorities
        )
        if len(rows) != 40:
            raise AssertionError(f"{family} allocation must contain 40 slots")
        family_rows[family] = rows

    slots: list[dict[str, object]] = []
    slot_number = 0
    for batch in range(1, 5):
        for family in FAMILY_ORDER:
            for cell, category, reason in family_rows[family][(batch - 1) * 10 : batch * 10]:
                target_class, agent_class = ISOMORPHS[slot_number % len(ISOMORPHS)]
                slot_number += 1
                slots.append(
                    {
                        "slot_id": f"BASE-SLOT-{slot_number:03d}",
                        "batch_id": f"BASE-BATCH-{batch}",
                        "family_id": family,
                        "cell_id": cell.cell_id,
                        "cell_index": cell.cell_index,
                        "boundary_category": category,
                        "target_relabeling_class": target_class,
                        "agent_relabeling_class": agent_class,
                        "reason": reason,
                    }
                )

    result: dict[str, object] = {
        "schema_version": "agents-base-campaign-allocation-v1",
        "status": "registered-public-metadata-no-private-instances",
        "selected_for_next_execution": False,
        "blocked_reason": "local-open-model infeasible on audited host",
        "allocation_algorithm": (
            "cover each canonical cell once; append family-specific deterministic "
            "boundary priorities; split each 40-slot family into four ordered "
            "10-slot batch blocks; cycle four isomorphism classes globally"
        ),
        "counts": {
            "slots": 200,
            "batches": 4,
            "slots_per_batch": 50,
            "families": 5,
            "slots_per_family": 40,
            "canonical_cells_covered": 138,
            "boundary_priority_repeats": 62,
            "private_instances_generated": 0,
        },
        "slots": slots,
    }
    validate_base_allocation(result)
    return result


def validate_base_allocation(document: Mapping[str, object]) -> None:
    """Validate the allocation invariants without generating a task."""
    raw_slots = document.get("slots")
    if not isinstance(raw_slots, Sequence) or isinstance(raw_slots, (str, bytes)):
        raise ValueError("allocation slots must be an array")
    slots = [slot for slot in raw_slots if isinstance(slot, Mapping)]
    if len(slots) != 200 or len(slots) != len(raw_slots):
        raise ValueError("allocation must contain exactly 200 object slots")
    if len({str(slot["slot_id"]) for slot in slots}) != 200:
        raise ValueError("allocation slot IDs must be unique")
    family_counts = Counter(str(slot["family_id"]) for slot in slots)
    if family_counts != Counter({family: 40 for family in FAMILY_ORDER}):
        raise ValueError("allocation must contain 40 slots per family")
    batch_counts = Counter(str(slot["batch_id"]) for slot in slots)
    if batch_counts != Counter({f"BASE-BATCH-{index}": 50 for index in range(1, 5)}):
        raise ValueError("allocation must contain four 50-slot batches")
    for batch in batch_counts:
        within = Counter(str(slot["family_id"]) for slot in slots if str(slot["batch_id"]) == batch)
        if within != Counter({family: 10 for family in FAMILY_ORDER}):
            raise ValueError("every batch must contain ten slots per family")
    canonical = {cell.cell_id for cell in canonical_cells()}
    covered = {str(slot["cell_id"]) for slot in slots}
    if covered != canonical:
        raise ValueError("allocation must cover every canonical cell exactly or repeatedly")
    priorities = sum(slot["boundary_category"] != "canonical-coverage" for slot in slots)
    if priorities != 62:
        raise ValueError("allocation must contain exactly 62 priority repeats")
    isomorph_counts = Counter(
        (str(slot["target_relabeling_class"]), str(slot["agent_relabeling_class"]))
        for slot in slots
    )
    if set(isomorph_counts.values()) != {50}:
        raise ValueError("four isomorphism classes must each receive 50 slots")


def validate_inactive_authorization(document: Mapping[str, object]) -> None:
    """Reject any authorization that would permit execution or positive spend."""
    if document.get("authorization_status") != "pending-owner-decision":
        raise ValueError("authorization must remain pending-owner-decision")
    if document.get("execution_allowed") is not False:
        raise ValueError("execution must remain disabled")
    spend_cap = document.get("external_spend_cap_usd")
    if not isinstance(spend_cap, (int, float)) or float(spend_cap) != 0:
        raise ValueError("inactive authorization must have zero spend cap")
    provider_caps = document.get("provider_spend_caps_usd")
    if not isinstance(provider_caps, Mapping) or any(
        not isinstance(value, (int, float)) or float(value) != 0 for value in provider_caps.values()
    ):
        raise ValueError("inactive provider caps must all be zero")
    if document.get("owner_attestation") is not None:
        raise ValueError("inactive authorization cannot contain an owner attestation")
