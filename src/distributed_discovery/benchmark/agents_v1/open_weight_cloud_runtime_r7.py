"""AO-0012 R7 public-only calibration gate adapter.

Importing this module is authorization-free. R7 preserves the R4 runtime
identity and lifecycle, uses a new authorization-derived namespace, and
narrows the prospective spend envelope after the consumed R5/R6 gates.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

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
    validate_registration,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    BRANCH,
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
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r5 import (
    validate_r5_registration,
)

TASK_ID = "AO-0012"
GATE_ID = "AOG-AO-0012-R7-PUBLIC-CALIBRATION"
CONTRACT_PATH = Path("tasks/treasurebench-open-weight-cloud-runtime-r7.yml")
GATE_PATH = Path("reports/agent-ops/AO-0012-open-weight-public-calibration-r7-owner-gate.yml")
OUTCOME_PATH = Path("reports/benchmark/treasurebench-open-weight-public-calibration-outcome-r7.yml")
AUDIT_PATH = Path(
    "reports/benchmark/treasurebench-open-weight-cloud-runtime-r7-calibration-gate-audit.yml"
)
CORRUPTIONS_PATH = Path("docs/benchmark/agents-v1/open-weight-cloud-runtime-corruptions-r7.yml")

EXPECTED_SPEND = Decimal("3")
HARD_CAP = Decimal("10")
MAX_HOURLY_RATE = Decimal("1.50")
MAX_GPU_SECONDS = 21_600
MAX_CALLS = 400

EXPECTED_CUMULATIVE_STATE: dict[str, object] = {
    "currency": "USD",
    "spend": "0",
    "calls": 0,
    "category_spend": {"runpod_gpu_compute_and_storage": "0"},
}
EXPECTED_HARD_CAPS: dict[str, object] = {
    "currency": "USD",
    "spend": str(HARD_CAP),
    "calls": MAX_CALLS,
    "category_spend": {"runpod_gpu_compute_and_storage": str(HARD_CAP)},
}
EXPECTED_REMAINING_CAPS = dict(EXPECTED_HARD_CAPS)


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
    return f"ao0012-owcal-r7-{suffix}"


def validate_canonical_caps(gate: Mapping[str, Any]) -> None:
    _require(gate.get("cumulative_state") == EXPECTED_CUMULATIVE_STATE, "cumulative state mismatch")
    _require(gate.get("hard_caps") == EXPECTED_HARD_CAPS, "hard caps mismatch")
    _require(gate.get("remaining_caps") == EXPECTED_REMAINING_CAPS, "remaining caps mismatch")


def validate_hourly_rate(value: object) -> Decimal:
    rate = Decimal(str(value))
    _require(rate > 0 and rate <= MAX_HOURLY_RATE, "hourly rate above R7 prospective cap")
    return rate


class R7RunPodControlPlane(RunPodControlPlane):
    """R4 transport with the tighter prospective R7 hourly-rate ceiling."""

    def create_pod(self, spec: Mapping[str, object]) -> dict[str, Any]:
        pod = super().create_pod(spec)
        validate_hourly_rate(pod.get("costPerHr", 0))
        return pod

    def get_pod(self, pod_id: str) -> dict[str, Any] | None:
        pod = super().get_pod(pod_id)
        if pod is not None:
            validate_hourly_rate(pod.get("costPerHr", 0))
        return pod


def validate_r7_registration(repo: Path) -> dict[str, object]:
    contract = load_yaml(repo / CONTRACT_PATH)
    _require(contract.get("task_id") == TASK_ID, "R7 task drift")
    identifiers = contract.get("frozen_identifiers")
    _require(isinstance(identifiers, Mapping), "R7 identifiers missing")
    exact_identifiers = identifiers if isinstance(identifiers, Mapping) else {}
    _require(exact_identifiers.get("gate_id") == GATE_ID, "R7 gate identity drift")
    _require(
        exact_identifiers.get("hard_total_cost_usd") == str(HARD_CAP),
        "R7 hard cap drift",
    )
    _require(
        exact_identifiers.get("maximum_gpu_seconds") == str(MAX_GPU_SECONDS),
        "R7 time cap drift",
    )
    audit = load_yaml(repo / AUDIT_PATH)
    _require(audit.get("credential_read") is False, "credential-read audit drift")
    _require(audit.get("authenticated_provider_call") is False, "provider-call audit drift")
    _require(audit.get("spend_usd") == "0", "spend audit drift")
    observation = audit.get("owner_observation")
    _require(isinstance(observation, Mapping), "owner observation missing")
    exact_observation = observation if isinstance(observation, Mapping) else {}
    _require(exact_observation.get("current_secrets_tab") == "empty", "owner observation drift")
    _require(exact_observation.get("api_proof") is False, "owner observation overstated")
    _require(
        exact_observation.get("historical_absence_proven") is False,
        "historical absence overstated",
    )
    corruptions = load_yaml(repo / CORRUPTIONS_PATH)
    cases = corruptions.get("cases")
    _require(isinstance(cases, list) and len(cases) >= 10, "R7 corruption coverage drift")
    case_count = len(cases) if isinstance(cases, list) else 0
    return {
        "contract": "pass",
        "calibration_gate_audit": "pass",
        "corruptions": 95 + case_count,
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
    validate(dict(value), "owner-authorization.schema.json")
    gate = dict(gate_override) if gate_override is not None else load_yaml(repo / GATE_PATH)
    validate(gate, "owner-gate.schema.json")
    validate_canonical_caps(gate)
    _require(value.get("gate_id") == GATE_ID, "R7 owner authorization required")
    _require(gate.get("gate_id") == GATE_ID, "R7 owner gate required")
    _require(value.get("issue") == ISSUE, "authorization issue mismatch")
    _require(value.get("pull_request") == PULL_REQUEST, "authorization PR mismatch")
    _require(value.get("branch") == BRANCH, "authorization branch mismatch")
    _require(value.get("commit") == gate["commit"], "authorization commit mismatch")
    _require(value.get("challenge") == authorization_challenge(gate), "challenge mismatch")
    contract_hash = sha256_file(repo / CONTRACT_PATH)
    _require(
        gate["task_contract"] == {"path": str(CONTRACT_PATH), "sha256": contract_hash},
        "R7 contract mismatch",
    )
    _require(value.get("task_contract_sha256") == contract_hash, "authorization contract mismatch")
    _require(value.get("tree_hashes") == gate["tree_hashes"], "protected tree mismatch")
    _require(
        value.get("owner_confirmation_statements") == gate["owner_confirmation_statements"],
        "owner statements mismatch",
    )
    _require(value.get("expires_at_utc") == gate["expires_at_utc"], "expiry mismatch")
    _require(value.get("authorization_digest") == _authorization_digest(value), "digest mismatch")
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
    validate_r7_registration(repo)
    validate_owner_authorization(repo, authorization)
    _require(not state_path().exists(), "existing AO-0012 R7 live resource or ledger conflict")
    digest = str(authorization["authorization_digest"])
    return Lifecycle(namespace_for(digest), digest, datetime.now(UTC))


def enforce_outcome_caps(outcome: dict[str, object]) -> dict[str, object]:
    breached = False
    billing = outcome.get("billing")
    if isinstance(billing, Mapping):
        breached = Decimal(str(billing.get("exact_amount_usd", 0))) > HARD_CAP
        billed_milliseconds = int(str(billing.get("billed_milliseconds", 0)))
        breached = breached or billed_milliseconds > MAX_GPU_SECONDS * 1000
    counts = outcome.get("operational_counts")
    if isinstance(counts, Mapping):
        breached = breached or int(str(counts.get("calls", 0))) > MAX_CALLS
    if breached:
        outcome["status"] = "hard-stop"
        outcome["failure_class"] = "circuit-breaker-or-runtime-cap-failure"
        outcome["decision"] = "calibration-integrity-failure-stop"
        outcome["merge_or_issue_close_allowed"] = False
    return outcome


def run_offline_rehearsal(repo: Path) -> dict[str, object]:
    result = run_r4_offline_rehearsal(repo)
    result["r7_registration"] = validate_r7_registration(repo)
    result["r7_gate"] = GATE_ID
    result["prospective_caps"] = {
        "expected_spend_usd": str(EXPECTED_SPEND),
        "hard_spend_usd": str(HARD_CAP),
        "maximum_hourly_rate_usd": str(MAX_HOURLY_RATE),
        "maximum_gpu_seconds": MAX_GPU_SECONDS,
        "maximum_inference_calls": MAX_CALLS,
    }
    return result


def run_live_calibration(
    repo: Path,
    *,
    credential_loader: Callable[..., CredentialSet] = load_credentials,
    plane_factory: Callable[[str], ControlPlane] = R7RunPodControlPlane,
    authorization_file: Path | None = None,
    pre_ingress_validator: Callable[[Path, Mapping[str, Any]], Lifecycle] = validate_pre_ingress,
) -> dict[str, object]:
    outcome = run_r4_lifecycle(
        repo,
        credential_loader=credential_loader,
        plane_factory=plane_factory,
        authorization_file=authorization_file or authorization_path(),
        pre_ingress_validator=pre_ingress_validator,
        live_state_file=state_path(),
        outcome_path=OUTCOME_PATH,
    )
    enforce_outcome_caps(outcome)
    (repo / OUTCOME_PATH).write_text(yaml.safe_dump(outcome, sort_keys=False), encoding="utf-8")
    return outcome


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
