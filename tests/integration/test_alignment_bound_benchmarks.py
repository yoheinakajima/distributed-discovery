import csv
import json
from fractions import Fraction
from pathlib import Path

from distributed_discovery.private_teams.alignment_bound import alignment_count_bound

ROOT = Path(__file__).resolve().parents[2]
TINY = (
    ROOT
    / "results/verified/20260720T200447Z_DD-001_6eb12861_ba766d1eba"
    / "outputs/tiny-phase-grid.csv"
)
ANTI = (
    ROOT
    / "results/verified/20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1"
    / "outputs/anti-informative-counterexamples.json"
)


def test_alignment_bound_is_exact_on_all_prior_tiny_grid_cases() -> None:
    with TINY.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 21
    assert any(row["direct_is_optimal"] == "True" for row in rows)
    assert any(row["direct_is_optimal"] == "False" for row in rows)
    for row in rows:
        bound = alignment_count_bound(
            int(row["candidates"]), int(row["searchers"]), Fraction(row["accuracy"])
        )
        assert bound.discovery_upper_bound == Fraction(row["optimum_fraction"])


def test_alignment_bound_remains_upper_valid_anti_informatively() -> None:
    records = json.loads(ANTI.read_text(encoding="utf-8"))
    assert len(records) == 2
    gaps = []
    for record in records:
        optimum = Fraction(record["unrestricted_optimum"])
        bound = alignment_count_bound(int(record["candidates"]), 2, Fraction(0))
        assert bound.discovery_upper_bound >= optimum
        gaps.append(bound.discovery_upper_bound - optimum)
    assert gaps == [Fraction(1, 12), Fraction(0)]
