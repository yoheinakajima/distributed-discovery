"""Provider-specific strict-output schemas with provider-independent semantics."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal

from distributed_discovery.benchmark.agents_v1.actions import parse_action
from distributed_discovery.benchmark.agents_v1.adapters import AdapterRequest
from distributed_discovery.benchmark.agents_v1.models import VERSIONS, StructuredAction

OPENAI_PROVIDER = "openai"
ANTHROPIC_PROVIDER = "anthropic"
PROVIDERS = frozenset({OPENAI_PROVIDER, ANTHROPIC_PROVIDER})

OPENAI_UNSUPPORTED_KEYWORDS = frozenset(
    {
        "allOf",
        "not",
        "dependentRequired",
        "dependentSchemas",
        "if",
        "then",
        "else",
        "minLength",
        "maxLength",
        "patternProperties",
        "unevaluatedProperties",
        "propertyNames",
        "minProperties",
        "maxProperties",
        "unevaluatedItems",
        "contains",
        "minContains",
        "maxContains",
        "uniqueItems",
    }
)
ANTHROPIC_UNSUPPORTED_KEYWORDS = frozenset(
    {
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
        "minLength",
        "maxLength",
        "uniqueItems",
        "maxItems",
        "contains",
        "minContains",
        "maxContains",
    }
)
KNOWN_SCHEMA_KEYWORDS = frozenset(
    {
        "type",
        "enum",
        "const",
        "description",
        "default",
        "properties",
        "required",
        "additionalProperties",
        "items",
        "minItems",
        "maxItems",
        "uniqueItems",
        "anyOf",
        "allOf",
        "$ref",
        "$defs",
        "$def",
        "definitions",
        "pattern",
        "format",
        "minimum",
        "maximum",
        "multipleOf",
        "minLength",
        "maxLength",
        "not",
        "dependentRequired",
        "dependentSchemas",
        "if",
        "then",
        "else",
        "patternProperties",
        "unevaluatedProperties",
        "propertyNames",
        "minProperties",
        "maxProperties",
        "unevaluatedItems",
        "contains",
        "minContains",
        "maxContains",
    }
)


class ProviderSchemaError(ValueError):
    """Raised before a provider call when a transport schema is ineligible."""


@dataclass(frozen=True)
class PublicCanaryPolicy:
    """Exact public-only route and budget envelope validated before credentials."""

    openai_route: str = "openai_direct"
    openai_model: str = "gpt-5.4-2026-03-05"
    anthropic_route: str = "anthropic_direct"
    anthropic_model: str = "claude-sonnet-4-6"
    aliases_allowed: bool = False
    fallbacks_allowed: bool = False
    openrouter_allowed: bool = False
    batch_routes_allowed: bool = False
    local_models_allowed: bool = False
    call_cap: int = 10
    hard_cap_usd: Decimal = Decimal("1.00")
    openai_cap_usd: Decimal = Decimal("0.50")
    anthropic_cap_usd: Decimal = Decimal("0.50")
    expected_cost_usd: Decimal = Decimal("0.099999")
    cumulative_calls: int = 0
    cumulative_spend_usd: Decimal = Decimal("0")


EXPECTED_PUBLIC_CANARY_POLICY = PublicCanaryPolicy()


def validate_public_canary_policy(policy: PublicCanaryPolicy) -> None:
    """Reject route, model, fallback, privacy, call, or spend drift."""
    expected = EXPECTED_PUBLIC_CANARY_POLICY
    exact_fields = (
        "openai_route",
        "openai_model",
        "anthropic_route",
        "anthropic_model",
        "aliases_allowed",
        "fallbacks_allowed",
        "openrouter_allowed",
        "batch_routes_allowed",
        "local_models_allowed",
        "call_cap",
        "hard_cap_usd",
        "openai_cap_usd",
        "anthropic_cap_usd",
        "cumulative_calls",
        "cumulative_spend_usd",
    )
    for field_name in exact_fields:
        if getattr(policy, field_name) != getattr(expected, field_name):
            raise PermissionError(f"public canary policy mismatch: {field_name}")
    if policy.expected_cost_usd < 0 or policy.expected_cost_usd >= Decimal("0.10"):
        raise PermissionError("public canary expected cost must remain below USD 0.10")


def canonical_action_schema(request: AdapterRequest) -> dict[str, object]:
    """Return the provider-independent semantic action contract."""
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "task_instance_commitment",
            "agent_id",
            "round",
            "final",
            "visible_message",
            "source_choice",
            "actions",
            "declared_metadata",
        ],
        "properties": {
            "schema_version": {
                "type": "string",
                "enum": [VERSIONS["action"]],
            },
            "task_instance_commitment": {
                "type": "string",
                "enum": [f"sha256:{request.prompt.task_commitment}"],
            },
            "agent_id": {
                "type": "string",
                "enum": [request.prompt.agent_id],
            },
            "round": {
                "type": "integer",
                "enum": [request.round_number],
            },
            "final": {
                "type": "boolean",
                "enum": [request.final_required],
            },
            "visible_message": {"type": "string", "maxLength": 1024},
            "source_choice": {
                "type": "string",
                "enum": list(request.source_vocabulary),
            },
            "actions": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1 if request.final_required else 6,
                "uniqueItems": True,
                "description": (
                    "Exactly one final action."
                    if request.final_required
                    else "One to six explicitly non-final proposal candidates."
                ),
                "items": {
                    "type": "string",
                    "enum": list(request.action_vocabulary),
                },
            },
            "declared_metadata": {
                "type": "object",
                "additionalProperties": False,
                "required": [],
                "properties": {},
            },
        },
    }


def compile_openai_action_schema(request: AdapterRequest) -> dict[str, object]:
    """Compile the canonical contract to OpenAI's documented strict subset."""
    schema = _without_keywords(
        canonical_action_schema(request),
        {"maxLength", "uniqueItems"},
    )
    assert_provider_schema(OPENAI_PROVIDER, schema)
    return schema


def compile_anthropic_action_schema(request: AdapterRequest) -> dict[str, object]:
    """Compile the canonical contract to Anthropic's documented strict subset."""
    schema = _without_keywords(
        canonical_action_schema(request),
        {"maxLength", "maxItems", "uniqueItems"},
    )
    assert_provider_schema(ANTHROPIC_PROVIDER, schema)
    return schema


def minimal_provider_schema(provider: str) -> dict[str, object]:
    """Return one documented-minimal closed object for a public canary."""
    schema: dict[str, object] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["ok"],
        "properties": {"ok": {"type": "boolean"}},
    }
    assert_provider_schema(provider, schema)
    return schema


def public_canary_matrix(request: AdapterRequest) -> tuple[Mapping[str, object], ...]:
    """Return the deterministic minimal-then-complete two-provider sequence."""
    return (
        {
            "canary_id": "openai-minimal-known-valid",
            "provider": OPENAI_PROVIDER,
            "route": "openai_direct",
            "model": "gpt-5.4-2026-03-05",
            "schema": minimal_provider_schema(OPENAI_PROVIDER),
            "complete": False,
        },
        {
            "canary_id": "openai-treasurebench-complete",
            "provider": OPENAI_PROVIDER,
            "route": "openai_direct",
            "model": "gpt-5.4-2026-03-05",
            "schema": compile_openai_action_schema(request),
            "complete": True,
        },
        {
            "canary_id": "anthropic-minimal-known-valid",
            "provider": ANTHROPIC_PROVIDER,
            "route": "anthropic_direct",
            "model": "claude-sonnet-4-6",
            "schema": minimal_provider_schema(ANTHROPIC_PROVIDER),
            "complete": False,
        },
        {
            "canary_id": "anthropic-treasurebench-complete",
            "provider": ANTHROPIC_PROVIDER,
            "route": "anthropic_direct",
            "model": "claude-sonnet-4-6",
            "schema": compile_anthropic_action_schema(request),
            "complete": True,
        },
    )


def provider_bisection_matrix(
    provider: str,
    request: AdapterRequest,
) -> tuple[Mapping[str, object], ...]:
    """Return the frozen diagnostic schemas used only after a complete failure."""
    if provider not in PROVIDERS:
        raise ProviderSchemaError(f"unsupported provider: {provider}")
    action_array: dict[str, object] = {
        "type": "array",
        "minItems": 1,
        "description": "One diagnostic action from the public vocabulary.",
        "items": {
            "type": "string",
            "enum": list(request.action_vocabulary),
        },
    }
    if provider == OPENAI_PROVIDER:
        action_array["maxItems"] = 1
    action_core: dict[str, object] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["actions"],
        "properties": {"actions": action_array},
    }
    identity_envelope: dict[str, object] = {
        "type": "object",
        "additionalProperties": False,
        "required": ["agent_id", "final"],
        "properties": {
            "agent_id": {
                "type": "string",
                "enum": [request.prompt.agent_id],
            },
            "final": {
                "type": "boolean",
                "enum": [True],
            },
        },
    }
    for schema in (action_core, identity_envelope):
        assert_provider_schema(provider, schema)
    return (
        {
            "canary_id": f"{provider}-bisection-action-cardinality",
            "provider": provider,
            "schema": action_core,
            "diagnostic_order": 1,
        },
        {
            "canary_id": f"{provider}-bisection-identity-envelope",
            "provider": provider,
            "schema": identity_envelope,
            "diagnostic_order": 2,
        },
    )


def validate_action_semantics(raw_output: str, request: AdapterRequest) -> StructuredAction:
    """Apply the unchanged semantic contract after provider parsing."""
    return parse_action(
        raw_output,
        task_commitment=request.prompt.task_commitment,
        agent_id=request.prompt.agent_id,
        round_number=request.round_number,
        action_vocabulary=request.action_vocabulary,
        source_vocabulary=request.source_vocabulary,
        final_required=request.final_required,
    )


def assert_provider_schema(provider: str, schema: Mapping[str, object]) -> None:
    issues = provider_schema_issues(provider, schema)
    if issues:
        raise ProviderSchemaError("; ".join(issues))


def provider_schema_issues(
    provider: str,
    schema: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic subset violations with JSON-style paths."""
    if provider not in PROVIDERS:
        return (f"unsupported provider: {provider}",)
    issues: list[str] = []
    if schema.get("type") != "object":
        issues.append("$: root type must be object")
    _walk_schema(provider, schema, "$", issues)
    return tuple(sorted(set(issues)))


def schema_fingerprint(schema: Mapping[str, object]) -> str:
    encoded = json.dumps(schema, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def assert_schema_fingerprint(schema: Mapping[str, object], expected: str) -> None:
    actual = schema_fingerprint(schema)
    if actual != expected:
        raise ProviderSchemaError(f"provider schema drift: expected {expected}, observed {actual}")


def _without_keywords(
    schema: Mapping[str, object],
    omitted: set[str],
) -> dict[str, object]:
    result = copy.deepcopy(dict(schema))

    def visit(value: object) -> None:
        if isinstance(value, dict):
            for key in tuple(value):
                if key in omitted:
                    del value[key]
                else:
                    visit(value[key])
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(result)
    return result


def _walk_schema(
    provider: str,
    schema: Mapping[str, object],
    path: str,
    issues: list[str],
) -> None:
    unsupported = (
        OPENAI_UNSUPPORTED_KEYWORDS
        if provider == OPENAI_PROVIDER
        else ANTHROPIC_UNSUPPORTED_KEYWORDS
    )
    for keyword in schema:
        if keyword not in KNOWN_SCHEMA_KEYWORDS:
            issues.append(f"{path}: unsupported keyword {keyword}")
        elif keyword in unsupported:
            issues.append(f"{path}: {provider} does not support {keyword}")

    schema_type = schema.get("type")
    if schema_type == "object":
        properties = schema.get("properties")
        required = schema.get("required")
        if not isinstance(properties, Mapping):
            issues.append(f"{path}: object must declare properties")
            properties = {}
        if schema.get("additionalProperties") is not False:
            issues.append(f"{path}: additionalProperties must be false")
        if not isinstance(required, Sequence) or isinstance(required, (str, bytes)):
            issues.append(f"{path}: object must declare required")
            required_names: tuple[str, ...] = ()
        else:
            required_names = tuple(str(item) for item in required)
        if len(required_names) != len(set(required_names)):
            issues.append(f"{path}: required contains duplicates")
        unknown_required = set(required_names) - set(str(key) for key in properties)
        if unknown_required:
            issues.append(f"{path}: required names missing from properties")
        if provider == OPENAI_PROVIDER and set(required_names) != set(properties):
            issues.append(f"{path}: OpenAI requires every property")
        if provider == ANTHROPIC_PROVIDER:
            optional_count = len(properties) - len(set(required_names))
            if optional_count > 24:
                issues.append(f"{path}: Anthropic optional-parameter limit exceeded")
        for name, child in properties.items():
            if not isinstance(child, Mapping):
                issues.append(f"{path}.properties.{name}: schema must be an object")
                continue
            _walk_schema(provider, child, f"{path}.properties.{name}", issues)
    if schema_type == "array":
        items = schema.get("items")
        if not isinstance(items, Mapping):
            issues.append(f"{path}: array must declare an item schema")
        else:
            _walk_schema(provider, items, f"{path}.items", issues)
        if (
            provider == ANTHROPIC_PROVIDER
            and "minItems" in schema
            and schema["minItems"] not in {0, 1}
        ):
            issues.append(f"{path}: Anthropic minItems must be 0 or 1")

    for keyword in ("anyOf", "allOf"):
        alternatives = schema.get(keyword)
        if alternatives is None:
            continue
        if not isinstance(alternatives, Sequence) or isinstance(alternatives, (str, bytes)):
            issues.append(f"{path}.{keyword}: must be an array")
            continue
        for index, child in enumerate(alternatives):
            if not isinstance(child, Mapping):
                issues.append(f"{path}.{keyword}[{index}]: schema must be an object")
            else:
                _walk_schema(provider, child, f"{path}.{keyword}[{index}]", issues)
