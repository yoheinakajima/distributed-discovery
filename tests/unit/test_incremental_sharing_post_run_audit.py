from fractions import Fraction
from math import comb
from pathlib import Path

import yaml

from distributed_discovery.incremental_sharing.model import compositions, multinomial

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "studies/DD-020-incremental-sharing/configs/census.yml"


def count_method_mass_and_tie(
    targets: int, block_size: int, accuracy: Fraction
) -> tuple[Fraction, Fraction]:
    wrong = (1 - accuracy) / (targets - 1)
    mass = Fraction()
    tie = Fraction()
    for counts in compositions(block_size, targets):
        probability = (
            multinomial(counts) * accuracy ** counts[0] * wrong ** (block_size - counts[0])
        )
        mass += probability
        if accuracy == Fraction(1, targets) or counts.count(max(counts)) > 1:
            tie += probability
    return mass, tie


def conditioned_method_mass_and_tie(
    targets: int, block_size: int, accuracy: Fraction
) -> tuple[Fraction, Fraction]:
    mass = Fraction()
    tie = Fraction()
    for correct in range(block_size + 1):
        wrong_total = block_size - correct
        correct_mass = comb(block_size, correct) * accuracy**correct * (1 - accuracy) ** wrong_total
        occupancy_mass = Fraction()
        occupancy_tie = Fraction()
        for wrong_counts in compositions(wrong_total, targets - 1):
            probability = Fraction(multinomial(wrong_counts), (targets - 1) ** wrong_total)
            occupancy_mass += probability
            counts = (correct, *wrong_counts)
            if accuracy == Fraction(1, targets) or counts.count(max(counts)) > 1:
                occupancy_tie += probability
        mass += correct_mass * occupancy_mass
        tie += correct_mass * occupancy_tie
    return mass, tie


def test_every_registered_point_distribution_normalizes_and_tie_methods_agree() -> None:
    config = yaml.safe_load(CONFIG.read_text())
    for targets in config["targets"]:
        for accuracy_text in config["accuracies_by_targets"][targets]:
            accuracy = Fraction(accuracy_text)
            for block_size in range(1, max(config["agents"]) + 1):
                count_mass, count_tie = count_method_mass_and_tie(targets, block_size, accuracy)
                conditioned_mass, conditioned_tie = conditioned_method_mass_and_tie(
                    targets, block_size, accuracy
                )
                assert count_mass == conditioned_mass == 1
                assert count_tie == conditioned_tie
