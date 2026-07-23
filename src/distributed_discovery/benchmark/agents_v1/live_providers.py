"""Disabled-by-default live provider adapters for public Agents v1 calibration."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol

from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    ModelManifest,
    Usage,
)
from distributed_discovery.benchmark.agents_v1.live_inputs import CostLedger
from distributed_discovery.benchmark.agents_v1.models import VERSIONS

OPENAI_MODEL = "gpt-5.4-2026-03-05"
ANTHROPIC_MODEL = "claude-sonnet-4-6"
OPENROUTER_MISTRAL_MODEL = "mistralai/mistral-small-3.1-24b-instruct"
OPENROUTER_GEMINI_MODEL = "google/gemini-2.5-pro"

OPENAI_MANIFEST = ModelManifest(
    provider="openai_direct",
    model_id=OPENAI_MODEL,
    exact_snapshot=OPENAI_MODEL,
    adapter_version="openai-responses-v1",
    live_capable=True,
)
ANTHROPIC_MANIFEST = ModelManifest(
    provider="anthropic_direct",
    model_id=ANTHROPIC_MODEL,
    exact_snapshot=ANTHROPIC_MODEL,
    adapter_version="anthropic-messages-v1",
    live_capable=True,
)


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    body: Mapping[str, object] | None = None
    headers: Mapping[str, str] = field(default_factory=dict, repr=False)
    timeout_seconds: int = 120

    def __repr__(self) -> str:
        return (
            f"HttpRequest(method={self.method!r}, url={self.url!r}, "
            f"body={self.body!r}, headers=<redacted>, timeout_seconds={self.timeout_seconds})"
        )


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: Mapping[str, object]
    response_headers: Mapping[str, str] = field(default_factory=dict, repr=False)


class HttpTransport(Protocol):
    def send(self, request: HttpRequest) -> HttpResponse: ...


class UrllibTransport:
    """Small standard-library JSON transport with no request logging."""

    def send(self, request: HttpRequest) -> HttpResponse:
        encoded = (
            json.dumps(request.body, separators=(",", ":")).encode("utf-8")
            if request.body is not None
            else None
        )
        raw_request = urllib.request.Request(
            request.url,
            data=encoded,
            headers=dict(request.headers),
            method=request.method,
        )
        try:
            with urllib.request.urlopen(  # noqa: S310 - exact HTTPS URLs are registered below
                raw_request, timeout=request.timeout_seconds
            ) as response:
                status = response.status
                raw = response.read()
                headers = dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            status = exc.code
            raw = exc.read()
            headers = dict(exc.headers.items()) if exc.headers else {}
        except TimeoutError as exc:
            raise ProviderTransportError("timeout") from exc
        except urllib.error.URLError as exc:
            raise ProviderTransportError("transient-transport") from exc
        try:
            loaded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderTransportError("invalid-provider-json") from exc
        if not isinstance(loaded, Mapping):
            raise ProviderTransportError("invalid-provider-json")
        return HttpResponse(status=status, body=dict(loaded), response_headers=headers)


class ProviderTransportError(RuntimeError):
    """Redacted transport error whose message is a normalized class only."""


@dataclass(frozen=True)
class RoutePricing:
    input_per_million_usd: Decimal
    output_per_million_usd: Decimal

    def calculate(self, input_tokens: int, output_tokens: int) -> Decimal:
        return (
            self.input_per_million_usd * Decimal(input_tokens)
            + self.output_per_million_usd * Decimal(output_tokens)
        ) / Decimal(1_000_000)

    def maximum_call_cost(self, *, input_ceiling: int, output_ceiling: int) -> Decimal:
        return self.calculate(input_ceiling, output_ceiling)


@dataclass(frozen=True)
class OpenRouterEndpoint:
    provider_slug: str
    provider_name: str
    model_variant: str
    context_length: int | None
    max_completion_tokens: int | None
    prompt_price_per_token: Decimal
    completion_price_per_token: Decimal
    supported_parameters: tuple[str, ...]
    quantization: str | None
    data_policy: Mapping[str, object]

    @property
    def pricing(self) -> RoutePricing:
        return RoutePricing(
            self.prompt_price_per_token * Decimal(1_000_000),
            self.completion_price_per_token * Decimal(1_000_000),
        )

    def public_record(self) -> dict[str, object]:
        return {
            "provider_slug": self.provider_slug,
            "provider_name": self.provider_name,
            "model_variant": self.model_variant,
            "context_length": self.context_length,
            "max_completion_tokens": self.max_completion_tokens,
            "prompt_price_per_token": str(self.prompt_price_per_token),
            "completion_price_per_token": str(self.completion_price_per_token),
            "supported_parameters": list(self.supported_parameters),
            "quantization": self.quantization,
            "data_policy": dict(self.data_policy),
        }


class LiveAdapterBase:
    manifest: ModelManifest
    gateway_id: str
    route_id: str

    def __init__(
        self,
        *,
        api_key: str,
        transport: HttpTransport | None,
        network_enabled: bool,
        ledger: CostLedger,
        pricing: RoutePricing,
        input_token_ceiling: int = 4_000,
    ) -> None:
        self._api_key = api_key
        self._transport = transport
        self._network_enabled = network_enabled
        self._ledger = ledger
        self._pricing = pricing
        self._input_token_ceiling = input_token_ceiling

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(manifest={self.manifest!r}, api_key=<redacted>, "
            f"network_enabled={self._network_enabled!r})"
        )

    def clear_secret(self) -> None:
        self._api_key = ""

    def _guard(self, request: AdapterRequest) -> None:
        if not self._network_enabled:
            raise PermissionError("live provider network access is disabled by default")
        if self._transport is None:
            raise PermissionError("an injected live HTTP transport is required")
        if request.manifest.exact_snapshot != self.manifest.exact_snapshot:
            raise PermissionError("adapter request model does not match the frozen snapshot")
        if request.max_output_tokens > 256:
            raise PermissionError("live output ceiling exceeds the registered maximum")
        self._ledger.authorize_next_call(
            gateway_id=self.gateway_id,
            route_id=self.route_id,
            maximum_call_cost_usd=self._pricing.maximum_call_cost(
                input_ceiling=self._input_token_ceiling,
                output_ceiling=request.max_output_tokens,
            ),
        )

    def _send(self, request: HttpRequest) -> HttpResponse:
        assert self._transport is not None
        return self._transport.send(request)

    def _finish(
        self,
        *,
        raw_output: str,
        input_tokens: int,
        output_tokens: int,
        error_class: str | None,
        operational_metadata: Mapping[str, object],
        provider_cost_usd: Decimal | None = None,
    ) -> AdapterResponse:
        calculated = self._pricing.calculate(input_tokens, output_tokens)
        actual = provider_cost_usd if provider_cost_usd is not None else calculated
        self._ledger.record_call(route_id=self.route_id, actual_cost_usd=actual)
        return AdapterResponse(
            raw_output=raw_output,
            usage=Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=actual,
            ),
            error_class=error_class,
            operational_metadata={
                **operational_metadata,
                "calculated_cost_usd": str(calculated),
                "provider_reported_cost_usd": (
                    str(provider_cost_usd) if provider_cost_usd is not None else None
                ),
                "hidden_reasoning_stored": False,
            },
        )


def action_schema(request: AdapterRequest) -> dict[str, object]:
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
            "visible_message": {"type": "string"},
            "source_choice": {
                "type": "string",
                "enum": list(request.source_vocabulary),
            },
            "actions": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(request.action_vocabulary),
                },
            },
            "declared_metadata": {
                "type": "object",
                "additionalProperties": False,
                "properties": {},
            },
        },
    }


def _instructions(request: AdapterRequest) -> str:
    repair = ""
    if request.schema_retry:
        repair = (
            " The previous response failed schema validation. Return only a corrected object; "
            "do not change the task semantics."
        )
    return request.prompt.system + repair


class OpenAIResponsesAdapter(LiveAdapterBase):
    manifest = OPENAI_MANIFEST
    gateway_id = "openai_direct"
    route_id = "openai_direct"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            pricing=RoutePricing(Decimal("2.50"), Decimal("15.00")),
            **kwargs,  # type: ignore[arg-type]
        )

    def build_payload(self, request: AdapterRequest) -> dict[str, object]:
        return {
            "model": self.manifest.exact_snapshot,
            "instructions": _instructions(request),
            "input": request.prompt.user,
            "max_output_tokens": request.max_output_tokens,
            "reasoning": {"effort": "none"},
            "store": False,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "discoverybench_agents_action",
                    "strict": True,
                    "schema": action_schema(request),
                }
            },
        }

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        self._guard(request)
        try:
            response = self._send(
                HttpRequest(
                    method="POST",
                    url="https://api.openai.com/v1/responses",
                    body=self.build_payload(request),
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout_seconds=request.timeout_seconds,
                )
            )
        except ProviderTransportError as exc:
            return AdapterResponse("", error_class=str(exc))
        error = normalize_http_error("openai", response.status, response.body)
        input_tokens, output_tokens = _openai_usage(response.body)
        output = _openai_output_text(response.body) if error is None else ""
        return self._finish(
            raw_output=output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error_class=error,
            operational_metadata={
                "gateway": self.gateway_id,
                "route_id": self.route_id,
                "model": _safe_exact(response.body.get("model"), self.manifest.exact_snapshot),
                "request_id": _safe_identifier(response.body.get("id")),
                "finish_status": _safe_status(response.body.get("status")),
                "reasoning_tokens_reported": _openai_reasoning_tokens(response.body),
                "cached_tokens_reported": _openai_cached_tokens(response.body),
            },
        )


class AnthropicMessagesAdapter(LiveAdapterBase):
    manifest = ANTHROPIC_MANIFEST
    gateway_id = "anthropic_direct"
    route_id = "anthropic_direct"

    def __init__(self, **kwargs: object) -> None:
        super().__init__(
            pricing=RoutePricing(Decimal("3.00"), Decimal("15.00")),
            **kwargs,  # type: ignore[arg-type]
        )

    def build_payload(self, request: AdapterRequest) -> dict[str, object]:
        return {
            "model": self.manifest.exact_snapshot,
            "system": _instructions(request),
            "messages": [{"role": "user", "content": request.prompt.user}],
            "max_tokens": request.max_output_tokens,
            "temperature": 0,
            "output_config": {
                "format": {
                    "type": "json_schema",
                    "schema": action_schema(request),
                }
            },
        }

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        self._guard(request)
        try:
            response = self._send(
                HttpRequest(
                    method="POST",
                    url="https://api.anthropic.com/v1/messages",
                    body=self.build_payload(request),
                    headers={
                        "x-api-key": self._api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    timeout_seconds=request.timeout_seconds,
                )
            )
        except ProviderTransportError as exc:
            return AdapterResponse("", error_class=str(exc))
        error = normalize_http_error("anthropic", response.status, response.body)
        input_tokens, output_tokens = _anthropic_usage(response.body)
        output = _anthropic_output_text(response.body) if error is None else ""
        return self._finish(
            raw_output=output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error_class=error,
            operational_metadata={
                "gateway": self.gateway_id,
                "route_id": self.route_id,
                "model": _safe_exact(response.body.get("model"), self.manifest.exact_snapshot),
                "request_id": _safe_identifier(response.body.get("id")),
                "finish_status": _safe_status(response.body.get("stop_reason")),
                "cache_read_input_tokens": _nested_int(
                    response.body, "usage", "cache_read_input_tokens"
                ),
                "cache_creation_input_tokens": _nested_int(
                    response.body, "usage", "cache_creation_input_tokens"
                ),
            },
        )


class OpenRouterAdapter(LiveAdapterBase):
    gateway_id = "openrouter"

    def __init__(
        self,
        *,
        model_slug: str,
        route_id: str,
        endpoint: OpenRouterEndpoint,
        **kwargs: object,
    ) -> None:
        self.route_id = route_id
        self.endpoint = endpoint
        self.manifest = ModelManifest(
            provider="openrouter",
            model_id=model_slug,
            exact_snapshot=model_slug,
            adapter_version="openrouter-chat-completions-v1",
            live_capable=True,
        )
        super().__init__(pricing=endpoint.pricing, **kwargs)  # type: ignore[arg-type]

    def build_payload(self, request: AdapterRequest) -> dict[str, object]:
        return {
            "model": self.manifest.exact_snapshot,
            "messages": [
                {"role": "system", "content": _instructions(request)},
                {"role": "user", "content": request.prompt.user},
            ],
            "max_tokens": request.max_output_tokens,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "discoverybench_agents_action",
                    "strict": True,
                    "schema": action_schema(request),
                },
            },
            "provider": {
                "only": [self.endpoint.provider_slug],
                "allow_fallbacks": False,
                "require_parameters": True,
                "data_collection": "deny",
                "zdr": True,
                "max_price": {
                    "prompt": str(self.endpoint.pricing.input_per_million_usd),
                    "completion": str(self.endpoint.pricing.output_per_million_usd),
                },
            },
            "usage": {"include": True},
        }

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        self._guard(request)
        try:
            response = self._send(
                HttpRequest(
                    method="POST",
                    url="https://openrouter.ai/api/v1/chat/completions",
                    body=self.build_payload(request),
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout_seconds=request.timeout_seconds,
                )
            )
        except ProviderTransportError as exc:
            return AdapterResponse("", error_class=str(exc))
        error = normalize_http_error("openrouter", response.status, response.body)
        if response.status == 404:
            error = "policy-ineligible"
        input_tokens, output_tokens = _openrouter_usage(response.body)
        output = _openrouter_output_text(response.body) if error is None else ""
        provider_cost = _optional_decimal(_mapping(response.body.get("usage")).get("cost"))
        returned_provider = _safe_identifier(
            response.body.get("provider") or _mapping(response.body.get("usage")).get("provider")
        )
        provider_matches = returned_provider is None or returned_provider.casefold() in {
            self.endpoint.provider_slug.casefold(),
            self.endpoint.provider_name.casefold(),
        }
        if error is None and not provider_matches:
            error = "returned-provider-mismatch"
        return self._finish(
            raw_output=output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error_class=error,
            provider_cost_usd=provider_cost,
            operational_metadata={
                "gateway": self.gateway_id,
                "route_id": self.route_id,
                "model": _safe_exact(response.body.get("model"), self.manifest.exact_snapshot),
                "generation_id": _safe_identifier(response.body.get("id")),
                "returned_upstream_provider": returned_provider,
                "returned_upstream_provider_matches": provider_matches,
                "finish_status": _openrouter_finish_reason(response.body),
                "native_finish_reason": _openrouter_native_finish_reason(response.body),
                "reasoning_tokens_reported": _nested_int(
                    response.body, "usage", "completion_tokens_details", "reasoning_tokens"
                ),
                "cached_tokens_reported": _nested_int(
                    response.body, "usage", "prompt_tokens_details", "cached_tokens"
                ),
                "fallbacks_disabled": True,
            },
        )


def discover_openrouter_endpoints(
    *,
    api_key: str,
    model_slug: str,
    transport: HttpTransport,
    network_enabled: bool,
) -> tuple[OpenRouterEndpoint, ...]:
    if not network_enabled:
        raise PermissionError("OpenRouter endpoint discovery requires explicit network enable")
    author, slug = model_slug.split("/", 1)
    response = transport.send(
        HttpRequest(
            method="GET",
            url=f"https://openrouter.ai/api/v1/models/{author}/{slug}/endpoints",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout_seconds=60,
        )
    )
    if response.status != 200:
        raise ProviderTransportError(
            normalize_http_error("openrouter", response.status, response.body)
            or "endpoint-discovery-failed"
        )
    data = response.body.get("data")
    raw_endpoints = data.get("endpoints") if isinstance(data, Mapping) else None
    if not isinstance(raw_endpoints, Sequence) or isinstance(raw_endpoints, (str, bytes)):
        raise ProviderTransportError("invalid-endpoint-discovery-response")
    endpoints: list[OpenRouterEndpoint] = []
    for item in raw_endpoints:
        if not isinstance(item, Mapping):
            continue
        pricing = _mapping(item.get("pricing"))
        prompt_price = _optional_decimal(pricing.get("prompt"))
        completion_price = _optional_decimal(pricing.get("completion"))
        provider_slug = str(
            item.get("provider_name") or item.get("provider_slug") or item.get("name") or ""
        ).strip()
        if not provider_slug or prompt_price is None or completion_price is None:
            continue
        parameters = item.get("supported_parameters")
        supported = (
            tuple(sorted(str(value) for value in parameters))
            if isinstance(parameters, Sequence) and not isinstance(parameters, (str, bytes))
            else ()
        )
        endpoints.append(
            OpenRouterEndpoint(
                provider_slug=provider_slug,
                provider_name=str(item.get("provider_name") or provider_slug),
                model_variant=str(item.get("name") or model_slug),
                context_length=_optional_int(item.get("context_length")),
                max_completion_tokens=_optional_int(item.get("max_completion_tokens")),
                prompt_price_per_token=prompt_price,
                completion_price_per_token=completion_price,
                supported_parameters=supported,
                quantization=(
                    str(item["quantization"]) if item.get("quantization") is not None else None
                ),
                data_policy={
                    key: item[key]
                    for key in (
                        "data_collection",
                        "zdr",
                        "supports_zdr",
                        "privacy_policy_url",
                    )
                    if key in item
                },
            )
        )
    return tuple(endpoints)


def select_openrouter_endpoint(
    endpoints: Sequence[OpenRouterEndpoint],
) -> OpenRouterEndpoint | None:
    eligible = [
        endpoint
        for endpoint in endpoints
        if "response_format" in endpoint.supported_parameters
        and endpoint.prompt_price_per_token >= 0
        and endpoint.completion_price_per_token >= 0
    ]
    if not eligible:
        return None
    return min(
        eligible,
        key=lambda endpoint: (
            endpoint.prompt_price_per_token + endpoint.completion_price_per_token,
            endpoint.provider_slug.casefold(),
            endpoint.model_variant,
        ),
    )


def normalize_http_error(provider: str, status: int, body: Mapping[str, object]) -> str | None:
    if 200 <= status < 300:
        return None
    if status == 401:
        return "authentication"
    if status == 402:
        return "billing-or-account-access"
    if status == 403:
        return "permission-or-policy"
    if status == 404:
        return "exact-model-access"
    if status == 408:
        return "timeout"
    if status == 409:
        return "conflict"
    if status in {400, 422}:
        return "schema-or-parameter"
    if status == 429:
        return "rate-limit"
    if status in {500, 502, 503, 504, 529}:
        return "transient-provider"
    error = body.get("error")
    if isinstance(error, Mapping):
        error_type = str(error.get("type") or error.get("code") or "").casefold()
        if "credit" in error_type or "billing" in error_type:
            return "billing-or-account-access"
        if "model" in error_type and ("not" in error_type or "access" in error_type):
            return "exact-model-access"
    return f"{provider}-http-{status}"


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _optional_decimal(value: object) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(str(value))
    except Exception:
        return None
    return result if result.is_finite() and result >= 0 else None


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        result = int(str(value))
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None


def _nested_int(body: Mapping[str, object], *keys: str) -> int:
    current: object = body
    for key in keys:
        if not isinstance(current, Mapping):
            return 0
        current = current.get(key)
    return _optional_int(current) or 0


def _safe_identifier(value: object) -> str | None:
    if not isinstance(value, str) or not value or len(value) > 240:
        return None
    if not all(character.isalnum() or character in "-_./: " for character in value):
        return None
    return value


def _safe_status(value: object) -> str | None:
    status = _safe_identifier(value)
    return status if status and len(status) <= 80 else None


def _safe_exact(value: object, expected: str) -> str | None:
    return expected if value == expected else _safe_identifier(value)


def _openai_usage(body: Mapping[str, object]) -> tuple[int, int]:
    return _nested_int(body, "usage", "input_tokens"), _nested_int(body, "usage", "output_tokens")


def _openai_reasoning_tokens(body: Mapping[str, object]) -> int:
    return _nested_int(body, "usage", "output_tokens_details", "reasoning_tokens")


def _openai_cached_tokens(body: Mapping[str, object]) -> int:
    return _nested_int(body, "usage", "input_tokens_details", "cached_tokens")


def _openai_output_text(body: Mapping[str, object]) -> str:
    output = body.get("output")
    if not isinstance(output, Sequence) or isinstance(output, (str, bytes)):
        return ""
    for item in output:
        if not isinstance(item, Mapping) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, Sequence) or isinstance(content, (str, bytes)):
            continue
        for part in content:
            if isinstance(part, Mapping) and part.get("type") == "output_text":
                text = part.get("text")
                if isinstance(text, str):
                    return text
    return ""


def _anthropic_usage(body: Mapping[str, object]) -> tuple[int, int]:
    return _nested_int(body, "usage", "input_tokens"), _nested_int(body, "usage", "output_tokens")


def _anthropic_output_text(body: Mapping[str, object]) -> str:
    content = body.get("content")
    if not isinstance(content, Sequence) or isinstance(content, (str, bytes)):
        return ""
    texts = [
        str(item["text"])
        for item in content
        if isinstance(item, Mapping)
        and item.get("type") == "text"
        and isinstance(item.get("text"), str)
    ]
    return "".join(texts)


def _openrouter_usage(body: Mapping[str, object]) -> tuple[int, int]:
    return _nested_int(body, "usage", "prompt_tokens"), _nested_int(
        body, "usage", "completion_tokens"
    )


def _openrouter_choice(body: Mapping[str, object]) -> Mapping[str, object]:
    choices = body.get("choices")
    if (
        isinstance(choices, Sequence)
        and not isinstance(choices, (str, bytes))
        and choices
        and isinstance(choices[0], Mapping)
    ):
        return choices[0]
    return {}


def _openrouter_output_text(body: Mapping[str, object]) -> str:
    content = _mapping(_openrouter_choice(body).get("message")).get("content")
    return content if isinstance(content, str) else ""


def _openrouter_finish_reason(body: Mapping[str, object]) -> str | None:
    return _safe_status(_openrouter_choice(body).get("finish_reason"))


def _openrouter_native_finish_reason(body: Mapping[str, object]) -> str | None:
    return _safe_status(_openrouter_choice(body).get("native_finish_reason"))
