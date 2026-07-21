"""Versioned DiscoveryBench registries and capability-scoped protocol interface."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import cast

import jsonschema

from distributed_discovery.validation.bootstrap import repository_root

TASK_SCHEMA_VERSION = "discoverybench-task-v1"
PROTOCOL_SCHEMA_VERSION = "discoverybench-protocol-v1"
METRIC_SCHEMA_VERSION = "discoverybench-metric-v1"

PROHIBITED_CAPABILITIES = frozenset(
    {
        "target_state",
        "other_agents_private_signals",
        "future_outcomes",
        "undeclared_source_ids",
        "global_evaluator_state",
        "expected_metrics",
        "reference_claims",
        "reference_runs",
    }
)


class InformationBoundaryError(PermissionError):
    """Raised when a protocol asks for undeclared benchmark information."""


@dataclass(frozen=True)
class CapabilityView(Mapping[str, object]):
    """Immutable allow-list view passed to protocols."""

    _values: Mapping[str, object]
    _allowed: frozenset[str]

    def __getitem__(self, key: str) -> object:
        if key not in self._allowed or key in PROHIBITED_CAPABILITIES:
            raise InformationBoundaryError(f"undeclared capability: {key}")
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._allowed - PROHIBITED_CAPABILITIES))

    def __len__(self) -> int:
        return len(self._allowed - PROHIBITED_CAPABILITIES)


@dataclass(frozen=True)
class BuiltinProtocol:
    protocol_id: str
    description: str
    capabilities: frozenset[str]
    output_fields: tuple[str, ...]
    external: bool = False
    enabled: bool = True

    def run(self, view: CapabilityView) -> Mapping[str, object]:
        """Return a deterministic declared decision without evaluator access."""
        task_id = str(view["task_id"])
        action_space = str(view["action_space"])
        return MappingProxyType(
            {
                "protocol_id": self.protocol_id,
                "task_id": task_id,
                "decision": f"{self.protocol_id}:{action_space}",
                "declared_metadata": {"schema_version": PROTOCOL_SCHEMA_VERSION},
            }
        )


@dataclass(frozen=True)
class ExternalAdapter:
    """Disabled-by-default boundary for non-repository agents."""

    adapter_id: str
    enabled: bool = False
    credentials: tuple[str, ...] = ()

    def run(self, _: CapabilityView) -> Mapping[str, object]:
        if not self.enabled:
            raise RuntimeError("external adapters are disabled")
        raise RuntimeError("no external provider implementation is bundled")


@dataclass(frozen=True)
class DeterministicMockAdapter:
    adapter_id: str = "mock-local"

    def run(self, view: CapabilityView) -> Mapping[str, object]:
        return MappingProxyType({"task_id": view["task_id"], "decision": "mock"})


def protocol_registry() -> list[dict[str, object]]:
    specs = [
        ("blind-distinct", "Coordinate distinct actions without evidence."),
        ("private-clue-following", "Act on each agent's declared private clue."),
        ("consensus", "Pool declared messages into one repeated action."),
        ("pooled-planner", "Assign a declared pooled-information portfolio."),
        ("anonymous-market", "Use the registered anonymous selected equilibrium."),
        ("posterior-sampling", "Sample actions from each declared posterior."),
        ("ex-ante-role-policy", "Commit to differentiated contingent roles ex ante."),
        ("sequential-greedy", "Use visible feedback in registered greedy order."),
        ("marginal-coverage-greedy", "Choose the largest declared marginal coverage."),
        ("sole-rescue-response", "Respond to the registered sole-rescue reward."),
        ("dd006a-mechanism", "Use the registered weak DD-006A mechanism row."),
        ("dd006b-mechanism", "Use the registered strict DD-006B mechanism row."),
        ("registered-atlas-architecture", "Execute one registered coherent Atlas cell."),
    ]
    capabilities = frozenset(
        {
            "task_id",
            "task_family",
            "per_agent_information",
            "communication_permissions",
            "source_choice_permissions",
            "report_message_space",
            "action_space",
            "budget",
            "timing",
            "feedback",
            "reward_rule",
        }
    )
    return [
        {
            "schema_version": PROTOCOL_SCHEMA_VERSION,
            "protocol_id": protocol_id,
            "description": description,
            "capabilities": sorted(capabilities),
            "output_fields": [
                "source_choice",
                "report",
                "message",
                "action",
                "contingent_policy",
                "declared_metadata",
            ],
            "external": False,
            "enabled": True,
        }
        for protocol_id, description in specs
    ]


def builtin_protocols() -> dict[str, BuiltinProtocol]:
    return {
        str(spec["protocol_id"]): BuiltinProtocol(
            protocol_id=str(spec["protocol_id"]),
            description=str(spec["description"]),
            capabilities=frozenset(
                str(value) for value in cast(list[object], spec["capabilities"])
            ),
            output_fields=tuple(str(value) for value in cast(list[object], spec["output_fields"])),
        )
        for spec in protocol_registry()
    }


def metric_registry() -> list[dict[str, object]]:
    definitions = [
        (
            "discovery",
            "Expected union discovery or registered coverage value.",
            "probability-or-coverage",
            ["covered_outcomes"],
        ),
        (
            "average-action-quality",
            "Expected correct actions divided by actions.",
            "probability",
            ["actions", "target_outcomes"],
        ),
        ("distinct-actions", "Expected number of distinct actions.", "actions", ["actions"]),
        (
            "weighted-coverage",
            "Declared weighted union coverage.",
            "coverage-units",
            ["coverage_sets", "weights"],
        ),
        ("redundant-hits", "Expected successful hits beyond the first.", "hits", ["target_hits"]),
        ("action-concentration", "Declared concentration of action shares.", "index", ["actions"]),
        (
            "source-concentration",
            "Declared concentration of source exposure.",
            "index",
            ["source_ids"],
        ),
        (
            "effective-channels",
            "Model-defined reciprocal source concentration.",
            "channels",
            ["source_ids", "channel_definition"],
        ),
        (
            "protocol-loss",
            "Registered frontier minus protocol discovery.",
            "objective-units",
            ["frontier", "discovery"],
        ),
        (
            "recovery-budget",
            "Smallest action budget recovering the comparator.",
            "actions",
            ["budget_frontier", "comparator"],
        ),
        (
            "information-cost",
            "Expected declared source-acquisition cost.",
            "payoff-units",
            ["source_choices", "costs"],
        ),
        ("expected-actions", "Expected number of actions used.", "actions", ["actions"]),
        ("expected-rounds", "Expected number of decision rounds.", "rounds", ["rounds"]),
        (
            "private-payoff",
            "Expected declared private payoff.",
            "payoff-units",
            ["rewards", "costs"],
        ),
        (
            "social-net-value",
            "Discovery value net of declared information and transfer costs.",
            "payoff-units",
            ["discovery", "information_cost", "transfer_budget"],
        ),
        ("transfer-budget", "Expected external transfer budget.", "payoff-units", ["transfers"]),
        (
            "truthfulness",
            "Whether truthful reporting satisfies the registered incentive condition.",
            "boolean-or-margin",
            ["reports", "deviations"],
        ),
        (
            "obedience",
            "Whether recommended action satisfies the registered incentive condition.",
            "boolean-or-margin",
            ["recommendations", "deviations"],
        ),
        (
            "strict-margin",
            "Minimum truthful/obedient payoff advantage over registered deviations.",
            "payoff-units",
            ["deviation_payoffs"],
        ),
    ]
    return [
        {
            "schema_version": METRIC_SCHEMA_VERSION,
            "metric_id": metric_id,
            "definition": definition,
            "scope": "registered task observables only",
            "units": units,
            "required_observables": required,
            "status": "exact-or-estimated-per-result",
            "aggregation": "task-level; family profiles and Pareto vectors only",
        }
        for metric_id, definition, units, required in definitions
    ]


def _task(
    number: int,
    family: str,
    agents: int,
    protocols: list[str],
    metrics: dict[str, dict[str, str | int | bool]],
    claims: list[str],
    runs: list[str],
    *,
    evidence: str = "conditionally independent declared channels",
    timing: str = "simultaneous",
    feedback: str = "none",
    coverage: str = "union discovery",
    reward: str = "common discovery objective",
) -> dict[str, object]:
    observables = sorted({metric for values in metrics.values() for metric in values})
    return {
        "schema_version": TASK_SCHEMA_VERSION,
        "task_id": f"DB-G{number:02d}",
        "task_family": family,
        "world_space": "finite registered world",
        "prior": "registered exact rational prior",
        "target_law": "registered finite target law",
        "evidence_channels": [evidence],
        "source_dependence": evidence,
        "agent_count": agents,
        "per_agent_information": [["declared private observation"] for _ in range(agents)],
        "communication_permissions": "task-family declared messages only",
        "source_choice_permissions": "task-family declared source choices only",
        "report_message_space": "finite registered message space",
        "action_space": "finite registered search actions",
        "coverage_function": coverage,
        "budget": "registered finite action budget",
        "timing": timing,
        "feedback": feedback,
        "reward_rule": reward,
        "social_objective": "registered discovery or net-value objective",
        "private_objective": "registered private payoff or protocol control",
        "evaluator": "exact",
        "seed_policy": "no randomness beyond exact model integration",
        "reference_claims": claims,
        "reference_runs": runs,
        "public_status": "golden",
        "compatible_protocols": protocols,
        "observables": observables,
        "expected_metrics": metrics,
    }


def task_registry() -> list[dict[str, object]]:
    canonical = "20260720T190336Z_DD-000_32dd1c32_217c602fa0"
    return [
        _task(
            1,
            "canonical-atomic-boxes",
            8,
            ["blind-distinct", "pooled-planner"],
            {
                "blind-distinct": {"discovery": "1/2", "distinct-actions": "8"},
                "pooled-planner": {
                    "discovery": "860391662035297/1001129150390625",
                    "recovery-budget": 7,
                },
            },
            ["DD-C-0003", "DD-C-0006", "DD-C-0008"],
            [canonical, "20260721T012208Z_DD-000_8e4b55e2_e8321d1048"],
        ),
        _task(
            2,
            "private-team-role-counterexample",
            2,
            ["ex-ante-role-policy"],
            {"ex-ante-role-policy": {"discovery": "7/10", "protocol-loss": "0"}},
            ["DD-C-0021"],
            ["20260720T200447Z_DD-001_6eb12861_ba766d1eba"],
        ),
        _task(
            3,
            "canonical-private-team-optimum",
            8,
            ["private-clue-following"],
            {"private-clue-following": {"discovery": "325089/390625", "protocol-loss": "0"}},
            ["DD-C-0038"],
            ["20260721T022739Z_DD-001_358cb1eb_cd16846ba5"],
        ),
        _task(
            4,
            "deterministic-disclosure-fixture",
            2,
            ["consensus"],
            {"consensus": {"discovery": "5/9"}},
            ["DD-C-0030"],
            ["20260720T225848Z_DD-002_94607423_e29b1460ae"],
        ),
        _task(
            5,
            "six-rule-selection-fixture",
            2,
            ["anonymous-market"],
            {"anonymous-market": {"discovery": "171/308", "protocol-loss": "1/2772"}},
            ["DD-C-0040", "DD-C-0041"],
            ["20260721T025802Z_DD-002_73a85c71_b0e5b6dc49"],
        ),
        _task(
            6,
            "homogeneous-source-network",
            4,
            ["private-clue-following"],
            {"private-clue-following": {"discovery": "8/9", "effective-channels": "8/5"}},
            ["DD-C-0032", "DD-C-0033"],
            ["20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1"],
            evidence="homogeneous conditionally independent sources",
        ),
        _task(
            7,
            "heterogeneous-source-moment-counterexample",
            4,
            ["posterior-sampling"],
            {"posterior-sampling": {"discovery": "3/4", "source-concentration": "17/25"}},
            ["DD-C-0043", "DD-C-0044"],
            ["20260721T032358Z_DD-003_84238b76_2cbc13e66a"],
            evidence="heterogeneous conditionally independent sources",
        ),
        _task(
            8,
            "perfect-elimination-sequential",
            1,
            ["sequential-greedy"],
            {
                "sequential-greedy": {
                    "discovery": "7/10",
                    "expected-actions": "109/40",
                    "expected-rounds": "109/40",
                }
            },
            ["DD-C-0045"],
            ["20260721T050038Z_DD-004_8ab02e7f_71d84de7c4"],
            timing="sequential",
            feedback="perfect failure elimination",
        ),
        _task(
            9,
            "overlapping-weighted-coverage",
            2,
            ["marginal-coverage-greedy"],
            {"marginal-coverage-greedy": {"weighted-coverage": "4", "distinct-actions": "2"}},
            ["DD-C-0046"],
            ["20260721T050706Z_DD-005_be3b544c_98698dee2f"],
            coverage="deterministic weighted union coverage",
        ),
        _task(
            10,
            "score-difference-mechanism",
            2,
            ["sole-rescue-response"],
            {
                "sole-rescue-response": {
                    "discovery": "8/9",
                    "truthfulness": True,
                    "obedience": True,
                    "strict-margin": "0",
                    "transfer-budget": "0",
                }
            },
            ["DD-C-0048"],
            ["20260721T051457Z_DD-006_d49a50ea_068bce4af3"],
            reward="registered positive sole-rescue score difference",
        ),
        _task(
            11,
            "dd006a-transfer-frontier",
            2,
            ["dd006a-mechanism"],
            {
                "dd006a-mechanism": {
                    "discovery": "11/12",
                    "truthfulness": True,
                    "obedience": True,
                    "strict-margin": "0",
                    "transfer-budget": "0",
                }
            },
            ["DD-C-0050"],
            ["20260721T140745Z_DD-006_401ad624_c942f43e42"],
            reward="registered normalized linear transfer",
        ),
        _task(
            12,
            "dd006b-strict-joint-mechanism",
            2,
            ["dd006b-mechanism"],
            {
                "dd006b-mechanism": {
                    "discovery": "11/12",
                    "truthfulness": True,
                    "obedience": True,
                    "strict-margin": "13/72",
                    "transfer-budget": "35/24",
                }
            },
            ["DD-C-0053"],
            ["20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b"],
            reward="registered subsidized joint mechanism",
        ),
        _task(
            13,
            "two-agent-evidence-acquisition",
            2,
            ["private-clue-following"],
            {
                "private-clue-following": {
                    "discovery": "8/9",
                    "information-cost": "1/8",
                    "social-net-value": "55/72",
                }
            },
            ["DD-C-0051"],
            ["20260721T141527Z_DD-008_0d11dc77_7e0c8f1d66"],
            evidence="one common and one independent source choice",
        ),
        _task(
            14,
            "n-agent-source-choice",
            8,
            ["ex-ante-role-policy"],
            {
                "ex-ante-role-policy": {
                    "discovery": "65535/65536",
                    "information-cost": "0",
                    "effective-channels": "8",
                }
            },
            ["DD-C-0052"],
            ["20260721T163030Z_DD-008A_8b70668b_06307caab4"],
            evidence="eight independent p=3/4 sources",
        ),
        _task(
            15,
            "architecture-atlas",
            2,
            ["registered-atlas-architecture"],
            {
                "registered-atlas-architecture": {
                    "discovery": "5/6",
                    "average-action-quality": "5/8",
                    "expected-actions": "4/3",
                    "expected-rounds": "4/3",
                    "social-net-value": "5/6",
                }
            },
            ["DD-C-0054"],
            ["20260721T171249Z_DD-009_bc78d249_0c3851c41a"],
            timing="sequential",
            feedback="perfect failure elimination",
        ),
    ]


def validate_task(task: Mapping[str, object], schema_path: Path | None = None) -> None:
    path = (
        schema_path
        or repository_root() / "studies/DD-010-discoverybench/schemas/task-v1.schema.json"
    )
    schema = __import__("json").loads(path.read_text(encoding="utf-8"))
    jsonschema.validate(dict(task), schema)
    information = cast(list[object], task["per_agent_information"])
    agent_count = cast(int, task["agent_count"])
    observables = cast(list[str], task["observables"])
    expected = cast(dict[str, dict[str, object]], task["expected_metrics"])
    compatible = cast(list[str], task["compatible_protocols"])
    if len(information) != agent_count:
        raise ValueError("per-agent information count must equal agent count")
    if set(observables) != {metric for values in expected.values() for metric in values}:
        raise ValueError("observables must exactly match emitted metrics")
    if set(compatible) != set(expected):
        raise ValueError("every compatible protocol needs one exact result")


def task_view(task: Mapping[str, object], protocol: BuiltinProtocol) -> CapabilityView:
    values = MappingProxyType(dict(task))
    return CapabilityView(values, protocol.capabilities)


def compatibility_matrix() -> list[dict[str, object]]:
    rows = []
    for task in task_registry():
        compatible = set(cast(list[str], task["compatible_protocols"]))
        for protocol in protocol_registry():
            protocol_id = str(protocol["protocol_id"])
            rows.append(
                {
                    "task_id": task["task_id"],
                    "protocol_id": protocol_id,
                    "compatible": protocol_id in compatible,
                    "reason": "declared exact fixture"
                    if protocol_id in compatible
                    else "protocol/task contract not registered",
                }
            )
    return rows
