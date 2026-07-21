"""Closed-form exact evaluator for DD-012 selective attention."""

from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import Any

STRATEGIC_REWARD_RULES = (
    "equal-split",
    "sole-rescue",
    "off-shared-success",
    "marginal-coverage",
    "assigned-reader-reward",
    "universal-pooling",
)


def _inverse_expectation(trials: int, offset: int, p: Fraction) -> Fraction:
    return sum(
        (
            Fraction(comb(trials, successes))
            * p**successes
            * (1 - p) ** (trials - successes)
            / (offset + successes)
            for successes in range(trials + 1)
        ),
        Fraction(),
    )


def discovery(n: int, k: int, p: Fraction, q: Fraction) -> Fraction:
    """Union discovery with k shared-signal attenders."""
    if not 0 <= k <= n:
        raise ValueError("attention count must lie in [0,n]")
    if k == 0:
        return 1 - (1 - p) ** n
    return 1 - (1 - q) * (1 - p) ** (n - k)


def equal_split_payoffs(
    n: int, k: int, p: Fraction, q: Fraction
) -> tuple[Fraction | None, Fraction | None]:
    """Per-agent gross payoff for an attender and an ignorer."""
    attending = None if k == 0 else q * _inverse_expectation(n - k, k, p)
    ignoring = (
        None
        if k == n
        else p
        * (
            q * _inverse_expectation(n - k - 1, k + 1, p)
            + (1 - q) * _inverse_expectation(n - k - 1, 1, p)
        )
    )
    return attending, ignoring


def private_attention_value(n: int, k: int, p: Fraction, q: Fraction) -> Fraction:
    """Payoff gain when one ignorer becomes attendee from a k-attender profile."""
    if not 0 <= k < n:
        raise ValueError("a switch to attend requires k<n")
    other_ignorers = n - k - 1
    return q * (1 - p) * _inverse_expectation(other_ignorers, k + 1, p) - p * (
        1 - q
    ) * _inverse_expectation(other_ignorers, 1, p)


def social_attention_value(n: int, k: int, p: Fraction, q: Fraction) -> Fraction:
    """Discovery change when one additional role attends."""
    if not 0 <= k < n:
        raise ValueError("a social attention margin requires k<n")
    return discovery(n, k + 1, p, q) - discovery(n, k, p, q)


def equilibrium(n: int, k: int, p: Fraction, q: Fraction) -> tuple[bool, bool]:
    """Return weak and strict pure attention-count equilibrium flags."""
    attend_ok = k == 0 or private_attention_value(n, k - 1, p, q) >= 0
    ignore_ok = k == n or private_attention_value(n, k, p, q) <= 0
    attend_strict = k == 0 or private_attention_value(n, k - 1, p, q) > 0
    ignore_strict = k == n or private_attention_value(n, k, p, q) < 0
    return attend_ok and ignore_ok, attend_strict and ignore_strict


def social_optima(n: int, p: Fraction, q: Fraction) -> list[int]:
    values = {k: discovery(n, k, p, q) for k in range(n + 1)}
    best = max(values.values())
    return [k for k, value in values.items() if value == best]


def reward_registry() -> list[dict[str, Any]]:
    return [
        {
            "rule_id": "equal-split",
            "strategic_attention": True,
            "payment": "unit success prize divided among all successful agents",
            "observability": ["individual action", "target or individual success"],
            "external_subsidy": False,
        },
        {
            "rule_id": "sole-rescue",
            "strategic_attention": True,
            "payment": "one unit only to the unique successful agent",
            "observability": ["all actions", "target or individual success"],
            "external_subsidy": False,
        },
        {
            "rule_id": "off-shared-success",
            "strategic_attention": True,
            "payment": (
                "one unit to each successful action different from the shared recommendation"
            ),
            "observability": ["shared signal", "all actions", "target"],
            "external_subsidy": True,
        },
        {
            "rule_id": "marginal-coverage",
            "strategic_attention": True,
            "payment": "one unit to a successful agent only when its action label is unique",
            "observability": ["all actions", "target"],
            "external_subsidy": False,
        },
        {
            "rule_id": "assigned-reader-reward",
            "strategic_attention": True,
            "payment": (
                "equal-split prize plus 1/N to every registered reader who follows "
                "the delivered signal"
            ),
            "observability": ["access roster", "shared signal", "all actions"],
            "external_subsidy": True,
        },
        {
            "rule_id": "public-reader-license",
            "strategic_attention": False,
            "payment": "equal-split prize under a binding ex-ante cap on shared-signal recipients",
            "observability": ["binding signal delivery"],
            "external_subsidy": False,
        },
        {
            "rule_id": "universal-pooling",
            "strategic_attention": True,
            "payment": "every agent receives 1/N when the team discovers the target",
            "observability": ["team discovery"],
            "external_subsidy": False,
        },
    ]


def reward_payoffs(
    rule: str, n: int, k: int, p: Fraction, q: Fraction
) -> tuple[Fraction | None, Fraction | None, Fraction]:
    """Return (attender payoff, ignorer payoff, expected total payment)."""
    if rule == "equal-split":
        attending, ignoring = equal_split_payoffs(n, k, p, q)
    elif rule in {"sole-rescue", "marginal-coverage"}:
        attending = None if k == 0 else (q * (1 - p) ** (n - 1) if k == 1 else Fraction())
        if k == n:
            ignoring = None
        elif k == 0:
            ignoring = p * (1 - p) ** (n - 1)
        else:
            ignoring = p * (1 - q) * (1 - p) ** (n - k - 1)
    elif rule == "off-shared-success":
        attending = None if k == 0 else Fraction()
        ignoring = None if k == n else p * (1 - q)
    elif rule == "assigned-reader-reward":
        attending, ignoring = equal_split_payoffs(n, k, p, q)
        if attending is not None:
            attending += Fraction(1, n)
    elif rule == "universal-pooling":
        pooled = discovery(n, k, p, q) / n
        attending = None if k == 0 else pooled
        ignoring = None if k == n else pooled
    else:
        raise ValueError(f"non-strategic or unknown reward rule: {rule}")
    budget = k * (attending or Fraction()) + (n - k) * (ignoring or Fraction())
    return attending, ignoring, budget


def reward_equilibrium(rule: str, n: int, k: int, p: Fraction, q: Fraction) -> tuple[bool, bool]:
    """Pure role-choice equilibrium under one strategic reward rule."""
    attending, ignoring, _ = reward_payoffs(rule, n, k, p, q)
    attend_ok = attend_strict = True
    if k:
        switched_ignore = reward_payoffs(rule, n, k - 1, p, q)[1]
        assert attending is not None and switched_ignore is not None
        attend_ok = attending >= switched_ignore
        attend_strict = attending > switched_ignore
    ignore_ok = ignore_strict = True
    if k < n:
        switched_attend = reward_payoffs(rule, n, k + 1, p, q)[0]
        assert ignoring is not None and switched_attend is not None
        ignore_ok = ignoring >= switched_attend
        ignore_strict = ignoring > switched_attend
    return attend_ok and ignore_ok, attend_strict and ignore_strict


def attention_category(optima: list[int], equilibria: list[int]) -> str:
    if set(equilibria) <= set(optima):
        if optima == [0]:
            return "efficient-ignorance"
        return "efficient-attention"
    if min(equilibria) > max(optima):
        return "excessive-attention"
    if max(equilibria) < min(optima):
        return "excessive-ignorance"
    return "equilibrium-multiplicity-with-welfare-difference"
