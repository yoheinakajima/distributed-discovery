"""Exact finite DD-006A normalized-linear transfer frontier."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import cast

from distributed_discovery.mechanisms.model import signal_probability

FEATURES = (
    "correct-report",
    "individual-success",
    "sole-rescue",
    "report-action-agreement",
)
REGIME_FEATURES = {
    "target-identity": FEATURES,
    "individual-success": ("individual-success", "report-action-agreement"),
    "sole-rescue": ("sole-rescue", "report-action-agreement"),
}


def recommendation(reports: tuple[int, int], tie_role: int) -> tuple[int, int]:
    """Posterior-leading distinct actions with declared fixed-role tie handling."""
    first, second = reports
    if first != second:
        return reports
    alternative = (first + 1) % 3
    return (first, alternative) if tie_role == 0 else (alternative, first)


def feature_vector(
    target: int, report: int, action: int, peer_report: int, peer_action: int
) -> dict[str, int]:
    return {
        "correct-report": int(report == target),
        "individual-success": int(action == target),
        "sole-rescue": int(action == target and peer_action != target),
        "report-action-agreement": int(report == action),
    }


def transfer(
    regime: str,
    coefficients: tuple[Fraction, Fraction, Fraction, Fraction],
    target: int,
    report: int,
    action: int,
    peer_report: int,
    peer_action: int,
) -> Fraction:
    own = feature_vector(target, report, action, peer_report, peer_action)
    peer = feature_vector(target, peer_report, peer_action, report, action)
    return sum(
        (
            coefficients[index] * (own[feature] - peer[feature])
            for index, feature in enumerate(FEATURES)
            if feature in REGIME_FEATURES[regime]
        ),
        Fraction(0),
    )


def coefficient_vectors() -> list[tuple[Fraction, Fraction, Fraction, Fraction]]:
    values = (Fraction(-1), Fraction(-1, 2), Fraction(0), Fraction(1, 2), Fraction(1))
    return [
        cast(tuple[Fraction, Fraction, Fraction, Fraction], vector)
        for vector in product(values, repeat=4)
        if sum(abs(value) for value in vector) <= 1
    ]


def expected_utility(
    regime: str,
    coefficients: tuple[Fraction, Fraction, Fraction, Fraction],
    agent: int,
    own_signal: int,
    own_report: int,
    own_action_rule: tuple[int, int, int],
    tie_role: int,
) -> Fraction:
    total = Fraction(0)
    for target, peer_signal in product(range(3), repeat=2):
        probability = (
            Fraction(1, 3)
            * signal_probability(target, own_signal)
            * signal_probability(target, peer_signal)
        )
        reports = (own_report, peer_signal) if agent == 0 else (peer_signal, own_report)
        recommended = recommendation(reports, tie_role)
        own_action = own_action_rule[peer_signal]
        peer_action = recommended[1 - agent]
        actions = (own_action, peer_action) if agent == 0 else (peer_action, own_action)
        total += probability * transfer(
            regime,
            coefficients,
            target,
            reports[agent],
            actions[agent],
            reports[1 - agent],
            actions[1 - agent],
        )
    return total / Fraction(1, 3)


def margin_for_tie(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction, Fraction], tie_role: int
) -> Fraction:
    margins: list[Fraction] = []
    for agent, signal, report in product(range(2), range(3), range(3)):
        baseline_rule = cast(
            tuple[int, int, int],
            tuple(
                recommendation((signal, peer) if agent == 0 else (peer, signal), tie_role)[agent]
                for peer in range(3)
            ),
        )
        baseline = expected_utility(
            regime, coefficients, agent, signal, signal, baseline_rule, tie_role
        )
        for action_rule in product(range(3), repeat=3):
            candidate_rule = cast(tuple[int, int, int], action_rule)
            if (report, candidate_rule) != (signal, baseline_rule):
                margins.append(
                    baseline
                    - expected_utility(
                        regime, coefficients, agent, signal, report, candidate_rule, tie_role
                    )
                )
    return min(margins)


def frontier_row(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction, Fraction]
) -> dict[str, object]:
    fixed = [margin_for_tie(regime, coefficients, role) for role in (0, 1)]
    public_margin = sum(fixed, Fraction(0)) / 2
    return {
        "regime": regime,
        "coefficients": [str(value) for value in coefficients],
        "fixed_role_margins": [str(value) for value in fixed],
        "public_lottery_margin": str(public_margin),
        "all_tie_rules_margin": str(min(fixed)),
        "weak_implements_all_ties": min(fixed) >= 0,
        "strictly_implements_all_ties": min(fixed) > 0,
    }
