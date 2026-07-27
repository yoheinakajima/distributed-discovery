"""Exact authorization-bound AO-0004 public provider-schema canary runner."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import jsonschema

from distributed_discovery.agent_ops.core import (
    GateObservation,
    authorization_challenge,
    collect_gate_observation,
    load_yaml,
    validate,
    validate_gate_surface,
)
from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    ModelManifest,
)
from distributed_discovery.benchmark.agents_v1.generation import generate_public_calibration
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CostLedger,
    PreflightAuthorization,
)
from distributed_discovery.benchmark.agents_v1.live_providers import (
    ANTHROPIC_MANIFEST,
    OPENAI_MANIFEST,
    AnthropicMessagesAdapter,
    HttpTransport,
    OpenAIResponsesAdapter,
    RoutePricing,
    UrllibTransport,
    build_anthropic_messages_payload,
    build_openai_responses_payload,
)
from distributed_discovery.benchmark.agents_v1.prompts import CompiledPrompt, compile_prompt
from distributed_discovery.benchmark.agents_v1.provider_schema import (
    ANTHROPIC_PROVIDER,
    EXPECTED_PUBLIC_CANARY_POLICY,
    OPENAI_PROVIDER,
    PublicCanaryPolicy,
    compile_anthropic_action_schema,
    compile_openai_action_schema,
    minimal_provider_schema,
    provider_bisection_matrix,
    schema_fingerprint,
    validate_action_semantics,
    validate_public_canary_policy,
)

TASK_ID = "AO-0004"
ISSUE_NUMBER = 198
PULL_REQUEST_NUMBER = 199
BRANCH = "benchmark/treasurebench-provider-schema-conformance"
R2_GATE_ID = "AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R2"
R2_GATE_RELATIVE = Path("reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r2.yml")
PUBLIC_LEDGER_RELATIVE = Path(
    "reports/benchmark/treasurebench-provider-schema-canaries/"
    "AO-0004-public-engineering-ledger.jsonl"
)
EXPECTED_COST_LIMIT_USD = Decimal("0.10")
MAX_OUTPUT_TOKENS = 128
LEDGER_VERSION = "treasurebench-provider-canary-ledger-v1"
_PROVIDERS = (OPENAI_PROVIDER, ANTHROPIC_PROVIDER)
_SAFE_ERROR_FIELDS = (
    "error_contract_version",
    "error_locus",
    "http_status",
    "retry_eligible",
    "provider_error_type",
    "provider_error_code",
    "rejected_parameter",
    "diagnostic_message_sha256",
)
_LEDGER_KEYS = frozenset(
    {
        "sequence",
        "previous_hash",
        "record_hash",
        "schema_version",
        "event_type",
        "recorded_at_utc",
        "task_id",
        "gate_id",
        "execution_commit",
        "canary_id",
        "provider",
        "route",
        "model",
        "schema_fingerprint",
        "schema_role",
        "intent_record_hash",
        "projected_max_cost_usd",
        "status",
        "input_tokens",
        "output_tokens",
        "cost_usd",
        "safe_error",
        "output_sha256",
        "stopping_decision",
        "calls",
        "total_cost_usd",
        "provider_cost_usd",
    }
)


@dataclass(frozen=True)
class RuntimeAuthorization:
    """Validated generic Agent Operations authorization and exact R2 gate."""

    gate: Mapping[str, object]
    contract: Mapping[str, object]
    authorization: Mapping[str, object]


@dataclass(frozen=True)
class CanarySpec:
    canary_id: str
    provider: str
    route: str
    model: str
    schema: Mapping[str, object]
    schema_role: str
    complete: bool = False
    minimal: bool = False
    bisection: bool = False


class OpaqueCredentialInputs:
    """Exactly two credential values with permanently redacted representation."""

    __slots__ = ("_values",)

    NAMES = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")

    def __init__(self, values: Mapping[str, str]) -> None:
        self._values = dict(values)

    def __repr__(self) -> str:
        return (
            "OpaqueCredentialInputs("
            "names=('OPENAI_API_KEY', 'ANTHROPIC_API_KEY'), values=<redacted>)"
        )

    @classmethod
    def load(cls, environment: Mapping[str, str]) -> OpaqueCredentialInputs:
        values: dict[str, str] = {}
        for name in cls.NAMES:
            value = environment.get(name)
            if not isinstance(value, str) or not value:
                raise PermissionError(f"required opaque credential is not configured: {name}")
            values[name] = value
        return cls(values)

    def get(self, name: str) -> str:
        if name not in self.NAMES:
            raise PermissionError("credential name is outside the exact AO-0004 allowlist")
        value = self._values.get(name)
        if not value:
            raise PermissionError(f"opaque credential is unavailable: {name}")
        return value

    def clear(self) -> None:
        for name in tuple(self._values):
            self._values[name] = ""
            del self._values[name]


class PublicEngineeringLedger:
    """Hash-chained append-only public metadata; raw outputs and errors are prohibited."""

    def __init__(self, path: Path, *, gate_id: str, execution_commit: str) -> None:
        self.path = path
        self.gate_id = gate_id
        self.execution_commit = execution_commit
        self.records = self._read_and_validate()

    def _read_and_validate(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        metadata = self.path.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise PermissionError("public canary ledger must be a regular non-symlink file")
        if stat.S_IMODE(metadata.st_mode) & 0o022:
            raise PermissionError("public canary ledger must not be group- or world-writable")
        records: list[dict[str, object]] = []
        previous = "GENESIS"
        for sequence, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            loaded = json.loads(line)
            if not isinstance(loaded, dict):
                raise ValueError("public canary ledger record must be an object")
            if set(loaded) - _LEDGER_KEYS:
                raise ValueError("public canary ledger contains an unsafe or unknown field")
            actual_hash = loaded.get("record_hash")
            unsigned = {key: value for key, value in loaded.items() if key != "record_hash"}
            expected_hash = _sha256_json(unsigned)
            if loaded.get("sequence") != sequence or loaded.get("previous_hash") != previous:
                raise ValueError("public canary ledger sequence or chain mismatch")
            if actual_hash != expected_hash:
                raise ValueError("public canary ledger record hash mismatch")
            if loaded.get("schema_version") != LEDGER_VERSION:
                raise ValueError("public canary ledger schema version mismatch")
            if loaded.get("task_id") != TASK_ID:
                raise ValueError("public canary ledger task mismatch")
            if loaded.get("gate_id") != self.gate_id:
                raise ValueError("public canary ledger gate mismatch")
            if loaded.get("execution_commit") != self.execution_commit:
                raise ValueError("public canary ledger execution commit mismatch")
            safe_error = loaded.get("safe_error")
            if safe_error is not None:
                if not isinstance(safe_error, Mapping):
                    raise ValueError("public canary ledger safe error must be an object")
                if set(safe_error) - set(_SAFE_ERROR_FIELDS):
                    raise ValueError("public canary ledger contains unsafe error fields")
            records.append(loaded)
            previous = str(actual_hash)
        return records

    def append(self, event: Mapping[str, object], *, now: datetime) -> Mapping[str, object]:
        record: dict[str, object] = {
            "sequence": len(self.records) + 1,
            "previous_hash": (str(self.records[-1]["record_hash"]) if self.records else "GENESIS"),
            "schema_version": LEDGER_VERSION,
            "event_type": str(event["event_type"]),
            "recorded_at_utc": now.astimezone(UTC).isoformat(),
            "task_id": TASK_ID,
            "gate_id": self.gate_id,
            "execution_commit": self.execution_commit,
            **{str(key): value for key, value in event.items() if key != "event_type"},
        }
        if set(record) - _LEDGER_KEYS:
            raise ValueError("attempted to append an unsafe public canary ledger field")
        record["record_hash"] = _sha256_json(record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            with os.fdopen(descriptor, "ab") as stream:
                stream.write(_canonical_json(record) + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
        except Exception:
            raise
        self.records.append(record)
        return record

    def intents(self) -> Mapping[str, Mapping[str, object]]:
        return {
            str(record["canary_id"]): record
            for record in self.records
            if record.get("event_type") == "call-intent"
        }

    def results(self) -> Mapping[str, Mapping[str, object]]:
        return {
            str(record["canary_id"]): record
            for record in self.records
            if record.get("event_type") == "call-result"
        }

    def open_intents(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.intents()) - set(self.results())))

    def totals(self) -> tuple[int, Decimal, Mapping[str, Decimal]]:
        results = self.results().values()
        total = sum((Decimal(str(record.get("cost_usd", "0"))) for record in results), Decimal())
        provider_cost = {
            provider: sum(
                (
                    Decimal(str(record.get("cost_usd", "0")))
                    for record in results
                    if record.get("provider") == provider
                ),
                Decimal(),
            )
            for provider in _PROVIDERS
        }
        return len(self.intents()), total, provider_cost

    def guard_next(self, spec: CanarySpec, *, projected_max_cost_usd: Decimal) -> None:
        if spec.canary_id in self.intents():
            raise PermissionError("public canary already has a committed call intent")
        calls, total, provider_cost = self.totals()
        policy = EXPECTED_PUBLIC_CANARY_POLICY
        provider_cap = (
            policy.openai_cap_usd if spec.provider == OPENAI_PROVIDER else policy.anthropic_cap_usd
        )
        if calls + 1 > policy.call_cap:
            raise PermissionError("public canary call cap would be exceeded")
        if total + projected_max_cost_usd > policy.hard_cap_usd:
            raise PermissionError("public canary hard spend cap would be exceeded")
        if provider_cost[spec.provider] + projected_max_cost_usd > provider_cap:
            raise PermissionError("public canary provider spend cap would be exceeded")
        if total + projected_max_cost_usd >= EXPECTED_COST_LIMIT_USD:
            raise PermissionError(
                "public canary expected aggregate cost must remain below USD 0.10"
            )


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_json(value: object) -> str:
    return f"sha256:{hashlib.sha256(_canonical_json(value)).hexdigest()}"


def _parse_time(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("authorization timestamp must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("authorization timestamp must be timezone aware")
    return parsed.astimezone(UTC)


def _authorization_digest(authorization: Mapping[str, object]) -> str:
    unsigned = {key: value for key, value in authorization.items() if key != "authorization_digest"}
    return _sha256_json(unsigned)


def _validate_exact_gate_caps(gate: Mapping[str, object]) -> None:
    expected_zero = {
        "currency": "USD",
        "spend": "0",
        "calls": 0,
        "category_spend": {"OpenAI": "0", "Anthropic": "0"},
    }
    expected_caps = {
        "currency": "USD",
        "spend": "1.00",
        "calls": 10,
        "category_spend": {"OpenAI": "0.50", "Anthropic": "0.50"},
    }
    if gate.get("cumulative_state") != expected_zero:
        raise PermissionError("AO-0004 gate must begin at zero calls and zero spend")
    if gate.get("hard_caps") != expected_caps or gate.get("remaining_caps") != expected_caps:
        raise PermissionError(
            "AO-0004 gate caps must be exactly ten calls, USD 1.00 total, and USD 0.50 per provider"
        )


def validate_runtime_authorization(
    *,
    repo: Path,
    gate: Mapping[str, object],
    contract: Mapping[str, object],
    authorization: Mapping[str, object],
    observation: GateObservation,
    issue_number: int,
    issue_state: str,
    now: datetime,
) -> RuntimeAuthorization:
    """Validate the exact generic gate, live GitHub surface, and R2 authorization."""
    gate_value = dict(gate)
    contract_value = dict(contract)
    authorization_value = dict(authorization)
    if gate_value.get("gate_id") != R2_GATE_ID:
        raise PermissionError("only the AO-0004 R2 owner gate is executable")
    if gate_value.get("issue") != ISSUE_NUMBER or issue_number != ISSUE_NUMBER:
        raise PermissionError("AO-0004 live issue identity mismatch")
    if issue_state != "OPEN":
        raise PermissionError("AO-0004 issue is not open")
    pull_request = gate_value.get("pull_request")
    if not isinstance(pull_request, Mapping) or pull_request.get("number") != PULL_REQUEST_NUMBER:
        raise PermissionError("AO-0004 pull request identity mismatch")
    if gate_value.get("branch") != BRANCH:
        raise PermissionError("AO-0004 branch identity mismatch")
    if gate_value.get("private_actions") != []:
        raise PermissionError("AO-0004 public canary gate must authorize no private action")
    _validate_exact_gate_caps(gate_value)
    validate_gate_surface(gate_value, contract_value, observation, root=repo)
    validate(authorization_value, "owner-authorization.schema.json")
    task_contract = gate_value.get("task_contract")
    if not isinstance(task_contract, Mapping):
        raise PermissionError("AO-0004 task contract binding is malformed")
    expected_fields = {
        "gate_id": gate_value["gate_id"],
        "issue": gate_value["issue"],
        "pull_request": pull_request["number"],
        "branch": gate_value["branch"],
        "commit": gate_value["commit"],
        "task_contract_sha256": task_contract["sha256"],
        "tree_hashes": gate_value["tree_hashes"],
        "expires_at_utc": gate_value["expires_at_utc"],
        "challenge": authorization_challenge(gate_value),
        "owner_confirmation_statements": gate_value["owner_confirmation_statements"],
    }
    for name, expected in expected_fields.items():
        if authorization_value.get(name) != expected:
            raise PermissionError(f"AO-0004 authorization mismatch: {name}")
    if authorization_value.get("authorization_digest") != _authorization_digest(
        authorization_value
    ):
        raise PermissionError("AO-0004 authorization digest mismatch")
    authorized_at = _parse_time(authorization_value["authorized_at_utc"])
    expires_at = _parse_time(authorization_value["expires_at_utc"])
    if authorized_at > now.astimezone(UTC) or now.astimezone(UTC) >= expires_at:
        raise PermissionError("AO-0004 authorization is not currently active")
    validate_public_canary_policy(PublicCanaryPolicy())
    return RuntimeAuthorization(gate_value, contract_value, authorization_value)


def _authorization_path(gate_id: str) -> Path:
    configured = os.environ.get("XDG_CONFIG_HOME")
    base = Path(configured) if configured else Path.home() / ".config"
    return base / "distributed-discovery" / "agent-ops" / "authorizations" / f"{gate_id}.yml"


def _live_issue(repo: Path) -> tuple[int, str]:
    raw = subprocess.run(
        (
            "gh",
            "issue",
            "view",
            str(ISSUE_NUMBER),
            "--repo",
            "yoheinakajima/distributed-discovery",
            "--json",
            "number,state",
        ),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    value = json.loads(raw)
    return int(value["number"]), str(value["state"])


def load_live_runtime_authorization(
    repo: Path,
    *,
    now: datetime | None = None,
) -> RuntimeAuthorization:
    """Load R2 only after validating the exact live branch, PR, and protected trees."""
    gate = load_yaml(repo / R2_GATE_RELATIVE)
    contract_path = gate.get("task_contract")
    if not isinstance(contract_path, Mapping):
        raise PermissionError("AO-0004 gate task contract is malformed")
    contract = load_yaml(repo / str(contract_path["path"]))
    observation = collect_gate_observation(dict(gate))
    issue_number, issue_state = _live_issue(repo)
    path = _authorization_path(R2_GATE_ID)
    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise PermissionError("AO-0004 authorization must be a regular non-symlink file")
    if stat.S_IMODE(metadata.st_mode) != 0o600:
        raise PermissionError("AO-0004 authorization mode must be 0600")
    try:
        path.resolve().relative_to(repo.resolve())
    except ValueError:
        pass
    else:
        raise PermissionError("AO-0004 authorization must remain outside Git")
    authorization = load_yaml(path)
    return validate_runtime_authorization(
        repo=repo,
        gate=gate,
        contract=contract,
        authorization=authorization,
        observation=observation,
        issue_number=issue_number,
        issue_state=issue_state,
        now=now or datetime.now(UTC),
    )


def _base_request(manifest: ModelManifest) -> AdapterRequest:
    task = generate_public_calibration()[2]
    agent_id = sorted(task.capabilities)[0]
    return AdapterRequest(
        prompt=compile_prompt(
            task,
            agent_id,
            architecture_id="provider-native-smoke",
            final_required=True,
        ),
        manifest=manifest,
        round_number=0,
        action_vocabulary=task.action_vocabulary,
        source_vocabulary=task.source_vocabulary,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        final_required=True,
    )


def frozen_canary_specs() -> tuple[CanarySpec, ...]:
    """Return the exact normal sequence followed by frozen provider bisection candidates."""
    openai_request = _base_request(OPENAI_MANIFEST)
    anthropic_request = _base_request(ANTHROPIC_MANIFEST)
    normal = (
        CanarySpec(
            "openai-minimal-known-valid",
            OPENAI_PROVIDER,
            "openai_direct",
            OPENAI_MANIFEST.exact_snapshot,
            minimal_provider_schema(OPENAI_PROVIDER),
            "minimal",
            minimal=True,
        ),
        CanarySpec(
            "openai-treasurebench-complete",
            OPENAI_PROVIDER,
            "openai_direct",
            OPENAI_MANIFEST.exact_snapshot,
            compile_openai_action_schema(openai_request),
            "complete",
            complete=True,
        ),
        CanarySpec(
            "anthropic-minimal-known-valid",
            ANTHROPIC_PROVIDER,
            "anthropic_direct",
            ANTHROPIC_MANIFEST.exact_snapshot,
            minimal_provider_schema(ANTHROPIC_PROVIDER),
            "minimal",
            minimal=True,
        ),
        CanarySpec(
            "anthropic-treasurebench-complete",
            ANTHROPIC_PROVIDER,
            "anthropic_direct",
            ANTHROPIC_MANIFEST.exact_snapshot,
            compile_anthropic_action_schema(anthropic_request),
            "complete",
            complete=True,
        ),
    )
    bisections: list[CanarySpec] = []
    for provider, request, route, model in (
        (
            OPENAI_PROVIDER,
            openai_request,
            "openai_direct",
            OPENAI_MANIFEST.exact_snapshot,
        ),
        (
            ANTHROPIC_PROVIDER,
            anthropic_request,
            "anthropic_direct",
            ANTHROPIC_MANIFEST.exact_snapshot,
        ),
    ):
        for item in provider_bisection_matrix(provider, request):
            schema = item["schema"]
            if not isinstance(schema, Mapping):
                raise TypeError("frozen bisection schema must be an object")
            bisections.append(
                CanarySpec(
                    str(item["canary_id"]),
                    provider,
                    route,
                    model,
                    schema,
                    "bisection",
                    bisection=True,
                )
            )
    return normal + tuple(bisections)


def _normal_specs() -> tuple[CanarySpec, ...]:
    return tuple(spec for spec in frozen_canary_specs() if not spec.bisection)


def _bisection_specs(provider: str) -> tuple[CanarySpec, ...]:
    return tuple(
        spec for spec in frozen_canary_specs() if spec.bisection and spec.provider == provider
    )


def next_canary_step(
    ledger: PublicEngineeringLedger,
) -> tuple[str, CanarySpec | None]:
    """Return the next exact call or a fail-closed terminal state."""
    specs = frozen_canary_specs()
    known_ids = {spec.canary_id for spec in specs}
    present_ids = set(ledger.intents()) | set(ledger.results())
    if present_ids - known_ids:
        raise ValueError("public canary ledger contains an unknown canary ID")
    open_intents = ledger.open_intents()
    if open_intents:
        return "manual-reconciliation-required-open-call-intent", None
    results = ledger.results()
    consumed: set[str] = set()
    for spec in _normal_specs():
        result = results.get(spec.canary_id)
        if result is None:
            if set(results) - consumed:
                raise ValueError("public canary ledger is outside the frozen sequence")
            return "call", spec
        consumed.add(spec.canary_id)
        if result.get("status") == "success":
            continue
        if spec.minimal:
            if set(results) - consumed:
                raise ValueError("records exist after a terminal minimal-schema failure")
            return "stopped-minimal-schema-failure", None
        for diagnostic in _bisection_specs(spec.provider):
            diagnostic_result = results.get(diagnostic.canary_id)
            if diagnostic_result is None:
                if set(results) - consumed:
                    raise ValueError("public canary bisection is outside the frozen order")
                return "call", diagnostic
            consumed.add(diagnostic.canary_id)
        if set(results) - consumed:
            raise ValueError("other-provider records exist after a complete-schema failure")
        return "stopped-complete-schema-failure-after-fixed-bisection", None
    if set(results) - consumed:
        raise ValueError("public canary ledger contains out-of-sequence bisection records")
    return "conformance-pass-both-complete-schemas", None


def _request_for_spec(spec: CanarySpec) -> AdapterRequest:
    manifest = OPENAI_MANIFEST if spec.provider == OPENAI_PROVIDER else ANTHROPIC_MANIFEST
    request = _base_request(manifest)
    if spec.complete:
        return request
    prompt = CompiledPrompt(
        task_commitment=request.prompt.task_commitment,
        agent_id=request.prompt.agent_id,
        system="Return exactly one JSON object matching the supplied public diagnostic schema.",
        user=json.dumps(
            {
                "public_canary": spec.canary_id,
                "purpose": "provider-schema-conformance-only",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        public_calibration=True,
    )
    return replace(request, prompt=prompt)


def _payload(spec: CanarySpec, request: AdapterRequest) -> Mapping[str, object]:
    if spec.provider == OPENAI_PROVIDER:
        return build_openai_responses_payload(request, schema=spec.schema)
    return build_anthropic_messages_payload(request, schema=spec.schema)


def _pricing(provider: str) -> RoutePricing:
    if provider == OPENAI_PROVIDER:
        return RoutePricing(Decimal("2.50"), Decimal("15.00"))
    return RoutePricing(Decimal("3.00"), Decimal("15.00"))


def _projected_max_cost(spec: CanarySpec, request: AdapterRequest) -> tuple[int, Decimal]:
    input_ceiling = len(_canonical_json(_payload(spec, request)))
    return input_ceiling, _pricing(spec.provider).maximum_call_cost(
        input_ceiling=input_ceiling,
        output_ceiling=request.max_output_tokens,
    )


def _preflight_cost_ledger(runtime: RuntimeAuthorization) -> CostLedger:
    gate = runtime.gate
    hard = gate["hard_caps"]
    assert isinstance(hard, Mapping)
    category = hard["category_spend"]
    assert isinstance(category, Mapping)
    authorization = PreflightAuthorization(
        authorization_id=R2_GATE_ID,
        authorized_base_commit=str(gate["commit"]),
        allowed_branch=BRANCH,
        expires_utc=_parse_time(gate["expires_at_utc"]),
        total_cap_usd=Decimal(str(hard["spend"])),
        gateway_caps_usd={
            "openai_direct": Decimal(str(category["OpenAI"])),
            "anthropic_direct": Decimal(str(category["Anthropic"])),
        },
        route_caps_usd={
            "openai_direct": Decimal(str(category["OpenAI"])),
            "anthropic_direct": Decimal(str(category["Anthropic"])),
        },
        max_calls_per_route=int(hard["calls"]),
        max_total_calls=int(hard["calls"]),
        max_live_concurrency=1,
        private_tasks_allowed=False,
        scientific_evidence_allowed=False,
        raw={},
    )
    ledger = CostLedger(authorization)
    return ledger


def _restore_cost_ledger(
    target: CostLedger,
    public_ledger: PublicEngineeringLedger,
) -> None:
    for result in public_ledger.results().values():
        cost = Decimal(str(result.get("cost_usd", "0")))
        route = str(result["route"])
        target.calls_made += 1
        target.total_cost_usd += cost
        target.route_calls[route] = target.route_calls.get(route, 0) + 1
        target.route_costs_usd[route] = target.route_costs_usd.get(route, Decimal()) + cost


def _safe_error(response: AdapterResponse) -> Mapping[str, object]:
    return {field: response.operational_metadata.get(field) for field in _SAFE_ERROR_FIELDS}


def _diagnostic_hash(error: Exception) -> str:
    bounded = str(error)[:4096].encode("utf-8", errors="replace")
    return f"sha256:{hashlib.sha256(bounded).hexdigest()}"


def _result_status(
    spec: CanarySpec,
    request: AdapterRequest,
    response: AdapterResponse,
) -> tuple[str, Mapping[str, object]]:
    if response.error_class is not None:
        return "error", _safe_error(response)
    metadata = response.operational_metadata
    if (
        metadata.get("gateway") != spec.route
        or metadata.get("route_id") != spec.route
        or metadata.get("model") != spec.model
    ):
        return (
            "invalid",
            {
                **_safe_error(response),
                "diagnostic_message_sha256": _diagnostic_hash(
                    ValueError("provider route or model identity mismatch")
                ),
            },
        )
    try:
        parsed = json.loads(response.raw_output)
        jsonschema.validate(parsed, spec.schema)
        if spec.complete:
            validate_action_semantics(response.raw_output, request)
    except (ValueError, jsonschema.ValidationError) as error:
        return (
            "invalid",
            {
                **_safe_error(response),
                "diagnostic_message_sha256": _diagnostic_hash(error),
            },
        )
    return "success", _safe_error(response)


def _stopping_decision(spec: CanarySpec, status: str) -> str:
    if status == "success":
        if spec.canary_id == "anthropic-treasurebench-complete":
            return "declare-conformance-both-complete-schemas-pass"
        if spec.bisection:
            return (
                "continue-fixed-same-provider-bisection"
                if spec.canary_id.endswith("action-cardinality")
                else "stop-complete-schema-failure-after-fixed-bisection"
            )
        return "continue-frozen-sequence"
    if spec.minimal:
        return "stop-minimal-schema-failure"
    if spec.complete:
        return "begin-fixed-same-provider-bisection"
    if spec.canary_id.endswith("action-cardinality"):
        return "continue-fixed-same-provider-bisection"
    return "stop-complete-schema-failure-after-fixed-bisection"


def _append_terminal_decision(
    ledger: PublicEngineeringLedger,
    *,
    status: str,
    now: datetime,
) -> None:
    if any(
        record.get("event_type") == "run-decision" and record.get("stopping_decision") == status
        for record in ledger.records
    ):
        return
    calls, total, provider_cost = ledger.totals()
    ledger.append(
        {
            "event_type": "run-decision",
            "status": "pass" if status.startswith("conformance-pass") else "stopped",
            "stopping_decision": status,
            "calls": calls,
            "total_cost_usd": str(total),
            "provider_cost_usd": {
                provider: str(provider_cost[provider]) for provider in _PROVIDERS
            },
        },
        now=now,
    )


def run_provider_schema_canaries(
    repo: Path,
    *,
    runtime: RuntimeAuthorization | None = None,
    transport: HttpTransport | None = None,
    environment: Mapping[str, str] | None = None,
    ledger_path: Path | None = None,
    now: datetime | None = None,
) -> Mapping[str, object]:
    """Run or resume only the exact R2-authorized public schema canaries."""
    timestamp = now or datetime.now(UTC)
    active = runtime or load_live_runtime_authorization(repo, now=timestamp)
    gate_id = str(active.gate["gate_id"])
    execution_commit = str(active.gate["commit"])
    path = ledger_path or repo / PUBLIC_LEDGER_RELATIVE
    if runtime is None and path.resolve() != (repo / PUBLIC_LEDGER_RELATIVE).resolve():
        raise PermissionError("live AO-0004 runner ledger path is frozen")
    ledger = PublicEngineeringLedger(
        path,
        gate_id=gate_id,
        execution_commit=execution_commit,
    )
    state, spec = next_canary_step(ledger)
    if spec is None:
        if not state.startswith("manual-reconciliation"):
            _append_terminal_decision(ledger, status=state, now=timestamp)
        calls, total, provider_cost = ledger.totals()
        return {
            "status": state,
            "ledger": str(path),
            "calls": calls,
            "cost_usd": str(total),
            "provider_cost_usd": {
                provider: str(provider_cost[provider]) for provider in _PROVIDERS
            },
            "credentials_loaded": False,
            "private_state_created": False,
            "scientific_state_created": False,
        }

    credentials = OpaqueCredentialInputs.load(
        environment if environment is not None else os.environ
    )
    cost_ledger = _preflight_cost_ledger(active)
    _restore_cost_ledger(cost_ledger, ledger)
    live_transport = transport or UrllibTransport()
    adapters: list[OpenAIResponsesAdapter | AnthropicMessagesAdapter] = []
    try:
        while spec is not None:
            request = _request_for_spec(spec)
            input_ceiling, projected = _projected_max_cost(spec, request)
            ledger.guard_next(spec, projected_max_cost_usd=projected)
            intent = ledger.append(
                {
                    "event_type": "call-intent",
                    "canary_id": spec.canary_id,
                    "provider": spec.provider,
                    "route": spec.route,
                    "model": spec.model,
                    "schema_fingerprint": schema_fingerprint(spec.schema),
                    "schema_role": spec.schema_role,
                    "projected_max_cost_usd": str(projected),
                    "stopping_decision": "pending-provider-response",
                },
                now=timestamp,
            )
            if spec.provider == OPENAI_PROVIDER:
                adapter: OpenAIResponsesAdapter | AnthropicMessagesAdapter = OpenAIResponsesAdapter(
                    api_key=credentials.get("OPENAI_API_KEY"),
                    transport=live_transport,
                    network_enabled=True,
                    ledger=cost_ledger,
                    input_token_ceiling=input_ceiling,
                )
            else:
                adapter = AnthropicMessagesAdapter(
                    api_key=credentials.get("ANTHROPIC_API_KEY"),
                    transport=live_transport,
                    network_enabled=True,
                    ledger=cost_ledger,
                    input_token_ceiling=input_ceiling,
                )
            adapters.append(adapter)
            try:
                response = adapter.respond_with_schema(request, schema=spec.schema)
            finally:
                adapter.clear_secret()
            status, safe_error = _result_status(spec, request, response)
            prior_total = ledger.totals()[1]
            actual_cost = response.usage.cost_usd
            if actual_cost > projected or prior_total + actual_cost >= EXPECTED_COST_LIMIT_USD:
                status = "invalid"
                safe_error = {
                    **safe_error,
                    "diagnostic_message_sha256": _diagnostic_hash(
                        ValueError("provider usage exceeded the frozen projected cost boundary")
                    ),
                }
            ledger.append(
                {
                    "event_type": "call-result",
                    "canary_id": spec.canary_id,
                    "provider": spec.provider,
                    "route": spec.route,
                    "model": spec.model,
                    "schema_fingerprint": schema_fingerprint(spec.schema),
                    "schema_role": spec.schema_role,
                    "intent_record_hash": str(intent["record_hash"]),
                    "status": status,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cost_usd": str(actual_cost),
                    "safe_error": dict(safe_error),
                    "output_sha256": (
                        f"sha256:{hashlib.sha256(response.raw_output.encode()).hexdigest()}"
                        if status == "success"
                        else None
                    ),
                    "stopping_decision": _stopping_decision(spec, status),
                },
                now=timestamp,
            )
            state, spec = next_canary_step(ledger)
        _append_terminal_decision(ledger, status=state, now=timestamp)
    finally:
        for adapter in adapters:
            adapter.clear_secret()
        credentials.clear()
    calls, total, provider_cost = ledger.totals()
    return {
        "status": state,
        "ledger": str(path),
        "calls": calls,
        "cost_usd": str(total),
        "provider_cost_usd": {provider: str(provider_cost[provider]) for provider in _PROVIDERS},
        "credentials_loaded": True,
        "credentials_cleared": True,
        "private_state_created": False,
        "scientific_state_created": False,
    }


def main() -> None:
    """Execute the exact repository-native canary command."""
    result = run_provider_schema_canaries(Path.cwd())
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("status") != "conformance-pass-both-complete-schemas":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
