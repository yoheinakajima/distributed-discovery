from __future__ import annotations

import json
import stat
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from distributed_discovery import editorial_review

ROOT = Path(__file__).resolve().parents[2]


def _valid_review(frozen: editorial_review.FrozenReviewInput) -> dict[str, Any]:
    return {
        "reviewer_system": "openai-responses-chatgpt-replacement",
        "model": editorial_review.OPENAI_MODEL,
        "reasoning_effort": editorial_review.OPENAI_REASONING_EFFORT,
        "packet_id": frozen.packet_id,
        "artifact_commit": frozen.artifact_commit,
        "manuscript_sha256": frozen.manuscript_sha256,
        "pdf_sha256": frozen.pdf_sha256,
        "independence_attestation": True,
        "verdict": "minor-revision",
        "summary": "The review is complete.",
        "requested_checks": list(editorial_review.REQUESTED_CHECKS),
        "page_notes": [
            {"page": number, "note": f"Page {number} was reviewed."}
            for number in range(1, frozen.page_count + 1)
        ],
        "findings": [],
        "limitations": "No external tool or prior review was used.",
    }


def _valid_codex_review(frozen: editorial_review.FrozenReviewInput) -> dict[str, Any]:
    review = _valid_review(frozen)
    review["reviewer_system"] = editorial_review.CODEX_REVIEWER_SYSTEM
    review["model"] = editorial_review.CODEX_MODEL
    review["reasoning_effort"] = editorial_review.CODEX_REASONING_EFFORT
    return review


def _valid_named_review(
    frozen: editorial_review.FrozenReviewInput,
    *,
    reviewer_system: str,
    model: str,
    effort: str,
) -> dict[str, Any]:
    review = _valid_review(frozen)
    review["reviewer_system"] = reviewer_system
    review["model"] = model
    review["reasoning_effort"] = effort
    return review


def _valid_anthropic_response(frozen: editorial_review.FrozenReviewInput) -> dict[str, Any]:
    review = _valid_named_review(
        frozen,
        reviewer_system=editorial_review.ANTHROPIC_REVIEWER_SYSTEM,
        model=editorial_review.ANTHROPIC_MODEL,
        effort=editorial_review.ANTHROPIC_REASONING_EFFORT,
    )
    return {
        "id": "msg_synthetic_claude",
        "type": "message",
        "role": "assistant",
        "model": editorial_review.ANTHROPIC_MODEL,
        "content": [{"type": "text", "text": json.dumps(review)}],
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 40_000, "output_tokens": 2_000},
    }


def _valid_gemini_response(frozen: editorial_review.FrozenReviewInput) -> dict[str, Any]:
    review = _valid_named_review(
        frozen,
        reviewer_system=editorial_review.GEMINI_REVIEWER_SYSTEM,
        model=editorial_review.GEMINI_MODEL,
        effort=editorial_review.GEMINI_REASONING_EFFORT,
    )
    return {
        "responseId": "resp_synthetic_gemini",
        "modelVersion": editorial_review.GEMINI_MODEL,
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "role": "model",
                    "parts": [{"text": json.dumps(review)}],
                },
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 40_000,
            "candidatesTokenCount": 1_800,
            "thoughtsTokenCount": 200,
            "totalTokenCount": 42_000,
        },
    }


def _valid_response(frozen: editorial_review.FrozenReviewInput) -> dict[str, Any]:
    return {
        "id": "resp_synthetic_001",
        "status": "completed",
        "model": editorial_review.OPENAI_MODEL,
        "service_tier": "default",
        "usage": {"input_tokens": 40_000, "output_tokens": 2_000},
        "output": [
            {"type": "reasoning", "content": []},
            {
                "type": "message",
                "content": [{"type": "output_text", "text": json.dumps(_valid_review(frozen))}],
            },
        ],
    }


def test_repository_root_is_checkout_not_installed_package_path() -> None:
    assert editorial_review.ROOT == ROOT
    packet = editorial_review.ROOT / "reports/editorial/common-source-trap-round2-review-packet.yml"
    assert packet.is_file()


def test_frozen_input_reconstructs_exact_round_two_artifacts() -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    assert frozen.packet_id == "common-source-trap-r2"
    assert frozen.artifact_commit == "4fa15aa7f77dcae9f02a42c64273a04969247571"
    assert (
        frozen.manuscript_sha256
        == "87a6e85450c72fc9c93b281646ecfbd60193747c80aae9eac0a022301e1f06e1"
    )
    assert frozen.pdf_sha256 == "ab53c6e4bd099234e42178646abdd7c9692533dfb0b63cea9d3d60ba1ccf1150"
    assert (
        frozen.packet_sha256 == "8d4e55adcb94161ff315be17c90945642695e531ad43770cde4154760457bbfe"
    )
    assert frozen.page_count == 21
    assert "RENDERED PDF PAGE 1 OF 21" in frozen.prompt
    assert "RENDERED PDF PAGE 21 OF 21" in frozen.prompt
    assert "prior reviews" in frozen.prompt


def test_request_is_single_call_strict_schema_and_tool_free() -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    request = editorial_review.build_openai_request(frozen)
    assert request["model"] == editorial_review.OPENAI_MODEL
    assert request["store"] is False
    assert request["reasoning"] == {"effort": "medium"}
    assert request["max_output_tokens"] == 3_000
    assert "tools" not in request
    response_format = request["text"]["format"]
    assert response_format["type"] == "json_schema"
    assert response_format["strict"] is True
    assert response_format["schema"]["additionalProperties"] is False
    assert "page_notes" in response_format["schema"]["required"]


def test_anthropic_request_uses_exact_model_effort_schema_and_no_tools() -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    request = editorial_review.build_anthropic_request(frozen)
    assert request["model"] == "claude-sonnet-5"
    assert request["max_tokens"] == 3_000
    assert request["thinking"] == {"type": "adaptive"}
    assert request["output_config"]["effort"] == "medium"
    assert request["output_config"]["format"]["type"] == "json_schema"
    schema = request["output_config"]["format"]["schema"]
    assert schema["properties"]["model"]["enum"] == ["claude-sonnet-5"]
    assert "const" not in json.dumps(schema)
    assert "tools" not in request


def test_gemini_request_uses_exact_model_effort_schema_and_no_tools() -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    request = editorial_review.build_gemini_request(frozen)
    config = request["generationConfig"]
    assert editorial_review.GEMINI_MODEL in editorial_review.GEMINI_GENERATE_URL
    assert config["maxOutputTokens"] == 3_000
    assert config["thinkingConfig"] == {
        "thinkingLevel": "medium",
        "includeThoughts": False,
    }
    assert config["responseFormat"]["text"]["mimeType"] == "application/json"
    schema = config["responseFormat"]["text"]["schema"]
    assert schema["properties"]["model"]["enum"] == ["gemini-3.1-pro-preview"]
    assert "const" not in json.dumps(schema)
    assert "tools" not in request


def test_codex_prompt_is_frozen_closed_schema_and_context_isolated() -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    prompt = editorial_review.build_codex_review_prompt(frozen)
    assert editorial_review.CODEX_REVIEWER_SYSTEM in prompt
    assert editorial_review.CODEX_MODEL in prompt
    assert "projectless" in prompt
    assert "exactly 21 ordered nonempty page notes" in prompt
    assert "RENDERED PDF PAGE 1 OF 21" in prompt
    assert "RENDERED PDF PAGE 21 OF 21" in prompt
    assert "prior paper or reviewer context" in prompt


def test_codex_review_writes_private_receipt_without_provider_activity(tmp_path: Path) -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    outcome = editorial_review.write_codex_review_receipt(
        json.dumps(_valid_codex_review(frozen)),
        thread_id="019f-synthetic-isolated-cst-review",
        receipt_root=tmp_path,
        clock=lambda: datetime(2026, 8, 8, tzinfo=UTC),
    )
    assert outcome.status == "qualifying"
    assert outcome.provider_calls == 0
    assert outcome.cost_upper_bound_usd == "0"
    receipt_path = tmp_path / f"{outcome.receipt_id}.json"
    assert stat.S_IMODE(receipt_path.stat().st_mode) == 0o600
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["reviewer_surface"] == "codex-projectless"
    assert receipt["review"]["model"] == editorial_review.CODEX_MODEL
    assert receipt["review"]["page_notes"][-1]["page"] == 21


def test_codex_review_rejects_identity_schema_and_page_coverage_drift(tmp_path: Path) -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    invalid = _valid_codex_review(frozen)
    invalid["model"] = "gpt-5.6-sol"
    with pytest.raises(editorial_review.QualificationError):
        editorial_review.write_codex_review_receipt(
            json.dumps(invalid), thread_id="wrong-model", receipt_root=tmp_path
        )
    invalid = _valid_codex_review(frozen)
    invalid["page_notes"].pop()
    with pytest.raises(editorial_review.QualificationError):
        editorial_review.write_codex_review_receipt(
            json.dumps(invalid), thread_id="missing-page", receipt_root=tmp_path
        )


def test_success_writes_private_complete_receipt_and_clears_key(tmp_path: Path) -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    captured: dict[str, object] = {}
    key = bytearray(b"sk-synthetic-secret")

    def sender(api_key: bytes, request: Mapping[str, Any]) -> Mapping[str, Any]:
        captured["api_key"] = api_key
        captured["request"] = request
        return _valid_response(frozen)

    outcome = editorial_review.run_openai_replacement_review(
        root=ROOT,
        receipt_root=tmp_path,
        key_reader=lambda: key,
        provider_sender=sender,
        clock=lambda: datetime(2026, 8, 7, tzinfo=UTC),
    )
    assert outcome.status == "qualifying"
    assert outcome.provider_calls == 1
    assert outcome.cost_upper_bound_usd == "0.13640000"
    assert captured["api_key"] == b"sk-synthetic-secret"
    assert key == bytearray(len(key))
    receipt_path = tmp_path / f"{outcome.receipt_id}.json"
    assert stat.S_IMODE(receipt_path.stat().st_mode) == 0o600
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "qualifying"
    assert receipt["provider_response"]["id"] == "resp_synthetic_001"
    assert "sk-synthetic-secret" not in receipt_path.read_text(encoding="utf-8")
    assert "sk-synthetic-secret" not in json.dumps(outcome.__dict__)


def test_missing_credential_blocks_before_provider_and_writes_failure_receipt(
    tmp_path: Path,
) -> None:
    calls = 0

    def sender(_api_key: bytes, _request: Mapping[str, Any]) -> Mapping[str, Any]:
        nonlocal calls
        calls += 1
        raise AssertionError("provider must remain unreachable")

    outcome = editorial_review.run_openai_replacement_review(
        root=ROOT,
        receipt_root=tmp_path,
        key_reader=lambda: (_ for _ in ()).throw(editorial_review.CredentialUnavailable("missing")),
        provider_sender=sender,
        clock=lambda: datetime(2026, 8, 7, tzinfo=UTC),
    )
    assert outcome.status == "credential-unavailable-no-provider-contact"
    assert outcome.provider_calls == 0
    assert calls == 0
    receipt = json.loads((tmp_path / f"{outcome.receipt_id}.json").read_text(encoding="utf-8"))
    assert receipt["provider_calls"] == 0
    assert receipt["status"] == "credential-unavailable-no-provider-contact"


def test_ambiguous_delivery_is_terminal_and_never_retried(tmp_path: Path) -> None:
    calls = 0
    key = bytearray(b"sk-synthetic-secret")

    def sender(_api_key: bytes, _request: Mapping[str, Any]) -> Mapping[str, Any]:
        nonlocal calls
        calls += 1
        raise editorial_review.AmbiguousDelivery("network")

    outcome = editorial_review.run_openai_replacement_review(
        root=ROOT,
        receipt_root=tmp_path,
        key_reader=lambda: key,
        provider_sender=sender,
        clock=lambda: datetime(2026, 8, 7, tzinfo=UTC),
    )
    assert outcome.status == "ambiguous-delivery-no-retry"
    assert outcome.provider_calls == 1
    assert calls == 1
    assert key == bytearray(len(key))


def test_incomplete_page_coverage_is_nonqualifying_without_a_second_call(tmp_path: Path) -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    response = _valid_response(frozen)
    review = json.loads(response["output"][1]["content"][0]["text"])
    review["page_notes"].pop()
    response["output"][1]["content"][0]["text"] = json.dumps(review)
    calls = 0

    def sender(_api_key: bytes, _request: Mapping[str, Any]) -> Mapping[str, Any]:
        nonlocal calls
        calls += 1
        return response

    outcome = editorial_review.run_openai_replacement_review(
        root=ROOT,
        receipt_root=tmp_path,
        key_reader=lambda: bytearray(b"sk-synthetic-secret"),
        provider_sender=sender,
        clock=lambda: datetime(2026, 8, 7, tzinfo=UTC),
    )
    assert outcome.status == "response-nonqualifying"
    assert outcome.provider_calls == 1
    assert calls == 1


def test_wrong_model_and_fast_tier_reject_after_one_response() -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    response = _valid_response(frozen)
    response["model"] = "gpt-5.6-sol"
    with pytest.raises(editorial_review.QualificationError):
        editorial_review.validate_qualified_response(response, frozen)
    response = _valid_response(frozen)
    response["service_tier"] = "fast"
    with pytest.raises(editorial_review.QualificationError):
        editorial_review.validate_qualified_response(response, frozen)


def test_keychain_reader_uses_one_exact_service_without_enumeration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[str] = []

    class Result:
        returncode = 0
        stdout = b"sk-synthetic-secret\n"

    def fake_run(arguments: list[str], **_kwargs: object) -> Result:
        captured.extend(arguments)
        return Result()

    monkeypatch.setenv("USER", "synthetic-user")
    monkeypatch.setattr(editorial_review.subprocess, "run", fake_run)
    value = editorial_review.read_existing_openai_key()
    assert value == bytearray(b"sk-synthetic-secret")
    assert captured == [
        "/usr/bin/security",
        "find-generic-password",
        "-a",
        "synthetic-user",
        "-s",
        editorial_review.OPENAI_KEYCHAIN_SERVICE,
        "-w",
    ]
    assert "list-keychains" not in captured
    editorial_review._clear(value)


@pytest.mark.parametrize(
    ("reader", "service"),
    [
        (
            editorial_review.read_existing_anthropic_key,
            editorial_review.ANTHROPIC_KEYCHAIN_SERVICE,
        ),
        (
            editorial_review.read_existing_gemini_key,
            editorial_review.GEMINI_KEYCHAIN_SERVICE,
        ),
    ],
)
def test_named_provider_keychain_reader_uses_only_exact_service(
    monkeypatch: pytest.MonkeyPatch,
    reader: Any,
    service: str,
) -> None:
    captured: list[str] = []

    class Result:
        returncode = 0
        stdout = b"synthetic-project-key\n"

    def fake_run(arguments: list[str], **_kwargs: object) -> Result:
        captured.extend(arguments)
        return Result()

    monkeypatch.setenv("USER", "synthetic-user")
    monkeypatch.setattr(editorial_review.subprocess, "run", fake_run)
    value = reader()
    assert value == bytearray(b"synthetic-project-key")
    assert captured == [
        "/usr/bin/security",
        "find-generic-password",
        "-a",
        "synthetic-user",
        "-s",
        service,
        "-w",
    ]
    editorial_review._clear(value)


@pytest.mark.parametrize(
    ("runner", "response_factory", "expected_cost", "provider_prefix"),
    [
        (
            editorial_review.run_anthropic_replacement_review,
            _valid_anthropic_response,
            "0.11000000",
            "cst-r2-anthropic-messages-",
        ),
        (
            editorial_review.run_gemini_replacement_review,
            _valid_gemini_response,
            "0.11440000",
            "cst-r2-google-gemini-",
        ),
    ],
)
def test_named_provider_success_is_one_call_private_and_clears_key(
    tmp_path: Path,
    runner: Any,
    response_factory: Any,
    expected_cost: str,
    provider_prefix: str,
) -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    key = bytearray(b"synthetic-project-key")
    calls = 0

    def sender(_api_key: bytes, _request: Mapping[str, Any]) -> Mapping[str, Any]:
        nonlocal calls
        calls += 1
        return response_factory(frozen)

    outcome = runner(
        root=ROOT,
        receipt_root=tmp_path,
        key_reader=lambda: key,
        provider_sender=sender,
        clock=lambda: datetime(2026, 8, 13, tzinfo=UTC),
    )
    assert outcome.status == "qualifying"
    assert outcome.provider_calls == 1
    assert outcome.cost_upper_bound_usd == expected_cost
    assert outcome.receipt_id.startswith(provider_prefix)
    assert calls == 1
    assert key == bytearray(len(key))
    receipt_path = tmp_path / f"{outcome.receipt_id}.json"
    assert stat.S_IMODE(receipt_path.stat().st_mode) == 0o600
    assert "synthetic-project-key" not in receipt_path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "runner",
    [
        editorial_review.run_anthropic_replacement_review,
        editorial_review.run_gemini_replacement_review,
    ],
)
def test_named_provider_ambiguous_delivery_is_terminal_and_clears_key(
    tmp_path: Path, runner: Any
) -> None:
    key = bytearray(b"synthetic-project-key")
    calls = 0

    def sender(_api_key: bytes, _request: Mapping[str, Any]) -> Mapping[str, Any]:
        nonlocal calls
        calls += 1
        raise editorial_review.AmbiguousDelivery("synthetic-timeout")

    outcome = runner(
        root=ROOT,
        receipt_root=tmp_path,
        key_reader=lambda: key,
        provider_sender=sender,
        clock=lambda: datetime(2026, 8, 13, tzinfo=UTC),
    )
    assert outcome.status == "ambiguous-delivery-no-retry"
    assert outcome.provider_calls == 1
    assert calls == 1
    assert key == bytearray(len(key))


def test_named_provider_wrong_model_or_page_coverage_is_nonqualifying() -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    anthropic = _valid_anthropic_response(frozen)
    anthropic["model"] = "claude-opus-5"
    with pytest.raises(editorial_review.QualificationError):
        editorial_review.validate_anthropic_response(anthropic, frozen)

    gemini = _valid_gemini_response(frozen)
    review = json.loads(gemini["candidates"][0]["content"]["parts"][0]["text"])
    review["page_notes"].pop()
    gemini["candidates"][0]["content"]["parts"][0]["text"] = json.dumps(review)
    with pytest.raises(editorial_review.QualificationError):
        editorial_review.validate_gemini_response(gemini, frozen)


def test_named_provider_nonqualifying_response_is_retained_privately(tmp_path: Path) -> None:
    frozen = editorial_review.build_frozen_review_input(ROOT)
    response = _valid_gemini_response(frozen)
    response["modelVersion"] = "gemini-drifted-model"

    outcome = editorial_review.run_gemini_replacement_review(
        root=ROOT,
        receipt_root=tmp_path,
        key_reader=lambda: bytearray(b"synthetic-project-key"),
        provider_sender=lambda _key, _request: response,
        clock=lambda: datetime(2026, 8, 13, tzinfo=UTC),
    )
    assert outcome.status == "response-nonqualifying"
    assert outcome.provider_calls == 1
    receipt = json.loads((tmp_path / f"{outcome.receipt_id}.json").read_text(encoding="utf-8"))
    assert receipt["provider_response"]["modelVersion"] == "gemini-drifted-model"
    assert "synthetic-project-key" not in json.dumps(receipt)
