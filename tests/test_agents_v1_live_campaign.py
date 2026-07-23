from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import yaml

from distributed_discovery.benchmark.agents_v1.live_campaign import (
    RouteSpec,
    _calibration_plan,
    _required_failure_decision,
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
