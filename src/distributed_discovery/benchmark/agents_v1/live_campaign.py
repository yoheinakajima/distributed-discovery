"""Authorized public-only provider preflight and calibration orchestration."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.benchmark.agents_v1.actions import parse_action
from distributed_discovery.benchmark.agents_v1.adapters import AdapterRequest, AgentAdapter
from distributed_discovery.benchmark.agents_v1.contamination import (
    PROBE_CLASSES,
    classify_text,
    run_public_probes,
)
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CostLedger,
    CredentialSet,
    PreflightAuthorization,
    load_credentials,
    load_preflight_authorization,
)
from distributed_discovery.benchmark.agents_v1.live_providers import (
    ANTHROPIC_MANIFEST,
    OPENAI_MANIFEST,
    OPENROUTER_GEMINI_MODEL,
    OPENROUTER_MISTRAL_MODEL,
    AnthropicMessagesAdapter,
    HttpTransport,
    OpenAIResponsesAdapter,
    OpenRouterAdapter,
    OpenRouterEndpoint,
    UrllibTransport,
    discover_openrouter_endpoints,
    select_openrouter_endpoint,
)
from distributed_discovery.benchmark.agents_v1.models import TaskInstance
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import reconstruct_metrics

STARTING_MAIN_SHA = "8fa51758f39d4d04290784969d7990dd998019cb"
BRANCH = "benchmark/discoverybench-agents-v1-provider-preflight"
ISSUE = 175
AUTHORIZATION_FILENAME = "agents-v1-provider-preflight-authorization.yml"
STATE_RELATIVE = Path("reports/benchmark/agents-v1-live-state.yml")
READINESS_RELATIVE = Path("reports/benchmark/agents-v1-provider-readiness.yml")
TRACE_RELATIVE = Path("reports/benchmark/agents-v1-public-operational-traces.jsonl")
CALIBRATION_RELATIVE = Path("reports/benchmark/agents-v1-public-calibration.yml")
RECEIPT_RELATIVE = Path("reports/benchmark/agents-v1-provider-cost-receipt.yml")
ROUTE_AUDIT_YML = Path("reports/benchmark/agents-v1-openrouter-route-audit.yml")
ROUTE_AUDIT_MD = Path("reports/benchmark/agents-v1-openrouter-route-audit.md")
ROUTE_AMENDMENT = Path("reports/roadmap-consolidation/agents-v1-openrouter-route-amendment.yml")
EXECUTION_PATHS = (
    "Makefile",
    "src/distributed_discovery/benchmark/agents_v1",
    "docs/benchmark/agents-v1",
)


@dataclass(frozen=True)
class RouteSpec:
    route_id: str
    gateway_id: str
    credential_name: str
    model_slug: str
    required: bool
    campaign_selected: bool
    campaign_eligible: bool
    endpoint: OpenRouterEndpoint | None = None

    def public_record(self) -> dict[str, object]:
        return {
            "route_id": self.route_id,
            "gateway_id": self.gateway_id,
            "credential_variable_name": self.credential_name,
            "model_slug": self.model_slug,
            "exact_endpoint_provider_slug": (
                self.endpoint.provider_slug if self.endpoint else None
            ),
            "required_for_selected_campaign": self.required,
            "campaign_selected": self.campaign_selected,
            "campaign_eligible": self.campaign_eligible,
            "model_family_diversity": self.gateway_id == "openrouter",
            "gateway_diversity": False if self.gateway_id == "openrouter" else None,
        }


def run_provider_preflight(root: Path, *, force: bool = False) -> dict[str, object]:
    """Run the consolidated fail-soft public credential and route sweep."""
    context = _load_live_context(root, require_clean_execution=True)
    credentials, authorization, ledger, transport, execution_commit = context
    try:
        existing = _read_yaml(root / STATE_RELATIVE)
        if (
            not force
            and existing.get("execution_commit") == execution_commit
            and existing.get("preflight_complete") is True
        ):
            return _public_summary(existing, resumed=True)
        _restore_prior_attempt_ledger(root, ledger, existing)
        prior_commit = existing.get("execution_commit")
        if (
            isinstance(prior_commit, str)
            and len(prior_commit) == 40
            and prior_commit != execution_commit
            and existing.get("preflight_complete") is True
        ):
            _write_yaml(
                root / "reports/benchmark/agents-v1-preflight-attempts" / f"{prior_commit}.yml",
                existing,
            )

        routes, route_audit = _discover_routes(
            credentials=credentials,
            authorization=authorization,
            ledger=ledger,
            transport=transport,
        )
        _write_route_audit(root, route_audit, execution_commit)
        state: dict[str, object] = {
            "schema_version": "agents-v1-live-state-v1",
            "classification": "public-engineering-calibration-not-scientific-evidence",
            "issue": ISSUE,
            "starting_main": STARTING_MAIN_SHA,
            "execution_commit": execution_commit,
            "branch": BRANCH,
            "authorization_id": authorization.authorization_id,
            "authorization_expires_utc": authorization.expires_utc.isoformat().replace(
                "+00:00", "Z"
            ),
            "configured_credentials": [
                name for name, configured in credentials.configured.items() if configured
            ],
            "unused_credential_names_present": list(credentials.unused_present),
            "routes": {},
            "preflight_complete": False,
            "calibration_complete": False,
            "ledger_cumulative_across_attempts": True,
            "private_material_exists": False,
            "scientific_evidence_exists": False,
            "updated_utc": _now(),
        }
        traces: list[dict[str, object]] = []
        route_records: dict[str, object] = {}
        for spec in routes:
            try:
                adapter = _adapter_for(
                    spec,
                    credentials=credentials,
                    ledger=ledger,
                    transport=transport,
                )
                record, route_traces = _run_route_preflight(spec, adapter)
                route_records[spec.route_id] = record
                traces.extend(route_traces)
                _clear_adapter(adapter)
            except Exception as exc:
                route_records[spec.route_id] = {
                    **spec.public_record(),
                    "credential_configured": True,
                    "credential_valid": False,
                    "account_or_project_access": False,
                    "exact_model_access": False,
                    "structured_output_supported": False,
                    "provider_adapter_supported": True,
                    "public_task_end_to_end_passed": False,
                    "usage_metadata_available": False,
                    "cost_accounting_available": False,
                    "retention_policy_eligible": spec.campaign_eligible,
                    "snapshot_policy_eligible": True,
                    "calibration_complete": False,
                    "failure_class": _safe_failure(exc),
                    "outcome": "adapter-failed",
                }
            state["routes"] = route_records
            state["ledger"] = _ledger_record(ledger, authorization)
            state["updated_utc"] = _now()
            _write_yaml(root / STATE_RELATIVE, state)
        audited_routes = route_audit.get("routes")
        if isinstance(audited_routes, Sequence):
            for audited in audited_routes:
                if not isinstance(audited, Mapping):
                    continue
                route_id = str(audited.get("route_id"))
                if not route_id or route_id in route_records:
                    continue
                discovery_pass = audited.get("endpoint_discovery_status") == "pass"
                endpoints = audited.get("endpoints")
                exact_model_access = (
                    discovery_pass and isinstance(endpoints, Sequence) and bool(endpoints)
                )
                route_records[route_id] = {
                    "route_id": route_id,
                    "gateway_id": "openrouter",
                    "credential_variable_name": "OPENROUTER_API_KEY",
                    "credential_configured": True,
                    "credential_valid": discovery_pass,
                    "account_or_project_access": discovery_pass,
                    "model_slug": audited.get("model_slug"),
                    "exact_endpoint_provider_slug": None,
                    "exact_model_access": exact_model_access,
                    "returned_upstream_provider_matches": None,
                    "fallbacks_disabled": True,
                    "data_policy_eligible": False,
                    "zdr_eligible": False,
                    "structured_output_supported": False,
                    "provider_adapter_supported": True,
                    "public_task_end_to_end_passed": False,
                    "usage_metadata_available": False,
                    "cost_accounting_available": False,
                    "retention_policy_eligible": False,
                    "snapshot_policy_eligible": True,
                    "campaign_selected": False,
                    "campaign_eligible": False,
                    "required_for_selected_campaign": False,
                    "calibration_complete": False,
                    "failure_class": (
                        "policy-ineligible"
                        if exact_model_access
                        else audited.get("failure_class", "exact-model-access")
                    ),
                    "outcome": "policy-ineligible",
                    "model_family_diversity": True,
                    "gateway_diversity": False,
                }
        for name in (
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "MISTRAL_API_KEY",
        ):
            if not credentials.configured[name]:
                route_records[f"not_configured_{name.lower()}"] = {
                    "credential_variable_name": name,
                    "credential_configured": False,
                    "outcome": "optional-not-configured",
                    "failure_class": None,
                    "campaign_selected": False,
                    "campaign_eligible": False,
                    "required_for_selected_campaign": False,
                }
        required_pass = all(
            isinstance(record, Mapping) and record.get("public_task_end_to_end_passed") is True
            for route_id, record in route_records.items()
            if route_id in {"openai_direct", "anthropic_direct"}
        )
        required_configured = all(
            credentials.configured[name] for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
        )
        state["routes"] = route_records
        state["preflight_complete"] = True
        state["required_routes_ready"] = required_pass and required_configured
        state["overall_decision"] = (
            "all-required-providers-ready-public-calibration-partial"
            if required_pass and required_configured
            else _required_failure_decision(route_records, required_configured)
        )
        state["ledger"] = _ledger_record(ledger, authorization)
        state["updated_utc"] = _now()
        _write_yaml(root / STATE_RELATIVE, state)
        _append_traces(root / TRACE_RELATIVE, traces)
        _write_readiness(root, state)
        return _public_summary(state, resumed=False)
    finally:
        credentials.clear()


def run_public_calibration(root: Path, *, force: bool = False) -> dict[str, object]:
    """Run the deterministic public matrix on passing campaign-selected routes."""
    context = _load_live_context(root, require_clean_execution=False)
    credentials, authorization, ledger, transport, execution_commit = context
    try:
        state = _read_yaml(root / STATE_RELATIVE)
        if state.get("execution_commit") != execution_commit:
            raise PermissionError("preflight state does not match the execution commit")
        if state.get("preflight_complete") is not True:
            raise PermissionError("provider preflight must pass before public calibration")
        if (
            not force
            and state.get("calibration_complete") is True
            and (root / CALIBRATION_RELATIVE).exists()
        ):
            return _public_summary(state, resumed=True)
        if state.get("required_routes_ready") is not True:
            raise PermissionError("required campaign routes are not ready")
        _restore_ledger(ledger, state.get("ledger"))
        routes = _routes_from_state(state)
        selected = [
            route
            for route in routes
            if route.required and route.campaign_selected and route.campaign_eligible
        ]
        if {route.route_id for route in selected} != {"openai_direct", "anthropic_direct"}:
            raise PermissionError("the exact two campaign-selected routes are not eligible")
        plan = _calibration_plan(selected, authorization, ledger)
        calibration: dict[str, object] = {
            "schema_version": "agents-v1-public-calibration-v1",
            "classification": "engineering-only-public-not-scientific-evidence",
            "execution_commit": execution_commit,
            "tasks": 10,
            "task_families": 5,
            "architectures": list(ARCHITECTURES),
            "repeats": 1,
            "routes": [route.public_record() for route in selected],
            "plan": plan,
            "route_results": {},
            "method_a_b_agreement": True,
            "contamination_clear": False,
            "private_material_exists": False,
            "scientific_evidence_exists": False,
            "started_utc": _now(),
        }
        all_traces: list[dict[str, object]] = []
        visible_outputs: list[str] = []
        route_results: dict[str, object] = {}
        tasks = generate_public_calibration()
        with ThreadPoolExecutor(
            max_workers=min(authorization.max_live_concurrency, len(selected))
        ) as pool:
            futures = [
                pool.submit(
                    _run_calibration_route,
                    spec,
                    _adapter_for(
                        spec,
                        credentials=credentials,
                        ledger=ledger,
                        transport=transport,
                    ),
                    tasks,
                )
                for spec in selected
            ]
            for future in futures:
                route_id, route_record, route_traces, route_outputs = future.result()
                route_results[route_id] = route_record
                all_traces.extend(route_traces)
                visible_outputs.extend(route_outputs)
        probe_results = [asdict(result) for result in run_public_probes()]
        probe_suite_pass = {
            str(record.get("probe_class"))
            for record in probe_results
            if isinstance(record, Mapping)
        } == set(PROBE_CLASSES)
        output_findings = [asdict(classify_text(output)) for output in visible_outputs]
        contamination_clear = probe_suite_pass and all(
            finding.get("quarantine") is False for finding in output_findings
        )
        all_agree = all(
            isinstance(record, Mapping) and record.get("method_a_b_agreement") is True
            for record in route_results.values()
        )
        calibration["route_results"] = route_results
        calibration["method_a_b_agreement"] = all_agree
        calibration["contamination_clear"] = contamination_clear
        calibration["contamination_probes"] = probe_results
        calibration["model_output_contamination_findings"] = output_findings
        calibration["ledger"] = _ledger_record(ledger, authorization)
        calibration["completed_utc"] = _now()
        calibration["status"] = (
            "pass" if all_agree and contamination_clear else "verification-failed"
        )
        _write_yaml(root / CALIBRATION_RELATIVE, calibration)
        _append_traces(root / TRACE_RELATIVE, all_traces)
        state["calibration_complete"] = calibration["status"] == "pass"
        state["calibration_scope"] = "full-registered-public-calibration"
        state["method_a_b_agreement"] = all_agree
        state["contamination_clear"] = contamination_clear
        state["ledger"] = _ledger_record(ledger, authorization)
        state["overall_decision"] = (
            "all-required-providers-ready-public-calibration-complete"
            if state["calibration_complete"]
            else "public-calibration-verification-failure"
        )
        state["updated_utc"] = _now()
        _write_yaml(root / STATE_RELATIVE, state)
        _write_readiness(root, state)
        _write_receipt(root, state, authorization)
        return _public_summary(state, resumed=False)
    finally:
        credentials.clear()


def run_provider_preflight_all(root: Path, *, force: bool = False) -> dict[str, object]:
    """Resume passing stages and finish the guarded public workflow."""
    context = _load_live_context(root, require_clean_execution=False)
    credentials, authorization, _ledger, _transport, execution_commit = context
    try:
        state = _read_yaml(root / STATE_RELATIVE)
        if not force and _completed_state_resumable(root, state, execution_commit):
            finalized = finalize_completed_live_artifacts(root)
            _write_receipt(root, finalized, authorization)
            return _public_summary(finalized, resumed=True)
    finally:
        credentials.clear()
    preflight = run_provider_preflight(root, force=force)
    if preflight.get("required_routes_ready") is not True:
        return preflight
    return run_public_calibration(root, force=force)


def _completed_state_resumable(
    root: Path,
    state: Mapping[str, object],
    execution_commit: str,
) -> bool:
    prior_commit = state.get("execution_commit")
    if (
        not isinstance(prior_commit, str)
        or len(prior_commit) != 40
        or state.get("preflight_complete") is not True
        or state.get("calibration_complete") is not True
        or not (root / CALIBRATION_RELATIVE).is_file()
        or not (root / TRACE_RELATIVE).is_file()
    ):
        return False
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", prior_commit, execution_commit],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def finalize_completed_live_artifacts(root: Path) -> dict[str, object]:
    """Reconcile already-recorded public usage without making provider calls."""
    state = _read_yaml(root / STATE_RELATIVE)
    calibration = _read_yaml(root / CALIBRATION_RELATIVE)
    if state.get("calibration_complete") is not True or calibration.get("status") != "pass":
        raise PermissionError("completed public calibration is required")

    route_results = calibration.get("route_results")
    routes = state.get("routes")
    if not isinstance(route_results, Mapping) or not isinstance(routes, Mapping):
        raise ValueError("completed calibration route records are missing")
    finalized_routes = {str(key): dict(value) for key, value in routes.items()}
    for route_id in ("openai_direct", "anthropic_direct"):
        result = route_results.get(route_id)
        route = finalized_routes.get(route_id)
        if not isinstance(result, Mapping) or not isinstance(route, dict):
            raise ValueError(f"required calibration route is missing: {route_id}")
        route["calibration_complete"] = True
        route["calibration_summary"] = {
            key: result.get(key)
            for key in (
                "cases",
                "calls",
                "input_tokens",
                "output_tokens",
                "cost_usd",
                "method_a_b_agreement",
                "protocol_compliance",
            )
        }
    state["routes"] = finalized_routes
    state["trace_usage_reconciled"] = True
    calibration["trace_usage_reconciled"] = True
    calibration["trace_usage_granularity"] = "per-public-case-and-preflight-task"
    _reconcile_trace_usage(root / TRACE_RELATIVE, state, calibration)
    _write_yaml(root / CALIBRATION_RELATIVE, calibration)
    _write_yaml(root / STATE_RELATIVE, state)
    _write_readiness(root, state)
    return state


def _reconcile_trace_usage(
    path: Path,
    state: Mapping[str, object],
    calibration: Mapping[str, object],
) -> None:
    route_results = calibration.get("route_results")
    assert isinstance(route_results, Mapping)
    case_usage: dict[tuple[str, int, str], dict[str, object]] = {}
    for route_id, result in route_results.items():
        if not isinstance(result, Mapping):
            continue
        records = result.get("case_records")
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, Mapping):
                continue
            method_a = record.get("method_a")
            if not isinstance(method_a, Mapping):
                continue
            case_usage[
                (
                    str(route_id),
                    int(record["task_index"]),
                    str(record["architecture"]),
                )
            ] = {
                key: method_a.get(key)
                for key in ("calls", "input_tokens", "output_tokens", "cost_usd")
            }

    routes = state.get("routes")
    assert isinstance(routes, Mapping)
    tiny_usage: dict[str, dict[str, object]] = {}
    for route_id, route in routes.items():
        if not isinstance(route, Mapping):
            continue
        metrics = route.get("tiny_public_task_metrics")
        if isinstance(metrics, Mapping):
            tiny_usage[str(route_id)] = {
                key: metrics.get(key)
                for key in ("calls", "input_tokens", "output_tokens", "cost_usd")
            }

    reconciled: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        route_id = str(record.get("route_id"))
        if record.get("stage") == "public-calibration":
            usage = case_usage.get(
                (
                    route_id,
                    int(record["task_index"]),
                    str(record["architecture"]),
                )
            )
            source = "public-calibration-case-record-method-a"
        else:
            usage = tiny_usage.get(route_id)
            source = "provider-preflight-route-metrics"
        if usage is None:
            raise ValueError("trace usage reconciliation record is missing")
        record["registered_usage_totals"] = {
            **usage,
            "granularity": "trace-run-total",
            "source": source,
        }
        reconciled.append(json.dumps(_serializable(record), sort_keys=True, separators=(",", ":")))
    _write_text(path, "\n".join(reconciled) + "\n")


def _load_live_context(
    root: Path, *, require_clean_execution: bool
) -> tuple[
    CredentialSet,
    PreflightAuthorization,
    CostLedger,
    HttpTransport,
    str,
]:
    branch = _git(root, "branch", "--show-current")
    if branch != BRANCH:
        raise PermissionError("live execution branch does not match authorization")
    execution_commit = _git(root, "rev-parse", "HEAD")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", STARTING_MAIN_SHA, execution_commit],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    if require_clean_execution:
        subprocess.run(
            ["git", "diff", "--quiet", "--", *EXECUTION_PATHS],
            cwd=root,
            check=True,
        )
        subprocess.run(
            ["git", "diff", "--cached", "--quiet", "--", *EXECUTION_PATHS],
            cwd=root,
            check=True,
        )
    authorization = load_preflight_authorization(
        _authorization_path(),
        expected_base_commit=STARTING_MAIN_SHA,
        expected_branch=BRANCH,
    )
    credentials = load_credentials(root / ".env.txt", explicit_live_mode=True)
    return (
        credentials,
        authorization,
        CostLedger(authorization),
        UrllibTransport(),
        execution_commit,
    )


def _authorization_path() -> Path:
    config_root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return config_root / "distributed-discovery" / AUTHORIZATION_FILENAME


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _discover_routes(
    *,
    credentials: CredentialSet,
    authorization: PreflightAuthorization,
    ledger: CostLedger,
    transport: HttpTransport,
) -> tuple[list[RouteSpec], dict[str, object]]:
    routes: list[RouteSpec] = []
    if credentials.configured["OPENAI_API_KEY"]:
        routes.append(
            RouteSpec(
                "openai_direct",
                "openai_direct",
                "OPENAI_API_KEY",
                OPENAI_MANIFEST.exact_snapshot,
                True,
                True,
                True,
            )
        )
    if credentials.configured["ANTHROPIC_API_KEY"]:
        routes.append(
            RouteSpec(
                "anthropic_direct",
                "anthropic_direct",
                "ANTHROPIC_API_KEY",
                ANTHROPIC_MANIFEST.exact_snapshot,
                True,
                True,
                True,
            )
        )
    audit_routes: list[dict[str, object]] = []
    if credentials.configured["OPENROUTER_API_KEY"]:
        api_key = credentials.get_secret("OPENROUTER_API_KEY")
        assert api_key is not None
        for route_id, slug in (
            ("openrouter_mistral_small_3_1", OPENROUTER_MISTRAL_MODEL),
            ("openrouter_gemini_2_5_pro", OPENROUTER_GEMINI_MODEL),
        ):
            try:
                endpoints = discover_openrouter_endpoints(
                    api_key=api_key,
                    model_slug=slug,
                    transport=transport,
                    network_enabled=True,
                )
                selected = select_openrouter_endpoint(endpoints)
                audit_routes.append(
                    {
                        "route_id": route_id,
                        "model_slug": slug,
                        "endpoint_discovery_status": "pass",
                        "endpoints": [endpoint.public_record() for endpoint in endpoints],
                        "selected_endpoint": (
                            selected.public_record() if selected is not None else None
                        ),
                        "fallbacks_disabled": True,
                        "require_parameters": True,
                        "data_collection": "deny",
                        "zdr_required": True,
                        "max_price_frozen": selected is not None,
                    }
                )
                if selected is not None:
                    routes.append(
                        RouteSpec(
                            route_id,
                            "openrouter",
                            "OPENROUTER_API_KEY",
                            slug,
                            False,
                            False,
                            False,
                            selected,
                        )
                    )
            except Exception as exc:
                audit_routes.append(
                    {
                        "route_id": route_id,
                        "model_slug": slug,
                        "endpoint_discovery_status": "fail",
                        "failure_class": _safe_failure(exc),
                        "endpoints": [],
                        "selected_endpoint": None,
                    }
                )
        del api_key
    audit = {
        "schema_version": "agents-v1-openrouter-route-audit-v1",
        "classification": "public-operational-route-audit-not-campaign-amendment",
        "audit_utc": _now(),
        "gateway": "openrouter",
        "credential_configured": credentials.configured["OPENROUTER_API_KEY"],
        "routes": audit_routes,
        "model_family_diversity": len(audit_routes) == 2,
        "gateway_diversity": False,
        "campaign_manifest_authorizes_openrouter": False,
        "route_amendment_decision": "optional-public-calibration-only",
        "authorization_call_ceiling": authorization.max_total_calls,
        "calls_recorded_before_generations": ledger.calls_made,
    }
    return routes, audit


def _adapter_for(
    spec: RouteSpec,
    *,
    credentials: CredentialSet,
    ledger: CostLedger,
    transport: HttpTransport,
) -> AgentAdapter:
    key = credentials.get_secret(spec.credential_name)
    if key is None:
        raise PermissionError("configured route lacks its credential")
    common = {
        "api_key": key,
        "transport": transport,
        "network_enabled": True,
        "ledger": ledger,
    }
    if spec.route_id == "openai_direct":
        return OpenAIResponsesAdapter(**common)
    if spec.route_id == "anthropic_direct":
        return AnthropicMessagesAdapter(**common)
    if spec.gateway_id == "openrouter" and spec.endpoint is not None:
        return OpenRouterAdapter(
            model_slug=spec.model_slug,
            route_id=spec.route_id,
            endpoint=spec.endpoint,
            **common,
        )
    raise PermissionError("route adapter is not implemented")


def _run_route_preflight(
    spec: RouteSpec, adapter: AgentAdapter
) -> tuple[dict[str, object], list[dict[str, object]]]:
    task = generate_public_calibration()[2]
    agent_id = sorted(task.capabilities)[0]
    prompt = compile_prompt(task, agent_id, architecture_id="provider-native-smoke")
    request = AdapterRequest(
        prompt=prompt,
        manifest=adapter.manifest,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        max_output_tokens=256,
        final_required=True,
    )
    response = adapter.respond(request)
    retry_count = 0
    validation_errors: list[str] = []
    if response.error_class is None:
        try:
            parse_action(
                response.raw_output,
                task_commitment=task.commitment,
                agent_id=agent_id,
                round_number=0,
                action_vocabulary=task.action_vocabulary,
                source_vocabulary=task.source_vocabulary,
                final_required=True,
            )
        except ValueError as exc:
            validation_errors.append(str(exc))
            retry_count = 1
            response = adapter.respond(
                replace(
                    request,
                    schema_retry=True,
                    repair_errors=tuple(validation_errors),
                )
            )
            if response.error_class is None:
                try:
                    parse_action(
                        response.raw_output,
                        task_commitment=task.commitment,
                        agent_id=agent_id,
                        round_number=0,
                        action_vocabulary=task.action_vocabulary,
                        source_vocabulary=task.source_vocabulary,
                        final_required=True,
                    )
                except ValueError as retry_exc:
                    validation_errors.append(str(retry_exc))
    if response.error_class is not None:
        validation_errors.append(response.error_class)
    smoke_pass = not validation_errors
    if not smoke_pass:
        return (
            {
                **spec.public_record(),
                "credential_configured": True,
                "credential_valid": response.error_class != "authentication",
                "account_or_project_access": response.error_class
                not in {"authentication", "billing-or-account-access"},
                "exact_model_access": response.error_class
                not in {"authentication", "billing-or-account-access", "exact-model-access"},
                "returned_upstream_provider_matches": response.operational_metadata.get(
                    "returned_upstream_provider_matches"
                ),
                "fallbacks_disabled": spec.gateway_id != "openrouter"
                or response.operational_metadata.get("fallbacks_disabled") is True,
                "data_policy_eligible": spec.gateway_id != "openrouter",
                "zdr_eligible": spec.gateway_id != "openrouter",
                "structured_output_supported": False,
                "provider_adapter_supported": True,
                "public_task_end_to_end_passed": False,
                "usage_metadata_available": response.usage.input_tokens > 0,
                "cost_accounting_available": response.usage.cost_usd >= 0,
                "retention_policy_eligible": spec.campaign_eligible,
                "snapshot_policy_eligible": True,
                "calibration_complete": False,
                "schema_retry_count": retry_count,
                "failure_class": response.error_class or "schema",
                "outcome": (
                    "credential-failed"
                    if response.error_class == "authentication"
                    else "structured-output-failed"
                ),
            },
            [],
        )
    run = run_architecture(task, "isolated-private-agents", adapter)
    method_a = evaluate_run(task, run).serializable()
    method_b = _serializable(reconstruct_metrics(task, run))
    agreement = method_a == method_b
    trace = build_trace(run)
    e2e_pass = not run.protocol_errors and agreement
    metadata = response.operational_metadata
    return (
        {
            **spec.public_record(),
            "credential_configured": True,
            "credential_valid": True,
            "account_or_project_access": True,
            "exact_model_access": True,
            "returned_upstream_provider_matches": metadata.get(
                "returned_upstream_provider_matches", True
            ),
            "fallbacks_disabled": metadata.get("fallbacks_disabled", True),
            "data_policy_eligible": True,
            "zdr_eligible": spec.gateway_id != "openrouter"
            or metadata.get("returned_upstream_provider_matches") is True,
            "structured_output_supported": True,
            "provider_adapter_supported": True,
            "public_task_end_to_end_passed": e2e_pass,
            "usage_metadata_available": response.usage.input_tokens > 0,
            "cost_accounting_available": response.usage.cost_usd >= 0,
            "retention_policy_eligible": spec.campaign_eligible,
            "snapshot_policy_eligible": True,
            "calibration_complete": False,
            "schema_retry_count": retry_count,
            "method_a_b_agreement": agreement,
            "tiny_public_task_metrics": method_a,
            "failure_class": None if e2e_pass else "adapter-boundary-failure",
            "outcome": "ready" if e2e_pass else "adapter-failed",
        },
        [
            {
                "stage": "tiny-public-task",
                "route_id": spec.route_id,
                "task_index": 2,
                "architecture": "isolated-private-agents",
                "trace": trace.redacted,
                "audit": trace.audit,
            }
        ],
    )


def _run_calibration_route(
    spec: RouteSpec,
    adapter: AgentAdapter,
    tasks: Sequence[TaskInstance],
) -> tuple[str, dict[str, object], list[dict[str, object]], list[str]]:
    cases: list[dict[str, object]] = []
    traces: list[dict[str, object]] = []
    visible_outputs: list[str] = []
    route_agreement = True
    route_protocol = True
    route_calls = 0
    route_input_tokens = 0
    route_output_tokens = 0
    route_cost = Decimal("0")
    try:
        for task_index, task in enumerate(tasks):
            for architecture in ARCHITECTURES:
                run = run_architecture(task, architecture, adapter)
                method_a = evaluate_run(task, run).serializable()
                method_b = _serializable(reconstruct_metrics(task, run))
                route_calls += int(str(method_a["calls"]))
                route_input_tokens += int(str(method_a["input_tokens"]))
                route_output_tokens += int(str(method_a["output_tokens"]))
                route_cost += Decimal(str(method_a["cost_usd"]))
                agreement = method_a == method_b
                route_agreement = route_agreement and agreement
                route_protocol = route_protocol and not run.protocol_errors
                trace = build_trace(run)
                events = trace.redacted.get("events")
                if isinstance(events, Sequence):
                    for event in events:
                        if isinstance(event, Mapping):
                            visible = event.get("visible_output")
                            if isinstance(visible, str):
                                visible_outputs.append(visible)
                traces.append(
                    {
                        "stage": "public-calibration",
                        "route_id": spec.route_id,
                        "task_index": task_index,
                        "architecture": architecture,
                        "trace": trace.redacted,
                        "audit": trace.audit,
                    }
                )
                cases.append(
                    {
                        "task_index": task_index,
                        "task_commitment": f"sha256:{task.commitment}",
                        "family_id": task.family_id,
                        "architecture": architecture,
                        "method_a": method_a,
                        "method_b": method_b,
                        "method_a_b_agree": agreement,
                        "protocol_errors": list(run.protocol_errors),
                        "trace_hash": trace.redacted["redacted_trace_hash"],
                    }
                )
    finally:
        _clear_adapter(adapter)
    return (
        spec.route_id,
        {
            "cases": len(cases),
            "calls": route_calls,
            "method_a_b_agreement": route_agreement,
            "protocol_compliance": route_protocol,
            "input_tokens": route_input_tokens,
            "output_tokens": route_output_tokens,
            "cost_usd": str(route_cost),
            "case_records": cases,
        },
        traces,
        visible_outputs,
    )


def _calibration_plan(
    routes: Sequence[RouteSpec],
    authorization: PreflightAuthorization,
    ledger: CostLedger,
) -> dict[str, object]:
    initial_calls_per_route = 294
    maximum_schema_retry_calls_per_route = 294
    maximum_calls_per_route = initial_calls_per_route + maximum_schema_retry_calls_per_route
    if maximum_calls_per_route > authorization.max_calls_per_route:
        raise PermissionError("registered calibration exceeds the route call ceiling")
    prices = {
        "openai_direct": (Decimal("2.50"), Decimal("15.00")),
        "anthropic_direct": (Decimal("3.00"), Decimal("15.00")),
    }
    route_plan: dict[str, object] = {}
    total_maximum = Decimal("0")
    for route in routes:
        input_price, output_price = prices[route.route_id]
        maximum = (
            Decimal(maximum_calls_per_route * 1_000) * input_price
            + Decimal(maximum_calls_per_route * 256) * output_price
        ) / Decimal(1_000_000)
        spent = ledger.route_costs_usd.get(route.route_id, Decimal("0"))
        cap = authorization.route_caps_usd.get(
            route.route_id, authorization.gateway_caps_usd[route.gateway_id]
        )
        if spent + maximum > cap:
            raise PermissionError("projected calibration cost exceeds a route cap")
        route_plan[route.route_id] = {
            "cases": 50,
            "initial_calls": initial_calls_per_route,
            "maximum_schema_retry_calls": maximum_schema_retry_calls_per_route,
            "maximum_calls": maximum_calls_per_route,
            "input_token_ceiling_per_call": 1_000,
            "output_token_ceiling_per_call": 256,
            "maximum_incremental_cost_usd": str(maximum),
            "remaining_route_cap_before_calibration_usd": str(cap - spent),
        }
        total_maximum += maximum
    if ledger.total_cost_usd + total_maximum > authorization.total_cap_usd:
        raise PermissionError("projected calibration cost exceeds the total cap")
    return {
        "deterministic_prefix": "all-10-public-tasks-all-5-architectures",
        "routes": route_plan,
        "maximum_incremental_cost_usd": str(total_maximum),
        "authorization_margin_usd": str(
            authorization.total_cap_usd - ledger.total_cost_usd - total_maximum
        ),
        "maximum_live_concurrency": min(
            authorization.max_live_concurrency,
            len(routes),
        ),
    }


def _routes_from_state(state: Mapping[str, object]) -> list[RouteSpec]:
    raw_routes = state.get("routes")
    if not isinstance(raw_routes, Mapping):
        return []
    routes: list[RouteSpec] = []
    for route_id in ("openai_direct", "anthropic_direct"):
        record = raw_routes.get(route_id)
        if not isinstance(record, Mapping):
            continue
        routes.append(
            RouteSpec(
                route_id=route_id,
                gateway_id=str(record["gateway_id"]),
                credential_name=str(record["credential_variable_name"]),
                model_slug=str(record["model_slug"]),
                required=bool(record["required_for_selected_campaign"]),
                campaign_selected=bool(record["campaign_selected"]),
                campaign_eligible=bool(record["campaign_eligible"]),
            )
        )
    return routes


def _restore_ledger(ledger: CostLedger, value: object) -> None:
    if not isinstance(value, Mapping):
        return
    ledger.total_cost_usd = Decimal(str(value.get("total_cost_usd", "0")))
    ledger.calls_made = int(value.get("calls_made", 0))
    route_costs = value.get("route_costs_usd")
    route_calls = value.get("route_calls")
    if isinstance(route_costs, Mapping):
        ledger.route_costs_usd = {str(key): Decimal(str(item)) for key, item in route_costs.items()}
    if isinstance(route_calls, Mapping):
        ledger.route_calls = {str(key): int(item) for key, item in route_calls.items()}


def _restore_prior_attempt_ledger(
    root: Path,
    ledger: CostLedger,
    existing: Mapping[str, object],
) -> None:
    if existing.get("ledger_cumulative_across_attempts") is True:
        _restore_ledger(ledger, existing.get("ledger"))
        return
    records: list[Mapping[str, object]] = []
    attempts = root / "reports/benchmark/agents-v1-preflight-attempts"
    if attempts.exists():
        records.extend(_read_yaml(path) for path in sorted(attempts.glob("*.yml")))
    if existing:
        records.append(existing)
    for record in records:
        value = record.get("ledger")
        if not isinstance(value, Mapping):
            continue
        ledger.calls_made += int(value.get("calls_made", 0))
        ledger.total_cost_usd += Decimal(str(value.get("total_cost_usd", "0")))
        route_costs = value.get("route_costs_usd")
        route_calls = value.get("route_calls")
        if isinstance(route_costs, Mapping):
            for key, item in route_costs.items():
                route_id = str(key)
                ledger.route_costs_usd[route_id] = ledger.route_costs_usd.get(
                    route_id, Decimal("0")
                ) + Decimal(str(item))
        if isinstance(route_calls, Mapping):
            for key, item in route_calls.items():
                route_id = str(key)
                ledger.route_calls[route_id] = ledger.route_calls.get(route_id, 0) + int(item)


def _ledger_record(ledger: CostLedger, authorization: PreflightAuthorization) -> dict[str, object]:
    return {
        "calls_made": ledger.calls_made,
        "route_calls": dict(sorted(ledger.route_calls.items())),
        "total_cost_usd": str(ledger.total_cost_usd),
        "route_costs_usd": {
            key: str(value) for key, value in sorted(ledger.route_costs_usd.items())
        },
        "total_cap_usd": str(authorization.total_cap_usd),
        "remaining_total_cap_usd": str(authorization.total_cap_usd - ledger.total_cost_usd),
    }


def _required_failure_decision(
    route_records: Mapping[str, object], required_configured: bool
) -> str:
    if not required_configured:
        return "required-provider-credential-failure"
    for route_id in ("openai_direct", "anthropic_direct"):
        record = route_records.get(route_id)
        if isinstance(record, Mapping):
            failure = record.get("failure_class")
            if failure == "authentication":
                return "required-provider-credential-failure"
            if failure == "exact-model-access":
                return "required-provider-model-access-failure"
            if failure in {"permission-or-policy", "returned-provider-mismatch"}:
                return "required-provider-policy-ineligible"
            if record.get("structured_output_supported") is False:
                return "structured-output-boundary-failure"
    return "adapter-boundary-failure"


def _write_route_audit(root: Path, audit: Mapping[str, object], execution_commit: str) -> None:
    document = {**audit, "execution_commit": execution_commit}
    _write_yaml(root / ROUTE_AUDIT_YML, document)
    routes = audit.get("routes")
    route_list = routes if isinstance(routes, Sequence) else []
    lines = [
        "# Agents v1 OpenRouter exact-route audit",
        "",
        "This is a public operational endpoint audit, not a campaign amendment "
        "or scientific result.",
        "",
        f"- Audit time: `{audit['audit_utc']}`",
        f"- Execution commit: `{execution_commit}`",
        "- Campaign manifest authorizes OpenRouter: `false`",
        "- Decision: `optional-public-calibration-only`",
        "- Model-family diversity: `true` when both route audits are present",
        "- Gateway diversity: `false`",
        "",
        "Every selected request pins one returned provider slug, disables fallback, requires "
        "structured-output parameters, denies data collection, requires ZDR, and freezes the "
        "returned endpoint price as a maximum.",
        "",
        "## Route results",
        "",
    ]
    for item in route_list:
        if not isinstance(item, Mapping):
            continue
        selected = item.get("selected_endpoint")
        selected_slug = selected.get("provider_slug") if isinstance(selected, Mapping) else "none"
        lines.extend(
            [
                f"### `{item.get('model_slug')}`",
                "",
                f"- Discovery: `{item.get('endpoint_discovery_status')}`",
                f"- Selected exact provider slug: `{selected_slug}`",
                f"- Endpoints returned: `{len(item.get('endpoints', []))}`",
                "",
            ]
        )
    _write_text(root / ROUTE_AUDIT_MD, "\n".join(lines))
    _write_yaml(
        root / ROUTE_AMENDMENT,
        {
            "schema_version": "agents-v1-openrouter-route-amendment-v1",
            "decision": "optional-public-calibration-only",
            "decision_utc": audit["audit_utc"],
            "execution_commit": execution_commit,
            "campaign_manifest_changed": False,
            "sealed_pilot_authorized": False,
            "base_campaign_authorized": False,
            "openrouter_gateway_count": 1,
            "model_family_diversity": True,
            "gateway_diversity": False,
            "reason": (
                "The frozen campaign manifest selects direct OpenAI and Anthropic. "
                "OpenRouter routes remain optional public engineering calibrations and "
                "cannot satisfy direct gateway or local/open requirements."
            ),
        },
    )


def _write_readiness(root: Path, state: Mapping[str, object]) -> None:
    _write_yaml(
        root / READINESS_RELATIVE,
        {
            "schema_version": "agents-v1-provider-readiness-v1",
            "classification": "public-operational-not-scientific-evidence",
            "overall_decision": state.get("overall_decision"),
            "execution_commit": state.get("execution_commit"),
            "authorization_id": state.get("authorization_id"),
            "configured_credentials": state.get("configured_credentials"),
            "unused_credential_names_present": state.get("unused_credential_names_present"),
            "routes": state.get("routes"),
            "ledger": state.get("ledger"),
            "public_tasks_only": True,
            "private_material_exists": False,
            "scientific_evidence_exists": False,
            "provider_ranking_created": False,
            "composite_score_created": False,
            "updated_utc": state.get("updated_utc"),
        },
    )


def _write_receipt(
    root: Path,
    state: Mapping[str, object],
    authorization: PreflightAuthorization,
) -> None:
    ledger = state.get("ledger")
    _write_yaml(
        root / RECEIPT_RELATIVE,
        {
            "schema_version": "agents-v1-provider-cost-receipt-v1",
            "classification": "redacted-public-operational-receipt",
            "authorization_id": authorization.authorization_id,
            "authorized_base_commit": STARTING_MAIN_SHA,
            "execution_commit": state.get("execution_commit"),
            "branch": BRANCH,
            "issue": ISSUE,
            "authorization_expiration": authorization.expires_utc.isoformat().replace(
                "+00:00", "Z"
            ),
            "total_cap_usd": str(authorization.total_cap_usd),
            "gateway_caps_usd": {
                key: str(value) for key, value in sorted(authorization.gateway_caps_usd.items())
            },
            "route_caps_usd": {
                key: str(value) for key, value in sorted(authorization.route_caps_usd.items())
            },
            "ledger": ledger,
            "stop_reason": state.get("overall_decision"),
            "credential_data_present": False,
            "private_data_present": False,
            "scientific_evidence_created": False,
            "updated_utc": state.get("updated_utc"),
        },
    )


def _append_traces(path: Path, records: Sequence[Mapping[str, object]]) -> None:
    if not records:
        return
    existing: list[str] = []
    if path.exists():
        existing = path.read_text(encoding="utf-8").splitlines()
    rendered = existing + [
        json.dumps(_serializable(record), sort_keys=True, separators=(",", ":"))
        for record in records
    ]
    _write_text(path, "\n".join(rendered) + "\n")


def _read_yaml(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    loaded: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    return dict(loaded) if isinstance(loaded, Mapping) else {}


def _write_yaml(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(
        _serializable(value),
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )
    path.write_text(rendered, encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _serializable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serializable(item) for item in value]
    if isinstance(value, (Decimal, Fraction)):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    return value


def _clear_adapter(adapter: AgentAdapter) -> None:
    clear = getattr(adapter, "clear_secret", None)
    if callable(clear):
        clear()


def _safe_failure(exc: Exception) -> str:
    message = str(exc)
    allowed = {
        "authentication",
        "billing-or-account-access",
        "permission-or-policy",
        "exact-model-access",
        "timeout",
        "rate-limit",
        "transient-provider",
        "transient-transport",
        "invalid-provider-json",
        "invalid-endpoint-discovery-response",
        "endpoint-discovery-failed",
        "schema-or-parameter",
        "returned-provider-mismatch",
    }
    return message if message in allowed else type(exc).__name__


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _public_summary(state: Mapping[str, object], *, resumed: bool) -> dict[str, object]:
    return {
        "status": state.get("overall_decision"),
        "required_routes_ready": state.get("required_routes_ready"),
        "preflight_complete": state.get("preflight_complete"),
        "calibration_complete": state.get("calibration_complete"),
        "configured_credentials": state.get("configured_credentials"),
        "ledger": state.get("ledger"),
        "private_material_exists": False,
        "scientific_evidence_exists": False,
        "resumed_without_paid_calls": resumed,
    }
