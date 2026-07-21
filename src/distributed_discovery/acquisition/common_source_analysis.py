"""General-N analytic thresholds for the common-versus-independent source game."""

from __future__ import annotations

from fractions import Fraction
from math import comb


def _validate(n: int, k: int, p: Fraction) -> None:
    if n < 2:
        raise ValueError("n must be at least two")
    if not 0 <= k < n:
        raise ValueError("k must index a source transition in 0,...,n-1")
    if not 0 < p < 1:
        raise ValueError("p must lie strictly between zero and one")


def _binomial_probability(trials: int, successes: int, p: Fraction) -> Fraction:
    return Fraction(comb(trials, successes)) * p**successes * (1 - p) ** (trials - successes)


def private_threshold(n: int, k: int, p: Fraction) -> Fraction:
    """Gross payoff gain when one common user becomes the (k+1)th I user.

    With m=n-k common users before the deviation and X~Binomial(k,p), the
    threshold is p(1-p) E[1/(1+X)-1/(m+X)].  A source cost below this value
    makes the unilateral acquisition profitable.
    """
    _validate(n, k, p)
    m = n - k
    expectation = sum(
        (
            _binomial_probability(k, x, p) * (Fraction(1, x + 1) - Fraction(1, x + m))
            for x in range(k + 1)
        ),
        Fraction(),
    )
    return p * (1 - p) * expectation


def planner_threshold(n: int, k: int, p: Fraction) -> Fraction:
    """Gross social gain from moving from k to k+1 independent users."""
    _validate(n, k, p)
    if k == n - 1:
        return Fraction()
    return p * (1 - p) ** (k + 1)


def equilibrium_counts(n: int, p: Fraction, cost: Fraction) -> list[int]:
    """Weak pure-equilibrium source counts implied by private thresholds."""
    if cost < 0:
        raise ValueError("cost must be nonnegative")
    thresholds = [private_threshold(n, k, p) for k in range(n)]
    return [
        k
        for k in range(n + 1)
        if (k == 0 or cost <= thresholds[k - 1]) and (k == n or cost >= thresholds[k])
    ]


def planner_counts(n: int, p: Fraction, cost: Fraction) -> list[int]:
    """Planner-optimal source counts implied by social marginal thresholds."""
    if cost < 0:
        raise ValueError("cost must be nonnegative")
    thresholds = [planner_threshold(n, k, p) for k in range(n)]
    return [
        k
        for k in range(n + 1)
        if (k == 0 or cost <= thresholds[k - 1]) and (k == n or cost >= thresholds[k])
    ]


def all_common_trap_interval(n: int, p: Fraction) -> tuple[Fraction, Fraction]:
    """Closed/open cost endpoints [private threshold, planner threshold)."""
    return private_threshold(n, 0, p), planner_threshold(n, 0, p)


def monotonicity_kernel(x: int, m: int, p: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    """Return direct difference, positive numerator, and denominator.

    For f_m(x)=1/(x+1)-1/(x+m) and Y~Bernoulli(p), this checks
    f_m(x)-E[f_{m-1}(x+Y)].
    """
    if x < 0 or m < 2 or not 0 < p < 1:
        raise ValueError("requires x>=0, m>=2, and 0<p<1")
    f_now = Fraction(1, x + 1) - Fraction(1, x + m)
    f_same = Fraction(1, x + 1) - Fraction(1, x + m - 1)
    f_plus = Fraction(1, x + 2) - Fraction(1, x + m)
    direct = f_now - ((1 - p) * f_same + p * f_plus)
    numerator = Fraction((x + 1) * (x + 2)) + p * (m - 2) * (2 * x + m + 1)
    denominator = Fraction((x + 1) * (x + 2) * (x + m - 1) * (x + m))
    return direct, numerator, denominator


def fixed_k_large_n_limit(k: int, p: Fraction) -> Fraction:
    """Limit of the private threshold as N grows with fixed k."""
    if k < 0 or not 0 < p < 1:
        raise ValueError("requires k>=0 and 0<p<1")
    q = 1 - p
    return q * (1 - q ** (k + 1)) / (k + 1)


def overacquisition_counterexample() -> dict[str, object]:
    """Exact N=3 counterexample to universal private under-acquisition."""
    n = 3
    p = Fraction(4, 5)
    cost = Fraction(13, 375)
    return {
        "agents": n,
        "accuracy": str(p),
        "cost": str(cost),
        "private_threshold_k1": str(private_threshold(n, 1, p)),
        "planner_threshold_k1": str(planner_threshold(n, 1, p)),
        "equilibrium_k": equilibrium_counts(n, p, cost),
        "planner_k": planner_counts(n, p, cost),
    }
