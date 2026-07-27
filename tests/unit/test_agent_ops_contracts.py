from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
AGENT_OPS = ROOT / "docs/agent-ops"


def _validate_yaml(instance: Path, schema: Path) -> dict[str, object]:
    value = yaml.safe_load(instance.read_text(encoding="utf-8"))
    definition = json.loads(schema.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(definition).validate(value)
    assert isinstance(value, dict)
    return value


def test_task_contract_template_and_active_contract_validate() -> None:
    schema = AGENT_OPS / "task-contract.schema.json"
    template = _validate_yaml(AGENT_OPS / "task-contract-template.yml", schema)
    active = _validate_yaml(ROOT / "tasks/agent-operations-v1.yml", schema)
    fresh = _validate_yaml(
        ROOT / "tasks/treasurebench-agents-v1-fresh-pilot.yml",
        schema,
    )
    assert template["task_id"] == "AO-0000"
    assert active["task_id"] == "AO-0001"
    assert fresh["task_id"] == "AO-0002"
    assert fresh["task_type"] == "private-evaluation"
    assert active["scientific_mutation_permissions"] == {
        "create_study": False,
        "create_claim": False,
        "create_run": False,
        "change_evidence_status": False,
        "change_proof_status": False,
        "change_paper_lifecycle": False,
    }


def test_task_delta_template_validates_and_defaults_closed() -> None:
    delta = _validate_yaml(
        AGENT_OPS / "task-delta-template.yml",
        AGENT_OPS / "task-delta.schema.json",
    )
    assert not any(delta["permissions"].values())


def test_task_contract_rejects_hidden_repository_permission() -> None:
    active = yaml.safe_load((ROOT / "tasks/agent-operations-v1.yml").read_text())
    schema = json.loads((AGENT_OPS / "task-contract.schema.json").read_text())
    corrupted = copy.deepcopy(active)
    corrupted["permissions"]["undeclared_external_action"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(corrupted)
