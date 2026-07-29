from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    ModelManifest,
    Usage,
)
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CostLedger,
    PreflightAuthorization,
)
from distributed_discovery.benchmark.agents_v1.live_providers import (
    OPENAI_MANIFEST,
    HttpRequest,
    HttpResponse,
    OpenAIResponsesAdapter,
)
from distributed_discovery.benchmark.agents_v1.pilot import (
    AppendOnlyLedger,
    ResumablePilotAdapter,
)
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.provider_outcome import (
    ProspectiveProviderOutcomeAdapter,
)
from distributed_discovery.benchmark.agents_v1.retry_backoff import (
    DeterministicNoWaitSleeper,
    RetryDelayRuntime,
    parse_retry_after,
    select_retry_delay,
)

MODEL = "gpt-5.4-2026-03-05"


class SequenceAdapter:
    def __init__(self, responses: Sequence[AdapterResponse]) -> None:
        self.responses = list(responses)
        self.calls = 0
        self.manifest = ModelManifest(
            provider="openai_direct",
            model_id=MODEL,
            exact_snapshot=MODEL,
            adapter_version="retry-delay-test-v1",
            moving_alias=False,
            live_capable=False,
        )

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        del request
        if self.calls >= len(self.responses):
            raise AssertionError("unexpected transport call")
        response = self.responses[self.calls]
        self.calls += 1
        return response


class SequenceTransport:
    def __init__(self, responses: Sequence[HttpResponse]) -> None:
        self.responses = list(responses)
        self.requests: list[HttpRequest] = []

    def send(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        if len(self.requests) > len(self.responses):
            raise AssertionError("unexpected direct provider transport call")
        return self.responses[len(self.requests) - 1]


class CrashSleeper:
    def __init__(self) -> None:
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)
        raise RuntimeError("synthetic restart boundary")


def _request(manifest: ModelManifest) -> AdapterRequest:
    task = generate_public_calibration()[0]
    agent_id = sorted(task.capabilities)[0]
    return AdapterRequest(
        prompt=compile_prompt(
            task,
            agent_id,
            architecture_id="isolated-private-agents",
            final_required=True,
        ),
        manifest=manifest,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        final_required=True,
    )


def _error(
    error_class: str = "timeout",
    *,
    metadata: Mapping[str, object] | None = None,
    input_tokens: int = 10,
    output_tokens: int = 2,
    cost_usd: str = "0.10",
) -> AdapterResponse:
    return AdapterResponse(
        raw_output="",
        usage=Usage(input_tokens, output_tokens, Decimal(cost_usd)),
        error_class=error_class,
        operational_metadata=dict(metadata or {}),
    )


def _success(
    *,
    input_tokens: int = 11,
    output_tokens: int = 3,
    cost_usd: str = "0.20",
) -> AdapterResponse:
    return AdapterResponse(
        raw_output="{}",
        usage=Usage(input_tokens, output_tokens, Decimal(cost_usd)),
        operational_metadata={"hidden_reasoning_stored": False},
    )


def _resumable(
    tmp_path: Path,
    ledger: AppendOnlyLedger,
    responses: Sequence[AdapterResponse],
    *,
    sleeper: Callable[[float], None],
    preflight: Callable[[], None] = lambda: None,
) -> tuple[ResumablePilotAdapter, SequenceAdapter]:
    underlying = SequenceAdapter(responses)
    adapter = ResumablePilotAdapter(
        ProspectiveProviderOutcomeAdapter(underlying, provider="OpenAI"),
        provider="OpenAI",
        model=MODEL,
        ledger=ledger,
        response_root=tmp_path / "responses",
        response_key=b"r" * 32,
        retry_delay_runtime=RetryDelayRuntime(
            sleeper=sleeper,
            preflight=preflight,
        ),
    )
    return adapter, underlying


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0", 1),
        ("7", 7),
        ("90", 30),
    ],
)
def test_retry_after_is_clamped_to_the_committed_bounds(raw: str, expected: int) -> None:
    decision = select_retry_delay("rate-limit", retry_after=raw)
    assert decision.retry_delay_seconds == expected
    assert decision.retry_delay_source == "provider-retry-after"
    assert decision.retry_class == "rate-limit"


@pytest.mark.parametrize("raw", ["not-a-delay", "", "NaN", "-1", object()])
def test_malformed_retry_after_uses_the_registered_fallback(raw: object) -> None:
    decision = select_retry_delay("rate-limit", retry_after=raw)
    assert decision.retry_delay_seconds == 5
    assert decision.retry_delay_source == "registered-class-fallback"


def test_missing_retry_after_uses_the_registered_fallback() -> None:
    decision = select_retry_delay("timeout")
    assert decision.retry_delay_seconds == 2
    assert decision.retry_delay_source == "registered-class-fallback"


@pytest.mark.parametrize(
    ("retry_class", "expected"),
    [
        ("timeout", 2),
        ("transient-transport", 2),
        ("invalid-provider-json", 2),
        ("rate-limit", 5),
        ("transient-provider", 5),
    ],
)
def test_every_registered_fallback_class_is_frozen(retry_class: str, expected: int) -> None:
    assert select_retry_delay(retry_class).retry_delay_seconds == expected


def test_retry_after_http_date_uses_the_injected_clock() -> None:
    now = datetime(2026, 7, 29, 20, 0, 0, tzinfo=UTC)
    assert (
        parse_retry_after(
            "Wed, 29 Jul 2026 20:00:09 GMT",
            clock=lambda: now,
        )
        == 9
    )


def test_delay_audit_is_append_only_and_does_not_change_accounting(
    tmp_path: Path,
) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    sleeper = DeterministicNoWaitSleeper()
    adapter, underlying = _resumable(
        tmp_path,
        ledger,
        (_error(), _success()),
        sleeper=sleeper,
    )
    request = _request(adapter.manifest)

    first = adapter.respond(request)
    replay = adapter.respond(request)

    assert first == replay
    assert underlying.calls == 2
    assert sleeper.delays == [2.0]
    assert [record["event_type"] for record in ledger.records] == [
        "provider-call",
        "provider-retry-delay-selected",
        "provider-retry-delay-completed",
        "provider-call",
    ]
    assert [record["transport_attempt"] for record in ledger.records] == [0, 1, 1, 1]
    assert ledger.records[0]["provider_outcome_disposition"] == ("provider-operational-missing")
    assert ledger.records[1]["first_failed_attempt_identity"].endswith("/attempt-0")
    assert ledger.records[1]["retry_delay_seconds"] == 2
    assert ledger.records[1]["retry_delay_source"] == "registered-class-fallback"
    assert ledger.records[2]["status"] == "completed"
    assert ledger.totals() == {
        "calls": 2,
        "input_tokens": 21,
        "output_tokens": 5,
        "cost_usd": Decimal("0.30"),
        "provider_usd": {
            "OpenAI": Decimal("0.30"),
            "Anthropic": Decimal("0"),
        },
    }
    provider_calls = [
        record for record in ledger.records if record["event_type"] == "provider-call"
    ]
    assert sum(int(str(record["transport_attempt"])) > 0 for record in provider_calls) == 1


def test_restart_replays_selected_delay_without_bypassing_it(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)
    crashing = CrashSleeper()
    adapter, first_underlying = _resumable(
        tmp_path,
        ledger,
        (_error(),),
        sleeper=crashing,
    )
    request = _request(adapter.manifest)
    with pytest.raises(RuntimeError, match="restart boundary"):
        adapter.respond(request)
    assert first_underlying.calls == 1
    assert crashing.delays == [2.0]
    assert [record["event_type"] for record in ledger.records] == [
        "provider-call",
        "provider-retry-delay-selected",
    ]

    resumed_ledger = AppendOnlyLedger(ledger_path)
    recorder = DeterministicNoWaitSleeper()
    resumed, second_underlying = _resumable(
        tmp_path,
        resumed_ledger,
        (_success(),),
        sleeper=recorder,
    )
    response = resumed.respond(_request(resumed.manifest))
    assert response.error_class is None
    assert second_underlying.calls == 1
    assert recorder.delays == [2.0]
    assert [record["event_type"] for record in resumed_ledger.records][-2:] == [
        "provider-retry-delay-completed",
        "provider-call",
    ]


def test_changed_delay_after_restart_is_rejected(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    recorder = DeterministicNoWaitSleeper()
    adapter, underlying = _resumable(
        tmp_path,
        ledger,
        (_success(),),
        sleeper=recorder,
    )
    request = _request(adapter.manifest)
    call_key = adapter._key(request)
    ledger.append(
        {
            "event_type": "provider-call",
            "idempotency_key": f"{call_key}/attempt-0",
            "call_key": call_key,
            "transport_attempt": 0,
            "status": "error",
            "provider": "OpenAI",
            "model": MODEL,
            "error_class": "timeout",
            "provider_outcome_disposition": "provider-operational-missing",
            "retry_delay_seconds": 2,
            "retry_delay_source": "registered-class-fallback",
            "retry_class": "timeout",
        }
    )
    ledger.append(
        {
            "event_type": "provider-retry-delay-selected",
            "idempotency_key": f"{call_key}/retry-delay-selected",
            "call_key": call_key,
            "status": "selected",
            "first_failed_attempt_identity": f"{call_key}/attempt-0",
            "registered_provider_outcome_disposition": "provider-operational-missing",
            "transport_attempt": 1,
            "retry_delay_seconds": 5,
            "retry_delay_source": "provider-retry-after",
            "retry_class": "timeout",
        }
    )
    with pytest.raises(PermissionError, match="changed"):
        adapter.respond(request)
    assert underlying.calls == 0
    assert recorder.delays == []


def test_recorded_success_cannot_create_a_duplicate_retry(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    recorder = DeterministicNoWaitSleeper()
    adapter, underlying = _resumable(
        tmp_path,
        ledger,
        (_error(), _success()),
        sleeper=recorder,
    )
    request = _request(adapter.manifest)
    adapter.respond(request)
    call_key = adapter._key(request)
    ledger.append(
        {
            "event_type": "provider-retry-delay-selected",
            "idempotency_key": f"{call_key}/retry-delay-selected-duplicate",
            "call_key": call_key,
            "status": "selected",
            "first_failed_attempt_identity": f"{call_key}/attempt-0",
            "registered_provider_outcome_disposition": "provider-operational-missing",
            "transport_attempt": 1,
            "retry_delay_seconds": 2,
            "retry_delay_source": "registered-class-fallback",
            "retry_class": "timeout",
        }
    )
    with pytest.raises(PermissionError, match="duplicate"):
        adapter.respond(request)
    assert underlying.calls == 2


def test_provider_phase_closed_before_retry_prevents_wait_and_dispatch(
    tmp_path: Path,
) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = AppendOnlyLedger(ledger_path)
    adapter, underlying = _resumable(
        tmp_path,
        ledger,
        (_error(),),
        sleeper=CrashSleeper(),
    )
    request = _request(adapter.manifest)
    with pytest.raises(RuntimeError, match="restart boundary"):
        adapter.respond(request)
    assert underlying.calls == 1
    ledger.close_provider_phase()

    resumed_ledger = AppendOnlyLedger(ledger_path)
    recorder = DeterministicNoWaitSleeper()
    resumed, resumed_underlying = _resumable(
        tmp_path,
        resumed_ledger,
        (_success(),),
        sleeper=recorder,
    )
    with pytest.raises(PermissionError, match="provider phase is closed"):
        resumed.respond(_request(resumed.manifest))
    assert recorder.delays == []
    assert resumed_underlying.calls == 0


def test_cap_failure_precedes_wait_and_second_dispatch(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl", max_calls=1)
    recorder = DeterministicNoWaitSleeper()
    adapter, underlying = _resumable(
        tmp_path,
        ledger,
        (_error(), _success()),
        sleeper=recorder,
    )
    with pytest.raises(PermissionError, match="call cap"):
        adapter.respond(_request(adapter.manifest))
    assert underlying.calls == 1
    assert recorder.delays == []
    assert [record["event_type"] for record in ledger.records] == ["provider-call"]


def test_authorization_or_identity_preflight_precedes_wait(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    recorder = DeterministicNoWaitSleeper()

    def fail_preflight() -> None:
        raise PermissionError("synthetic authorization identity failure")

    adapter, underlying = _resumable(
        tmp_path,
        ledger,
        (_error(), _success()),
        sleeper=recorder,
        preflight=fail_preflight,
    )
    with pytest.raises(PermissionError, match="authorization identity"):
        adapter.respond(_request(adapter.manifest))
    assert underlying.calls == 1
    assert recorder.delays == []
    assert [record["event_type"] for record in ledger.records] == ["provider-call"]


def test_contract_or_safety_failure_never_waits_or_retries(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    recorder = DeterministicNoWaitSleeper()
    adapter, underlying = _resumable(
        tmp_path,
        ledger,
        (
            _error(
                "rate-limit",
                metadata={
                    "http_status": 429,
                    "provider_error_code": "insufficient_quota",
                    "retry_delay_seconds": 12,
                    "retry_delay_source": "provider-retry-after",
                    "retry_class": "rate-limit",
                },
            ),
        ),
        sleeper=recorder,
    )
    response = adapter.respond(_request(adapter.manifest))
    assert response.error_class == (
        "provider-contract-or-safety:credential-authorization-or-billing-boundary-failure"
    )
    assert underlying.calls == 1
    assert recorder.delays == []
    assert not {
        "retry_delay_seconds",
        "retry_delay_source",
        "retry_class",
    } & set(response.operational_metadata)
    assert [record["event_type"] for record in ledger.records] == ["provider-call"]


def test_attempted_third_transport_call_is_rejected_and_never_dispatched(
    tmp_path: Path,
) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    recorder = DeterministicNoWaitSleeper()
    adapter, underlying = _resumable(
        tmp_path,
        ledger,
        (_error(), _error()),
        sleeper=recorder,
    )
    request = _request(adapter.manifest)
    adapter.respond(request)
    call_key = adapter._key(request)
    ledger.append(
        {
            "event_type": "provider-call",
            "idempotency_key": f"{call_key}/attempt-2",
            "call_key": call_key,
            "transport_attempt": 2,
            "status": "error",
            "provider": "OpenAI",
            "model": MODEL,
            "error_class": "timeout",
        }
    )
    with pytest.raises(PermissionError, match="attempt sequence"):
        adapter.respond(request)
    assert underlying.calls == 2
    assert recorder.delays == [2.0]


def _authorization() -> PreflightAuthorization:
    return PreflightAuthorization(
        authorization_id="retry-delay-test",
        authorized_base_commit="a" * 40,
        allowed_branch="codex/treasurebench-agents-v1-fresh-pilot-v5",
        expires_utc=datetime.now(UTC) + timedelta(days=1),
        total_cap_usd=Decimal("25"),
        gateway_caps_usd={"openai_direct": Decimal("10")},
        route_caps_usd={"openai_direct": Decimal("10")},
        max_calls_per_route=10,
        max_total_calls=10,
        max_live_concurrency=1,
        private_tasks_allowed=False,
        scientific_evidence_allowed=False,
        raw={},
    )


def test_raw_headers_and_provider_messages_never_enter_retry_ledger_or_metadata(
    tmp_path: Path,
) -> None:
    request = _request(OPENAI_MANIFEST)
    transport = SequenceTransport(
        (
            HttpResponse(
                429,
                {
                    "error": {
                        "type": "rate_limit_error",
                        "code": "rate_limit_exceeded",
                        "message": "RAW-PROVIDER-MESSAGE-MUST-NOT-LEAK",
                    }
                },
                response_headers={
                    "Retry-After": "8",
                    "Authorization": "RAW-HEADER-SECRET",
                    "X-Unrestricted": "RAW-HEADER-VALUE",
                },
            ),
            HttpResponse(
                200,
                {
                    "id": "resp_safe",
                    "model": MODEL,
                    "status": "completed",
                    "output": [
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": "{}"}],
                        }
                    ],
                    "usage": {"input_tokens": 1, "output_tokens": 1},
                },
            ),
        )
    )
    live = OpenAIResponsesAdapter(
        api_key="SYNTHETIC-CREDENTIAL-MUST-NOT-LEAK",
        transport=transport,
        network_enabled=True,
        ledger=CostLedger(_authorization()),
    )
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    recorder = DeterministicNoWaitSleeper()
    adapter = ResumablePilotAdapter(
        ProspectiveProviderOutcomeAdapter(live, provider="OpenAI"),
        provider="OpenAI",
        model=MODEL,
        ledger=ledger,
        response_root=tmp_path / "responses",
        response_key=b"r" * 32,
        retry_delay_runtime=RetryDelayRuntime(sleeper=recorder),
    )
    response = adapter.respond(request)
    assert response.error_class is None
    assert recorder.delays == [8.0]
    assert ledger.records[0]["retry_delay_seconds"] == 8
    assert ledger.records[0]["retry_delay_source"] == "provider-retry-after"
    retained = json.dumps(
        {
            "ledger": ledger.records,
            "terminal_metadata": response.operational_metadata,
        }
    )
    for prohibited in (
        "RAW-PROVIDER-MESSAGE-MUST-NOT-LEAK",
        "RAW-HEADER-SECRET",
        "RAW-HEADER-VALUE",
        "SYNTHETIC-CREDENTIAL-MUST-NOT-LEAK",
        "Authorization",
        "X-Unrestricted",
    ):
        assert prohibited not in retained
