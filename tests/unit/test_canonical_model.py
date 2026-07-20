from fractions import Fraction

import pytest

from distributed_discovery.canonical.model import (
    blind_discovery,
    independent_count_frontier,
    posterior_from_counts,
    private_discovery,
    private_expected_distinct,
    tiny_consensus_bruteforce,
)


def test_blind_and_private_closed_forms() -> None:
    assert blind_discovery(16, 8) == Fraction(1, 2)
    assert private_discovery(8, Fraction(1, 5)) == 1 - Fraction(4, 5) ** 8
    assert float(private_discovery(8, Fraction(1, 5))) == pytest.approx(0.83222784)


def test_posterior_normalizes_and_respects_relabeling() -> None:
    posterior = posterior_from_counts((2, 1, 0), Fraction(1, 2))
    relabeled = posterior_from_counts((0, 2, 1), Fraction(1, 2))
    assert sum(posterior) == 1
    assert posterior == (relabeled[1], relabeled[2], relabeled[0])


def test_tiny_consensus_matches_independent_count_enumeration() -> None:
    exact = tiny_consensus_bruteforce(3, 2, Fraction(1, 2))
    frontier, normalization = independent_count_frontier(3, 2, 0.5)
    assert normalization == pytest.approx(1.0, abs=1e-14)
    assert frontier[0] == pytest.approx(float(exact), abs=1e-14)
    assert 0.0 <= frontier[0] <= frontier[1] <= 1.0


def test_canonical_independent_frontier_and_distinct_actions() -> None:
    frontier, normalization = independent_count_frontier(16, 8, 0.2)
    assert normalization == pytest.approx(1.0, abs=3e-12)
    assert frontier[0] == pytest.approx(0.383468709731, abs=5e-12)
    assert frontier[-1] == pytest.approx(0.859421246199, abs=5e-12)
    expected_distinct = private_expected_distinct(16, 8, Fraction(1, 5))
    assert float(expected_distinct) == pytest.approx(6.156849828175, abs=5e-13)
