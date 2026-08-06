"""AO-0012 R2 preauthorized live lifecycle and fail-closed control plane.

Importing this module is authorization-free: it performs no credential read,
network request, model download, GPU operation, inference call, or spend.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import stat
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol, cast

import yaml
from jsonschema import Draft202012Validator

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
    CONTAINER_DIGEST,
    MODEL_NAME,
    MODEL_REVISION,
    RUNTIME_IDENTITY,
    RuntimeConformanceError,
    _canonical_digest,
    _run_public_matrix,
    _run_synthetic_public_matrix,
    _verify_public_bounds,
    attestation_signature,
    validate_registration,
)
from distributed_discovery.benchmark.agents_v1.provider_outcome import (
    PairingClassificationV3,
)

TASK_ID = "AO-0012"
ISSUE = 212
PULL_REQUEST = 213
BRANCH = "agent/treasurebench-open-weight-cloud-runtime"
GATE_ID = "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R2"
SUPERSEDED_GATE_ID = "AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION"
CONTRACT_PATH = Path("tasks/treasurebench-open-weight-cloud-runtime-r2.yml")
GATE_PATH = Path("reports/agent-ops/AO-0012-open-weight-public-calibration-r2-owner-gate.yml")
MANIFEST_PATH = Path("docs/benchmark/agents-v1/open-weight-cloud-runtime-manifest-r2.yml")
STARTUP_PATH = Path("scripts/treasurebench_open_weight_runtime_start_r2.sh")
PROXY_PATH = Path("scripts/treasurebench_open_weight_proxy_r2.py")
OUTCOME_PATH = Path("reports/benchmark/treasurebench-open-weight-public-calibration-outcome-r2.yml")
OUTCOME_SCHEMA_PATH = Path(
    "docs/benchmark/agents-v1/open-weight-public-calibration-outcome-r2.schema.json"
)
CREDENTIAL_PATH = Path(".env.txt")
CREDENTIAL_NAMES = frozenset({"RUNPOD_API_KEY", "HF_TOKEN"})
MAX_GPU_SECONDS = 21_600
MAX_BILLED_MS = 21_600_000
MAX_CALLS = 400
HARD_CAP = Decimal("20")
EXPECTED_CAP = Decimal("10")
RUNPOD_GRAPHQL = "https://api.runpod.io/graphql"
RUNPOD_REST = "https://rest.runpod.io/v1"
MISTRAL_COMMON_MINIMUM = "1.11.3"
RUNPODCTL_VERSION = "2.8.0"
RUNPODCTL_RELEASE_COMMIT = "v2.8.0"
AUTO_TERMINATION_CONTROL = "podFindAndDeployOnDemand.terminateAfter"
FAILURE_CLASSES = frozenset(
    {
        "pod-create-rejected-before-resource-creation",
        "ambiguous-create-reconciled-and-deleted",
        "exact-hardware-or-secure-cloud-unavailable",
        "hourly-rate-above-prospective-cap",
        "container-image-identity-mismatch",
        "driver-cuda-runtime-attestation-mismatch",
        "artifact-download-or-checksum-failure",
        "engine-startup-readiness-failure",
        "endpoint-authentication-control-failure",
        "calibration-contract-safety-failure",
        "circuit-breaker-or-runtime-cap-failure",
        "teardown-ambiguity",
        "secret-template-deletion-ambiguity",
        "billing-reconciliation-unavailable",
        "calibration-integrity-failure",
    }
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeConformanceError(message)


def _numeric_version(value: object) -> tuple[int, ...]:
    parts = str(value).split(".")
    _require(bool(parts) and all(part.isdigit() for part in parts), "malformed version")
    return tuple(int(part) for part in parts)


class MutableSecret:
    """Best-effort mutable secret storage with an explicit clearing invariant."""

    __slots__ = ("_value", "cleared")

    def __init__(self, value: str) -> None:
        self._value = bytearray(value.encode())
        self.cleared = False

    def reveal(self) -> str:
        _require(not self.cleared, "secret already cleared")
        return self._value.decode()

    def clear(self) -> None:
        for index in range(len(self._value)):
            self._value[index] = 0
        self._value.clear()
        self.cleared = True

    def __repr__(self) -> str:
        return "MutableSecret(<redacted>)"


@dataclass(frozen=True)
class ResourceRef:
    id: str
    name: str


@dataclass
class Lifecycle:
    namespace: str
    authorization_digest: str
    started_at: datetime
    pod_id: str | None = None
    possible_pod: bool = False
    template: ResourceRef | None = None
    secrets: list[ResourceRef] = field(default_factory=list)
    dispatch_stopped: bool = False
    pod_deleted: bool | None = None
    pod_unaddressable: bool | None = None
    volume_deleted: bool | None = None
    template_deleted: bool | None = None
    secrets_deleted: bool | None = None
    billing: BillingRecord | None = None


@dataclass(frozen=True)
class BillingRecord:
    amount_usd: Decimal
    billed_milliseconds: int
    disk_space_billed_gb: Decimal
    record_count: int


@dataclass(frozen=True)
class Finalization:
    exact: bool
    hard_stop_class: str | None
    remediation: tuple[str, ...]


class ControlPlane(Protocol):
    def list_pods(self) -> list[dict[str, Any]]: ...
    def list_templates(self) -> list[dict[str, Any]]: ...
    def list_secrets(self) -> list[dict[str, Any]]: ...
    def create_secret(self, name: str, value: str) -> ResourceRef: ...
    def delete_secret(self, resource: ResourceRef) -> None: ...
    def create_template(self, spec: Mapping[str, object]) -> ResourceRef: ...
    def delete_template(self, resource: ResourceRef) -> None: ...
    def create_pod(self, spec: Mapping[str, object]) -> dict[str, Any]: ...
    def delete_pod(self, pod_id: str) -> None: ...
    def get_pod(self, pod_id: str) -> dict[str, Any] | None: ...
    def billing(self, pod_id: str, started_at: datetime) -> BillingRecord: ...


class RunPodControlPlane:
    """Official GraphQL/REST operations with redacted exception surfaces."""

    def __init__(self, api_key: str) -> None:
        self._api_key = MutableSecret(api_key)

    def clear(self) -> None:
        self._api_key.clear()

    def _request(
        self,
        url: str,
        *,
        method: str = "GET",
        body: Mapping[str, object] | None = None,
    ) -> Any:
        request = urllib.request.Request(
            url,
            data=None if body is None else json.dumps(body).encode(),
            method=method,
            headers={
                "Authorization": f"Bearer {self._api_key.reveal()}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read(2_000_000)
        except urllib.error.HTTPError as error:
            raise RuntimeConformanceError(f"RunPod control-plane HTTP {error.code}") from None
        except (TimeoutError, urllib.error.URLError):
            raise RuntimeConformanceError("RunPod control-plane transport failure") from None
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeConformanceError("RunPod control-plane malformed JSON") from None

    def _graphql(self, query: str, variables: Mapping[str, object]) -> dict[str, Any]:
        value = self._request(
            RUNPOD_GRAPHQL,
            method="POST",
            body={"query": query, "variables": dict(variables)},
        )
        _require(isinstance(value, Mapping), "RunPod GraphQL non-object response")
        if value.get("errors"):
            raise RuntimeConformanceError("RunPod GraphQL operation rejected")
        data = value.get("data")
        _require(isinstance(data, Mapping), "RunPod GraphQL data missing")
        return dict(data)

    def _inventory(self) -> dict[str, list[dict[str, Any]]]:
        query = """
        query AO0012Inventory {
          myself {
            pods { id name createdAt templateId desiredStatus volumeInGb networkVolumeId }
            podTemplates { id name imageName }
            secrets { id name }
          }
        }
        """
        data = self._graphql(query, {})
        myself = data.get("myself")
        if not isinstance(myself, Mapping):
            raise RuntimeConformanceError("RunPod inventory missing")
        result: dict[str, list[dict[str, Any]]] = {}
        for key in ("pods", "podTemplates", "secrets"):
            value = myself.get(key, [])
            _require(isinstance(value, list), f"RunPod inventory {key} malformed")
            result[key] = [dict(item) for item in value if isinstance(item, Mapping)]
        return result

    def list_pods(self) -> list[dict[str, Any]]:
        return self._inventory()["pods"]

    def list_templates(self) -> list[dict[str, Any]]:
        return self._inventory()["podTemplates"]

    def list_secrets(self) -> list[dict[str, Any]]:
        return self._inventory()["secrets"]

    def create_secret(self, name: str, value: str) -> ResourceRef:
        query = (
            "mutation AO0012SecretCreate { secretCreate(input: { name: "
            + json.dumps(name)
            + ", value: "
            + json.dumps(value)
            + " }) { id name } }"
        )
        data = self._graphql(query, {})
        item = data.get("secretCreate")
        if not isinstance(item, Mapping):
            raise RuntimeConformanceError("RunPod secret creation missing identity")
        return ResourceRef(id=str(item["id"]), name=str(item["name"]))

    def delete_secret(self, resource: ResourceRef) -> None:
        query = "mutation AO0012SecretDelete { secretDelete(id: " + json.dumps(resource.id) + ") }"
        self._graphql(query, {})

    def create_template(self, spec: Mapping[str, object]) -> ResourceRef:
        item = self._request(
            f"{RUNPOD_REST}/templates",
            method="POST",
            body=spec,
        )
        if not isinstance(item, Mapping):
            raise RuntimeConformanceError("RunPod template creation missing identity")
        return ResourceRef(id=str(item["id"]), name=str(item["name"]))

    def delete_template(self, resource: ResourceRef) -> None:
        self._request(
            f"{RUNPOD_REST}/templates/{resource.id}",
            method="DELETE",
        )

    def create_pod(self, spec: Mapping[str, object]) -> dict[str, Any]:
        query = """
        mutation AO0012PodCreate($input: PodFindAndDeployOnDemandInput!) {
          podFindAndDeployOnDemand(input: $input) {
            id name imageName desiredStatus costPerHr containerDiskInGb
            volumeInGb volumeMountPath gpuCount templateId createdAt
            volumeEncrypted networkVolumeId podType
            machine { gpuDisplayName location secureCloud }
          }
        }
        """
        data = self._graphql(query, {"input": dict(spec)})
        item = data.get("podFindAndDeployOnDemand")
        if not isinstance(item, Mapping):
            raise RuntimeConformanceError("RunPod Pod creation missing identity")
        return dict(item)

    def delete_pod(self, pod_id: str) -> None:
        self._request(f"{RUNPOD_REST}/pods/{pod_id}", method="DELETE")

    def get_pod(self, pod_id: str) -> dict[str, Any] | None:
        try:
            value = self._request(f"{RUNPOD_REST}/pods/{pod_id}")
        except RuntimeConformanceError as error:
            if "HTTP 404" in str(error):
                return None
            raise
        _require(isinstance(value, Mapping), "RunPod Pod lookup malformed")
        return dict(value)

    def billing(self, pod_id: str, started_at: datetime) -> BillingRecord:
        from urllib.parse import urlencode

        query = urlencode(
            {
                "bucketSize": "hour",
                "grouping": "podId",
                "podId": pod_id,
                "startTime": started_at.isoformat().replace("+00:00", "Z"),
                "endTime": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
        )
        for _ in range(30):
            value = self._request(f"{RUNPOD_REST}/billing/pods?{query}")
            if isinstance(value, list):
                rows = [
                    item
                    for item in value
                    if isinstance(item, Mapping) and item.get("podId") == pod_id
                ]
                amount = sum((Decimal(str(item.get("amount", 0))) for item in rows), Decimal())
                milliseconds = sum(int(str(item.get("timeBilledMs", 0))) for item in rows)
                disk = sum(
                    (Decimal(str(item.get("diskSpaceBilledGb", 0))) for item in rows),
                    Decimal(),
                )
                if amount > 0 and milliseconds > 0:
                    return BillingRecord(amount, milliseconds, disk, len(rows))
            time.sleep(10)
        raise RuntimeConformanceError("billing reconciliation unavailable")


def validate_r2_registration(repo: Path) -> dict[str, object]:
    manifest = load_yaml(repo / MANIFEST_PATH)
    _require(
        manifest.get("schema_version") == "treasurebench-open-weight-cloud-runtime-manifest-r2-v1",
        "R2 manifest schema drift",
    )
    _require(manifest.get("runtime_identity") == RUNTIME_IDENTITY, "runtime identity drift")
    _require(manifest["model"]["revision"] == MODEL_REVISION, "model revision drift")
    _require(manifest["model"]["precision"] == "BF16", "precision drift")
    _require(manifest["model"]["quantized"] is False, "quantization rejected")
    _require(manifest["compute"]["gpu_type_id"] == "NVIDIA A100 80GB PCIe", "GPU drift")
    _require(manifest["compute"]["gpu_count"] == 1, "GPU count drift")
    _require(manifest["engine"]["version"] == "0.23.0", "engine drift")
    _require(manifest["engine"]["tensor_parallel_size"] == 1, "sharding drift")
    _require(
        manifest["tokenizer"]["sha256"]
        == "c604f35d1035f534519622c0ec83fed6184978d4fdee92a5bd2a50bc05438094",
        "tokenizer checksum drift",
    )
    contract = load_yaml(repo / CONTRACT_PATH)
    _require(contract.get("task_id") == TASK_ID, "R2 task drift")
    _require(
        contract["frozen_identifiers"]["gate_id"] == GATE_ID,
        "R2 gate identity drift",
    )
    _require(
        contract["frozen_identifiers"]["superseded_gate_id"] == SUPERSEDED_GATE_ID,
        "R1 supersession drift",
    )
    audit_path = Path(
        "reports/benchmark/treasurebench-open-weight-cloud-runtime-r2-preauthorization-audit.yml"
    )
    audit = load_yaml(repo / audit_path)
    _require(audit.get("credential_read") is False, "credential-read audit drift")
    _require(audit.get("provider_call") is False, "provider-call audit drift")
    _require(audit.get("spend_usd") == "0", "spend audit drift")
    corruptions_path = Path("docs/benchmark/agents-v1/open-weight-cloud-runtime-corruptions-r2.yml")
    corruptions = load_yaml(repo / corruptions_path)
    cases = corruptions.get("cases")
    if not isinstance(cases, list) or len(cases) < 36:
        raise RuntimeConformanceError("R2 corruption coverage drift")
    _require(
        corruptions.get("credential_source_read") is False,
        "synthetic credential boundary drift",
    )
    for path in (STARTUP_PATH, PROXY_PATH):
        _require((repo / path).is_file(), f"R2 deployment file missing: {path}")
    return {
        "manifest": "pass",
        "contract": "pass",
        "preauthorization_audit": "pass",
        "corruptions": len(cases),
        "credential_read": False,
        "provider_call": False,
        "spend_usd": "0",
    }


def authorization_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return root / "distributed-discovery" / "agent-ops" / "authorizations" / f"{GATE_ID}.yml"


def _validate_live_github_and_git(repo: Path, gate: Mapping[str, Any]) -> None:
    status = subprocess.run(
        ("git", "status", "--porcelain", "--untracked-files=no"),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    _require(not status.strip(), "tracked worktree must be clean before credential ingress")
    local_head = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    issue_raw = subprocess.run(
        (
            "gh",
            "issue",
            "view",
            str(ISSUE),
            "--repo",
            "yoheinakajima/distributed-discovery",
            "--json",
            "number,state",
        ),
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    issue = json.loads(issue_raw)
    _require(issue == {"number": ISSUE, "state": "OPEN"}, "live issue state mismatch")
    pr_raw = subprocess.run(
        (
            "gh",
            "pr",
            "view",
            str(PULL_REQUEST),
            "--repo",
            "yoheinakajima/distributed-discovery",
            "--json",
            "number,state,isDraft,headRefName,headRefOid",
        ),
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    pr = json.loads(pr_raw)
    _require(pr.get("number") == PULL_REQUEST, "live PR identity mismatch")
    _require(pr.get("state") == "OPEN" and pr.get("isDraft") is True, "live draft PR required")
    _require(pr.get("headRefName") == BRANCH, "live PR branch mismatch")
    _require(pr.get("headRefOid") == local_head, "local and live PR head mismatch")
    _require(
        gate["pull_request"]["number"] == PULL_REQUEST,
        "gate PR identity mismatch",
    )


def state_path() -> Path:
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "distributed-discovery" / "agent-ops" / f"{GATE_ID}.json"


def _authorization_digest(value: Mapping[str, object]) -> str:
    unsigned = dict(value)
    unsigned.pop("authorization_digest", None)
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def validate_owner_authorization(repo: Path, value: Mapping[str, Any]) -> dict[str, Any]:
    validate(dict(value), "owner-authorization.schema.json")
    gate = load_yaml(repo / GATE_PATH)
    validate(gate, "owner-gate.schema.json")
    _require(False, "R2 owner gate was superseded unused and may never be used")
    _require(value.get("gate_id") == GATE_ID, "R2 owner authorization required")
    _require(value.get("issue") == ISSUE, "authorization issue mismatch")
    _require(value.get("branch") == BRANCH, "authorization branch mismatch")
    _require(value.get("commit") == gate["commit"], "authorization commit mismatch")
    _require(value.get("challenge") == authorization_challenge(gate), "challenge mismatch")
    _require(
        value.get("task_contract_sha256") == sha256_file(repo / CONTRACT_PATH),
        "R2 contract mismatch",
    )
    _require(value.get("tree_hashes") == gate["tree_hashes"], "protected tree mismatch")
    _require(
        value.get("authorization_digest") == _authorization_digest(value),
        "authorization digest mismatch",
    )
    now = datetime.now(UTC)
    authorized = datetime.fromisoformat(str(value["authorized_at_utc"]).replace("Z", "+00:00"))
    expires = datetime.fromisoformat(str(value["expires_at_utc"]).replace("Z", "+00:00"))
    _require(authorized <= now < expires, "authorization outside active interval")
    for relative, expected in gate["tree_hashes"].items():
        _require(hash_path(repo / relative) == expected, f"authorized tree drift: {relative}")
    current_branch = subprocess.run(
        ("git", "branch", "--show-current"),
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _require(current_branch == BRANCH, "live branch mismatch")
    ancestry = subprocess.run(
        ("git", "merge-base", "--is-ancestor", str(value["commit"]), "HEAD"),
        cwd=repo,
        check=False,
        capture_output=True,
    )
    _require(ancestry.returncode == 0, "execution commit is not an ancestor")
    _validate_live_github_and_git(repo, gate)
    return gate


def namespace_for(authorization_digest: str) -> str:
    _require(authorization_digest.startswith("sha256:"), "authorization digest format")
    suffix = authorization_digest.removeprefix("sha256:")[:16]
    _require(len(suffix) == 16 and all(c in "0123456789abcdef" for c in suffix), "digest")
    return f"ao0012-owcal-r2-{suffix}"


def validate_pre_ingress(repo: Path, authorization: Mapping[str, Any]) -> Lifecycle:
    validate_registration(repo)
    validate_owner_authorization(repo, authorization)
    _require(not state_path().exists(), "existing AO-0012 live resource or ledger conflict")
    digest = str(authorization["authorization_digest"])
    return Lifecycle(namespace_for(digest), digest, datetime.now(UTC))


def _secret_names(namespace: str) -> dict[str, str]:
    return {
        "hf": f"{namespace}-hf",
        "endpoint": f"{namespace}-endpoint",
        "attestation": f"{namespace}-attestation",
    }


def _secret_reference(name: str) -> str:
    return f"{{{{ RUNPOD_SECRET_{name} }}}}"


def build_template_spec(repo: Path, namespace: str) -> dict[str, object]:
    manifest_bytes = (repo / MANIFEST_PATH).read_bytes()
    startup = (repo / STARTUP_PATH).read_bytes()
    proxy = (repo / PROXY_PATH).read_bytes()
    names = _secret_names(namespace)
    environment = {
        "HF_TOKEN": _secret_reference(names["hf"]),
        "TREASUREBENCH_RUNTIME_API_KEY": _secret_reference(names["endpoint"]),
        "TREASUREBENCH_RUNTIME_ATTESTATION_KEY": _secret_reference(names["attestation"]),
        "TREASUREBENCH_EXPECTED_IMAGE_DIGEST": CONTAINER_DIGEST,
        "TREASUREBENCH_RUNTIME_MANIFEST_B64": base64.b64encode(manifest_bytes).decode(),
        "TREASUREBENCH_STARTUP_SCRIPT_B64": base64.b64encode(startup).decode(),
        "TREASUREBENCH_PROXY_SCRIPT_B64": base64.b64encode(proxy).decode(),
    }
    launch = (
        "umask 077; printf '%s' \"$TREASUREBENCH_STARTUP_SCRIPT_B64\" "
        "| base64 --decode >/tmp/treasurebench-r2-start.sh; "
        "chmod 700 /tmp/treasurebench-r2-start.sh; "
        "exec /tmp/treasurebench-r2-start.sh"
    )
    return {
        "name": namespace,
        "imageName": (
            "vllm/vllm-openai@"
            "sha256:3a1e7f5904e1a1192a02aa0086ceaffc33985d7044c7bb25b3a43d61bdbe3ac0"
        ),
        "containerDiskInGb": 50,
        "volumeInGb": 120,
        "volumeMountPath": "/workspace",
        "ports": ["8000/http"],
        "dockerEntrypoint": ["/bin/bash"],
        "dockerStartCmd": ["-lc", launch],
        "env": environment,
        "isPublic": False,
        "isServerless": False,
    }


def build_pod_spec(namespace: str, template_id: str, now: datetime) -> dict[str, object]:
    return {
        "name": namespace,
        "cloudType": "SECURE",
        "gpuCount": 1,
        "gpuTypeId": "NVIDIA A100 80GB PCIe",
        "templateId": template_id,
        "containerDiskInGb": 50,
        "volumeInGb": 120,
        "volumeMountPath": "/workspace",
        "countryCode": "US",
        "minCudaVersion": "13.0",
        "startSsh": False,
        "supportPublicIp": False,
        "terminateAfter": (now + timedelta(hours=6)).isoformat().replace("+00:00", "Z"),
    }


def _matches_namespace(items: list[dict[str, Any]], namespace: str) -> list[dict[str, Any]]:
    return [item for item in items if item.get("name") == namespace]


def require_remote_conflict_free(plane: ControlPlane, namespace: str) -> None:
    _require(not _matches_namespace(plane.list_pods(), namespace), "duplicate Pod namespace")
    _require(
        not _matches_namespace(plane.list_templates(), namespace),
        "duplicate template namespace",
    )
    secret_names = set(_secret_names(namespace).values())
    _require(
        not [item for item in plane.list_secrets() if item.get("name") in secret_names],
        "duplicate secret namespace",
    )


def validate_measured_attestation(
    value: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    key: str,
) -> None:
    signature = value.get("signature")
    if not isinstance(signature, str):
        raise RuntimeConformanceError("attestation signature missing")
    unsigned = dict(value)
    unsigned.pop("signature", None)
    _require(
        secrets.compare_digest(signature, attestation_signature(unsigned, key)),
        "attestation signature mismatch",
    )
    _require(value.get("evidence_class") == "measured-runtime-r2", "manifest echo rejected")
    _require(value.get("runtime_identity") == RUNTIME_IDENTITY, "runtime identity drift")
    _require(value.get("manifest_sha256") == _canonical_digest(manifest), "manifest drift")
    _require(value.get("image_digest") == CONTAINER_DIGEST, "container digest drift")
    _require(value.get("model_revision") == MODEL_REVISION, "model revision drift")
    _require(
        value.get("model_weight_sha256") == manifest["model"]["primary_weight"]["sha256"],
        "weight hash drift",
    )
    _require(value.get("tokenizer_sha256") == manifest["tokenizer"]["sha256"], "tokenizer drift")
    _require(value.get("vllm_version") == "0.23.0", "vLLM drift")
    _require(
        _numeric_version(value.get("mistral_common_version"))
        >= _numeric_version(MISTRAL_COMMON_MINIMUM),
        "mistral-common below minimum",
    )
    _require(value.get("gpu_names") == ["NVIDIA A100 80GB PCIe"], "measured GPU drift")
    _require(value.get("gpu_count") == 1, "measured GPU count drift")
    memories = value.get("gpu_memory_mib")
    if not isinstance(memories, list) or len(memories) != 1:
        raise RuntimeConformanceError("GPU memory missing")
    _require(int(str(memories[0])) >= 80_000, "measured GPU memory below A100 80GB class")
    _require(
        _numeric_version(value.get("driver_version"))
        >= _numeric_version(manifest["compute"]["minimum_linux_driver_version"]),
        "driver below minimum",
    )
    _require(value.get("requested_cuda_compatibility_class") == "13.0", "CUDA class drift")
    _require(
        str(value.get("measured_container_cuda_toolkit", "")).startswith("13.0"),
        "measured container CUDA drift",
    )
    _require(
        str(value.get("pytorch_cuda_runtime", "")).startswith("13.0"),
        "PyTorch CUDA runtime drift",
    )
    _require(value.get("quantization") in (None, "none"), "quantization rejected")
    _require(value.get("tensor_parallel_size") == 1, "sharding rejected")
    _require(int(value.get("startup_seconds", 0)) > 0, "startup time not measured")
    _require(int(value.get("model_load_seconds", 0)) > 0, "model load time not measured")


def _write_state(path: Path, lifecycle: Lifecycle) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "ao0012-r2-local-lifecycle-v1",
        "namespace": lifecycle.namespace,
        "authorization_digest": lifecycle.authorization_digest,
        "pod_id": lifecycle.pod_id,
        "template_id": None if lifecycle.template is None else lifecycle.template.id,
        "secret_ids": [resource.id for resource in lifecycle.secrets],
        "started_at": lifecycle.started_at.isoformat().replace("+00:00", "Z"),
    }
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def reconcile_ambiguous_create(
    plane: ControlPlane,
    lifecycle: Lifecycle,
    *,
    window_seconds: int = 300,
) -> str | None:
    matches = _matches_namespace(plane.list_pods(), lifecycle.namespace)
    recent: list[dict[str, Any]] = []
    for item in matches:
        created = datetime.fromisoformat(str(item["createdAt"]).replace("Z", "+00:00"))
        if abs((created - lifecycle.started_at).total_seconds()) <= window_seconds:
            recent.append(item)
    _require(len(recent) <= 1, "multiple exact namespace Pods after ambiguous create")
    if not recent:
        return None
    pod_id = str(recent[0]["id"])
    lifecycle.pod_id = pod_id
    lifecycle.possible_pod = True
    return pod_id


def finalize_lifecycle(
    plane: ControlPlane,
    lifecycle: Lifecycle,
    *,
    poll: Callable[[float], None] = time.sleep,
) -> Finalization:
    lifecycle.dispatch_stopped = True
    remediation: list[str] = []
    failures: list[str] = []
    if lifecycle.pod_id:
        try:
            plane.delete_pod(lifecycle.pod_id)
            lifecycle.pod_deleted = True
            absent = False
            for _ in range(24):
                if plane.get_pod(lifecycle.pod_id) is None:
                    absent = True
                    break
                poll(5)
            lifecycle.pod_unaddressable = absent
            lifecycle.volume_deleted = absent
            if not absent:
                failures.append("teardown-ambiguity")
                remediation.append(f"runpodctl pod get {lifecycle.pod_id}")
        except Exception:
            lifecycle.pod_deleted = False
            lifecycle.pod_unaddressable = False
            lifecycle.volume_deleted = False
            failures.append("teardown-ambiguity")
            remediation.append(f"runpodctl pod get {lifecycle.pod_id}")
    if lifecycle.template:
        try:
            plane.delete_template(lifecycle.template)
            for _ in range(24):
                if not [
                    item
                    for item in plane.list_templates()
                    if item.get("id") == lifecycle.template.id
                    or item.get("name") == lifecycle.template.name
                ]:
                    lifecycle.template_deleted = True
                    break
                poll(5)
            if lifecycle.template_deleted is not True:
                failures.append("secret-template-deletion-ambiguity")
                remediation.append("runpodctl template list --type user")
        except Exception:
            lifecycle.template_deleted = False
            failures.append("secret-template-deletion-ambiguity")
            remediation.append("runpodctl template list --type user")
    secret_exact = True
    for resource in reversed(lifecycle.secrets):
        try:
            plane.delete_secret(resource)
        except Exception:
            secret_exact = False
    try:
        for _ in range(24):
            remaining = plane.list_secrets()
            if not any(
                item.get("id") == resource.id or item.get("name") == resource.name
                for item in remaining
                for resource in lifecycle.secrets
            ):
                break
            poll(5)
        else:
            secret_exact = False
    except Exception:
        secret_exact = False
    lifecycle.secrets_deleted = secret_exact
    if not secret_exact:
        failures.append("secret-template-deletion-ambiguity")
        remediation.append("query { myself { secrets { id name } } }")
    if lifecycle.pod_id:
        try:
            lifecycle.billing = plane.billing(lifecycle.pod_id, lifecycle.started_at)
            _require(lifecycle.billing.amount_usd > 0, "nonpositive exact Pod bill")
            _require(lifecycle.billing.billed_milliseconds > 0, "nonpositive billed time")
            _require(
                lifecycle.billing.amount_usd <= HARD_CAP,
                "hard total cost cap exceeded",
            )
            _require(
                lifecycle.billing.billed_milliseconds <= MAX_BILLED_MS,
                "six GPU-hour billed-time cap exceeded",
            )
        except Exception:
            failures.append("billing-reconciliation-unavailable")
            remediation.append(f"GET /v1/billing/pods?podId={lifecycle.pod_id}")
    hard = failures[0] if failures else None
    return Finalization(not failures, hard, tuple(dict.fromkeys(remediation)))


def operational_projections(
    *,
    fixed_seconds: Decimal,
    generation_seconds: Decimal,
    exact_cost: Decimal,
    tokens: int,
    calls: int,
    retries: int,
    peak_gpu_memory_mib: int,
) -> dict[str, object]:
    total = fixed_seconds + generation_seconds
    _require(total > 0 and generation_seconds > 0, "projection durations must be positive")
    fixed_cost = exact_cost * fixed_seconds / total
    marginal_cost = exact_cost - fixed_cost
    return {
        "fixed_startup_download_model_load_seconds": str(fixed_seconds),
        "fixed_startup_download_model_load_cost_usd": str(fixed_cost),
        "marginal_50_pairing_generation_seconds": str(generation_seconds),
        "marginal_50_pairing_generation_cost_usd": str(marginal_cost),
        "observed_tokens_per_second": str(Decimal(tokens) / generation_seconds),
        "observed_calls": calls,
        "observed_retries": retries,
        "peak_measured_gpu_memory_mib": peak_gpu_memory_mib,
        "open_weight_arm_continuous_runtime": {
            "pairings": 3000,
            "seconds": str(fixed_seconds + generation_seconds * Decimal(60)),
            "cost_usd": str(fixed_cost + marginal_cost * Decimal(60)),
        },
        "open_weight_arm_repeated_batch_upper_bound": {
            "pairings": 3000,
            "seconds": str(total * Decimal(60)),
            "cost_usd": str(exact_cost * Decimal(60)),
        },
        "complete_9000_pairing_mechanical_reference": {
            "pairings": 9000,
            "continuous_seconds": str(fixed_seconds + generation_seconds * Decimal(180)),
            "continuous_self_operated_cost_usd": str(fixed_cost + marginal_cost * Decimal(180)),
            "interpretation": (
                "mechanical runtime reference only; OpenAI and Anthropic costs "
                "are not supplied by this calibration"
            ),
        },
    }


def run_offline_rehearsal(repo: Path) -> dict[str, object]:
    registration = validate_registration(repo)
    r2_registration = validate_r2_registration(repo)
    template = build_template_spec(repo, "ao0012-owcal-r2-0123456789abcdef")
    env = cast(Mapping[str, str], template["env"])
    _require(
        all(
            env[name].startswith("{{ RUNPOD_SECRET_")
            for name in (
                "HF_TOKEN",
                "TREASUREBENCH_RUNTIME_API_KEY",
                "TREASUREBENCH_RUNTIME_ATTESTATION_KEY",
            )
        ),
        "template raw secret detected",
    )
    matrix = _run_synthetic_public_matrix()
    projections = operational_projections(
        fixed_seconds=Decimal("1200"),
        generation_seconds=Decimal("600"),
        exact_cost=Decimal("0.695"),
        tokens=6000,
        calls=int(str(matrix["calls"])),
        retries=0,
        peak_gpu_memory_mib=70_000,
    )
    return {
        **registration,
        "r2_registration": r2_registration,
        "r2_gate": GATE_ID,
        "superseded_gate": SUPERSEDED_GATE_ID,
        "credential_source": ".env.txt",
        "credential_names": sorted(CREDENTIAL_NAMES),
        "template_secret_references_only": True,
        "server_side_auto_termination": {
            "control": AUTO_TERMINATION_CONTROL,
            "runpodctl_version_audit": RUNPODCTL_VERSION,
            "duration_seconds": MAX_GPU_SECONDS,
        },
        "synthetic_public_matrix": matrix,
        "synthetic_projections": projections,
        "live_action": False,
    }


def _classify_failure(error: Exception, *, possible_pod: bool) -> str:
    text = str(error).lower()
    mapping = (
        ("ambiguous create reconciled", "ambiguous-create-reconciled-and-deleted"),
        ("create rejected before", "pod-create-rejected-before-resource-creation"),
        ("multiple exact namespace", "teardown-ambiguity"),
        ("hourly", "hourly-rate-above-prospective-cap"),
        ("gpu", "exact-hardware-or-secure-cloud-unavailable"),
        ("image", "container-image-identity-mismatch"),
        ("cuda", "driver-cuda-runtime-attestation-mismatch"),
        ("driver", "driver-cuda-runtime-attestation-mismatch"),
        ("checksum", "artifact-download-or-checksum-failure"),
        ("artifact", "artifact-download-or-checksum-failure"),
        ("readiness", "engine-startup-readiness-failure"),
        ("endpoint", "endpoint-authentication-control-failure"),
        ("circuit", "circuit-breaker-or-runtime-cap-failure"),
        ("cap", "circuit-breaker-or-runtime-cap-failure"),
        ("integrity", "calibration-integrity-failure"),
        ("attestation", "driver-cuda-runtime-attestation-mismatch"),
    )
    for fragment, classification in mapping:
        if fragment in text:
            return classification
    if not possible_pod:
        return "pod-create-rejected-before-resource-creation"
    return "calibration-contract-safety-failure"


def _redacted_outcome(
    lifecycle: Lifecycle,
    *,
    failure_class: str | None,
    finalization: Finalization,
    matrix: Mapping[str, object] | None,
    projections: Mapping[str, object] | None,
) -> dict[str, object]:
    decision = (
        "open-weight-self-operated-cloud-runtime-feasible-base-registration-next"
        if failure_class is None and finalization.exact
        else "calibration-integrity-failure-stop"
    )
    if failure_class in {
        "teardown-ambiguity",
        "secret-template-deletion-ambiguity",
        "billing-reconciliation-unavailable",
    }:
        decision = "self-operated-control-boundary-failed-managed-api-rejected"
    return {
        "schema_version": "treasurebench-open-weight-public-calibration-outcome-r2-v1",
        "task_id": TASK_ID,
        "scientific_run": False,
        "status": (
            "public-calibration-operational-closeout"
            if failure_class is None and finalization.exact
            else "hard-stop"
        ),
        "runtime_identity": RUNTIME_IDENTITY,
        "model_identity": MODEL_NAME,
        "failure_class": failure_class,
        "decision": decision,
        "resource_ids": {
            "pod": lifecycle.pod_id,
            "template": None if lifecycle.template is None else lifecycle.template.id,
            "secrets": [resource.id for resource in lifecycle.secrets],
        },
        "teardown": {
            "dispatch_stopped": lifecycle.dispatch_stopped,
            "pod_deleted": lifecycle.pod_deleted,
            "pod_unaddressable": lifecycle.pod_unaddressable,
            "disposable_volume_deleted": lifecycle.volume_deleted,
            "template_deleted": lifecycle.template_deleted,
            "secrets_deleted": lifecycle.secrets_deleted,
        },
        "billing": (
            None
            if lifecycle.billing is None
            else {
                "exact_amount_usd": str(lifecycle.billing.amount_usd),
                "billed_milliseconds": lifecycle.billing.billed_milliseconds,
                "disk_space_billed_gb": str(lifecycle.billing.disk_space_billed_gb),
                "record_count": lifecycle.billing.record_count,
            }
        ),
        "operational_counts": (
            None
            if matrix is None
            else {
                key: matrix[key]
                for key in (
                    "terminal_pairings",
                    "protocol_valid_count",
                    "protocol_invalid_count",
                    "provider_operational_missing_count",
                    "runtime_failure_count",
                    "calls",
                    "input_tokens",
                    "output_tokens",
                )
            }
        ),
        "projections": projections,
        "remediation": list(finalization.remediation),
        "raw_provider_bodies_published": False,
        "prompts_or_outputs_published": False,
        "performance_values_published": False,
        "merge_or_issue_close_allowed": failure_class is None and finalization.exact,
    }


def run_live_calibration(
    repo: Path,
    *,
    credential_loader: Callable[..., CredentialSet] = load_credentials,
    plane_factory: Callable[[str], ControlPlane] = RunPodControlPlane,
) -> dict[str, object]:
    """Execute R2 only after authorization; every possible Pod enters one finalizer."""

    auth_file = authorization_path()
    _require(auth_file.exists(), "R2 owner authorization required")
    metadata = auth_file.lstat()
    _require(stat.S_ISREG(metadata.st_mode), "authorization must be regular")
    _require(stat.S_IMODE(metadata.st_mode) == 0o600, "authorization mode must be 0600")
    authorization = load_yaml(auth_file)
    lifecycle = validate_pre_ingress(repo, authorization)
    credentials: CredentialSet | None = None
    runtime_client: RunPodRuntimeClient | None = None
    runpod_value = ""
    hf_value = ""
    secret_values: dict[str, str] = {}
    plane: ControlPlane | None = None
    endpoint = MutableSecret("")
    attestation = MutableSecret("")
    matrix: dict[str, object] | None = None
    projections: dict[str, object] | None = None
    failure: Exception | None = None
    finalization = Finalization(False, "calibration-integrity-failure", ())
    try:
        credentials = credential_loader(
            repo / CREDENTIAL_PATH,
            explicit_live_mode=True,
            requested_names=CREDENTIAL_NAMES,
        )
        runpod_value = credentials.get_secret("RUNPOD_API_KEY") or ""
        hf_value = credentials.get_secret("HF_TOKEN") or ""
        _require(bool(runpod_value) and bool(hf_value), "exact two credentials required")
        endpoint = MutableSecret(secrets.token_urlsafe(32))
        attestation = MutableSecret(secrets.token_urlsafe(32))
        plane = plane_factory(runpod_value)
        require_remote_conflict_free(plane, lifecycle.namespace)
        secret_values = {
            "hf": hf_value,
            "endpoint": endpoint.reveal(),
            "attestation": attestation.reveal(),
        }
        for kind, name in _secret_names(lifecycle.namespace).items():
            lifecycle.secrets.append(plane.create_secret(name, secret_values[kind]))
            _write_state(state_path(), lifecycle)
        lifecycle.template = plane.create_template(build_template_spec(repo, lifecycle.namespace))
        _write_state(state_path(), lifecycle)
        lifecycle.possible_pod = True
        try:
            pod = plane.create_pod(
                build_pod_spec(lifecycle.namespace, lifecycle.template.id, lifecycle.started_at)
            )
            lifecycle.pod_id = str(pod.get("id", "")) or None
            _require(lifecycle.pod_id is not None, "Pod create response missing identity")
        except Exception:
            reconciled = reconcile_ambiguous_create(plane, lifecycle)
            if reconciled is not None:
                raise RuntimeConformanceError("ambiguous create reconciled and deleted") from None
            lifecycle.possible_pod = False
            raise RuntimeConformanceError("Pod create rejected before resource creation") from None
        _write_state(state_path(), lifecycle)
        manifest = load_yaml(repo / MANIFEST_PATH)
        _require(pod.get("name") == lifecycle.namespace, "Pod namespace drift")
        _require(
            pod.get("imageName") == manifest["container"]["immutable_reference"],
            "Pod container image identity mismatch",
        )
        _require(pod.get("templateId") == lifecycle.template.id, "Pod template drift")
        _require(pod.get("gpuCount") == 1, "Pod GPU count drift")
        machine = pod.get("machine")
        if not isinstance(machine, Mapping):
            raise RuntimeConformanceError("Pod machine identity missing")
        _require(machine.get("secureCloud") is True, "Secure Cloud required")
        _require(
            machine.get("gpuDisplayName") == "NVIDIA A100 80GB PCIe",
            "Pod GPU type drift",
        )
        _require(pod.get("containerDiskInGb") == 50, "container disk drift")
        _require(pod.get("volumeInGb") == 120, "disposable volume size drift")
        _require(pod.get("podType") != "INTERRUPTABLE", "interruptible Pod rejected")
        _require(pod.get("volumeEncrypted") is True, "encrypted Pod volume required")
        _require(pod.get("networkVolumeId") in (None, ""), "network volume rejected")
        rate = Decimal(str(pod.get("costPerHr", 0)))
        _require(rate > 0 and rate * Decimal(6) < HARD_CAP, "hourly rate above cap")
        runtime_endpoint = f"https://{lifecycle.pod_id}-8000.proxy.runpod.net"
        ready: dict[str, Any] | None = None
        started_wait = time.monotonic()
        while time.monotonic() - started_wait < 3600:
            try:
                runtime_client = RunPodRuntimeClient(runtime_endpoint, endpoint.reveal())
                ready = runtime_client.get_attestation()
                break
            except Exception:
                time.sleep(10)
        if ready is None:
            raise RuntimeConformanceError("engine startup readiness failure")
        validate_measured_attestation(
            cast(Mapping[str, Any], ready),
            manifest=manifest,
            key=attestation.reveal(),
        )
        generation_started = time.monotonic()
        matrix = _run_public_matrix(
            runtime_endpoint,
            endpoint.reveal(),
            deadline=started_wait + MAX_GPU_SECONDS,
            started=started_wait,
            hourly_rate=rate,
        )
        generation_seconds = Decimal(str(time.monotonic() - generation_started))
        # Cost-dependent bounds are completed after exact billing in the finalizer.
        fixed_seconds = Decimal(str(ready["startup_seconds"])) + Decimal(
            str(ready["model_load_seconds"])
        )
        projections = {
            "_fixed_seconds": fixed_seconds,
            "_generation_seconds": generation_seconds,
            "_peak_gpu_memory_mib": int(ready["peak_gpu_memory_mib"]),
        }
    except Exception as error:
        failure = error
    finally:
        try:
            if plane is not None:
                finalization = finalize_lifecycle(plane, lifecycle)
        except Exception as finalizer_error:
            if failure is None:
                failure = finalizer_error
            finalization = Finalization(
                False,
                "teardown-ambiguity",
                ("query exact AO-0012 R2 namespace resources",),
            )
        finally:
            if credentials is not None:
                credentials.clear()
            secret_values.clear()
            runpod_value = ""
            hf_value = ""
            if runtime_client is not None:
                runtime_client.clear()
            endpoint.clear()
            attestation.clear()
            if hasattr(plane, "clear"):
                cast(Any, plane).clear()
    failure_class = (
        None if failure is None else _classify_failure(failure, possible_pod=lifecycle.possible_pod)
    )
    if finalization.hard_stop_class is not None:
        failure_class = finalization.hard_stop_class
    if (
        failure_class is None
        and matrix is not None
        and lifecycle.billing is not None
        and projections is not None
    ):
        classifications = cast(list[PairingClassificationV3], matrix.pop("_classifications"))
        pending = cast(list[tuple[Any, Any, int]], matrix.pop("_pending"))
        matrix["bound_count"] = _verify_public_bounds(
            classifications,
            pending,
            reconciled_cost_usd=lifecycle.billing.amount_usd,
        )
        matrix["primary_and_independent_bounds_agree"] = True
        fixed = cast(Decimal, projections.pop("_fixed_seconds"))
        generated = cast(Decimal, projections.pop("_generation_seconds"))
        peak = int(str(projections.pop("_peak_gpu_memory_mib")))
        projections = operational_projections(
            fixed_seconds=fixed,
            generation_seconds=generated,
            exact_cost=lifecycle.billing.amount_usd,
            tokens=int(str(matrix["input_tokens"])) + int(str(matrix["output_tokens"])),
            calls=int(str(matrix["calls"])),
            retries=len(
                [
                    record
                    for record in cast(list[dict[str, object]], matrix.get("call_records", []))
                    if int(str(record.get("transport_attempt", 1))) > 1
                ]
            ),
            peak_gpu_memory_mib=peak,
        )
    outcome = _redacted_outcome(
        lifecycle,
        failure_class=failure_class,
        finalization=finalization,
        matrix=matrix,
        projections=projections,
    )
    schema = json.loads((repo / OUTCOME_SCHEMA_PATH).read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(outcome)
    (repo / OUTCOME_PATH).write_text(yaml.safe_dump(outcome, sort_keys=False), encoding="utf-8")
    if finalization.exact and state_path().exists():
        state_path().unlink()
    return outcome


class RunPodRuntimeClient:
    def __init__(self, endpoint: str, bearer: str) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.bearer = MutableSecret(bearer)

    def clear(self) -> None:
        self.bearer.clear()

    def get_attestation(self) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.endpoint}/runtime-attestation",
            headers={"Authorization": f"Bearer {self.bearer.reveal()}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                raw = response.read(1_000_000)
        except Exception:
            raise RuntimeConformanceError("endpoint authentication/control failure") from None
        value = json.loads(raw)
        _require(isinstance(value, dict), "malformed runtime attestation")
        return cast(dict[str, Any], value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--rehearsal", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.live:
        result = run_live_calibration(args.repo)
    elif args.rehearsal:
        result = run_offline_rehearsal(args.repo)
    else:
        result = run_offline_rehearsal(args.repo)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
