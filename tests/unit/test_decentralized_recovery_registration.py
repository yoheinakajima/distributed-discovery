from __future__ import annotations

from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "plans" / "decentralized-recovery-registration"
GLOBAL_DECISION = (
    ROOT / "reports" / "roadmap-consolidation" / "decentralized-recovery-registration-decision.yml"
)


def _load_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text())


def _load_schema(path: Path) -> dict[str, object]:
    value = _load_yaml(path)
    assert isinstance(value, dict)
    return value


def test_registration_decision_is_exact_and_unallocated() -> None:
    decision = _load_yaml(PACKAGE / "registration-decision.yml")
    Draft202012Validator(_load_schema(PACKAGE / "registration-decision.schema.json")).validate(
        decision
    )
    assert decision == _load_yaml(GLOBAL_DECISION)
    assert isinstance(decision, dict)
    assert decision["decision"] == "stop-classical-overlap"
    assert decision["study_id_allocated"] is False
    assert decision["study_id"] is None
    assert decision["next_program_if_stopped"] == "Reliable Discovery"


def test_corruption_registry_is_semantic_and_complete() -> None:
    registry = _load_yaml(PACKAGE / "corruptions.yml")
    Draft202012Validator(_load_schema(PACKAGE / "corruption-plan.schema.json")).validate(registry)
    assert isinstance(registry, dict)
    corruptions = registry["corruptions"]
    assert isinstance(corruptions, list)
    assert len(corruptions) == 12
    assert len({row["id"] for row in corruptions}) == 12
    assert all(row["expected_invariant"] for row in corruptions)
    assert not (ROOT / "studies" / "DD-023-decentralized-recovery-equilibrium-robustness").exists()
