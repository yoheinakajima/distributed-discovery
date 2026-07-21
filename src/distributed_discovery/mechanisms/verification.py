"""Independent accounting check for the DD-006 transfer family."""

from __future__ import annotations

from itertools import product

from distributed_discovery.mechanisms.model import REGIMES, utility


def ex_post_balance_passes() -> bool:
    """Check that every realized transfer pair sums to zero exactly."""
    for (
        regime,
        coefficient,
        target,
        first_report,
        first_action,
        second_report,
        second_action,
    ) in product(REGIMES, (-1, 0, 1), range(3), range(3), range(3), range(3), range(3)):
        first = utility(
            regime,
            coefficient,
            target,
            first_report,
            first_action,
            second_report,
            second_action,
        )
        second = utility(
            regime,
            coefficient,
            target,
            second_report,
            second_action,
            first_report,
            first_action,
        )
        if first + second != 0:
            return False
    return True
