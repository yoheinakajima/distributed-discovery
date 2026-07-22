from fractions import Fraction

from distributed_discovery.dynamic_attention.threshold_extension import (
    enumerate_threshold_policy,
    solve_threshold_planner,
)


def test_threshold_two_planner_matches_labeled_tree() -> None:
    for objective in ("fixed-budget", "stopping-on-success"):
        planner = solve_threshold_planner(Fraction(1, 2), Fraction(2, 3), objective)
        direct = enumerate_threshold_policy(
            Fraction(1, 2), Fraction(2, 3), objective, planner["policy"]
        )
        assert direct["probability_mass"] == 1
        assert direct["discovery"] == planner["discovery"]
        assert direct["expected_actions"] == planner["expected_actions"]


def test_threshold_two_policy_exercises_team_action_categories() -> None:
    planner = solve_threshold_planner(Fraction(1, 2), Fraction(2, 3), "fixed-budget")
    direct = enumerate_threshold_policy(
        Fraction(1, 2), Fraction(2, 3), "fixed-budget", planner["policy"]
    )
    assert direct["category_mass"]["start-new-singleton"] > 0
    assert direct["category_mass"]["join-singleton"] > 0
    assert direct["category_mass"]["follow-shared-clue"] > 0
    assert direct["category_mass"]["oppose-shared-clue"] > 0
