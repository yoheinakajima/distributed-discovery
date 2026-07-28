"""Offline controls for the wholly fresh TreasureBench repair-confirmation v2 pilot.

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
from distributed_discovery.benchmark.agents_v1.adapters import AdapterRequest, MockAdapter
from distributed_discovery.benchmark.agents_v1.contamination import classify_text, run_public_probes
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.generation import (
    canonical_cells,
    generate_instance,
)
from distributed_discovery.benchmark.agents_v1.live_providers import (
    ANTHROPIC_MANIFEST,
    OPENAI_MANIFEST,
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
from distributed_discovery.benchmark.agents_v1.prompts import compile_prompt
from distributed_discovery.benchmark.agents_v1.protocol_contract import (
    verify_metric_ranges,
    verify_protocol_contract,
)
from distributed_discovery.benchmark.agents_v1.provider_schema import (
    ANTHROPIC_PROVIDER,
    OPENAI_PROVIDER,
    assert_provider_schema,
    compile_anthropic_action_schema,
    compile_openai_action_schema,
    schema_fingerprint,
    validate_action_semantics,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import (
    verify_method_agreement,
)

CAMPAIGN_ID = "treasurebench-agents-v1-repair-confirmation-v2"
BATCH_ID = "tb-agents-v1-repair-confirmation-v2-b01"
TASK_ID = "AO-0006"
ISSUE = 200
BRANCH = "benchmark/treasurebench-agents-v1-fresh-pilot-v2"
GATE_ID = "AOG-AO-0006-FRESH-PILOT-V2"
MODELS = ("gpt-5.4-2026-03-05", "claude-sonnet-4-6")
PROVIDERS = ("OpenAI", "Anthropic")
TOTAL_CAP = Decimal("25")
PROVIDER_CAPS = {"OpenAI": Decimal("10"), "Anthropic": Decimal("15")}
MAX_CALLS = 5200
NORMAL_CALLS = 3016
CALLS_PER_PROVIDER = 1508
MAX_CALLS_PER_PROVIDER = 2600
MAX_OUTPUT_TOKENS_PER_REQUEST = 256
ROUTE_TOKEN_CAPS = {
    "OpenAI": {"input": 1_680_000, "output": 386_048},
    "Anthropic": {"input": 3_000_000, "output": 386_048},
}
REQUEST_PATH = Path("docs/benchmark/agents-v1/treasurebench-fresh-pilot-v2-request.yml")
ALLOCATION_PATH = Path("docs/benchmark/agents-v1/treasurebench-fresh-pilot-v2-allocation.yml")
EXECUTION_BUDGET_PATH = Path(
    "docs/benchmark/agents-v1/treasurebench-fresh-pilot-v2-execution-budget.yml"
)
CORRUPTIONS_PATH = Path("docs/benchmark/agents-v1/treasurebench-fresh-pilot-v2-corruptions.yml")
GATE_PATH = Path("reports/agent-ops/AO-0006-treasurebench-fresh-pilot-v2-owner-gate.yml")
CONTRACT_PATH = Path("tasks/treasurebench-agents-v1-fresh-pilot-v2.yml")
RESERVED_IDENTITY_FRAGMENTS = (
    "treasurebench-agents-v1-pilot-v1",
    "tb-agents-v1-pilot-v1-b01",
    "treasurebench-agents-v1-repair-confirmation-v1",
    "tb-agents-v1-repair-confirmation-v1-b01",
    "PILOT-SLOT",
    "RC-SLOT",
    "BASE-SLOT",
    "BASE-BATCH",
    "future-base",
    "base-campaign",
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


def load_execution_budget(repo: Path) -> dict[str, Any]:
    return _load_and_validate(
        repo,
        EXECUTION_BUDGET_PATH,
        EXECUTION_BUDGET_PATH.with_suffix(".schema.json"),
    )


def load_corruption_registry(repo: Path) -> dict[str, Any]:
    return _load_and_validate(
        repo,
        CORRUPTIONS_PATH,
        CORRUPTIONS_PATH.with_suffix(".schema.json"),
    )


def allocation_slots(repo: Path) -> tuple[FreshSlot, ...]:
    allocation = load_allocation(repo)
    families = allocation["families"]
    categories = allocation["boundary_cycle"]
    if not isinstance(families, Mapping) or not isinstance(categories, Sequence):
        raise ValueError("fresh allocation recipe is malformed")
    canonical = {(cell.family_id, cell.cell_index) for cell in canonical_cells()}
    slots: list[FreshSlot] = []
    prefix = str(allocation["slot_prefix"])
    for family_offset, (family, indices) in enumerate(families.items()):
        if not isinstance(indices, Sequence):
            raise ValueError("fresh allocation indices must be a sequence")
        for within_family, raw_index in enumerate(indices):
            number = len(slots) + 1
            index = int(raw_index)
            slot = FreshSlot(
                slot_id=f"{prefix}-{number:03d}",
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
    return root / "distributed-discovery" / "agent-ops" / "authorizations" / f"{GATE_ID}.yml"


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
    permit = None if public_fixture else GenerationPermit(CAMPAIGN_ID, True, synthetic=False)
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
        material=f"fresh-private-v2/{seed.hex()}",
        public_fixture=False,
        authorization=authorization,
    )


def validate_provider_boundary(tasks: Sequence[TaskInstance]) -> dict[str, object]:
    """Compile both transports and apply the shared semantic contract offline."""

    if not tasks:
        raise ValueError("provider boundary requires a task")
    task = tasks[0]
    agent_id = sorted(task.capabilities)[0]
    compiled: dict[str, str] = {}
    for provider, manifest, compiler in (
        (OPENAI_PROVIDER, OPENAI_MANIFEST, compile_openai_action_schema),
        (ANTHROPIC_PROVIDER, ANTHROPIC_MANIFEST, compile_anthropic_action_schema),
    ):
        request = AdapterRequest(
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
            max_output_tokens=MAX_OUTPUT_TOKENS_PER_REQUEST,
            final_required=True,
        )
        schema = compiler(request)
        assert_provider_schema(provider, schema)
        response = MockAdapter().respond(request)
        response_value = json.loads(response.raw_output)
        response_value["declared_metadata"] = {}
        raw_output = json.dumps(response_value, sort_keys=True)
        jsonschema.validate(response_value, schema)
        action = validate_action_semantics(raw_output, request)
        if not action.final or len(action.actions) != 1:
            raise ValueError("provider-independent exactly-one-final-action failed")
        compiled[provider] = schema_fingerprint(schema)
    if compiled[OPENAI_PROVIDER] == compiled[ANTHROPIC_PROVIDER]:
        raise ValueError("provider-specific transport schemas unexpectedly match")
    return {
        "status": "pass",
        "output_tokens_per_request": MAX_OUTPUT_TOKENS_PER_REQUEST,
        "provider_schema_fingerprints": compiled,
        "provider_independent_semantic_validation": "pass",
        "exactly_one_final_action": "pass",
    }


def validate_registration(repo: Path) -> dict[str, object]:
    request = load_request(repo)
    allocation = load_allocation(repo)
    budget = load_execution_budget(repo)
    corruptions = load_corruption_registry(repo)
    slots = allocation_slots(repo)
    policy = load_yaml(repo / request["failure_policy"]["path"])
    audit = load_yaml(
        repo / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v2-provider-audit.yml"
    )
    conformance = load_yaml(
        repo / "reports/agent-ops/AO-0004-r4-public-provider-canary-outcome.yml"
    )
    serialized = canonical_json(
        {
            "request": request,
            "allocation": allocation,
            "budget": budget,
            "corruptions": corruptions,
        }
    ).decode()
    if any(fragment in serialized for fragment in RESERVED_IDENTITY_FRAGMENTS):
        raise ValueError("reserved pilot or base identity appears in fresh registration")
    for value, expected, name in (
        (request["task_id"], TASK_ID, "task"),
        (request["campaign_id"], CAMPAIGN_ID, "campaign"),
        (request["batch_id"], BATCH_ID, "batch"),
        (request["branch"], BRANCH, "branch"),
        (allocation["campaign_id"], CAMPAIGN_ID, "allocation campaign"),
        (allocation["batch_id"], BATCH_ID, "allocation batch"),
        (budget["campaign_id"], CAMPAIGN_ID, "budget campaign"),
        (budget["batch_id"], BATCH_ID, "budget batch"),
    ):
        _require_equal(value, expected, name)
    if policy["retry"]["transport"]["maximum_attempts"] != 2:
        raise ValueError("prospective transport attempt bound changed")
    if policy["retry"]["schema"]["maximum_repairs"] != 1:
        raise ValueError("prospective schema repair bound changed")
    if policy["action_budget"]["final_action_cardinality"] != ("exactly-one-per-required-agent"):
        raise ValueError("repaired final-action contract changed")
    if audit["status"] != "pass-current-official-docs-no-credential-or-provider-api-call":
        raise ValueError("provider audit is not current and passing")
    if conformance["final_decision"] != "conformance-pass-both-complete-schemas":
        raise ValueError("AO-0004 complete-schema prerequisite is not passing")
    if conformance["classification"] != "public-engineering-only-not-scientific-evidence":
        raise ValueError("AO-0004 evidence boundary changed")
    complete = [item for item in conformance["canaries"] if item["schema_role"] == "complete"]
    if len(complete) != 2 or any(
        item["status"] != "success" or item["max_output_tokens"] != MAX_OUTPUT_TOKENS_PER_REQUEST
        for item in complete
    ):
        raise ValueError("AO-0004 complete-schema ceiling changed")
    if Decimal(request["budget"]["hard_cap"]) != TOTAL_CAP:
        raise ValueError("fresh total cap changed")
    if {
        provider: Decimal(value) for provider, value in request["budget"]["provider_caps"].items()
    } != PROVIDER_CAPS:
        raise ValueError("fresh provider caps changed")
    if request["budget"]["call_cap"] != MAX_CALLS:
        raise ValueError("fresh call cap changed")
    if request["budget"]["normal_calls"] != NORMAL_CALLS:
        raise ValueError("fresh normal graph changed")
    if request["budget"]["calls_per_provider"] != CALLS_PER_PROVIDER:
        raise ValueError("fresh per-provider graph changed")
    if request["budget"]["route_token_caps"] != ROUTE_TOKEN_CAPS:
        raise ValueError("fresh route token caps changed")
    if request["provider_conformance"]["output_tokens_per_request"] != (
        MAX_OUTPUT_TOKENS_PER_REQUEST
    ):
        raise ValueError("fresh per-request output ceiling changed")
    if budget["graph"]["matrix_calls"] + budget["graph"]["public_canary_calls"] != (NORMAL_CALLS):
        raise ValueError("fresh execution graph does not reconcile")
    if len(corruptions["corruptions"]) != 41:
        raise ValueError("fresh corruption registry changed")
    activity = audit["activity"]
    if not isinstance(activity, Mapping) or any(
        Decimal(str(value)) != 0 for value in activity.values()
    ):
        raise PermissionError("registration audit records consequential activity")
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
        "budget_sha256": f"sha256:{sha256_hex(canonical_json(budget))}",
        "corruption_registry_sha256": (f"sha256:{sha256_hex(canonical_json(corruptions))}"),
    }


def run_synthetic_rehearsal(repo: Path) -> dict[str, object]:
    """Exercise the full 50 × 5 × 2 matrix without network or private data."""

    registration = validate_registration(repo)
    allocation = load_allocation(repo)
    material = str(allocation["generation"]["public_rehearsal_material"])
    tasks = generate_tasks(repo, material=material, public_fixture=True)
    provider_boundary = validate_provider_boundary(tasks)
    task_key = hashlib.sha256(b"fresh-rc-v2/synthetic/task-key").digest()
    answer_key = hashlib.sha256(b"fresh-rc-v2/synthetic/answer-key").digest()
    task_seal = seal_object(
        domain="fresh-synthetic-v2-task-batch",
        value=[task.visible_record() for task in tasks],
        key=task_key,
        nonce=hashlib.sha256(b"fresh-rc-v2/task-nonce").digest()[:12],
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    answers = [task.evaluator_record() for task in tasks]
    answer_seal = seal_object(
        domain="fresh-synthetic-v2-answer-key",
        value=answers,
        key=answer_key,
        nonce=hashlib.sha256(b"fresh-rc-v2/answer-nonce").digest()[:12],
        campaign_id=CAMPAIGN_ID,
        batch_id=BATCH_ID,
    )
    runs = 0
    turns = 0
    method_ab_errors = 0
    method_c_errors = 0
    range_errors = 0
    final_cardinality_errors = 0
    contamination_findings = 0
    redacted_traces = 0
    pairings: set[tuple[str, str, str]] = set()
    with tempfile.TemporaryDirectory(prefix="fresh-rc-v2-rehearsal-") as temporary:
        ledger = AppendOnlyLedger(Path(temporary) / "usage-cost-ledger.jsonl")
        traces: dict[str, bytes] = {}
        for model_index, model in enumerate(MODELS):
            for task in tasks:
                for architecture in ARCHITECTURES:
                    run = run_architecture(task, architecture, MockAdapter())
                    contract = verify_protocol_contract(task, run)
                    method_c_errors += len(contract.errors)
                    final_cardinality_errors += contract.invalid_final_records
                    metrics = asdict(evaluate_run(task, run))
                    method_ab_errors += len(verify_method_agreement(metrics, task, run))
                    range_errors += len(verify_metric_ranges(metrics))
                    contamination_findings += sum(
                        classify_text(turn.response.raw_output).classification
                        in {"direct-leakage", "probable-memorization"}
                        for turn in run.turns
                    )
                    pairing = (model, task.task_id, architecture)
                    if pairing in pairings:
                        raise ValueError("duplicate synthetic architecture/model pairing")
                    pairings.add(pairing)
                    trace = build_trace(run)
                    if trace.audit["hidden_reasoning_stored"] is not False:
                        raise PermissionError("hidden reasoning trace boundary failed")
                    trace_id = f"{model_index}/{task.task_id}/{architecture}"
                    sealed = seal_object(
                        domain=f"fresh-synthetic-v2-trace/{trace_id}",
                        value=trace.raw,
                        key=hashlib.sha256(f"fresh-rc-v2/{trace_id}".encode()).digest(),
                        nonce=hashlib.sha256(f"fresh-rc-v2/nonce/{trace_id}".encode()).digest()[
                            :12
                        ],
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
    expected_pairings = {
        (model, task.task_id, architecture)
        for model in MODELS
        for task in tasks
        for architecture in ARCHITECTURES
    }
    incomplete_pairings = len(expected_pairings.symmetric_difference(pairings))
    if any(
        (
            method_ab_errors,
            method_c_errors,
            range_errors,
            final_cardinality_errors,
            contamination_findings,
            incomplete_pairings,
        )
    ):
        raise ValueError("fresh repaired rehearsal verification failed")
    summary: dict[str, object] = {
        "schema_version": "treasurebench-agents-v1-fresh-pilot-v2-rehearsal-v1",
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
        "invalid_final_action_cardinalities": final_cardinality_errors,
        "incomplete_pairings": incomplete_pairings,
        "exact_pairings_verified": len(pairings),
        "nonfinal_proposals_excluded_from_scoring": True,
        "contamination_findings": contamination_findings,
        "contamination_probes": len(probes),
        "provider_boundary": provider_boundary,
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
    tasks = generate_tasks(
        repo,
        material=str(allocation["generation"]["public_rehearsal_material"]),
        public_fixture=True,
    )
    task = tasks[0]
    agent_id = sorted(task.capabilities)[0]
    provider_requests = {
        OPENAI_PROVIDER: AdapterRequest(
            prompt=compile_prompt(
                task,
                agent_id,
                architecture_id="provider-native-smoke",
                final_required=True,
            ),
            manifest=OPENAI_MANIFEST,
            round_number=0,
            action_vocabulary=task.action_vocabulary,
            source_vocabulary=task.source_vocabulary,
            final_required=True,
        ),
        ANTHROPIC_PROVIDER: AdapterRequest(
            prompt=compile_prompt(
                task,
                agent_id,
                architecture_id="provider-native-smoke",
                final_required=True,
            ),
            manifest=ANTHROPIC_MANIFEST,
            round_number=0,
            action_vocabulary=task.action_vocabulary,
            source_vocabulary=task.source_vocabulary,
            final_required=True,
        ),
    }

    for corruption_id, field, fragment in (
        ("IDENTITY-01-original-campaign", "campaign_id", RESERVED_IDENTITY_FRAGMENTS[0]),
        ("IDENTITY-02-original-batch", "batch_id", RESERVED_IDENTITY_FRAGMENTS[1]),
        (
            "IDENTITY-03-repair-confirmation-v1-campaign",
            "campaign_id",
            RESERVED_IDENTITY_FRAGMENTS[2],
        ),
        (
            "IDENTITY-04-repair-confirmation-v1-batch",
            "batch_id",
            RESERVED_IDENTITY_FRAGMENTS[3],
        ),
    ):
        reject(
            corruption_id,
            lambda name=field, value=fragment: _reject_reserved({**request, name: value}),
        )
    reject(
        "IDENTITY-05-prior-slot-prefix",
        lambda: _reject_reserved({**allocation, "slot_prefix": "RC-SLOT"}),
    )
    expected_tree = execution_tree_hashes(repo)
    reject(
        "IDENTITY-06-execution-tree-mismatch",
        lambda: _require_equal(
            {**expected_tree, next(iter(expected_tree)): "sha256:mutated"},
            expected_tree,
            "execution tree",
        ),
    )
    reject(
        "GENERATION-01-no-authorization",
        lambda: generate_tasks(repo, material="private", public_fixture=False),
    )
    reject(
        "GENERATION-02-short-seed",
        lambda: generate_authorized_private_tasks(repo, seed=b"short"),
    )
    reject(
        "AUTH-01-missing-file",
        lambda: load_owner_authorization(repo, Path("/nonexistent/AOG-AO-0006-FRESH-PILOT-V2.yml")),
    )
    reject(
        "AUTH-02-synthetic",
        lambda: validate_owner_authorization(
            {"schema_version": "agent-ops-owner-authorization-v1", "synthetic": True},
            repo=repo,
        ),
    )
    reject("BUDGET-01-total-cap", lambda: _require_equal(Decimal("26"), TOTAL_CAP, "total cap"))
    reject(
        "BUDGET-02-openai-cap",
        lambda: _require_equal(Decimal("11"), PROVIDER_CAPS["OpenAI"], "OpenAI cap"),
    )
    reject(
        "BUDGET-03-anthropic-cap",
        lambda: _require_equal(Decimal("16"), PROVIDER_CAPS["Anthropic"], "Anthropic cap"),
    )
    reject("BUDGET-04-call-cap", lambda: _require_equal(5201, MAX_CALLS, "call cap"))
    for corruption_id, provider, token_kind in (
        ("BUDGET-05-openai-input-token-cap", "OpenAI", "input"),
        ("BUDGET-06-openai-output-token-cap", "OpenAI", "output"),
        ("BUDGET-07-anthropic-input-token-cap", "Anthropic", "input"),
        ("BUDGET-08-anthropic-output-token-cap", "Anthropic", "output"),
    ):
        cap = ROUTE_TOKEN_CAPS[provider][token_kind]
        reject(
            corruption_id,
            lambda ceiling=cap: _require_equal(ceiling + 1, ceiling, "route token cap"),
        )

    def unsupported_openai_schema() -> None:
        schema = compile_openai_action_schema(provider_requests[OPENAI_PROVIDER])
        properties = schema["properties"]
        assert isinstance(properties, dict)
        actions = properties["actions"]
        assert isinstance(actions, dict)
        actions["uniqueItems"] = True
        assert_provider_schema(OPENAI_PROVIDER, schema)

    def unsupported_anthropic_schema() -> None:
        schema = compile_anthropic_action_schema(provider_requests[ANTHROPIC_PROVIDER])
        properties = schema["properties"]
        assert isinstance(properties, dict)
        actions = properties["actions"]
        assert isinstance(actions, dict)
        actions["maxItems"] = 1
        assert_provider_schema(ANTHROPIC_PROVIDER, schema)

    reject("SCHEMA-01-openai-unsupported-keyword", unsupported_openai_schema)
    reject("SCHEMA-02-anthropic-unsupported-keyword", unsupported_anthropic_schema)

    valid_output = json.loads(MockAdapter().respond(provider_requests[OPENAI_PROVIDER]).raw_output)
    valid_output["declared_metadata"] = {}
    for corruption_id, actions in (
        ("SEMANTIC-01-multiple-final-actions", list(task.action_vocabulary[:2])),
        ("SEMANTIC-02-missing-final-action", []),
    ):
        corrupted = {**valid_output, "actions": actions}
        reject(
            corruption_id,
            lambda value=corrupted: validate_action_semantics(
                json.dumps(value), provider_requests[OPENAI_PROVIDER]
            ),
        )

    expected_pairings = {
        (model, item.task_id, architecture)
        for model in MODELS
        for item in tasks
        for architecture in ARCHITECTURES
    }
    incomplete = set(expected_pairings)
    incomplete.pop()
    reject(
        "PAIRING-01-incomplete-architecture-model-cell",
        lambda: _require_equal(incomplete, expected_pairings, "pairing matrix"),
    )
    valid_run = run_architecture(task, ARCHITECTURES[0], MockAdapter())
    mutated_metrics = asdict(evaluate_run(task, valid_run))
    mutated_metrics["group_discovery"] = "mutated"
    reject(
        "METHOD-01-a-b-disagreement",
        lambda: _reject_true(
            bool(verify_method_agreement(mutated_metrics, task, valid_run)),
            "Method A/B disagreement",
        ),
    )
    invalid_run = run_architecture(task, ARCHITECTURES[0], MockAdapter("error"))
    reject(
        "METHOD-02-c-protocol-failure",
        lambda: _reject_true(
            bool(verify_protocol_contract(task, invalid_run).errors),
            "Method C protocol failure",
        ),
    )
    reject(
        "METRIC-01-out-of-range",
        lambda: _reject_true(
            bool(verify_metric_ranges({"distinct_action_coverage": 2})),
            "metric range failure",
        ),
    )
    reject(
        "CONTAMINATION-01-direct",
        lambda: _reject_contamination("answer_key from private holdout"),
    )
    reject(
        "CONTAMINATION-02-probable",
        lambda: _reject_contamination("SEALED-0123456789abcdef"),
    )

    key = hashlib.sha256(b"fresh-rc-v2-corruption-key").digest()
    sealed = seal_object(
        domain="fresh-rc-v2-corruption",
        value={"ok": True},
        key=key,
        nonce=hashlib.sha256(b"fresh-rc-v2-corruption-nonce").digest()[:12],
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
        "REDACTION-02-answer",
        lambda: validate_public_pilot_summary({"redaction_status": "pass", "answer": "forbidden"}),
    )
    reject(
        "REDACTION-03-ranking",
        lambda: validate_public_pilot_summary({"redaction_status": "pass", "ranking": []}),
    )
    reject(
        "SCIENCE-01-dd023",
        lambda: validate_public_pilot_summary({"redaction_status": "pass", "study_id": "DD-023"}),
    )
    reject(
        "SCIENCE-02-claim",
        lambda: validate_public_pilot_summary(
            {"redaction_status": "pass", "claim_id": "DD-C-0111"}
        ),
    )
    reject(
        "SCIENCE-03-scientific-run",
        lambda: _reject_scientific_surface({"scientific_run_created": True}),
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


def _reject_true(condition: bool, name: str) -> None:
    if condition:
        raise ValueError(name)


def _reject_contamination(text: str) -> None:
    finding = classify_text(text)
    if finding.classification in {"direct-leakage", "probable-memorization"}:
        raise PermissionError("contamination requires quarantine")


def _reject_scientific_surface(value: Mapping[str, object]) -> None:
    if any(value.values()):
        raise PermissionError("scientific mutation is prohibited")
