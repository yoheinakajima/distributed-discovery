from fractions import Fraction

from distributed_discovery.dynamic_attention.model import solve_protocol
from distributed_discovery.dynamic_attention.verification import enumerate_policy


def test_visible_action_protocols_normalize_and_match_direct_tree() -> None:
    for objective in ("fixed-budget", "stopping-on-success"):
        result = solve_protocol(2, Fraction(1, 2), Fraction(2, 3), objective, "autonomous")
        direct = enumerate_policy(
            2,
            Fraction(1, 2),
            Fraction(2, 3),
            objective,
            result["policy"],
        )
        assert direct["probability_mass"] == 1
        assert direct["discovery"] == result["discovery"]
        assert direct["expected_actions"] == result["expected_actions"]


def test_planner_weakly_dominates_full_credit_equilibrium() -> None:
    for objective in ("fixed-budget", "stopping-on-success"):
        autonomous = solve_protocol(3, Fraction(1, 2), Fraction(2, 3), objective, "autonomous")
        planner = solve_protocol(3, Fraction(1, 2), Fraction(2, 3), objective, "planner")
        assert planner["discovery"] >= autonomous["discovery"]


def test_stopping_preserves_discovery_and_uses_fewer_actions_for_private_control() -> None:
    fixed = solve_protocol(2, Fraction(1, 3), Fraction(1, 3), "fixed-budget", "planner")
    stopping = solve_protocol(2, Fraction(1, 3), Fraction(1, 3), "stopping-on-success", "planner")
    assert fixed["discovery"] == stopping["discovery"]
    assert stopping["expected_actions"] < fixed["expected_actions"]
