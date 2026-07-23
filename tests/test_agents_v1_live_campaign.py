from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from distributed_discovery.benchmark.agents_v1.adapters import MockAdapter
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.live_campaign import (
    RouteSpec,
    _calibration_plan,
    _completed_state_resumable,
    _required_failure_decision,
    _restore_prior_attempt_ledger,
    _run_calibration_route,
    _write_route_audit,
)
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CostLedger,
    PreflightAuthorization,
)


def _authorization() -> PreflightAuthorization:
    return PreflightAuthorization(
        authorization_id="synthetic",
        authorized_base_commit="a" * 40,
        allowed_branch="benchmark/discoverybench-agents-v1-provider-preflight",
        expires_utc=datetime.now(UTC) + timedelta(days=1),
        total_cap_usd=Decimal("20"),
        gateway_caps_usd={
            "openai_direct": Decimal("5"),
            "anthropic_direct": Decimal("5"),
            "openrouter": Decimal("20"),
        },
        route_caps_usd={},
        max_calls_per_route=600,
        max_total_calls=2_000,
        max_live_concurrency=2,
        private_tasks_allowed=False,
        scientific_evidence_allowed=False,
        raw={},
    )


def _routes() -> list[RouteSpec]:
    return [
        RouteSpec(
            "openai_direct",
            "openai_direct",
            "OPENAI_API_KEY",
            "gpt-5.4-2026-03-05",
            True,
            True,
            True,
        ),
        RouteSpec(
            "anthropic_direct",
            "anthropic_direct",
            "ANTHROPIC_API_KEY",
            "claude-sonnet-4-6",
            True,
            True,
            True,
        ),
    ]


def test_calibration_plan_reserves_every_schema_retry_below_caps() -> None:
    authorization = _authorization()
    plan = _calibration_plan(_routes(), authorization, CostLedger(authorization))
    assert plan["deterministic_prefix"] == "all-10-public-tasks-all-5-architectures"
    routes = plan["routes"]
    assert isinstance(routes, dict)
    assert routes["openai_direct"]["maximum_calls"] == 588
    assert routes["anthropic_direct"]["maximum_calls"] == 588
    assert Decimal(str(plan["authorization_margin_usd"])) > 0


def test_required_failure_decision_preserves_failure_class() -> None:
    assert (
        _required_failure_decision(
            {
                "openai_direct": {
                    "failure_class": "authentication",
                    "structured_output_supported": False,
                }
            },
            True,
        )
        == "required-provider-credential-failure"
    )
    assert (
        _required_failure_decision(
            {
                "openai_direct": {
                    "failure_class": "schema",
                    "structured_output_supported": False,
                }
            },
            True,
        )
        == "structured-output-boundary-failure"
    )


def test_route_worker_preserves_method_agreement_and_redacted_traces() -> None:
    route_id, record, traces, outputs = _run_calibration_route(
        _routes()[0],
        MockAdapter(),
        generate_public_calibration()[:1],
    )
    assert route_id == "openai_direct"
    assert record["cases"] == 5
    assert record["method_a_b_agreement"] is True
    assert len(traces) == 5
    assert outputs


def test_prior_attempt_costs_and_calls_are_cumulative(tmp_path: Path) -> None:
    attempts = tmp_path / "reports/benchmark/agents-v1-preflight-attempts"
    attempts.mkdir(parents=True)
    (attempts / f"{'a' * 40}.yml").write_text(
        yaml.safe_dump(
            {
                "ledger": {
                    "calls_made": 3,
                    "total_cost_usd": "0",
                    "route_calls": {"openai_direct": 1},
                    "route_costs_usd": {"openai_direct": "0"},
                }
            }
        )
    )
    authorization = _authorization()
    ledger = CostLedger(authorization)
    _restore_prior_attempt_ledger(
        tmp_path,
        ledger,
        {
            "ledger": {
                "calls_made": 7,
                "total_cost_usd": "0.02",
                "route_calls": {"openai_direct": 3},
                "route_costs_usd": {"openai_direct": "0.01"},
            }
        },
    )
    assert ledger.calls_made == 10
    assert ledger.total_cost_usd == Decimal("0.02")
    assert ledger.route_calls["openai_direct"] == 4


def test_route_audit_records_optional_only_without_campaign_mutation(
    tmp_path: Path,
) -> None:
    audit = {
        "schema_version": "agents-v1-openrouter-route-audit-v1",
        "classification": "public-operational-route-audit-not-campaign-amendment",
        "audit_utc": "2026-07-23T00:00:00Z",
        "gateway": "openrouter",
        "credential_configured": True,
        "routes": [
            {
                "model_slug": "author/model",
                "endpoint_discovery_status": "pass",
                "endpoints": [],
                "selected_endpoint": None,
            }
        ],
        "model_family_diversity": True,
        "gateway_diversity": False,
        "campaign_manifest_authorizes_openrouter": False,
        "route_amendment_decision": "optional-public-calibration-only",
    }
    _write_route_audit(tmp_path, audit, "b" * 40)
    amendment = yaml.safe_load(
        (
            tmp_path / "reports/roadmap-consolidation/agents-v1-openrouter-route-amendment.yml"
        ).read_text()
    )
    assert amendment["decision"] == "optional-public-calibration-only"
    assert amendment["campaign_manifest_changed"] is False
    assert amendment["sealed_pilot_authorized"] is False


def test_completed_state_resumes_for_descendant_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calibration = tmp_path / "reports/benchmark/agents-v1-public-calibration.yml"
    traces = tmp_path / "reports/benchmark/agents-v1-public-operational-traces.jsonl"
    calibration.parent.mkdir(parents=True)
    calibration.write_text("status: pass\n")
    traces.write_text("{}\n")

    class Result:
        returncode = 0

    monkeypatch.setattr(
        "distributed_discovery.benchmark.agents_v1.live_campaign.subprocess.run",
        lambda *args, **kwargs: Result(),
    )
    assert _completed_state_resumable(
        tmp_path,
        {
            "execution_commit": "a" * 40,
            "preflight_complete": True,
            "calibration_complete": True,
        },
        "b" * 40,
    )
