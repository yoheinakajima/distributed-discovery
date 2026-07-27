"""Build deterministic public-only TreasureBench provider request fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.adapters import AdapterRequest, ModelManifest
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.live_providers import (
    ANTHROPIC_MANIFEST,
    OPENAI_MANIFEST,
    build_anthropic_messages_payload,
    build_openai_responses_payload,
)
from distributed_discovery.benchmark.agents_v1.models import canonical_json, sha256_hex
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.provider_schema import (
    ANTHROPIC_PROVIDER,
    OPENAI_PROVIDER,
    canonical_action_schema,
    compile_anthropic_action_schema,
    compile_openai_action_schema,
    minimal_provider_schema,
    provider_bisection_matrix,
    public_canary_matrix,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "docs/benchmark/agents-v1/fixtures/provider-schema"
R4_OUTPUT_TOKEN_CEILING = 256


def _request(manifest: ModelManifest) -> AdapterRequest:
    task = generate_public_calibration()[2]
    agent_id = sorted(task.capabilities)[0]
    prompt = compile_prompt(
        task,
        agent_id,
        architecture_id="provider-native-smoke",
        final_required=True,
    )
    return AdapterRequest(
        prompt=prompt,
        manifest=manifest,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        max_output_tokens=R4_OUTPUT_TOKEN_CEILING,
        final_required=True,
    )


def _write(name: str, value: object) -> str:
    encoded = canonical_json(value) + b"\n"
    (FIXTURE_ROOT / name).write_bytes(encoded)
    return f"sha256:{sha256_hex(encoded)}"


def build() -> dict[str, object]:
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    openai_request = _request(OPENAI_MANIFEST)
    anthropic_request = _request(ANTHROPIC_MANIFEST)

    reconstructed_failed = build_openai_responses_payload(
        openai_request,
        schema=canonical_action_schema(openai_request),
    )
    fixtures: list[dict[str, object]] = []

    def add(
        *,
        fixture_id: str,
        provider: str,
        filename: str,
        payload: object,
        complete: bool,
        expected_offline_status: str,
    ) -> None:
        fixtures.append(
            {
                "fixture_id": fixture_id,
                "provider": provider,
                "path": f"docs/benchmark/agents-v1/fixtures/provider-schema/{filename}",
                "sha256": _write(filename, payload),
                "complete": complete,
                "expected_offline_status": expected_offline_status,
            }
        )

    add(
        fixture_id="openai-terminal-http400-reconstructed",
        provider=OPENAI_PROVIDER,
        filename="openai-terminal-http400-reconstructed.json",
        payload=reconstructed_failed,
        complete=True,
        expected_offline_status="reject-unsupported-provider-keywords",
    )
    add(
        fixture_id="openai-minimal-known-valid",
        provider=OPENAI_PROVIDER,
        filename="openai-minimal-known-valid.json",
        payload=build_openai_responses_payload(
            openai_request,
            schema=minimal_provider_schema(OPENAI_PROVIDER),
        ),
        complete=False,
        expected_offline_status="pass",
    )
    add(
        fixture_id="openai-treasurebench-complete",
        provider=OPENAI_PROVIDER,
        filename="openai-treasurebench-complete.json",
        payload=build_openai_responses_payload(
            openai_request,
            schema=compile_openai_action_schema(openai_request),
        ),
        complete=True,
        expected_offline_status="pass",
    )
    add(
        fixture_id="anthropic-minimal-known-valid",
        provider=ANTHROPIC_PROVIDER,
        filename="anthropic-minimal-known-valid.json",
        payload=build_anthropic_messages_payload(
            anthropic_request,
            schema=minimal_provider_schema(ANTHROPIC_PROVIDER),
        ),
        complete=False,
        expected_offline_status="pass",
    )
    add(
        fixture_id="anthropic-treasurebench-complete",
        provider=ANTHROPIC_PROVIDER,
        filename="anthropic-treasurebench-complete.json",
        payload=build_anthropic_messages_payload(
            anthropic_request,
            schema=compile_anthropic_action_schema(anthropic_request),
        ),
        complete=True,
        expected_offline_status="pass",
    )
    bisection_order: dict[str, list[str]] = {}
    for provider, request, payload_builder in (
        (OPENAI_PROVIDER, openai_request, build_openai_responses_payload),
        (ANTHROPIC_PROVIDER, anthropic_request, build_anthropic_messages_payload),
    ):
        bisection_order[provider] = []
        for item in provider_bisection_matrix(provider, request):
            fixture_id = str(item["canary_id"])
            bisection_order[provider].append(fixture_id)
            add(
                fixture_id=fixture_id,
                provider=provider,
                filename=f"{fixture_id}.json",
                payload=payload_builder(request, schema=item["schema"]),
                complete=False,
                expected_offline_status="pass-diagnostic-only",
            )
    matrix = {
        "schema_version": "treasurebench-provider-canary-matrix-v2",
        "task_id": "AO-0004",
        "public_fixture_index": 2,
        "agent_selection": "lexicographically-first",
        "round": 0,
        "final_required": True,
        "output_token_ceilings": {
            "openai": {"minimal": 256, "complete": 256, "bisection": 256},
            "anthropic": {"minimal": 256, "complete": 256, "bisection": 256},
        },
        "diagnostic_classifications": [
            "provider-http-error",
            "refusal",
            "max-tokens",
            "json-decode",
            "transport-schema",
            "semantic-contract",
            "route-model-identity",
            "cost-boundary",
            "pass",
        ],
        "ledger_path": (
            "reports/benchmark/treasurebench-provider-schema-canaries/"
            "AO-0004-public-engineering-ledger-r4.jsonl"
        ),
        "r3_ledger_reuse_allowed": False,
        "projected_cost_usd": {
            "both_complete_pass_four_calls": "0.030703",
            "openai_complete_failure_plus_bisection_four_calls": "0.0257075",
            "anthropic_complete_failure_plus_bisection_six_calls": "0.041893",
            "expected_aggregate_strictly_below": "0.10",
            "hard_cap_total": "1.00",
            "hard_cap_per_provider": "0.50",
            "hard_call_cap": 10,
        },
        "fixtures": fixtures,
        "sequence": [item["canary_id"] for item in public_canary_matrix(openai_request)],
        "bisection_order": bisection_order,
        "bisection_policy": (
            "Only the two committed same-provider candidates may run, in their listed "
            "order, after that provider's complete schema fails. Diagnostic success "
            "does not establish conformance, and the other provider remains blocked."
        ),
        "stopping_rule": (
            "Stop immediately on any authorization, route, model, alias, fallback, "
            "privacy, schema, call-cap, or spend-cap mismatch. Stop on a minimal-schema "
            "failure. If a complete schema fails, allow only bounded schema bisection "
            "within the same provider and remaining exact gate caps; do not call the "
            "other provider until the failing provider is resolved. Declare conformance "
            "only after both complete schemas pass."
        ),
        "credentials_included": False,
        "headers_included": False,
        "private_material_included": False,
        "provider_calls": 0,
        "spend_usd": "0",
    }
    matrix_hash = _write("canary-matrix.json", matrix)
    return {
        "fixtures": len(fixtures),
        "matrix_sha256": matrix_hash,
        "provider_calls": 0,
        "spend_usd": "0",
    }


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True))
