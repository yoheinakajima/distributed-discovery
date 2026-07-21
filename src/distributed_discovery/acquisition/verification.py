"""Direct target/signal enumerator for DD-008 closed forms."""

from __future__ import annotations

from fractions import Fraction
from itertools import product

from distributed_discovery.acquisition.model import values


def direct_values(
    profile: str, accuracy: Fraction, cost: Fraction
) -> tuple[Fraction, tuple[Fraction, Fraction]]:
    discovery = Fraction(0)
    payoffs = [Fraction(0), Fraction(0)]
    for target in range(3):
        for first_signal, second_signal in product(range(3), repeat=2):
            if profile == "CC" and first_signal != second_signal:
                continue
            probability = Fraction(1, 3) * (
                accuracy if first_signal == target else (1 - accuracy) / 2
            )
            if profile != "CC":
                probability *= accuracy if second_signal == target else (1 - accuracy) / 2
            actions = (first_signal, second_signal)
            winners = [action == target for action in actions]
            count = sum(winners)
            discovery += probability * int(count > 0)
            for agent in range(2):
                payoffs[agent] += probability * (Fraction(1, count) if winners[agent] else 0)
    costs = (cost if profile[0] == "I" else 0, cost if profile[1] == "I" else 0)
    return discovery - sum(costs), (payoffs[0] - costs[0], payoffs[1] - costs[1])


def agrees(profile: str, accuracy: Fraction, cost: Fraction) -> bool:
    return values(profile, accuracy, cost) == direct_values(profile, accuracy, cost)
