from fractions import Fraction

from distributed_discovery.sequential.model import (
    dynamic_optimum,
    evaluate_schedule,
    ordered_compositions,
)
from distributed_discovery.sequential.verification import enumerate_sequences


def test_compositions_of_four_cover_parallel_to_sequential() -> None:
    assert ordered_compositions(4) == (
        (4,),
        (1, 3),
        (2, 2),
        (1, 1, 2),
        (3, 1),
        (1, 2, 1),
        (2, 1, 1),
        (1, 1, 1, 1),
    )


def test_perfect_elimination_preserves_terminal_discovery_and_reduces_actions() -> None:
    prior = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    parallel = evaluate_schedule(prior, 3, (3,))
    sequential = evaluate_schedule(prior, 3, (1, 1, 1))
    assert parallel["terminal_discovery"] == sequential["terminal_discovery"] == 1
    assert sequential["expected_actions"] < parallel["expected_actions"]
    assert sequential["expected_rounds"] > parallel["expected_rounds"]


def test_dp_matches_independent_policy_path_enumerator() -> None:
    prior = (Fraction(1, 4), Fraction(1, 4), Fraction(1, 4), Fraction(1, 4))
    for schedule in ordered_compositions(4):
        assert dynamic_optimum(prior, 4, schedule) == enumerate_sequences(prior, 4, schedule)
