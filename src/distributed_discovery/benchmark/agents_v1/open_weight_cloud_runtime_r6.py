"""AO-0012 R6 exact RunPod Secret status and conditional cleanup surface.

Importing and rehearsing this module are authorization-free.  The live entry
point is deliberately narrower than R5: after exact R6 authorization it may
load only ``RUNPOD_API_KEY``, inspect the RunPod Secrets inventory once,
conditionally delete one unique exact target, verify once, and stop.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, cast
from urllib.parse import quote

import yaml

from distributed_discovery.agent_ops.core import (
    authorization_challenge,
    hash_path,
    load_yaml,
    sha256_file,
    validate,
)
from distributed_discovery.benchmark.agents_v1.live_inputs import CredentialSet, load_credentials
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime import (
    RuntimeConformanceError,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r4 import (
    BRANCH,
    ISSUE,
    PULL_REQUEST,
    MutableSecret,
    _authorization_digest,
    _require,
    _validate_live_github_and_git,
)
from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime_r5 import (
    run_offline_rehearsal as run_r5_offline_rehearsal,
)

TASK_ID = "AO-0012"
FAILED_GATE_ID = "AOG-AO-0012-R6-RUNPOD-SECRET-STATUS-CONDITIONAL-CLEANUP"
GATE_ID = "AOG-AO-0012-R6-RUNPOD-SECRET-CLEANUP"
CONSUMED_GATE_ID = "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R5"
NAMESPACE = "ao0012-owcal-r5-01b41c9aa04bf2a4"
TARGET_SECRET_NAME = f"{NAMESPACE}-hf"
CONTRACT_PATH = Path("tasks/treasurebench-open-weight-cloud-runtime-r6b.yml")
GATE_PATH = Path("reports/agent-ops/AO-0012-runpod-secret-status-cleanup-r6b-owner-gate.yml")
FAILED_GATE_PATH = Path("reports/agent-ops/AO-0012-runpod-secret-status-cleanup-r6-owner-gate.yml")
POSTMORTEM_PATH = Path(
    "reports/benchmark/treasurebench-open-weight-cloud-runtime-r5-control-plane-postmortem.yml"
)
AUDIT_PATH = Path(
    "reports/benchmark/treasurebench-open-weight-cloud-runtime-r6b-gate-compatibility-audit.yml"
)
CORRUPTIONS_PATH = Path("docs/benchmark/agents-v1/open-weight-cloud-runtime-corruptions-r6.yml")
OUTCOME_PATH = Path("reports/benchmark/treasurebench-open-weight-secret-cleanup-outcome-r6.yml")
R5_OUTCOME_PATH = Path(
    "reports/benchmark/treasurebench-open-weight-public-calibration-outcome-r5.yml"
)
R5_HANDOFF_PATH = Path("reports/agent-ops/AO-0012-r5-live-hard-stop-handoff.yml")
RUNPOD_GRAPHQL = "https://api.runpod.io/graphql"
CREDENTIAL_NAMES = frozenset({"RUNPOD_API_KEY"})
MAX_AUTHENTICATED_OPERATIONS = 3

EXPECTED_CUMULATIVE_STATE: dict[str, object] = {
    "currency": "USD",
    "spend": "0",
    "calls": 0,
    "category_spend": {"runpod_secret_status_cleanup": "0"},
}
EXPECTED_HARD_CAPS: dict[str, object] = {
    "currency": "USD",
    "spend": "0",
    "calls": 3,
    "category_spend": {"runpod_secret_status_cleanup": "0"},
}
EXPECTED_REMAINING_CAPS = EXPECTED_HARD_CAPS


class SecretCleanupPlane(Protocol):
    operations: int

    def list_secrets(self) -> list[dict[str, str]]: ...

    def delete_secret(self, secret_id: str) -> None: ...

    def clear(self) -> None: ...


class RunPodSecretCleanupPlane:
    """Three-operation, query-key-only RunPod GraphQL cleanup transport."""

    def __init__(
        self,
        api_key: str,
        *,
        urlopen: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        _require(bool(api_key), "RunPod API key required")
        self._api_key = MutableSecret(api_key)
        self._urlopen = urlopen
        self.operations = 0

    def __repr__(self) -> str:
        return f"RunPodSecretCleanupPlane(operations={self.operations}, credential=<redacted>)"

    def clear(self) -> None:
        self._api_key.clear()

    def _graphql(self, query: str) -> dict[str, Any]:
        _require(
            self.operations < MAX_AUTHENTICATED_OPERATIONS,
            "R6 authenticated operation cap reached",
        )
        self.operations += 1
        authenticated_url = f"{RUNPOD_GRAPHQL}?api_key={quote(self._api_key.reveal(), safe='')}"
        request = urllib.request.Request(
            authenticated_url,
            data=json.dumps({"query": query, "variables": {}}).encode(),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        raw = b""
        try:
            with self._urlopen(request, timeout=20) as response:
                raw = response.read(1_000_000)
        except urllib.error.HTTPError as error:
            raise RuntimeConformanceError(f"RunPod R6 GraphQL HTTP {int(error.code)}") from None
        except Exception:
            raise RuntimeConformanceError("RunPod R6 GraphQL transport failure") from None
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise RuntimeConformanceError("RunPod R6 GraphQL malformed JSON") from None
        finally:
            raw = b""
            authenticated_url = ""
        _require(isinstance(value, Mapping), "RunPod R6 GraphQL non-object response")
        if value.get("errors"):
            raise RuntimeConformanceError("RunPod R6 GraphQL operation rejected")
        data = value.get("data")
        _require(isinstance(data, Mapping), "RunPod R6 GraphQL data missing")
        return dict(data)

    def list_secrets(self) -> list[dict[str, str]]:
        data = self._graphql("query AO0012R6SecretInventory { myself { secrets { id name } } }")
        myself = data.get("myself")
        _require(isinstance(myself, Mapping), "RunPod R6 Secret inventory missing")
        inventory = cast(Mapping[str, Any], myself)
        items = inventory.get("secrets")
        _require(isinstance(items, list), "RunPod R6 Secret inventory malformed")
        item_list = cast(list[Any], items)
        result: list[dict[str, str]] = []
        for item in item_list:
            _require(isinstance(item, Mapping), "RunPod R6 Secret item malformed")
            secret_id = item.get("id")
            name = item.get("name")
            _require(
                isinstance(secret_id, str) and bool(secret_id),
                "RunPod R6 Secret identity malformed",
            )
            _require(isinstance(name, str) and bool(name), "RunPod R6 Secret name malformed")
            result.append({"id": secret_id, "name": name})
        return result

    def delete_secret(self, secret_id: str) -> None:
        _require(bool(secret_id), "RunPod R6 exact Secret identity required")
        query = "mutation AO0012R6SecretDelete { secretDelete(id: " + json.dumps(secret_id) + ") }"
        data = self._graphql(query)
        _require(data.get("secretDelete") is True, "RunPod R6 Secret deletion unconfirmed")


def authorization_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return root / "distributed-discovery" / "agent-ops" / "authorizations" / f"{GATE_ID}.yml"


def consumption_path() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "distributed-discovery" / "agent-ops" / f"{GATE_ID}.json"


def _consume_authorization(path: Path, authorization: Mapping[str, Any]) -> None:
    _require(not path.exists(), "R6 authorization already consumed")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "ao0012-r6-authorization-consumption-v1",
        "gate_id": GATE_ID,
        "authorization_digest": str(authorization.get("authorization_digest", "synthetic-test")),
        "status": "consumed-before-credential-ingress",
    }
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def validate_canonical_caps(gate: Mapping[str, Any]) -> None:
    _require(gate.get("cumulative_state") == EXPECTED_CUMULATIVE_STATE, "cumulative state drift")
    _require(gate.get("hard_caps") == EXPECTED_HARD_CAPS, "hard cap drift")
    _require(gate.get("remaining_caps") == EXPECTED_REMAINING_CAPS, "remaining cap drift")


def validate_r6_registration(repo: Path) -> dict[str, object]:
    contract = load_yaml(repo / CONTRACT_PATH)
    _require(contract.get("task_id") == TASK_ID, "R6 task drift")
    identifiers = contract.get("frozen_identifiers")
    _require(isinstance(identifiers, Mapping), "R6 identifiers missing")
    frozen = cast(Mapping[str, Any], identifiers)
    _require(frozen.get("gate_id") == GATE_ID, "R6 gate identity drift")
    _require(frozen.get("failed_gate_id") == FAILED_GATE_ID, "failed R6 gate identity drift")
    _require(frozen.get("consumed_gate_id") == CONSUMED_GATE_ID, "R5 gate drift")
    _require(frozen.get("target_secret_name") == TARGET_SECRET_NAME, "target Secret drift")
    failed_gate = load_yaml(repo / FAILED_GATE_PATH)
    _require(failed_gate.get("gate_id") == FAILED_GATE_ID, "failed R6 gate record drift")
    postmortem = load_yaml(repo / POSTMORTEM_PATH)
    _require(
        postmortem.get("provider_presence_conclusion") == "ambiguous",
        "provider presence overclaimed",
    )
    _require(
        postmortem.get("root_cause_conclusion")
        == "ambiguous-between-conflict-inventory-and-first-secret-create",
        "R5 root cause overclaimed",
    )
    exact = postmortem.get("exact_possible_resource")
    _require(isinstance(exact, Mapping), "possible resource proof missing")
    exact_resource = cast(Mapping[str, Any], exact)
    _require(exact_resource.get("name") == TARGET_SECRET_NAME, "possible resource identity drift")
    evidence = postmortem.get("evidence")
    _require(isinstance(evidence, Mapping), "R5 evidence missing")
    evidence_map = cast(Mapping[str, Any], evidence)
    outcome_evidence = evidence_map.get("hard_stop_outcome")
    handoff_evidence = evidence_map.get("hard_stop_handoff")
    _require(isinstance(outcome_evidence, Mapping), "R5 outcome evidence missing")
    _require(isinstance(handoff_evidence, Mapping), "R5 handoff evidence missing")
    _require(
        sha256_file(repo / R5_OUTCOME_PATH)
        == cast(Mapping[str, Any], outcome_evidence).get("sha256"),
        "R5 outcome evidence drift",
    )
    _require(
        sha256_file(repo / R5_HANDOFF_PATH)
        == cast(Mapping[str, Any], handoff_evidence).get("sha256"),
        "R5 handoff evidence drift",
    )
    audit = load_yaml(repo / AUDIT_PATH)
    preparation = audit.get("preparation_activity")
    _require(isinstance(preparation, Mapping), "R6 preparation audit missing")
    preparation_map = cast(Mapping[str, Any], preparation)
    _require(
        audit.get("failed_gate_sha256") == sha256_file(repo / FAILED_GATE_PATH),
        "failed R6 gate evidence drift",
    )
    _require(
        audit.get("authorization_creation_result") == "failed-closed-before-authorization-write",
        "failed authorization result drift",
    )
    _require(preparation_map.get("real_env_txt_read") is False, "credential audit drift")
    _require(
        preparation_map.get("authenticated_provider_call") is False,
        "provider audit drift",
    )
    _require(preparation_map.get("spend_usd") == "0", "spend audit drift")
    corruptions = load_yaml(repo / CORRUPTIONS_PATH)
    cases = corruptions.get("cases")
    _require(isinstance(cases, list) and len(cases) >= 15, "R6 corruption coverage drift")
    case_list = cast(list[Any], cases)
    return {
        "contract": "pass",
        "postmortem": "pass",
        "cleanup_audit": "pass",
        "corruptions": 95 + len(case_list),
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
) -> dict[str, Any]:
    """Validate the exact R6 gate before the one-name credential loader runs."""

    validate(dict(value), "owner-authorization.schema.json")
    gate = dict(gate_override) if gate_override is not None else load_yaml(repo / GATE_PATH)
    validate(gate, "owner-gate.schema.json")
    validate_canonical_caps(gate)
    _require(value.get("gate_id") == GATE_ID, "R6 owner authorization required")
    _require(gate.get("gate_id") == GATE_ID, "R6 owner gate required")
    _require(value.get("issue") == ISSUE, "authorization issue mismatch")
    _require(value.get("pull_request") == PULL_REQUEST, "authorization PR mismatch")
    _require(value.get("branch") == BRANCH, "authorization branch mismatch")
    _require(value.get("commit") == gate["commit"], "authorization commit mismatch")
    _require(value.get("challenge") == authorization_challenge(gate), "challenge mismatch")
    contract_hash = sha256_file(repo / CONTRACT_PATH)
    _require(
        gate["task_contract"] == {"path": str(CONTRACT_PATH), "sha256": contract_hash},
        "R6 contract mismatch",
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
    branch = subprocess.run(
        ("git", "branch", "--show-current"),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
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


def validate_pre_ingress(repo: Path, authorization: Mapping[str, Any]) -> None:
    validate_r6_registration(repo)
    validate_owner_authorization(repo, authorization)


def _validate_outcome(outcome: Mapping[str, object]) -> None:
    expected_fields = {
        "schema_version",
        "task_id",
        "status",
        "failure_class",
        "target_secret_name",
        "target_secret_id",
        "authenticated_operations",
        "inventory_exact_matches",
        "delete_attempted",
        "target_absent_verified",
        "credential_names_loaded",
        "provider_body_published",
        "inference_calls",
        "spend_usd",
        "merge_or_calibration_authority",
    }
    _require(set(outcome) == expected_fields, "R6 cleanup outcome field drift")
    _require(outcome["task_id"] == TASK_ID, "R6 cleanup outcome task drift")
    _require(outcome["target_secret_name"] == TARGET_SECRET_NAME, "R6 target drift")
    _require(
        int(cast(int, outcome["authenticated_operations"])) <= MAX_AUTHENTICATED_OPERATIONS,
        "R6 operation cap exceeded",
    )
    _require(outcome["credential_names_loaded"] == ["RUNPOD_API_KEY"], "credential drift")
    _require(outcome["provider_body_published"] is False, "provider body publication rejected")
    _require(outcome["inference_calls"] == 0, "inference rejected")
    _require(outcome["spend_usd"] == "0", "spend rejected")
    _require(outcome["merge_or_calibration_authority"] is False, "authority expansion rejected")


def _write_outcome(path: Path, outcome: Mapping[str, object]) -> None:
    _validate_outcome(outcome)
    path.write_text(yaml.safe_dump(dict(outcome), sort_keys=False), encoding="utf-8")


def run_cleanup_with_plane(plane: SecretCleanupPlane) -> dict[str, object]:
    """Perform the exact one-inventory, conditional-delete, one-verification flow."""

    target_id: str | None = None
    exact_matches: int | None = None
    delete_attempted = False
    absent: bool | None = None
    failure_class: str | None = None
    try:
        inventory = plane.list_secrets()
        namespace_matches = [item for item in inventory if item["name"].startswith(f"{NAMESPACE}-")]
        matches = [item for item in namespace_matches if item["name"] == TARGET_SECRET_NAME]
        exact_matches = len(matches)
        if any(item["name"] != TARGET_SECRET_NAME for item in namespace_matches):
            failure_class = "namespace-conflict"
        elif not matches:
            absent = True
        elif len(matches) != 1:
            failure_class = "namespace-conflict"
        else:
            target_id = matches[0]["id"]
            delete_attempted = True
            try:
                plane.delete_secret(target_id)
            except Exception:
                failure_class = "deletion-transport-ambiguity"
            try:
                verification = plane.list_secrets()
                verification_namespace = [
                    item for item in verification if item["name"].startswith(f"{NAMESPACE}-")
                ]
                if any(item["name"] != TARGET_SECRET_NAME for item in verification_namespace):
                    failure_class = "verification-ambiguity"
                else:
                    remaining = [
                        item
                        for item in verification_namespace
                        if item["name"] == TARGET_SECRET_NAME
                    ]
                    absent = not remaining
                    if remaining:
                        failure_class = "verification-ambiguity"
                    elif failure_class == "deletion-transport-ambiguity":
                        failure_class = None
            except Exception:
                absent = None
                failure_class = "verification-ambiguity"
    except Exception:
        failure_class = "inventory-ambiguity"
    outcome: dict[str, object] = {
        "schema_version": "treasurebench-open-weight-secret-cleanup-outcome-r6-v1",
        "task_id": TASK_ID,
        "status": "verified" if failure_class is None and absent is True else "hard-stop",
        "failure_class": failure_class,
        "target_secret_name": TARGET_SECRET_NAME,
        "target_secret_id": target_id,
        "authenticated_operations": plane.operations,
        "inventory_exact_matches": exact_matches,
        "delete_attempted": delete_attempted,
        "target_absent_verified": absent,
        "credential_names_loaded": ["RUNPOD_API_KEY"],
        "provider_body_published": False,
        "inference_calls": 0,
        "spend_usd": "0",
        "merge_or_calibration_authority": False,
    }
    _validate_outcome(outcome)
    return outcome


def run_live_cleanup(
    repo: Path,
    *,
    credential_loader: Callable[..., CredentialSet] = load_credentials,
    plane_factory: Callable[[str], SecretCleanupPlane] = RunPodSecretCleanupPlane,
    authorization_file: Path | None = None,
    consumption_file: Path | None = None,
    pre_ingress_validator: Callable[[Path, Mapping[str, Any]], None] = validate_pre_ingress,
    outcome_path: Path = OUTCOME_PATH,
) -> dict[str, object]:
    """Run the exact R6 cleanup only after a valid, unconsumed R6 authorization."""

    auth_file = authorization_file or authorization_path()
    _require(auth_file.exists(), "R6 owner authorization required")
    metadata = auth_file.lstat()
    _require(stat.S_ISREG(metadata.st_mode), "authorization must be regular")
    _require(stat.S_IMODE(metadata.st_mode) == 0o600, "authorization mode must be 0600")
    authorization = load_yaml(auth_file)
    pre_ingress_validator(repo, authorization)
    consumed = consumption_file or consumption_path()
    _consume_authorization(consumed, authorization)
    credentials: CredentialSet | None = None
    plane: SecretCleanupPlane | None = None
    runpod_value = ""
    try:
        credentials = credential_loader(
            repo / ".env.txt",
            explicit_live_mode=True,
            requested_names=CREDENTIAL_NAMES,
        )
        runpod_value = credentials.get_secret("RUNPOD_API_KEY") or ""
        _require(bool(runpod_value), "RUNPOD_API_KEY required")
        plane = plane_factory(runpod_value)
        outcome = run_cleanup_with_plane(plane)
        _write_outcome(repo / outcome_path, outcome)
        return outcome
    finally:
        if credentials is not None:
            credentials.clear()
        runpod_value = ""
        if plane is not None:
            plane.clear()


def run_offline_rehearsal(repo: Path) -> dict[str, object]:
    result = run_r5_offline_rehearsal(repo)
    result["r6_registration"] = validate_r6_registration(repo)
    result["r6_gate"] = GATE_ID
    result["consumed_r5_gate"] = CONSUMED_GATE_ID
    result["target_secret_name"] = TARGET_SECRET_NAME
    result["credential_names"] = sorted(CREDENTIAL_NAMES)
    result["maximum_authenticated_operations"] = MAX_AUTHENTICATED_OPERATIONS
    result["live_action"] = False
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--rehearsal", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    result = run_live_cleanup(args.repo) if args.live else run_offline_rehearsal(args.repo)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
