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


def test_partition_generator_matches_small_bell_numbers() -> None:
    assert [len(canonical_partitions(size)) for size in range(1, 6)] == [1, 2, 5, 15, 52]


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

    second_weight, second_posterior = message_posterior(likelihood, (2, 3))
    assert second_weight == Fraction(3, 8)
    assert second_posterior == (Fraction(1, 3), Fraction(2, 9), Fraction(4, 9))
    assert symmetric_equilibrium(second_posterior).discovery == Fraction(4, 7)
    assert {equilibrium.discovery for equilibrium in pure_equilibria(second_posterior)} == {
        Fraction(7, 9)
    }

    pooled_weight, pooled_posterior = message_posterior(likelihood, (0, 1, 2, 3))
    assert pooled_weight == 1
    assert pooled_posterior == (Fraction(1, 3),) * 3
    assert symmetric_equilibrium(pooled_posterior).discovery == Fraction(5, 9)
    assert {equilibrium.discovery for equilibrium in pure_equilibria(pooled_posterior)} == {
        Fraction(2, 3)
    }

    selected_fine = weight * Fraction(6, 11) + second_weight * Fraction(4, 7)
    pure_fine = weight * Fraction(11, 15) + second_weight * Fraction(7, 9)
    assert selected_fine == Fraction(171, 308) < Fraction(5, 9)
    assert pure_fine == Fraction(3, 4) > Fraction(2, 3)
