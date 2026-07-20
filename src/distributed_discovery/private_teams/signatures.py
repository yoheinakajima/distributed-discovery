"""Lossless policy signatures for the DD-001 zero-communication model."""

from __future__ import annotations

import itertools
import math
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from typing import TypeAlias

from distributed_discovery.private_teams.model import Policy

Signature: TypeAlias = tuple[tuple[int, int], ...]
SignatureProfile: TypeAlias = tuple[Signature, ...]


@dataclass(frozen=True)
class FeasibilityResult:
    feasible: bool
    policy: Policy | None
    reason: str


@dataclass(frozen=True)
class SignatureExhaustiveResult:
    value: Fraction
    profile: SignatureProfile
    signature_count: int
    reduced_profile_count: int
    signature_ties: int
    raw_policy_multiset_ties: int


def signature_from_policy(policy: Policy) -> Signature:
    candidates = len(policy)
    if candidates < 2:
        raise ValueError("policy must contain at least two signals")
    if any(action < 0 or action >= candidates for action in policy):
        raise ValueError("policy action outside candidate space")
    counts = [0] * candidates
    for action in policy:
        counts[action] += 1
    return tuple((counts[target], int(policy[target] == target)) for target in range(candidates))


def _local_error(signature: Signature) -> str | None:
    candidates = len(signature)
    if candidates < 2:
        return "signature must contain at least two targets"
    for target, pair in enumerate(signature):
        if len(pair) != 2:
            return f"target {target} must contain a count and fixed-point indicator"
        count, fixed = pair
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            return f"target {target} count must be a nonnegative integer"
        if isinstance(fixed, bool) or not isinstance(fixed, int) or fixed not in (0, 1):
            return f"target {target} fixed-point indicator must be 0 or 1"
        if fixed > count:
            return f"target {target} cannot be fixed with zero incoming count"
    if sum(count for count, _ in signature) != candidates:
        return "signature counts must sum to the number of targets"
    return None


def reference_feasibility(signature: Signature) -> FeasibilityResult:
    """Decide feasibility by explicit matching to duplicated residual column slots."""
    error = _local_error(signature)
    if error is not None:
        return FeasibilityResult(False, None, error)

    residual = [count - fixed for count, fixed in signature]
    rows = [target for target, (_, fixed) in enumerate(signature) if fixed == 0]
    slots = [target for target, capacity in enumerate(residual) for _ in range(capacity)]
    if len(rows) != len(slots):
        return FeasibilityResult(False, None, "residual row and capacity totals differ")

    slot_owner: list[int | None] = [None] * len(slots)

    def augment(row: int, seen: set[int]) -> bool:
        for slot, column in enumerate(slots):
            if column == row or slot in seen:
                continue
            seen.add(slot)
            owner = slot_owner[slot]
            if owner is None or augment(owner, seen):
                slot_owner[slot] = row
                return True
        return False

    for row in rows:
        if not augment(row, set()):
            return FeasibilityResult(
                False,
                None,
                f"residual bipartite assignment has no match for nonfixed row {row}",
            )

    policy = [target if fixed else -1 for target, (_, fixed) in enumerate(signature)]
    for slot, matched_row in enumerate(slot_owner):
        if matched_row is None:
            return FeasibilityResult(False, None, "residual matching left a slot unused")
        policy[matched_row] = slots[slot]
    reconstructed = tuple(policy)
    if signature_from_policy(reconstructed) != signature:
        raise RuntimeError("reference reconstruction changed the requested signature")
    return FeasibilityResult(True, reconstructed, "feasible by complete residual matching")


def reduced_feasibility(signature: Signature) -> FeasibilityResult:
    """Decide feasibility using the proved singleton Hall characterization."""
    error = _local_error(signature)
    if error is not None:
        return FeasibilityResult(False, None, error)
    nonfixed = sum(fixed == 0 for _, fixed in signature)
    for target, (count, fixed) in enumerate(signature):
        residual = count - fixed
        capacity = nonfixed - 1 if fixed == 0 else nonfixed
        if residual > capacity:
            return FeasibilityResult(
                False,
                None,
                f"target {target} residual capacity {residual} exceeds Hall bound {capacity}",
            )
    return FeasibilityResult(True, None, "feasible by singleton Hall conditions")


def signature_success_reference(signature: Signature, accuracy: Fraction) -> tuple[Fraction, ...]:
    feasibility = reference_feasibility(signature)
    if not feasibility.feasible:
        raise ValueError(feasibility.reason)
    candidates = len(signature)
    if not 0 <= accuracy <= 1:
        raise ValueError("accuracy must lie in [0,1]")
    error_probability = (1 - accuracy) / (candidates - 1)
    return tuple(
        error_probability * count + (accuracy - error_probability) * fixed
        for count, fixed in signature
    )


def evaluate_signatures_reference(profile: SignatureProfile, accuracy: Fraction) -> Fraction:
    if not profile:
        raise ValueError("signature profile must contain at least one searcher")
    candidates = len(profile[0])
    if any(len(signature) != candidates for signature in profile):
        raise ValueError("all signatures must use the same target space")
    successes = [signature_success_reference(signature, accuracy) for signature in profile]
    failure_sum = Fraction(0)
    for target in range(candidates):
        failure = Fraction(1)
        for agent in range(len(profile)):
            failure *= 1 - successes[agent][target]
        failure_sum += failure
    return 1 - failure_sum / candidates


def scaled_signature_scores(
    signature: Signature, accuracy: Fraction
) -> tuple[int, tuple[int, ...]]:
    feasibility = reduced_feasibility(signature)
    if not feasibility.feasible:
        raise ValueError(feasibility.reason)
    candidates = len(signature)
    numerator = accuracy.numerator
    denominator = accuracy.denominator
    scale = denominator * (candidates - 1)
    scores = tuple(
        (denominator - numerator) * count + (numerator * candidates - denominator) * fixed
        for count, fixed in signature
    )
    if any(score < 0 or score > scale for score in scores):
        raise RuntimeError("scaled success score lies outside probability bounds")
    return scale, scores


def evaluate_signatures_scaled(
    profile: SignatureProfile, accuracy: Fraction
) -> tuple[Fraction, int, int]:
    """Evaluate with one integer scale; return value, failure sum, and denominator."""
    if not profile:
        raise ValueError("signature profile must contain at least one searcher")
    candidates = len(profile[0])
    scaled = [scaled_signature_scores(signature, accuracy) for signature in profile]
    if any(len(signature) != candidates for signature in profile):
        raise ValueError("all signatures must use the same target space")
    scale = scaled[0][0]
    if any(candidate_scale != scale for candidate_scale, _ in scaled):
        raise RuntimeError("signature scales disagree")
    failure_sum = sum(
        math.prod(scale - scores[target] for _, scores in scaled) for target in range(candidates)
    )
    denominator = candidates * scale ** len(profile)
    numerator = denominator - failure_sum
    return Fraction(numerator, denominator), failure_sum, denominator


def _weak_compositions(total: int, parts: int) -> tuple[tuple[int, ...], ...]:
    if parts == 1:
        return ((total,),)
    return tuple(
        (first, *tail)
        for first in range(total + 1)
        for tail in _weak_compositions(total - first, parts - 1)
    )


def all_feasible_signatures(candidates: int) -> tuple[Signature, ...]:
    if candidates < 2:
        raise ValueError("candidates must be at least two")
    signatures: list[Signature] = []
    for fixed in itertools.product((0, 1), repeat=candidates):
        nonfixed = sum(value == 0 for value in fixed)
        for residual in _weak_compositions(nonfixed, candidates):
            if any(
                residual[target] > (nonfixed - 1 if fixed[target] == 0 else nonfixed)
                for target in range(candidates)
            ):
                continue
            signatures.append(
                tuple(
                    (residual[target] + fixed[target], fixed[target])
                    for target in range(candidates)
                )
            )
    return tuple(signatures)


def feasible_signature_count(candidates: int) -> int:
    if candidates < 2:
        raise ValueError("candidates must be at least two")
    return sum(
        math.comb(candidates, nonfixed)
        * (math.comb(nonfixed + candidates - 1, candidates - 1) - nonfixed)
        for nonfixed in range(candidates + 1)
    )


def canonicalize_signature(signature: Signature) -> Signature:
    if _local_error(signature) is not None:
        raise ValueError("cannot canonicalize a locally invalid signature")
    return tuple(sorted(signature))


def _multiset_sum_counts(parts: int, maximum: int, total: int) -> tuple[int, ...]:
    counts = [[0] * (total + 1) for _ in range(parts + 1)]
    counts[0][0] = 1
    for value in range(maximum + 1):
        updated = [row[:] for row in counts]
        for used in range(parts + 1):
            for subtotal in range(total + 1):
                ways = counts[used][subtotal]
                if ways == 0:
                    continue
                for copies in range(1, parts - used + 1):
                    next_total = subtotal + copies * value
                    if next_total > total:
                        break
                    updated[used + copies][next_total] += ways
        counts = updated
    return tuple(counts[parts])


def target_orbit_signature_count(candidates: int) -> int:
    """Count individual-signature orbits under global target relabeling."""
    if candidates < 2:
        raise ValueError("candidates must be at least two")
    total_orbits = 0
    for nonfixed in range(candidates + 1):
        fixed = candidates - nonfixed
        nonfixed_counts = _multiset_sum_counts(nonfixed, max(0, nonfixed - 1), nonfixed)
        fixed_counts = _multiset_sum_counts(fixed, nonfixed, nonfixed)
        total_orbits += sum(
            nonfixed_counts[subtotal] * fixed_counts[nonfixed - subtotal]
            for subtotal in range(nonfixed + 1)
        )
    return total_orbits


def raw_policy_multiplicities(candidates: int) -> Counter[Signature]:
    return Counter(
        signature_from_policy(policy)
        for policy in itertools.product(range(candidates), repeat=candidates)
    )


def signature_reduced_profile_count(candidates: int, searchers: int) -> int:
    signatures = feasible_signature_count(candidates)
    return math.comb(signatures + searchers - 1, searchers)


def exhaustive_signature_optimum(
    candidates: int, searchers: int, accuracy: Fraction
) -> SignatureExhaustiveResult:
    signatures = all_feasible_signatures(candidates)
    multiplicities = raw_policy_multiplicities(candidates)
    best_value = Fraction(-1)
    best_profile: SignatureProfile | None = None
    signature_ties = 0
    raw_ties = 0
    evaluated = 0
    for indices in itertools.combinations_with_replacement(range(len(signatures)), searchers):
        profile = tuple(signatures[index] for index in indices)
        value, _, _ = evaluate_signatures_scaled(profile, accuracy)
        reference = evaluate_signatures_reference(profile, accuracy)
        if value != reference:
            raise RuntimeError("reference and scaled signature evaluators disagree")
        index_counts = Counter(indices)
        represented_raw_multisets = math.prod(
            math.comb(multiplicities[signatures[index]] + count - 1, count)
            for index, count in index_counts.items()
        )
        evaluated += 1
        if value > best_value:
            best_value = value
            best_profile = profile
            signature_ties = 1
            raw_ties = represented_raw_multisets
        elif value == best_value:
            signature_ties += 1
            raw_ties += represented_raw_multisets
    expected = signature_reduced_profile_count(candidates, searchers)
    if evaluated != expected or best_profile is None:
        raise RuntimeError("signature profile count mismatch")
    return SignatureExhaustiveResult(
        best_value,
        best_profile,
        len(signatures),
        evaluated,
        signature_ties,
        raw_ties,
    )
