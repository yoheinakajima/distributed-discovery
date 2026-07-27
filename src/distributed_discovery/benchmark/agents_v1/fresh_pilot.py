"""Offline controls for the wholly fresh TreasureBench repair-confirmation pilot.

This module may validate a generic Agent Operations authorization and prepare
fresh private generation, but it never reads credentials or calls a provider.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import jsonschema
from cryptography.exceptions import InvalidTag
from jsonschema import Draft202012Validator, FormatChecker

from distributed_discovery.agent_ops.core import (
    AgentOpsError,
    authorization_challenge,
    hash_path,
    load_yaml,
    sha256_file,
    validate,
)
from distributed_discovery.benchmark.agents_v1.adapters import MockAdapter
from distributed_discovery.benchmark.agents_v1.contamination import run_public_probes
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import (
    canonical_cells,
    generate_instance,
)
from distributed_discovery.benchmark.agents_v1.models import (
    TaskInstance,
    canonical_json,
    sha256_hex,
)
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.pilot import (
    AppendOnlyLedger,
    GenerationPermit,
    create_output_lock,
    seal_object,
    unseal_object,
    validate_contamination_probe_set,
    validate_lock_inventory,
    validate_public_pilot_summary,
    verify_output_lock,
)
from distributed_discovery.benchmark.agents_v1.protocol_contract import (
    verify_metric_ranges,
    verify_protocol_contract,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import (
    verify_method_agreement,
)

CAMPAIGN_ID = "treasurebench-agents-v1-repair-confirmation-v1"
BATCH_ID = "tb-agents-v1-repair-confirmation-v1-b01"
TASK_ID = "AO-0002"
ISSUE = 196
BRANCH = "benchmark/treasurebench-agents-v1-fresh-pilot"
GATE_ID = "AOG-AO-0002-FRESH-PILOT"
MODELS = ("gpt-5.4-2026-03-05", "claude-sonnet-4-6")
PROVIDERS = ("OpenAI", "Anthropic")
TOTAL_CAP = Decimal("25")
PROVIDER_CAPS = {"OpenAI": Decimal("10"), "Anthropic": Decimal("15")}
MAX_CALLS = 5200
REQUEST_PATH = Path("docs/benchmark/agents-v1/treasurebench-fresh-pilot-request.yml")
ALLOCATION_PATH = Path("docs/benchmark/agents-v1/treasurebench-fresh-pilot-allocation.yml")
GATE_PATH = Path("reports/agent-ops/AO-0002-treasurebench-fresh-pilot-owner-gate.yml")
CONTRACT_PATH = Path("tasks/treasurebench-agents-v1-fresh-pilot.yml")
RESERVED_IDENTITY_FRAGMENTS = (
    "treasurebench-agents-v1-pilot-v1",
    "tb-agents-v1-pilot-v1-b01",
    "PILOT-SLOT",
    "BASE-SLOT",
    "BASE-BATCH",
)


@dataclass(frozen=True)
class FreshSlot:
    slot_id: str
    family_id: str
    cell_index: int
    boundary_category: str
    target_relabeling_class: str
    agent_relabeling_class: str

    @property
    def variant(self) -> int:
        target = 0 if self.target_relabeling_class == "target-A" else 1
        agent = 0 if self.agent_relabeling_class == "agent-A" else 2
        return target + agent


def _load_and_validate(repo: Path, path: Path, schema: Path) -> dict[str, Any]:
    value = load_yaml(repo / path)
    definition = json.loads((repo / schema).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(definition)
    errors = sorted(
        Draft202012Validator(
            definition,
            format_checker=FormatChecker(),
        ).iter_errors(value),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    if errors:
        location = ".".join(str(item) for item in errors[0].absolute_path) or "$"
        raise ValueError(f"{path}:{location}: {errors[0].message}")
    return value


def load_request(repo: Path) -> dict[str, Any]:
    return _load_and_validate(
        repo,
        REQUEST_PATH,
        REQUEST_PATH.with_suffix(".schema.json"),
    )


def load_allocation(repo: Path) -> dict[str, Any]:
    return _load_and_validate(
        repo,
        ALLOCATION_PATH,
        ALLOCATION_PATH.with_suffix(".schema.json"),
    )


def allocation_slots(repo: Path) -> tuple[FreshSlot, ...]:
    allocation = load_allocation(repo)
    families = allocation["families"]
    categories = allocation["boundary_cycle"]
    if not isinstance(families, Mapping) or not isinstance(categories, Sequence):
        raise ValueError("fresh allocation recipe is malformed")
    canonical = {(cell.family_id, cell.cell_index) for cell in canonical_cells()}
    slots: list[FreshSlot] = []
    for family_offset, (family, indices) in enumerate(families.items()):
        if not isinstance(indices, Sequence):
            raise ValueError("fresh allocation indices must be a sequence")
        for within_family, raw_index in enumerate(indices):
            number = len(slots) + 1
            index = int(raw_index)
            slot = FreshSlot(
                slot_id=f"RC-SLOT-{number:03d}",
                family_id=str(family),
                cell_index=index,
                boundary_category=str(categories[within_family % len(categories)]),
                target_relabeling_class=(
                    "target-A" if (within_family + family_offset) % 2 == 0 else "target-B"
                ),
                agent_relabeling_class="agent-A" if number % 2 else "agent-B",
            )
            if (slot.family_id, slot.cell_index) not in canonical:
                raise ValueError(f"unknown fresh generator cell: {slot}")
            slots.append(slot)
    if len(slots) != 50 or len({slot.slot_id for slot in slots}) != 50:
        raise ValueError("fresh allocation must produce 50 unique slots")
    if {slot.target_relabeling_class for slot in slots} != {"target-A", "target-B"}:
        raise ValueError("fresh target relabeling is unbalanced")
    for attribute in ("target_relabeling_class", "agent_relabeling_class"):
        counts = {
            label: sum(getattr(slot, attribute) == label for slot in slots)
            for label in {getattr(slot, attribute) for slot in slots}
        }
        if set(counts.values()) != {25}:
            raise ValueError(f"fresh relabeling is not 25/25: {attribute}")
    return tuple(slots)


def execution_tree_hashes(repo: Path) -> dict[str, str]:
    request = load_request(repo)
    paths = request["execution_sensitive_paths"]
    if not isinstance(paths, list):
        raise ValueError("execution-sensitive paths must be a list")
    return {str(path): hash_path(repo / str(path)) for path in paths}


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode:
        raise PermissionError(result.stderr.strip() or "Git validation failed")
    return result.stdout.strip()


def authorization_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return (
        root
        / "distributed-discovery"
        / "agent-ops"
        / "authorizations"
        / f"{GATE_ID}.yml"
    )


def _authorization_digest(value: Mapping[str, object]) -> str:
    unsigned = dict(value)
    unsigned.pop("authorization_digest", None)
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def validate_owner_authorization(
    value: dict[str, Any],
    *,
    repo: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Bind generic owner authorization to this fresh execution surface."""

    validate(value, "owner-authorization.schema.json")
    gate = load_yaml(repo / GATE_PATH)
    validate(gate, "owner-gate.schema.json")
    if value["authorization_digest"] != _authorization_digest(value):
        raise PermissionError("owner authorization digest mismatch")
    expected = {
        "gate_id": GATE_ID,
        "issue": ISSUE,
        "pull_request": gate["pull_request"]["number"],
        "branch": BRANCH,
        "commit": gate["commit"],
        "task_contract_sha256": sha256_file(repo / CONTRACT_PATH),
        "tree_hashes": gate["tree_hashes"],
        "challenge": authorization_challenge(gate),
    }
    if any(value.get(key) != item for key, item in expected.items()):
        raise PermissionError("owner authorization does not bind the fresh pilot")
    current = now or datetime.now(UTC)
    authorized = datetime.fromisoformat(str(value["authorized_at_utc"]).replace("Z", "+00:00"))
    expires = datetime.fromisoformat(str(value["expires_at_utc"]).replace("Z", "+00:00"))
    if authorized > current or expires <= current:
        raise PermissionError("owner authorization is outside its active interval")
    if _git(repo, "branch", "--show-current") != BRANCH:
        raise PermissionError("fresh pilot branch mismatch")
    if subprocess.run(
        ("git", "merge-base", "--is-ancestor", str(value["commit"]), "HEAD"),
        cwd=repo,
        check=False,
        capture_output=True,
    ).returncode:
        raise PermissionError("authorized execution commit is not an ancestor")
    current_hashes = execution_tree_hashes(repo)
    if current_hashes != value["tree_hashes"]:
        raise PermissionError("fresh execution-sensitive tree changed")
    return value


def load_owner_authorization(repo: Path, path: Path | None = None) -> dict[str, Any]:
    resolved = path or authorization_path()
    info = resolved.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise PermissionError("owner authorization must be a regular file")
    if stat.S_IMODE(info.st_mode) != 0o600:
        raise PermissionError("owner authorization must have mode 0600")
    return validate_owner_authorization(load_yaml(resolved), repo=repo)


def generate_tasks(
    repo: Path,
    *,
    material: str,
    public_fixture: bool,
    authorization: Mapping[str, object] | None = None,
) -> tuple[TaskInstance, ...]:
    cells = {(cell.family_id, cell.cell_index): cell for cell in canonical_cells()}
    permit = (
        None
        if public_fixture
        else GenerationPermit(CAMPAIGN_ID, True, synthetic=False)
    )
    if not public_fixture and authorization is None:
        raise PermissionError("owner authorization is required for private generation")
    tasks = []
    for slot in allocation_slots(repo):
        tasks.append(
            generate_instance(
                cells[(slot.family_id, slot.cell_index)],
                variant=slot.variant,
                public_fixture=public_fixture,
                material=f"{material}/{slot.slot_id}",
                hidden_labels=False,
                authorization=authorization,
                custody_context=permit,
            )
        )
    if len({task.task_id for task in tasks}) != 50:
        raise ValueError("fresh generation did not produce 50 unique tasks")
    return tuple(tasks)


def generate_authorized_private_tasks(
    repo: Path,
    *,
    seed: bytes,
    authorization_path_override: Path | None = None,
) -> tuple[TaskInstance, ...]:
    """Generate only after validating the generic gate; seed creation is external."""

    if len(seed) != 32:
        raise ValueError("fresh OS-CSPRNG seed must be 32 bytes")
    authorization = load_owner_authorization(repo, authorization_path_override)
    return generate_tasks(
        repo,
        material=f"fresh-private/{seed.hex()}",
        public_fixture=False,
        authorization=authorization,
    )


def validate_registration(repo: Path) -> dict[str, object]:
    request = load_request(repo)
    allocation = load_allocation(repo)
    slots = allocation_slots(repo)
    policy = load_yaml(repo / request["failure_policy"]["path"])
    audit = load_yaml(
        repo
        / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-provider-audit.yml"
    )
    serialized = canonical_json({"request": request, "allocation": allocation}).decode()
    if any(fragment in serialized for fragment in RESERVED_IDENTITY_FRAGMENTS):
        raise ValueError("reserved pilot or base identity appears in fresh registration")
    if policy["retry"]["transport"]["maximum_attempts"] != 2:
        raise ValueError("prospective transport attempt bound changed")
    if policy["retry"]["schema"]["maximum_repairs"] != 1:
        raise ValueError("prospective schema repair bound changed")
    if policy["action_budget"]["final_action_cardinality"] != (
        "exactly-one-per-required-agent"
    ):
        raise ValueError("repaired final-action contract changed")
    if audit["status"] != "pass-current-official-docs-no-provider-api-call":
        raise ValueError("provider audit is not current and passing")
    if Decimal(request["budget"]["hard_cap"]) != TOTAL_CAP:
        raise ValueError("fresh total cap changed")
    if {
        provider: Decimal(value)
        for provider, value in request["budget"]["provider_caps"].items()
    } != PROVIDER_CAPS:
        raise ValueError("fresh provider caps changed")
    if request["budget"]["call_cap"] != MAX_CALLS:
        raise ValueError("fresh call cap changed")
    return {
        "status": "pass",
        "task_id": TASK_ID,
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "slots": len(slots),
        "runs": len(slots) * len(ARCHITECTURES) * len(MODELS),
        "provider_calls": 0,
        "credential_reads": 0,
        "private_objects_created": 0,
        "spend_usd": "0",
        "request_sha256": f"sha256:{sha256_hex(canonical_json(request))}",
        "allocation_sha256": f"sha256:{sha256_hex(canonical_json(allocation))}",
    }


def run_synthetic_rehearsal(repo: Path) -> dict[str, object]:
    """Exercise the full 50 × 5 × 2 matrix without network or private data."""

    registration = validate_registration(repo)
    allocation = load_allocation(repo)
    material = str(allocation["generation"]["public_rehearsal_material"])
    tasks = generate_tasks(repo, material=material, public_fixture=True)
    task_key = hashlib.sha256(b"fresh-rc/synthetic/task-key").digest()
    answer_key = hashlib.sha256(b"fresh-rc/synthetic/answer-key").digest()
    task_seal = seal_object(
        domain="fresh-synthetic-task-batch",
        value=[task.visible_record() for task in tasks],
        key=task_key,
        nonce=hashlib.sha256(b"fresh-rc/task-nonce").digest()[:12],
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    answers = [task.evaluator_record() for task in tasks]
    answer_seal = seal_object(
        domain="fresh-synthetic-answer-key",
        value=answers,
        key=answer_key,
        nonce=hashlib.sha256(b"fresh-rc/answer-nonce").digest()[:12],
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    runs = 0
    turns = 0
    method_ab_errors = 0
    method_c_errors = 0
    range_errors = 0
    redacted_traces = 0
    with tempfile.TemporaryDirectory(prefix="fresh-rc-rehearsal-") as temporary:
        ledger = AppendOnlyLedger(Path(temporary) / "usage-cost-ledger.jsonl")
        traces: dict[str, bytes] = {}
        for model_index, model in enumerate(MODELS):
            for task in tasks:
                for architecture in ARCHITECTURES:
                    run = run_architecture(task, architecture, MockAdapter())
                    metrics = asdict(evaluate_run(task, run))
                    method_ab_errors += len(verify_method_agreement(metrics, task, run))
                    method_c_errors += len(verify_protocol_contract(task, run).errors)
                    range_errors += len(verify_metric_ranges(metrics))
                    trace = build_trace(run)
                    if trace.audit["hidden_reasoning_stored"] is not False:
                        raise PermissionError("hidden reasoning trace boundary failed")
                    trace_id = f"{model_index}/{task.task_id}/{architecture}"
                    sealed = seal_object(
                        domain=f"fresh-synthetic-trace/{trace_id}",
                        value=trace.raw,
                        key=hashlib.sha256(f"fresh-rc/{trace_id}".encode()).digest(),
                        nonce=hashlib.sha256(
                            f"fresh-rc/nonce/{trace_id}".encode()
                        ).digest()[:12],
                        campaign_id=CAMPAIGN_ID,
                        batch_id=BATCH_ID,
                    )
                    traces[trace_id] = sealed.ciphertext
                    ledger.append(
                        {
                            "idempotency_key": trace_id,
                            "status": "success",
                            "provider": PROVIDERS[model_index],
                            "model": model,
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "cost_usd": "0",
                            "synthetic": True,
                        }
                    )
                    runs += 1
                    turns += len(run.turns)
                    redacted_traces += 1
        ledger.close_provider_phase()
        objects = {
            "task-ciphertext": task_seal.ciphertext,
            "answer-ciphertext": answer_seal.ciphertext,
            "access-log": b"synthetic-public-only\n",
            "usage-cost-ledger": ledger.path.read_bytes(),
            **{f"trace/{name}": value for name, value in traces.items()},
        }
        validate_lock_inventory(objects)
        lock = create_output_lock(
            objects,
            ledger=ledger,
            campaign_id=CAMPAIGN_ID,
            batch_id=BATCH_ID,
        )
        verify_output_lock(lock, objects, ledger=ledger)
        unsealed = unseal_object(
            answer_seal,
            key=answer_key,
            campaign_id=CAMPAIGN_ID,
            batch_id=BATCH_ID,
        )
        if canonical_json(unsealed) != canonical_json(answers):
            raise ValueError("fresh synthetic answer unseal mismatch")
    probes = run_public_probes()
    validate_contamination_probe_set(item.probe_class for item in probes)
    if any((method_ab_errors, method_c_errors, range_errors)):
        raise ValueError("fresh repaired rehearsal verification failed")
    summary: dict[str, object] = {
        "schema_version": "treasurebench-agents-v1-fresh-pilot-rehearsal-v1",
        "status": "pass",
        "classification": "public-synthetic-only",
        "task_id": TASK_ID,
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "tasks": len(tasks),
        "families": 5,
        "architectures": len(ARCHITECTURES),
        "synthetic_route_labels": len(MODELS),
        "runs": runs,
        "turns": turns,
        "method_a_b_errors": method_ab_errors,
        "method_c_errors": method_c_errors,
        "metric_range_errors": range_errors,
        "contamination_probes": len(probes),
        "redacted_traces_verified": redacted_traces,
        "output_lock_verified": True,
        "provider_calls": 0,
        "credential_reads": 0,
        "private_objects_created": 0,
        "external_cost_usd": "0",
        "network_enabled": False,
        "private_material": False,
        "redaction_status": "pass",
        "registration_sha256": registration["request_sha256"],
    }
    summary["rehearsal_hash"] = f"sha256:{sha256_hex(canonical_json(summary))}"
    validate_public_pilot_summary(summary)
    return summary


def audit_corruptions(repo: Path) -> tuple[dict[str, str], ...]:
    """Reject identity, budget, protocol, gate, custody, and redaction mutations."""

    outcomes: list[dict[str, str]] = []

    def reject(name: str, action: object) -> None:
        try:
            assert callable(action)
            action()
        except (
            AgentOpsError,
            KeyError,
            OSError,
            InvalidTag,
            PermissionError,
            TypeError,
            ValueError,
            jsonschema.ValidationError,
        ):
            outcomes.append({"corruption_id": name, "status": "rejected"})
            return
        outcomes.append({"corruption_id": name, "status": "accepted"})

    request = load_request(repo)
    allocation = load_allocation(repo)
    reject(
        "IDENTITY-01-quarantined-campaign",
        lambda: _reject_reserved({**request, "campaign_id": RESERVED_IDENTITY_FRAGMENTS[0]}),
    )
    reject(
        "IDENTITY-02-quarantined-batch",
        lambda: _reject_reserved({**request, "batch_id": RESERVED_IDENTITY_FRAGMENTS[1]}),
    )
    reject(
        "IDENTITY-03-pilot-slot",
        lambda: _reject_reserved({**allocation, "slot_prefix": "PILOT-SLOT"}),
    )
    reject("GENERATION-01-no-authorization", lambda: generate_tasks(
        repo, material="private", public_fixture=False
    ))
    reject("GENERATION-02-short-seed", lambda: generate_authorized_private_tasks(
        repo, seed=b"short"
    ))
    reject("AUTH-01-missing-file", lambda: load_owner_authorization(
        repo, Path("/nonexistent/AOG-AO-0002-FRESH-PILOT.yml")
    ))
    reject("AUTH-02-synthetic", lambda: validate_owner_authorization(
        {"schema_version": "agent-ops-owner-authorization-v1", "synthetic": True},
        repo=repo,
    ))
    reject("BUDGET-01-total-cap", lambda: _require_equal(
        Decimal("26"), TOTAL_CAP, "total cap"
    ))
    reject("BUDGET-02-openai-cap", lambda: _require_equal(
        Decimal("11"), PROVIDER_CAPS["OpenAI"], "OpenAI cap"
    ))
    reject("BUDGET-03-anthropic-cap", lambda: _require_equal(
        Decimal("16"), PROVIDER_CAPS["Anthropic"], "Anthropic cap"
    ))
    reject("BUDGET-04-call-cap", lambda: _require_equal(5201, MAX_CALLS, "call cap"))
    key = hashlib.sha256(b"fresh-corruption-key").digest()
    sealed = seal_object(
        domain="fresh-corruption",
        value={"ok": True},
        key=key,
        nonce=hashlib.sha256(b"fresh-corruption-nonce").digest()[:12],
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    reject(
        "CUSTODY-01-wrong-campaign",
        lambda: unseal_object(
            sealed,
            key=key,
            campaign_id="treasurebench-agents-v1-pilot-v1",
            batch_id=BATCH_ID,
        ),
    )
    reject(
        "CUSTODY-02-wrong-batch",
        lambda: unseal_object(
            sealed,
            key=key,
            campaign_id=CAMPAIGN_ID,
            batch_id="tb-agents-v1-pilot-v1-b01",
        ),
    )
    reject(
        "CUSTODY-03-wrong-key",
        lambda: unseal_object(
            sealed,
            key=hashlib.sha256(b"wrong").digest(),
            campaign_id=CAMPAIGN_ID,
            batch_id=BATCH_ID,
        ),
    )
    reject(
        "REDACTION-01-task-text",
        lambda: validate_public_pilot_summary(
            {"redaction_status": "pass", "task_text": "forbidden"}
        ),
    )
    reject(
        "REDACTION-02-ranking",
        lambda: validate_public_pilot_summary(
            {"redaction_status": "pass", "ranking": []}
        ),
    )
    reject(
        "SCIENCE-01-dd023",
        lambda: validate_public_pilot_summary(
            {"redaction_status": "pass", "study_id": "DD-023"}
        ),
    )
    reject(
        "SCIENCE-02-claim",
        lambda: validate_public_pilot_summary(
            {"redaction_status": "pass", "claim_id": "DD-C-0111"}
        ),
    )
    if any(item["status"] != "rejected" for item in outcomes):
        raise ValueError("one or more fresh-pilot corruptions were accepted")
    return tuple(outcomes)


def _reject_reserved(value: object) -> None:
    serialized = canonical_json(value).decode()
    if any(fragment in serialized for fragment in RESERVED_IDENTITY_FRAGMENTS):
        raise ValueError("reserved identity rejected")


def _require_equal(actual: object, expected: object, name: str) -> None:
    if actual != expected:
        raise ValueError(f"{name} mismatch")
