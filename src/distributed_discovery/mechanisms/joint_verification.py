"""Independent exact verifier for DD-006B frontier certificates."""

from fractions import Fraction
from itertools import product
from typing import cast

REGIMES = ("target-actions", "success-actions", "sole-rescue", "target-hidden-actions")


def _signal_probability(target: int, signal: int) -> Fraction:
    return Fraction(2, 3) if target == signal else Fraction(1, 6)


def _recommendation(reports: tuple[int, int], tie_role: int) -> tuple[int, int]:
    if reports[0] != reports[1]:
        return reports
    alternative = (reports[0] + 1) % 3
    return (reports[0], alternative) if tie_role == 0 else (alternative, reports[0])


def _score(report: int, target: int) -> Fraction:
    probabilities = [Fraction(1, 6)] * 3
    probabilities[report] = Fraction(2, 3)
    return 2 * probabilities[target] - sum((value * value for value in probabilities), Fraction())


def _transfer(
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
    information = _score(reports[agent], target) if regime.startswith("target") else Fraction()
    if regime in ("target-actions", "sole-rescue"):
        coverage = Fraction(actions[agent] == target and actions[peer] != target)
    elif regime == "success-actions":
        coverage = Fraction(actions[agent] == target)
    else:
        coverage = Fraction()
    obedience = (
        Fraction(actions[agent] == _recommendation(reports, tie_role)[agent])
        if regime != "target-hidden-actions"
        else Fraction()
    )
    return lam * information + mu * coverage + rho * obedience


def _prize(target: int, actions: tuple[int, int], agent: int) -> Fraction:
    winners = [action == target for action in actions]
    return Fraction(1, sum(winners)) if winners[agent] else Fraction()


def _expected_utility(
    regime: str,
    coefficients: tuple[Fraction, Fraction, Fraction],
    agent: int,
    signal: int,
    report: int,
    rule: tuple[int, int, int],
    tie_role: int,
) -> Fraction:
    total = Fraction()
    for target, peer_signal in product(range(3), repeat=2):
        probability = (
            _signal_probability(target, signal)
            * _signal_probability(target, peer_signal)
            / 3
        )
        reports = (report, peer_signal) if agent == 0 else (peer_signal, report)
        recommended = _recommendation(reports, tie_role)
        action = rule[peer_signal]
        actions = (action, recommended[1]) if agent == 0 else (recommended[0], action)
        total += probability * (
            _prize(target, actions, agent)
            + _transfer(regime, coefficients, target, reports, actions, agent, tie_role)
        )
    return total / Fraction(1, 3)


def _margin(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction], tie_role: int
) -> Fraction:
    gaps: list[Fraction] = []
    for agent, signal in product(range(2), range(3)):
        baseline_rule = cast(
            tuple[int, int, int],
            tuple(
                _recommendation((signal, peer) if agent == 0 else (peer, signal), tie_role)[agent]
                for peer in range(3)
            ),
        )
        baseline = _expected_utility(
            regime, coefficients, agent, signal, signal, baseline_rule, tie_role
        )
        for report, raw_rule in product(range(3), product(range(3), repeat=3)):
            rule = cast(tuple[int, int, int], raw_rule)
            if (report, rule) != (signal, baseline_rule):
                gaps.append(
                    baseline
                    - _expected_utility(
                        regime, coefficients, agent, signal, report, rule, tie_role
                    )
                )
    return min(gaps)


def _accounting(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction], tie_role: int
) -> dict[str, object]:
    total_transfer = Fraction()
    utilities = [Fraction(), Fraction()]
    for target, signal_0, signal_1 in product(range(3), repeat=3):
        probability = (
            Fraction(1, 3)
            * _signal_probability(target, signal_0)
            * _signal_probability(target, signal_1)
        )
        reports = (signal_0, signal_1)
        actions = _recommendation(reports, tie_role)
        for agent in range(2):
            payment = _transfer(
                regime, coefficients, target, reports, actions, agent, tie_role
            )
            total_transfer += probability * payment
            utilities[agent] += probability * (_prize(target, actions, agent) + payment)

    interim: list[Fraction] = []
    for agent, signal in product(range(2), range(3)):
        baseline_rule = cast(
            tuple[int, int, int],
            tuple(
                _recommendation((signal, peer) if agent == 0 else (peer, signal), tie_role)[agent]
                for peer in range(3)
            ),
        )
        interim.append(
            _expected_utility(
                regime, coefficients, agent, signal, signal, baseline_rule, tie_role
            )
        )

    transfer_bound = max(
        abs(_transfer(regime, coefficients, target, reports, actions, agent, tie_role))
        for target, report_0, report_1, action_0, action_1, agent in product(
            range(3), range(3), range(3), range(3), range(3), range(2)
        )
        for reports in [(report_0, report_1)]
        for actions in [(action_0, action_1)]
    )
    return {
        "expected_total_transfer": str(total_transfer),
        "expected_agent_utilities": [str(value) for value in utilities],
        "minimum_interim_utility": str(min(interim)),
        "participation": min(interim) >= 0,
        "worst_case_abs_transfer": str(transfer_bound),
    }


def verify_row(row: dict[str, object]) -> bool:
    raw = row.get("coefficients")
    if not isinstance(raw, list) or len(raw) != 3:
        return False
    values = cast(tuple[Fraction, Fraction, Fraction], tuple(Fraction(str(x)) for x in raw))
    if (
        any(x < 0 for x in values)
        or sum(values, Fraction()) != 1
        or row.get("regime") not in REGIMES
    ):
        return False
    regime = str(row["regime"])
    margins = [_margin(regime, values, role) for role in (0, 1)]
    expected = min(margins)
    accounting = row.get("accounting_by_tie_role")
    return (
        row.get("tie_role_margins") == [str(value) for value in margins]
        and Fraction(str(row.get("all_tie_margin"))) == expected
        and row.get("weak") is (expected >= 0)
        and row.get("strict") is (expected > 0)
        and accounting == [_accounting(regime, values, role) for role in (0, 1)]
    )
