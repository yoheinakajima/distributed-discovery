from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from distributed_discovery.benchmark.agents_v1 import fresh_pilot_v5
from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    MockAdapter,
    Usage,
)
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v5_runner import (
    OperationalCircuitBreakerError,
    ProtocolValidityPilotRunner,
    ProviderOperationalMissingError,
    _CaptureProviderOutcome,
)
from distributed_discovery.benchmark.agents_v1.orchestration import ARCHITECTURES
from distributed_discovery.benchmark.agents_v1.pilot import AppendOnlyLedger
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.provider_outcome import (
    CONTRACT_SAFETY_CLASSES,
    PROTOCOL_INVALID,
    PROTOCOL_VALID,
    PROVIDER_CONTRACT_OR_SAFETY_FAILURE,
    PROVIDER_OPERATIONAL_MISSING,
    BatchAcceptanceInputsV3,
    MetricIntervalV3,
    OperationalCircuitBreaker,
    PairingClassificationV3,
    architecture_contrast_bounds_v3,
    assess_batch_v3,
    classify_pairing_v3,
    classify_provider_error,
    metric_intervals_v3,
    selection_conditioned_diagnostic_v3,
    validate_terminal_classifications_v3,
)
from distributed_discovery.benchmark.agents_v1.provider_outcome_independent import (
    require_provider_outcome_agreement,
)

ROOT = Path(__file__).resolve().parents[1]


def _completed(
    pairing_id: str,
    *,
    provider: str = "OpenAI",
    status: str = PROTOCOL_VALID,
) -> PairingClassificationV3:
    errors = () if status == PROTOCOL_VALID else ("missing-final-action",)
    return PairingClassificationV3(
        pairing_id=pairing_id,
        provider=provider,
        model=("gpt-5.4-2026-03-05" if provider == "OpenAI" else "claude-sonnet-4-6"),
        task_commitment=f"task-{pairing_id}",
        architecture_id="isolated-private-agents",
        trace_id=f"trace-{pairing_id}",
        status=status,  # type: ignore[arg-type]
        provider_response_completed=True,
        protocol_compliance="pass" if status == PROTOCOL_VALID else "fail",
        method_c_errors=errors,
    )


def _missing(
    pairing_id: str,
    *,
    provider: str = "OpenAI",
    taxonomy_class: str | None = None,
) -> PairingClassificationV3:
    if taxonomy_class is None:
        taxonomy_class = (
            "openai-client-timeout" if provider == "OpenAI" else "anthropic-client-timeout"
        )
    return PairingClassificationV3(
        pairing_id=pairing_id,
        provider=provider,
        model=("gpt-5.4-2026-03-05" if provider == "OpenAI" else "claude-sonnet-4-6"),
        task_commitment=f"task-{pairing_id}",
        architecture_id="isolated-private-agents",
        trace_id=f"trace-{pairing_id}",
        status=PROVIDER_OPERATIONAL_MISSING,
        provider_response_completed=False,
        protocol_compliance="not-applicable",
        method_c_errors=(),
        provider_error_class=taxonomy_class,
    )


@pytest.mark.parametrize(
    ("provider", "error_class", "metadata", "expected"),
    [
        ("OpenAI", "timeout", {}, "openai-client-timeout"),
        ("OpenAI", "transient-transport", {}, "openai-transient-transport"),
        (
            "OpenAI",
            "rate-limit",
            {"http_status": 429, "provider_error_code": "rate_limit_exceeded"},
            "openai-rate-limit-reached",
        ),
        (
            "OpenAI",
            "transient-provider",
            {"http_status": 500, "provider_error_type": "server_error"},
            "openai-server-error",
        ),
        (
            "OpenAI",
            "transient-provider",
            {"http_status": 503, "provider_error_type": "overloaded_error"},
            "openai-overloaded",
        ),
        (
            "OpenAI",
            "invalid-provider-json",
            {},
            "openai-invalid-provider-envelope-exhausted",
        ),
        ("Anthropic", "timeout", {}, "anthropic-client-timeout"),
        (
            "Anthropic",
            "transient-transport",
            {},
            "anthropic-transient-transport",
        ),
        (
            "Anthropic",
            "rate-limit",
            {"http_status": 429, "provider_error_type": "rate_limit_error"},
            "anthropic-rate-limit-error",
        ),
        (
            "Anthropic",
            "transient-provider",
            {"http_status": 500, "provider_error_type": "api_error"},
            "anthropic-api-error",
        ),
        (
            "Anthropic",
            "transient-provider",
            {"http_status": 504, "provider_error_type": "timeout_error"},
            "anthropic-timeout-error",
        ),
        (
            "Anthropic",
            "transient-provider",
            {"http_status": 529, "provider_error_type": "overloaded_error"},
            "anthropic-overloaded-error",
        ),
        (
            "Anthropic",
            "invalid-provider-json",
            {},
            "anthropic-invalid-provider-envelope-exhausted",
        ),
    ],
)
def test_v3_registered_operational_taxonomy_is_exact_and_independently_reproduced(
    provider: str,
    error_class: str,
    metadata: dict[str, object],
    expected: str,
) -> None:
    primary = classify_provider_error(
        provider=provider,
        error_class=error_class,
        operational_metadata=metadata,
    )
    pairing = classify_pairing_v3(
        pairing_id="p",
        provider=provider,
        model=("gpt-5.4-2026-03-05" if provider == "OpenAI" else "claude-sonnet-4-6"),
        task_commitment="task",
        architecture_id="isolated-private-agents",
        trace_id="trace",
        provider_response_completed=False,
        provider_error=primary,
    )
    assert primary.disposition == PROVIDER_OPERATIONAL_MISSING
    assert primary.taxonomy_class == expected
    require_provider_outcome_agreement(
        (pairing.serializable(),),
        ({"pairing_id": "p", **primary.serializable()},),
    )


@pytest.mark.parametrize(
    ("error_class", "metadata", "retention_safe", "expected"),
    [
        ("schema-or-parameter", {}, True, "request-contract-rejection"),
        ("exact-model-mismatch", {}, True, "exact-model-mismatch"),
        (
            "timeout",
            {"route_id": "regional-fallback"},
            True,
            "route-provider-or-region-substitution",
        ),
        (
            "hidden-reasoning-boundary",
            {},
            True,
            "hidden-reasoning-boundary-failure",
        ),
        (
            "authentication",
            {},
            True,
            "credential-authorization-or-billing-boundary-failure",
        ),
        (
            "provider-contract-or-safety:retained-state-ledger-trace-or-response-identity-failure",
            {},
            True,
            "retained-state-ledger-trace-or-response-identity-failure",
        ),
        (
            "provider-contract-or-safety:execution-identity-mismatch",
            {},
            True,
            "execution-identity-mismatch",
        ),
        ("unrecognized", {}, True, "unregistered-error-class"),
        ("timeout", {}, False, "unsafe-provider-response-retention"),
        (
            "rate-limit",
            {"http_status": 429},
            True,
            "ambiguous-operational-versus-contract-status",
        ),
    ],
)
def test_v3_each_protected_contract_or_safety_class_quarantines(
    error_class: str,
    metadata: dict[str, object],
    retention_safe: bool,
    expected: str,
) -> None:
    result = classify_provider_error(
        provider="OpenAI",
        error_class=error_class,
        operational_metadata=metadata,
        response_retention_safe=retention_safe,
    )
    assert result.disposition == PROVIDER_CONTRACT_OR_SAFETY_FAILURE
    assert result.taxonomy_class == expected
    assert result.retry_eligible is False
    assert expected in CONTRACT_SAFETY_CLASSES


def test_v3_completed_refusal_and_nonconforming_output_are_protocol_invalid_not_missing() -> None:
    refusal = classify_pairing_v3(
        pairing_id="refusal",
        provider="OpenAI",
        model="gpt-5.4-2026-03-05",
        task_commitment="task",
        architecture_id="isolated-private-agents",
        trace_id="trace-refusal",
        provider_response_completed=True,
        method_c_errors=("completed-refusal",),
    )
    nonconforming = classify_pairing_v3(
        pairing_id="nonconforming",
        provider="Anthropic",
        model="claude-sonnet-4-6",
        task_commitment="task",
        architecture_id="isolated-private-agents",
        trace_id="trace-nonconforming",
        provider_response_completed=True,
        method_c_errors=("schema-invalid-after-one-repair",),
    )
    assert refusal.status == nonconforming.status == PROTOCOL_INVALID
    assert refusal.provider_response_completed is True
    assert nonconforming.provider_error_class is None


def test_v3_one_missing_and_mixed_invalid_missing_pairings_complete_engineering() -> None:
    classifications = (
        _completed("p0"),
        _completed("p1", status=PROTOCOL_INVALID),
        _missing("p2"),
    )
    breaker = OperationalCircuitBreaker()
    for sequence, item in enumerate(classifications):
        breaker.observe(item, sequence=sequence)
    disposition = assess_batch_v3(
        intended_pairing_ids=("p0", "p1", "p2"),
        classifications=classifications,
        circuit_breaker=breaker.snapshot(),
        acceptance=BatchAcceptanceInputsV3(),
    )
    assert disposition.decision == "engineering-complete"
    assert disposition.protocol_invalid == 1
    assert disposition.provider_operational_missing == 1
    assert disposition.quarantine_reasons == ()


def test_v3_exact_ten_cumulative_missing_fire_and_eleventh_is_impossible() -> None:
    breaker = OperationalCircuitBreaker()
    for sequence in range(10):
        missing = _missing(
            f"m{sequence}",
            provider="OpenAI" if sequence % 2 == 0 else "Anthropic",
        )
        snapshot = breaker.observe(missing, sequence=sequence)
        if sequence < 9:
            assert snapshot.fired is False
    assert snapshot.fired is True
    assert snapshot.reason == "ten-cumulative-provider-operational-missing"
    with pytest.raises(RuntimeError, match="already fired"):
        breaker.observe(_missing("m10"), sequence=10)


def test_v3_three_consecutive_same_provider_missing_fire() -> None:
    breaker = OperationalCircuitBreaker()
    breaker.observe(_missing("m0"), sequence=0)
    breaker.observe(_missing("m1"), sequence=1)
    snapshot = breaker.observe(_missing("m2"), sequence=2)
    assert snapshot.fired is True
    assert snapshot.reason == "three-consecutive-same-provider-operational-missing"


def test_v3_contract_failure_and_nonvalid_public_canary_fire_immediately() -> None:
    contract = replace(
        _missing("contract"),
        status=PROVIDER_CONTRACT_OR_SAFETY_FAILURE,
        provider_error_class="request-contract-rejection",
    )
    breaker = OperationalCircuitBreaker()
    assert breaker.observe(contract, sequence=0).fired is True
    canary_breaker = OperationalCircuitBreaker()
    snapshot = canary_breaker.observe(
        _completed("canary", status=PROTOCOL_INVALID),
        sequence=0,
        public_canary=True,
    )
    assert snapshot.reason == "public-canary-not-protocol-valid"


def test_v3_missing_metric_intervals_have_no_invented_action_or_invalid_credit() -> None:
    task = fresh_pilot_v5.generate_tasks(
        ROOT,
        material="FRESH-RC-V5-MISSING-BOUNDS-TEST",
        public_fixture=True,
    )[0]
    intervals = metric_intervals_v3(
        task=task,
        classification=_missing("missing"),
        exact_metrics={
            "calls": 2,
            "input_tokens": 17,
            "output_tokens": 0,
            "cost_usd": Decimal("0.002"),
            "retry_count": 1,
        },
    )
    indexed = {item.metric_id: item for item in intervals}
    assert indexed["invalid-action-rate"].lower == 0
    assert indexed["invalid-action-rate"].upper == 1
    assert indexed["invalid-action-rate"].operational_credit == "not-an-invalid-submitted-action"
    assert indexed["protocol-compliance"].exact_metric_defined is False
    assert indexed["calls"].lower == indexed["calls"].upper == 2
    assert indexed["retry-count"].lower == indexed["retry-count"].upper == 1
    assert indexed["provider-response-completion"].lower == 0
    assert indexed["provider-missingness"].lower == 1
    assert all("invented-action" not in item.operational_credit for item in intervals)


def test_v3_architecture_bounds_keep_every_intended_pairing_in_denominator() -> None:
    values = (
        MetricIntervalV3(
            pairing_id="p0-left",
            provider="OpenAI",
            model="gpt-5.4-2026-03-05",
            task_commitment="t0",
            architecture_id="isolated-private-agents",
            metric_id="group-discovery",
            status=PROTOCOL_VALID,
            lower=1,
            upper=1,
            operational_credit="exact:1",
            exact_metric_defined=True,
        ),
        MetricIntervalV3(
            pairing_id="p0-right",
            provider="OpenAI",
            model="gpt-5.4-2026-03-05",
            task_commitment="t0",
            architecture_id="full-broadcast-shared-transcript",
            metric_id="group-discovery",
            status=PROTOCOL_VALID,
            lower=0,
            upper=0,
            operational_credit="exact:0",
            exact_metric_defined=True,
        ),
        MetricIntervalV3(
            pairing_id="p1-left",
            provider="OpenAI",
            model="gpt-5.4-2026-03-05",
            task_commitment="t1",
            architecture_id="isolated-private-agents",
            metric_id="group-discovery",
            status=PROVIDER_OPERATIONAL_MISSING,
            lower=0,
            upper=1,
            operational_credit="0-no-valid-action",
            exact_metric_defined=False,
        ),
        MetricIntervalV3(
            pairing_id="p1-right",
            provider="OpenAI",
            model="gpt-5.4-2026-03-05",
            task_commitment="t1",
            architecture_id="full-broadcast-shared-transcript",
            metric_id="group-discovery",
            status=PROTOCOL_INVALID,
            lower=0,
            upper=1,
            operational_credit="none-no-valid-action",
            exact_metric_defined=False,
        ),
    )
    bounds = architecture_contrast_bounds_v3(
        values,
        contrasts=(
            (
                "isolated-private-agents",
                "full-broadcast-shared-transcript",
            ),
        ),
    )
    assert len(bounds) == 1
    assert bounds[0].intended_eligible_pairs == 2
    assert bounds[0].lower == 0
    assert bounds[0].upper == 1


def test_v3_complete_case_overclaim_and_terminal_inventory_corruptions_reject() -> None:
    diagnostic = selection_conditioned_diagnostic_v3([1, 0])
    assert diagnostic["unconditional_architecture_effect"] is False
    with pytest.raises(ValueError, match="cannot be labeled unconditional"):
        selection_conditioned_diagnostic_v3(
            [1, 0],
            label="unconditional-architecture-effect",
        )
    with pytest.raises(ValueError, match="duplicate"):
        validate_terminal_classifications_v3(
            ("p0", "p1"),
            (_completed("p0"), _completed("p0")),
        )
    with pytest.raises(ValueError, match="disagrees"):
        require_provider_outcome_agreement(
            (_missing("p0").serializable(),),
            (
                {
                    "pairing_id": "p0",
                    "provider": "OpenAI",
                    "source_error_class": "transient-transport",
                    "http_status": None,
                    "provider_error_type": None,
                    "provider_error_code": None,
                },
            ),
        )


class _FailOnePairingAdapter:
    def __init__(self, target_architecture: str) -> None:
        self.delegate = MockAdapter()
        self.manifest = self.delegate.manifest
        self.target_architecture = target_architecture
        self.failed = False

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        payload = json.loads(request.prompt.user)
        if payload["architecture_id"] == self.target_architecture and not self.failed:
            self.failed = True
            return AdapterResponse(
                "",
                Usage(input_tokens=8),
                error_class="timeout",
                operational_metadata={},
            )
        return self.delegate.respond(request)


@pytest.mark.parametrize("pairing_position", ["first", "middle", "final"])
def test_v3_missing_first_middle_final_intended_pairing_continues(
    tmp_path: Path,
    pairing_position: str,
) -> None:
    task = fresh_pilot_v5.generate_tasks(
        ROOT,
        material=f"FRESH-RC-V5-{pairing_position}-PAIRING",
        public_fixture=True,
    )[0]
    adapters: dict[str, object] = {model: MockAdapter() for model in fresh_pilot_v5.MODELS}
    target_model_index, target_architecture = {
        "first": (0, ARCHITECTURES[0]),
        "middle": (1, ARCHITECTURES[0]),
        "final": (1, ARCHITECTURES[-1]),
    }[pairing_position]
    adapters[fresh_pilot_v5.MODELS[target_model_index]] = _FailOnePairingAdapter(
        target_architecture
    )
    runner = ProtocolValidityPilotRunner(
        state_root=tmp_path,
        ledger=AppendOnlyLedger(tmp_path / "ledger.jsonl"),
        trace_key=b"k" * 32,
        campaign_id=fresh_pilot_v5.CAMPAIGN_ID,
        batch_id=fresh_pilot_v5.BATCH_ID,
        models=fresh_pilot_v5.MODELS,
        providers=fresh_pilot_v5.PROVIDERS,
    )
    result = runner.run_stage(
        stage="private-prefix",
        tasks=(task,),
        adapters=adapters,  # type: ignore[arg-type]
        verify_metrics=False,
        analyze=False,
        persist_traces=True,
        persist_analysis=False,
    )
    assert result["runs"] == 10
    assert result["provider_operational_missing"] == 1
    assert result["provider_contract_or_safety_failure"] == 0
    assert result["circuit_breaker"]["fired"] is False  # type: ignore[index]
    assert len(tuple((tmp_path / "encrypted-traces").glob("*.sealed"))) == 10
    assert len(tuple((tmp_path / "encrypted-provider-outcomes").glob("*.sealed"))) == 10


class _ThreeCallAdapter:
    def __init__(self, fail_index: int) -> None:
        self.manifest = MockAdapter().manifest
        self.fail_index = fail_index
        self.calls = 0

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        index = self.calls
        self.calls += 1
        if index == self.fail_index:
            return AdapterResponse("", error_class="timeout")
        return AdapterResponse("{}", Usage(input_tokens=1, output_tokens=1))


@pytest.mark.parametrize(
    ("logical_position", "fail_index"),
    [("first", 0), ("middle", 1), ("final", 2)],
)
def test_v3_missing_first_middle_final_logical_request_preserves_prior_calls(
    logical_position: str,
    fail_index: int,
) -> None:
    task = fresh_pilot_v5.generate_tasks(
        ROOT,
        material=f"FRESH-RC-V5-{logical_position}-LOGICAL-REQUEST",
        public_fixture=True,
    )[0]
    agent_id = sorted(task.capabilities)[0]
    prompt = compile_prompt(
        task,
        agent_id,
        architecture_id="isolated-private-agents",
        final_required=True,
    )
    request = AdapterRequest(
        prompt=prompt,
        manifest=MockAdapter().manifest,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        final_required=True,
    )
    guarded = _CaptureProviderOutcome(
        _ThreeCallAdapter(fail_index),
        provider="OpenAI",
        model="gpt-5.4-2026-03-05",
    )
    for index in range(fail_index):
        guarded.respond(replace(request, round_number=index))
    with pytest.raises(ProviderOperationalMissingError) as caught:
        guarded.respond(replace(request, round_number=fail_index))
    assert len(caught.value.completed_calls) == fail_index
    assert all(
        record["provider_response_completed"] is True for record in caught.value.completed_calls
    )


def test_v3_runner_stops_after_three_same_provider_missing_pairings(
    tmp_path: Path,
) -> None:
    task = fresh_pilot_v5.generate_tasks(
        ROOT,
        material="FRESH-RC-V5-CIRCUIT-RUNNER",
        public_fixture=True,
    )[0]
    runner = ProtocolValidityPilotRunner(
        state_root=tmp_path,
        ledger=AppendOnlyLedger(tmp_path / "ledger.jsonl"),
        trace_key=b"k" * 32,
        campaign_id=fresh_pilot_v5.CAMPAIGN_ID,
        batch_id=fresh_pilot_v5.BATCH_ID,
        models=fresh_pilot_v5.MODELS,
        providers=fresh_pilot_v5.PROVIDERS,
    )
    with pytest.raises(
        OperationalCircuitBreakerError,
        match="three-consecutive-same-provider",
    ):
        runner.run_stage(
            stage="private-prefix",
            tasks=(task,),
            adapters={model: MockAdapter("timeout") for model in fresh_pilot_v5.MODELS},
            verify_metrics=False,
            analyze=False,
            persist_traces=True,
            persist_analysis=False,
        )
    assert len(tuple((tmp_path / "encrypted-provider-outcomes").glob("*.sealed"))) == 3
