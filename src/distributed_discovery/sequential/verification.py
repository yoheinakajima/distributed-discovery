"""Independent bounded sequence enumerator for DD-004 certificates."""

from __future__ import annotations

from fractions import Fraction
from itertools import permutations


def enumerate_sequences(
    prior: tuple[Fraction, ...], budget: int, schedule: tuple[int, ...]
) -> dict[str, Fraction]:
    """Exhaust every no-repeat policy path; perfect failures leave one history path."""
    candidates = tuple(range(len(prior)))
    best: dict[str, Fraction] | None = None
    for actions in permutations(candidates, budget):
        terminal = sum((prior[action] for action in actions), Fraction(0))
        expected_actions = Fraction(0)
        expected_rounds = Fraction(0)
        failure = Fraction(1)
        cursor = 0
        for size in schedule:
            expected_actions += size * failure
            expected_rounds += failure
            failure -= sum(
                (prior[action] for action in actions[cursor : cursor + size]), Fraction(0)
            )
            cursor += size
        candidate = {
            "terminal_discovery": terminal,
            "expected_actions": expected_actions,
            "expected_rounds": expected_rounds,
        }
        if (
            best is None
            or candidate["terminal_discovery"] > best["terminal_discovery"]
            or (
                candidate["terminal_discovery"] == best["terminal_discovery"]
                and candidate["expected_actions"] < best["expected_actions"]
            )
        ):
            best = candidate
    if best is None:
        raise RuntimeError("no enumerated policy")
    return best
