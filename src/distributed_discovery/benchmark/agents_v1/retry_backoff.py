"""Deterministic bounded retry-delay policy for the prospective AO-0011 v5 pilot.

Only normalized delay metadata leaves this module. Raw provider headers are
never returned, persisted, or included in an exception message.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_CEILING, Decimal, InvalidOperation
from email.utils import parsedate_to_datetime

MINIMUM_RETRY_DELAY_SECONDS = 1
MAXIMUM_RETRY_AFTER_SECONDS = 30
RETRY_DELAY_FALLBACK_SECONDS = {
    "timeout": 2,
    "transient-transport": 2,
    "invalid-provider-json": 2,
    "rate-limit": 5,
    "transient-provider": 5,
}
RETRY_DELAY_SOURCES = frozenset(
    {
        "provider-retry-after",
        "registered-class-fallback",
    }
)
SAFE_RETRY_METADATA_FIELDS = frozenset(
    {
        "retry_delay_seconds",
        "retry_delay_source",
        "retry_class",
        "transport_attempt",
    }
)

RetryClock = Callable[[], datetime]
RetrySleeper = Callable[[float], None]
RetryPreflight = Callable[[], None]


def utc_now() -> datetime:
    return datetime.now(UTC)


def no_retry_preflight() -> None:
    return None


@dataclass(frozen=True)
class RetryDelayDecision:
    retry_delay_seconds: int
    retry_delay_source: str
    retry_class: str

    def __post_init__(self) -> None:
        if self.retry_class not in RETRY_DELAY_FALLBACK_SECONDS:
            raise ValueError("retry class is outside the frozen delay table")
        if self.retry_delay_source not in RETRY_DELAY_SOURCES:
            raise ValueError("retry delay source is not registered")
        if not (
            MINIMUM_RETRY_DELAY_SECONDS <= self.retry_delay_seconds <= MAXIMUM_RETRY_AFTER_SECONDS
        ):
            raise ValueError("retry delay is outside the frozen bounds")
        if (
            self.retry_delay_source == "registered-class-fallback"
            and self.retry_delay_seconds != RETRY_DELAY_FALLBACK_SECONDS[self.retry_class]
        ):
            raise ValueError("retry fallback differs from the frozen class table")

    def metadata(self) -> dict[str, object]:
        return {
            "retry_delay_seconds": self.retry_delay_seconds,
            "retry_delay_source": self.retry_delay_source,
            "retry_class": self.retry_class,
        }


@dataclass(frozen=True)
class RetryDelayRuntime:
    """Injected delay execution dependencies.

    Authorized live mode supplies ``time.sleep``. Tests and authorization-free
    rehearsals supply ``DeterministicNoWaitSleeper``.
    """

    sleeper: RetrySleeper
    clock: RetryClock = utc_now
    preflight: RetryPreflight = no_retry_preflight


class DeterministicNoWaitSleeper:
    """Record frozen delays without sleeping."""

    def __init__(self) -> None:
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        if seconds < MINIMUM_RETRY_DELAY_SECONDS or seconds > MAXIMUM_RETRY_AFTER_SECONDS:
            raise ValueError("recorded retry delay is outside the frozen bounds")
        self.delays.append(seconds)


def _numeric_retry_after(value: str) -> int | None:
    try:
        seconds = Decimal(value)
    except InvalidOperation:
        return None
    if not seconds.is_finite() or seconds < 0:
        return None
    return int(seconds.to_integral_value(rounding=ROUND_CEILING))


def _dated_retry_after(value: str, *, now: datetime) -> int | None:
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    current = now if now.tzinfo is not None else now.replace(tzinfo=UTC)
    seconds = Decimal(str((parsed.astimezone(UTC) - current.astimezone(UTC)).total_seconds()))
    return max(0, int(seconds.to_integral_value(rounding=ROUND_CEILING)))


def parse_retry_after(value: object, *, clock: RetryClock = utc_now) -> int | None:
    """Parse delta-seconds or an HTTP date and clamp it to the committed bounds."""

    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized or len(normalized) > 128:
        return None
    seconds = _numeric_retry_after(normalized)
    if seconds is None:
        seconds = _dated_retry_after(normalized, now=clock())
    if seconds is None:
        return None
    return min(
        MAXIMUM_RETRY_AFTER_SECONDS,
        max(MINIMUM_RETRY_DELAY_SECONDS, seconds),
    )


def retry_after_from_headers(headers: Mapping[str, str]) -> str | None:
    """Extract only the exact Retry-After value from a direct response."""

    matches = [value for name, value in headers.items() if name.casefold() == "retry-after"]
    if len(matches) != 1:
        return None
    return matches[0]


def select_retry_delay(
    retry_class: str,
    *,
    retry_after: object = None,
    clock: RetryClock = utc_now,
) -> RetryDelayDecision:
    if retry_class not in RETRY_DELAY_FALLBACK_SECONDS:
        raise ValueError("retry class is outside the frozen delay table")
    parsed = parse_retry_after(retry_after, clock=clock)
    if parsed is not None:
        return RetryDelayDecision(parsed, "provider-retry-after", retry_class)
    return RetryDelayDecision(
        RETRY_DELAY_FALLBACK_SECONDS[retry_class],
        "registered-class-fallback",
        retry_class,
    )


def select_retry_delay_from_headers(
    retry_class: str,
    headers: Mapping[str, str],
    *,
    clock: RetryClock = utc_now,
) -> RetryDelayDecision:
    return select_retry_delay(
        retry_class,
        retry_after=retry_after_from_headers(headers),
        clock=clock,
    )


def decision_from_metadata(
    retry_class: str,
    metadata: Mapping[str, object],
) -> RetryDelayDecision:
    """Validate retained safe metadata or deterministically choose the fallback."""

    names = {"retry_delay_seconds", "retry_delay_source", "retry_class"}
    present = names & set(metadata)
    if not present:
        return select_retry_delay(retry_class)
    if present != names:
        raise ValueError("partial retry-delay metadata is prohibited")
    try:
        seconds = int(str(metadata["retry_delay_seconds"]))
    except (TypeError, ValueError) as error:
        raise ValueError("retry delay seconds are malformed") from error
    decision = RetryDelayDecision(
        retry_delay_seconds=seconds,
        retry_delay_source=str(metadata["retry_delay_source"]),
        retry_class=str(metadata["retry_class"]),
    )
    if decision.retry_class != retry_class:
        raise ValueError("retry metadata class differs from the provider error class")
    return decision
