"""Deterministic public generation for the five registered task families."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import replace
from fractions import Fraction
from itertools import combinations, product
from math import comb
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
FAMILY_PUBLIC_CODES = {
    family_id: f"SYNTHETIC-FAMILY-{index}"
    for index, family_id in enumerate(FAMILY_STATE_COUNTS, start=1)
}

def _cells(
    family: str,
    rows: Iterable[dict[str, object]],
    state_counter: Callable[[dict[str, object]], int],
) -> list[GeneratorCell]:
    return [
        GeneratorCell(
            family,
            index,
            MappingProxyType(parameters),
            int(state_counter(parameters)),
        )
        for index, parameters in enumerate(rows, start=1)
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
            (2, 3, 4),
            ("1/2", "2/3", "3/4"),
            ("below-private-threshold", "trap-interval", "above-planner-threshold"),
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
        _cells(
            "common-source-acquisition",
            acquisition,
            lambda row: 9 + 3 ** (int(str(row["agent_count"])) + 1),
        )
        + _cells(
            "one-reader-versus-broadcast-attention",
            attention,
            lambda row: 3 ** (int(str(row["agent_count"])) + 2),
        )
        + _cells("point-versus-shortlist-sharing", sharing, _channel_state_count)
        + _cells(
            "consensus-collapse-versus-portfolio-recovery",
            recovery,
            _channel_state_count,
        )
        + _cells(
            "threshold-team-formation",
            threshold,
            lambda row: int(str(row["target_count"]))
            ** int(str(row["agent_count"])),
        )
    )
    if len(rows) != 138 or sum(row.primitive_labeled_states for row in rows) != 58945:
        raise AssertionError("registered generator counts changed")
    return tuple(rows)


def _channel_state_count(parameters: dict[str, object]) -> int:
    targets = int(str(parameters["target_count"]))
    agents = int(str(parameters["agent_count"]))
    signal_count = targets if parameters["channel"] == "noisy-point" else comb(targets, 2)
    return int(targets * signal_count**agents)


def _acquisition_baseline(parameters: dict[str, object]) -> tuple[BaselineObject, str]:
    from distributed_discovery.acquisition.common_source_analysis import (
        all_common_trap_interval,
        equilibrium_counts,
        planner_counts,
    )
    from distributed_discovery.acquisition.n_agent import discovery

    agents = int(str(parameters["agent_count"]))
    accuracy = Fraction(str(parameters["accuracy"]))
    lower, upper = all_common_trap_interval(agents, accuracy)
    region = str(parameters["cost_region"])
    if region == "below-private-threshold":
        cost = lower / 2
    elif region == "trap-interval":
        cost = (lower + upper) / 2
    else:
        cost = upper + (1 - upper) / 2
    planner_values = [
        discovery(agents, count, accuracy)
        for count in planner_counts(agents, accuracy, cost)
    ]
    equilibrium_values = [
        discovery(agents, count, accuracy)
        for count in equilibrium_counts(agents, accuracy, cost)
    ]
    return (
        BaselineObject(
            str(discovery(agents, agents, accuracy)),
            str(max(planner_values)),
            None,
            str(max(equilibrium_values)),
            str(min(equilibrium_values)),
        ),
        str(cost),
    )


def _attention_baseline(parameters: dict[str, object]) -> BaselineObject:
    from distributed_discovery.attention.model import discovery

    agents = int(str(parameters["agent_count"]))
    private = Fraction(str(parameters["private_accuracy"]))
    shared = Fraction(str(parameters["shared_accuracy"]))
    values = [discovery(agents, readers, private, shared) for readers in range(agents + 1)]
    return BaselineObject(str(values[0]), str(max(values)), 1)


def _channel(
    targets: int,
    channel_id: str,
) -> tuple[tuple[object, ...], dict[int, dict[object, Fraction]]]:
    if channel_id == "noisy-point":
        signals: tuple[object, ...] = tuple(range(targets))
        accuracy = Fraction(1, 2)
        law = {
            target: {
                signal: (
                    accuracy
                    if signal == target
                    else (1 - accuracy) / (targets - 1)
                )
                for signal in signals
            }
            for target in range(targets)
        }
        return signals, law
    signals = tuple(combinations(range(targets), 2))
    inclusion = Fraction(1) if channel_id == "guaranteed-two-shortlist" else Fraction(3, 4)
    containing = targets - 1
    excluding = comb(targets - 1, 2)
    law = {
        target: {
            signal: (
                inclusion / containing
                if _signal_contains(signal, target)
                else (1 - inclusion) / excluding
            )
            for signal in signals
        }
        for target in range(targets)
    }
    return signals, law


def _signal_contains(signal: object, target: int) -> bool:
    return isinstance(signal, tuple) and target in signal


def _channel_profile(
    targets: int,
    agents: int,
    channel_id: str,
) -> tuple[Fraction, tuple[Fraction, ...]]:
    signals, law = _channel(targets, channel_id)
    prior = Fraction(1, targets)
    one_person = sum(
        (max(prior * law[target][signal] for target in range(targets)) for signal in signals),
        Fraction(0),
    )
    profile = [Fraction(0) for _ in range(min(targets, agents))]
    for observations in product(signals, repeat=agents):
        weights = [
            prior
            * _fraction_product(law[target][signal] for signal in observations)
            for target in range(targets)
        ]
        probability = sum(weights, Fraction(0))
        if probability == 0:
            continue
        posterior = sorted((weight / probability for weight in weights), reverse=True)
        for index in range(len(profile)):
            profile[index] += probability * sum(posterior[: index + 1], Fraction(0))
    return one_person, tuple(profile)


def _fraction_product(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def _sharing_baseline(parameters: dict[str, object]) -> BaselineObject:
    targets = int(str(parameters["target_count"]))
    agents = int(str(parameters["agent_count"]))
    accuracy, profile = _channel_profile(targets, agents, str(parameters["channel"]))
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


def _sharing_public_primitives(parameters: dict[str, object]) -> dict[str, object]:
    targets = int(str(parameters["target_count"]))
    channel_id = str(parameters["channel"])
    return {
        "prior": [str(Fraction(1, targets))] * targets,
        "channel": channel_id,
        "point_accuracy": "1/2" if channel_id == "noisy-point" else None,
        "shortlist_inclusion_probability": (
            "1"
            if channel_id == "guaranteed-two-shortlist"
            else "3/4"
            if channel_id == "noisy-two-shortlist"
            else None
        ),
        "law": "symmetric across target relabelings",
    }


def _posterior_profile(targets: int, profile: str) -> tuple[Fraction, ...]:
    if profile == "tied":
        return (Fraction(1, targets),) * targets
    weights = (
        tuple(range(targets, 0, -1))
        if profile == "strict"
        else (2, *((1,) * (targets - 1)))
    )
    total = sum(weights)
    return tuple(Fraction(weight, total) for weight in weights)


def _threshold_baseline(parameters: dict[str, object]) -> tuple[BaselineObject, tuple[str, ...]]:
    from distributed_discovery.threshold_discovery.model import binomial_tail, planner_value
    from distributed_discovery.threshold_equilibrium.model import (
        discovery_value,
        pure_nash_occupancies,
    )

    targets = int(str(parameters["target_count"]))
    agents = int(str(parameters["agent_count"]))
    threshold = int(str(parameters["threshold"]))
    posterior = _posterior_profile(targets, str(parameters["posterior_profile"]))
    private = sum(
        (
            mass * binomial_tail(agents, mass, threshold)
            for mass in posterior
        ),
        Fraction(0),
    )
    equilibrium_values = [
        discovery_value(occupancy, posterior, threshold)
        for occupancy in pure_nash_occupancies(posterior, agents, threshold)
    ]
    baseline = BaselineObject(
        str(private),
        str(planner_value(posterior, agents, threshold)),
        min(targets, agents // threshold),
        str(max(equilibrium_values)),
        str(min(equilibrium_values)),
    )
    return baseline, tuple(str(value) for value in posterior)


def baseline_for_cell(cell: GeneratorCell) -> tuple[BaselineObject, dict[str, object]]:
    parameters = dict(cell.parameters)
    extras: dict[str, object] = {}
    if cell.family_id == "common-source-acquisition":
        baseline, cost = _acquisition_baseline(parameters)
        extras["cost"] = cost
        return baseline, extras
    if cell.family_id == "one-reader-versus-broadcast-attention":
        return _attention_baseline(parameters), extras
    if cell.family_id in {
        "point-versus-shortlist-sharing",
        "consensus-collapse-versus-portfolio-recovery",
    }:
        return _sharing_baseline(parameters), _sharing_public_primitives(parameters)
    baseline, posterior = _threshold_baseline(parameters)
    extras["posterior"] = posterior
    return baseline, extras


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
    if not public_fixture:
        raise PermissionError(
            "private generation is disabled until a future authorized campaign "
            "implements its custody context"
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
    baseline, exact_extras = baseline_for_cell(cell)
    capabilities: dict[str, CapabilityView] = {}
    source_signals: dict[str, dict[str, str]] = {}
    common_observed = targets[(cell.cell_index + variant + material_offset) % len(targets)]
    for index, agent_id in enumerate(agent_ids):
        observed = targets[(cell.cell_index + index + variant + material_offset) % len(targets)]
        clue = (
            f"HIDDEN-LABEL-{(index + variant) % target_count + 1}"
            if hidden_labels
            else observed.replace("TARGET-", "CLUE-")
        )
        if cell.family_id == "common-source-acquisition":
            common_clue = (
                "HIDDEN-COMMON-LABEL"
                if hidden_labels
                else common_observed.replace("TARGET-", "CLUE-")
            )
            source_signals[agent_id] = {
                "common": common_clue,
                "independent": clue,
            }
            visible_observation = "SOURCE-SELECTION-PENDING"
        elif cell.family_id == "one-reader-versus-broadcast-attention":
            visible_observation = (
                f"PRIVATE:{clue};SHARED:"
                f"{common_observed.replace('TARGET-', 'CLUE-')}"
                if index == 0 and not hidden_labels
                else f"PRIVATE:{clue}"
            )
        elif cell.family_id in {
            "point-versus-shortlist-sharing",
            "consensus-collapse-versus-portfolio-recovery",
        }:
            signals, _ = _channel(target_count, str(parameters["channel"]))
            signal = signals[(material_offset + cell.cell_index + index) % len(signals)]
            if isinstance(signal, tuple):
                labels = "+".join(targets[item].removeprefix("TARGET-") for item in signal)
                visible_observation = f"SHORTLIST:{labels}"
            else:
                visible_observation = (
                    targets[int(str(signal))].replace("TARGET-", "CLUE-")
                    if not hidden_labels
                    else clue
                )
        else:
            visible_observation = (
                f"RECOMMENDATION:{clue};POSTERIOR-PROFILE:"
                f"{parameters['posterior_profile']}"
            )
        capabilities[agent_id] = CapabilityView(
            agent_id,
            MappingProxyType(
                {
                    "task_class": FAMILY_PUBLIC_CODES[cell.family_id],
                    "parameters": parameters,
                    "exact_public_primitives": exact_extras,
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
            "exact_public_primitives": exact_extras,
            "material_commitment": sha256_hex(canonical_json(material)),
            "hidden_labels": hidden_labels,
            "public_test_only": public_fixture,
            "source_signals": source_signals,
        }
    )
    draft = TaskInstance(
        task_id=task_id,
        family_id=cell.family_id,
        cell_id=cell.cell_id,
        public_fixture=public_fixture,
        variant=variant,
        action_vocabulary=targets,
        source_vocabulary=(
            ("common", "independent")
            if cell.family_id == "common-source-acquisition"
            else ("none",)
        ),
        capabilities=MappingProxyType(capabilities),
        primitive_state=primitive,
        baseline=baseline,
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
