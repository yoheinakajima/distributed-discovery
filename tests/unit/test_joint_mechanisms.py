from copy import deepcopy
from fractions import Fraction

from distributed_discovery.mechanisms.joint import (
    coefficient_vectors,
    frontier_row,
    information_score,
    truthful_discovery,
)
from distributed_discovery.mechanisms.joint_verification import verify_row


def test_brier_score_and_registered_grid() -> None:
    assert information_score(0, 0) > information_score(1, 0)
    assert len(coefficient_vectors()) == 15
    assert truthful_discovery(0) == truthful_discovery(1) == Fraction(11, 12)


def test_joint_frontier_certificate_and_corruption() -> None:
    row = frontier_row("target-actions", coefficient_vectors()[0])
    assert verify_row(row)
    bad = deepcopy(row)
    bad["all_tie_margin"] = "99"
    assert not verify_row(bad)
    accounting = row["accounting_by_tie_role"]
    assert all(item["participation"] for item in accounting)
    assert all(Fraction(item["worst_case_abs_transfer"]) >= 0 for item in accounting)
    bad_accounting = deepcopy(row)
    bad_accounting["accounting_by_tie_role"][0]["expected_total_transfer"] = "99"
    assert not verify_row(bad_accounting)
    certificates = row["deviation_certificates_by_tie_role"]
    assert all("report_only_margin" in item for item in certificates)
    assert all("action_only_margin" in item for item in certificates)
