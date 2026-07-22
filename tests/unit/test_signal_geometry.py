import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

from distributed_discovery.signal_geometry.model import channels, evaluate
from distributed_discovery.signal_geometry.verification import build

ROOT = Path(__file__).resolve().parents[2]


def test_channel_schema_is_valid() -> None:
    schema = json.loads(
        (ROOT / "studies/DD-019-signal-geometry/schemas/channel-v1.schema.json").read_text()
    )
    Draft202012Validator.check_schema(schema)


def test_channel_laws_normalize() -> None:
    for channel in channels():
        for target in channel["targets"]:
            assert sum(channel["law"][target].values(), Fraction()) == 1


def test_exact_methods_and_bounds() -> None:
    rows, verification, corruptions = build()
    assert len(rows) == 5
    assert verification["passed"]
    assert all(corruptions.values())


def test_same_accuracy_witness_is_not_assumed_equal_profile() -> None:
    rows = evaluate()
    point = next(r for r in rows if r["channel_id"] == "noisy-point-half")
    shortlist = next(r for r in rows if r["channel_id"] == "guaranteed-shortlist-two")
    assert point["one_person_accuracy"] == shortlist["one_person_accuracy"] == Fraction(1, 2)
    assert point["private_portfolio_discovery"] == shortlist["private_portfolio_discovery"]
    assert point["profile"] != shortlist["profile"]
