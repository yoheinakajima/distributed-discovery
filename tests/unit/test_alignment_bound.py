import copy
from fractions import Fraction

import pytest

from distributed_discovery.private_teams.alignment_bound import (
    alignment_bound_certificate,
    alignment_count_bound,
    local_failure_floor,
)
from distributed_discovery.private_teams.alignment_bound_verification import (
    verify_alignment_bound_certificate,
)


def test_canonical_local_failure_floor_uses_exact_signal_law() -> None:
    assert local_failure_floor(16, Fraction(1, 5), 0) == 1
    assert local_failure_floor(16, Fraction(1, 5), 1) == Fraction(4, 5)
    assert local_failure_floor(16, Fraction(1, 5), 2) == Fraction(56, 75)
    assert local_failure_floor(16, Fraction(1, 5), 16) == 0


@pytest.mark.parametrize(
    ("candidates", "searchers", "accuracy", "expected"),
    [
        (3, 2, Fraction(2, 5), Fraction(7, 10)),
        (4, 2, Fraction(3, 10), Fraction(8, 15)),
        (3, 2, Fraction(0), Fraction(1)),
        (4, 2, Fraction(0), Fraction(2, 3)),
    ],
)
def test_alignment_relaxation_matches_known_exact_or_upper_values(
    candidates: int, searchers: int, accuracy: Fraction, expected: Fraction
) -> None:
    assert alignment_count_bound(candidates, searchers, accuracy).discovery_upper_bound == expected


def test_canonical_relaxation_matches_attainable_direct_policy() -> None:
    result = alignment_count_bound(16, 8, Fraction(1, 5))
    assert result.discovery_upper_bound == Fraction(325089, 390625)
    assert result.average_failure_lower_bound == Fraction(4, 5) ** 8
    assert result.target_resource_pattern == (8,) * 16


def test_independent_bellman_verifier_rejects_corruption() -> None:
    certificate = alignment_bound_certificate(alignment_count_bound(4, 2, Fraction(3, 10)))
    assert verify_alignment_bound_certificate(certificate) == []
    corrupted = copy.deepcopy(certificate)
    corrupted["target_dp"]["values"][-1][-1] = "0"
    errors = verify_alignment_bound_certificate(corrupted)
    assert errors
    assert any("target Bellman" in error or "average failure" in error for error in errors)
