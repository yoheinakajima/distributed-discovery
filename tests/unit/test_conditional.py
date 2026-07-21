from __future__ import annotations

from fractions import Fraction

from distributed_discovery.conditional.model import (
    POLICY_TYPES,
    anonymous_profiles,
    evaluate_profile,
    evaluate_raw_ordered,
    policy_action,
)
from distributed_discovery.conditional.study import build_bundle
from distributed_discovery.conditional.verification import (
    corruption_tests,
    direct_profile,
    direct_raw,
    verify_bundle,
)


def test_policy_class_and_anonymous_profile_counts() -> None:
    assert len(POLICY_TYPES) == 3
    assert [len(anonymous_profiles(n)) for n in (2, 3, 4)] == [6, 10, 15]
    for label in range(3):
        assert all(policy_action(policy, label, label) == label for policy in POLICY_TYPES)
    assert policy_action("contrarian", 0, 1) == 2


def test_primary_and_independent_profile_evaluators_match() -> None:
    p, q = Fraction(1, 2), Fraction(3, 4)
    for counts in anonymous_profiles(3):
        assert evaluate_profile(counts, p, q) == direct_profile(counts, p, q)


def test_raw_primary_and_independent_evaluators_match() -> None:
    p, q = Fraction(2, 3), Fraction(3, 4)
    for policies in ((0, 15), (12, 10), (5, 9), (15, 0)):
        assert evaluate_raw_ordered(policies, p, q) == direct_raw(policies, p, q)


def test_small_bundle_verifies_and_rejects_corruptions() -> None:
    bundle = build_bundle(
        {"agents": [2], "accuracies": ["1/2", "3/4"], "raw_audit_accuracies": ["2/3"]}
    )
    assert bundle["summary"]["grid_cells"] == 4
    assert bundle["summary"]["anonymous_profiles"] == 24
    assert bundle["theorem_checks"]["raw_audit_exposes_restricted_class_gap"] is True
    assert verify_bundle(bundle)["passed"] is True
    assert all(corruption_tests(bundle).values())
