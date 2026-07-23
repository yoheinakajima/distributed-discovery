"""Strict, redacted local inputs for the public provider-preflight gate."""

from __future__ import annotations

import re
import stat
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

ALLOWED_CREDENTIAL_NAMES = frozenset(
    {
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "MISTRAL_API_KEY",
    }
)
OUT_OF_SCOPE_CREDENTIAL_NAMES = frozenset({"FLYMYAI_API_KEY", "MONID_API_KEY"})
ALL_RECOGNIZED_CREDENTIAL_NAMES = ALLOWED_CREDENTIAL_NAMES | OUT_OF_SCOPE_CREDENTIAL_NAMES
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_FORBIDDEN_VALUE_FRAGMENTS = ("$(", "${", "`", "&&", "||", ";", "\x00")
_AUTHORIZATION_FIELDS = frozenset(
    {
        "schema_version",
        "authorization_id",
        "purpose",
        "authorization_status",
        "execution_allowed",
        "private_tasks_allowed",
        "scientific_evidence_allowed",
        "authorized_base_commit",
        "allowed_branch",
        "credential_source",
        "external_spend_cap_usd",
        "gateway_caps_usd",
        "route_caps_usd",
        "max_calls_per_route",
        "max_total_calls",
        "max_live_concurrency",
        "expires_utc",
        "revoked",
    }
)


class CredentialSet:
    """Allowlisted credentials whose representation never exposes values."""

    __slots__ = ("_values", "configured", "unused_present")

    def __init__(
        self,
        values: Mapping[str, str],
        *,
        configured: Mapping[str, bool],
        unused_present: tuple[str, ...],
    ) -> None:
        self._values = dict(values)
        self.configured = dict(configured)
        self.unused_present = unused_present

    def __repr__(self) -> str:
        return (
            "CredentialSet(configured="
            f"{self.configured!r}, unused_present={self.unused_present!r}, values=<redacted>)"
        )

    def get_secret(self, name: str) -> str | None:
        if name not in ALLOWED_CREDENTIAL_NAMES:
            raise PermissionError("credential name is outside the live LLM allowlist")
        return self._values.get(name)

    def clear(self) -> None:
        for name in tuple(self._values):
            self._values[name] = ""
            del self._values[name]


@dataclass(frozen=True)
class PreflightAuthorization:
    authorization_id: str
    authorized_base_commit: str
    allowed_branch: str
    expires_utc: datetime
    total_cap_usd: Decimal
    gateway_caps_usd: Mapping[str, Decimal]
    route_caps_usd: Mapping[str, Decimal]
    max_calls_per_route: int
    max_total_calls: int
    max_live_concurrency: int
    private_tasks_allowed: bool
    scientific_evidence_allowed: bool
    raw: Mapping[str, object] = field(repr=False)


@dataclass
class CostLedger:
    """Fail-closed call and cost accounting for a validated authorization."""

    authorization: PreflightAuthorization
    total_cost_usd: Decimal = Decimal("0")
    calls_made: int = 0
    route_costs_usd: dict[str, Decimal] = field(default_factory=dict)
    route_calls: dict[str, int] = field(default_factory=dict)

    def authorize_next_call(
        self,
        *,
        gateway_id: str,
        route_id: str,
        maximum_call_cost_usd: Decimal,
    ) -> None:
        if maximum_call_cost_usd < 0:
            raise ValueError("maximum call cost cannot be negative")
        route_calls = self.route_calls.get(route_id, 0)
        if route_calls + 1 > self.authorization.max_calls_per_route:
            raise PermissionError("route call ceiling would be exceeded")
        if self.calls_made + 1 > self.authorization.max_total_calls:
            raise PermissionError("total call ceiling would be exceeded")
        gateway_cap = self.authorization.gateway_caps_usd.get(gateway_id)
        if gateway_cap is None:
            raise PermissionError("gateway is not authorized")
        route_cap = self.authorization.route_caps_usd.get(route_id, gateway_cap)
        route_cost = self.route_costs_usd.get(route_id, Decimal("0"))
        gateway_cost = sum(
            (
                cost
                for key, cost in self.route_costs_usd.items()
                if _gateway_for_route(key) == gateway_id
            ),
            Decimal("0"),
        )
        if route_cost + maximum_call_cost_usd > route_cap:
            raise PermissionError("projected route cost exceeds authorization")
        if gateway_cost + maximum_call_cost_usd > gateway_cap:
            raise PermissionError("projected gateway cost exceeds authorization")
        if self.total_cost_usd + maximum_call_cost_usd > self.authorization.total_cap_usd:
            raise PermissionError("projected total cost exceeds authorization")

    def record_call(self, *, route_id: str, actual_cost_usd: Decimal) -> None:
        if actual_cost_usd < 0:
            raise ValueError("actual cost cannot be negative")
        self.calls_made += 1
        self.total_cost_usd += actual_cost_usd
        self.route_calls[route_id] = self.route_calls.get(route_id, 0) + 1
        self.route_costs_usd[route_id] = (
            self.route_costs_usd.get(route_id, Decimal("0")) + actual_cost_usd
        )


def _gateway_for_route(route_id: str) -> str:
    if route_id.startswith("openrouter_"):
        return "openrouter"
    if route_id.endswith("_direct"):
        return route_id
    return route_id.split("_", 1)[0]


def load_credentials(path: Path, *, explicit_live_mode: bool) -> CredentialSet:
    """Read the exact local credential file after strict metadata checks."""
    if not explicit_live_mode:
        raise PermissionError("explicit live mode is required before credential loading")
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode):
        raise PermissionError("credential file must not be a symlink")
    if not stat.S_ISREG(metadata.st_mode):
        raise PermissionError("credential source must be a regular file")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise PermissionError("credential file permissions must be 0600 or stricter")
    parsed = parse_dotenv(path.read_bytes())
    values = {name: parsed[name] for name in ALLOWED_CREDENTIAL_NAMES if name in parsed}
    configured = {name: name in parsed for name in sorted(ALLOWED_CREDENTIAL_NAMES)}
    unused = tuple(sorted(name for name in OUT_OF_SCOPE_CREDENTIAL_NAMES if name in parsed))
    return CredentialSet(values, configured=configured, unused_present=unused)


def parse_dotenv(raw: bytes) -> dict[str, str]:
    """Parse one non-executable dotenv document without interpolation."""
    if b"\x00" in raw:
        raise ValueError("dotenv contains a prohibited NUL byte")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("dotenv must be valid UTF-8") from exc
    result: dict[str, str] = {}
    for line_number, original in enumerate(text.splitlines(), start=1):
        line = original.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith("\\"):
            raise ValueError(f"dotenv line {line_number} uses a prohibited multiline construct")
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        if "=" not in line:
            raise ValueError(f"dotenv line {line_number} is malformed")
        name, raw_value = line.split("=", 1)
        name = name.strip()
        if not _NAME.fullmatch(name):
            raise ValueError(f"dotenv line {line_number} has a malformed name")
        if name in result:
            raise ValueError(f"dotenv line {line_number} duplicates a definition")
        value = _parse_value(raw_value.strip(), line_number)
        result[name] = value
    return result


def _parse_value(raw_value: str, line_number: int) -> str:
    if not raw_value:
        return ""
    if raw_value[0] in {'"', "'"}:
        quote = raw_value[0]
        end = _closing_quote(raw_value, quote)
        if end is None:
            raise ValueError(f"dotenv line {line_number} has an unterminated quote")
        suffix = raw_value[end + 1 :].strip()
        if suffix and not suffix.startswith("#"):
            raise ValueError(f"dotenv line {line_number} has executable trailing content")
        value = raw_value[1:end]
        if quote == '"':
            value = _decode_double_quoted(value, line_number)
    else:
        value = raw_value.split(" #", 1)[0].rstrip()
    if any(fragment in value for fragment in _FORBIDDEN_VALUE_FRAGMENTS):
        raise ValueError(f"dotenv line {line_number} contains prohibited shell syntax")
    if any(character in value for character in ("|", ">", "<")):
        raise ValueError(f"dotenv line {line_number} contains a prohibited shell operator")
    if "\r" in value or "\n" in value:
        raise ValueError(f"dotenv line {line_number} contains a prohibited multiline value")
    return value


def _closing_quote(raw_value: str, quote: str) -> int | None:
    escaped = False
    for index, character in enumerate(raw_value[1:], start=1):
        if quote == '"' and escaped:
            escaped = False
            continue
        if quote == '"' and character == "\\":
            escaped = True
            continue
        if character == quote:
            return index
    return None


def _decode_double_quoted(value: str, line_number: int) -> str:
    output: list[str] = []
    index = 0
    escapes = {'"': '"', "\\": "\\", "n": "\n", "r": "\r", "t": "\t"}
    while index < len(value):
        character = value[index]
        if character != "\\":
            output.append(character)
            index += 1
            continue
        index += 1
        if index >= len(value) or value[index] not in escapes:
            raise ValueError(f"dotenv line {line_number} has an invalid escape")
        output.append(escapes[value[index]])
        index += 1
    return "".join(output)


def load_preflight_authorization(
    path: Path,
    *,
    expected_base_commit: str,
    expected_branch: str,
    now: datetime | None = None,
) -> PreflightAuthorization:
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode):
        raise PermissionError("authorization file must not be a symlink")
    if not stat.S_ISREG(metadata.st_mode):
        raise PermissionError("authorization source must be a regular file")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise PermissionError("authorization file permissions must be 0600 or stricter")
    loaded: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise ValueError("authorization root must be an object")
    document = dict(loaded)
    missing = _AUTHORIZATION_FIELDS - set(document)
    extra = set(document) - _AUTHORIZATION_FIELDS
    if missing or extra:
        raise ValueError(
            f"authorization fields mismatch; missing={sorted(missing)} extra={sorted(extra)}"
        )
    checks = {
        "schema_version": document["schema_version"] == 1,
        "purpose": (
            document["purpose"] == "unified-provider-credential-preflight-and-public-calibration"
        ),
        "authorization_status": document["authorization_status"] == "authorized",
        "execution_allowed": document["execution_allowed"] is True,
        "private_tasks_allowed": document["private_tasks_allowed"] is False,
        "scientific_evidence_allowed": document["scientific_evidence_allowed"] is False,
        "authorized_base_commit": document["authorized_base_commit"] == expected_base_commit,
        "allowed_branch": document["allowed_branch"] == expected_branch,
        "credential_source": document["credential_source"] == "repository-local-env-txt",
        "revoked": document["revoked"] is False,
    }
    failed = sorted(key for key, valid in checks.items() if not valid)
    if failed:
        raise PermissionError(f"authorization validation failed: {failed}")
    expires = datetime.fromisoformat(str(document["expires_utc"]).replace("Z", "+00:00"))
    if expires <= (now or datetime.now(UTC)):
        raise PermissionError("authorization expired")
    total_cap = _positive_decimal(document["external_spend_cap_usd"], "total cap")
    if total_cap > Decimal("20"):
        raise PermissionError("authorization exceeds the owner-declared USD 20 maximum")
    gateway_caps = _decimal_mapping(document["gateway_caps_usd"], "gateway caps")
    route_caps = _decimal_mapping(document["route_caps_usd"], "route caps")
    for route_id, route_cap in route_caps.items():
        gateway_id = _gateway_for_route(route_id)
        if gateway_id not in gateway_caps or route_cap > gateway_caps[gateway_id]:
            raise ValueError("route cap exceeds or lacks its gateway cap")
        if route_cap > total_cap:
            raise ValueError("route cap exceeds total cap")
    max_calls_per_route = _positive_int(document["max_calls_per_route"], "route call ceiling")
    max_total_calls = _positive_int(document["max_total_calls"], "total call ceiling")
    max_live_concurrency = _positive_int(document["max_live_concurrency"], "concurrency")
    if max_live_concurrency > 2:
        raise PermissionError("live concurrency exceeds the registered maximum of two")
    authorization_id = str(document["authorization_id"])
    if not authorization_id or len(authorization_id) > 160:
        raise ValueError("authorization ID is invalid")
    return PreflightAuthorization(
        authorization_id=authorization_id,
        authorized_base_commit=expected_base_commit,
        allowed_branch=expected_branch,
        expires_utc=expires,
        total_cap_usd=total_cap,
        gateway_caps_usd=gateway_caps,
        route_caps_usd=route_caps,
        max_calls_per_route=max_calls_per_route,
        max_total_calls=max_total_calls,
        max_live_concurrency=max_live_concurrency,
        private_tasks_allowed=False,
        scientific_evidence_allowed=False,
        raw=document,
    )


def _decimal_mapping(value: object, label: str) -> dict[str, Decimal]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    result: dict[str, Decimal] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{label} contains an invalid key")
        result[key] = _positive_decimal(item, label, allow_zero=True)
    return result


def _positive_decimal(value: object, label: str, *, allow_zero: bool = False) -> Decimal:
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"{label} is not numeric") from exc
    if not result.is_finite() or result < 0 or (result == 0 and not allow_zero):
        raise ValueError(f"{label} must be {'nonnegative' if allow_zero else 'positive'}")
    return result


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value
