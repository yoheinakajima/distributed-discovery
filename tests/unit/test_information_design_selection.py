import copy
from fractions import Fraction
from pathlib import Path

import yaml

from distributed_discovery.information_design.game import Likelihood
from distributed_discovery.information_design.selection import (
    PartitionSelection,
    evaluate_catalogue,
    exact_potential,
    profile_payoffs,
    refinement_comparisons,
    selection_certificate,
    strict_best_response_moves,
)
from distributed_discovery.information_design.selection_verification import (
    verify_selection_certificate,
)

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "studies/DD-002-information-design/configs/selection-robustness.yml"


def _catalogue() -> tuple[Likelihood, tuple[PartitionSelection, ...]]:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    likelihood: Likelihood = tuple(
        tuple(Fraction(value) for value in row) for row in config["likelihood"]
    )
    return likelihood, evaluate_catalogue(likelihood)


def test_equal_split_game_has_exact_rosenthal_potential() -> None:
    _, catalogue = _catalogue()
    for partition in catalogue:
        for message in partition.messages:
            posterior = message.posterior
            for first in range(3):
                for second in range(3):
                    profile = (first, second)
                    for player in (0, 1):
                        for action in range(3):
                            updated = list(profile)
                            updated[player] = action
                            updated_profile = (updated[0], updated[1])
                            assert profile_payoffs(posterior, updated_profile)[
                                player
                            ] - profile_payoffs(posterior, profile)[player] == exact_potential(
                                posterior, updated_profile
                            ) - exact_potential(posterior, profile)


def test_strict_best_response_moves_raise_potential() -> None:
    _, catalogue = _catalogue()
    for partition in catalogue:
        for message in partition.messages:
            for first in range(3):
                for second in range(3):
                    profile = (first, second)
                    assert all(
                        exact_potential(message.posterior, move)
                        > exact_potential(message.posterior, profile)
                        for move in strict_best_response_moves(message.posterior, profile)
                    )


def test_known_witness_reverses_only_anonymous_symmetric_rule() -> None:
    _, catalogue = _catalogue()
    less = next(item for item in catalogue if item.partition_id == "P00")
    more = next(item for item in catalogue if item.partition_id == "P03")
    assert less.values["anonymous_symmetric"] == Fraction(5, 9)
    assert more.values["anonymous_symmetric"] == Fraction(171, 308)
    assert more.values["anonymous_symmetric"] < less.values["anonymous_symmetric"]
    for rule in (
        "best_pure",
        "worst_pure",
        "uniform_potential_maximum",
        "uniform_strict_best_response_basin",
        "planner",
    ):
        assert less.values[rule] == Fraction(2, 3)
        assert more.values[rule] == Fraction(3, 4)


def test_selection_refinement_census_counts_are_exact() -> None:
    likelihood, catalogue = _catalogue()
    certificate = selection_certificate(likelihood, catalogue, refinement_comparisons(catalogue))
    assert certificate["refinement_counts"] == {
        "anonymous_symmetric": {"harmful": 1, "improving": 43, "tied": 1},
        "best_pure": {"harmful": 0, "improving": 35, "tied": 10},
        "worst_pure": {"harmful": 8, "improving": 24, "tied": 13},
        "uniform_potential_maximum": {"harmful": 2, "improving": 35, "tied": 8},
        "uniform_strict_best_response_basin": {
            "harmful": 2,
            "improving": 35,
            "tied": 8,
        },
        "planner": {"harmful": 0, "improving": 35, "tied": 10},
    }


def test_independent_selection_certificate_verifier_rejects_corruption() -> None:
    likelihood, catalogue = _catalogue()
    certificate = selection_certificate(likelihood, catalogue, refinement_comparisons(catalogue))
    assert verify_selection_certificate(certificate) == []
    corrupted = copy.deepcopy(certificate)
    corrupted["partitions"][0]["messages"][0]["absorption_by_initial"][0]["absorption"][0][
        "probability"
    ] = "0"
    errors = verify_selection_certificate(corrupted)
    assert any("absorption" in error for error in errors)
