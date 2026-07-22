"""Independent checks and deliberate corruptions for DD-020."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from distributed_discovery.incremental_sharing.model import (
    channel_profiles,
    group_discovery,
    point_census,
    pooled_accuracy_counts,
)


def verify(
    config: dict[str, Any], point_rows: list[dict[str, Any]], channel_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    method_agreement = all(
        row["pooled_accuracy"] == row["independent_pooled_accuracy"]
        and row["group_discovery"] == row["independent_group_discovery"]
        for row in point_rows
    ) and all(
        row["pooled_accuracy"] == row["independent_pooled_accuracy"]
        and row["profile"] == row["independent_profile"]
        for row in channel_rows
    )
    identity = all(
        row["group_discovery"]
        == group_discovery(
            row["pooled_accuracy"], row["accuracy"], row["agents"], row["block_size"]
        )
        for row in point_rows
    )
    bounds = all(
        0 <= row["pooled_accuracy"] <= 1 and 0 <= row["group_discovery"] <= 1 for row in point_rows
    )
    first_endpoint = all(
        row["pooled_accuracy"] == row["accuracy"] for row in point_rows if row["block_size"] == 1
    )
    consensus_endpoint = all(
        row["group_discovery"] == row["pooled_accuracy"]
        for row in point_rows
        if row["block_size"] == row["agents"]
    )
    monotone = all(row["increment"] is None or row["increment"] <= 0 for row in point_rows)
    strict_boundary = all(
        row["increment"] is None
        or (row["increment"] == 0 if row["accuracy"] == 1 else row["increment"] < 0)
        for row in point_rows
    )
    n2 = all(
        row["pooled_accuracy"] == row["accuracy"]
        for row in point_rows
        if row["agents"] == 2 and row["block_size"] == 2
    )
    expected_rows = config["protocol_rows"] == len(point_rows)
    channel_ids = [row["channel_id"] for row in channel_rows]
    expected_channels = channel_ids == config["dd019_channels"]
    point = next(row for row in channel_rows if row["channel_id"] == "noisy-point-half")
    shortlist = next(row for row in channel_rows if row["channel_id"] == "guaranteed-shortlist-two")
    same_accuracy = point["one_person_accuracy"] == shortlist["one_person_accuracy"]
    different_incremental_profiles = point["profile"] != shortlist["profile"]
    checks = {
        "method_agreement": method_agreement,
        "aggregation_rescue_identity": identity,
        "probability_bounds": bounds,
        "first_block_pooled_accuracy": first_endpoint,
        "full_consensus_endpoint": consensus_endpoint,
        "point_profile_nonincreasing": monotone,
        "point_profile_strict_except_perfect": strict_boundary,
        "two_agent_pooled_identity": n2,
        "registered_row_count": expected_rows,
        "registered_channel_ids": expected_channels,
        "same_accuracy_witness": same_accuracy,
        "different_incremental_profiles": different_incremental_profiles,
    }
    return {"passed": all(checks.values()), **checks}


def corruption_tests(
    config: dict[str, Any], point_rows: list[dict[str, Any]], channel_rows: list[dict[str, Any]]
) -> dict[str, bool]:
    baseline = verify(config, point_rows, channel_rows)

    bad_count = [dict(row) for row in point_rows]
    bad_count[0]["independent_pooled_accuracy"] += Fraction(1, 1000)

    bad_tie = pooled_accuracy_counts(2, 2, Fraction(1, 2)) != Fraction(3, 4)

    bad_pooled = [dict(row) for row in point_rows]
    bad_pooled[1]["pooled_accuracy"] += Fraction(1, 1000)

    bad_discovery = [dict(row) for row in point_rows]
    bad_discovery[0]["group_discovery"] -= Fraction(1, 1000)

    bad_sign = [dict(row) for row in point_rows]
    candidate = next(i for i, row in enumerate(bad_sign) if row["increment"] is not None)
    bad_sign[candidate]["increment"] = Fraction(1, 1000)

    return {
        "baseline_passes": baseline["passed"],
        "count_probability_corruption_rejected": not verify(config, bad_count, channel_rows)[
            "passed"
        ],
        "tie_weight_corruption_rejected": bad_tie,
        "pooled_accuracy_corruption_rejected": not verify(config, bad_pooled, channel_rows)[
            "passed"
        ],
        "discovery_corruption_rejected": not verify(config, bad_discovery, channel_rows)["passed"],
        "sign_corruption_rejected": not verify(config, bad_sign, channel_rows)["passed"],
    }


def build(
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, bool]]:
    point_rows = point_census(config)
    channel_rows = channel_profiles()
    verification = verify(config, point_rows, channel_rows)
    corruptions = corruption_tests(config, point_rows, channel_rows)
    return point_rows, channel_rows, verification, corruptions
