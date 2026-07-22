"""Presentation-only formatting for exact public-site values."""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class PresentedNumber:
    """A readable display paired with the lossless source representation."""

    display: str
    exact: str
    accessible: str


def _special(value: object) -> PresentedNumber | None:
    if value is None or str(value).strip().lower() in {"", "na", "n/a", "not applicable"}:
        return PresentedNumber("Not applicable", "not applicable", "Not applicable")
    text = str(value).strip()
    if text.lower() in {"undefined", "nan"}:
        return PresentedNumber("Undefined", text, "Undefined")
    if text.lower() in {"infinity", "+infinity", "inf", "+inf"}:
        return PresentedNumber("∞", text, "Infinite")
    if text.lower() in {"-infinity", "-inf"}:
        return PresentedNumber("−∞", text, "Negative infinite")
    if isinstance(value, float) and not math.isfinite(value):
        return _special(str(value))
    return None


def _fraction(value: object) -> tuple[Fraction, str]:
    exact = str(value)
    return Fraction(exact), exact


def probability(value: object, digits: int = 1) -> PresentedNumber:
    """Format a probability as a percentage while preserving its exact value."""

    special = _special(value)
    if special:
        return special
    parsed, exact = _fraction(value)
    display = f"{float(parsed) * 100:.{digits}f}%"
    return PresentedNumber(display, exact, f"{display}; exact value {exact}")


def expected_count(value: object, digits: int = 3) -> PresentedNumber:
    """Format an expected count with bounded decimals and an exact companion."""

    special = _special(value)
    if special:
        return special
    parsed, exact = _fraction(value)
    display = f"{float(parsed):.{digits}f}".rstrip("0").rstrip(".")
    return PresentedNumber(display, exact, f"{display}; exact value {exact}")


def currency(value: object, digits: int = 2, symbol: str = "$") -> PresentedNumber:
    """Format a monetary presentation value without changing the exact source."""

    special = _special(value)
    if special:
        return special
    parsed, exact = _fraction(value)
    display = f"{symbol}{float(parsed):,.{digits}f}"
    return PresentedNumber(display, exact, f"{display}; exact value {exact}")
