"""Fail-closed headless review capture for the Common-Source Trap Round 2 packet.

The module deliberately separates deterministic local preflight from the one
consequential provider request.  It never reads a credential until artifact,
payload, and schema checks have passed, and it never retries a request.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NoReturn

import jsonschema
import yaml


def _repository_root() -> Path:
    """Resolve the checkout from the working directory, not an installed wheel."""

    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository-root-unavailable")


ROOT = _repository_root()
ROUND2_PACKET_PATH = Path("reports/editorial/common-source-trap-round2-review-packet.yml")
OPENAI_KEYCHAIN_SERVICE = "com.yoheinakajima.chief-of-staff.openai-reviewer"
OPENAI_MODEL = "gpt-5.6-terra"
OPENAI_REASONING_EFFORT = "medium"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
CODEX_REVIEWER_SYSTEM = "openai-codex-isolated-reviewer"
CODEX_MODEL = "gpt-5.6-terra"
CODEX_REASONING_EFFORT = "medium"
MAX_PROMPT_BYTES = 170_000
MAX_OUTPUT_TOKENS = 3_000
MAX_COST_USD = 1.0

REQUESTED_CHECKS = (
    "theorem-and-proof-correctness",
    "claim-status-and-scope-calibration",
    "citation-support-and-neighboring-literature",
    "self-containment-and-dependency-clarity",
    "exposition-structure-and-reader-comprehension",
    "figures-tables-and-visual-legibility",
    "limitations-negative-results-and-counterboundaries",
    "whether-prior-revision-left-any-critical-major-or-minor-defect",
)


class ReviewError(RuntimeError):
    """Base class for a redacted, review-specific terminal condition."""


class PreflightError(ReviewError):
    """Local frozen-input or request construction validation failed."""


class CredentialUnavailable(ReviewError):
    """The exact existing Keychain entry is absent or inaccessible."""


class ProviderRejected(ReviewError):
    """The provider returned a bounded HTTP rejection after one request."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"provider-rejected-http-{status_code}")
        self.status_code = status_code


class AmbiguousDelivery(ReviewError):
    """The request may have reached the provider but no complete response exists."""


class QualificationError(ReviewError):
    """A completed response does not satisfy the frozen review contract."""


@dataclass(frozen=True)
class FrozenReviewInput:
    """Canonical public input material reconstructed from frozen Git objects."""

    artifact_commit: str
    packet_id: str
    manuscript_sha256: str
    pdf_sha256: str
    page_count: int
    packet_sha256: str
    prompt: str


@dataclass(frozen=True)
class ReviewOutcome:
    """Redacted terminal result safe to print from the command line."""

    status: str
    receipt_id: str
    receipt_sha256: str
    provider_calls: int
    cost_upper_bound_usd: str | None


KeyReader = Callable[[], bytearray]
ProviderSender = Callable[[bytes, Mapping[str, Any]], Mapping[str, Any]]
Clock = Callable[[], datetime]


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _redacted_error(error: BaseException) -> str:
    if isinstance(error, ProviderRejected):
        return str(error)
    if isinstance(error, AmbiguousDelivery):
        return "ambiguous-delivery-no-retry"
    if isinstance(error, CredentialUnavailable):
        return "credential-unavailable-no-provider-contact"
    if isinstance(error, QualificationError):
        return "response-nonqualifying"
    if isinstance(error, PreflightError):
        return "local-preflight-failed"
    return "unexpected-local-failure"


def _git_bytes(root: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise PreflightError("frozen-artifact-unavailable")
    return result.stdout


def _load_packet(root: Path) -> tuple[dict[str, Any], bytes]:
    packet_path = root / ROUND2_PACKET_PATH
    try:
        raw = packet_path.read_bytes()
        loaded = yaml.safe_load(raw)
    except (OSError, yaml.YAMLError) as error:
        raise PreflightError("round2-packet-unreadable") from error
    if not isinstance(loaded, dict):
        raise PreflightError("round2-packet-not-a-mapping")
    return loaded, raw


def _extract_pdf_pages(pdf_bytes: bytes) -> list[str]:
    """Extract text per rendered page without writing an artifact into the repository."""

    try:
        result = subprocess.run(
            ["pdftotext", "-layout", "-", "-"],
            input=pdf_bytes,
            check=False,
            capture_output=True,
        )
    except OSError as error:
        raise PreflightError("pdftotext-unavailable") from error
    if result.returncode != 0:
        raise PreflightError("pdf-page-extraction-failed")
    text = result.stdout.decode("utf-8", errors="strict")
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if not pages or any(not page.strip() for page in pages):
        raise PreflightError("pdf-page-text-empty")
    return pages


def _require_mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PreflightError(f"{name}-invalid")
    return value


def _require_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise PreflightError(f"{name}-invalid")
    return value


def _require_int(value: object, name: str) -> int:
    if not isinstance(value, int) or value < 1:
        raise PreflightError(f"{name}-invalid")
    return value


def build_frozen_review_input(root: Path = ROOT) -> FrozenReviewInput:
    """Reconstruct and verify only the three Round 2 reviewer inputs."""

    packet, packet_raw = _load_packet(root)
    source = _require_mapping(packet.get("source"), "packet-source")
    artifact_commit = _require_string(source.get("artifact_commit"), "artifact-commit")
    packet_id = _require_string(packet.get("packet_id"), "packet-id")
    manuscript = _require_mapping(source.get("manuscript"), "manuscript-record")
    pdf = _require_mapping(source.get("pdf"), "pdf-record")
    manuscript_path = _require_string(manuscript.get("path"), "manuscript-path")
    pdf_path = _require_string(pdf.get("path"), "pdf-path")
    manuscript_sha256 = _require_string(manuscript.get("sha256"), "manuscript-sha256")
    pdf_sha256 = _require_string(pdf.get("sha256"), "pdf-sha256")
    page_count = _require_int(pdf.get("page_count"), "page-count")

    manuscript_bytes = _git_bytes(root, artifact_commit, manuscript_path)
    pdf_bytes = _git_bytes(root, artifact_commit, pdf_path)
    if _sha256(manuscript_bytes) != manuscript_sha256:
        raise PreflightError("manuscript-hash-mismatch")
    if _sha256(pdf_bytes) != pdf_sha256:
        raise PreflightError("pdf-hash-mismatch")
    pages = _extract_pdf_pages(pdf_bytes)
    if len(pages) != page_count:
        raise PreflightError("pdf-page-count-mismatch")

    reviewer_prompt = _require_string(packet.get("reviewer_prompt"), "reviewer-prompt")
    requested_checks = packet.get("review_round", {}).get("requested_checks")
    if requested_checks != list(REQUESTED_CHECKS):
        raise PreflightError("requested-checks-drift")

    source_text = manuscript_bytes.decode("utf-8", errors="strict")
    page_text = "\n\n".join(
        f"===== RENDERED PDF PAGE {number} OF {page_count} =====\n{page.strip()}"
        for number, page in enumerate(pages, start=1)
    )
    packet_text = packet_raw.decode("utf-8", errors="strict")
    prompt = "\n\n".join(
        (
            reviewer_prompt,
            "Return only the strict JSON object requested by the response schema.",
            "The following are the complete, frozen review inputs. Do not use external tools, "
            "prior reviews, other sessions, or manager synthesis.",
            f"PACKET_ID: {packet_id}",
            f"ARTIFACT_COMMIT: {artifact_commit}",
            f"MANUSCRIPT_SHA256: {manuscript_sha256}",
            f"PDF_SHA256: {pdf_sha256}",
            "===== ROUND 2 PACKET =====\n" + packet_text,
            "===== REVISED MANUSCRIPT SOURCE =====\n" + source_text,
            "===== REVISED RENDERED PAPER, PAGE-LABELLED TEXT =====\n" + page_text,
        )
    )
    if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise PreflightError("prompt-byte-cap-exceeded")
    return FrozenReviewInput(
        artifact_commit=artifact_commit,
        packet_id=packet_id,
        manuscript_sha256=manuscript_sha256,
        pdf_sha256=pdf_sha256,
        page_count=page_count,
        packet_sha256=_sha256(packet_raw),
        prompt=prompt,
    )


def _review_schema(
    frozen: FrozenReviewInput,
    *,
    reviewer_system: str = "openai-responses-chatgpt-replacement",
    model: str = OPENAI_MODEL,
    reasoning_effort: str = OPENAI_REASONING_EFFORT,
) -> dict[str, Any]:
    """Return the strict model-output schema; envelope provenance is measured locally."""

    finding = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "finding_id": {"type": "string"},
            "severity": {"type": "string", "enum": ["critical", "major", "minor", "optional"]},
            "manuscript_location": {"type": "string"},
            "affected_claim_or_citation": {"type": ["string", "null"]},
            "finding": {"type": "string"},
            "repository_evidence_needed": {"type": "string"},
            "recommended_disposition": {"type": "string"},
        },
        "required": [
            "finding_id",
            "severity",
            "manuscript_location",
            "affected_claim_or_citation",
            "finding",
            "repository_evidence_needed",
            "recommended_disposition",
        ],
    }
    page_note = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"page": {"type": "integer"}, "note": {"type": "string"}},
        "required": ["page", "note"],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "reviewer_system": {"type": "string", "const": reviewer_system},
            "model": {"type": "string", "const": model},
            "reasoning_effort": {"type": "string", "const": reasoning_effort},
            "packet_id": {"type": "string", "const": frozen.packet_id},
            "artifact_commit": {"type": "string", "const": frozen.artifact_commit},
            "manuscript_sha256": {"type": "string", "const": frozen.manuscript_sha256},
            "pdf_sha256": {"type": "string", "const": frozen.pdf_sha256},
            "independence_attestation": {"type": "boolean", "const": True},
            "verdict": {
                "type": "string",
                "enum": ["ready", "minor-revision", "major-revision", "reject"],
            },
            "summary": {"type": "string"},
            "requested_checks": {
                "type": "array",
                "items": {"type": "string", "enum": list(REQUESTED_CHECKS)},
            },
            "page_notes": {"type": "array", "items": page_note},
            "findings": {"type": "array", "items": finding},
            "limitations": {"type": "string"},
        },
        "required": [
            "reviewer_system",
            "model",
            "reasoning_effort",
            "packet_id",
            "artifact_commit",
            "manuscript_sha256",
            "pdf_sha256",
            "independence_attestation",
            "verdict",
            "summary",
            "requested_checks",
            "page_notes",
            "findings",
            "limitations",
        ],
    }


def build_codex_review_prompt(frozen: FrozenReviewInput) -> str:
    """Bind one projectless Codex reviewer to the same frozen closed contract."""

    schema = _review_schema(
        frozen,
        reviewer_system=CODEX_REVIEWER_SYSTEM,
        model=CODEX_MODEL,
        reasoning_effort=CODEX_REASONING_EFFORT,
    )
    prompt = "\n\n".join(
        (
            "You are the single fresh, isolated OpenAI reviewer for Common-Source Trap "
            "Round 2. You are projectless and must use only the inputs below. Do not use "
            "prior paper or reviewer context, tools, browser state, connectors, network "
            "retrieval, or other sessions. Inspect all 21 page-labelled pages explicitly.",
            frozen.prompt,
            "Return exactly one JSON object and no Markdown or surrounding prose. It must "
            "validate against this closed JSON Schema, including all eight requested checks "
            "in their frozen order and exactly 21 ordered nonempty page notes:",
            json.dumps(schema, sort_keys=True, separators=(",", ":")),
        )
    )
    if len(prompt.encode("utf-8")) > MAX_PROMPT_BYTES:
        raise PreflightError("codex-prompt-byte-cap-exceeded")
    return prompt


def validate_codex_review_output(output_text: str, frozen: FrozenReviewInput) -> dict[str, Any]:
    """Validate one projectless Codex final response against the frozen contract."""

    try:
        review = json.loads(output_text)
    except json.JSONDecodeError as error:
        raise QualificationError("codex-response-nonqualifying") from error
    if not isinstance(review, dict):
        raise QualificationError("codex-response-nonqualifying")
    schema = _review_schema(
        frozen,
        reviewer_system=CODEX_REVIEWER_SYSTEM,
        model=CODEX_MODEL,
        reasoning_effort=CODEX_REASONING_EFFORT,
    )
    try:
        jsonschema.Draft202012Validator(schema).validate(review)
    except jsonschema.ValidationError as error:
        raise QualificationError("codex-response-nonqualifying") from error
    if tuple(review["requested_checks"]) != REQUESTED_CHECKS:
        raise QualificationError("codex-response-nonqualifying")
    notes = review["page_notes"]
    if not isinstance(notes, list) or len(notes) != frozen.page_count:
        raise QualificationError("codex-response-nonqualifying")
    if [note.get("page") for note in notes] != list(range(1, frozen.page_count + 1)):
        raise QualificationError("codex-response-nonqualifying")
    if any(not isinstance(note.get("note"), str) or not note["note"].strip() for note in notes):
        raise QualificationError("codex-response-nonqualifying")
    return review


def write_codex_review_receipt(
    output_text: str,
    *,
    thread_id: str,
    receipt_root: Path | None = None,
    clock: Clock = _utc_now,
) -> ReviewOutcome:
    """Write one private receipt after local validation of an isolated Codex review."""

    if not thread_id.strip():
        raise PreflightError("codex-thread-id-missing")
    frozen = build_frozen_review_input(ROOT)
    review = validate_codex_review_output(output_text, frozen)
    observed_at = clock().astimezone(UTC).isoformat()
    receipt_id = "cst-r2-codex-" + hashlib.sha256(thread_id.encode()).hexdigest()[:16]
    payload = {
        "schema_version": "common-source-trap-codex-review-receipt-v1",
        "status": "qualifying",
        "reviewer_surface": "codex-projectless",
        "thread_id": thread_id,
        "observed_at_utc": observed_at,
        "artifact_commit": frozen.artifact_commit,
        "packet_id": frozen.packet_id,
        "packet_sha256": frozen.packet_sha256,
        "manuscript_sha256": frozen.manuscript_sha256,
        "pdf_sha256": frozen.pdf_sha256,
        "page_count": frozen.page_count,
        "provider_calls": 0,
        "spend_usd": "0",
        "review": review,
    }
    target_root = receipt_root or _private_receipt_root()
    _, receipt_sha256 = _write_private_receipt(target_root, receipt_id, payload)
    return ReviewOutcome(
        status="qualifying",
        receipt_id=receipt_id,
        receipt_sha256=receipt_sha256,
        provider_calls=0,
        cost_upper_bound_usd="0",
    )


def build_openai_request(frozen: FrozenReviewInput) -> dict[str, Any]:
    """Construct the one-request, no-tool OpenAI Responses payload."""

    request = {
        "model": OPENAI_MODEL,
        "store": False,
        "reasoning": {"effort": OPENAI_REASONING_EFFORT},
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "input": frozen.prompt,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "common_source_trap_round2_review",
                "strict": True,
                "schema": _review_schema(frozen),
            }
        },
    }
    if "tools" in request:
        raise PreflightError("tools-must-be-absent")
    serialized = json.dumps(request, separators=(",", ":")).encode("utf-8")
    if len(serialized) > MAX_PROMPT_BYTES:
        raise PreflightError("serialized-request-byte-cap-exceeded")
    return request


def _clear(value: bytearray) -> None:
    for index in range(len(value)):
        value[index] = 0


def read_existing_openai_key() -> bytearray:
    """Read one exact Keychain entry without enumerating the Keychain or logging it."""

    account = os.environ.get("USER")
    if not account:
        raise CredentialUnavailable("credential-unavailable-no-provider-contact")
    try:
        result = subprocess.run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-a",
                account,
                "-s",
                OPENAI_KEYCHAIN_SERVICE,
                "-w",
            ],
            check=False,
            capture_output=True,
        )
    except OSError as error:
        raise CredentialUnavailable("credential-unavailable-no-provider-contact") from error
    if result.returncode != 0 or not result.stdout.strip():
        raise CredentialUnavailable("credential-unavailable-no-provider-contact")
    return bytearray(result.stdout.strip())


def _send_openai_response(api_key: bytes, request: Mapping[str, Any]) -> Mapping[str, Any]:
    """Issue exactly one response request and never surface provider bodies in errors."""

    body = json.dumps(request, separators=(",", ":")).encode("utf-8")
    authorization = b"Bearer " + api_key
    try:
        http_request = urllib.request.Request(
            OPENAI_RESPONSES_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": authorization.decode("ascii"),
                "User-Agent": "distributed-discovery-cst-review/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(http_request, timeout=120) as response:  # noqa: S310
            raw = response.read()
    except urllib.error.HTTPError as error:
        raise ProviderRejected(error.code) from None
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise AmbiguousDelivery("ambiguous-delivery-no-retry") from error
    finally:
        authorization = b""
        body = b""
    try:
        decoded = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise QualificationError("response-nonqualifying") from error
    if not isinstance(decoded, dict):
        raise QualificationError("response-nonqualifying")
    return decoded


def _response_text(response: Mapping[str, Any]) -> str:
    output = response.get("output")
    if not isinstance(output, list):
        raise QualificationError("response-nonqualifying")
    values: list[str] = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if isinstance(part, dict) and part.get("type") == "output_text":
                text = part.get("text")
                if isinstance(text, str):
                    values.append(text)
    if len(values) != 1:
        raise QualificationError("response-nonqualifying")
    return values[0]


def validate_qualified_response(
    response: Mapping[str, Any], frozen: FrozenReviewInput
) -> tuple[dict[str, Any], str]:
    """Validate response identity, strict schema, and all ordered 21-page notes."""

    if response.get("status") != "completed" or response.get("model") != OPENAI_MODEL:
        raise QualificationError("response-nonqualifying")
    if response.get("service_tier") in {"fast", "priority"}:
        raise QualificationError("response-nonqualifying")
    try:
        review = json.loads(_response_text(response))
    except json.JSONDecodeError as error:
        raise QualificationError("response-nonqualifying") from error
    if not isinstance(review, dict):
        raise QualificationError("response-nonqualifying")
    try:
        jsonschema.Draft202012Validator(_review_schema(frozen)).validate(review)
    except jsonschema.ValidationError as error:
        raise QualificationError("response-nonqualifying") from error
    if tuple(review["requested_checks"]) != REQUESTED_CHECKS:
        raise QualificationError("response-nonqualifying")
    notes = review["page_notes"]
    if not isinstance(notes, list) or len(notes) != frozen.page_count:
        raise QualificationError("response-nonqualifying")
    page_numbers = [note.get("page") for note in notes if isinstance(note, dict)]
    if page_numbers != list(range(1, frozen.page_count + 1)):
        raise QualificationError("response-nonqualifying")
    if any(not isinstance(note.get("note"), str) or not note["note"].strip() for note in notes):
        raise QualificationError("response-nonqualifying")
    response_id = response.get("id")
    if not isinstance(response_id, str) or not response_id:
        raise QualificationError("response-nonqualifying")
    return review, response_id


def _usage_cost_upper_bound(response: Mapping[str, Any]) -> str:
    """Compute a conservative standard-tier bound from returned usage only."""

    usage = response.get("usage")
    if not isinstance(usage, dict):
        raise QualificationError("response-nonqualifying")
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
        raise QualificationError("response-nonqualifying")
    if input_tokens < 0 or output_tokens < 0 or output_tokens > MAX_OUTPUT_TOKENS:
        raise QualificationError("response-nonqualifying")
    # GPT-5.6 Terra's maximum standard short-context cache-write input rate is
    # USD 2.50/M and its output rate is USD 12/M. Add 10% residency uplift.
    cost = ((input_tokens * 2.5) + (output_tokens * 12.0)) / 1_000_000 * 1.1
    if cost > MAX_COST_USD:
        raise QualificationError("response-nonqualifying")
    return f"{cost:.8f}"


def _private_receipt_root() -> Path:
    return (
        Path.home()
        / "Library"
        / "Application Support"
        / "Distributed Discovery"
        / "private-review-receipts"
    )


def _write_private_receipt(
    receipt_root: Path,
    receipt_id: str,
    payload: Mapping[str, Any],
) -> tuple[Path, str]:
    """Write a mode-0600 receipt outside Git atomically and return its hash."""

    receipt_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    receipt_root.chmod(0o700)
    target = receipt_root / f"{receipt_id}.json"
    if target.exists():
        raise PreflightError("private-receipt-collision")
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    target.chmod(0o600)
    if target.stat().st_mode & 0o777 != 0o600:
        target.unlink(missing_ok=True)
        raise PreflightError("private-receipt-mode-unsafe")
    return target, _sha256(encoded)


def _receipt_id(started: datetime) -> str:
    return f"cst-r2-openai-{started.strftime('%Y%m%dT%H%M%SZ')}"


def _failure_outcome(
    *,
    receipt_root: Path,
    started: datetime,
    frozen: FrozenReviewInput | None,
    error: BaseException,
    provider_calls: int,
) -> ReviewOutcome:
    receipt_id = _receipt_id(started)
    _path, receipt_hash = _write_private_receipt(
        receipt_root,
        receipt_id,
        {
            "schema_version": "common-source-trap-private-review-receipt-v1",
            "status": _redacted_error(error),
            "started_utc": started.isoformat(),
            "completed_utc": _utc_now().isoformat(),
            "provider_calls": provider_calls,
            "frozen_binding": (
                {
                    "packet_id": frozen.packet_id,
                    "artifact_commit": frozen.artifact_commit,
                    "manuscript_sha256": frozen.manuscript_sha256,
                    "pdf_sha256": frozen.pdf_sha256,
                    "packet_sha256": frozen.packet_sha256,
                }
                if frozen is not None
                else None
            ),
        },
    )
    return ReviewOutcome(
        status=_redacted_error(error),
        receipt_id=receipt_id,
        receipt_sha256=receipt_hash,
        provider_calls=provider_calls,
        cost_upper_bound_usd=None,
    )


def run_openai_replacement_review(
    *,
    root: Path = ROOT,
    receipt_root: Path | None = None,
    key_reader: KeyReader = read_existing_openai_key,
    provider_sender: ProviderSender = _send_openai_response,
    clock: Clock = _utc_now,
) -> ReviewOutcome:
    """Run the sole permitted OpenAI request after deterministic preflight.

    All terminal states receive a private receipt.  The caller receives only a
    redacted summary and cannot request a retry through this interface.
    """

    started = clock()
    destination = receipt_root or _private_receipt_root()
    frozen: FrozenReviewInput | None = None
    provider_calls = 0
    credential: bytearray | None = None
    try:
        frozen = build_frozen_review_input(root)
        request = build_openai_request(frozen)
        credential = key_reader()
        if not isinstance(credential, bytearray) or not credential:
            raise CredentialUnavailable("credential-unavailable-no-provider-contact")
        provider_calls = 1
        response = provider_sender(bytes(credential), request)
        review, response_id = validate_qualified_response(response, frozen)
        cost_upper_bound = _usage_cost_upper_bound(response)
        receipt_id = _receipt_id(started)
        _path, receipt_hash = _write_private_receipt(
            destination,
            receipt_id,
            {
                "schema_version": "common-source-trap-private-review-receipt-v1",
                "status": "qualifying",
                "reviewer_slot": "chatgpt",
                "provider": "openai-responses",
                "actual_model": OPENAI_MODEL,
                "reasoning_effort": OPENAI_REASONING_EFFORT,
                "started_utc": started.isoformat(),
                "completed_utc": clock().isoformat(),
                "provider_calls": provider_calls,
                "cost_upper_bound_usd": cost_upper_bound,
                "response_id": response_id,
                "frozen_binding": {
                    "packet_id": frozen.packet_id,
                    "artifact_commit": frozen.artifact_commit,
                    "manuscript_sha256": frozen.manuscript_sha256,
                    "pdf_sha256": frozen.pdf_sha256,
                    "packet_sha256": frozen.packet_sha256,
                    "page_count": frozen.page_count,
                },
                "review": review,
                "provider_response": response,
            },
        )
        return ReviewOutcome(
            status="qualifying",
            receipt_id=receipt_id,
            receipt_sha256=receipt_hash,
            provider_calls=provider_calls,
            cost_upper_bound_usd=cost_upper_bound,
        )
    except ReviewError as error:
        return _failure_outcome(
            receipt_root=destination,
            started=started,
            frozen=frozen,
            error=error,
            provider_calls=provider_calls,
        )
    except Exception as error:
        return _failure_outcome(
            receipt_root=destination,
            started=started,
            frozen=frozen,
            error=error,
            provider_calls=provider_calls,
        )
    finally:
        if credential is not None:
            _clear(credential)


def _parse_args(arguments: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m distributed_discovery.editorial_review")
    parser.add_argument(
        "--execute-openai-chatgpt-replacement",
        action="store_true",
        help="perform the one authorized OpenAI request after local preflight",
    )
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> NoReturn:
    args = _parse_args(arguments or sys.argv[1:])
    if not args.execute_openai_chatgpt_replacement:
        frozen = build_frozen_review_input()
        request = build_openai_request(frozen)
        print(
            json.dumps(
                {
                    "status": "local-preflight-passed-no-credential-or-provider-contact",
                    "packet_id": frozen.packet_id,
                    "artifact_commit": frozen.artifact_commit,
                    "page_count": frozen.page_count,
                    "request_has_tools": "tools" in request,
                },
                sort_keys=True,
            )
        )
        raise SystemExit(0)
    outcome = run_openai_replacement_review()
    print(
        json.dumps(
            {
                "status": outcome.status,
                "receipt_id": outcome.receipt_id,
                "receipt_sha256": outcome.receipt_sha256,
                "provider_calls": outcome.provider_calls,
                "cost_upper_bound_usd": outcome.cost_upper_bound_usd,
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if outcome.status == "qualifying" else 1)


if __name__ == "__main__":
    main()
