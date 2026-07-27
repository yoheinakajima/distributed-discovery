from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import jsonschema
import pytest

from distributed_discovery.benchmark.agents_v1.adapters import AdapterRequest
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.live_providers import (
    ANTHROPIC_MANIFEST,
    OPENAI_MANIFEST,
    build_anthropic_messages_payload,
    build_openai_responses_payload,
)
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.provider_schema import (
    ANTHROPIC_PROVIDER,
    EXPECTED_PUBLIC_CANARY_POLICY,
    OPENAI_PROVIDER,
    ProviderSchemaError,
    assert_provider_schema,
    assert_schema_fingerprint,
    canonical_action_schema,
    compile_anthropic_action_schema,
    compile_openai_action_schema,
    provider_schema_issues,
    public_canary_matrix,
    schema_fingerprint,
    validate_action_semantics,
    validate_public_canary_policy,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "docs/benchmark/agents-v1/fixtures/provider-schema"


def _request(manifest: Any = OPENAI_MANIFEST) -> AdapterRequest:
    task = generate_public_calibration()[2]
    agent_id = sorted(task.capabilities)[0]
    return AdapterRequest(
        prompt=compile_prompt(
            task,
            agent_id,
            architecture_id="provider-native-smoke",
            final_required=True,
        ),
        manifest=manifest,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        final_required=True,
    )


def _valid_action(request: AdapterRequest) -> dict[str, object]:
    return {
        "schema_version": "agents-action-v1",
        "task_instance_commitment": f"sha256:{request.prompt.task_commitment}",
        "agent_id": request.prompt.agent_id,
        "round": 0,
        "final": True,
        "visible_message": "public",
        "source_choice": request.source_vocabulary[0],
        "actions": [request.action_vocabulary[0]],
        "declared_metadata": {},
    }


def test_reconstructed_openai_request_contains_corrected_bounded_violations() -> None:
    request = _request()
    payload = build_openai_responses_payload(
        request,
        schema=canonical_action_schema(request),
    )
    text = payload["text"]
    assert isinstance(text, dict)
    schema = text["format"]["schema"]
    assert isinstance(schema, dict)
    issues = provider_schema_issues(OPENAI_PROVIDER, schema)
    for keyword in ("maxLength", "uniqueItems"):
        assert any(keyword in issue for issue in issues)
    for keyword in ("minItems", "maxItems"):
        assert not any(keyword in issue for issue in issues)
    assert payload["model"] == "gpt-5.4-2026-03-05"
    assert payload["reasoning"] == {"effort": "none"}
    assert payload["store"] is False


def test_provider_compilers_preserve_canonical_semantics_outside_transport() -> None:
    request = _request()
    canonical = canonical_action_schema(request)
    openai = compile_openai_action_schema(request)
    anthropic = compile_anthropic_action_schema(request)
    canonical_properties = cast(dict[str, object], canonical["properties"])
    openai_properties = cast(dict[str, object], openai["properties"])
    anthropic_properties = cast(dict[str, object], anthropic["properties"])
    canonical_actions = cast(dict[str, object], canonical_properties["actions"])
    openai_actions = cast(dict[str, object], openai_properties["actions"])
    anthropic_actions = cast(dict[str, object], anthropic_properties["actions"])
    assert canonical_actions["minItems"] == 1
    assert canonical_actions["maxItems"] == 1
    assert canonical_actions["uniqueItems"] is True
    assert openai_actions["minItems"] == 1
    assert openai_actions["maxItems"] == 1
    assert "uniqueItems" not in openai_actions
    assert anthropic_actions["minItems"] == 1
    assert all(keyword not in anthropic_actions for keyword in ("maxItems", "uniqueItems"))
    assert_provider_schema(OPENAI_PROVIDER, openai)
    assert_provider_schema(ANTHROPIC_PROVIDER, anthropic)


@pytest.mark.parametrize(
    ("corruption", "expected"),
    [
        ("unsupported-provider-keyword", "uniqueItems"),
        ("omitted-required-field-declaration", "every property"),
        ("missing-additional-properties-false", "additionalProperties"),
        ("empty-nested-object", "must declare properties"),
    ],
)
def test_provider_schema_corruptions_fail_offline(corruption: str, expected: str) -> None:
    request = _request()
    schema = compile_openai_action_schema(request)
    properties = schema["properties"]
    assert isinstance(properties, dict)
    if corruption == "unsupported-provider-keyword":
        actions = cast(dict[str, object], properties["actions"])
        actions["uniqueItems"] = True
    elif corruption == "omitted-required-field-declaration":
        required = schema["required"]
        assert isinstance(required, list)
        schema["required"] = required[1:]
    elif corruption == "missing-additional-properties-false":
        del schema["additionalProperties"]
    elif corruption == "empty-nested-object":
        properties["declared_metadata"] = {"type": "object"}
    with pytest.raises(ProviderSchemaError, match=expected):
        assert_provider_schema(OPENAI_PROVIDER, schema)


def test_provider_schema_drift_fails_exact_fingerprint() -> None:
    schema = compile_openai_action_schema(_request())
    expected = schema_fingerprint(schema)
    drifted = deepcopy(schema)
    drifted["description"] = "provider drift"
    with pytest.raises(ProviderSchemaError, match="provider schema drift"):
        assert_schema_fingerprint(drifted, expected)


def test_openai_transport_and_post_parse_both_enforce_one_final_action() -> None:
    request = _request()
    schema = compile_openai_action_schema(request)
    for actions, message in (
        (["TARGET-A", "TARGET-B"], "final action cardinality"),
        ([], "missing actions"),
    ):
        value = _valid_action(request)
        value["actions"] = actions
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(value, schema)
        with pytest.raises(ValueError, match=message):
            validate_action_semantics(json.dumps(value), request)


def test_omitted_openai_max_length_remains_post_parse_enforced() -> None:
    request = _request()
    value = _valid_action(request)
    value["visible_message"] = "x" * 1025
    schema = compile_openai_action_schema(request)
    jsonschema.validate(value, schema)
    with pytest.raises(ValueError, match="visible message"):
        validate_action_semantics(json.dumps(value), request)


def test_complete_payloads_use_distinct_provider_compilers() -> None:
    openai_request = _request(OPENAI_MANIFEST)
    anthropic_request = _request(ANTHROPIC_MANIFEST)
    openai = build_openai_responses_payload(openai_request)
    anthropic = build_anthropic_messages_payload(anthropic_request)
    openai_text = cast(Mapping[str, object], openai["text"])
    openai_format = cast(Mapping[str, object], openai_text["format"])
    openai_schema = cast(Mapping[str, object], openai_format["schema"])
    anthropic_output = cast(Mapping[str, object], anthropic["output_config"])
    anthropic_format = cast(Mapping[str, object], anthropic_output["format"])
    anthropic_schema = cast(Mapping[str, object], anthropic_format["schema"])
    assert provider_schema_issues(OPENAI_PROVIDER, openai_schema) == ()
    assert provider_schema_issues(ANTHROPIC_PROVIDER, anthropic_schema) == ()
    assert openai_schema != anthropic_schema


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("openai_route", "openrouter"),
        ("openai_model", "gpt-5.4"),
        ("anthropic_route", "anthropic_batch"),
        ("anthropic_model", "claude-sonnet-latest"),
        ("aliases_allowed", True),
        ("fallbacks_allowed", True),
        ("openrouter_allowed", True),
        ("batch_routes_allowed", True),
        ("local_models_allowed", True),
        ("call_cap", 11),
        ("hard_cap_usd", Decimal("1.01")),
        ("openai_cap_usd", Decimal("0.51")),
        ("anthropic_cap_usd", Decimal("0.51")),
        ("cumulative_calls", 1),
        ("cumulative_spend_usd", Decimal("0.01")),
        ("expected_cost_usd", Decimal("0.10")),
    ],
)
def test_route_model_alias_fallback_call_and_spend_drift_fails(
    field_name: str,
    value: object,
) -> None:
    policy = replace(
        EXPECTED_PUBLIC_CANARY_POLICY,
        **{field_name: value},  # type: ignore[arg-type]
    )
    with pytest.raises(PermissionError, match="public canary"):
        validate_public_canary_policy(policy)


def test_deterministic_canary_matrix_requires_both_complete_schemas() -> None:
    matrix = public_canary_matrix(_request())
    assert [item["canary_id"] for item in matrix] == [
        "openai-minimal-known-valid",
        "openai-treasurebench-complete",
        "anthropic-minimal-known-valid",
        "anthropic-treasurebench-complete",
    ]
    assert [item["complete"] for item in matrix] == [False, True, False, True]
    for item in matrix:
        schema = item["schema"]
        assert isinstance(schema, Mapping)
        assert_provider_schema(str(item["provider"]), schema)


def test_committed_serialized_request_fixtures_match_compilers_and_hashes() -> None:
    openai_request = _request(OPENAI_MANIFEST)
    anthropic_request = _request(ANTHROPIC_MANIFEST)
    expected = {
        "openai-terminal-http400-reconstructed.json": build_openai_responses_payload(
            openai_request,
            schema=canonical_action_schema(openai_request),
        ),
        "openai-treasurebench-complete.json": build_openai_responses_payload(openai_request),
        "anthropic-treasurebench-complete.json": build_anthropic_messages_payload(
            anthropic_request
        ),
    }
    for filename, payload in expected.items():
        assert json.loads((FIXTURE_ROOT / filename).read_text(encoding="utf-8")) == payload

    matrix = json.loads((FIXTURE_ROOT / "canary-matrix.json").read_text(encoding="utf-8"))
    for fixture in matrix["fixtures"]:
        data = (ROOT / fixture["path"]).read_bytes()
        assert f"sha256:{hashlib.sha256(data).hexdigest()}" == fixture["sha256"]
