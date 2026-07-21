"""Exact N-agent common-versus-independent source accounting."""

from fractions import Fraction
from math import comb


def discovery(n: int, k: int, p: Fraction) -> Fraction:
    """Union discovery: k I channels plus C iff at least one user selects C."""
    failure = Fraction((Fraction(1) - p) ** (k + int(k < n)))
    return Fraction(1) - failure


def _expect_inverse(trials: int, offset: int, p: Fraction) -> Fraction:
    return sum(
        (
            Fraction(comb(trials, x)) * p**x * (1 - p) ** (trials - x) / (offset + x)
            for x in range(trials + 1)
        ),
        Fraction(),
    )


def gross_payoffs(n: int, k: int, p: Fraction) -> tuple[Fraction | None, Fraction | None]:
    """Per-agent gross prize payoffs (I, C); None marks an absent type."""
    m = n - k
    independent = (
        None
        if k == 0
        else p
        * (
            (p * _expect_inverse(k - 1, m + 1, p) if m else _expect_inverse(k - 1, 1, p))
            + ((1 - p) * _expect_inverse(k - 1, 1, p) if m else 0)
        )
    )
    common = None if m == 0 else p * _expect_inverse(k, m, p)
    return independent, common


def payoffs(n: int, k: int, p: Fraction, c: Fraction) -> tuple[Fraction | None, Fraction | None]:
    independent, common = gross_payoffs(n, k, p)
    return (None if independent is None else independent - c), common


def equilibrium(n: int, k: int, p: Fraction, c: Fraction) -> tuple[bool, bool]:
    """Return (weak, strict) pure source-count equilibrium classifications."""
    independent, common = payoffs(n, k, p, c)
    c_to_i = m_ok = True
    if k < n:
        _, switching = payoffs(n, k + 1, p, c)
        # In k+1 profile the newly independent user's payoff is the first value.
        switching = payoffs(n, k + 1, p, c)[0]
        c_to_i = common >= switching  # type: ignore[operator]
        m_ok = common > switching  # type: ignore[operator]
    i_to_c = i_strict = True
    if k:
        switching_common = payoffs(n, k - 1, p, c)[1]
        i_to_c = independent >= switching_common  # type: ignore[operator]
        i_strict = independent > switching_common  # type: ignore[operator]
    return c_to_i and i_to_c, m_ok and i_strict


def planner(n: int, p: Fraction, c: Fraction) -> list[int]:
    values = {k: discovery(n, k, p) - k * c for k in range(n + 1)}
    best = max(values.values())
    return [k for k, value in values.items() if value == best]
