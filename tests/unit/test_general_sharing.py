import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
import yaml
from jsonschema import Draft202012Validator

from distributed_discovery.general_sharing.model import (
    build_channels,
    channel_record,
    derive_metrics,
    histogram_core,
    labeled_core,
    validate_channel,
)
from distributed_discovery.general_sharing.study import bundle

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "studies/DD-021-general-sharing-frontier/configs/registry.yml"


@pytest.fixture(scope="module")
def exact_bundle() -> dict[str, Any]:
    return bundle(yaml.safe_load(CONFIG.read_text()), ROOT)


def test_registered_channels_reuse_schema_and_validate() -> None:
    config = yaml.safe_load(CONFIG.read_text())
    channels = build_channels(config)
    assert len(channels) == 59
    assert all(validate_channel(channel) for channel in channels)
    schema = json.loads((ROOT / config["channel_schema_path"]).read_text())
    validator = Draft202012Validator(schema)
    assert not [
        error for channel in channels for error in validator.iter_errors(channel_record(channel))
    ]


def test_two_methods_agree_and_all_corruptions_are_rejected(
    exact_bundle: dict[str, Any],
) -> None:
    assert exact_bundle["verification"]["passed"] is True
    assert all(exact_bundle["corruptions"].values())
    assert len(exact_bundle["rows"]) == 177
    assert exact_bundle["rows"] == exact_bundle["independent_rows"]


def test_hand_check_point_and_guaranteed_shortlist() -> None:
    config = yaml.safe_load(CONFIG.read_text())
    channels = build_channels(config)
    point = next(channel for channel in channels if channel.channel_id == "point-m3-p1of2")
    shortlist = next(
        channel for channel in channels if channel.channel_id == "guaranteed-shortlist-m3-k2"
    )
    point_row = derive_metrics(point, 2, labeled_core(point, 2))
    shortlist_row = derive_metrics(shortlist, 2, histogram_core(shortlist, 2))
    assert point_row["q"] == shortlist_row["q"] == Fraction(1, 2)
    assert point_row["private_discovery"] == shortlist_row["private_discovery"] == Fraction(3, 4)
    assert point_row["sharing_increments"][0] < 0
    assert shortlist_row["sharing_increments"][0] == 0
    assert point_row["recovery_budget"] == 2
    assert shortlist_row["recovery_budget"] == 1


def test_frontier_identity_full_capacity_and_minimal_witness(
    exact_bundle: dict[str, Any],
) -> None:
    rows = exact_bundle["rows"]
    assert all(row["action_budget_profile"][-1] >= row["private_discovery"] for row in rows)
    for row in rows:
        for index, increment in enumerate(row["sharing_increments"]):
            errors = row["pooled_error"]
            threshold_gap = (1 - row["q"]) * errors[index] - errors[index + 1]
            assert (increment > 0) == (threshold_gap > 0)
            assert (increment == 0) == (threshold_gap == 0)
    witness = exact_bundle["witnesses"]["same_baseline_opposite_sign"]
    assert witness["left"]["targets"] == witness["right"]["targets"] == 4
    assert witness["left"]["agents"] == witness["right"]["agents"] == 2
    assert {witness["left"]["channel_id"], witness["right"]["channel_id"]} == {
        "point-m4-p1of2",
        "guaranteed-shortlist-m4-k2",
    }
