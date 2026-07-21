import csv
import json
from fractions import Fraction
from pathlib import Path

import yaml

from distributed_discovery.information_design.game import Likelihood
from distributed_discovery.information_design.selection import (
    PartitionSelection,
    evaluate_catalogue,
    refinement_comparisons,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE_RUN = ROOT / "results/verified/20260720T225848Z_DD-002_94607423_e29b1460ae"


def _catalogue() -> tuple[PartitionSelection, ...]:
    config = yaml.safe_load(
        (ROOT / "studies/DD-002-information-design/configs/selection-robustness.yml").read_text(
            encoding="utf-8"
        )
    )
    likelihood: Likelihood = tuple(
        tuple(Fraction(value) for value in row) for row in config["likelihood"]
    )
    return evaluate_catalogue(likelihood)


def test_selection_extension_preserves_every_frozen_partition_value() -> None:
    catalogue = _catalogue()
    previous = {
        row["partition_id"]: row
        for row in csv.DictReader(
            (SOURCE_RUN / "outputs/partition-summary.csv").open(encoding="utf-8")
        )
    }
    registry = json.loads(
        (SOURCE_RUN / "outputs/equilibrium-registry.json").read_text(encoding="utf-8")
    )
    assert len(catalogue) == len(previous) == len(registry) == 15
    assert sum(len(item.messages) for item in catalogue) == 37
    assert sum(item["global_pure_equilibrium_count"] for item in registry) == 256
    for item in catalogue:
        row = previous[item.partition_id]
        assert item.values["anonymous_symmetric"] == Fraction(row["selected_discovery"])
        assert item.values["best_pure"] == Fraction(row["best_pure_discovery"])
        assert item.values["worst_pure"] == Fraction(row["worst_pure_discovery"])
        assert item.values["planner"] == Fraction(row["planner_discovery"])


def test_all_refinements_and_branch_dependence_are_retained() -> None:
    catalogue = _catalogue()
    assert len(refinement_comparisons(catalogue)) == 45
    assert sum(item.potential_multiple_discovery_values for item in catalogue) == 5
    assert sum(item.basin_branch_dependent for item in catalogue) == 5
    assert all(
        item.values["uniform_potential_maximum"]
        == item.values["uniform_strict_best_response_basin"]
        for item in catalogue
    )
