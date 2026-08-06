"""AO-0012 R5 generic owner-gate compatibility adapter.

Importing this module is authorization-free.  R5 changes only the prospective
authorization adapter; the encrypted-Pod runtime lifecycle remains the frozen
R4 implementation.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from distributed_discovery.agent_ops.core import (
    authorization_challenge,
    hash_path,
    load_yaml,
    sha256_file,
    validate,
)
from distributed_discovery.benchmark.agents_v1.live_inputs import (
    CredentialSet,
    load_credentials,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime import (
    RuntimeConformanceError,
    validate_registration,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    BRANCH as R4_BRANCH,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    ISSUE,
    PULL_REQUEST,
    ControlPlane,
    Lifecycle,
    RunPodControlPlane,
    _authorization_digest,
    _require,
    _validate_live_github_and_git,
    validate_r4_registration,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    run_live_calibration as run_r4_lifecycle,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    run_offline_rehearsal as run_r4_offline_rehearsal,
)

TASK_ID = "AO-0012"
BRANCH = R4_BRANCH
GATE_ID = "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R5"
CONSUMED_GATE_ID = "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R4"
CONTRACT_PATH = Path("tasks/treasurebench-open-weight-cloud-runtime-r5.yml")
GATE_PATH = Path("reports/agent-ops/AO-0012-open-weight-public-calibration-r5-owner-gate.yml")
OUTCOME_PATH = Path("reports/benchmark/treasurebench-open-weight-public-calibration-outcome-r5.yml")
AUDIT_PATH = Path(
    "reports/benchmark/treasurebench-open-weight-cloud-runtime-r5-generic-gate-compatibility-audit.yml"
)
CORRUPTIONS_PATH = Path("docs/benchmark/agents-v1/open-weight-cloud-runtime-corruptions-r5.yml")

EXPECTED_CUMULATIVE_STATE: dict[str, object] = {
    "currency": "USD",
    "spend": "0",
    "calls": 0,
    "category_spend": {"runpod_gpu_compute_and_storage": "0"},
}
EXPECTED_HARD_CAPS: dict[str, object] = {
    "currency": "USD",
    "spend": "20",
    "calls": 400,
    "category_spend": {"runpod_gpu_compute_and_storage": "20"},
}
EXPECTED_REMAINING_CAPS: dict[str, object] = {
    "currency": "USD",
    "spend": "20",
    "calls": 400,
    "category_spend": {"runpod_gpu_compute_and_storage": "20"},
}


def authorization_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return root / "distributed-discovery" / "agent-ops" / "authorizations" / f"{GATE_ID}.yml"


def state_path() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "distributed-discovery" / "agent-ops" / f"{GATE_ID}.json"


def namespace_for(authorization_digest: str) -> str:
    _require(authorization_digest.startswith("sha256:"), "authorization digest format")
    suffix = authorization_digest.removeprefix("sha256:")[:16]
    _require(len(suffix) == 16 and all(c in "0123456789abcdef" for c in suffix), "digest")
    return f"ao0012-owcal-r5-{suffix}"


def validate_canonical_caps(gate: Mapping[str, Any]) -> None:
    """Require the exact generic gate cap mappings; no legacy budget fallback exists."""

    _require(gate.get("cumulative_state") == EXPECTED_CUMULATIVE_STATE, "cumulative state mismatch")
    _require(gate.get("hard_caps") == EXPECTED_HARD_CAPS, "hard caps mismatch")
    _require(gate.get("remaining_caps") == EXPECTED_REMAINING_CAPS, "remaining caps mismatch")


def validate_r5_registration(repo: Path) -> dict[str, object]:
    contract = load_yaml(repo / CONTRACT_PATH)
    _require(contract.get("task_id") == TASK_ID, "R5 task drift")
    identifiers = contract.get("frozen_identifiers")
    if not isinstance(identifiers, Mapping):
        raise RuntimeConformanceError("R5 identifiers missing")
    _require(identifiers.get("gate_id") == GATE_ID, "R5 gate identity drift")
    _require(identifiers.get("consumed_gate_id") == CONSUMED_GATE_ID, "R4 consumed identity drift")
    audit = load_yaml(repo / AUDIT_PATH)
    _require(audit.get("credential_read") is False, "credential-read audit drift")
    _require(audit.get("authenticated_provider_call") is False, "provider-call audit drift")
    _require(audit.get("spend_usd") == "0", "spend audit drift")
    corruptions = load_yaml(repo / CORRUPTIONS_PATH)
    cases = corruptions.get("cases")
    if not isinstance(cases, list) or len(cases) < 11:
        raise RuntimeConformanceError("R5 corruption coverage drift")
    _require(
        corruptions.get("inherits")
        == "docs/benchmark/agents-v1/open-weight-cloud-runtime-corruptions-r4.yml",
        "R4 corruption inheritance drift",
    )
    return {
        "contract": "pass",
        "compatibility_audit": "pass",
        "corruptions": 84 + len(cases),
        "credential_read": False,
        "authenticated_provider_call": False,
        "spend_usd": "0",
    }


def validate_owner_authorization(
    repo: Path,
    value: Mapping[str, Any],
    *,
    gate_override: Mapping[str, Any] | None = None,
    live_state_validator: Callable[[Path, Mapping[str, Any]], None] = _validate_live_github_and_git,
    now: datetime | None = None,
    synthetic_branch_context: str | None = None,
) -> dict[str, Any]:
    """Validate a real generic R5 authorization before credential ingress."""

    validate(dict(value), "owner-authorization.schema.json")
    gate = dict(gate_override) if gate_override is not None else load_yaml(repo / GATE_PATH)
    validate(gate, "owner-gate.schema.json")
    validate_canonical_caps(gate)
    _require(value.get("gate_id") == GATE_ID, "R5 owner authorization required")
    _require(gate.get("gate_id") == GATE_ID, "R5 owner gate required")
    _require(value.get("issue") == ISSUE, "authorization issue mismatch")
    _require(value.get("pull_request") == PULL_REQUEST, "authorization PR mismatch")
    _require(value.get("branch") == BRANCH, "authorization branch mismatch")
    _require(value.get("commit") == gate["commit"], "authorization commit mismatch")
    _require(value.get("challenge") == authorization_challenge(gate), "challenge mismatch")
    contract_hash = sha256_file(repo / CONTRACT_PATH)
    _require(
        gate["task_contract"] == {"path": str(CONTRACT_PATH), "sha256": contract_hash},
        "R5 contract mismatch",
    )
    _require(value.get("task_contract_sha256") == contract_hash, "authorization contract mismatch")
    _require(value.get("tree_hashes") == gate["tree_hashes"], "protected tree mismatch")
    _require(
        value.get("owner_confirmation_statements") == gate["owner_confirmation_statements"],
        "owner statements mismatch",
    )
    _require(value.get("expires_at_utc") == gate["expires_at_utc"], "expiry mismatch")
    _require(
        value.get("authorization_digest") == _authorization_digest(value),
        "authorization digest mismatch",
    )
    observed_now = now or datetime.now(UTC)
    authorized = datetime.fromisoformat(str(value["authorized_at_utc"]).replace("Z", "+00:00"))
    expires = datetime.fromisoformat(str(value["expires_at_utc"]).replace("Z", "+00:00"))
    _require(authorized <= observed_now < expires, "authorization outside active interval")
    for relative, expected in gate["tree_hashes"].items():
        _require(hash_path(repo / relative) == expected, f"authorized tree drift: {relative}")
    if synthetic_branch_context is None:
        branch = subprocess.run(
            ("git", "branch", "--show-current"),
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    else:
        _require(gate_override is not None, "synthetic branch context requires gate override")
        _require(
            live_state_validator is not _validate_live_github_and_git,
            "synthetic branch context requires synthetic live-state validator",
        )
        branch = synthetic_branch_context
    _require(branch == BRANCH, "live branch mismatch")
    ancestry = subprocess.run(
        ("git", "merge-base", "--is-ancestor", str(value["commit"]), "HEAD"),
        cwd=repo,
        check=False,
        capture_output=True,
    )
    _require(ancestry.returncode == 0, "execution commit is not an ancestor")
    live_state_validator(repo, gate)
    return gate


def validate_pre_ingress(repo: Path, authorization: Mapping[str, Any]) -> Lifecycle:
    validate_registration(repo)
    validate_r4_registration(repo)
    validate_r5_registration(repo)
    validate_owner_authorization(repo, authorization)
    _require(not state_path().exists(), "existing AO-0012 R5 live resource or ledger conflict")
    digest = str(authorization["authorization_digest"])
    return Lifecycle(namespace_for(digest), digest, datetime.now(UTC))


def run_offline_rehearsal(repo: Path) -> dict[str, object]:
    result = run_r4_offline_rehearsal(repo)
    result["r5_registration"] = validate_r5_registration(repo)
    result["r5_gate"] = GATE_ID
    result["consumed_r4_gate"] = CONSUMED_GATE_ID
    result["canonical_owner_gate_caps"] = {
        "cumulative_state": EXPECTED_CUMULATIVE_STATE,
        "hard_caps": EXPECTED_HARD_CAPS,
        "remaining_caps": EXPECTED_REMAINING_CAPS,
    }
    result["legacy_budget_dependency"] = False
    return result


def run_live_calibration(
    repo: Path,
    *,
    credential_loader: Callable[..., CredentialSet] = load_credentials,
    plane_factory: Callable[[str], ControlPlane] = RunPodControlPlane,
    authorization_file: Path | None = None,
    pre_ingress_validator: Callable[[Path, Mapping[str, Any]], Lifecycle] = validate_pre_ingress,
) -> dict[str, object]:
    """Run the unchanged R4 lifecycle only after exact R5 pre-ingress validation."""

    return run_r4_lifecycle(
        repo,
        credential_loader=credential_loader,
        plane_factory=plane_factory,
        authorization_file=authorization_file or authorization_path(),
        pre_ingress_validator=pre_ingress_validator,
        live_state_file=state_path(),
        outcome_path=OUTCOME_PATH,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--rehearsal", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    result = run_live_calibration(args.repo) if args.live else run_offline_rehearsal(args.repo)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
