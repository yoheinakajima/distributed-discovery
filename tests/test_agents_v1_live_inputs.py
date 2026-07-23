from __future__ import annotations

import os
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CostLedger,
    load_credentials,
    load_preflight_authorization,
    parse_dotenv,
)

BASE = "8fa51758f39d4d04290784969d7990dd998019cb"
BRANCH = "benchmark/discoverybench-agents-v1-provider-preflight"


def _authorization() -> dict[str, object]:
    return {
        "schema_version": 1,
        "authorization_id": "synthetic-authorization",
        "purpose": "unified-provider-credential-preflight-and-public-calibration",
        "authorization_status": "authorized",
        "execution_allowed": True,
        "private_tasks_allowed": False,
        "scientific_evidence_allowed": False,
        "authorized_base_commit": BASE,
        "allowed_branch": BRANCH,
        "credential_source": "repository-local-env-txt",
        "external_spend_cap_usd": 20,
        "gateway_caps_usd": {"openrouter": 20},
        "route_caps_usd": {
            "openrouter_mistral_small_3_1": 5,
            "openrouter_gemini_2_5_pro": 10,
        },
        "max_calls_per_route": 600,
        "max_total_calls": 2000,
        "max_live_concurrency": 2,
        "expires_utc": "2026-07-30T00:00:00Z",
        "revoked": False,
    }


def _write_private(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    os.chmod(path, 0o600)


def test_strict_dotenv_supports_quotes_without_interpolation() -> None:
    parsed = parse_dotenv(
        b"""
        # synthetic only
        export OPENROUTER_API_KEY='synthetic-openrouter'
        OPENAI_API_KEY=\"synthetic-openai\"
        FLYMYAI_API_KEY=unused-synthetic # ignored
        """
    )
    assert parsed["OPENROUTER_API_KEY"] == "synthetic-openrouter"
    assert parsed["OPENAI_API_KEY"] == "synthetic-openai"
    assert parsed["FLYMYAI_API_KEY"] == "unused-synthetic"


@pytest.mark.parametrize(
    "body",
    [
        b"A=one\nA=two\n",
        b"BAD-NAME=value\n",
        b"A=$(whoami)\n",
        b"A=`whoami`\n",
        b"A=value; whoami\n",
        b"A=value && whoami\n",
        b"A=value | whoami\n",
        b"A=value\\\ncontinued\n",
        b"A=\x00value\n",
        b'A="line\\nvalue"\n',
    ],
)
def test_strict_dotenv_rejects_executable_or_ambiguous_forms(body: bytes) -> None:
    with pytest.raises(ValueError):
        parse_dotenv(body)


def test_credential_loader_is_explicit_private_allowlisted_and_redacted(tmp_path: Path) -> None:
    path = tmp_path / ".env.txt"
    _write_private(
        path,
        "OPENROUTER_API_KEY=synthetic-secret\n"
        "FLYMYAI_API_KEY=unused-one\n"
        "MONID_API_KEY=unused-two\n",
    )
    with pytest.raises(PermissionError, match="explicit"):
        load_credentials(path, explicit_live_mode=False)
    credentials = load_credentials(path, explicit_live_mode=True)
    assert credentials.configured["OPENROUTER_API_KEY"] is True
    assert credentials.configured["OPENAI_API_KEY"] is False
    assert credentials.unused_present == ("FLYMYAI_API_KEY", "MONID_API_KEY")
    assert credentials.get_secret("OPENROUTER_API_KEY") == "synthetic-secret"
    assert "synthetic-secret" not in repr(credentials)
    with pytest.raises(PermissionError, match="outside"):
        credentials.get_secret("MONID_API_KEY")
    credentials.clear()
    assert credentials.get_secret("OPENROUTER_API_KEY") is None


def test_credential_and_authorization_permissions_are_fail_closed(tmp_path: Path) -> None:
    credential_path = tmp_path / ".env.txt"
    credential_path.write_text("OPENROUTER_API_KEY=synthetic\n", encoding="utf-8")
    os.chmod(credential_path, 0o644)
    with pytest.raises(PermissionError, match="permissions"):
        load_credentials(credential_path, explicit_live_mode=True)

    authorization_path = tmp_path / "authorization.yml"
    authorization_path.write_text(yaml.safe_dump(_authorization()), encoding="utf-8")
    os.chmod(authorization_path, 0o644)
    with pytest.raises(PermissionError, match="permissions"):
        load_preflight_authorization(
            authorization_path,
            expected_base_commit=BASE,
            expected_branch=BRANCH,
            now=datetime(2026, 7, 23, tzinfo=UTC),
        )


def test_preflight_authorization_and_cost_ledger(tmp_path: Path) -> None:
    path = tmp_path / "authorization.yml"
    _write_private(path, yaml.safe_dump(_authorization(), sort_keys=True))
    authorization = load_preflight_authorization(
        path,
        expected_base_commit=BASE,
        expected_branch=BRANCH,
        now=datetime(2026, 7, 23, tzinfo=UTC),
    )
    assert authorization.total_cap_usd == Decimal("20")
    assert authorization.private_tasks_allowed is False
    assert authorization.scientific_evidence_allowed is False

    ledger = CostLedger(authorization)
    ledger.authorize_next_call(
        gateway_id="openrouter",
        route_id="openrouter_mistral_small_3_1",
        maximum_call_cost_usd=Decimal("0.25"),
    )
    ledger.record_call(
        route_id="openrouter_mistral_small_3_1",
        actual_cost_usd=Decimal("0.01"),
    )
    assert ledger.calls_made == 1
    assert ledger.total_cost_usd == Decimal("0.01")
    with pytest.raises(PermissionError, match="route cost"):
        ledger.authorize_next_call(
            gateway_id="openrouter",
            route_id="openrouter_mistral_small_3_1",
            maximum_call_cost_usd=Decimal("5"),
        )


def test_authorization_rejects_branch_base_expiry_and_scope(tmp_path: Path) -> None:
    for key, value in [
        ("allowed_branch", "wrong"),
        ("authorized_base_commit", "0" * 40),
        ("private_tasks_allowed", True),
        ("scientific_evidence_allowed", True),
        ("revoked", True),
    ]:
        document = _authorization()
        document[key] = value
        path = tmp_path / f"{key}.yml"
        _write_private(path, yaml.safe_dump(document))
        with pytest.raises(PermissionError):
            load_preflight_authorization(
                path,
                expected_base_commit=BASE,
                expected_branch=BRANCH,
                now=datetime(2026, 7, 23, tzinfo=UTC),
            )
    expired = _authorization()
    expired["expires_utc"] = "2026-07-22T00:00:00Z"
    path = tmp_path / "expired.yml"
    _write_private(path, yaml.safe_dump(expired))
    with pytest.raises(PermissionError, match="expired"):
        load_preflight_authorization(
            path,
            expected_base_commit=BASE,
            expected_branch=BRANCH,
            now=datetime(2026, 7, 23, tzinfo=UTC),
        )
