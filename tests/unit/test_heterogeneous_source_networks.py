from fractions import Fraction

from distributed_discovery.source_networks.heterogeneous import (
    accuracy_assignments,
    canonical_colored,
    colored_network,
    complete_moment_signature,
    enumerate_colored_networks,
    exact_action_moments,
    exact_private_discovery,
    signal_probability,
)
from distributed_discovery.source_networks.heterogeneous_verification import (
    verify_pairwise_counterexample,
)


def test_accuracy_assignments_require_every_registered_color() -> None:
    levels = (Fraction(1, 2), Fraction(2, 3))
    assert accuracy_assignments(levels, 2) == [
        (Fraction(1, 2), Fraction(2, 3)),
        (Fraction(2, 3), Fraction(1, 2)),
    ]
    assert len(accuracy_assignments(levels, 3)) == 6


def test_colored_canonicalization_carries_accuracy_with_source_row() -> None:
    left = colored_network(((0, 0, 0, 1), (1, 1, 1, 1)), (Fraction(1, 2), Fraction(2, 3)))
    source_relabeled = colored_network(
        ((1, 1, 1, 1), (0, 0, 0, 1)), (Fraction(2, 3), Fraction(1, 2))
    )
    colors_swapped_without_rows = colored_network(
        ((0, 0, 0, 1), (1, 1, 1, 1)), (Fraction(2, 3), Fraction(1, 2))
    )
    assert canonical_colored(left) == canonical_colored(source_relabeled)
    assert canonical_colored(left) != canonical_colored(colors_swapped_without_rows)


def test_heterogeneous_signal_law_and_first_moments_normalize() -> None:
    network = colored_network(((1, 1, 0, 0), (0, 0, 1, 1)), (Fraction(1, 3), Fraction(5, 6)))
    total = sum(
        signal_probability(target, signals, (Fraction(1, 3), Fraction(5, 6)))
        for target in range(3)
        for signals in ((a, b) for a in range(3) for b in range(3))
    )
    first, _ = exact_action_moments(network)
    assert total == 1
    assert all(value == Fraction(1, 3) for row in first for value in row)


def test_registered_colored_orbit_counts() -> None:
    assert len(enumerate_colored_networks((Fraction(2, 3),), 2, 4)) == 8
    assert len(enumerate_colored_networks((Fraction(1, 2), Fraction(2, 3)), 2, 4)) == 13
    assert (
        len(enumerate_colored_networks((Fraction(1, 3), Fraction(2, 3), Fraction(5, 6)), 3, 4))
        == 168
    )


def test_complete_pairwise_moments_do_not_determine_discovery() -> None:
    left = canonical_colored(
        colored_network(
            ((0, 0, 0, 1), (1, 1, 1, 1)),
            (Fraction(1, 2), Fraction(2, 3)),
        )
    )
    right = canonical_colored(
        colored_network(
            ((1, 1, 1, 1), (0, 0, 0, 1)),
            (Fraction(1, 2), Fraction(2, 3)),
        )
    )
    assert complete_moment_signature(left) == complete_moment_signature(right)
    assert exact_private_discovery(left) == Fraction(3, 4)
    assert exact_private_discovery(right) == Fraction(2, 3)

    witness = {
        "left": {
            "accuracies": [str(value) for value, _ in left],
            "adjacency": [list(row) for _, row in left],
        },
        "right": {
            "accuracies": [str(value) for value, _ in right],
            "adjacency": [list(row) for _, row in right],
        },
        "left_private_discovery": "3/4",
        "right_private_discovery": "2/3",
        "private_discovery_difference": "1/12",
    }
    assert verify_pairwise_counterexample(witness)
    witness["private_discovery_difference"] = "0"
    assert not verify_pairwise_counterexample(witness)
