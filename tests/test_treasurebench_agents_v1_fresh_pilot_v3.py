from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path

import pytest

from distributed_discovery.benchmark.agents_v1 import fresh_pilot_v3, fresh_pilot_v3_live
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v3_live import (
    RouteCappedLedger,
    audit_live_corruptions,
    private_state_root,
    run_live_fresh_pilot,
    run_mock_fresh_pilot,
    run_production_permit_custody_rehearsal,
)
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v3_session import (
    LongSessionStopRequired,
)
from distributed_discovery.benchmark.agents_v1.live_inputs import CredentialSet
from distributed_discovery.benchmark.agents_v1.live_providers import (
    ANTHROPIC_MANIFEST,
    OPENAI_MANIFEST,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v3_registration_allocation_budget_and_provider_boundary_are_exact() -> None:
    registration = fresh_pilot_v3.validate_registration(ROOT)
    slots = fresh_pilot_v3.allocation_slots(ROOT)
    tasks = fresh_pilot_v3.generate_tasks(
        ROOT,
        material="FRESH-RC-V3-TEST-PUBLIC",
        public_fixture=True,
    )
    boundary = fresh_pilot_v3.validate_provider_boundary(tasks)
    assert registration["status"] == "pass"
    assert registration["slots"] == 50
    assert registration["runs"] == 500
    assert len({slot.slot_id for slot in slots}) == 50
    assert all(slot.slot_id.startswith("RCV3-SLOT-") for slot in slots)
    assert boundary["provider_independent_semantic_validation"] == "pass"
    assert boundary["exactly_one_final_action"] == "pass"
    fingerprints = boundary["provider_schema_fingerprints"]
    assert isinstance(fingerprints, dict)
    assert len(set(fingerprints.values())) == 2
    assert registration["provider_calls"] == 0
    assert registration["credential_reads"] == 0
    assert registration["private_objects_created"] == 0
    assert registration["spend_usd"] == "0"


def test_v3_private_generation_fails_before_generic_owner_authorization() -> None:
    with pytest.raises(PermissionError, match="owner authorization"):
        fresh_pilot_v3.generate_tasks(ROOT, material="forbidden", public_fixture=False)


def test_v3_production_permit_and_custody_rehearsal_uses_no_synthetic_bypass() -> None:
    result = run_production_permit_custody_rehearsal(ROOT)
    assert result["status"] == "pass"
    assert result["production_generator_permit_path"] == "pass"
    assert result["synthetic_mode_bypass_used"] is False
    assert result["tasks"] == 50
    assert result["answers"] == 50
    assert result["independent_verification"] == "pass"
    assert len(result["negative_checks"]) == 6
    assert result["cleanup"] == "pass"
    assert result["real_seed_or_private_campaign_material_created"] is False
    assert result["credentials_read"] == 0
    assert result["provider_calls"] == 0
    assert result["spend_usd"] == "0"


def test_v3_complete_500_run_rehearsal() -> None:
    result = fresh_pilot_v3.run_synthetic_rehearsal(ROOT)
    assert result["status"] == "pass"
    assert result["tasks"] == 50
    assert result["runs"] == 500
    assert result["turns"] == 3014
    assert result["exact_pairings_verified"] == 500
    assert result["incomplete_pairings"] == 0
    assert result["method_a_b_errors"] == 0
    assert result["method_c_errors"] == 0
    assert result["metric_range_errors"] == 0
    assert result["invalid_final_action_cardinalities"] == 0
    assert result["contamination_findings"] == 0
    assert result["nonfinal_proposals_excluded_from_scoring"] is True
    assert result["output_lock_verified"] is True
    assert result["provider_calls"] == 0
    assert result["credential_reads"] == 0
    assert result["private_objects_created"] == 0
    assert result["external_cost_usd"] == "0"


def test_all_43_v3_corruptions_reject_and_match_registry() -> None:
    observed = (
        *fresh_pilot_v3.audit_corruptions(ROOT),
        *audit_live_corruptions(ROOT),
    )
    registry = fresh_pilot_v3.load_corruption_registry(ROOT)
    assert len(observed) == 43
    assert {item["corruption_id"] for item in observed} == set(registry["corruptions"])
    assert all(item["status"] == "rejected" for item in observed)


@pytest.mark.parametrize(
    ("provider", "input_tokens", "output_tokens"),
    [
        ("OpenAI", 1_680_001, 0),
        ("OpenAI", 0, 386_049),
        ("Anthropic", 3_000_001, 0),
        ("Anthropic", 0, 386_049),
    ],
)
def test_v3_route_token_caps_fail_closed(
    tmp_path: Path,
    provider: str,
    input_tokens: int,
    output_tokens: int,
) -> None:
    ledger = RouteCappedLedger(tmp_path / f"{provider}.jsonl")
    with pytest.raises(PermissionError, match="token cap"):
        ledger.guard_next(
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=Decimal("0"),
        )


def test_v3_offline_module_has_no_credential_or_provider_runtime() -> None:
    source = (ROOT / "src/distributed_discovery/benchmark/agents_v1/fresh_pilot_v3.py").read_text(
        encoding="utf-8"
    )
    assert "load_credentials" not in source
    assert "UrllibTransport" not in source
    assert "OpenAIResponsesAdapter" not in source
    assert "AnthropicMessagesAdapter" not in source


def _synthetic_generic_authorization() -> dict[str, object]:
    request = fresh_pilot_v3.load_request(ROOT)
    return {
        "schema_version": "agent-ops-owner-authorization-v1",
        "kind": "owner-authorization",
        "synthetic": True,
        "gate_id": fresh_pilot_v3.GATE_ID,
        "issue": fresh_pilot_v3.ISSUE,
        "pull_request": 0,
        "branch": fresh_pilot_v3.BRANCH,
        "commit": request["starting_main"],
        "task_contract_sha256": "sha256:" + "0" * 64,
        "tree_hashes": fresh_pilot_v3.execution_tree_hashes(ROOT),
        "authorized_at_utc": "2026-07-28T00:00:00+00:00",
        "expires_at_utc": "2099-01-01T00:00:00Z",
        "challenge": "SYNTHETIC-OFFLINE-ONLY",
        "owner_confirmation_statements": ["synthetic offline fixture"],
        "authorization_digest": "sha256:" + "1" * 64,
    }


def test_v3_live_driver_uses_distinct_private_root() -> None:
    path = private_state_root().as_posix()
    assert path.endswith("/treasurebench-agents-v1/repair-confirmation-v3")
    assert "repair-confirmation-v1" not in path


def test_v3_live_driver_stops_before_authorization_and_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    with pytest.raises(FileNotFoundError):
        run_live_fresh_pilot(ROOT)
    assert not (tmp_path / "state").exists()


def test_v3_staged_mock_driver_completes_and_resumes_without_calls(tmp_path: Path) -> None:
    root = tmp_path / "fresh-v3-mock-live"
    authorization = _synthetic_generic_authorization()
    first, first_adapters = run_mock_fresh_pilot(
        ROOT,
        authorization=authorization,
        root=root,
    )
    assert first["status"] == "pass"
    assert first["campaign_id"] == fresh_pilot_v3.CAMPAIGN_ID
    assert first["batch_id"] == fresh_pilot_v3.BATCH_ID
    assert first["private_runs"] == 500
    assert first["method_a_b_disagreements"] == 0
    assert first["method_c_failures"] == 0
    assert first["invalid_final_action_cardinalities"] == 0
    assert first["metric_range_errors"] == 0
    assert first["incomplete_pairings"] == 0
    assert first["contamination_findings"] == 0
    assert first["provider_phase_closed"] is True
    assert first["output_lock_verified"] is True
    assert first["unseal_after_lock_verified"] is True
    assert first["exact_cost_reconciliation"] is True
    assert first["base_campaign_authorized"] is False
    assert sum(adapter.calls for adapter in first_adapters.values()) == 3016

    second, second_adapters = run_mock_fresh_pilot(
        ROOT,
        authorization=authorization,
        root=root,
    )
    assert second == first
    assert sum(adapter.calls for adapter in second_adapters.values()) == 0


def _write_private_env(path: Path, text: str, *, mode: int = 0o600) -> None:
    path.write_text(text, encoding="utf-8")
    os.chmod(path, mode)


class _CapturedProviderAdapter:
    def __init__(self, *, api_key: str, manifest: object) -> None:
        self._api_key = api_key
        self.manifest = manifest

    def clear_secret(self) -> None:
        self._api_key = ""

    def __repr__(self) -> str:
        return "_CapturedProviderAdapter(api_key=<redacted>)"


def test_v3_live_adapters_request_return_and_retain_only_exact_two_credentials(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "checkout"
    repo.mkdir()
    unrelated = {
        "OPENROUTER_API_KEY": "unrelated-openrouter",
        "GEMINI_API_KEY": "unrelated-gemini",
        "GOOGLE_API_KEY": "unrelated-google",
        "MISTRAL_API_KEY": "unrelated-mistral",
        "FLYMYAI_API_KEY": "unrelated-flymyai",
        "MONID_API_KEY": "unrelated-monid",
    }
    _write_private_env(
        repo / ".env.txt",
        "OPENAI_API_KEY=synthetic-openai\n"
        "ANTHROPIC_API_KEY=synthetic-anthropic\n"
        + "".join(f"{name}={value}\n" for name, value in unrelated.items()),
    )
    received: list[_CapturedProviderAdapter] = []

    def capture_openai(**kwargs: object) -> _CapturedProviderAdapter:
        adapter = _CapturedProviderAdapter(
            api_key=str(kwargs["api_key"]),
            manifest=OPENAI_MANIFEST,
        )
        received.append(adapter)
        return adapter

    def capture_anthropic(**kwargs: object) -> _CapturedProviderAdapter:
        adapter = _CapturedProviderAdapter(
            api_key=str(kwargs["api_key"]),
            manifest=ANTHROPIC_MANIFEST,
        )
        received.append(adapter)
        return adapter

    monkeypatch.setattr(fresh_pilot_v3_live, "OpenAIResponsesAdapter", capture_openai)
    monkeypatch.setattr(fresh_pilot_v3_live, "AnthropicMessagesAdapter", capture_anthropic)
    ledger = RouteCappedLedger(tmp_path / "ledger.jsonl")
    _, credentials, underlying = fresh_pilot_v3_live._live_adapters(
        repo,
        _synthetic_generic_authorization(),
        ledger,
        b"k" * 32,
        tmp_path / "responses",
    )
    assert credentials.configured == {
        "ANTHROPIC_API_KEY": True,
        "OPENAI_API_KEY": True,
    }
    assert credentials.unused_present == ()
    assert [adapter._api_key for adapter in received] == [
        "synthetic-openai",
        "synthetic-anthropic",
    ]
    rendered = repr(credentials) + repr(received) + repr(underlying)
    for value in unrelated.values():
        assert value not in rendered
        assert all(adapter._api_key != value for adapter in received)
    for name in unrelated:
        with pytest.raises(PermissionError, match="outside"):
            credentials.get_secret(name)
    fresh_pilot_v3_live._clear_stage_secrets(credentials, underlying)
    assert credentials.get_secret("OPENAI_API_KEY") is None
    assert credentials.get_secret("ANTHROPIC_API_KEY") is None
    assert all(adapter._api_key == "" for adapter in received)


@pytest.mark.parametrize(
    "case",
    ["missing-openai", "missing-anthropic", "unsafe-mode", "symlink"],
)
def test_v3_credential_source_refuses_before_adapter_or_call(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    repo = tmp_path / "checkout"
    repo.mkdir()
    path = repo / ".env.txt"
    complete = "OPENAI_API_KEY=synthetic-openai\nANTHROPIC_API_KEY=synthetic-anthropic\n"
    if case == "missing-openai":
        _write_private_env(path, "ANTHROPIC_API_KEY=synthetic-anthropic\n")
    elif case == "missing-anthropic":
        _write_private_env(path, "OPENAI_API_KEY=synthetic-openai\n")
    elif case == "unsafe-mode":
        _write_private_env(path, complete, mode=0o644)
    else:
        target = tmp_path / "target-env"
        _write_private_env(target, complete)
        path.symlink_to(target)
    adapter_created = False

    def prohibit_adapter(**kwargs: object) -> object:
        nonlocal adapter_created
        adapter_created = True
        raise AssertionError("provider adapter must not be created")

    monkeypatch.setattr(fresh_pilot_v3_live, "OpenAIResponsesAdapter", prohibit_adapter)
    monkeypatch.setattr(fresh_pilot_v3_live, "AnthropicMessagesAdapter", prohibit_adapter)
    with pytest.raises(PermissionError):
        fresh_pilot_v3_live._live_adapters(
            repo,
            _synthetic_generic_authorization(),
            RouteCappedLedger(tmp_path / "ledger.jsonl"),
            b"k" * 32,
            tmp_path / "responses",
        )
    assert adapter_created is False


@pytest.mark.parametrize(
    "failure_point",
    ["authorization", "execution-tree", "identity", "stage", "ledger", "projected-cap"],
)
def test_v3_preflight_failures_precede_credential_ingress(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_point: str,
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    credential_ingress = False

    def prohibit_credentials(*args: object, **kwargs: object) -> CredentialSet:
        nonlocal credential_ingress
        credential_ingress = True
        raise AssertionError("credential ingress occurred before preflight completed")

    monkeypatch.setattr(fresh_pilot_v3_live, "load_credentials", prohibit_credentials)
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "load_owner_authorization",
        lambda repo: _synthetic_generic_authorization(),
    )
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_bind_private_state",
        lambda repo, root, authorization: {"status": "bound"},
    )
    if failure_point == "authorization":
        monkeypatch.setattr(
            fresh_pilot_v3_live,
            "load_owner_authorization",
            lambda repo: (_ for _ in ()).throw(PermissionError("authorization")),
        )
    elif failure_point in {"execution-tree", "identity"}:
        monkeypatch.setattr(
            fresh_pilot_v3_live,
            "_bind_private_state",
            lambda repo, root, authorization: (_ for _ in ()).throw(PermissionError(failure_point)),
        )
    elif failure_point == "stage":
        monkeypatch.setattr(
            fresh_pilot_v3_live,
            "_next_stage",
            lambda repo, root, state: (_ for _ in ()).throw(PermissionError("stage")),
        )
    elif failure_point == "ledger":
        monkeypatch.setattr(
            fresh_pilot_v3_live,
            "_fresh_ledger",
            lambda path: (_ for _ in ()).throw(PermissionError("ledger")),
        )
    elif failure_point == "projected-cap":
        monkeypatch.setattr(
            fresh_pilot_v3_live,
            "_validate_call_stage_before_credential_ingress",
            lambda stage, ledger: (_ for _ in ()).throw(PermissionError("projected cap")),
        )
    expected = "cap-guard" if failure_point == "projected-cap" else failure_point.replace("-", ".*")
    with pytest.raises(PermissionError, match=expected):
        fresh_pilot_v3_live._prepare_live_stage(ROOT)
    assert credential_ingress is False


@pytest.mark.parametrize(
    ("stage", "outcome"),
    [
        ("public-canary", "success"),
        ("private-prefix", "success"),
        ("fixed-full-batch", "success"),
        ("public-canary", "provider-failure"),
        ("public-canary", "parser-failure"),
        ("public-canary", "protocol-failure"),
        ("public-canary", "unexpected-exception"),
    ],
)
def test_v3_every_provider_stage_and_exit_path_clears_selected_secrets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
    outcome: str,
) -> None:
    credentials = CredentialSet(
        {
            "OPENAI_API_KEY": "synthetic-openai",
            "ANTHROPIC_API_KEY": "synthetic-anthropic",
        },
        allowed_names=fresh_pilot_v3_live.CREDENTIAL_NAMES,
        configured={name: True for name in fresh_pilot_v3_live.CREDENTIAL_NAMES},
        unused_present=(),
    )
    adapters = (
        _CapturedProviderAdapter(
            api_key="synthetic-openai",
            manifest=OPENAI_MANIFEST,
        ),
        _CapturedProviderAdapter(
            api_key="synthetic-anthropic",
            manifest=ANTHROPIC_MANIFEST,
        ),
    )
    ledger = RouteCappedLedger(tmp_path / "ledger.jsonl")
    prepared = fresh_pilot_v3_live.PreparedLiveStage(
        authorization=_synthetic_generic_authorization(),
        root=tmp_path / "state",
        operational_key=b"k" * 32,
        response_root=tmp_path / "responses",
        ledger=ledger,
        stage=stage,
    )
    monkeypatch.setattr(fresh_pilot_v3_live, "_prepare_live_stage", lambda repo: prepared)
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_live_adapters",
        lambda *args, **kwargs: ({}, credentials, adapters),
    )

    def execute(*args: object, **kwargs: object) -> dict[str, str]:
        if outcome != "success":
            raise RuntimeError(outcome)
        return {"status": "pass"}

    monkeypatch.setattr(fresh_pilot_v3_live, "_execute_stage", execute)
    if outcome == "success":
        assert fresh_pilot_v3_live._run_prepared_live_stage(ROOT, prepared)["status"] == "pass"
    else:
        with pytest.raises(RuntimeError, match=outcome):
            fresh_pilot_v3_live._run_prepared_live_stage(ROOT, prepared)
    assert credentials.get_secret("OPENAI_API_KEY") is None
    assert credentials.get_secret("ANTHROPIC_API_KEY") is None
    assert all(adapter._api_key == "" for adapter in adapters)
    assert "synthetic" not in repr(credentials)
    assert all("synthetic" not in repr(adapter) for adapter in adapters)


def _prepared_stage(tmp_path: Path, stage: str) -> fresh_pilot_v3_live.PreparedLiveStage:
    return fresh_pilot_v3_live.PreparedLiveStage(
        authorization=_synthetic_generic_authorization(),
        root=tmp_path / "state",
        operational_key=b"k" * 32,
        response_root=tmp_path / "responses",
        ledger=RouteCappedLedger(tmp_path / "ledger.jsonl"),
        stage=stage,
    )


def test_v3_live_command_runs_all_stages_and_public_commitments_without_pause(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stages = iter(
        [
            "public-canary",
            "custody",
            "private-prefix",
            "fixed-full-batch",
            "output-lock",
            "verify",
        ]
    )
    events: list[str] = []
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_prepare_live_stage",
        lambda repo: _prepared_stage(tmp_path, next(stages)),
    )

    def run_stage(
        repo: Path,
        prepared: fresh_pilot_v3_live.PreparedLiveStage,
    ) -> dict[str, str]:
        events.append(prepared.stage)
        return {"status": "pass", "stage": prepared.stage}

    monkeypatch.setattr(fresh_pilot_v3_live, "_run_prepared_live_stage", run_stage)
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_publish_public_commitment",
        lambda repo, prepared, result: events.append(f"publish-{prepared.stage}"),
    )
    result = run_live_fresh_pilot(ROOT)
    assert result == {"status": "pass", "stage": "verify"}
    assert events == [
        "public-canary",
        "custody",
        "publish-custody",
        "private-prefix",
        "fixed-full-batch",
        "output-lock",
        "publish-output-lock",
        "verify",
    ]


def test_v3_live_terminal_failure_quarantines_and_never_advances(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _prepared_stage(tmp_path, "private-prefix")
    events: list[str] = []
    monkeypatch.setattr(fresh_pilot_v3_live, "_prepare_live_stage", lambda repo: prepared)
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_run_prepared_live_stage",
        lambda repo, value: (_ for _ in ()).throw(RuntimeError("terminal provider")),
    )

    def quarantine(
        value: fresh_pilot_v3_live.PreparedLiveStage,
        *,
        failure_class: str,
    ) -> dict[str, object]:
        events.append(f"quarantine-{failure_class}")
        return {
            "status": "quarantined",
            "output_lock_commitment": "sha256:" + "3" * 64,
            "objects_locked": 4,
        }

    monkeypatch.setattr(fresh_pilot_v3_live, "_quarantine_live_failure", quarantine)
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_publish_public_commitment",
        lambda repo, value, result: events.append("publish-output-lock"),
    )
    result = run_live_fresh_pilot(ROOT)
    assert result["status"] == "quarantined"
    assert events == ["quarantine-private-prefix-failure", "publish-output-lock"]


def test_v3_live_cap_guard_quarantines_before_credential_ingress(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _prepared_stage(tmp_path, "public-canary")
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_prepare_live_stage",
        lambda repo: (_ for _ in ()).throw(
            fresh_pilot_v3_live.PreparedStageFailure(
                prepared=prepared,
                failure_class="cap-guard-failure",
            )
        ),
    )
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_quarantine_live_failure",
        lambda value, failure_class: {
            "status": "quarantined",
            "failure_class": failure_class,
            "output_lock_commitment": "sha256:" + "4" * 64,
            "objects_locked": 2,
        },
    )
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_publish_public_commitment",
        lambda repo, value, result: {"status": "pass"},
    )
    result = run_live_fresh_pilot(ROOT)
    assert result["failure_class"] == "cap-guard-failure"


def test_v3_live_output_lock_failure_stops_for_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepared = _prepared_stage(tmp_path, "output-lock")
    monkeypatch.setattr(fresh_pilot_v3_live, "_prepare_live_stage", lambda repo: prepared)
    monkeypatch.setattr(
        fresh_pilot_v3_live,
        "_run_prepared_live_stage",
        lambda repo, value: (_ for _ in ()).throw(RuntimeError("cannot lock")),
    )
    with pytest.raises(LongSessionStopRequired, match="safely output-locked"):
        run_live_fresh_pilot(ROOT)
