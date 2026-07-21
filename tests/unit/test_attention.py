from __future__ import annotations

from fractions import Fraction

import pytest

from distributed_discovery.attention.model import (
    STRATEGIC_REWARD_RULES,
    discovery,
    equal_split_payoffs,
    equilibrium,
    private_attention_value,
    reward_equilibrium,
    reward_payoffs,
    social_attention_value,
    social_optima,
)
from distributed_discovery.attention.study import build_bundle
from distributed_discovery.attention.verification import (
    corruption_tests,
    direct_profile,
    verify_bundle,
)


@pytest.mark.parametrize("n", range(2, 9))
def test_one_reader_discovery_theorem(n: int) -> None:
    p = Fraction(1, 2)
    high = Fraction(3, 4)
    low = Fraction(1, 3)
    assert social_optima(n, p, high) == [1]
    assert social_optima(n, p, low) == [0]
    assert social_optima(n, p, p) == [0, 1]
    assert all(discovery(n, k, p, high) > discovery(n, k + 1, p, high) for k in range(1, n))


def test_payoff_accounting_and_direct_enumerator_agree() -> None:
    n, p, q = 4, Fraction(1, 2), Fraction(3, 4)
    for k in range(n + 1):
        attending, ignoring = equal_split_payoffs(n, k, p, q)
        assert k * (attending or 0) + (n - k) * (ignoring or 0) == discovery(n, k, p, q)
        direct = direct_profile(n, k, p, q)
        assert direct["probability_mass"] == 1
        assert direct["discovery"] == discovery(n, k, p, q)
        assert direct["rules"]["equal-split"]["attending"] == attending
        assert direct["rules"]["equal-split"]["ignoring"] == ignoring


def test_private_attention_thresholds_are_strictly_decreasing() -> None:
    n, p, q = 8, Fraction(2, 3), Fraction(5, 6)
    margins = [private_attention_value(n, k, p, q) for k in range(n)]
    assert all(left > right for left, right in zip(margins, margins[1:], strict=False))
    equilibria = [k for k in range(n + 1) if equilibrium(n, k, p, q)[0]]
    assert len(equilibria) in {1, 2}
    assert equilibria == list(range(equilibria[0], equilibria[-1] + 1))


def test_boundary_characterizations_and_wedge() -> None:
    n, p = 3, Fraction(1, 2)
    q = Fraction(3, 4)
    assert private_attention_value(n, 0, p, q) > 0
    assert 0 not in [k for k in range(n + 1) if equilibrium(n, k, p, q)[0]]
    assert social_attention_value(n, 0, p, q) > 0
    assert social_attention_value(n, 1, p, q) < 0
    threshold = Fraction(n) * p / (1 + (n - 1) * p)
    assert equilibrium(n, n, p, threshold)[0]


def test_reward_rules_and_atomic_identity() -> None:
    n, k, p, q = 3, 1, Fraction(1, 2), Fraction(3, 4)
    sole = reward_payoffs("sole-rescue", n, k, p, q)
    marginal = reward_payoffs("marginal-coverage", n, k, p, q)
    assert sole == marginal
    for rule in STRATEGIC_REWARD_RULES:
        direct = direct_profile(n, k, p, q)["rules"][rule]
        closed = reward_payoffs(rule, n, k, p, q)
        assert direct["attending"] == closed[0]
        assert direct["ignoring"] == closed[1]
        assert direct["budget"] == closed[2]
        assert isinstance(reward_equilibrium(rule, n, k, p, q)[0], bool)


def test_small_bundle_verifies_and_rejects_corruption() -> None:
    bundle = build_bundle({"agents": [2, 3], "accuracies": ["1/2", "3/4"]})
    result = verify_bundle(bundle)
    assert result["passed"] is True
    assert result["profiles_verified"] == 28
    assert all(corruption_tests(bundle).values())
