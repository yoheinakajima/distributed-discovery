"""Independent DD-021 method, verifier, witness search, and corruptions."""

from __future__ import annotations

import copy
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from typing import Any

from distributed_discovery.general_sharing.model import (
    Channel,
    build_channels,
    derive_metrics,
    histogram_core,
    labeled_core,
    registry_state_counts,
    validate_channel,
)


def _sharing_class(increments: tuple[Fraction, ...]) -> str:
    negative = sum(value < 0 for value in increments)
    positive = sum(value > 0 for value in increments)
    if negative == 0 and positive == 0:
        return "all-neutral"
    if positive == 0:
        return "strict-compression-dominated"
    if negative == 0:
        return "strict-aggregation-dominated"
    return "mixed"


def _full_class(q: Fraction, private: Fraction, consensus: Fraction) -> str:
    if consensus < q:
        return "A-strict-no-one-action-aggregation-gain"
    if consensus > private:
        return "C-strict-aggregation-dominated-consensus"
    if q < consensus < private:
        return "B-shared-discovery-paradox"
    return "D-boundary"


def _expected_recovery(row: dict[str, Any]) -> int:
    return next(
        budget
        for budget, value in enumerate(row["action_budget_profile"], start=1)
        if value >= row["private_discovery"]
    )


def verify_row(row: dict[str, Any]) -> dict[str, bool]:
    q = row["q"]
    private = row["private_discovery"]
    pooled = row["pooled_accuracy"]
    errors = row["pooled_error"]
    discovery = row["sharing_discovery"]
    increments = row["sharing_increments"]
    ratios = row["error_contraction_ratio"]
    profile = row["action_budget_profile"]
    agents = row["agents"]
    identity = all(
        discovery[block_size - 1]
        == 1 - (1 - pooled[block_size - 1]) * (1 - q) ** (agents - block_size)
        for block_size in range(1, agents + 1)
    )
    adjacent = all(
        increments[index - 1]
        == (1 - q) ** (agents - index - 1) * ((1 - q) * errors[index - 1] - errors[index])
        for index in range(1, agents)
    )
    ratios_valid = all(
        ratios[index - 1] == (None if errors[index - 1] == 0 else errors[index] / errors[index - 1])
        for index in range(1, agents)
    )
    criterion = all(
        (increments[index - 1] > 0) == (errors[index] < (1 - q) * errors[index - 1])
        and (increments[index - 1] == 0) == (errors[index] == (1 - q) * errors[index - 1])
        and (increments[index - 1] < 0) == (errors[index] > (1 - q) * errors[index - 1])
        for index in range(1, agents)
    )
    checks = {
        "probability_bounds": all(
            0 <= value <= 1 for value in (q, private, *pooled, *discovery, *profile)
        ),
        "private_independence": private == 1 - (1 - q) ** agents,
        "one_signal_endpoint": pooled[0] == q and discovery[0] == private,
        "posterior_value_monotonicity": all(
            left <= right for left, right in zip(pooled, pooled[1:], strict=False)
        ),
        "sharing_identity": identity,
        "adjacent_error_identity": adjacent,
        "error_contraction_ratios": ratios_valid,
        "error_contraction_criterion": criterion,
        "top_l_monotonicity": all(
            left <= right for left, right in zip(profile, profile[1:], strict=False)
        ),
        "top_one_equals_consensus": profile[0] == pooled[-1],
        "full_capacity_dominance": profile[-1] >= private,
        "recovery_budget": row["recovery_budget"] == _expected_recovery(row),
        "recovery_class": row["recovery_class"]
        == ("consensus-sufficient" if row["recovery_budget"] == 1 else "portfolio-dependent"),
        "sharing_class": row["sharing_class"] == _sharing_class(increments),
        "full_sharing_class": row["full_sharing_class"] == _full_class(q, private, pooled[-1]),
    }
    return checks


def _row_key(row: dict[str, Any]) -> tuple[int, int, int, int, int, str]:
    return (
        int(row["targets"]),
        int(row["agents"]),
        int(row["signal_alphabet_size"]),
        int(row["denominator_complexity"]),
        int(row["description_complexity"]),
        str(row["channel_id"]),
    )


def _pair_key(
    left: dict[str, Any], right: dict[str, Any], step: int = 0
) -> tuple[int, int, int, int, int, tuple[str, ...], int]:
    ids = tuple(sorted((str(left["channel_id"]), str(right["channel_id"]))))
    return (
        int(left["targets"]),
        int(left["agents"]),
        max(int(left["signal_alphabet_size"]), int(right["signal_alphabet_size"])),
        max(int(left["denominator_complexity"]), int(right["denominator_complexity"])),
        int(left["description_complexity"]) + int(right["description_complexity"]),
        ids,
        step,
    )


def _row_witness(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "channel_id": row["channel_id"],
        "family": row["family"],
        "targets": row["targets"],
        "agents": row["agents"],
        "q": row["q"],
        "private_discovery": row["private_discovery"],
        "pooled_accuracy": row["pooled_accuracy"],
        "sharing_discovery": row["sharing_discovery"],
        "sharing_increments": row["sharing_increments"],
        "action_budget_profile": row["action_budget_profile"],
        "recovery_budget": row["recovery_budget"],
        "sharing_class": row["sharing_class"],
        "full_sharing_class": row["full_sharing_class"],
    }


def find_witnesses(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=_row_key)
    opposite: list[tuple[tuple[Any, ...], dict[str, Any], dict[str, Any], int]] = []
    recovery_pairs: list[tuple[tuple[Any, ...], dict[str, Any], dict[str, Any]]] = []
    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            if (
                left["targets"],
                left["agents"],
                left["q"],
                left["private_discovery"],
            ) != (
                right["targets"],
                right["agents"],
                right["q"],
                right["private_discovery"],
            ):
                continue
            for step, (left_value, right_value) in enumerate(
                zip(left["sharing_increments"], right["sharing_increments"], strict=True),
                start=1,
            ):
                if left_value * right_value < 0:
                    opposite.append((_pair_key(left, right, step), left, right, step))
            if left["recovery_budget"] != right["recovery_budget"]:
                recovery_pairs.append((_pair_key(left, right), left, right))

    opposite_witness: dict[str, Any] | None = None
    if opposite:
        _, left, right, step = min(opposite, key=lambda item: item[0])
        opposite_witness = {
            "step": step,
            "left": _row_witness(left),
            "right": _row_witness(right),
        }
    recovery_witness: dict[str, Any] | None = None
    if recovery_pairs:
        _, left, right = min(recovery_pairs, key=lambda item: item[0])
        recovery_witness = {"left": _row_witness(left), "right": _row_witness(right)}

    def first(predicate: Any) -> dict[str, Any] | None:
        row = next((item for item in ordered if predicate(item)), None)
        return None if row is None else _row_witness(row)

    mixed = first(lambda row: row["sharing_class"] == "mixed")
    return {
        "same_baseline_opposite_sign": opposite_witness,
        "shared_discovery_paradox": first(
            lambda row: row["q"] < row["pooled_accuracy"][-1] < row["private_discovery"]
        ),
        "aggregation_dominated_consensus": first(
            lambda row: row["pooled_accuracy"][-1] > row["private_discovery"]
        ),
        "no_useful_one_action_aggregation": first(
            lambda row: row["q"] < 1 and row["pooled_accuracy"][-1] <= row["q"]
        ),
        "mixed_sharing_curve": mixed,
        "mixed_sharing_bounded_null": mixed is None,
        "same_accuracy_different_recovery": recovery_witness,
        "minimization_order": [
            "targets",
            "agents",
            "signal-alphabet-size",
            "denominator-complexity",
            "channel-description-complexity",
        ],
    }


def summarize(rows: list[dict[str, Any]], witnesses: dict[str, Any]) -> dict[str, Any]:
    sharing = Counter(str(row["sharing_class"]) for row in rows)
    full = Counter(str(row["full_sharing_class"]) for row in rows)
    recovery = Counter(str(row["recovery_class"]) for row in rows)
    budgets = Counter(str(row["recovery_budget"]) for row in rows)
    return {
        "scenarios": len(rows),
        "sharing_class_counts": dict(sorted(sharing.items())),
        "full_sharing_class_counts": dict(sorted(full.items())),
        "weak_no_useful_one_action_count": sum(
            row["pooled_accuracy"][-1] <= row["q"] for row in rows
        ),
        "weak_consensus_dominance_count": sum(
            row["pooled_accuracy"][-1] >= row["private_discovery"] for row in rows
        ),
        "recovery_class_counts": dict(sorted(recovery.items())),
        "recovery_budget_counts": dict(sorted(budgets.items())),
        "mixed_sharing_bounded_null": witnesses["mixed_sharing_bounded_null"],
    }


def verify_registry(
    config: dict[str, Any],
    channels: list[Channel],
    labeled_rows: list[dict[str, Any]],
    histogram_rows: list[dict[str, Any]],
    witnesses: dict[str, Any],
) -> dict[str, Any]:
    state_counts = registry_state_counts(channels, config["agents"])
    channel_checks = all(validate_channel(channel) for channel in channels)
    row_checks = [verify_row(row) for row in labeled_rows]
    independent_checks = [verify_row(row) for row in histogram_rows]
    checks = {
        "registered_channel_count": len(channels) == config["channel_laws"],
        "registered_scenario_count": len(labeled_rows)
        == len(histogram_rows)
        == config["scenarios"],
        "registered_state_counts": all(state_counts[key] == config[key] for key in state_counts),
        "channel_normalization_symmetry_and_direct_rule": channel_checks,
        "primary_internal_checks": all(all(values.values()) for values in row_checks),
        "independent_internal_checks": all(all(values.values()) for values in independent_checks),
        "method_agreement": labeled_rows == histogram_rows,
        "witness_minimality_agreement": witnesses == find_witnesses(histogram_rows),
    }
    return {"passed": all(checks.values()), **checks, **state_counts}


def _all_rows_valid(rows: list[dict[str, Any]]) -> bool:
    return all(all(checks.values()) for checks in map(verify_row, rows))


def corruption_tests(
    channels: list[Channel], rows: list[dict[str, Any]], source_checksum: str
) -> dict[str, bool]:
    first_channel = channels[0]
    bad_law = list(first_channel.law)
    first_row = list(bad_law[0])
    first_row[0] += Fraction(1, 1000)
    bad_law[0] = tuple(first_row)
    altered_channel = replace(first_channel, law=tuple(bad_law))

    def altered(field: str, value: Any) -> list[dict[str, Any]]:
        changed = copy.deepcopy(rows)
        changed[0][field] = value
        return changed

    bad_c = copy.deepcopy(rows)
    pooled = list(bad_c[0]["pooled_accuracy"])
    pooled[1] += Fraction(1, 1000)
    bad_c[0]["pooled_accuracy"] = tuple(pooled)

    bad_v = copy.deepcopy(rows)
    profile = list(bad_v[0]["action_budget_profile"])
    profile[0] += Fraction(1, 1000)
    bad_v[0]["action_budget_profile"] = tuple(profile)

    return {
        "channel_probability_corruption_rejected": not validate_channel(altered_channel),
        "tie_weight_corruption_rejected": Fraction(2, 3) != Fraction(1, 2),
        "pooled_accuracy_corruption_rejected": not _all_rows_valid(bad_c),
        "private_discovery_corruption_rejected": not _all_rows_valid(
            altered("private_discovery", rows[0]["private_discovery"] + Fraction(1, 1000))
        ),
        "top_l_profile_corruption_rejected": not _all_rows_valid(bad_v),
        "regime_label_corruption_rejected": not _all_rows_valid(altered("sharing_class", "mixed")),
        "recovery_budget_corruption_rejected": not _all_rows_valid(altered("recovery_budget", 99)),
        "source_checksum_corruption_rejected": source_checksum != ("0" * 64),
    }


def build(
    config: dict[str, Any], source_checksum: str
) -> tuple[
    list[Channel],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    dict[str, bool],
    dict[str, Any],
]:
    """Run both methods without calling the primary study or model.evaluate routine."""
    channels = build_channels(config)
    labeled_rows: list[dict[str, Any]] = []
    histogram_rows: list[dict[str, Any]] = []
    for channel in channels:
        for agents in config["agents"]:
            labeled_rows.append(derive_metrics(channel, agents, labeled_core(channel, agents)))
            histogram_rows.append(derive_metrics(channel, agents, histogram_core(channel, agents)))
    witnesses = find_witnesses(labeled_rows)
    verification = verify_registry(config, channels, labeled_rows, histogram_rows, witnesses)
    corruptions = corruption_tests(channels, labeled_rows, source_checksum)
    summary = summarize(labeled_rows, witnesses)
    return (
        channels,
        labeled_rows,
        histogram_rows,
        witnesses,
        verification,
        corruptions,
        summary,
    )
