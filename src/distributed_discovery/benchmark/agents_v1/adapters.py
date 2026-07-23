"""Provider-neutral adapters. Every live-capable path is disabled by default."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol

from distributed_discovery.benchmark.agents_v1.models import VERSIONS
from distributed_discovery.benchmark.agents_v1.prompts import CompiledPrompt


@dataclass(frozen=True)
class ModelManifest:
    provider: str
    model_id: str
    exact_snapshot: str
    adapter_version: str
    moving_alias: bool = False
    live_capable: bool = False


@dataclass(frozen=True)
class AdapterRequest:
    prompt: CompiledPrompt
    manifest: ModelManifest
    round_number: int
    action_vocabulary: tuple[str, ...]
    source_vocabulary: tuple[str, ...]
    timeout_seconds: int = 120
    max_output_tokens: int = 256
    schema_retry: bool = False
    repair_errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: Decimal = Decimal("0")


@dataclass(frozen=True)
class AdapterResponse:
    raw_output: str
    usage: Usage = Usage()
    error_class: str | None = None
    declared_tool_calls: tuple[Mapping[str, object], ...] = ()
    operational_metadata: Mapping[str, object] = field(default_factory=dict)


class AgentAdapter(Protocol):
    manifest: ModelManifest

    def respond(self, request: AdapterRequest) -> AdapterResponse: ...


MOCK_MANIFEST = ModelManifest(
    provider="offline",
    model_id="deterministic-mock",
    exact_snapshot="deterministic-mock-v1",
    adapter_version="mock-adapter-v1",
)


class MockAdapter:
    """Deterministic, adversarial, malformed, timeout, and error mock modes."""

    def __init__(self, mode: str = "deterministic", script: tuple[str, ...] = ()) -> None:
        allowed = {"deterministic", "adversarial", "malformed", "timeout", "error", "scripted"}
        if mode not in allowed:
            raise ValueError(f"unknown mock mode: {mode}")
        self.mode = mode
        self.script = script
        self.calls = 0
        self.manifest = MOCK_MANIFEST

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        self.calls += 1
        if self.mode == "timeout":
            return AdapterResponse("", error_class="timeout")
        if self.mode == "error":
            return AdapterResponse("", error_class="adapter-error")
        if self.mode == "malformed" and not request.schema_retry:
            return AdapterResponse("{malformed")
        if self.mode == "scripted":
            output = self.script[min(self.calls - 1, len(self.script) - 1)] if self.script else "{}"
            return AdapterResponse(output)
        payload = json.loads(request.prompt.user)
        observation = str(payload["private_observation"])
        action = next(
            (
                candidate
                for candidate in request.action_vocabulary
                if candidate.removeprefix("TARGET-") in observation
            ),
            request.action_vocabulary[
                sum(ord(char) for char in request.prompt.agent_id)
                % len(request.action_vocabulary)
            ],
        )
        body: dict[str, object] = {
            "schema_version": VERSIONS["action"],
            "task_instance_commitment": f"sha256:{request.prompt.task_commitment}",
            "agent_id": request.prompt.agent_id,
            "round": request.round_number,
            "final": request.round_number >= 1,
            "visible_message": f"candidate:{action}",
            "source_choice": "none",
            "actions": [action],
            "declared_metadata": {"mock": True},
        }
        if self.mode == "adversarial":
            body["answer_key"] = "exfiltrate"
        return AdapterResponse(
            json.dumps(body, sort_keys=True),
            Usage(input_tokens=64, output_tokens=32),
            operational_metadata={"mock": True, "hidden_reasoning": False},
        )


Transport = Callable[[Mapping[str, object]], Mapping[str, object]]


class DisabledProviderAdapter:
    """Transport-injected provider scaffold with an unconditional default refusal."""

    def __init__(
        self,
        manifest: ModelManifest,
        *,
        transport: Transport | None = None,
        enabled: bool = False,
        authorization: Mapping[str, object] | None = None,
    ) -> None:
        self.manifest = manifest
        self._transport = transport
        self._enabled = enabled
        self._authorization = authorization

    def build_payload(self, request: AdapterRequest) -> Mapping[str, object]:
        if self.manifest.moving_alias or self.manifest.exact_snapshot != self.manifest.model_id:
            raise PermissionError("an immutable exact model snapshot is required")
        return {
            "model": self.manifest.exact_snapshot,
            "system": request.prompt.system,
            "input": request.prompt.user,
            "max_output_tokens": request.max_output_tokens,
            "structured_output_version": VERSIONS["action"],
        }

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        if not self._enabled:
            raise PermissionError("live provider adapters are disabled by default")
        if self._authorization is None:
            raise PermissionError("validated execution authorization is required")
        if self._transport is None:
            raise PermissionError("an injected transport is required")
        payload = self.build_payload(request)
        response = self._transport(payload)
        return AdapterResponse(
            raw_output=str(response.get("output", "")),
            error_class=(
                str(response["error_class"]) if response.get("error_class") is not None else None
            ),
        )


@dataclass(frozen=True)
class LocalOpenProcessContract:
    command: tuple[str, ...]
    model_artifact_sha256: str
    invocation_enabled: bool = False

    def execute(self) -> None:
        raise PermissionError("local model execution is outside the offline implementation scope")
