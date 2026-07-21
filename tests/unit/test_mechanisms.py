from distributed_discovery.mechanisms.model import check_truthful_direct
from distributed_discovery.mechanisms.verification import ex_post_balance_passes


def test_score_difference_transfers_are_ex_post_budget_balanced() -> None:
    assert ex_post_balance_passes()


def test_positive_target_scoring_supports_weak_but_not_strict_truthful_direct_equilibrium() -> None:
    result = check_truthful_direct("target-identity", 1)
    assert result["pure_bne"]
    assert not result["strict"]
