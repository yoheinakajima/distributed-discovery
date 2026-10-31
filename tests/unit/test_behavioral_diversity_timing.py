"""Single-cell implementation checks, never the frozen 36-cell primary grid."""

from __future__ import annotations

import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from distributed_discovery.behavioral_diversity import timing

CONFIG = (
    Path(__file__).resolve().parents[2]
    / "studies/DD-024-behavioral-diversity-discovery/tracks/track-04/config.json"
)


def small_config(m: int, p: str, q: str) -> dict[str, Any]:
    config: dict[str, Any] = json.loads(CONFIG.read_text())
    config.update(target_counts=[m], p_values=[p], q_values=[q])
    return config


@pytest.fixture(scope="module")
def informative() -> tuple[dict[str, Any], dict[str, Any]]:
    config = small_config(3, "1/2", "3/4")
    return config, timing.run(config)


def test_no_information_has_known_coverage_and_individual_values() -> None:
    # A always covers labels 0,1. MAP B repeats them; coverage B selects 2,3.
    config = small_config(5, "chance", "chance")
    result = timing.run(config)
    for row in result["rows"]:
        expected = Fraction(2, 5) if row["receiver"] == "individual_map" else Fraction(4, 5)
        assert Fraction(row["value"]) == expected
    verified = timing.verify(config, result)
    assert verified["passed"], verified["errors"]
    assert all(verified["corruptions"].values())


def test_raw_verifier_and_event_emulation(
    informative: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    config, result = informative
    checked = timing.verify(config, result)
    assert checked["passed"], checked["errors"]
    assert checked["checks"]["raw_rows"] == 16
    assert checked["checks"]["emulations"] == 4
    assert checked["checks"]["local_deviations"] > 0
    for comparison in result["comparisons"]:
        assert comparison["emulation_difference"] == "0/1"
        if comparison["receiver"] == "coverage_aware":
            assert Fraction(comparison["transcript_matched_residual"]) <= 0
    json.dumps(result)  # A Fraction or other non-JSON value would fail here.


def test_event_silence_and_yoked_control_have_distinct_information(
    informative: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    _config, result = informative
    cell = result["rows"][0]["cell_id"]
    trigger = result["channels"][f"{cell}/agreement_trigger"]
    yoked = result["channels"][f"{cell}/yoked_agreement"]
    assert trigger["arrival_probability"] == yoked["arrival_probability"] == "7/16"
    trigger_silence = [k for k in trigger["first_information"] if k.split("|")[1] == "0"]
    yoked_silence = [k for k in yoked["first_information"] if k.split("|")[1] == "0"]
    assert trigger_silence and yoked_silence
    assert all(k.split("|")[2:] == ["-1", "0"] for k in trigger_silence)
    assert all(k.split("|")[2:] == ["-1", "-1"] for k in yoked_silence)


@pytest.mark.parametrize(
    "field", ["trigger_early_on", "arrival_probability", "payload_alphabet_max"]
)
def test_channel_corruptions_rejected_by_full_verifier(
    informative: tuple[dict[str, Any], dict[str, Any]],
    field: str,
) -> None:
    config, original = informative
    result = deepcopy(original)
    cell = result["rows"][0]["cell_id"]
    channel = result["channels"][f"{cell}/agreement_trigger"]
    channel[field] = "1/1" if field == "arrival_probability" else 999
    checked = timing.verify(config, result)
    assert not checked["passed"]
    assert "timing, silence, payload, or probability mismatch" in checked["errors"][0]


def test_silence_probability_corruption_rejected(
    informative: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    config, original = informative
    result = deepcopy(original)
    cell = result["rows"][0]["cell_id"]
    channel = result["channels"][f"{cell}/agreement_trigger"]
    history = next(k for k in channel["first_information"] if k.split("|")[1] == "0")
    channel["first_information"][history]["target_masses"][0] = "99/100"
    checked = timing.verify(config, result)
    assert not checked["passed"]
    assert "timing, silence, payload, or probability mismatch" in checked["errors"][0]


def test_saved_value_corruption_rejected(
    informative: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    config, original = informative
    result = deepcopy(original)
    result["rows"][0]["value"] = "101/100"
    checked = timing.verify(config, result)
    assert not checked["passed"]
    assert "saved value or row metadata" in checked["errors"][0]


def test_saved_policy_deviation_rejected(
    informative: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    config, original = informative
    result = deepcopy(original)
    row = next(row for row in result["rows"] if row["receiver"] == "individual_map")
    first = result["saved_policies"][row["policy_id"]]["first"]
    history = next(iter(first))
    first[history] = (first[history] + 1) % row["m"]
    checked = timing.verify(config, result)
    assert not checked["passed"]
    assert "local deviation or tie-break violation" in checked["errors"][0]


def test_verifier_does_not_call_primary_probability_or_optimizer(
    informative: tuple[dict[str, Any], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, result = informative

    def forbidden(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("Primary scientific implementation called by verifier")

    for name in (
        "_primary_sources",
        "_timed_atoms",
        "_first_observation",
        "_second_observation",
        "_primary_channel",
        "_optimize",
        "_primary_execute",
        "_emulate",
    ):
        monkeypatch.setattr(timing, name, forbidden)
    checked = timing.verify(config, result)
    assert checked["passed"], checked["errors"]


def test_built_in_corruptions_detect_a_disabled_channel_validator(
    informative: tuple[dict[str, Any], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config, result = informative

    def accept_any_channel(_observed: dict[str, Any], _expected: dict[str, Any]) -> bool:
        return True

    monkeypatch.setattr(timing, "_channel_matches", accept_any_channel)
    checked = timing.verify(config, result)
    assert not checked["passed"]
    assert checked["corruptions"] == {
        "trigger": False,
        "arrival": False,
        "silence_likelihood": False,
        "payload_alphabet": False,
        "value": True,
    }
    assert "required validation corruption was not rejected" in checked["errors"][0]
