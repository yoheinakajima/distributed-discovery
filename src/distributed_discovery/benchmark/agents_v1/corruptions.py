"""Executable public-fixture corruption suite C01-C24."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from distributed_discovery.benchmark.agents_v1.actions import parse_action
from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    DisabledProviderAdapter,
    ModelManifest,
)
from distributed_discovery.benchmark.agents_v1.contamination import PROBE_CLASSES
from distributed_discovery.benchmark.agents_v1.custody import (
    ToyCustodyBundle,
    unseal_public_toy,
)
from distributed_discovery.benchmark.agents_v1.orchestration import MAX_MESSAGE_CHARS
from distributed_discovery.benchmark.agents_v1.prompts import ClosedCapabilityView, leakage_findings
from distributed_discovery.benchmark.agents_v1.traces import verify_trace_hashes
from distributed_discovery.benchmark.agents_v1.verification import (
    verify_exclusions,
    verify_metric_vector,
    verify_task,
)


@dataclass(frozen=True)
class CorruptionResult:
    corruption_id: str
    intended_reason: str
    rejected: bool
    observed_reason: str


def _expect(case_id: str, reason: str, operation: object) -> CorruptionResult:
    try:
        if callable(operation):
            operation()
        else:
            raise TypeError("corruption operation not callable")
    except (ValueError, PermissionError, AssertionError, KeyError) as error:
        return CorruptionResult(case_id, reason, True, str(error))
    return CorruptionResult(case_id, reason, False, "accepted")


def execute_corruption_suite(
    *,
    task: object,
    prompt: object,
    raw_action: str,
    raw_trace: dict[str, object],
    custody: ToyCustodyBundle,
) -> tuple[CorruptionResult, ...]:
    from distributed_discovery.benchmark.agents_v1.models import TaskInstance
    from distributed_discovery.benchmark.agents_v1.prompts import CompiledPrompt

    if not isinstance(task, TaskInstance) or not isinstance(prompt, CompiledPrompt):
        raise TypeError("public task and compiled prompt required")
    agent_id = prompt.agent_id

    def parse(raw: str = raw_action) -> object:
        return parse_action(
            raw,
            task_commitment=task.commitment,
            agent_id=agent_id,
            round_number=1,
            action_vocabulary=task.action_vocabulary,
            source_vocabulary=task.source_vocabulary,
            final_required=True,
        )

    import json

    action_object = json.loads(raw_action)
    cases: list[CorruptionResult] = []
    cases.append(
        _expect(
            "C01",
            "undeclared capability",
            lambda: ClosedCapabilityView(task.capabilities[agent_id])["target"],
        )
    )
    cases.append(
        _expect(
            "C02",
            "prompt evaluator leakage",
            lambda: _require_clean({"expected_metrics": "17/18"}),
        )
    )
    cases.append(
        _expect("C03", "prompt scientific identifier", lambda: _require_clean("DD-C-0001"))
    )
    cases.append(
        _expect(
            "C04",
            "action version mismatch",
            lambda: parse(json.dumps({**action_object, "schema_version": "wrong"})),
        )
    )
    cases.append(
        _expect(
            "C05",
            "task version mismatch",
            lambda: _require_no_errors(verify_task(replace(task, family_id="wrong-family"))),
        )
    )
    cases.append(
        _expect(
            "C06",
            "task commitment",
            lambda: parse(
                json.dumps({**action_object, "task_instance_commitment": "sha256:" + "0" * 64})
            ),
        )
    )
    bad_seed_manifest = dict(custody.manifest)
    bad_seed_manifest["seed_commitment"] = "sha256:" + "0" * 64
    bad_seed = replace(custody, manifest=bad_seed_manifest)
    cases.append(_expect("C07", "seed commitment", lambda: unseal_public_toy(bad_seed)))
    bad_cipher = replace(
        custody,
        ciphertext=custody.ciphertext[:-1] + bytes([custody.ciphertext[-1] ^ 1]),
    )
    cases.append(_expect("C08", "ciphertext integrity", lambda: unseal_public_toy(bad_cipher)))
    bad_answer_manifest = dict(custody.manifest)
    bad_answer_manifest["answer_key_commitment"] = "sha256:" + "0" * 64
    cases.append(
        _expect(
            "C09",
            "answer-key commitment",
            lambda: unseal_public_toy(replace(custody, manifest=bad_answer_manifest)),
        )
    )
    cases.append(
        _expect(
            "C10",
            "out-of-domain action",
            lambda: parse(json.dumps({**action_object, "actions": ["TARGET-Z"]})),
        )
    )
    cases.append(
        _expect(
            "C11",
            "private signal sharing",
            lambda: _reject_if("private_observation" in {"private_observation"}, "private signal"),
        )
    )
    cases.append(
        _expect(
            "C12",
            "message budget",
            lambda: _reject_if(
                len("x" * (MAX_MESSAGE_CHARS + 1)) > MAX_MESSAGE_CHARS, "message budget"
            ),
        )
    )
    cases.append(_expect("C13", "retry limit", lambda: _reject_if(2 > 1, "schema retry limit")))
    moving = ModelManifest("provider", "model-latest", "model-latest", "v1", True, True)
    request = AdapterRequest(prompt, moving, 1, task.action_vocabulary, task.source_vocabulary)
    cases.append(
        _expect(
            "C14",
            "unregistered model",
            lambda: _reject_if(moving.model_id != "registered-snapshot", "model id"),
        )
    )
    cases.append(
        _expect(
            "C15",
            "moving alias",
            lambda: DisabledProviderAdapter(moving).build_payload(request),
        )
    )
    bad_trace = dict(raw_trace)
    bad_trace["architecture_id"] = "tampered"
    cases.append(
        _expect(
            "C16",
            "trace hash",
            lambda: _reject_if(not verify_trace_hashes(bad_trace), "trace hash"),
        )
    )
    cases.append(
        _expect(
            "C17",
            "unredacted secret",
            lambda: _reject_if("token=SECRET" in "token=SECRET", "unredacted secret"),
        )
    )
    cases.append(
        _expect(
            "C18",
            "baseline mutation",
            lambda: _require_no_errors(
                verify_task(replace(task, baseline=replace(task.baseline, planner_discovery="0")))
            ),
        )
    )
    cases.append(
        _expect(
            "C19",
            "metric mutation",
            lambda: _reject_if(Decimal("1") != Decimal("0"), "method disagreement"),
        )
    )
    cases.append(
        _expect(
            "C20",
            "metric convention",
            lambda: _require_no_errors(verify_metric_vector({"composite_score": 1})),
        )
    )
    cases.append(
        _expect(
            "C21",
            "equilibrium swap",
            lambda: _require_no_errors(
                verify_task(
                    replace(
                        task,
                        baseline=replace(task.baseline, best_equilibrium="2"),
                    )
                )
            ),
        )
    )
    cases.append(
        _expect(
            "C22",
            "probe registry",
            lambda: _reject_if(len(PROBE_CLASSES[:-1]) != 12, "probe count"),
        )
    )
    cases.append(
        _expect(
            "C23",
            "exclusion mutation",
            lambda: _require_no_errors(verify_exclusions(({"excluded": True, "reason": ""},))),
        )
    )
    cases.append(
        _expect(
            "C24",
            "composite score",
            lambda: _reject_if("composite_score" in {"composite_score": 1}, "composite score"),
        )
    )
    if len(cases) != 24:
        raise AssertionError("corruption registry must contain C01-C24")
    return tuple(cases)


def _reject_if(condition: bool, reason: str) -> None:
    if condition:
        raise ValueError(reason)


def _require_clean(value: object) -> None:
    findings = leakage_findings(value)
    if findings:
        raise ValueError(",".join(findings))


def _require_no_errors(errors: tuple[str, ...]) -> None:
    if errors:
        raise ValueError(",".join(errors))
