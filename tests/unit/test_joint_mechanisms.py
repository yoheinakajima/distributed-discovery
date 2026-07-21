from copy import deepcopy

from distributed_discovery.mechanisms.joint import (
    coefficient_vectors,
    frontier_row,
    information_score,
)
from distributed_discovery.mechanisms.joint_verification import verify_row


def test_brier_score_and_registered_grid() -> None:
    assert information_score(0, 0) > information_score(1, 0)
    assert len(coefficient_vectors()) == 15


def test_joint_frontier_certificate_and_corruption() -> None:
    row = frontier_row("target-actions", coefficient_vectors()[0])
    assert verify_row(row)
    bad = deepcopy(row)
    bad["all_tie_margin"] = "99"
    assert not verify_row(bad)
