from __future__ import annotations

import json
import os
from collections.abc import Iterator, Mapping
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest
import yaml

import distributed_discovery.benchmark.agents_v1.provider_canary_live as canary_module
from distributed_discovery.agent_ops.core import (
    GateObservation,
    hash_path,
    sha256_file,
    write_authorization,
)
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CredentialSet,
)
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    load_credentials as strict_load_credentials,
)
from distributed_discovery.benchmark.agents_v1.live_providers import HttpRequest, HttpResponse
from distributed_discovery.benchmark.agents_v1.provider_canary_live import (
    BRANCH,
    ISSUE_NUMBER,
    PULL_REQUEST_NUMBER,
    R3_GATE_ID,
    CanarySpec,
    PublicEngineeringLedger,
    RuntimeAuthorization,
    _projected_max_cost,
    _request_for_spec,
    frozen_canary_specs,
    run_provider_schema_canaries,
    validate_runtime_authorization,
)
from distributed_discovery.benchmark.agents_v1.provider_schema import schema_fingerprint

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 7, 27, 18, 0, tzinfo=UTC)
EXECUTION_COMMIT = "a" * 40
MANIFEST_COMMIT = "b" * 40


def _gate_and_contract() -> tuple[dict[str, object], dict[str, object]]:
    contract_path = ROOT / "tasks/treasurebench-provider-schema-conformance.yml"
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    contract_hash = sha256_file(contract_path)
    gate: dict[str, object] = {
        "schema_version": "agent-ops-owner-gate-v1",
        "kind": "owner-gate",
        "synthetic": False,
        "gate_id": R3_GATE_ID,
        "task_contract": {
            "path": "tasks/treasurebench-provider-schema-conformance.yml",
            "sha256": contract_hash,
        },
        "issue": ISSUE_NUMBER,
        "pull_request": {
            "number": PULL_REQUEST_NUMBER,
            "expected_state": "OPEN",
            "head_sha": EXECUTION_COMMIT,
        },
        "branch": BRANCH,
        "commit": EXECUTION_COMMIT,
        "tree_hashes": {
            "tasks/treasurebench-provider-schema-conformance.yml": hash_path(contract_path)
        },
        "purpose": "Authorize only the exact synthetic AO-0004 R3 unit-test surface.",
        "irreversible_actions": [
            {
                "permission": "external_action_permissions.spend",
                "description": "Spend only within the exact caps.",
            }
        ],
        "private_actions": [],
        "external_actions": [
            {
                "permission": "external_action_permissions.provider_calls",
                "description": "Call only the exact direct providers.",
            },
            {
                "permission": "external_action_permissions.network_observation",
                "description": "Observe only safe provider responses.",
            },
        ],
        "cumulative_state": {
            "currency": "USD",
            "spend": "0",
            "calls": 0,
            "category_spend": {"OpenAI": "0", "Anthropic": "0"},
        },
        "hard_caps": {
            "currency": "USD",
            "spend": "1.00",
            "calls": 10,
            "category_spend": {"OpenAI": "0.50", "Anthropic": "0.50"},
        },
        "remaining_caps": {
            "currency": "USD",
            "spend": "1.00",
            "calls": 10,
            "category_spend": {"OpenAI": "0.50", "Anthropic": "0.50"},
        },
        "owner_confirmation_statements": [
            "I authorize only the exact synthetic AO-0004 R3 unit-test surface."
        ],
        "explicit_prohibitions": [
            "provider-calls-outside-manifest",
            "credential-read-outside-manifest",
            "unauthorized-private-access",
            "scientific-mutation-outside-contract",
            "cap-increase",
            "consequential-action-by-gate-engine",
            "credential-source-other-than-repository-local-dot-env-txt",
            "credential-input-other-than-openai-api-key-or-anthropic-api-key",
            "shell-sourcing-execution-or-dotenv-interpolation",
        ],
        "expires_at_utc": "2026-08-03T18:00:00Z",
        "authorization_output_symbolic_path": (
            f"XDG_CONFIG_HOME/distributed-discovery/agent-ops/authorizations/{R3_GATE_ID}.yml"
        ),
        "next_milestone": "Synthetic AO-0004 R3 canary unit test.",
        "generated_resume_message": "Resume only the synthetic AO-0004 R3 unit test.",
    }
    return gate, contract


def _observation() -> GateObservation:
    return GateObservation(
        branch=BRANCH,
        commit=MANIFEST_COMMIT,
        remote_commit=MANIFEST_COMMIT,
        tracked_clean=True,
        pull_request_number=PULL_REQUEST_NUMBER,
        pull_request_state="OPEN",
        pull_request_head_sha=MANIFEST_COMMIT,
        observed_execution_commit=EXECUTION_COMMIT,
        execution_commit_is_ancestor=True,
        observed_at_utc=NOW,
    )


def _runtime(tmp_path: Path) -> RuntimeAuthorization:
    gate, contract = _gate_and_contract()
    authorization_path, _ = write_authorization(
        gate,
        f"AUTHORIZE {R3_GATE_ID} {EXECUTION_COMMIT[:7]}",
        config_root=tmp_path / "config",
        now=NOW,
    )
    authorization = yaml.safe_load(authorization_path.read_text(encoding="utf-8"))
    return validate_runtime_authorization(
        repo=ROOT,
        gate=gate,
        contract=contract,
        authorization=authorization,
        observation=_observation(),
        issue_number=ISSUE_NUMBER,
        issue_state="OPEN",
        now=NOW,
    )


class ExactEnvironment(Mapping[str, str]):
    def __init__(self) -> None:
        self._entries = {
            "OPENAI_API_KEY": "synthetic-openai-secret",
            "ANTHROPIC_API_KEY": "synthetic-anthropic-secret",
            "UNRELATED_SECRET": "must-not-be-read",
        }
        self.reads: list[str] = []

    def __getitem__(self, key: str) -> str:
        self.reads.append(key)
        return self._entries[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)


class ForbiddenEnvironment(Mapping[str, str]):
    def __getitem__(self, key: str) -> str:
        raise AssertionError(f"credential read before preflight completed: {key}")

    def __iter__(self) -> Iterator[str]:
        return iter(())

    def __len__(self) -> int:
        return 0


def _write_private_env(path: Path, body: str, *, mode: int = 0o600) -> None:
    path.write_text(body, encoding="utf-8")
    os.chmod(path, mode)


def _schema_from_request(request: HttpRequest) -> Mapping[str, object]:
    assert request.body is not None
    if "text" in request.body:
        text = cast(Mapping[str, object], request.body["text"])
        output_format = cast(Mapping[str, object], text["format"])
    else:
        output_config = cast(Mapping[str, object], request.body["output_config"])
        output_format = cast(Mapping[str, object], output_config["format"])
    return cast(Mapping[str, object], output_format["schema"])


def _value_for_schema(schema: Mapping[str, object]) -> object:
    if "enum" in schema:
        choices = schema["enum"]
        assert isinstance(choices, list)
        return choices[0]
    schema_type = schema.get("type")
    if schema_type == "object":
        properties = schema.get("properties")
        assert isinstance(properties, Mapping)
        required = schema.get("required")
        assert isinstance(required, list)
        return {
            str(name): _value_for_schema(cast(Mapping[str, object], properties[str(name)]))
            for name in required
        }
    if schema_type == "array":
        items = schema.get("items")
        assert isinstance(items, Mapping)
        return [_value_for_schema(items)]
    if schema_type == "string":
        return "public"
    if schema_type == "integer":
        return 0
    if schema_type == "boolean":
        return True
    raise AssertionError(f"unsupported test schema: {schema}")


class CanaryTransport:
    def __init__(
        self,
        *,
        failure_ids: frozenset[str] = frozenset(),
        interrupt_on_call: int | None = None,
    ) -> None:
        self.failure_ids = failure_ids
        self.interrupt_on_call = interrupt_on_call
        self.requests: list[HttpRequest] = []
        self.ids_by_fingerprint = {
            (spec.provider, schema_fingerprint(spec.schema)): spec.canary_id
            for spec in frozen_canary_specs()
        }
        self.providers_by_url = {
            "https://api.openai.com/v1/responses": "openai",
            "https://api.anthropic.com/v1/messages": "anthropic",
        }
        self.canary_ids: list[str] = []

    def send(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        schema = _schema_from_request(request)
        provider = self.providers_by_url[request.url]
        canary_id = self.ids_by_fingerprint[(provider, schema_fingerprint(schema))]
        self.canary_ids.append(canary_id)
        if self.interrupt_on_call == len(self.requests):
            raise RuntimeError("synthetic interruption after committed call intent")
        if canary_id in self.failure_ids:
            return HttpResponse(
                400,
                {
                    "error": {
                        "type": "invalid_request_error",
                        "code": "invalid_json_schema",
                        "param": "schema",
                        "message": "synthetic bounded failure",
                        "raw_secret": "must-not-be-retained",
                    }
                },
            )
        output = json.dumps(_value_for_schema(schema), sort_keys=True)
        if request.url.endswith("/responses"):
            return HttpResponse(
                200,
                {
                    "id": "resp_public",
                    "model": "gpt-5.4-2026-03-05",
                    "status": "completed",
                    "output": [
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": output}],
                        }
                    ],
                    "usage": {"input_tokens": 10, "output_tokens": 10},
                },
            )
        return HttpResponse(
            200,
            {
                "id": "msg_public",
                "model": "claude-sonnet-4-6",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": output}],
                "usage": {"input_tokens": 10, "output_tokens": 10},
            },
        )


def test_exact_runtime_authorization_validates_generic_surface(tmp_path: Path) -> None:
    runtime = _runtime(tmp_path)
    assert runtime.gate["gate_id"] == R3_GATE_ID
    assert runtime.gate["commit"] == EXECUTION_COMMIT
    assert runtime.gate["private_actions"] == []


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("issue", 999, "issue"),
        ("branch", "wrong", "branch"),
        ("gate_id", "AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R2", "R3"),
        (
            "hard_caps",
            {
                "currency": "USD",
                "spend": "0.99",
                "calls": 10,
                "category_spend": {"OpenAI": "0.50", "Anthropic": "0.49"},
            },
            "caps",
        ),
    ],
)
def test_runtime_authorization_rejects_identity_drift(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    runtime = _runtime(tmp_path)
    gate = deepcopy(dict(runtime.gate))
    gate[field] = value
    with pytest.raises((PermissionError, ValueError), match=message):
        validate_runtime_authorization(
            repo=ROOT,
            gate=gate,
            contract=runtime.contract,
            authorization=runtime.authorization,
            observation=_observation(),
            issue_number=ISSUE_NUMBER,
            issue_state="OPEN",
            now=NOW,
        )


def test_complete_runner_sequence_and_public_ledger(tmp_path: Path) -> None:
    environment = ExactEnvironment()
    transport = CanaryTransport()
    ledger_path = tmp_path / "public-ledger.jsonl"
    result = run_provider_schema_canaries(
        ROOT,
        runtime=_runtime(tmp_path),
        transport=transport,
        environment=environment,
        ledger_path=ledger_path,
        now=NOW,
    )
    assert result["status"] == "conformance-pass-both-complete-schemas"
    assert transport.canary_ids == [
        "openai-minimal-known-valid",
        "openai-treasurebench-complete",
        "anthropic-minimal-known-valid",
        "anthropic-treasurebench-complete",
    ]
    assert (
        environment.reads
        == [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
        ]
        * 4
    )
    ledger = PublicEngineeringLedger(
        ledger_path,
        gate_id=R3_GATE_ID,
        execution_commit=EXECUTION_COMMIT,
    )
    assert ledger.totals()[0] == 4
    assert all("raw_error_body" not in record for record in ledger.records)
    assert all("synthetic-openai-secret" not in json.dumps(record) for record in ledger.records)
    assert list(tmp_path.glob("**/public-ledger.jsonl")) == [ledger_path]


def test_exact_live_command_uses_repository_local_env_without_shell_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "checkout"
    repo.mkdir()
    credential_path = repo / ".env.txt"
    _write_private_env(
        credential_path,
        "OPENAI_API_KEY=synthetic-openai\n"
        "ANTHROPIC_API_KEY=synthetic-anthropic\n"
        "OPENROUTER_API_KEY=must-not-be-selected\n",
    )
    runtime = _runtime(tmp_path / "authorization")
    observed: list[tuple[Path, frozenset[str]]] = []

    def tracked_loader(
        path: Path,
        *,
        explicit_live_mode: bool,
        requested_names: tuple[str, ...],
    ) -> CredentialSet:
        assert explicit_live_mode is True
        observed.append((path, frozenset(requested_names)))
        return strict_load_credentials(
            path,
            explicit_live_mode=explicit_live_mode,
            requested_names=requested_names,
        )

    def prohibit_shell(*args: object, **kwargs: object) -> object:
        raise AssertionError("shell execution is prohibited for credential ingress")

    monkeypatch.setattr(
        canary_module,
        "load_live_runtime_authorization",
        lambda checkout, now: runtime,
    )
    monkeypatch.setattr(
        "distributed_discovery.benchmark.agents_v1.provider_canary_live.load_credentials",
        tracked_loader,
    )
    monkeypatch.setattr("subprocess.run", prohibit_shell)
    result = run_provider_schema_canaries(
        repo,
        transport=CanaryTransport(),
        now=NOW,
    )
    assert result["status"] == "conformance-pass-both-complete-schemas"
    assert (
        observed
        == [
            (
                credential_path,
                frozenset({"OPENAI_API_KEY", "ANTHROPIC_API_KEY"}),
            )
        ]
        * 4
    )
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert (
        "treasurebench-provider-schema-canaries:\n"
        "\t$(PY) -m distributed_discovery.benchmark.agents_v1.provider_canary_live" in makefile
    )


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("missing-file", "missing"),
        ("unsafe-mode", "permissions"),
        ("symlink", "symlink"),
        ("parser-error", "prohibited shell syntax"),
        ("missing-openai", "OPENAI_API_KEY"),
        ("missing-anthropic", "ANTHROPIC_API_KEY"),
    ],
)
def test_credential_file_failures_refuse_before_call_or_intent(
    tmp_path: Path,
    case: str,
    expected: str,
) -> None:
    credential_path = tmp_path / ".env.txt"
    if case == "unsafe-mode":
        _write_private_env(
            credential_path,
            "OPENAI_API_KEY=synthetic-openai\nANTHROPIC_API_KEY=synthetic-anthropic\n",
            mode=0o644,
        )
    elif case == "symlink":
        target = tmp_path / "synthetic-target"
        _write_private_env(
            target,
            "OPENAI_API_KEY=synthetic-openai\nANTHROPIC_API_KEY=synthetic-anthropic\n",
        )
        credential_path.symlink_to(target)
    elif case == "missing-openai":
        _write_private_env(
            credential_path,
            "ANTHROPIC_API_KEY=synthetic-anthropic\n",
        )
    elif case == "parser-error":
        _write_private_env(
            credential_path,
            "OPENAI_API_KEY=synthetic-openai\nANTHROPIC_API_KEY=$(must-not-execute)\n",
        )
    elif case == "missing-anthropic":
        _write_private_env(
            credential_path,
            "OPENAI_API_KEY=synthetic-openai\n",
        )
    transport = CanaryTransport()
    ledger_path = tmp_path / "failure-ledger.jsonl"
    with pytest.raises((PermissionError, FileNotFoundError, ValueError), match=expected):
        run_provider_schema_canaries(
            ROOT,
            runtime=_runtime(tmp_path / "authorization"),
            transport=transport,
            credential_path=credential_path,
            ledger_path=ledger_path,
            now=NOW,
        )
    assert transport.requests == []
    assert not ledger_path.exists()


def test_unrelated_dotenv_keys_are_never_returned_transmitted_or_retained(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credential_path = tmp_path / ".env.txt"
    unrelated_values = (
        "unrelated-openrouter",
        "unrelated-fly",
        "unrelated-monid",
        "unrelated-gemini",
        "unrelated-google",
        "unrelated-mistral",
    )
    _write_private_env(
        credential_path,
        "OPENAI_API_KEY=synthetic-openai\n"
        "ANTHROPIC_API_KEY=synthetic-anthropic\n"
        "OPENROUTER_API_KEY=unrelated-openrouter\n"
        "FLYMYAI_API_KEY=unrelated-fly\n"
        "MONID_API_KEY=unrelated-monid\n"
        "GEMINI_API_KEY=unrelated-gemini\n"
        "GOOGLE_API_KEY=unrelated-google\n"
        "MISTRAL_API_KEY=unrelated-mistral\n",
    )
    loaded_sets: list[CredentialSet] = []

    def tracked_loader(
        path: Path,
        *,
        explicit_live_mode: bool,
        requested_names: tuple[str, ...],
    ) -> CredentialSet:
        credentials = strict_load_credentials(
            path,
            explicit_live_mode=explicit_live_mode,
            requested_names=requested_names,
        )
        loaded_sets.append(credentials)
        return credentials

    monkeypatch.setattr(
        "distributed_discovery.benchmark.agents_v1.provider_canary_live.load_credentials",
        tracked_loader,
    )
    transport = CanaryTransport()
    ledger_path = tmp_path / "public-ledger.jsonl"
    result = run_provider_schema_canaries(
        ROOT,
        runtime=_runtime(tmp_path / "authorization"),
        transport=transport,
        credential_path=credential_path,
        ledger_path=ledger_path,
        now=NOW,
    )
    assert result["status"] == "conformance-pass-both-complete-schemas"
    retained = ledger_path.read_text(encoding="utf-8")
    for value in unrelated_values:
        assert value not in retained
        assert all(value not in repr(request) for request in transport.requests)
        assert all(value not in json.dumps(request.body) for request in transport.requests)
        assert all(value not in json.dumps(request.headers) for request in transport.requests)
        assert all(value not in repr(credentials) for credentials in loaded_sets)
    assert all(credentials.unused_present == () for credentials in loaded_sets)
    for credentials in loaded_sets:
        assert credentials.get_secret("OPENAI_API_KEY") is None
        assert credentials.get_secret("ANTHROPIC_API_KEY") is None
        with pytest.raises(PermissionError, match="outside"):
            credentials.get_secret("OPENROUTER_API_KEY")


@pytest.mark.parametrize(
    "outcome",
    ["provider-error", "response-parser-error", "unexpected-exception"],
)
def test_credentials_clear_on_every_provider_exit_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    outcome: str,
) -> None:
    credential_path = tmp_path / ".env.txt"
    _write_private_env(
        credential_path,
        "OPENAI_API_KEY=synthetic-openai\nANTHROPIC_API_KEY=synthetic-anthropic\n",
    )
    loaded_sets: list[CredentialSet] = []

    def tracked_loader(
        path: Path,
        *,
        explicit_live_mode: bool,
        requested_names: tuple[str, ...],
    ) -> CredentialSet:
        credentials = strict_load_credentials(
            path,
            explicit_live_mode=explicit_live_mode,
            requested_names=requested_names,
        )
        loaded_sets.append(credentials)
        return credentials

    class InvalidJsonTransport(CanaryTransport):
        def send(self, request: HttpRequest) -> HttpResponse:
            response = super().send(request)
            if request.url.endswith("/responses"):
                return HttpResponse(
                    200,
                    {
                        "id": "resp_public",
                        "model": "gpt-5.4-2026-03-05",
                        "status": "completed",
                        "output": [
                            {
                                "type": "message",
                                "content": [{"type": "output_text", "text": "not-json"}],
                            }
                        ],
                        "usage": {"input_tokens": 10, "output_tokens": 10},
                    },
                )
            return response

    monkeypatch.setattr(
        "distributed_discovery.benchmark.agents_v1.provider_canary_live.load_credentials",
        tracked_loader,
    )
    if outcome == "provider-error":
        transport: CanaryTransport = CanaryTransport(
            failure_ids=frozenset({"openai-minimal-known-valid"})
        )
    elif outcome == "response-parser-error":
        transport = InvalidJsonTransport()
    else:
        transport = CanaryTransport(interrupt_on_call=1)
    runtime = _runtime(tmp_path / "authorization")
    ledger_path = tmp_path / "exit-ledger.jsonl"
    if outcome == "unexpected-exception":
        with pytest.raises(RuntimeError, match="synthetic interruption"):
            run_provider_schema_canaries(
                ROOT,
                runtime=runtime,
                transport=transport,
                credential_path=credential_path,
                ledger_path=ledger_path,
                now=NOW,
            )
    else:
        result = run_provider_schema_canaries(
            ROOT,
            runtime=runtime,
            transport=transport,
            credential_path=credential_path,
            ledger_path=ledger_path,
            now=NOW,
        )
        assert result["status"] == "stopped-minimal-schema-failure"
    assert loaded_sets
    for credentials in loaded_sets:
        assert credentials.get_secret("OPENAI_API_KEY") is None
        assert credentials.get_secret("ANTHROPIC_API_KEY") is None
        assert "synthetic" not in repr(credentials)


def test_complete_failure_runs_only_frozen_same_provider_bisection(tmp_path: Path) -> None:
    ledger_path = tmp_path / "bisection.jsonl"
    transport = CanaryTransport(failure_ids=frozenset({"openai-treasurebench-complete"}))
    result = run_provider_schema_canaries(
        ROOT,
        runtime=_runtime(tmp_path),
        transport=transport,
        environment=ExactEnvironment(),
        ledger_path=ledger_path,
        now=NOW,
    )
    assert result["status"] == "stopped-complete-schema-failure-after-fixed-bisection"
    assert transport.canary_ids == [
        "openai-minimal-known-valid",
        "openai-treasurebench-complete",
        "openai-bisection-action-cardinality",
        "openai-bisection-identity-envelope",
    ]
    assert not any(item.startswith("anthropic") for item in transport.canary_ids)
    serialized = ledger_path.read_text(encoding="utf-8")
    assert "raw_secret" not in serialized
    assert "synthetic bounded failure" not in serialized
    assert "diagnostic_message_sha256" in serialized


def test_minimal_failure_stops_before_complete_and_other_provider(tmp_path: Path) -> None:
    transport = CanaryTransport(failure_ids=frozenset({"openai-minimal-known-valid"}))
    result = run_provider_schema_canaries(
        ROOT,
        runtime=_runtime(tmp_path),
        transport=transport,
        environment=ExactEnvironment(),
        ledger_path=tmp_path / "minimal-failure.jsonl",
        now=NOW,
    )
    assert result["status"] == "stopped-minimal-schema-failure"
    assert transport.canary_ids == ["openai-minimal-known-valid"]


def test_interrupted_call_intent_resumes_fail_closed_without_credentials(tmp_path: Path) -> None:
    ledger_path = tmp_path / "interrupted.jsonl"
    with pytest.raises(RuntimeError, match="synthetic interruption"):
        run_provider_schema_canaries(
            ROOT,
            runtime=_runtime(tmp_path),
            transport=CanaryTransport(interrupt_on_call=1),
            environment=ExactEnvironment(),
            ledger_path=ledger_path,
            now=NOW,
        )

    class NoCredentialAccess(Mapping[str, str]):
        def __getitem__(self, key: str) -> str:
            raise AssertionError(f"credential read during fail-closed resume: {key}")

        def __iter__(self) -> Iterator[str]:
            return iter(())

        def __len__(self) -> int:
            return 0

    result = run_provider_schema_canaries(
        ROOT,
        runtime=_runtime(tmp_path / "second"),
        transport=CanaryTransport(),
        environment=NoCredentialAccess(),
        ledger_path=ledger_path,
        now=NOW,
    )
    assert result["status"] == "manual-reconciliation-required-open-call-intent"
    assert result["credentials_loaded"] is False


def test_live_authorization_failure_precedes_credential_file_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_authorization(repo: Path, *, now: datetime) -> RuntimeAuthorization:
        raise PermissionError("synthetic protected-tree authorization failure")

    def reject_credential_read(*args: object, **kwargs: object) -> CredentialSet:
        raise AssertionError("credential file accessed before authorization")

    monkeypatch.setattr(
        canary_module,
        "load_live_runtime_authorization",
        reject_authorization,
    )
    monkeypatch.setattr(canary_module, "load_credentials", reject_credential_read)
    with pytest.raises(PermissionError, match="protected-tree"):
        run_provider_schema_canaries(tmp_path, transport=CanaryTransport(), now=NOW)


def test_invalid_sequence_precedes_credential_access(tmp_path: Path) -> None:
    ledger_path = tmp_path / "invalid-sequence.jsonl"
    ledger = PublicEngineeringLedger(
        ledger_path,
        gate_id=R3_GATE_ID,
        execution_commit=EXECUTION_COMMIT,
    )
    ledger.append(
        {
            "event_type": "call-intent",
            "canary_id": "not-a-frozen-canary",
            "provider": "openai",
            "route": "openai_direct",
            "model": "gpt-5.4-2026-03-05",
            "schema_fingerprint": "sha256:" + "1" * 64,
            "schema_role": "minimal",
            "projected_max_cost_usd": "0.001",
            "stopping_decision": "pending-provider-response",
        },
        now=NOW,
    )
    with pytest.raises(ValueError, match="unknown canary"):
        run_provider_schema_canaries(
            ROOT,
            runtime=_runtime(tmp_path / "authorization"),
            transport=CanaryTransport(),
            environment=ForbiddenEnvironment(),
            ledger_path=ledger_path,
            now=NOW,
        )


def test_projected_cap_failure_precedes_credential_access(tmp_path: Path) -> None:
    ledger_path = tmp_path / "projected-cap.jsonl"
    ledger = PublicEngineeringLedger(
        ledger_path,
        gate_id=R3_GATE_ID,
        execution_commit=EXECUTION_COMMIT,
    )
    intent = ledger.append(
        {
            "event_type": "call-intent",
            "canary_id": "openai-minimal-known-valid",
            "provider": "openai",
            "route": "openai_direct",
            "model": "gpt-5.4-2026-03-05",
            "schema_fingerprint": schema_fingerprint(frozen_canary_specs()[0].schema),
            "schema_role": "minimal",
            "projected_max_cost_usd": "0.099",
            "stopping_decision": "pending-provider-response",
        },
        now=NOW,
    )
    ledger.append(
        {
            "event_type": "call-result",
            "canary_id": "openai-minimal-known-valid",
            "provider": "openai",
            "route": "openai_direct",
            "model": "gpt-5.4-2026-03-05",
            "schema_fingerprint": schema_fingerprint(frozen_canary_specs()[0].schema),
            "schema_role": "minimal",
            "intent_record_hash": intent["record_hash"],
            "status": "success",
            "input_tokens": 1,
            "output_tokens": 1,
            "cost_usd": "0.099",
            "safe_error": {},
            "output_sha256": "sha256:" + "2" * 64,
            "stopping_decision": "continue-frozen-sequence",
        },
        now=NOW,
    )
    with pytest.raises(PermissionError, match="below USD 0.10"):
        run_provider_schema_canaries(
            ROOT,
            runtime=_runtime(tmp_path / "authorization"),
            transport=CanaryTransport(),
            environment=ForbiddenEnvironment(),
            ledger_path=ledger_path,
            now=NOW,
        )


def test_public_ledger_rejects_unsafe_raw_error_field(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.jsonl"
    ledger = PublicEngineeringLedger(
        path,
        gate_id=R3_GATE_ID,
        execution_commit=EXECUTION_COMMIT,
    )
    with pytest.raises(ValueError, match="unsafe"):
        ledger.append(
            {
                "event_type": "call-result",
                "canary_id": "openai-minimal-known-valid",
                "raw_error_body": "prohibited",
            },
            now=NOW,
        )


def test_public_ledger_rejects_hash_chain_tampering(tmp_path: Path) -> None:
    path = tmp_path / "tampered.jsonl"
    ledger = PublicEngineeringLedger(
        path,
        gate_id=R3_GATE_ID,
        execution_commit=EXECUTION_COMMIT,
    )
    ledger.append(
        {
            "event_type": "run-decision",
            "status": "stopped",
            "stopping_decision": "synthetic-test",
            "calls": 0,
            "total_cost_usd": "0",
            "provider_cost_usd": {"openai": "0", "anthropic": "0"},
        },
        now=NOW,
    )
    path.write_text(
        path.read_text(encoding="utf-8").replace("synthetic-test", "tampered"),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="hash"):
        PublicEngineeringLedger(
            path,
            gate_id=R3_GATE_ID,
            execution_commit=EXECUTION_COMMIT,
        )


def test_expected_cost_cap_rejects_next_call(tmp_path: Path) -> None:
    ledger = PublicEngineeringLedger(
        tmp_path / "caps.jsonl",
        gate_id=R3_GATE_ID,
        execution_commit=EXECUTION_COMMIT,
    )
    spec: CanarySpec = frozen_canary_specs()[0]
    intent = ledger.append(
        {
            "event_type": "call-intent",
            "canary_id": "prior",
            "provider": "openai",
            "route": "openai_direct",
            "model": "gpt-5.4-2026-03-05",
            "schema_fingerprint": "sha256:" + "1" * 64,
            "schema_role": "minimal",
            "projected_max_cost_usd": "0.099",
            "stopping_decision": "pending-provider-response",
        },
        now=NOW,
    )
    ledger.append(
        {
            "event_type": "call-result",
            "canary_id": "prior",
            "provider": "openai",
            "route": "openai_direct",
            "model": "gpt-5.4-2026-03-05",
            "schema_fingerprint": "sha256:" + "1" * 64,
            "schema_role": "minimal",
            "intent_record_hash": intent["record_hash"],
            "status": "success",
            "input_tokens": 1,
            "output_tokens": 1,
            "cost_usd": "0.099",
            "safe_error": {},
            "output_sha256": "sha256:" + "2" * 64,
            "stopping_decision": "continue-frozen-sequence",
        },
        now=NOW,
    )
    request = _request_for_spec(spec)
    _, projected = _projected_max_cost(spec, request)
    with pytest.raises(PermissionError, match="below USD 0.10"):
        ledger.guard_next(spec, projected_max_cost_usd=projected)
