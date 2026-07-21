"""Independent direct enumerator for N-agent source accounting."""

from fractions import Fraction
from itertools import product


def direct(n: int, k: int, p: Fraction, c: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    total = Fraction()
    i_pay = Fraction()
    c_pay = Fraction()
    m = n - k
    # one common signal when m>0, otherwise no common coordinate
    width = k + (m > 0)
    for target in range(3):
        for signals in product(range(3), repeat=width):
            probability = Fraction(1, 3)
            for signal in signals:
                probability *= p if signal == target else (1 - p) / 2
            actions = list(signals[:k]) + ([signals[-1]] * m if m else [])
            winners = [action == target for action in actions]
            count = sum(winners)
            total += probability * bool(count)
            for index, winner in enumerate(winners):
                if winner:
                    if index < k:
                        i_pay += probability / count
                    else:
                        c_pay += probability / count
    return total - k * c, (i_pay / k - c if k else Fraction()), (c_pay / m if m else Fraction())
