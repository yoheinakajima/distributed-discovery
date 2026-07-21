"""Independent structural verifier for DD-006B frontier certificates."""

from fractions import Fraction
from typing import cast

from distributed_discovery.mechanisms.joint import REGIMES, margin


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
    expected = min(margin(str(row["regime"]), values, role) for role in (0, 1))
    return Fraction(str(row.get("all_tie_margin"))) == expected
