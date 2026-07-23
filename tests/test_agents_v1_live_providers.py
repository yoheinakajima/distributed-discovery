from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest

from distributed_discovery.benchmark.agents_v1.adapters import AdapterRequest
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CostLedger,
    PreflightAuthorization,
)
from distributed_discovery.benchmark.agents_v1.live_providers import (
    ANTHROPIC_MANIFEST,
    OPENAI_MANIFEST,
    AnthropicMessagesAdapter,
    HttpRequest,
    HttpResponse,
    OpenAIResponsesAdapter,
    OpenRouterAdapter,
    OpenRouterEndpoint,
    RoutePricing,
    action_schema,
    discover_openrouter_endpoints,
    normalize_http_error,
    select_openrouter_endpoint,
)
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt


class FakeTransport:
    def __init__(self, response: HttpResponse) -> None:
        self.response = response
        self.requests: list[HttpRequest] = []

    def send(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        return self.response


def _authorization() -> PreflightAuthorization:
    return PreflightAuthorization(
        authorization_id="test-auth",
        authorized_base_commit="a" * 40,
        allowed_branch="benchmark/discoverybench-agents-v1-provider-preflight",
        expires_utc=datetime.now(UTC) + timedelta(days=1),
        total_cap_usd=Decimal("20"),
        gateway_caps_usd={
            "openai_direct": Decimal("5"),
            "anthropic_direct": Decimal("5"),
            "openrouter": Decimal("20"),
        },
        route_caps_usd={
            "openrouter_mistral_small_3_1": Decimal("5"),
            "openrouter_gemini_2_5_pro": Decimal("10"),
        },
        max_calls_per_route=600,
        max_total_calls=2_000,
        max_live_concurrency=2,
        private_tasks_allowed=False,
        scientific_evidence_allowed=False,
        raw={},
    )


def _request(manifest: Any) -> AdapterRequest:
    task = generate_public_calibration()[0]
    agent_id = sorted(task.capabilities)[0]
    return AdapterRequest(
        prompt=compile_prompt(task, agent_id),
        manifest=manifest,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        final_required=True,
    )


def _action(request: AdapterRequest) -> str:
    return json.dumps(
        {
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
    )


def test_request_repr_redacts_headers() -> None:
    request = HttpRequest("GET", "https://example.test", headers={"Authorization": "secret"})
    assert "secret" not in repr(request)
    assert "redacted" in repr(request)


def test_action_schema_freezes_task_fields_and_vocabularies() -> None:
    request = _request(OPENAI_MANIFEST)
    schema = action_schema(request)
    properties = schema["properties"]
    assert isinstance(properties, dict)
    assert properties["agent_id"] == {
        "type": "string",
        "enum": [request.prompt.agent_id],
    }
    assert properties["actions"]["items"]["enum"] == list(request.action_vocabulary)
    assert "maxLength" not in properties["visible_message"]
    assert "minItems" not in properties["actions"]
    assert "maxItems" not in properties["actions"]


def test_openai_payload_and_response_parser() -> None:
    request = _request(OPENAI_MANIFEST)
    output = _action(request)
    transport = FakeTransport(
        HttpResponse(
            200,
            {
                "id": "resp_safe",
                "model": OPENAI_MANIFEST.exact_snapshot,
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": output}],
                    }
                ],
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 40,
                    "input_tokens_details": {"cached_tokens": 5},
                    "output_tokens_details": {"reasoning_tokens": 0},
                },
            },
        )
    )
    adapter = OpenAIResponsesAdapter(
        api_key="synthetic-secret",
        transport=transport,
        network_enabled=True,
        ledger=CostLedger(_authorization()),
    )
    result = adapter.respond(request)
    payload = transport.requests[0].body
    assert payload is not None
    assert payload["model"] == "gpt-5.4-2026-03-05"
    assert payload["store"] is False
    assert payload["reasoning"] == {"effort": "none"}
    assert result.raw_output == output
    assert result.usage.input_tokens == 100
    assert result.usage.cost_usd == Decimal("0.00085")
    assert "synthetic-secret" not in repr(adapter)
    assert "Authorization" not in result.operational_metadata


def test_openai_is_disabled_by_default() -> None:
    adapter = OpenAIResponsesAdapter(
        api_key="synthetic-secret",
        transport=FakeTransport(HttpResponse(200, {})),
        network_enabled=False,
        ledger=CostLedger(_authorization()),
    )
    with pytest.raises(PermissionError, match="disabled"):
        adapter.respond(_request(OPENAI_MANIFEST))


def test_anthropic_payload_and_response_parser() -> None:
    request = _request(ANTHROPIC_MANIFEST)
    output = _action(request)
    transport = FakeTransport(
        HttpResponse(
            200,
            {
                "id": "msg_safe",
                "model": ANTHROPIC_MANIFEST.exact_snapshot,
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": output}],
                "usage": {"input_tokens": 80, "output_tokens": 30},
            },
        )
    )
    adapter = AnthropicMessagesAdapter(
        api_key="synthetic-secret",
        transport=transport,
        network_enabled=True,
        ledger=CostLedger(_authorization()),
    )
    result = adapter.respond(request)
    payload = transport.requests[0].body
    assert payload is not None
    assert payload["model"] == "claude-sonnet-4-6"
    assert payload["temperature"] == 0
    assert "output_config" in payload
    assert result.raw_output == output
    assert result.usage.cost_usd == Decimal("0.00069")


def test_openrouter_endpoint_discovery_and_selection() -> None:
    transport = FakeTransport(
        HttpResponse(
            200,
            {
                "data": {
                    "endpoints": [
                        {
                            "provider_name": "Provider-A",
                            "name": "variant-a",
                            "context_length": 100_000,
                            "max_completion_tokens": 4_096,
                            "pricing": {"prompt": "0.000001", "completion": "0.000003"},
                            "supported_parameters": ["response_format", "max_tokens"],
                            "quantization": "fp16",
                            "supports_zdr": True,
                        },
                        {
                            "provider_name": "Provider-B",
                            "name": "variant-b",
                            "pricing": {"prompt": "0.000002", "completion": "0.000004"},
                            "supported_parameters": ["max_tokens"],
                        },
                    ]
                }
            },
        )
    )
    endpoints = discover_openrouter_endpoints(
        api_key="synthetic-secret",
        model_slug="author/model",
        transport=transport,
        network_enabled=True,
    )
    assert len(endpoints) == 2
    selected = select_openrouter_endpoint(endpoints)
    assert selected is not None
    assert selected.provider_slug == "Provider-A"
    assert "synthetic-secret" not in repr(transport.requests[0])


def test_openrouter_payload_pins_provider_and_disables_fallback() -> None:
    endpoint = OpenRouterEndpoint(
        provider_slug="Provider-A",
        provider_name="Provider-A",
        model_variant="variant-a",
        context_length=100_000,
        max_completion_tokens=4_096,
        prompt_price_per_token=Decimal("0.000001"),
        completion_price_per_token=Decimal("0.000003"),
        supported_parameters=("response_format",),
        quantization="fp16",
        data_policy={"supports_zdr": True},
    )
    manifest = _openrouter_adapter(endpoint, FakeTransport(HttpResponse(200, {}))).manifest
    request = _request(manifest)
    output = _action(request)
    transport = FakeTransport(
        HttpResponse(
            200,
            {
                "id": "gen_safe",
                "model": manifest.exact_snapshot,
                "provider": "Provider-A",
                "choices": [
                    {
                        "message": {"content": output},
                        "finish_reason": "stop",
                        "native_finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 50, "completion_tokens": 20, "cost": "0.00011"},
            },
        )
    )
    adapter = _openrouter_adapter(endpoint, transport)
    result = adapter.respond(request)
    payload = transport.requests[0].body
    assert payload is not None
    provider = payload["provider"]
    assert isinstance(provider, dict)
    assert provider["only"] == ["Provider-A"]
    assert provider["allow_fallbacks"] is False
    assert provider["require_parameters"] is True
    assert provider["data_collection"] == "deny"
    assert provider["zdr"] is True
    assert result.usage.cost_usd == Decimal("0.00011")
    assert result.error_class is None


def test_openrouter_404_after_endpoint_freeze_is_policy_ineligible() -> None:
    endpoint = OpenRouterEndpoint(
        provider_slug="Provider-A",
        provider_name="Provider-A",
        model_variant="variant-a",
        context_length=100_000,
        max_completion_tokens=4_096,
        prompt_price_per_token=Decimal("0.000001"),
        completion_price_per_token=Decimal("0.000003"),
        supported_parameters=("response_format",),
        quantization="fp16",
        data_policy={},
    )
    adapter = _openrouter_adapter(endpoint, FakeTransport(HttpResponse(404, {"error": {}})))
    assert adapter.respond(_request(adapter.manifest)).error_class == "policy-ineligible"


def _openrouter_adapter(
    endpoint: OpenRouterEndpoint, transport: FakeTransport
) -> OpenRouterAdapter:
    return OpenRouterAdapter(
        api_key="synthetic-secret",
        model_slug="author/model",
        route_id="openrouter_mistral_small_3_1",
        endpoint=endpoint,
        transport=transport,
        network_enabled=True,
        ledger=CostLedger(_authorization()),
    )


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (400, "schema-or-parameter"),
        (401, "authentication"),
        (402, "billing-or-account-access"),
        (403, "permission-or-policy"),
        (404, "exact-model-access"),
        (429, "rate-limit"),
        (529, "transient-provider"),
    ],
)
def test_normalized_provider_errors(status: int, expected: str) -> None:
    assert normalize_http_error("provider", status, {}) == expected


def test_route_pricing_uses_reported_token_counts() -> None:
    pricing = RoutePricing(Decimal("2.5"), Decimal("15"))
    assert pricing.calculate(100, 20) == Decimal("0.00055")
