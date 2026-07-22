from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
import yaml

from distributed_discovery.coordination_free_sharing import exact, private_game, shared_game
from distributed_discovery.coordination_free_sharing.equilibrium import (
    private_correspondence_record,
)
from distributed_discovery.coordination_free_sharing.study import bundle
from distributed_discovery.coordination_free_sharing.thresholds import (
    ROOT_INTERVAL,
    certificate,
    polynomial,
)

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "studies/DD-022-coordination-free-positive-sharing/configs/registry.yml"


@pytest.fixture(scope="module")
def exact_bundle() -> dict[str, Any]:
    return bundle(yaml.safe_load(CONFIG.read_text()), ROOT)


def test_closed_forms_match_independent_enumeration(exact_bundle: dict[str, Any]) -> None:
    assert exact_bundle["verification"]["passed"] is True
    assert all(exact_bundle["corruptions"].values())
    assert len(exact_bundle["rows"]) == 42


def test_hand_check_canonical_positive_cell() -> None:
    p, rho = Fraction(3, 5), Fraction(3, 4)
    private = private_game.selected_equilibrium(p, rho)
    shared = shared_game.selected_equilibrium(p, rho)
    assert private.follow_probability == Fraction(17, 19)
    assert shared.agreement_action_probability == Fraction(37, 44)
    assert shared_game.metrics(p, rho).discovery > private_game.selected_metrics(p, rho).discovery
    assert exact.private_metrics(
        p, rho, private.follow_probability
    ) == private_game.selected_metrics(p, rho)
    assert exact.shared_metrics(p, rho) == shared_game.metrics(p, rho)


def test_threshold_certificate_and_corrupted_interval() -> None:
    lower, upper = ROOT_INTERVAL
    assert certificate()["passed"] is True
    assert polynomial(lower) < 0 < polynomial(upper)
    assert not (polynomial(Fraction(1, 2)) < 0 < polynomial(Fraction(13, 25)))


def test_private_pure_correspondence_exposes_selection_dependence() -> None:
    low = private_correspondence_record(Fraction(3, 5), Fraction(1, 2))
    boundary = private_correspondence_record(Fraction(3, 5), Fraction(7, 12))
    high = private_correspondence_record(Fraction(3, 5), Fraction(3, 4))
    assert low["equilibrium_count"] == 3
    assert boundary["equilibrium_count"] == 5
    assert high["equilibrium_count"] == 4
    assert low["best_pure_discovery"] == high["best_pure_discovery"] == 1
    assert ("constant-0", "constant-1") in {
        tuple(record["strategies"]) for record in low["equilibria"]
    }


def test_boundary_cases() -> None:
    assert (
        private_game.selected_equilibrium(Fraction(1, 2), Fraction(0)).unique_in_symmetric_class
        is False
    )
    assert private_game.selected_equilibrium(
        Fraction(1, 2), Fraction(1)
    ).follow_probability == Fraction(1, 2)
    assert private_game.selected_equilibrium(Fraction(1), Fraction(1)).follow_probability == 1
    assert (
        shared_game.metrics(Fraction(3, 5), Fraction(1)).discovery
        == private_game.selected_metrics(Fraction(3, 5), Fraction(1)).discovery
    )
