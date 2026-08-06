#!/usr/bin/env python3
"""R4 no-log authenticated proxy for the frozen self-operated vLLM endpoint."""

from __future__ import annotations

import argparse
import hmac
import json
import os
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FORBIDDEN_INPUT_KEYS = {
    "answer",
    "answer_key",
    "evaluator",
    "generator",
    "generator_internals",
    "hidden_labels",
    "private_seed",
}
FORBIDDEN_ENV_NAMES = {
    "HF_TOKEN",
    "RUNPOD_API_KEY",
    "TREASUREBENCH_RUNTIME_ATTESTATION_KEY",
    "TREASUREBENCH_RUNTIME_API_KEY",
}
MAX_BODY_BYTES = 1_048_576


def scrub_environment() -> None:
    for name in tuple(os.environ):
        if name in FORBIDDEN_ENV_NAMES or name.endswith("_API_KEY") or name.endswith("_TOKEN"):
            os.environ.pop(name, None)


class Proxy(BaseHTTPRequestHandler):
    server_version = "TreasureBenchRuntimeR4/1"
    sys_version = ""
    upstream: str
    attestation: bytes
    expected_bearer: str
    peak_memory_file: Path

    def log_message(self, _format: str, *args: object) -> None:
        return

    def _authorized(self) -> bool:
        supplied = self.headers.get("Authorization", "")
        return hmac.compare_digest(supplied, f"Bearer {self.expected_bearer}")

    def _send(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if not self._authorized():
            self._send(HTTPStatus.UNAUTHORIZED, b'{"error":"unauthorized"}')
            return
        if self.path == "/runtime-attestation":
            self._send(HTTPStatus.OK, self.attestation)
            return
        if self.path == "/runtime-operational-metrics":
            try:
                peak = int(self.peak_memory_file.read_text(encoding="utf-8").strip())
            except (OSError, ValueError):
                self._send(HTTPStatus.SERVICE_UNAVAILABLE, b'{"error":"metrics-unavailable"}')
                return
            self._send(
                HTTPStatus.OK,
                json.dumps({"peak_gpu_memory_mib": peak}, separators=(",", ":")).encode(),
            )
            return
        if self.path == "/health":
            self._send(HTTPStatus.OK, b'{"status":"ok"}')
            return
        self._send(HTTPStatus.NOT_FOUND, b'{"error":"not-found"}')

    def do_POST(self) -> None:  # noqa: N802
        if not self._authorized():
            self._send(HTTPStatus.UNAUTHORIZED, b'{"error":"unauthorized"}')
            return
        if self.path != "/v1/chat/completions":
            self._send(HTTPStatus.NOT_FOUND, b'{"error":"not-found"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send(HTTPStatus.BAD_REQUEST, b'{"error":"invalid-body-size"}')
            return
        body = self.rfile.read(length)
        try:
            value = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send(HTTPStatus.BAD_REQUEST, b'{"error":"invalid-json"}')
            return
        if not isinstance(value, dict) or FORBIDDEN_INPUT_KEYS.intersection(value):
            self._send(HTTPStatus.BAD_REQUEST, b'{"error":"forbidden-input"}')
            return
        request = urllib.request.Request(
            f"{self.upstream}/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                self._send(response.status, response.read(MAX_BODY_BYTES))
        except urllib.error.HTTPError as error:
            # Do not forward raw provider bodies from the engine.
            self._send(error.code, b'{"error":"engine-rejected-request"}')
        except (TimeoutError, urllib.error.URLError):
            self._send(HTTPStatus.BAD_GATEWAY, b'{"error":"upstream-unavailable"}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-host", required=True)
    parser.add_argument("--listen-port", required=True, type=int)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--attestation", required=True, type=Path)
    parser.add_argument("--bearer-file", required=True, type=Path)
    parser.add_argument("--peak-memory-file", required=True, type=Path)
    args = parser.parse_args()
    if args.bearer_file.is_symlink() or not args.bearer_file.is_file():
        raise SystemExit("invalid bearer file")
    if args.bearer_file.stat().st_mode & 0o077:
        raise SystemExit("unsafe bearer file mode")
    bearer = args.bearer_file.read_text(encoding="utf-8")
    if not bearer:
        raise SystemExit("missing runtime bearer")
    scrub_environment()
    if FORBIDDEN_ENV_NAMES.intersection(os.environ):
        raise SystemExit("credential environment scrub failed")
    Proxy.upstream = args.upstream.rstrip("/")
    Proxy.attestation = args.attestation.read_bytes()
    Proxy.expected_bearer = bearer
    Proxy.peak_memory_file = args.peak_memory_file
    ThreadingHTTPServer((args.listen_host, args.listen_port), Proxy).serve_forever()


if __name__ == "__main__":
    main()
