"""Small independent structural checks for DD-006A frontier rows."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import cast

from distributed_discovery.mechanisms.general import FEATURES, REGIME_FEATURES, transfer


def verify_balance(
    regime: str, coefficients: tuple[Fraction, Fraction, Fraction, Fraction]
) -> bool:
    for target, first_report, second_report, first_action, second_action in product(
        range(3), repeat=5
    ):
        first = transfer(
            regime, coefficients, target, first_report, first_action, second_report, second_action
        )
        second = transfer(
            regime, coefficients, target, second_report, second_action, first_report, first_action
        )
        if first + second != 0:
            return False
    return True


def verify_row(row: dict[str, object]) -> bool:
    raw_values = row["coefficients"]
    if not isinstance(raw_values, list):
        return False
    values = tuple(Fraction(str(value)) for value in raw_values)
    if len(values) != len(FEATURES) or sum(abs(value) for value in values) > 1:
        return False
    regime = str(row["regime"])
    vector = cast(tuple[Fraction, Fraction, Fraction, Fraction], values)
    return regime in REGIME_FEATURES and verify_balance(regime, vector)
