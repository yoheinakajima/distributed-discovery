from fractions import Fraction

from distributed_discovery.acquisition.verification import agrees

from distributed_discovery.acquisition.model import equilibria, planner


def test_direct_enumerator_matches_closed_forms() -> None:
    assert all(
        agrees(profile, Fraction(2, 3), Fraction(1, 12)) for profile in ("CC", "CI", "IC", "II")
    )


def test_common_source_trap_interval_witness() -> None:
    accuracy, cost = Fraction(2, 3), Fraction(1, 8)
    assert equilibria(accuracy, cost) == ["CC"]
    assert set(planner(accuracy, cost) == ["CI", "IC"] for _ in [0]) == {True}
