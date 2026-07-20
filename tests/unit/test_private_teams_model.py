from fractions import Fraction

from distributed_discovery.private_teams.model import (
    direct_profile,
    direct_value,
    evaluate_direct,
    evaluate_formula,
    pooled_planner_value,
    territorial_profile,
)
from distributed_discovery.private_teams.study import _sanitize_package_snapshot


def test_formula_matches_direct_enumeration_and_normalizes() -> None:
    profile = ((0, 2, 1), (1, 1, 2))
    formula = evaluate_formula(profile, 3, Fraction(2, 3))
    direct, normalization = evaluate_direct(profile, 3, Fraction(2, 3))
    assert normalization == 1
    assert direct == formula


def test_direct_policy_has_hand_checkable_formula() -> None:
    profile = direct_profile(3, 2)
    assert evaluate_formula(profile, 3, Fraction(1, 2)) == direct_value(2, Fraction(1, 2))
    assert evaluate_formula(profile, 3, Fraction(1, 2)) == Fraction(3, 4)


def test_uninformative_two_agent_territories_discover_binary_target() -> None:
    profile = territorial_profile(2, 2)
    value, normalization = evaluate_direct(profile, 2, Fraction(1, 2))
    assert normalization == 1
    assert value == 1


def test_pooled_planner_dominates_fixed_private_profile() -> None:
    accuracy = Fraction(2, 3)
    private = evaluate_formula(direct_profile(3, 2), 3, accuracy)
    assert pooled_planner_value(3, 2, accuracy) >= private


def test_package_snapshot_omits_private_local_project_url() -> None:
    lines = [
        "attrs==26.1.0",
        "distributed-discovery @ file:///private/checkout/distributed-discovery",
    ]
    assert _sanitize_package_snapshot(lines) == ["attrs==26.1.0"]
