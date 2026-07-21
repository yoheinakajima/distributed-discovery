"""Closed-form exact evaluator for DD-013 audience design."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from distributed_discovery.attention.model import (
    discovery,
    private_attention_value,
    reward_equilibrium,
    social_optima,
)


def action_quality(n: int, readers: int, p: Fraction, q: Fraction) -> Fraction:
    """Probability that a uniformly selected action is correct."""
    return (readers * q + (n - readers) * p) / n


def expected_distinct_actions(n: int, readers: int, p: Fraction, q: Fraction) -> Fraction:
    """Expected number of distinct action labels among three targets."""
    private_count = n - readers
    wrong = (1 - p) / 2
    if readers == 0:
        return 1 - (1 - p) ** n + 2 * (1 - (1 - wrong) ** n)
    if private_count == 0:
        return Fraction(1)
    shared_correct = 1 + 2 * (1 - (1 - wrong) ** private_count)
    shared_wrong = 1 + (1 - (1 - p) ** private_count) + (1 - (1 - wrong) ** private_count)
    return q * shared_correct + (1 - q) * shared_wrong


def binding_metrics(n: int, audience: int, p: Fraction, q: Fraction) -> dict[str, Any]:
    """Exact metrics when an audience is bound to follow the shared signal."""
    if not 0 <= audience <= n:
        raise ValueError("audience must lie in [0,n]")
    return {
        "discovery": discovery(n, audience, p, q),
        "action_quality": action_quality(n, audience, p, q),
        "expected_distinct_actions": expected_distinct_actions(n, audience, p, q),
        "information_access_count": audience,
        "effective_action_channels": n if audience == 0 else n - audience + 1,
    }


def binding_optima(n: int, p: Fraction, q: Fraction) -> list[int]:
    return social_optima(n, p, q)


def voluntary_equilibrium(
    n: int, audience: int, readers: int, p: Fraction, q: Fraction
) -> tuple[bool, bool]:
    """Weak/strict equilibrium among recipients choosing one ex-ante action mode."""
    if not 0 <= readers <= audience <= n:
        raise ValueError("require 0<=readers<=audience<=n")
    reader_ok = readers == 0 or private_attention_value(n, readers - 1, p, q) >= 0
    reader_strict = readers == 0 or private_attention_value(n, readers - 1, p, q) > 0
    recipient_private_ok = readers == audience or private_attention_value(n, readers, p, q) <= 0
    recipient_private_strict = readers == audience or private_attention_value(n, readers, p, q) < 0
    return (
        reader_ok and recipient_private_ok,
        reader_strict and recipient_private_strict,
    )


def voluntary_equilibria(n: int, audience: int, p: Fraction, q: Fraction) -> dict[str, list[int]]:
    weak: list[int] = []
    strict: list[int] = []
    for readers in range(audience + 1):
        is_weak, is_strict = voluntary_equilibrium(n, audience, readers, p, q)
        if is_weak:
            weak.append(readers)
        if is_strict:
            strict.append(readers)
    return {"weak": weak, "strict": strict}


def institution_registry() -> list[dict[str, Any]]:
    """Registered information firewalls with non-interchangeable assumptions."""
    return [
        {
            "institution_id": "exclusive-delivery",
            "who_sees_shared": "selected audience only",
            "who_may_act_on_shared": "selected audience only",
            "access_verifiable": True,
            "action_verifiable": False,
            "commitment": "binding delivery gate",
            "external_subsidy": False,
            "evaluated": True,
        },
        {
            "institution_id": "random-single-reader",
            "who_sees_shared": "one uniformly assigned identity",
            "who_may_act_on_shared": "assigned identity",
            "access_verifiable": True,
            "action_verifiable": False,
            "commitment": "binding randomized delivery",
            "external_subsidy": False,
            "evaluated": True,
        },
        {
            "institution_id": "rotating-reader",
            "who_sees_shared": "one identity per round on a public schedule",
            "who_may_act_on_shared": "scheduled identity",
            "access_verifiable": True,
            "action_verifiable": False,
            "commitment": "binding scheduled delivery",
            "external_subsidy": False,
            "evaluated": True,
        },
        {
            "institution_id": "exclusive-attention-token",
            "who_sees_shared": "current token holder",
            "who_may_act_on_shared": "current token holder",
            "access_verifiable": True,
            "action_verifiable": False,
            "commitment": "exclusive authenticated access",
            "external_subsidy": False,
            "evaluated": True,
        },
        {
            "institution_id": "private-recommendation",
            "who_sees_shared": "one privately addressed recipient",
            "who_may_act_on_shared": "addressed recipient",
            "access_verifiable": True,
            "action_verifiable": False,
            "commitment": "private delivery",
            "external_subsidy": False,
            "evaluated": True,
        },
        {
            "institution_id": "public-plus-binding-role",
            "who_sees_shared": "everyone",
            "who_may_act_on_shared": "one assigned role",
            "access_verifiable": False,
            "action_verifiable": True,
            "commitment": "binding action enforcement",
            "external_subsidy": False,
            "evaluated": True,
        },
        {
            "institution_id": "public-plus-nonbinding-recommendation",
            "who_sees_shared": "everyone",
            "who_may_act_on_shared": "everyone",
            "access_verifiable": False,
            "action_verifiable": False,
            "commitment": "none; equal-split voluntary modes",
            "external_subsidy": False,
            "evaluated": True,
        },
        {
            "institution_id": "public-plus-universal-pooling",
            "who_sees_shared": "everyone",
            "who_may_act_on_shared": "everyone",
            "access_verifiable": False,
            "action_verifiable": False,
            "commitment": "ex-ante registered follow-shared/follow-private modes",
            "external_subsidy": False,
            "evaluated": True,
        },
    ]


def mechanism_results(n: int, p: Fraction, q: Fraction) -> dict[str, Any]:
    """Exact count implementation for binding delivery and two public regimes."""
    optimum = binding_optima(n, p, q)
    pooled_weak: list[int] = []
    pooled_strict: list[int] = []
    for readers in range(n + 1):
        weak, strict = reward_equilibrium("universal-pooling", n, readers, p, q)
        if weak:
            pooled_weak.append(readers)
        if strict:
            pooled_strict.append(readers)
    nonbinding = voluntary_equilibria(n, n, p, q)
    identity_equilibria = sum(1 if count == 0 else n for count in pooled_weak)
    return {
        "binding_exclusive_delivery": {
            "implemented_counts": optimum,
            "weak": None,
            "strict": None,
            "budget_balance": "unit discovery prize unchanged",
            "expected_external_subsidy": "0",
        },
        "public_equal_split_nonbinding": nonbinding,
        "public_universal_pooling": {
            "weak": pooled_weak,
            "strict": pooled_strict,
            "ex_post_budget_balance": True,
            "expected_external_subsidy": "0",
            "identity_equilibrium_count": identity_equilibria,
            "count_correspondence_matches_optimum": pooled_weak == optimum,
        },
    }
