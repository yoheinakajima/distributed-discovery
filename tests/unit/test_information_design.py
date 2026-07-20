from fractions import Fraction

from distributed_discovery.information_design.game import (
    canonical_partitions,
    message_posterior,
    planner_discovery,
    pure_equilibria,
    refines,
    symmetric_equilibrium,
)


def test_four_state_partition_registry_is_complete() -> None:
    partitions = canonical_partitions(4)
    assert len(partitions) == 15
    assert len(set(partitions)) == 15
    assert refines(((0,), (1,), (2,), (3,)), ((0, 1), (2, 3)))
    assert not refines(((0, 2), (1, 3)), ((0, 1), (2, 3)))


def test_fixture_reversal_posteriors_and_equilibria() -> None:
    likelihood = (
        (Fraction(1, 2), Fraction(1, 8), Fraction(1, 8), Fraction(1, 4)),
        (Fraction(1, 4), Fraction(1, 2), Fraction(1, 8), Fraction(1, 8)),
        (Fraction(1, 8), Fraction(3, 8), Fraction(1, 8), Fraction(3, 8)),
    )
    weight, posterior = message_posterior(likelihood, (0, 1))
    assert weight == Fraction(5, 8)
    assert posterior == (Fraction(1, 3), Fraction(2, 5), Fraction(4, 15))
    assert symmetric_equilibrium(posterior).discovery == Fraction(6, 11)
    assert {equilibrium.discovery for equilibrium in pure_equilibria(posterior)} == {
        Fraction(11, 15)
    }
    assert planner_discovery(posterior) == Fraction(11, 15)
