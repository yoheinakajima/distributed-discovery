from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import jsonschema
import pytest

from distributed_discovery.benchmark.agents import (
    audit_registration,
    deterministic_mock_action,
    load_json,
    load_yaml,
    prompt_leaks,
    redact_value,
    trace_hash,
    validate_capability_isolation,
    validate_corruptions,
    validate_document,
    verify_public_custody_vector,
)

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/benchmark/agents-v1"


def test_agents_registration_audit_is_offline_and_complete() -> None:
    result = audit_registration(ROOT)
    assert result == {
        "architectures": 5,
        "corruptions": 24,
        "generator_cells": 138,
        "holdouts": 0,
        "invalid_fixtures": 4,
        "metrics": 15,
        "model_candidates": 4,
        "model_downloads": 0,
        "primitive_states": 58945,
        "private_seeds": 0,
        "provider_calls": 0,
        "results": 0,
        "schemas": 25,
        "task_families": 5,
        "traces": 0,
        "valid_fixtures": 6,
    }


def test_task_capability_isolation_rejects_target_leak() -> None:
    task = load_json(BASE / "fixtures/valid-task-instance.json")
    validate_capability_isolation(task)
    corrupted = deepcopy(task)
    views = corrupted["capability_views"]
    assert isinstance(views, dict)
    agent = views["AGENT-01"]
    assert isinstance(agent, dict)
    agent["target"] = "TARGET-B"
    with pytest.raises(ValueError, match="leaks target"):
        validate_capability_isolation(corrupted)


def test_deterministic_mock_is_repeatable_and_schema_valid() -> None:
    task = load_json(BASE / "fixtures/valid-task-instance.json")
    first = deterministic_mock_action(task, "AGENT-01")
    second = deterministic_mock_action(task, "AGENT-01")
    assert first == second
    assert first["actions"] == ["TARGET-B"]
    validate_document(first, load_json(BASE / "structured-output.schema.json"))


def test_prompt_contamination_cues_are_detected() -> None:
    assert prompt_leaks({"prompt": "Use claim DD-C-0059 and expected value 2/3."})
    assert not prompt_leaks({"prompt": "Choose one of TARGET-A, TARGET-B, TARGET-C."})


def test_public_custody_vector_is_domain_separated_and_verified() -> None:
    vector = load_yaml(BASE / "public-test-vectors/custody-public-toy.yml")
    verify_public_custody_vector(vector)
    corrupted = deepcopy(vector)
    corrupted["seed_text"] = "PUBLIC-TOY-SEED-0002"
    with pytest.raises(ValueError, match="seed commitment mismatch"):
        verify_public_custody_vector(corrupted)


def test_trace_hash_detects_mutation() -> None:
    trace = load_json(BASE / "fixtures/valid-trace.json")
    assert trace_hash(trace) == trace["trace_sha256"]
    trace["declared_actions"] = ["TARGET-A"]
    assert trace_hash(trace) != trace["trace_sha256"]


def test_redaction_removes_path_token_email_and_key_patterns() -> None:
    fixture = load_json(BASE / "fixtures/invalid-trace-unredacted.json")
    fixture["email"] = "toy@example.test"
    fixture["key"] = "sk-PUBLICINVALID123"
    redacted, counts = redact_value(fixture)
    rendered = json.dumps(redacted)
    assert "/Users/" not in rendered
    assert "Bearer " not in rendered
    assert "toy@example.test" not in rendered
    assert "sk-PUBLICINVALID123" not in rendered
    assert sum(counts.values()) == 4


def test_invalid_fixtures_are_rejected() -> None:
    with pytest.raises(jsonschema.ValidationError):
        validate_document(
            load_json(BASE / "fixtures/invalid-action.json"),
            load_json(BASE / "structured-output.schema.json"),
        )
    with pytest.raises(jsonschema.ValidationError):
        validate_document(
            load_json(BASE / "fixtures/invalid-contamination-report.json"),
            load_json(BASE / "contamination-report.schema.json"),
        )


def test_corruption_registry_has_24_unique_complete_entries() -> None:
    plan = load_yaml(BASE / "corruption-plan.yml")
    validate_corruptions(plan)
    rows = plan["corruptions"]
    assert isinstance(rows, list)
    assert len(rows) == 24


def test_provider_registry_has_two_cloud_families_and_local_open_candidate() -> None:
    registry = load_yaml(BASE / "provider-model-candidates.yml")
    candidates = registry["candidates"]
    assert isinstance(candidates, list)
    cloud_providers = {row["provider"] for row in candidates if row["deployment"] == "cloud-api"}
    assert {"OpenAI", "Anthropic"}.issubset(cloud_providers)
    assert any(row["deployment"] == "local-open-weights" for row in candidates)
    assert registry["execution_authorized"] is False
    assert all(row["moving_alias_status"] != "allowed" for row in candidates)


def test_no_provider_implementation_or_network_import_exists() -> None:
    source = (ROOT / "src/distributed_discovery/benchmark/agents.py").read_text(encoding="utf-8")
    assert "import requests" not in source
    assert "import httpx" not in source
    assert "import openai" not in source
    assert "import anthropic" not in source
    assert "subprocess" not in source
