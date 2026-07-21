"""Closed-form values for common versus independent evidence."""

from __future__ import annotations

from fractions import Fraction

PROFILES = ("CC", "CI", "IC", "II")


def values(
    profile: str, accuracy: Fraction, cost: Fraction
) -> tuple[Fraction, tuple[Fraction, Fraction]]:
    if profile == "CC":
        return accuracy, (accuracy / 2, accuracy / 2)
    discovery = 2 * accuracy - accuracy * accuracy
    pay = accuracy - accuracy * accuracy / 2
    costs = (cost if profile[0] == "I" else 0, cost if profile[1] == "I" else 0)
    return discovery - sum(costs), (pay - costs[0], pay - costs[1])


def equilibria(accuracy: Fraction, cost: Fraction) -> list[str]:
    out = []
    for profile in PROFILES:
        _, payoff = values(profile, accuracy, cost)
        ok = True
        for agent in range(2):
            switched = list(profile)
            switched[agent] = "I" if switched[agent] == "C" else "C"
            alt = "".join(switched)
            if values(alt, accuracy, cost)[1][agent] > payoff[agent]:
                ok = False
        if ok:
            out.append(profile)
    return out


def planner(accuracy: Fraction, cost: Fraction) -> list[str]:
    scores = {profile: values(profile, accuracy, cost)[0] for profile in PROFILES}
    best = max(scores.values())
    return [profile for profile in PROFILES if scores[profile] == best]
