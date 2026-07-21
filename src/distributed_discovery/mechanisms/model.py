"""Exact Bayesian deviation checker for the registered DD-006 class."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import cast

REGIMES = ("target-identity", "individual-success", "sole-rescue")


def signal_probability(target: int, signal: int) -> Fraction:
    return Fraction(2, 3) if target == signal else Fraction(1, 6)


def score(regime: str, target: int, report: int, action: int, peer_action: int) -> int:
    if regime == "target-identity":
        return int(report == target)
    if regime == "individual-success":
        return int(action == target)
    if regime == "sole-rescue":
        return int(action == target and peer_action != target)
    raise ValueError("unknown observability regime")


def utility(
    regime: str,
    coefficient: int,
    target: int,
    report: int,
    action: int,
    peer_report: int,
    peer_action: int,
) -> Fraction:
    own = score(regime, target, report, action, peer_action)
    peer = score(regime, target, peer_report, peer_action, action)
    return Fraction(coefficient * (own - peer))


def expected_utility(
    regime: str,
    coefficient: int,
    own_signal: int,
    report: int,
    action: int,
    peer_policy: tuple[int, int, int],
) -> Fraction:
    total = Fraction(0)
    for target, peer_signal in product(range(3), repeat=2):
        probability = (
            Fraction(1, 3)
            * signal_probability(target, own_signal)
            * signal_probability(target, peer_signal)
        )
        peer_report = peer_signal
        peer_action = peer_policy[peer_signal]
        total += probability * utility(
            regime, coefficient, target, report, action, peer_report, peer_action
        )
    return total / (Fraction(1, 3))


def direct_discovery() -> Fraction:
    return Fraction(1) - Fraction(1, 3) ** 2


def check_truthful_direct(regime: str, coefficient: int) -> dict[str, object]:
    policy = (0, 1, 2)
    deviations: list[dict[str, object]] = []
    passed = True
    strict = True
    for signal in range(3):
        baseline = expected_utility(regime, coefficient, signal, signal, signal, policy)
        for report, action in product(range(3), repeat=2):
            candidate = expected_utility(regime, coefficient, signal, report, action, policy)
            if candidate > baseline:
                passed = False
            if (report, action) != (signal, signal) and candidate >= baseline:
                strict = False
            deviations.append(
                {
                    "signal": signal,
                    "report": report,
                    "action": action,
                    "gain": str(candidate - baseline),
                }
            )
    return {
        "pure_bne": passed,
        "strict": strict,
        "deviations": deviations,
        "discovery": str(direct_discovery()),
    }


def enumerate_symmetric_action_profiles(regime: str, coefficient: int) -> int:
    """Count symmetric action maps satisfying best responses after truthful reports."""
    equilibria = 0
    for raw_policy in product(range(3), repeat=3):
        policy = cast(tuple[int, int, int], raw_policy)
        valid = True
        for signal in range(3):
            baseline = expected_utility(regime, coefficient, signal, signal, policy[signal], policy)
            if any(
                expected_utility(regime, coefficient, signal, signal, action, policy) > baseline
                for action in range(3)
            ):
                valid = False
        equilibria += int(valid)
    return equilibria
