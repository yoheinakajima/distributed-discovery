from fractions import Fraction

from distributed_discovery.coverage.model import exact_frontier, greedy, top_individual
from distributed_discovery.coverage.verification import verify_exact


def test_duplicate_high_rank_actions_are_not_an_optimal_portfolio() -> None:
    weights = (Fraction(1),) * 4
    actions = (frozenset({0, 1, 2}), frozenset({0, 1, 2}), frozenset({3}))
    assert top_individual(weights, actions, 2)[1] == 3
    assert exact_frontier(weights, actions, 2)[1] == 4
    assert exact_frontier(weights, actions, 2) == verify_exact(weights, actions, 2)


def test_greedy_can_miss_exact_weighted_coverage_frontier() -> None:
    weights = (Fraction(1),) * 6
    actions = (frozenset({0, 1, 2, 3}), frozenset({0, 1, 4}), frozenset({2, 3, 5}))
    assert greedy(weights, actions, 2)[1] == 5
    assert exact_frontier(weights, actions, 2)[1] == 6
