"""Independent provider-outcome classifier for policy v3.

This module intentionally does not import the primary provider-outcome
classifier. It consumes serialized safe terminal records and rederives their
status from the frozen provider-specific taxonomy.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().casefold()
    return normalized or None


def _status(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def independently_classify_provider_error(
    record: Mapping[str, object],
) -> tuple[str, str]:
    """Return `(disposition, taxonomy_class)` without primary implementation."""

    provider = str(record.get("provider", ""))
    error_class = str(record.get("source_error_class", ""))
    http_status = _status(record.get("http_status"))
    provider_type = _text(record.get("provider_error_type"))
    provider_code = _text(record.get("provider_error_code"))
    typed = {value for value in (provider_type, provider_code) if value is not None}

    contract = "provider-contract-or-safety-failure"
    operational = "provider-operational-missing"
    if provider not in {"OpenAI", "Anthropic"}:
        return contract, "route-provider-or-region-substitution"
    if error_class.startswith("provider-contract-or-safety:"):
        suffix = error_class.split(":", 1)[1]
        allowed = {
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
        return contract, suffix if suffix in allowed else "unregistered-error-class"
    if error_class in {"authentication", "billing-or-account-access", "permission-or-policy"}:
        return contract, "credential-authorization-or-billing-boundary-failure"
    if error_class in {
        "schema-or-parameter",
        "exact-model-access",
        "conflict",
        "request-too-large",
    }:
        return contract, "request-contract-rejection"
    if error_class == "exact-model-mismatch":
        return contract, "exact-model-mismatch"
    if error_class == "hidden-reasoning-boundary":
        return contract, "hidden-reasoning-boundary-failure"

    provider_prefix = "openai" if provider == "OpenAI" else "anthropic"
    if error_class == "timeout":
        return operational, f"{provider_prefix}-client-timeout"
    if error_class == "transient-transport":
        return operational, f"{provider_prefix}-transient-transport"
    if error_class == "invalid-provider-json":
        return (
            operational,
            f"{provider_prefix}-invalid-provider-envelope-exhausted",
        )
    if provider == "OpenAI":
        if error_class == "rate-limit":
            if typed & {"insufficient_quota", "billing_error", "credits_exhausted"}:
                return contract, "credential-authorization-or-billing-boundary-failure"
            if typed & {"rate_limit_error", "rate_limit_exceeded"}:
                return operational, "openai-rate-limit-reached"
            return contract, "ambiguous-operational-versus-contract-status"
        if error_class == "transient-provider":
            if http_status == 500 and (not typed or typed & {"server_error", "api_error"}):
                return operational, "openai-server-error"
            if http_status == 503 and (not typed or typed & {"overloaded_error", "server_error"}):
                return operational, "openai-overloaded"
            return contract, "ambiguous-operational-versus-contract-status"
    else:
        if error_class == "rate-limit" and (http_status == 429 or "rate_limit_error" in typed):
            return operational, "anthropic-rate-limit-error"
        if error_class == "transient-provider":
            if http_status == 500 and "api_error" in typed:
                return operational, "anthropic-api-error"
            if http_status == 504 and "timeout_error" in typed:
                return operational, "anthropic-timeout-error"
            if http_status == 529 and "overloaded_error" in typed:
                return operational, "anthropic-overloaded-error"
            return contract, "ambiguous-operational-versus-contract-status"
    return contract, "unregistered-error-class"


def require_provider_outcome_agreement(
    primary: Sequence[Mapping[str, object]],
    source_records: Sequence[Mapping[str, object]],
) -> None:
    """Reject identity, status, or exact taxonomy disagreements."""

    if len(primary) != len(source_records):
        raise ValueError("provider-outcome classifier record count differs")
    expected: dict[str, tuple[str, str]] = {}
    for record in source_records:
        pairing_id = str(record["pairing_id"])
        if pairing_id in expected:
            raise ValueError("duplicate independent provider-outcome source")
        expected[pairing_id] = independently_classify_provider_error(record)
    observed: dict[str, tuple[str, str]] = {}
    for record in primary:
        pairing_id = str(record["pairing_id"])
        if pairing_id in observed:
            raise ValueError("duplicate primary provider-outcome classification")
        observed[pairing_id] = (
            str(record["status"]),
            str(record["provider_error_class"]),
        )
    if observed != expected:
        raise ValueError("independent provider-outcome classifier disagrees")
