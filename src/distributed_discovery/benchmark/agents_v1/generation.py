"""Deterministic public generation for the five registered task families."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from itertools import product
from types import MappingProxyType

from distributed_discovery.benchmark.agents_v1.models import (
    BaselineObject,
    CapabilityView,
    GeneratorCell,
    TaskInstance,
    canonical_json,
    sha256_hex,
)

FAMILY_STATE_COUNTS = {
    "common-source-acquisition": 3402,
    "one-reader-versus-broadcast-attention": 9477,
    "point-versus-shortlist-sharing": 7547,
    "consensus-collapse-versus-portfolio-recovery": 7547,
    "threshold-team-formation": 30972,
}

FAMILY_BASELINES = {
    "common-source-acquisition": BaselineObject("8/9", "65535/65536", None),
    "one-reader-versus-broadcast-attention": BaselineObject("15/16", "31/32", 1),
    "point-versus-shortlist-sharing": BaselineObject("7/8", "17/18", 2),
    "consensus-collapse-versus-portfolio-recovery": BaselineObject(
        "7/8", "1", 2, "1", "3/4"
    ),
    "threshold-team-formation": BaselineObject(
        "194017/390625",
        "223779310319051/333709716796875",
        2,
        "1",
        "0",
    ),
}


def _cells(
    family: str, rows: Iterable[dict[str, object]], state_count: int
) -> list[GeneratorCell]:
    material = list(rows)
    quotient, remainder = divmod(state_count, len(material))
    return [
        GeneratorCell(
            family,
            index,
            MappingProxyType(parameters),
            quotient + (1 if index <= remainder else 0),
        )
        for index, parameters in enumerate(material, start=1)
    ]


def canonical_cells() -> tuple[GeneratorCell, ...]:
    """Return the complete 138-cell registered generator domain."""
    acquisition = (
        {
            "agent_count": agents,
            "accuracy": accuracy,
            "cost_region": cost,
            "target_count": 3,
        }
        for agents, accuracy, cost in product(
            (2, 3, 4), ("1/2", "2/3", "3/4"), ("below", "trap", "above")
        )
    )
    attention = (
        {
            "agent_count": agents,
            "private_accuracy": private,
            "shared_accuracy": shared,
            "target_count": 3,
        }
        for agents, private, shared in product(
            (2, 3, 4), ("1/2", "2/3", "3/4"), ("1/2", "2/3", "3/4")
        )
    )
    sharing = (
        {
            "target_count": targets,
            "agent_count": agents,
            "channel": channel,
            "shared_block_size": block,
        }
        for targets, agents, channel in product(
            (3, 4), (2, 3), ("noisy-point", "guaranteed-two-shortlist", "noisy-two-shortlist")
        )
        for block in range(1, agents + 1)
    )
    recovery = (
        {
            "target_count": targets,
            "agent_count": agents,
            "channel": channel,
            "action_budget": budget,
        }
        for targets, agents, channel in product(
            (3, 4), (2, 3), ("noisy-point", "guaranteed-two-shortlist", "noisy-two-shortlist")
        )
        for budget in range(1, min(targets, agents) + 1)
    )
    threshold = (
        {
            "target_count": targets,
            "agent_count": agents,
            "threshold": tau,
            "posterior_profile": posterior,
        }
        for targets, agents, tau, posterior in product(
            (3, 4), (4, 6), (2, 3), ("strict", "tied", "diffuse")
        )
    )
    rows = (
        _cells("common-source-acquisition", acquisition, 3402)
        + _cells("one-reader-versus-broadcast-attention", attention, 9477)
        + _cells("point-versus-shortlist-sharing", sharing, 7547)
        + _cells("consensus-collapse-versus-portfolio-recovery", recovery, 7547)
        + _cells("threshold-team-formation", threshold, 30972)
    )
    if len(rows) != 138 or sum(row.primitive_labeled_states for row in rows) != 58945:
        raise AssertionError("registered generator counts changed")
    return tuple(rows)


def _permutation(labels: tuple[str, ...], variant: int) -> tuple[str, ...]:
    if variant % 2 == 0 or len(labels) < 2:
        return labels
    return (labels[1], labels[0], *labels[2:])


def generate_instance(
    cell: GeneratorCell,
    *,
    variant: int,
    public_fixture: bool,
    material: str = "public-toy-material-v1",
    hidden_labels: bool = False,
    authorization: object | None = None,
    custody_context: object | None = None,
) -> TaskInstance:
    """Generate one deterministic instance; private generation fails closed."""
    if variant not in range(4):
        raise ValueError("variant must be in 0..3")
    if not public_fixture and (authorization is None or custody_context is None):
        raise PermissionError(
            "private generation requires future authorization and custody context"
        )
    parameters = dict(cell.parameters)
    target_count = int(str(parameters["target_count"]))
    agent_count = int(str(parameters["agent_count"]))
    canonical_targets = tuple(f"TARGET-{chr(65 + index)}" for index in range(target_count))
    targets = _permutation(canonical_targets, variant)
    agent_ids = tuple(f"AGENT-{index:02d}" for index in range(1, agent_count + 1))
    if variant >= 2:
        agent_ids = tuple(reversed(agent_ids))
    material_offset = int(sha256_hex(canonical_json(material))[:8], 16)
    target = targets[(cell.cell_index + material_offset) % len(targets)]
    capabilities: dict[str, CapabilityView] = {}
    for index, agent_id in enumerate(agent_ids):
        observed = targets[(cell.cell_index + index + variant + material_offset) % len(targets)]
        visible_observation = (
            f"HIDDEN-LABEL-{(index + variant) % target_count + 1}"
            if hidden_labels
            else observed.replace("TARGET-", "CLUE-")
        )
        capabilities[agent_id] = CapabilityView(
            agent_id,
            MappingProxyType(
                {
                    "family_id": cell.family_id,
                    "parameters": parameters,
                    "action_vocabulary": targets,
                    "reward_rule": "declared machine-gradable group discovery",
                }
            ),
            visible_observation,
        )
    task_id = (
        f"PUBLIC-CAL-{cell.family_id[:3].upper()}-{cell.cell_index:03d}-V{variant}"
        if public_fixture
        else f"SEALED-{sha256_hex(canonical_json([cell.cell_id, variant]))[:16]}"
    )
    primitive = MappingProxyType(
        {
            "target": target,
            "parameters": parameters,
            "material_commitment": sha256_hex(canonical_json(material)),
            "hidden_labels": hidden_labels,
            "public_test_only": public_fixture,
        }
    )
    draft = TaskInstance(
        task_id=task_id,
        family_id=cell.family_id,
        cell_id=cell.cell_id,
        public_fixture=public_fixture,
        variant=variant,
        action_vocabulary=targets,
        source_vocabulary=("common", "independent", "none"),
        capabilities=MappingProxyType(capabilities),
        primitive_state=primitive,
        baseline=FAMILY_BASELINES[cell.family_id],
    )
    commitment = instance_commitment(draft)
    return replace(draft, commitment=commitment)


def instance_commitment(task: TaskInstance) -> str:
    """Commit to an instance without recursively committing to the commitment field."""
    evaluator = task.evaluator_record()
    visible = task.visible_record()
    visible["commitment"] = ""
    evaluator["visible"] = visible
    return sha256_hex(canonical_json(evaluator))


def generate_public_calibration() -> tuple[TaskInstance, ...]:
    """Generate exactly two public calibration cases per family."""
    selected: list[GeneratorCell] = []
    for family in FAMILY_STATE_COUNTS:
        family_cells = [cell for cell in canonical_cells() if cell.family_id == family]
        selected.extend((family_cells[0], family_cells[-1]))
    return tuple(
        generate_instance(cell, variant=index % 4, public_fixture=True)
        for index, cell in enumerate(selected)
    )


def generate_prompt_space() -> tuple[TaskInstance, ...]:
    """Generate one instance for every registered cell/isomorphism pair."""
    return tuple(
        generate_instance(cell, variant=variant, public_fixture=True)
        for cell in canonical_cells()
        for variant in range(4)
    )
