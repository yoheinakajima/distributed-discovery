"""Prospective TreasureBench Agents v1 provider-outcome policy v3.

This module is additive for AO-0011. It does not reinterpret any historical
campaign. It separates completed-response protocol validity from bounded
provider operational missingness and contract or safety failures.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from decimal import Decimal
from fractions import Fraction
from typing import Literal

from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    AgentAdapter,
)
from distributed_discovery.benchmark.agents_v1.models import TaskInstance
from distributed_discovery.benchmark.agents_v1.protocol_validity import (
    CONDITIONAL_DIAGNOSTIC_ROLE,
    FORBIDDEN_UNCONDITIONAL_LABELS,
    PRIMARY_CONTRASTS,
)
from distributed_discovery.benchmark.agents_v1.retry_backoff import (
    SAFE_RETRY_METADATA_FIELDS,
)

PairingStatusV3 = Literal[
    "protocol-valid",
    "protocol-invalid",
    "provider-operational-missing",
    "provider-contract-or-safety-failure",
]
ProviderErrorDisposition = Literal[
    "provider-operational-missing",
    "provider-contract-or-safety-failure",
]
ProtocolComplianceStatus = Literal["pass", "fail", "not-applicable"]

PROTOCOL_VALID: PairingStatusV3 = "protocol-valid"
PROTOCOL_INVALID: PairingStatusV3 = "protocol-invalid"
PROVIDER_OPERATIONAL_MISSING: PairingStatusV3 = "provider-operational-missing"
PROVIDER_CONTRACT_OR_SAFETY_FAILURE: PairingStatusV3 = "provider-contract-or-safety-failure"
PAIRING_STATUSES_V3 = frozenset(
    {
        PROTOCOL_VALID,
        PROTOCOL_INVALID,
        PROVIDER_OPERATIONAL_MISSING,
        PROVIDER_CONTRACT_OR_SAFETY_FAILURE,
    }
)

OPENAI_OPERATIONAL_CLASSES = frozenset(
    {
        "openai-client-timeout",
        "openai-transient-transport",
        "openai-rate-limit-reached",
        "openai-server-error",
        "openai-overloaded",
        "openai-invalid-provider-envelope-exhausted",
    }
)
ANTHROPIC_OPERATIONAL_CLASSES = frozenset(
    {
        "anthropic-client-timeout",
        "anthropic-transient-transport",
        "anthropic-rate-limit-error",
        "anthropic-api-error",
        "anthropic-timeout-error",
        "anthropic-overloaded-error",
        "anthropic-invalid-provider-envelope-exhausted",
    }
)
OPERATIONAL_CLASSES = OPENAI_OPERATIONAL_CLASSES | ANTHROPIC_OPERATIONAL_CLASSES
CONTRACT_SAFETY_CLASSES = frozenset(
    {
        "request-contract-rejection",
        "exact-model-mismatch",
        "route-provider-or-region-substitution",
        "hidden-reasoning-boundary-failure",
        "credential-authorization-or-billing-boundary-failure",
        "retained-state-ledger-trace-or-response-identity-failure",
        "execution-identity-mismatch",
        "unregistered-error-class",
        "unsafe-provider-response-retention",
        "ambiguous-operational-versus-contract-status",
    }
)
EXPECTED_ROUTES = {
    "OpenAI": ("openai_direct", "gpt-5.4-2026-03-05"),
    "Anthropic": ("anthropic_direct", "claude-sonnet-4-6"),
}

METRIC_IDS_V3 = (
    "group-discovery",
    "distinct-action-coverage",
    "duplication",
    "planner-regret",
    "private-baseline-regret",
    "recovery-budget-attainment",
    "source-diversity",
    "communication-induced-action-compression",
    "distance-from-best-registered-equilibrium",
    "distance-from-worst-registered-equilibrium",
    "invalid-action-rate",
    "protocol-compliance",
    "calls",
    "tokens",
    "cost",
    "retry-count",
    "provider-response-completion",
    "provider-missingness",
)
METRIC_FIELD_NAMES_V3 = {
    "group-discovery": "group_discovery",
    "distinct-action-coverage": "distinct_action_coverage",
    "duplication": "duplication",
    "planner-regret": "planner_regret",
    "private-baseline-regret": "private_baseline_regret",
    "recovery-budget-attainment": "recovery_budget_attainment",
    "source-diversity": "source_diversity",
    "communication-induced-action-compression": "communication_action_compression",
    "distance-from-best-registered-equilibrium": "best_equilibrium_distance",
    "distance-from-worst-registered-equilibrium": "worst_equilibrium_distance",
    "invalid-action-rate": "invalid_action_rate",
    "protocol-compliance": "protocol_compliance",
    "calls": "calls",
    "tokens": "tokens",
    "cost": "cost_usd",
    "retry-count": "retry_count",
    "provider-response-completion": "provider_response_completion",
    "provider-missingness": "provider_missingness",
}


@dataclass(frozen=True)
class ProviderErrorClassification:
    """Prospective classification of one terminal provider error envelope."""

    provider: str
    disposition: ProviderErrorDisposition
    taxonomy_class: str
    source_error_class: str
    http_status: int | None
    provider_error_type: str | None
    provider_error_code: str | None

    def __post_init__(self) -> None:
        if self.disposition == PROVIDER_OPERATIONAL_MISSING:
            if self.taxonomy_class not in OPERATIONAL_CLASSES:
                raise ValueError("operational disposition requires a registered class")
        elif self.taxonomy_class not in CONTRACT_SAFETY_CLASSES:
            raise ValueError("contract/safety disposition requires a registered class")

    @property
    def retry_eligible(self) -> bool:
        return self.disposition == PROVIDER_OPERATIONAL_MISSING

    def serializable(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "disposition": self.disposition,
            "taxonomy_class": self.taxonomy_class,
            "source_error_class": self.source_error_class,
            "http_status": self.http_status,
            "provider_error_type": self.provider_error_type,
            "provider_error_code": self.provider_error_code,
        }


def _optional_status(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().casefold()
    return normalized or None


def _contract(
    provider: str,
    error_class: str,
    taxonomy_class: str,
    metadata: Mapping[str, object],
) -> ProviderErrorClassification:
    return ProviderErrorClassification(
        provider=provider,
        disposition="provider-contract-or-safety-failure",
        taxonomy_class=taxonomy_class,
        source_error_class=error_class,
        http_status=_optional_status(metadata.get("http_status")),
        provider_error_type=_optional_text(metadata.get("provider_error_type")),
        provider_error_code=_optional_text(metadata.get("provider_error_code")),
    )


def _operational(
    provider: str,
    error_class: str,
    taxonomy_class: str,
    metadata: Mapping[str, object],
) -> ProviderErrorClassification:
    return ProviderErrorClassification(
        provider=provider,
        disposition="provider-operational-missing",
        taxonomy_class=taxonomy_class,
        source_error_class=error_class,
        http_status=_optional_status(metadata.get("http_status")),
        provider_error_type=_optional_text(metadata.get("provider_error_type")),
        provider_error_code=_optional_text(metadata.get("provider_error_code")),
    )


def classify_provider_error(
    *,
    provider: str,
    error_class: str,
    operational_metadata: Mapping[str, object],
    response_retention_safe: bool = True,
) -> ProviderErrorClassification:
    """Classify only the complete prospectively registered provider taxonomy."""

    if provider not in EXPECTED_ROUTES:
        return _contract(
            provider,
            error_class,
            "route-provider-or-region-substitution",
            operational_metadata,
        )
    if not response_retention_safe:
        return _contract(
            provider,
            error_class,
            "unsafe-provider-response-retention",
            operational_metadata,
        )
    expected_route, expected_model = EXPECTED_ROUTES[provider]
    route = operational_metadata.get("route_id")
    gateway = operational_metadata.get("gateway")
    model = operational_metadata.get("model")
    if route not in {None, expected_route} or gateway not in {None, expected_route}:
        return _contract(
            provider,
            error_class,
            "route-provider-or-region-substitution",
            operational_metadata,
        )
    if model not in {None, expected_model} or error_class == "exact-model-mismatch":
        return _contract(
            provider,
            error_class,
            "exact-model-mismatch",
            operational_metadata,
        )
    if error_class == "hidden-reasoning-boundary":
        return _contract(
            provider,
            error_class,
            "hidden-reasoning-boundary-failure",
            operational_metadata,
        )
    if error_class in {
        "authentication",
        "billing-or-account-access",
        "permission-or-policy",
    }:
        return _contract(
            provider,
            error_class,
            "credential-authorization-or-billing-boundary-failure",
            operational_metadata,
        )
    if error_class in {
        "schema-or-parameter",
        "exact-model-access",
        "conflict",
        "request-too-large",
    }:
        return _contract(
            provider,
            error_class,
            "request-contract-rejection",
            operational_metadata,
        )
    if error_class.startswith("provider-contract-or-safety:"):
        taxonomy_class = error_class.split(":", 1)[1]
        if taxonomy_class not in CONTRACT_SAFETY_CLASSES:
            taxonomy_class = "unregistered-error-class"
        return _contract(provider, error_class, taxonomy_class, operational_metadata)

    status = _optional_status(operational_metadata.get("http_status"))
    provider_type = _optional_text(operational_metadata.get("provider_error_type"))
    provider_code = _optional_text(operational_metadata.get("provider_error_code"))
    typed = {value for value in (provider_type, provider_code) if value is not None}

    if provider == "OpenAI":
        if error_class == "timeout":
            return _operational(
                provider, error_class, "openai-client-timeout", operational_metadata
            )
        if error_class == "transient-transport":
            return _operational(
                provider, error_class, "openai-transient-transport", operational_metadata
            )
        if error_class == "invalid-provider-json":
            return _operational(
                provider,
                error_class,
                "openai-invalid-provider-envelope-exhausted",
                operational_metadata,
            )
        if error_class == "rate-limit":
            if typed & {"insufficient_quota", "billing_error", "credits_exhausted"}:
                return _contract(
                    provider,
                    error_class,
                    "credential-authorization-or-billing-boundary-failure",
                    operational_metadata,
                )
            if typed & {"rate_limit_error", "rate_limit_exceeded"}:
                return _operational(
                    provider,
                    error_class,
                    "openai-rate-limit-reached",
                    operational_metadata,
                )
            return _contract(
                provider,
                error_class,
                "ambiguous-operational-versus-contract-status",
                operational_metadata,
            )
        if error_class == "transient-provider":
            if status == 500 and (not typed or typed & {"server_error", "api_error"}):
                return _operational(
                    provider, error_class, "openai-server-error", operational_metadata
                )
            if status == 503 and (not typed or typed & {"overloaded_error", "server_error"}):
                return _operational(
                    provider, error_class, "openai-overloaded", operational_metadata
                )
            return _contract(
                provider,
                error_class,
                "ambiguous-operational-versus-contract-status",
                operational_metadata,
            )
    else:
        if error_class == "timeout":
            return _operational(
                provider, error_class, "anthropic-client-timeout", operational_metadata
            )
        if error_class == "transient-transport":
            return _operational(
                provider,
                error_class,
                "anthropic-transient-transport",
                operational_metadata,
            )
        if error_class == "invalid-provider-json":
            return _operational(
                provider,
                error_class,
                "anthropic-invalid-provider-envelope-exhausted",
                operational_metadata,
            )
        if error_class == "rate-limit" and (status == 429 or "rate_limit_error" in typed):
            return _operational(
                provider,
                error_class,
                "anthropic-rate-limit-error",
                operational_metadata,
            )
        if error_class == "transient-provider":
            if status == 500 and "api_error" in typed:
                return _operational(
                    provider, error_class, "anthropic-api-error", operational_metadata
                )
            if status == 504 and "timeout_error" in typed:
                return _operational(
                    provider, error_class, "anthropic-timeout-error", operational_metadata
                )
            if status == 529 and "overloaded_error" in typed:
                return _operational(
                    provider,
                    error_class,
                    "anthropic-overloaded-error",
                    operational_metadata,
                )
            return _contract(
                provider,
                error_class,
                "ambiguous-operational-versus-contract-status",
                operational_metadata,
            )
    return _contract(
        provider,
        error_class,
        "unregistered-error-class",
        operational_metadata,
    )


class ProspectiveProviderOutcomeAdapter:
    """Make contract/safety failures nonretryable before the bounded retry layer."""

    def __init__(self, adapter: AgentAdapter, *, provider: str) -> None:
        self.adapter = adapter
        self.provider = provider
        self.manifest = adapter.manifest

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        response = self.adapter.respond(request)
        if response.error_class is None:
            return response
        classified = classify_provider_error(
            provider=self.provider,
            error_class=response.error_class,
            operational_metadata=response.operational_metadata,
        )
        metadata = {
            **response.operational_metadata,
            "provider_outcome_disposition": classified.disposition,
            "provider_outcome_class": classified.taxonomy_class,
        }
        if classified.retry_eligible:
            return replace(response, operational_metadata=metadata)
        for name in SAFE_RETRY_METADATA_FIELDS:
            metadata.pop(name, None)
        return replace(
            response,
            error_class=f"provider-contract-or-safety:{classified.taxonomy_class}",
            operational_metadata=metadata,
        )


@dataclass(frozen=True)
class PairingClassificationV3:
    """Exactly one prospective policy-v3 terminal status for a pairing."""

    pairing_id: str
    provider: str
    model: str
    task_commitment: str
    architecture_id: str
    trace_id: str
    status: PairingStatusV3
    provider_response_completed: bool
    protocol_compliance: ProtocolComplianceStatus
    method_c_errors: tuple[str, ...]
    provider_error_class: str | None = None

    def __post_init__(self) -> None:
        if self.status not in PAIRING_STATUSES_V3:
            raise ValueError("unregistered policy-v3 pairing status")
        completed_status = self.status in {PROTOCOL_VALID, PROTOCOL_INVALID}
        if self.provider_response_completed is not completed_status:
            raise ValueError("provider completion does not match pairing status")
        expected_protocol = {
            PROTOCOL_VALID: "pass",
            PROTOCOL_INVALID: "fail",
            PROVIDER_OPERATIONAL_MISSING: "not-applicable",
            PROVIDER_CONTRACT_OR_SAFETY_FAILURE: "not-applicable",
        }[self.status]
        if self.protocol_compliance != expected_protocol:
            raise ValueError("protocol compliance status does not match terminal status")
        if self.status == PROTOCOL_VALID and self.method_c_errors:
            raise ValueError("protocol-valid pairing cannot carry Method C errors")
        if self.status == PROTOCOL_INVALID and not self.method_c_errors:
            raise ValueError("protocol-invalid pairing requires a safe Method C error")
        if completed_status and self.provider_error_class is not None:
            raise ValueError("completed response cannot carry provider terminal error class")
        if not completed_status and not self.provider_error_class:
            raise ValueError("provider terminal status requires a safe error class")

    def serializable(self) -> dict[str, object]:
        return {
            "pairing_id": self.pairing_id,
            "provider": self.provider,
            "model": self.model,
            "task_commitment": self.task_commitment,
            "architecture_id": self.architecture_id,
            "trace_id": self.trace_id,
            "status": self.status,
            "provider_response_completed": self.provider_response_completed,
            "protocol_compliance": self.protocol_compliance,
            "method_c_errors": list(self.method_c_errors),
            "provider_error_class": self.provider_error_class,
        }


def classify_pairing_v3(
    *,
    pairing_id: str,
    provider: str,
    model: str,
    task_commitment: str,
    architecture_id: str,
    trace_id: str,
    provider_response_completed: bool,
    method_c_errors: Sequence[str] = (),
    provider_error: ProviderErrorClassification | None = None,
) -> PairingClassificationV3:
    errors = tuple(str(item) for item in method_c_errors)
    if provider_response_completed:
        if provider_error is not None:
            raise ValueError("completed provider response cannot have a terminal provider error")
        status: PairingStatusV3 = PROTOCOL_INVALID if errors else PROTOCOL_VALID
        compliance: ProtocolComplianceStatus = "fail" if errors else "pass"
        error_class = None
    else:
        if errors:
            raise ValueError("missing provider response cannot have Method C errors")
        if provider_error is None:
            raise ValueError("missing provider response requires provider classification")
        status = provider_error.disposition
        compliance = "not-applicable"
        error_class = provider_error.taxonomy_class
    return PairingClassificationV3(
        pairing_id=pairing_id,
        provider=provider,
        model=model,
        task_commitment=task_commitment,
        architecture_id=architecture_id,
        trace_id=trace_id,
        status=status,
        provider_response_completed=provider_response_completed,
        protocol_compliance=compliance,
        method_c_errors=errors,
        provider_error_class=error_class,
    )


def validate_terminal_classifications_v3(
    intended_pairing_ids: Iterable[str],
    classifications: Sequence[PairingClassificationV3],
) -> dict[str, PairingClassificationV3]:
    intended = tuple(str(item) for item in intended_pairing_ids)
    if len(set(intended)) != len(intended):
        raise ValueError("intended pairing registry contains duplicates")
    counts = Counter(item.pairing_id for item in classifications)
    if any(count != 1 for count in counts.values()):
        raise ValueError("duplicate terminal pairing classification")
    if set(counts) != set(intended):
        raise ValueError("missing or unexpected terminal pairing classification")
    return {item.pairing_id: item for item in classifications}


@dataclass(frozen=True)
class CircuitBreakerSnapshot:
    cumulative_operational_missing: int
    consecutive_same_provider_missing: int
    last_missing_provider: str | None
    fired: bool
    reason: str | None
    firing_sequence: int | None

    def serializable(self) -> dict[str, object]:
        return {
            "cumulative_operational_missing": self.cumulative_operational_missing,
            "consecutive_same_provider_missing": self.consecutive_same_provider_missing,
            "last_missing_provider": self.last_missing_provider,
            "fired": self.fired,
            "reason": self.reason,
            "firing_sequence": self.firing_sequence,
        }


class OperationalCircuitBreaker:
    """Frozen sequence-only engineering guard; it never inspects performance."""

    consecutive_limit = 3
    cumulative_limit = 10

    def __init__(self) -> None:
        self._cumulative = 0
        self._consecutive = 0
        self._last_provider: str | None = None
        self._fired = False
        self._reason: str | None = None
        self._firing_sequence: int | None = None
        self._last_sequence = -1

    def observe(
        self,
        classification: PairingClassificationV3,
        *,
        sequence: int,
        public_canary: bool = False,
    ) -> CircuitBreakerSnapshot:
        if self._fired:
            raise RuntimeError("operational circuit breaker already fired")
        if sequence <= self._last_sequence:
            raise ValueError("terminal sequence must increase strictly")
        self._last_sequence = sequence
        if public_canary and classification.status != PROTOCOL_VALID:
            self._fire("public-canary-not-protocol-valid", sequence)
        elif classification.status == PROVIDER_CONTRACT_OR_SAFETY_FAILURE:
            self._fire("provider-contract-or-safety-failure", sequence)
        elif classification.status == PROVIDER_OPERATIONAL_MISSING:
            self._cumulative += 1
            if self._last_provider == classification.provider:
                self._consecutive += 1
            else:
                self._last_provider = classification.provider
                self._consecutive = 1
            if self._consecutive >= self.consecutive_limit:
                self._fire("three-consecutive-same-provider-operational-missing", sequence)
            elif self._cumulative >= self.cumulative_limit:
                self._fire("ten-cumulative-provider-operational-missing", sequence)
        else:
            self._last_provider = None
            self._consecutive = 0
        return self.snapshot()

    def _fire(self, reason: str, sequence: int) -> None:
        self._fired = True
        self._reason = reason
        self._firing_sequence = sequence

    def snapshot(self) -> CircuitBreakerSnapshot:
        return CircuitBreakerSnapshot(
            cumulative_operational_missing=self._cumulative,
            consecutive_same_provider_missing=self._consecutive,
            last_missing_provider=self._last_provider,
            fired=self._fired,
            reason=self._reason,
            firing_sequence=self._firing_sequence,
        )


@dataclass(frozen=True)
class MetricIntervalV3:
    pairing_id: str
    provider: str
    model: str
    task_commitment: str
    architecture_id: str
    metric_id: str
    status: PairingStatusV3
    lower: Fraction
    upper: Fraction
    operational_credit: str
    exact_metric_defined: bool

    def __post_init__(self) -> None:
        if self.metric_id not in METRIC_IDS_V3:
            raise ValueError("unregistered policy-v3 metric")
        if self.status == PROVIDER_CONTRACT_OR_SAFETY_FAILURE:
            raise ValueError("contract/safety failure is quarantining, not bounded")
        if self.lower > self.upper:
            raise ValueError("metric interval lower bound exceeds upper bound")
        if self.status == PROTOCOL_VALID and self.lower != self.upper:
            raise ValueError("protocol-valid metric interval must be exact")

    def serializable(self) -> dict[str, object]:
        return {
            "pairing_id": self.pairing_id,
            "provider": self.provider,
            "model": self.model,
            "task_commitment": self.task_commitment,
            "architecture_id": self.architecture_id,
            "metric_id": self.metric_id,
            "status": self.status,
            "lower": str(self.lower),
            "upper": str(self.upper),
            "operational_credit": self.operational_credit,
            "exact_metric_defined": self.exact_metric_defined,
        }


@dataclass(frozen=True)
class ContrastBoundV3:
    model: str
    metric_id: str
    left_architecture: str
    right_architecture: str
    intended_eligible_pairs: int
    lower: Fraction
    upper: Fraction

    def serializable(self) -> dict[str, object]:
        return {
            "model": self.model,
            "metric_id": self.metric_id,
            "left_architecture": self.left_architecture,
            "right_architecture": self.right_architecture,
            "intended_eligible_pairs": self.intended_eligible_pairs,
            "lower": str(self.lower),
            "upper": str(self.upper),
        }


def _fraction(value: object) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, Decimal):
        return Fraction(value)
    if isinstance(value, int):
        return Fraction(value, 1)
    return Fraction(str(value))


def _eligible(task: TaskInstance, metric_id: str) -> bool:
    if metric_id == "recovery-budget-attainment":
        return task.baseline.recovery_budget is not None
    if metric_id == "source-diversity":
        return task.family_id == "common-source-acquisition"
    if metric_id == "distance-from-best-registered-equilibrium":
        return task.baseline.best_equilibrium is not None
    if metric_id == "distance-from-worst-registered-equilibrium":
        return task.baseline.worst_equilibrium is not None
    return True


def _unknown_action_bounds(
    task: TaskInstance,
    metric_id: str,
    *,
    missing: bool,
) -> tuple[Fraction, Fraction, str, bool]:
    prefix = "missing" if missing else "invalid"
    if metric_id in {
        "group-discovery",
        "distinct-action-coverage",
        "recovery-budget-attainment",
        "source-diversity",
    }:
        return Fraction(0), Fraction(1), f"0-operational-no-valid-action-{prefix}", False
    if metric_id == "duplication":
        return Fraction(0), Fraction(1), f"none-no-valid-portfolio-{prefix}", False
    if metric_id == "planner-regret":
        comparator = Fraction(task.baseline.planner_discovery)
        return comparator - 1, comparator, f"none-no-valid-portfolio-{prefix}", False
    if metric_id == "private-baseline-regret":
        comparator = Fraction(task.baseline.private_discovery)
        return comparator - 1, comparator, f"none-no-valid-portfolio-{prefix}", False
    if metric_id == "communication-induced-action-compression":
        return Fraction(-1), Fraction(1), f"none-no-valid-paired-portfolio-{prefix}", False
    if metric_id in {
        "distance-from-best-registered-equilibrium",
        "distance-from-worst-registered-equilibrium",
    }:
        return Fraction(0), Fraction(1), f"none-no-valid-portfolio-{prefix}", False
    if metric_id == "invalid-action-rate":
        if missing:
            return Fraction(0), Fraction(1), "not-an-invalid-submitted-action", False
        return Fraction(1), Fraction(1), "1-invalid-submitted-action", True
    if metric_id == "protocol-compliance":
        if missing:
            return Fraction(0), Fraction(1), "not-applicable-no-completed-response", False
        return Fraction(0), Fraction(0), "0", True
    raise ValueError(f"operational metric requires exact ledger value: {metric_id}")


def metric_intervals_v3(
    *,
    task: TaskInstance,
    classification: PairingClassificationV3,
    exact_metrics: Mapping[str, object],
) -> tuple[MetricIntervalV3, ...]:
    if classification.status == PROVIDER_CONTRACT_OR_SAFETY_FAILURE:
        raise ValueError("provider contract/safety failure requires quarantine")
    normalized = dict(exact_metrics)
    if "tokens" not in normalized and {
        "input_tokens",
        "output_tokens",
    }.issubset(normalized):
        normalized["tokens"] = int(str(normalized["input_tokens"])) + int(
            str(normalized["output_tokens"])
        )
    normalized["provider_response_completion"] = int(classification.provider_response_completed)
    normalized["provider_missingness"] = int(classification.status == PROVIDER_OPERATIONAL_MISSING)
    intervals: list[MetricIntervalV3] = []
    for metric_id in METRIC_IDS_V3:
        if not _eligible(task, metric_id):
            continue
        field = METRIC_FIELD_NAMES_V3[metric_id]
        if classification.status == PROTOCOL_VALID:
            if field not in normalized and metric_id not in normalized:
                raise ValueError(f"valid pairing is missing exact metric: {metric_id}")
            value = _fraction(normalized.get(field, normalized.get(metric_id)))
            lower = upper = value
            credit = f"exact:{value}"
            exact_defined = True
        elif metric_id in {
            "calls",
            "tokens",
            "cost",
            "retry-count",
            "provider-response-completion",
            "provider-missingness",
        }:
            if field not in normalized and metric_id not in normalized:
                raise ValueError(f"terminal pairing is missing operational metric: {metric_id}")
            value = _fraction(normalized.get(field, normalized.get(metric_id)))
            lower = upper = value
            credit = f"exact-ledger:{value}"
            exact_defined = True
        else:
            lower, upper, credit, exact_defined = _unknown_action_bounds(
                task,
                metric_id,
                missing=classification.status == PROVIDER_OPERATIONAL_MISSING,
            )
        intervals.append(
            MetricIntervalV3(
                pairing_id=classification.pairing_id,
                provider=classification.provider,
                model=classification.model,
                task_commitment=classification.task_commitment,
                architecture_id=classification.architecture_id,
                metric_id=metric_id,
                status=classification.status,
                lower=lower,
                upper=upper,
                operational_credit=credit,
                exact_metric_defined=exact_defined,
            )
        )
    return tuple(intervals)


def architecture_contrast_bounds_v3(
    intervals: Sequence[MetricIntervalV3],
    *,
    contrasts: Sequence[tuple[str, str]] = PRIMARY_CONTRASTS,
) -> tuple[ContrastBoundV3, ...]:
    indexed: dict[tuple[str, str, str, str], MetricIntervalV3] = {}
    for item in intervals:
        key = (item.model, item.task_commitment, item.architecture_id, item.metric_id)
        if key in indexed:
            raise ValueError("duplicate policy-v3 metric interval")
        indexed[key] = item
    output: list[ContrastBoundV3] = []
    for model in sorted({item.model for item in intervals}):
        for metric_id in METRIC_IDS_V3:
            tasks = sorted(
                {
                    item.task_commitment
                    for item in intervals
                    if item.model == model and item.metric_id == metric_id
                }
            )
            for left_architecture, right_architecture in contrasts:
                pair_bounds: list[tuple[Fraction, Fraction]] = []
                for task_commitment in tasks:
                    left = indexed.get((model, task_commitment, left_architecture, metric_id))
                    right = indexed.get((model, task_commitment, right_architecture, metric_id))
                    if left is None and right is None:
                        continue
                    if left is None or right is None:
                        raise ValueError("intended metric contrast pairing is incomplete")
                    pair_bounds.append((left.lower - right.upper, left.upper - right.lower))
                if pair_bounds:
                    denominator = len(pair_bounds)
                    output.append(
                        ContrastBoundV3(
                            model=model,
                            metric_id=metric_id,
                            left_architecture=left_architecture,
                            right_architecture=right_architecture,
                            intended_eligible_pairs=denominator,
                            lower=sum((item[0] for item in pair_bounds), Fraction(0)) / denominator,
                            upper=sum((item[1] for item in pair_bounds), Fraction(0)) / denominator,
                        )
                    )
    return tuple(output)


def selection_conditioned_diagnostic_v3(
    values: Sequence[object],
    *,
    selection_condition: Literal[
        "protocol-valid-output", "completed-provider-response"
    ] = "protocol-valid-output",
    label: str = CONDITIONAL_DIAGNOSTIC_ROLE,
) -> Mapping[str, object]:
    if label in FORBIDDEN_UNCONDITIONAL_LABELS or label != CONDITIONAL_DIAGNOSTIC_ROLE:
        raise ValueError("complete-case estimate cannot be labeled unconditional")
    exact = tuple(_fraction(item) for item in values)
    return {
        "role": CONDITIONAL_DIAGNOSTIC_ROLE,
        "selection_condition": selection_condition,
        "n": len(exact),
        "estimate": (str(sum(exact, Fraction(0)) / len(exact)) if exact else None),
        "unconditional_architecture_effect": False,
    }


@dataclass(frozen=True)
class BatchAcceptanceInputsV3:
    both_public_canaries_pass: bool = True
    fresh_custody_pass: bool = True
    response_ledger_trace_classification_bound_identity_exact: bool = True
    contamination_zero: bool = True
    caps_hold: bool = True
    provider_phase_closed_before_lock: bool = True
    output_lock_and_commitments_pass: bool = True
    no_call_after_lock: bool = True
    post_lock_unseal_and_commitments_pass: bool = True
    method_a_b_agree_where_defined: bool = True
    method_c_classifies_every_completed_response: bool = True
    independent_provider_outcomes_agree: bool = True
    independent_bounds_agree: bool = True
    corruptions_pass: bool = True
    redaction_pass: bool = True
    execution_identity_matches: bool = True
    retained_state_safe: bool = True


@dataclass(frozen=True)
class BatchDispositionV3:
    decision: Literal["engineering-complete", "quarantine"]
    intended_pairings: int
    protocol_valid: int
    protocol_invalid: int
    provider_operational_missing: int
    provider_contract_or_safety_failure: int
    circuit_breaker: CircuitBreakerSnapshot
    quarantine_reasons: tuple[str, ...]

    @property
    def quarantined(self) -> bool:
        return self.decision == "quarantine"


def assess_batch_v3(
    *,
    intended_pairing_ids: Iterable[str],
    classifications: Sequence[PairingClassificationV3],
    circuit_breaker: CircuitBreakerSnapshot,
    acceptance: BatchAcceptanceInputsV3 | None = None,
) -> BatchDispositionV3:
    if acceptance is None:
        acceptance = BatchAcceptanceInputsV3()
    intended = tuple(str(item) for item in intended_pairing_ids)
    reasons: list[str] = []
    try:
        classified = validate_terminal_classifications_v3(intended, classifications)
    except ValueError:
        classified = {}
        reasons.append("missing-or-duplicate-terminal-classification")
    counts = Counter(item.status for item in classified.values())
    if counts[PROVIDER_CONTRACT_OR_SAFETY_FAILURE]:
        reasons.append("provider-contract-or-safety-failure")
    if circuit_breaker.fired:
        reasons.append(circuit_breaker.reason or "operational-circuit-breaker")
    flags = {
        "both_public_canaries_pass": "public-canary-failure",
        "fresh_custody_pass": "fresh-custody-failure",
        "response_ledger_trace_classification_bound_identity_exact": (
            "response-ledger-trace-classification-bound-integrity-failure"
        ),
        "contamination_zero": "contamination",
        "caps_hold": "cap-breach",
        "provider_phase_closed_before_lock": "provider-phase-close-order-failure",
        "output_lock_and_commitments_pass": "output-lock-or-commitment-failure",
        "no_call_after_lock": "call-after-lock",
        "post_lock_unseal_and_commitments_pass": "unseal-or-commitment-failure",
        "method_a_b_agree_where_defined": "method-a-b-disagreement",
        "method_c_classifies_every_completed_response": "method-c-classification-failure",
        "independent_provider_outcomes_agree": "provider-outcome-classifier-disagreement",
        "independent_bounds_agree": "independent-bound-reconstruction-disagreement",
        "corruptions_pass": "corruption-acceptance",
        "redaction_pass": "redaction-failure",
        "execution_identity_matches": "execution-identity-mismatch",
        "retained_state_safe": "unsafe-retained-state",
    }
    for field, reason in flags.items():
        if not getattr(acceptance, field):
            reasons.append(reason)
    return BatchDispositionV3(
        decision="quarantine" if reasons else "engineering-complete",
        intended_pairings=len(intended),
        protocol_valid=counts[PROTOCOL_VALID],
        protocol_invalid=counts[PROTOCOL_INVALID],
        provider_operational_missing=counts[PROVIDER_OPERATIONAL_MISSING],
        provider_contract_or_safety_failure=counts[PROVIDER_CONTRACT_OR_SAFETY_FAILURE],
        circuit_breaker=circuit_breaker,
        quarantine_reasons=tuple(dict.fromkeys(reasons)),
    )
