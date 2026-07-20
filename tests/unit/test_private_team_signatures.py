import itertools
from fractions import Fraction

from distributed_discovery.private_teams.model import evaluate_formula
from distributed_discovery.private_teams.signatures import (
    all_feasible_signatures,
    canonicalize_signature,
    evaluate_signatures_reference,
    evaluate_signatures_scaled,
    exhaustive_signature_optimum,
    feasible_signature_count,
    raw_policy_multiplicities,
    reduced_feasibility,
    reference_feasibility,
    signature_from_policy,
    target_orbit_signature_count,
)


def test_signature_evaluator_matches_raw_policy_and_canonical_integer_formula() -> None:
    profile = ((0, 2, 1), (1, 1, 2))
    signatures = tuple(signature_from_policy(policy) for policy in profile)
    accuracy = Fraction(2, 5)
    reference = evaluate_signatures_reference(signatures, accuracy)
    scaled, failure_sum, denominator = evaluate_signatures_scaled(signatures, accuracy)
    assert reference == scaled == evaluate_formula(profile, 3, accuracy)
    assert scaled == Fraction(denominator - failure_sum, denominator)


def test_reference_and_reduced_feasibility_match_all_small_raw_signatures() -> None:
    for candidates in range(2, 5):
        raw = raw_policy_multiplicities(candidates)
        generated = set(all_feasible_signatures(candidates))
        assert generated == set(raw)
        assert len(generated) == feasible_signature_count(candidates)
        for signature in generated:
            reference = reference_feasibility(signature)
            reduced = reduced_feasibility(signature)
            assert reference.feasible and reduced.feasible
            assert reference.policy is not None
            assert signature_from_policy(reference.policy) == signature


def test_reference_and_reduced_decisions_match_all_small_local_candidates() -> None:
    for candidates in range(2, 5):
        raw = raw_policy_multiplicities(candidates)
        for counts in itertools.product(range(candidates + 1), repeat=candidates):
            if sum(counts) != candidates:
                continue
            for fixed in itertools.product((0, 1), repeat=candidates):
                signature = tuple(zip(counts, fixed, strict=True))
                reference = reference_feasibility(signature)
                reduced = reduced_feasibility(signature)
                assert reference.feasible == reduced.feasible
                assert reference.feasible == (signature in raw)


def test_reduced_feasibility_rejects_the_singleton_hall_obstruction() -> None:
    signature = ((3, 0), (0, 0), (0, 0))
    reference = reference_feasibility(signature)
    reduced = reduced_feasibility(signature)
    assert not reference.feasible
    assert not reduced.feasible
    assert "Hall bound" in reduced.reason


def test_signature_counts_and_target_orbits_match_small_enumeration() -> None:
    for candidates in range(2, 6):
        signatures = all_feasible_signatures(candidates)
        assert len(signatures) == feasible_signature_count(candidates)
        canonical = {canonicalize_signature(signature) for signature in signatures}
        assert len(canonical) == target_orbit_signature_count(candidates)


def test_signature_search_reproduces_hybrid_optimum_and_raw_ties() -> None:
    result = exhaustive_signature_optimum(3, 2, Fraction(2, 5))
    assert result.value == Fraction(7, 10)
    assert result.raw_policy_multiset_ties == 6


def test_all_binary_profiles_match_both_signature_evaluators() -> None:
    policies = tuple(itertools.product(range(2), repeat=2))
    for profile in itertools.product(policies, repeat=2):
        signatures = tuple(signature_from_policy(policy) for policy in profile)
        reference = evaluate_signatures_reference(signatures, Fraction(3, 4))
        scaled, _, _ = evaluate_signatures_scaled(signatures, Fraction(3, 4))
        assert reference == scaled == evaluate_formula(profile, 2, Fraction(3, 4))
