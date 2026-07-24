from __future__ import annotations

import json
import stat
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from distributed_discovery.benchmark.agents_v1.adapters import MockAdapter
from distributed_discovery.benchmark.agents_v1.generation import (
    canonical_cells,
    generate_instance,
)
from distributed_discovery.benchmark.agents_v1.pilot import (
    MODELS,
    AppendOnlyLedger,
    PilotBatchRunner,
    ResumablePilotAdapter,
    atomic_private_write,
    audit_pilot_corruptions,
    create_output_lock,
    execution_tree_hash,
    generate_allocated_tasks,
    initialize_private_state,
    load_allocation,
    load_request,
    pilot_offline_readiness,
    run_synthetic_rehearsal,
    seal_object,
    synthetic_authorization,
    unseal_object,
    validate_pilot_authorization,
    verify_output_lock,
)

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs/benchmark/agents-v1"


def test_request_and_allocation_are_schema_valid_and_balanced() -> None:
    request = load_request(REPO)
    allocation = load_allocation(REPO)
    assert request["campaign_id"] == "treasurebench-agents-v1-pilot-v1"
    assert len(allocation["slots"]) == 50  # type: ignore[arg-type]


def test_authorization_fixtures_have_intended_boundaries() -> None:
    schema = json.loads((DOCS / "treasurebench-pilot-authorization.schema.json").read_text())
    valid = yaml.safe_load(
        (DOCS / "fixtures/treasurebench-pilot-valid-synthetic-authorization.yml").read_text()
    )
    inactive = yaml.safe_load(
        (DOCS / "fixtures/treasurebench-pilot-inactive-authorization.yml").read_text()
    )
    invalid = yaml.safe_load(
        (DOCS / "fixtures/treasurebench-pilot-invalid-synthetic-authorization.yml").read_text()
    )
    Draft202012Validator(schema).validate(valid)
    Draft202012Validator(schema).validate(inactive)
    assert list(Draft202012Validator(schema).iter_errors(invalid))


def test_synthetic_authorization_never_authorizes_live() -> None:
    authorization = synthetic_authorization(REPO)
    with pytest.raises(PermissionError, match="synthetic"):
        validate_pilot_authorization(
            authorization,
            repo=REPO,
            expected_commit=str(authorization["authorized_execution_commit"]),
            expected_tree_hash=str(authorization["execution_tree_hash"]),
        )


def test_private_generation_requires_exact_permit() -> None:
    with pytest.raises(PermissionError, match="private generation"):
        generate_instance(canonical_cells()[0], variant=0, public_fixture=False)
    authorization = synthetic_authorization(REPO)
    tasks = generate_allocated_tasks(REPO, authorization=authorization, material="SYNTHETIC-TEST")
    assert len(tasks) == 50
    assert all(task.public_fixture is False for task in tasks)


def test_private_state_is_outside_repo_and_mode_restricted(tmp_path: Path) -> None:
    root = tmp_path / "private-state"
    manifest = initialize_private_state(root, repo=REPO, synthetic=True)
    assert manifest["classification"] == "synthetic-phase-a"
    assert stat.S_IMODE(root.stat().st_mode) == 0o700
    assert stat.S_IMODE((root / "manifest.json").stat().st_mode) == 0o600
    with pytest.raises(PermissionError, match="outside"):
        initialize_private_state(REPO / "private-state", repo=REPO, synthetic=True)


def test_atomic_private_write_refuses_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.write_text("target")
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(PermissionError, match="symlink"):
        atomic_private_write(link, b"replacement")


def test_independent_aes_domains_and_tamper_rejection() -> None:
    key = bytes(range(32))
    nonce = bytes(range(12))
    sealed = seal_object(domain="task", value={"value": 1}, key=key, nonce=nonce)
    assert unseal_object(sealed, key=key) == {"value": 1}
    with pytest.raises(ValueError, match="ciphertext"):
        unseal_object(
            sealed.__class__(
                sealed.domain,
                sealed.nonce_hex,
                sealed.ciphertext + b"x",
                sealed.ciphertext_sha256,
                sealed.associated_data_sha256,
            ),
            key=key,
        )


def test_ledger_idempotency_caps_close_and_output_lock(tmp_path: Path) -> None:
    ledger = AppendOnlyLedger(tmp_path / "ledger.jsonl")
    ledger.guard_next(
        provider="OpenAI",
        input_tokens=100,
        output_tokens=50,
        cost_usd=Decimal("1"),
    )
    ledger.append(
        {
            "idempotency_key": "one",
            "status": "success",
            "provider": "OpenAI",
            "input_tokens": 100,
            "output_tokens": 50,
            "cost_usd": "1",
        }
    )
    with pytest.raises(PermissionError, match="idempotency"):
        ledger.append({"idempotency_key": "one", "status": "success"})
    with pytest.raises(PermissionError, match="closed"):
        create_output_lock({"trace": b"value"}, ledger=ledger)
    ledger.close_provider_phase()
    objects = {"trace": b"value", "ledger": ledger.path.read_bytes()}
    lock = create_output_lock(objects, ledger=ledger)
    verify_output_lock(lock, objects, ledger=ledger)
    with pytest.raises(PermissionError, match="closed"):
        ledger.append({"idempotency_key": "two", "status": "success"})


def test_all_pilot_corruptions_reject() -> None:
    results = audit_pilot_corruptions(REPO)
    assert len(results) >= 35
    assert all(item["status"] == "rejected" for item in results)
    required = {
        str(item["corruption_id"])
        for item in results
        if str(item["corruption_id"]).startswith("PILOT-")
    }
    assert len(required) == 35


def test_provider_neutral_runner_resumes_without_duplicate_calls(
    tmp_path: Path,
) -> None:
    ledger = AppendOnlyLedger(tmp_path / "usage-cost-ledger.jsonl")
    underlying = {model: MockAdapter() for model in MODELS}
    adapters = {
        model: ResumablePilotAdapter(
            underlying[model],
            provider=("OpenAI" if index == 0 else "Anthropic"),
            model=model,
            ledger=ledger,
            response_root=tmp_path / f"responses-{index}",
            response_key=bytes([index + 1]) * 32,
        )
        for index, model in enumerate(MODELS)
    }
    runner = PilotBatchRunner(
        state_root=tmp_path,
        ledger=ledger,
        trace_key=b"t" * 32,
    )
    task = generate_instance(canonical_cells()[0], variant=0, public_fixture=True)
    first = runner.run_stage(
        stage="public-canary",
        tasks=(task,),
        adapters=adapters,
    )
    calls = {model: adapter.calls for model, adapter in underlying.items()}
    second = runner.run_stage(
        stage="public-canary",
        tasks=(task,),
        adapters=adapters,
    )
    assert first == second
    assert {model: adapter.calls for model, adapter in underlying.items()} == calls
    assert first["runs"] == 10


def test_offline_readiness_reads_no_credentials_or_private_material(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    result = pilot_offline_readiness(REPO)
    assert result["status"] == "pass"
    assert result["authorization_present"] is False
    assert result["credential_reads"] == 0
    assert result["provider_calls"] == 0
    assert result["private_material"] is False
    assert result["execution_tree_hash"] == execution_tree_hash(REPO)


def test_complete_synthetic_rehearsal_is_stable_and_sealed() -> None:
    first = run_synthetic_rehearsal(REPO)
    second = run_synthetic_rehearsal(REPO)
    assert first == second
    assert first["tasks"] == 50
    assert first["runs"] == 500
    assert first["encrypted_traces"] == 500
    assert first["method_disagreements"] == 0
    assert first["output_lock_verified"] is True
    assert first["provider_calls"] == 0
    assert first["external_cost_usd"] == "0"
    assert first["network_enabled"] is False


def test_authorization_interval_rejects_expiration() -> None:
    authorization = dict(synthetic_authorization(REPO))
    authorization["expires_at_utc"] = "2026-07-23T00:00:00Z"
    with pytest.raises(PermissionError, match="active interval"):
        validate_pilot_authorization(
            authorization,
            repo=REPO,
            now=datetime(2026, 7, 24, tzinfo=UTC),
            allow_synthetic=True,
            expected_commit=str(authorization["authorized_execution_commit"]),
            expected_tree_hash=str(authorization["execution_tree_hash"]),
        )
