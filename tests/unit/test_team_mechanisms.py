from fractions import Fraction

from distributed_discovery.team_mechanisms.model import (
    MECHANISMS,
    discovery,
    evaluate_mechanism,
    planner_profile,
)


def _row(name: str, posterior: tuple[Fraction, ...]) -> dict[str, object]:
    spec = next(candidate for candidate in MECHANISMS if candidate.name == name)
    return evaluate_mechanism(spec, posterior, 4, 2)


def test_planner_profile_opens_top_two_minimum_teams() -> None:
    posterior = (Fraction(1, 2), Fraction(3, 10), Fraction(1, 5))
    profile = planner_profile(posterior, 4, 2)
    assert profile == (0, 0, 1, 1)
    assert discovery(profile, posterior, 2) == Fraction(4, 5)


def test_team_tokens_support_strict_budget_safe_planner_portfolio() -> None:
    row = _row("team-tokens", (Fraction(3, 5), Fraction(1, 4), Fraction(3, 20)))
    assert row["implements_planner_portfolio"] is True
    assert row["obedience"] is True
    assert row["strict_unilateral_obedience"] is True
    assert row["pairwise_strict_stable"] is True
    assert row["weak_budget_balance"] is True
    assert row["external_subsidy"] == 0


def test_universal_pooling_is_not_the_planner_portfolio() -> None:
    posterior = (Fraction(1, 2), Fraction(3, 10), Fraction(1, 5))
    row = _row("universal-pooling", posterior)
    assert row["expected_discovery"] == Fraction(1, 2)
    assert row["planner_discovery"] == Fraction(4, 5)
    assert row["implements_planner_portfolio"] is False


def test_nonbinding_mediator_can_fail_obedience_on_steep_fixture() -> None:
    row = _row(
        "correlated-mediator",
        (Fraction(3, 5), Fraction(1, 4), Fraction(3, 20)),
    )
    assert row["implements_planner_portfolio"] is True
    assert row["obedience"] is False
    assert row["strict_unilateral_obedience"] is False


def test_authority_is_not_labeled_coalition_stability() -> None:
    row = _row("central-assignment", (Fraction(1, 3),) * 3)
    assert row["obedience"] == "not-applicable-authoritative-commitment"
    assert row["pairwise_strict_stable"] == "not-applicable-authoritative-commitment"
    assert row["tau_player_strict_stable"] == "not-applicable-authoritative-commitment"
    assert row["equilibrium_multiplicity"] == "not-applicable-authoritative-commitment"
