"""Exact action-budget discovery profiles for finite channels."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import factorial
from typing import Any


def channels() -> list[dict[str, Any]]:
    m = 4
    point = tuple(range(m))
    short = tuple((i, j) for i in range(m) for j in range(i + 1, m))

    def point_law(q: Fraction) -> dict[int, dict[Any, Fraction]]:
        return {t: {s: q if s == t else (1 - q) / (m - 1) for s in point} for t in point}

    def shortlist_law(a: Fraction) -> dict[int, dict[Any, Fraction]]:
        return {t: {s: (a / 3 if t in s else (1 - a) / 3) for s in short} for t in point}

    exclusion = {t: {s: Fraction(0) if s == t else Fraction(1, 3) for s in point} for t in point}
    conf_signals = tuple((s, c) for s in point for c in ("low", "high"))
    conf = {
        t: {
            (s, c): Fraction(1, 2) * (q if s == t else (1 - q) / 3)
            for s, c in conf_signals
            for q in (Fraction(1, 2), Fraction(3, 4))
            if (c == "low" and q == Fraction(1, 2)) or (c == "high" and q == Fraction(3, 4))
        }
        for t in point
    }
    return [
        _record("noisy-point-half", "symmetric-noisy-point", point, point_law(Fraction(1, 2))),
        _record(
            "noisy-shortlist-three-quarters",
            "noisy-k-shortlist",
            short,
            shortlist_law(Fraction(3, 4)),
        ),
        _record(
            "guaranteed-shortlist-two", "guaranteed-shortlist", short, shortlist_law(Fraction(1))
        ),
        _record("explicit-exclusion", "exclusion", point, exclusion),
        _record("confidence-point", "confidence-augmented-point", conf_signals, conf),
    ]


def _record(
    channel_id: str, family: str, signals: tuple[Any, ...], law: dict[int, dict[Any, Fraction]]
) -> dict[str, Any]:
    return {
        "channel_id": channel_id,
        "family": family,
        "targets": tuple(range(4)),
        "prior": (Fraction(1, 4),) * 4,
        "signals": signals,
        "law": law,
    }


def posterior(channel: dict[str, Any], observations: tuple[Any, ...]) -> tuple[Fraction, ...]:
    weights = [channel["prior"][t] for t in channel["targets"]]
    for t in channel["targets"]:
        for s in observations:
            weights[t] *= channel["law"][t][s]
    total = sum(weights, Fraction())
    return tuple(w / total for w in weights)


def profile_labeled(channel: dict[str, Any], n: int = 3) -> tuple[Fraction, ...]:
    out = [Fraction() for _ in range(min(n, len(channel["targets"])))]
    for obs in product(channel["signals"], repeat=n):
        probability = sum(
            channel["prior"][t] * _prod(channel["law"][t][s] for s in obs)
            for t in channel["targets"]
        )
        if probability == 0:
            continue
        post = sorted(posterior(channel, obs), reverse=True)
        for i in range(len(out)):
            out[i] += probability * sum(post[: i + 1], Fraction())
    return tuple(out)


def profile_histogram(channel: dict[str, Any], n: int = 3) -> tuple[Fraction, ...]:
    out = [Fraction() for _ in range(min(n, len(channel["targets"])))]
    signals = channel["signals"]
    for counts in _compositions(n, len(signals)):
        obs = tuple(s for s, count in zip(signals, counts, strict=True) for _ in range(count))
        multiplicity = factorial(n)
        for count in counts:
            multiplicity //= factorial(count)
        probability = multiplicity * sum(
            channel["prior"][t] * _prod(channel["law"][t][s] for s in obs)
            for t in channel["targets"]
        )
        if probability == 0:
            continue
        post = sorted(posterior(channel, obs), reverse=True)
        for i in range(len(out)):
            out[i] += probability * sum(post[: i + 1], Fraction())
    return tuple(out)


def one_person_accuracy(channel: dict[str, Any]) -> Fraction:
    value = Fraction()
    for s in channel["signals"]:
        value += max(channel["prior"][t] * channel["law"][t][s] for t in channel["targets"])
    return value


def private_portfolio(channel: dict[str, Any], n: int = 3) -> Fraction:
    q = one_person_accuracy(channel)
    return 1 - (1 - q) ** n


def recovery_budget(profile: tuple[Fraction, ...], baseline: Fraction) -> int | None:
    return next((i + 1 for i, value in enumerate(profile) if value >= baseline), None)


def evaluate() -> list[dict[str, Any]]:
    rows = []
    for channel in channels():
        labeled = profile_labeled(channel)
        histogram = profile_histogram(channel)
        rows.append(
            {
                "channel_id": channel["channel_id"],
                "family": channel["family"],
                "signal_count": len(channel["signals"]),
                "one_person_accuracy": one_person_accuracy(channel),
                "private_portfolio_discovery": private_portfolio(channel),
                "profile": labeled,
                "independent_profile": histogram,
                "recovery_budget": recovery_budget(labeled, private_portfolio(channel)),
            }
        )
    return rows


def _prod(values: Any) -> Fraction:
    out = Fraction(1)
    for value in values:
        out *= value
    return out


def _compositions(total: int, parts: int) -> list[tuple[int, ...]]:
    if parts == 1:
        return [(total,)]
    return [
        (first, *rest)
        for first in range(total + 1)
        for rest in _compositions(total - first, parts - 1)
    ]
