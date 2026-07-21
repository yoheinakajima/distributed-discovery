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


def deviation_certificate(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction], tie_role: int
) -> dict[str, object]:
    joint_gaps: list[Fraction] = []
    report_gaps: list[Fraction] = []
    action_gaps: list[Fraction] = []
    best_response_counts: list[int] = []
    for agent, signal in product(range(2), range(3)):
        baseline = cast(
            tuple[int, int, int],
            tuple(
                recommendation((signal, p) if agent == 0 else (p, signal), tie_role)[agent]
                for p in range(3)
            ),
        )
        value = expected_utility(regime, coefficients, agent, signal, signal, baseline, tie_role)
        candidate_values = [value]
        for report, rule in product(range(3), product(range(3), repeat=3)):
            candidate = cast(tuple[int, int, int], rule)
            if (report, candidate) != (signal, baseline):
                candidate_value = expected_utility(
                    regime, coefficients, agent, signal, report, candidate, tie_role
                )
                candidate_values.append(candidate_value)
                gap = value - candidate_value
                joint_gaps.append(gap)
                if report == signal:
                    action_gaps.append(gap)
                obeying_rule = cast(
                    tuple[int, int, int],
                    tuple(
                        recommendation((report, peer) if agent == 0 else (peer, report), tie_role)[
                            agent
                        ]
                        for peer in range(3)
                    ),
                )
                if report != signal and candidate == obeying_rule:
                    report_gaps.append(gap)
        best = max(candidate_values)
        best_response_counts.append(sum(candidate == best for candidate in candidate_values))
    return {
        "report_only_margin": str(min(report_gaps)),
        "action_only_margin": str(min(action_gaps)),
        "joint_margin": str(min(joint_gaps)),
        "best_response_counts": best_response_counts,
        "truthful_profile_is_bne": min(joint_gaps) >= 0,
        "truthful_profile_is_strict_bne": min(joint_gaps) > 0,
    }


def margin(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction], tie_role: int
) -> Fraction:
    return Fraction(str(deviation_certificate(regime, coefficients, tie_role)["joint_margin"]))


def truthful_discovery(tie_role: int) -> Fraction:
    probability = Fraction()
    for target, signal_0, signal_1 in product(range(3), repeat=3):
        state_probability = (
            Fraction(1, 3)
            * signal_probability(target, signal_0)
            * signal_probability(target, signal_1)
        )
        actions = recommendation((signal_0, signal_1), tie_role)
        probability += state_probability * Fraction(target in actions)
    return probability


def truthful_accounting(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction], tie_role: int
) -> dict[str, object]:
    """Return exact ex-ante budget, utility, and transfer-bound certificates."""
    total_transfer = Fraction()
    utilities = [Fraction(), Fraction()]
    state_total_transfers: list[Fraction] = []
    for target, signal_0, signal_1 in product(range(3), repeat=3):
        probability = (
            Fraction(1, 3)
            * signal_probability(target, signal_0)
            * signal_probability(target, signal_1)
        )
        reports = (signal_0, signal_1)
        actions = recommendation(reports, tie_role)
        state_total_transfer = Fraction()
        for agent in range(2):
            payment = realized_transfer(
                regime, coefficients, target, reports, actions, agent, tie_role
            )
            total_transfer += probability * payment
            state_total_transfer += payment
            utilities[agent] += probability * (realized_prize(target, actions, agent) + payment)
        state_total_transfers.append(state_total_transfer)

    interim = []
    for agent, signal in product(range(2), range(3)):
        baseline = cast(
            tuple[int, int, int],
            tuple(
                recommendation((signal, peer) if agent == 0 else (peer, signal), tie_role)[agent]
                for peer in range(3)
            ),
        )
        interim.append(
            expected_utility(regime, coefficients, agent, signal, signal, baseline, tie_role)
        )

    transfer_bound = max(
        abs(realized_transfer(regime, coefficients, target, reports, actions, agent, tie_role))
        for target, report_0, report_1, action_0, action_1, agent in product(
            range(3), range(3), range(3), range(3), range(3), range(2)
        )
        for reports in [(report_0, report_1)]
        for actions in [(action_0, action_1)]
    )
    return {
        "expected_total_transfer": str(total_transfer),
        "expected_agent_utilities": [str(value) for value in utilities],
        "ex_post_total_transfer_bounds": [
            str(min(state_total_transfers)),
            str(max(state_total_transfers)),
        ],
        "minimum_interim_utility": str(min(interim)),
        "participation": min(interim) >= 0,
        "worst_case_abs_transfer": str(transfer_bound),
    }


def frontier_row(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction]
) -> dict[str, object]:
    certificates = [deviation_certificate(regime, coefficients, role) for role in (0, 1)]
    margins = [Fraction(str(certificate["joint_margin"])) for certificate in certificates]
    accounting = [truthful_accounting(regime, coefficients, role) for role in (0, 1)]
    return {
        "regime": regime,
        "coefficients": [str(x) for x in coefficients],
        "active_components": {
            "information_score": regime.startswith("target"),
            "coverage": regime != "target-hidden-actions",
            "obedience": regime != "target-hidden-actions",
        },
        "tie_role_margins": [str(x) for x in margins],
        "deviation_certificates_by_tie_role": certificates,
        "all_tie_margin": str(min(margins)),
        "weak": min(margins) >= 0,
        "strict": min(margins) > 0,
        "externally_subsidized": True,
        "accounting_by_tie_role": accounting,
        "truthful_discovery_by_tie_role": [str(truthful_discovery(role)) for role in (0, 1)],
        "tie_rule": "fixed ex ante and checked for both role assignments",
    }
