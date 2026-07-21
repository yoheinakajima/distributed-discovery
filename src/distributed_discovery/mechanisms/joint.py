"""Exact bounded DD-006B proper-score plus discovery mechanism."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import cast

from distributed_discovery.mechanisms.general import recommendation
from distributed_discovery.mechanisms.model import signal_probability

REGIMES = ("target-actions", "success-actions", "sole-rescue", "target-hidden-actions")


def coefficient_vectors() -> list[tuple[Fraction, Fraction, Fraction]]:
    values = [Fraction(i, 4) for i in range(5)]
    return [(a, b, c) for a, b, c in product(values, repeat=3) if a + b + c == 1]


def information_score(report: int, target: int) -> Fraction:
    q = [Fraction(1, 6)] * 3
    q[report] = Fraction(2, 3)
    return 2 * q[target] - sum((x * x for x in q), Fraction())


def realized_transfer(
    regime: str,
    coefficients: tuple[Fraction, Fraction, Fraction],
    target: int,
    reports: tuple[int, int],
    actions: tuple[int, int],
    agent: int,
    tie_role: int,
) -> Fraction:
    lam, mu, rho = coefficients
    peer = 1 - agent
    info = information_score(reports[agent], target) if regime.startswith("target") else Fraction()
    if regime == "sole-rescue":
        coverage = Fraction(actions[agent] == target and actions[peer] != target)
    elif regime == "success-actions":
        coverage = Fraction(actions[agent] == target)
    elif regime == "target-actions":
        coverage = Fraction(actions[agent] == target and actions[peer] != target)
    else:
        coverage = Fraction()
    obedience = (
        Fraction(actions[agent] == recommendation(reports, tie_role)[agent])
        if regime != "target-hidden-actions"
        else Fraction()
    )
    return lam * info + mu * coverage + rho * obedience


def realized_prize(target: int, actions: tuple[int, int], agent: int) -> Fraction:
    winners = [a == target for a in actions]
    count = sum(winners)
    return Fraction(1, count) if winners[agent] else Fraction()


def expected_utility(
    regime: str,
    coefficients: tuple[Fraction, Fraction, Fraction],
    agent: int,
    own_signal: int,
    own_report: int,
    action_rule: tuple[int, int, int],
    tie_role: int,
) -> Fraction:
    total = Fraction()
    for target, peer_signal in product(range(3), repeat=2):
        probability = (
            signal_probability(target, own_signal) * signal_probability(target, peer_signal) / 3
        )
        reports = (own_report, peer_signal) if agent == 0 else (peer_signal, own_report)
        rec = recommendation(reports, tie_role)
        own_action = action_rule[peer_signal]
        actions = (own_action, rec[1]) if agent == 0 else (rec[0], own_action)
        total += probability * (
            realized_prize(target, actions, agent)
            + realized_transfer(regime, coefficients, target, reports, actions, agent, tie_role)
        )
    return total / Fraction(1, 3)


def margin(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction], tie_role: int
) -> Fraction:
    gaps = []
    for agent, signal in product(range(2), range(3)):
        baseline = cast(
            tuple[int, int, int],
            tuple(
                recommendation((signal, p) if agent == 0 else (p, signal), tie_role)[agent]
                for p in range(3)
            ),
        )
        value = expected_utility(regime, coefficients, agent, signal, signal, baseline, tie_role)
        for report, rule in product(range(3), product(range(3), repeat=3)):
            candidate = cast(tuple[int, int, int], rule)
            if (report, candidate) != (signal, baseline):
                gaps.append(
                    value
                    - expected_utility(
                        regime, coefficients, agent, signal, report, candidate, tie_role
                    )
                )
    return min(gaps)


def frontier_row(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction]
) -> dict[str, object]:
    margins = [margin(regime, coefficients, role) for role in (0, 1)]
    return {
        "regime": regime,
        "coefficients": [str(x) for x in coefficients],
        "tie_role_margins": [str(x) for x in margins],
        "all_tie_margin": str(min(margins)),
        "weak": min(margins) >= 0,
        "strict": min(margins) > 0,
        "externally_subsidized": True,
    }
