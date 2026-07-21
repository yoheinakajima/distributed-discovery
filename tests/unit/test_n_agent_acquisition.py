from fractions import Fraction

from distributed_discovery.acquisition.n_agent import discovery, gross_payoffs, planner
from distributed_discovery.acquisition.n_agent_verification import direct


def test_closed_form_matches_direct_enumerator_and_prize_accounting() -> None:
    p, c = Fraction(2, 3), Fraction(1, 8)
    for n in range(2, 5):
        for k in range(n + 1):
            net, independent, common = direct(n, k, p, c)
            gross_i, gross_c = gross_payoffs(n, k, p)
            assert net == discovery(n, k, p) - k * c
            assert independent == (gross_i - c if gross_i is not None else 0)
            assert common == (gross_c if gross_c is not None else 0)
            assert (k * (gross_i or 0) + (n - k) * (gross_c or 0)) == discovery(n, k, p)


def test_two_agent_planner_recovers_one_independent_source() -> None:
    assert planner(2, Fraction(2, 3), Fraction(1, 8)) == [1]


def test_corrupted_direct_discovery_is_rejected() -> None:
    p, c = Fraction(2, 3), Fraction(1, 8)
    net, _, _ = direct(3, 1, p, c)
    assert net + Fraction(1, 100) != discovery(3, 1, p) - c
