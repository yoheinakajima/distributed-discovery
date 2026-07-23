"""Execution-authorization validation and fail-closed live guard."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal

REQUIRED_AUTHORIZATION_FIELDS = frozenset(
    {
        "schema_version",
        "authorization_id",
        "authorized_commit",
        "issue",
        "branch",
        "allowed_providers_models",
        "exact_snapshots",
        "total_spend_cap_usd",
        "provider_spend_caps_usd",
        "local_resource_caps",
        "expires_at",
        "custody_required",
        "trace_required",
        "campaign_id",
        "owner_decision_timestamp",
        "revoked",
        "public_fixtures_only",
    }
)


def validate_authorization(
    value: Mapping[str, object],
    *,
    expected_commit: str | None = None,
    allow_positive_spend: bool = False,
    now: datetime | None = None,
) -> Mapping[str, object]:
    missing = REQUIRED_AUTHORIZATION_FIELDS - set(value)
    if missing:
        raise ValueError(f"authorization missing fields: {sorted(missing)}")
    if value["schema_version"] != "agents-execution-authorization-v1":
        raise ValueError("authorization version mismatch")
    if value["revoked"] is not False:
        raise PermissionError("authorization is revoked")
    if expected_commit is not None and value["authorized_commit"] != expected_commit:
        raise PermissionError("authorized commit mismatch")
    models = value["allowed_providers_models"]
    snapshots = value["exact_snapshots"]
    if not isinstance(models, list) or not isinstance(snapshots, list):
        raise ValueError("provider/model and snapshot fields must be arrays")
    if any("latest" in str(item).lower() for item in snapshots):
        raise PermissionError("moving model aliases are prohibited")
    spend = Decimal(str(value["total_spend_cap_usd"]))
    provider_caps = value["provider_spend_caps_usd"]
    if spend < 0 or not isinstance(provider_caps, Mapping):
        raise ValueError("invalid spend cap")
    if sum((Decimal(str(item)) for item in provider_caps.values()), Decimal("0")) > spend:
        raise ValueError("provider caps exceed total spend cap")
    if spend > 0 and not allow_positive_spend:
        raise PermissionError("positive spend requires a future deliberate owner authorization")
    current = now or datetime.now(UTC)
    expires = datetime.fromisoformat(str(value["expires_at"]).replace("Z", "+00:00"))
    if expires <= current:
        raise PermissionError("authorization expired")
    if value["custody_required"] is not True or value["trace_required"] is not True:
        raise PermissionError("custody and trace requirements must be enabled")
    return value


def guard_live_execution(
    authorization: Mapping[str, object] | None,
    *,
    explicit_execute: bool,
    expected_commit: str,
) -> None:
    if not explicit_execute:
        raise PermissionError("an explicit live-execution flag is required")
    if authorization is None:
        raise PermissionError("execution authorization is required")
    validate_authorization(
        authorization,
        expected_commit=expected_commit,
        allow_positive_spend=False,
    )
    raise PermissionError("this implementation contains no authorized live campaign")
