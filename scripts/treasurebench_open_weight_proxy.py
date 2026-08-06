#!/usr/bin/env python3
"""No-log authenticated proxy for the frozen self-operated vLLM endpoint."""

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
MAX_BODY_BYTES = 1_048_576


class Proxy(BaseHTTPRequestHandler):
    server_version = "TreasureBenchRuntime/1"
    sys_version = ""
    upstream: str
    attestation: bytes
    expected_bearer: str

    def log_message(self, _format: str, *args: object) -> None:
        return

    def _authorized(self) -> bool:
        supplied = self.headers.get("Authorization", "")
        return hmac.compare_digest(supplied, f"Bearer {self.expected_bearer}")

    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
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
                result = response.read(MAX_BODY_BYTES)
                self._send(response.status, result)
        except urllib.error.HTTPError as error:
            self._send(error.code, error.read(MAX_BODY_BYTES))
        except (TimeoutError, urllib.error.URLError):
            self._send(HTTPStatus.BAD_GATEWAY, b'{"error":"upstream-unavailable"}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-host", required=True)
    parser.add_argument("--listen-port", required=True, type=int)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--attestation", required=True, type=Path)
    args = parser.parse_args()
    bearer = os.environ.get("TREASUREBENCH_RUNTIME_API_KEY", "")
    if not bearer:
        raise SystemExit("missing runtime API key")
    Proxy.upstream = args.upstream.rstrip("/")
    Proxy.attestation = args.attestation.read_bytes()
    Proxy.expected_bearer = bearer
    ThreadingHTTPServer((args.listen_host, args.listen_port), Proxy).serve_forever()


if __name__ == "__main__":
    main()
