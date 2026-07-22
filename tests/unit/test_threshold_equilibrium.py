from fractions import Fraction

from distributed_discovery.threshold_equilibrium.model import (
    evaluate_game,
    pure_nash_occupancies,
    strict_coalition_witness,
    symmetric_mixed_equilibrium_check,
    tied_mode_distribution,
)
from distributed_discovery.threshold_equilibrium.verification import (
    aggregate_strict_coalition_block_exists,
    labeled_pure_nash_occupancies,
)


def test_threshold_two_two_agent_coordination_equilibria() -> None:
    posterior = (Fraction(1, 2), Fraction(1, 2))
    equilibria = pure_nash_occupancies(posterior, 2, 2)
    assert equilibria == ((0, 2), (2, 0))
    assert labeled_pure_nash_occupancies(posterior, 2, 2) == equilibria


def test_three_agent_full_crowd_is_nash_but_pair_blocked() -> None:
    posterior = (Fraction(1, 2), Fraction(1, 2))
    assert pure_nash_occupancies(posterior, 3, 2) == ((0, 3), (3, 0))
    witness = strict_coalition_witness((3, 0), posterior, 2, 2)
    assert witness is not None
    assert witness["new_occupancy"] == (1, 2)
    assert witness["old_payoffs"] == (Fraction(1, 6), Fraction(1, 6))
    assert witness["new_payoffs"] == (Fraction(1, 4), Fraction(1, 4))
    assert aggregate_strict_coalition_block_exists((3, 0), posterior, 2, 2)


def test_four_agent_balanced_teams_are_pairwise_stable() -> None:
    posterior = (Fraction(1, 2), Fraction(1, 2))
    game = evaluate_game("uniform-two", posterior, 4, 2)
    balanced = next(row for row in game["pure_nash"] if row["occupancy"] == (2, 2))
    assert balanced["pairwise_strict_stable"] is True
    assert not aggregate_strict_coalition_block_exists((2, 2), posterior, 2, 2)
    assert game["planner_discovery"] == game["best_equilibrium_discovery"] == 1


def test_tied_mode_mixture_can_fail_at_tau_one_but_pass_at_tau_two() -> None:
    posterior = (Fraction(7, 20), Fraction(7, 20), Fraction(3, 10))
    mixture = tied_mode_distribution(posterior)
    tau_one = symmetric_mixed_equilibrium_check(posterior, 2, 1, mixture)
    tau_two = symmetric_mixed_equilibrium_check(posterior, 2, 2, mixture)
    assert tau_one["is_equilibrium"] is False
    assert tau_one["action_payoffs"][2] > tau_one["support_payoff"]
    assert tau_two["is_equilibrium"] is True
