#!/usr/bin/env python3
"""No-log, Pod-scoped six-hour self-deletion watchdog for AO-0012 R4."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import quote

REST_BASE = "https://rest.runpod.io/v1"
DEADLINE_SECONDS = 21_600
MAX_RESPONSE_BYTES = 1_000_000


class WatchdogError(RuntimeError):
    """Fixed-surface watchdog failure with no provider body or credential."""


class MutableKey:
    __slots__ = ("_value", "cleared")

    def __init__(self, value: str) -> None:
        self._value = bytearray(value.encode())
        self.cleared = False

    def reveal(self) -> str:
        if self.cleared:
            raise WatchdogError("watchdog key already cleared")
        return self._value.decode()

    def clear(self) -> None:
        for index in range(len(self._value)):
            self._value[index] = 0
        self._value.clear()
        self.cleared = True

    def __repr__(self) -> str:
        return "MutableKey(<redacted>)"


class PodDeleteWatchdog:
    """Verify one Pod, arm a monotonic deadline, and delete only that Pod."""

    def __init__(
        self,
        pod_id: str,
        api_key: MutableKey,
        *,
        urlopen: Callable[..., Any] = urllib.request.urlopen,
        monotonic: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not pod_id:
            raise WatchdogError("watchdog Pod identity missing")
        self.pod_id = pod_id
        self.api_key = api_key
        self.urlopen = urlopen
        self.monotonic = monotonic
        self.sleeper = sleeper

    def __repr__(self) -> str:
        return "PodDeleteWatchdog(<redacted>)"

    def _request(self, method: str) -> Any:
        url = f"{REST_BASE}/pods/{quote(self.pod_id, safe='')}"
        request = urllib.request.Request(
            url,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key.reveal()}"},
        )
        try:
            with self.urlopen(request, timeout=20) as response:
                raw = response.read(MAX_RESPONSE_BYTES)
        except urllib.error.HTTPError as error:
            if method == "DELETE" and int(error.code) == 404:
                return {}
            raise WatchdogError(f"watchdog REST {method} HTTP {int(error.code)}") from None
        except Exception:
            raise WatchdogError(f"watchdog REST {method} unavailable") from None
        if not raw:
            return {}
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise WatchdogError(f"watchdog REST {method} malformed") from None
        finally:
            raw = b""
        return value

    def verify(self, expected_namespace: str) -> None:
        if not expected_namespace:
            raise WatchdogError("watchdog namespace missing")
        value = self._request("GET")
        if not isinstance(value, Mapping):
            raise WatchdogError("watchdog Pod response malformed")
        checks = (
            value.get("id") == self.pod_id,
            value.get("name") == expected_namespace,
            value.get("volumeEncrypted") is True,
            value.get("networkVolume") in (None, {}),
            value.get("networkVolumeId") in (None, ""),
        )
        if not all(checks):
            raise WatchdogError("watchdog Pod boundary mismatch")
        if isinstance(value, dict):
            value.clear()

    @staticmethod
    def _write_status(path: Path, *, pid: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        payload = json.dumps(
            {
                "schema_version": "ao0012-r4-pod-watchdog-v1",
                "pid": pid,
                "verified": True,
                "deadline_seconds": DEADLINE_SECONDS,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        fd = os.open(path, flags, 0o600)
        try:
            os.write(fd, payload + b"\n")
        finally:
            os.close(fd)

    def run(self, expected_namespace: str, status_path: Path) -> None:
        self.verify(expected_namespace)
        expected_namespace = ""
        deadline = self.monotonic() + DEADLINE_SECONDS
        self._write_status(status_path, pid=os.getpid())
        remaining = max(0.0, deadline - self.monotonic())
        self.sleeper(remaining)
        self._request("DELETE")


def main() -> None:
    pod_id = os.environ.pop("RUNPOD_POD_ID", "")
    raw_key = os.environ.pop("RUNPOD_API_KEY", "")
    expected_namespace = os.environ.pop("TREASUREBENCH_EXPECTED_NAMESPACE", "")
    status_path = Path(
        os.environ.pop(
            "TREASUREBENCH_WATCHDOG_STATUS_PATH",
            "/run/treasurebench-runtime-r4/watchdog-status.json",
        )
    )
    for name in tuple(os.environ):
        os.environ.pop(name, None)
    key = MutableKey(raw_key)
    raw_key = ""
    code = 0
    try:
        PodDeleteWatchdog(pod_id, key).run(expected_namespace, status_path)
    except Exception:
        code = 1
    finally:
        key.clear()
        pod_id = ""
        expected_namespace = ""
    raise SystemExit(code)


if __name__ == "__main__":
    main()
