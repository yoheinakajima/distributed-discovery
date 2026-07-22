"""Exact finite-channel model and primary DD-021 evaluator."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations, product
from math import comb, factorial
from typing import Any

Signal = tuple[int, ...]


@dataclass(frozen=True)
class Channel:
    channel_id: str
    family: str
    targets: int
    parameter_k: int | None
    parameters: tuple[tuple[str, Fraction], ...]
    signals: tuple[Signal, ...]
    law: tuple[tuple[Fraction, ...], ...]
    direct_actions: tuple[tuple[int, ...], ...]
    denominator_complexity: int
    description_complexity: int


def fraction_text(value: Fraction, *, slash: bool = False) -> str:
    if value.denominator == 1 and not slash:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _slug(value: Fraction) -> str:
    return f"{value.numerator}of{value.denominator}"


def _prod(values: Iterator[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first, *rest)


def multinomial(counts: tuple[int, ...]) -> int:
    value = factorial(sum(counts))
    for count in counts:
        value //= factorial(count)
    return value


def _resolve(value: str, targets: int, shortlist_size: int | None = None) -> Fraction:
    if value == "uninformative":
        return Fraction(shortlist_size or 1, targets)
    return Fraction(value)


def _complexity(*values: Fraction) -> int:
    return max(value.denominator for value in values)


def _point_channel(targets: int, accuracy: Fraction) -> Channel:
    signals = tuple((value,) for value in range(targets))
    law = tuple(
        tuple(
            accuracy if signal[0] == target else (1 - accuracy) / (targets - 1)
            for signal in signals
        )
        for target in range(targets)
    )
    return Channel(
        channel_id=f"point-m{targets}-p{_slug(accuracy)}",
        family="symmetric-noisy-point",
        targets=targets,
        parameter_k=None,
        parameters=(("accuracy", accuracy),),
        signals=signals,
        law=law,
        direct_actions=signals,
        denominator_complexity=_complexity(accuracy, (1 - accuracy) / (targets - 1)),
        description_complexity=1,
    )


def _shortlist_channel(
    targets: int, shortlist_size: int, inclusion: Fraction, *, guaranteed: bool
) -> Channel:
    signals = tuple(combinations(range(targets), shortlist_size))
    inside = inclusion / comb(targets - 1, shortlist_size - 1)
    outside_count = comb(targets - 1, shortlist_size)
    outside = Fraction() if outside_count == 0 else (1 - inclusion) / outside_count
    law = tuple(
        tuple(inside if target in signal else outside for signal in signals)
        for target in range(targets)
    )
    family = "guaranteed-k-shortlist" if guaranteed else "noisy-k-shortlist"
    prefix = "guaranteed-shortlist" if guaranteed else "shortlist"
    return Channel(
        channel_id=(
            f"{prefix}-m{targets}-k{shortlist_size}"
            if guaranteed
            else f"{prefix}-m{targets}-k{shortlist_size}-a{_slug(inclusion)}"
        ),
        family=family,
        targets=targets,
        parameter_k=shortlist_size,
        parameters=(("inclusion_accuracy", inclusion),),
        signals=signals,
        law=law,
        direct_actions=signals,
        denominator_complexity=_complexity(inside, outside),
        description_complexity=3 if guaranteed else 2,
    )


def _exclusion_channel(targets: int, exclusion_size: int) -> Channel:
    signals = tuple(combinations(range(targets), exclusion_size))
    compatible = Fraction(1, comb(targets - 1, exclusion_size))
    law = tuple(
        tuple(Fraction() if target in signal else compatible for signal in signals)
        for target in range(targets)
    )
    direct = tuple(
        tuple(target for target in range(targets) if target not in signal) for signal in signals
    )
    return Channel(
        channel_id=f"exclusion-m{targets}-k{exclusion_size}",
        family="explicit-k-exclusion",
        targets=targets,
        parameter_k=exclusion_size,
        parameters=(("excluded_targets", Fraction(exclusion_size)),),
        signals=signals,
        law=law,
        direct_actions=direct,
        denominator_complexity=compatible.denominator,
        description_complexity=4,
    )


def _confidence_channel(targets: int, low: Fraction, high: Fraction) -> Channel:
    signals = tuple((nominee, level) for level in (0, 1) for nominee in range(targets))
    level_probability = Fraction(1, 2)
    law_rows: list[tuple[Fraction, ...]] = []
    for target in range(targets):
        values = []
        for nominee, level in signals:
            accuracy = low if level == 0 else high
            nomination = accuracy if nominee == target else (1 - accuracy) / (targets - 1)
            values.append(level_probability * nomination)
        law_rows.append(tuple(values))
    return Channel(
        channel_id=f"confidence-point-m{targets}-low{_slug(low)}-high{_slug(high)}",
        family="confidence-augmented-point",
        targets=targets,
        parameter_k=None,
        parameters=(("low_accuracy", low), ("high_accuracy", high)),
        signals=signals,
        law=tuple(law_rows),
        direct_actions=tuple((signal[0],) for signal in signals),
        denominator_complexity=_complexity(
            low / 2,
            high / 2,
            (1 - low) / (2 * (targets - 1)),
            (1 - high) / (2 * (targets - 1)),
        ),
        description_complexity=5,
    )


def build_channels(config: dict[str, Any]) -> list[Channel]:
    result: list[Channel] = []
    for targets in config["targets"]:
        point_values = sorted(
            {_resolve(str(value), targets) for value in config["point_accuracies"]}
        )
        result.extend(_point_channel(targets, value) for value in point_values)
        for shortlist_size in range(1, targets):
            inclusion_values = sorted(
                {
                    _resolve(str(value), targets, shortlist_size)
                    for value in config["shortlist_inclusion_accuracies"]
                }
            )
            result.extend(
                _shortlist_channel(targets, shortlist_size, inclusion, guaranteed=False)
                for inclusion in inclusion_values
                if Fraction(shortlist_size, targets) <= inclusion < 1
            )
            if config["guaranteed_shortlists"]:
                result.append(
                    _shortlist_channel(targets, shortlist_size, Fraction(1), guaranteed=True)
                )
            result.append(_exclusion_channel(targets, shortlist_size))
        for raw_low, raw_high in config["confidence_pairs"]:
            low = _resolve(str(raw_low), targets)
            high = _resolve(str(raw_high), targets)
            result.append(_confidence_channel(targets, low, high))
    ids = [channel.channel_id for channel in result]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate channel id")
    return result


def _relabel_signal(channel: Channel, signal: Signal, permutation: tuple[int, ...]) -> Signal:
    if channel.family == "confidence-augmented-point":
        return (permutation[signal[0]], signal[1])
    return tuple(sorted(permutation[value] for value in signal))


def target_symmetric(channel: Channel) -> bool:
    signal_index = {signal: index for index, signal in enumerate(channel.signals)}
    for permutation in permutations(range(channel.targets)):
        for target in range(channel.targets):
            for index, signal in enumerate(channel.signals):
                mapped = signal_index[_relabel_signal(channel, signal, permutation)]
                if channel.law[permutation[target]][mapped] != channel.law[target][index]:
                    return False
                expected = tuple(
                    sorted(permutation[value] for value in channel.direct_actions[index])
                )
                if tuple(sorted(channel.direct_actions[mapped])) != expected:
                    return False
    return True


def validate_channel(channel: Channel) -> bool:
    if len(channel.signals) != len(channel.direct_actions):
        return False
    if any(not actions for actions in channel.direct_actions):
        return False
    if any(
        any(target < 0 or target >= channel.targets for target in actions)
        for actions in channel.direct_actions
    ):
        return False
    if any(any(value < 0 for value in row) or sum(row, Fraction()) != 1 for row in channel.law):
        return False
    return target_symmetric(channel)


def _direct_success(channel: Channel, signal_index: int, target: int) -> Fraction:
    actions = channel.direct_actions[signal_index]
    return Fraction(1, len(actions)) if target in actions else Fraction()


def _joint_weights(channel: Channel, observations: tuple[int, ...]) -> tuple[Fraction, ...]:
    prior = Fraction(1, channel.targets)
    return tuple(
        prior * _prod(channel.law[target][signal] for signal in observations)
        for target in range(channel.targets)
    )


def labeled_core(channel: Channel, agents: int) -> dict[str, Any]:
    """Method A: ordered signal profiles and direct-failure enumeration."""
    signal_indices = tuple(range(len(channel.signals)))
    q = sum(
        (channel.law[0][signal] * _direct_success(channel, signal, 0) for signal in signal_indices),
        Fraction(),
    )
    private_failure = Fraction()
    for observations in product(signal_indices, repeat=agents):
        probability = _prod(channel.law[0][signal] for signal in observations)
        failure = _prod(1 - _direct_success(channel, signal, 0) for signal in observations)
        private_failure += probability * failure
    pooled: list[Fraction] = []
    profile: list[Fraction] = [Fraction() for _ in range(min(agents, channel.targets))]
    for block_size in range(1, agents + 1):
        accuracy = Fraction()
        for observations in product(signal_indices, repeat=block_size):
            accuracy += max(_joint_weights(channel, observations))
        pooled.append(accuracy)
    for observations in product(signal_indices, repeat=agents):
        ordered = sorted(_joint_weights(channel, observations), reverse=True)
        for budget in range(1, len(profile) + 1):
            profile[budget - 1] += sum(ordered[:budget], Fraction())
    return {
        "q": q,
        "private_discovery": 1 - private_failure,
        "pooled_accuracy": tuple(pooled),
        "action_budget_profile": tuple(profile),
    }


def histogram_core(channel: Channel, agents: int) -> dict[str, Any]:
    """Method B: unordered signal histograms with multinomial weights."""
    signal_indices = tuple(range(len(channel.signals)))
    prior = Fraction(1, channel.targets)
    q = sum(
        (
            prior * channel.law[target][signal] * _direct_success(channel, signal, target)
            for target in range(channel.targets)
            for signal in signal_indices
        ),
        Fraction(),
    )
    pooled: list[Fraction] = []
    profile: list[Fraction] = [Fraction() for _ in range(min(agents, channel.targets))]
    for block_size in range(1, agents + 1):
        accuracy = Fraction()
        for counts in compositions(block_size, len(signal_indices)):
            observations = tuple(
                signal
                for signal, count in zip(signal_indices, counts, strict=True)
                for _ in range(count)
            )
            accuracy += multinomial(counts) * max(_joint_weights(channel, observations))
        pooled.append(accuracy)
    for counts in compositions(agents, len(signal_indices)):
        observations = tuple(
            signal
            for signal, count in zip(signal_indices, counts, strict=True)
            for _ in range(count)
        )
        ordered = sorted(_joint_weights(channel, observations), reverse=True)
        multiplicity = multinomial(counts)
        for budget in range(1, len(profile) + 1):
            profile[budget - 1] += multiplicity * sum(ordered[:budget], Fraction())
    return {
        "q": q,
        "private_discovery": 1 - (1 - q) ** agents,
        "pooled_accuracy": tuple(pooled),
        "action_budget_profile": tuple(profile),
    }


def _sharing_class(increments: tuple[Fraction, ...]) -> str:
    if all(value == 0 for value in increments):
        return "all-neutral"
    if all(value <= 0 for value in increments):
        return "strict-compression-dominated"
    if all(value >= 0 for value in increments):
        return "strict-aggregation-dominated"
    return "mixed"


def _full_sharing_class(q: Fraction, private: Fraction, consensus: Fraction) -> str:
    if consensus < q:
        return "A-strict-no-one-action-aggregation-gain"
    if q < consensus < private:
        return "B-shared-discovery-paradox"
    if consensus > private:
        return "C-strict-aggregation-dominated-consensus"
    return "D-boundary"


def derive_metrics(channel: Channel, agents: int, core: dict[str, Any]) -> dict[str, Any]:
    q = core["q"]
    private = core["private_discovery"]
    pooled = core["pooled_accuracy"]
    profile = core["action_budget_profile"]
    discovery = tuple(
        1 - (1 - accuracy) * (1 - q) ** (agents - block_size)
        for block_size, accuracy in enumerate(pooled, start=1)
    )
    increments = tuple(discovery[index] - discovery[index - 1] for index in range(1, agents))
    errors = tuple(1 - value for value in pooled)
    ratios = tuple(
        None if errors[index - 1] == 0 else errors[index] / errors[index - 1]
        for index in range(1, agents)
    )
    recovery = next(budget for budget, value in enumerate(profile, start=1) if value >= private)
    return {
        "channel_id": channel.channel_id,
        "family": channel.family,
        "targets": channel.targets,
        "agents": agents,
        "parameter_k": channel.parameter_k,
        "parameters": dict(channel.parameters),
        "signal_alphabet_size": len(channel.signals),
        "denominator_complexity": channel.denominator_complexity,
        "description_complexity": channel.description_complexity,
        "q": q,
        "private_discovery": private,
        "pooled_accuracy": pooled,
        "pooled_error": errors,
        "error_contraction_ratio": ratios,
        "rescue_threshold": 1 - q,
        "sharing_discovery": discovery,
        "sharing_increments": increments,
        "action_budget_profile": profile,
        "recovery_budget": recovery,
        "sharing_class": _sharing_class(increments),
        "full_sharing_class": _full_sharing_class(q, private, pooled[-1]),
        "recovery_class": "consensus-sufficient" if recovery == 1 else "portfolio-dependent",
    }


def channel_record(channel: Channel) -> dict[str, Any]:
    conditional = {
        "parameters": ",".join(
            f"{name}={fraction_text(value, slash=True)}" for name, value in channel.parameters
        ),
        "matrix_rows": str(channel.targets),
        "matrix_columns": str(len(channel.signals)),
    }
    return {
        "schema_version": "signal-channel-v1",
        "channel_id": channel.channel_id,
        "target_set": list(range(channel.targets)),
        "prior": [fraction_text(Fraction(1, channel.targets), slash=True)] * channel.targets,
        "signal_alphabet": [list(signal) for signal in channel.signals],
        "conditional_distribution": conditional,
        "symmetry_class": f"simultaneous S{channel.targets} target/signal relabeling",
        "likelihood_ratios": {},
        "posterior_update": "prior(theta)*product_i W(s_i|theta), normalized",
        "private_bayes_action_correspondence": "declared target-equivariant direct action set",
        "tie_breaking": "uniform with independent private and pooled randomization sources",
        "signal_cost": "0/1",
        "source_dependence": "conditionally-independent",
        "evaluation_mode": "exact-rational",
    }


def channel_certificate(channel: Channel) -> dict[str, Any]:
    return {
        **channel_record(channel),
        "family": channel.family,
        "parameter_k": channel.parameter_k,
        "parameters": dict(channel.parameters),
        "law": channel.law,
        "direct_actions": channel.direct_actions,
        "denominator_complexity": channel.denominator_complexity,
        "description_complexity": channel.description_complexity,
    }


def registry_state_counts(channels: list[Channel], agents: list[int]) -> dict[str, int]:
    labeled = 0
    histogram = 0
    largest_labeled = 0
    largest_histogram = 0
    for channel in channels:
        alphabet = len(channel.signals)
        for count in agents:
            labeled_states = channel.targets * sum(alphabet**size for size in range(1, count + 1))
            histogram_states = channel.targets * sum(
                comb(alphabet + size - 1, size) for size in range(1, count + 1)
            )
            labeled += labeled_states
            histogram += histogram_states
            largest_labeled = max(largest_labeled, labeled_states)
            largest_histogram = max(largest_histogram, histogram_states)
    return {
        "labeled_target_profile_states": labeled,
        "histogram_target_profile_states": histogram,
        "largest_labeled_target_profile_states": largest_labeled,
        "largest_histogram_target_profile_states": largest_histogram,
    }


def evaluate(
    config: dict[str, Any],
) -> tuple[list[Channel], list[dict[str, Any]], list[dict[str, Any]]]:
    channels = build_channels(config)
    labeled_rows: list[dict[str, Any]] = []
    histogram_rows: list[dict[str, Any]] = []
    for channel in channels:
        for agents in config["agents"]:
            labeled_rows.append(derive_metrics(channel, agents, labeled_core(channel, agents)))
            histogram_rows.append(derive_metrics(channel, agents, histogram_core(channel, agents)))
    return channels, labeled_rows, histogram_rows
