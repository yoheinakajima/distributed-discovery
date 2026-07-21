import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from distributed_discovery.audits.model import audit_events, generate_sessions

ROOT = Path(__file__).resolve().parents[2]


def test_synthetic_copying_estimator_recovers_full_copying_without_error() -> None:
    _, events, _ = generate_sessions(
        candidates=4,
        sessions=500,
        copying_rate=1.0,
        protocol="private",
        provenance_missing_rate=0.0,
        matching_error_rate=0.0,
        seed=11,
    )
    audit = audit_events(events, 4)
    assert audit["copying_estimate"] == 1.0
    assert audit["ci_low"] <= 1.0 <= audit["ci_high"]


def test_event_schema_accepts_valid_fixture_and_rejects_invalid_fixture() -> None:
    schema = json.loads((ROOT / "schemas/discovery-events/v1/event.schema.json").read_text())
    validator = Draft202012Validator(schema)
    valid = json.loads((ROOT / "schemas/discovery-events/v1/fixtures/valid-event.json").read_text())
    invalid = json.loads(
        (ROOT / "schemas/discovery-events/v1/fixtures/invalid-event.json").read_text()
    )
    validator.validate(valid)
    with pytest.raises(ValidationError):
        validator.validate(invalid)
