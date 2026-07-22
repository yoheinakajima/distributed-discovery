from fractions import Fraction
from pathlib import Path

import yaml

from distributed_discovery.incremental_sharing.model import (
    channel_profiles,
    point_profile,
    pooled_accuracy_counts,
    pooled_accuracy_occupancy,
    wrong_occupancy_tie_weight,
)
from distributed_discovery.incremental_sharing.study import bundle

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "studies/DD-020-incremental-sharing/configs/census.yml"


def test_registered_bundle_passes_exact_checks() -> None:
    config = yaml.safe_load(CONFIG.read_text())
    data = bundle(config)
    assert len(data["point_rows"]) == 2555
    assert data["verification"]["passed"]
    assert all(data["corruptions"].values())


def test_two_exact_point_methods_agree_on_small_grid() -> None:
    for targets in range(2, 6):
        for block_size in range(1, 7):
            for accuracy in (Fraction(1, targets), Fraction(1, 2), Fraction(3, 4), Fraction(1)):
                if accuracy < Fraction(1, targets):
                    continue
                assert pooled_accuracy_counts(targets, block_size, accuracy) == (
                    pooled_accuracy_occupancy(targets, block_size, accuracy)
                )


def test_occupancy_tie_weight_hand_checks() -> None:
    assert wrong_occupancy_tie_weight(0, 3, 1) == 1
    assert wrong_occupancy_tie_weight(1, 3, 1) == Fraction(1, 2)
    assert wrong_occupancy_tie_weight(2, 1, 1) == 0


def test_point_profile_boundary_and_monotonicity() -> None:
    uninformative = point_profile(4, 4, Fraction(1, 4))
    assert uninformative == (
        Fraction(175, 256),
        Fraction(37, 64),
        Fraction(7, 16),
        Fraction(1, 4),
    )
    assert point_profile(4, 4, Fraction(1)) == (Fraction(1),) * 4
    ordinary = point_profile(4, 4, Fraction(1, 2))
    assert all(left > right for left, right in zip(ordinary, ordinary[1:], strict=False))


def test_same_accuracy_channels_can_have_opposite_increment_signs() -> None:
    rows = channel_profiles()
    point = next(row for row in rows if row["channel_id"] == "noisy-point-half")
    shortlist = next(row for row in rows if row["channel_id"] == "guaranteed-shortlist-two")
    assert point["one_person_accuracy"] == shortlist["one_person_accuracy"] == Fraction(1, 2)
    assert point["profile"] == (Fraction(7, 8), Fraction(3, 4), Fraction(7, 12))
    assert shortlist["profile"] == (Fraction(7, 8), Fraction(11, 12), Fraction(17, 18))
    assert all(value < 0 for value in point["increments"])
    assert all(value > 0 for value in shortlist["increments"])
