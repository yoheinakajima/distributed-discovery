"""Offline-only registration validators for DiscoveryBench Agents v1.

This module deliberately has no provider client, network transport, credential
loader, model downloader, or private-holdout generator.
"""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import cast

import jsonschema
import yaml

REGISTRY = Path("docs/benchmark/agents-v1")
PROMPT_PROHIBITIONS = (
    re.compile(r"\bDD-\d{3}[A-Z]?\b"),
    re.compile(r"\bDD-C-\d{4}\b"),
    re.compile(r"\b20\d{6}T\d{6}Z_DD-"),
    re.compile(r"\b(expected (?:value|metric|answer)|answer[_ -]?key)\b", re.IGNORECASE),
    re.compile(r"\b(?:paradox|one-reader theorem)\b", re.IGNORECASE),
)
REDACTION_PATTERNS = (
    (re.compile(r"/(?:Users|home)/[^\s\"']+"), "[REDACTED:HOST_PATH]"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._-]+"), "[REDACTED:BEARER]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"), "[REDACTED:API_KEY]"),
    (re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"), "[REDACTED:EMAIL]"),
)


def canonical_json(value: object) -> bytes:
    """Return the exact UTF-8 serialization used by public commitments."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_hex(value: bytes) -> str:
    """Return a lowercase SHA-256 digest."""
    return hashlib.sha256(value).hexdigest()


def trace_hash(trace: dict[str, object]) -> str:
    """Hash a trace without its self-referential trace_sha256 field."""
    payload = {key: value for key, value in trace.items() if key != "trace_sha256"}
    return sha256_hex(canonical_json(payload))


def load_yaml(path: Path) -> dict[str, object]:
    """Load a mapping-valued YAML document."""
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} is not a mapping")
    return cast(dict[str, object], value)


def load_json(path: Path) -> dict[str, object]:
    """Load a mapping-valued JSON document."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} is not a mapping")
    return cast(dict[str, object], value)


def validate_document(document: object, schema: dict[str, object]) -> None:
    """Validate a document against its Draft 2020-12 schema."""
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(document)


def prompt_leaks(value: object) -> tuple[str, ...]:
    """Return registered leak classes present in a public prompt-like value."""
    text = json.dumps(value, sort_keys=True)
    return tuple(pattern.pattern for pattern in PROMPT_PROHIBITIONS if pattern.search(text))


def validate_capability_isolation(task: dict[str, object]) -> None:
    """Reject target/answer/other-agent data in an agent's capability view."""
    views = task.get("capability_views")
    if not isinstance(views, dict):
        raise ValueError("task has no capability_views")
    for agent_id, view in views.items():
        if not isinstance(view, dict):
            raise ValueError(f"{agent_id} capability view is not a mapping")
        for prohibited in ("target\":", "answer_key\":", "other_agent_private_observation\":"):
            # The explicit forbidden_fields declaration may name a field; an actual
            # key/value outside that declaration is what is prohibited.
            payload = {key: value for key, value in view.items() if key != "forbidden_fields"}
            if prohibited in json.dumps(payload, sort_keys=True).lower():
                raise ValueError(f"{agent_id} leaks {prohibited[:-2]}")


def deterministic_mock_action(
    task: dict[str, object], agent_id: str, *, round_number: int = 0
) -> dict[str, object]:
    """Return a deterministic public-fixture action without external calls."""
    views = cast(dict[str, dict[str, object]], task["capability_views"])
    view = views[agent_id]
    clue = str(view["private_observation"])
    target = clue.replace("CLUE-", "TARGET-")
    vocabulary = cast(list[str], task["action_vocabulary"])
    if target not in vocabulary:
        target = sorted(vocabulary)[0]
    return {
        "schema_version": "agents-action-v1",
        "task_instance_commitment": task["task_commitment"],
        "agent_id": agent_id,
        "round": round_number,
        "final": True,
        "visible_message": "Public deterministic mock used its private clue.",
        "source_choice": "none",
        "actions": [target],
        "declared_confidence": 0.5,
    }


def redact_value(value: object) -> tuple[object, dict[str, int]]:
    """Apply deterministic public redaction to every string leaf."""
    counts: dict[str, int] = {}

    def redact(item: object) -> object:
        if isinstance(item, dict):
            return {str(key): redact(child) for key, child in item.items()}
        if isinstance(item, list):
            return [redact(child) for child in item]
        if not isinstance(item, str):
            return item
        result = item
        for pattern, replacement in REDACTION_PATTERNS:
            result, count = pattern.subn(replacement, result)
            if count:
                counts[replacement] = counts.get(replacement, 0) + count
        return result

    return redact(deepcopy(value)), counts


def verify_public_custody_vector(vector: dict[str, object]) -> None:
    """Verify the clearly public SHA-256 custody vector."""
    if vector.get("public_test_only") is not True:
        raise ValueError("custody vector is not explicitly public")
    commitments = cast(dict[str, str], vector["commitments"])
    seed_payload = (
        commitments["domain_separator"].encode() + str(vector["seed_text"]).encode()
    )
    if sha256_hex(seed_payload) != commitments["seed_sha256"]:
        raise ValueError("seed commitment mismatch")
    if sha256_hex(str(vector["instance_text"]).encode()) != commitments["instance_sha256"]:
        raise ValueError("instance commitment mismatch")


def validate_corruptions(plan: dict[str, object]) -> None:
    """Check the 24-entry corruption registry is complete and unique."""
    rows = cast(list[dict[str, object]], plan["corruptions"])
    if len(rows) < 24:
        raise ValueError("fewer than 24 corruptions")
    ids = {str(row["id"]) for row in rows}
    if len(ids) != len(rows):
        raise ValueError("duplicate corruption IDs")
    required = {"mutation", "rejecting_component", "error_class", "purpose"}
    for row in rows:
        if not required.issubset(row):
            raise ValueError(f"incomplete corruption {row.get('id')}")


def registry_documents(root: Path) -> tuple[tuple[Path, Path], ...]:
    """Return every registered schema/document pair."""
    base = root / REGISTRY
    return (
        (base / "versioning.yml", base / "versioning.schema.json"),
        (base / "task-families.yml", base / "task-families.schema.json"),
        (base / "agent-protocol.yml", base / "agent-protocol.schema.json"),
        (base / "team-architectures.yml", base / "team-architectures.schema.json"),
        (
            base / "provider-model-candidates.yml",
            base / "provider-model-candidates.schema.json",
        ),
        (base / "metrics.yml", base / "metrics.schema.json"),
        (base / "statistical-analysis.yml", base / "statistical-analysis.schema.json"),
        (
            root
            / "reports/roadmap-consolidation/discoverybench-agents-v1-registration-decision.yml",
            base / "registration-decision.schema.json",
        ),
    )


def audit_registration(root: Path) -> dict[str, object]:
    """Run the complete offline registration audit."""
    base = root / REGISTRY
    for document_path, schema_path in registry_documents(root):
        validate_document(load_yaml(document_path), load_json(schema_path))

    fixture_pairs = (
        ("valid-task-instance.json", "task-instance.schema.json"),
        ("valid-action.json", "structured-output.schema.json"),
        ("valid-execution-config.yml", "execution-config.schema.json"),
        ("valid-contamination-report.json", "contamination-report.schema.json"),
        ("valid-trace.json", "trace.schema.json"),
    )
    for fixture_name, schema_name in fixture_pairs:
        fixture_path = base / "fixtures" / fixture_name
        document = (
            load_yaml(fixture_path)
            if fixture_path.suffix == ".yml"
            else load_json(fixture_path)
        )
        validate_document(document, load_json(base / schema_name))

    invalid_pairs = (
        ("invalid-action.json", "structured-output.schema.json"),
        ("invalid-contamination-report.json", "contamination-report.schema.json"),
    )
    for fixture_name, schema_name in invalid_pairs:
        try:
            validate_document(
                load_json(base / "fixtures" / fixture_name), load_json(base / schema_name)
            )
        except jsonschema.ValidationError:
            continue
        raise ValueError(f"invalid fixture unexpectedly validated: {fixture_name}")

    task = load_json(base / "fixtures/valid-task-instance.json")
    validate_capability_isolation(task)
    visible_fixture = {
        "task_id": task["task_id"],
        "family_id": task["family_id"],
        "action_vocabulary": task["action_vocabulary"],
        "capability_views": {
            agent_id: {
                key: value
                for key, value in cast(dict[str, object], view).items()
                if key != "forbidden_fields"
            }
            for agent_id, view in cast(dict[str, object], task["capability_views"]).items()
        },
    }
    if prompt_leaks(visible_fixture):
        raise ValueError("valid public task contains contamination cue")
    if not prompt_leaks(load_json(base / "fixtures/invalid-task-leak.json")):
        raise ValueError("invalid prompt leak fixture was not detected")
    mock = deterministic_mock_action(task, "AGENT-01")
    validate_document(mock, load_json(base / "structured-output.schema.json"))

    vector = load_yaml(base / "public-test-vectors/custody-public-toy.yml")
    validate_document(vector, load_json(base / "custody-manifest.schema.json"))
    verify_public_custody_vector(vector)

    trace = load_json(base / "fixtures/valid-trace.json")
    if trace_hash(trace) != trace["trace_sha256"]:
        raise ValueError("valid trace hash mismatch")
    invalid_trace = load_json(base / "fixtures/invalid-trace-unredacted.json")
    redacted, counts = redact_value(invalid_trace)
    if not counts or "/Users/" in json.dumps(redacted):
        raise ValueError("redaction fixture was not redacted")

    corruptions = load_yaml(base / "corruption-plan.yml")
    validate_corruptions(corruptions)
    families = load_yaml(base / "task-families.yml")
    family_rows = cast(list[dict[str, object]], families["families"])
    claims_text = (root / "claims/claims.yml").read_text(encoding="utf-8")
    for family in family_rows:
        for claim_id in cast(list[str], family["claim_ids"]):
            if claim_id not in claims_text:
                raise ValueError(f"unknown scientific owner claim: {claim_id}")
        for run_id in cast(list[str], family["source_runs"]):
            if not any((root / "results").glob(f"**/{run_id}/manifest.json")):
                raise ValueError(f"unknown scientific owner run: {run_id}")

    return {
        "schemas": len(tuple(base.glob("*.schema.json"))),
        "valid_fixtures": len(fixture_pairs),
        "invalid_fixtures": 3,
        "task_families": len(family_rows),
        "generator_cells": sum(
            cast(int, row["canonical_cells"]) for row in family_rows
        ),
        "primitive_states": sum(
            cast(int, row["primitive_labeled_task_states"]) for row in family_rows
        ),
        "architectures": load_yaml(base / "team-architectures.yml")[
            "agent_architecture_count"
        ],
        "model_candidates": len(
            cast(list[object], load_yaml(base / "provider-model-candidates.yml")["candidates"])
        ),
        "metrics": len(cast(list[object], load_yaml(base / "metrics.yml")["metrics"])),
        "corruptions": len(cast(list[object], corruptions["corruptions"])),
        "provider_calls": 0,
        "model_downloads": 0,
        "private_seeds": 0,
        "holdouts": 0,
        "traces": 0,
        "results": 0,
    }
