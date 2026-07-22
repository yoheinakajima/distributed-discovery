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
ATTENTION_TASK_SCHEMA_VERSION = "discoverybench-task-v2"
ATTENTION_PROTOCOL_SCHEMA_VERSION = "discoverybench-protocol-v2"
ATTENTION_METRIC_SCHEMA_VERSION = "discoverybench-metric-v2"
THRESHOLD_TASK_SCHEMA_VERSION = "discoverybench-task-v3"
THRESHOLD_PROTOCOL_SCHEMA_VERSION = "discoverybench-protocol-v3"
THRESHOLD_METRIC_SCHEMA_VERSION = "discoverybench-metric-v3"

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
    schema_version: str = PROTOCOL_SCHEMA_VERSION
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
                "declared_metadata": {"schema_version": self.schema_version},
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


def protocol_registry(version: str = "v1") -> list[dict[str, object]]:
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
    if version in {"v2", "v3"}:
        specs += [
            ("private-only", "Ignore the public signal and use private signals only."),
            ("public-only", "All agents use the public signal."),
            ("designated-reader", "Exactly one designated agent uses the public signal."),
            (
                "voluntary-attention-equilibrium",
                "Use the registered voluntary-attention equilibrium count.",
            ),
            (
                "audience-optimal-assignment",
                "Assign the public signal to the registered optimal audience.",
            ),
            ("conditional-private-dominant", "Follow private evidence on disagreement."),
            ("conditional-public-dominant", "Follow public evidence on disagreement."),
            ("third-option-contrarian", "Choose the third label on disagreement."),
        ]
        if version == "v3":
            specs += [
                (
                    "threshold-tied-mode-selection",
                    "Use the DD-016 registered independent tied-mode selection.",
                ),
                (
                    "threshold-minimum-team-planner",
                    "Assign minimum teams to the posterior top-L candidates.",
                ),
                (
                    "threshold-equilibrium-census",
                    "Audit the DD-017 weak-Nash and small-coalition registry.",
                ),
                (
                    "dynamic-autonomous-bayes",
                    "Use the DD-015 full-credit sequential Bayesian policy.",
                ),
                (
                    "dynamic-common-information-planner",
                    "Use the DD-015 exact common-information planner.",
                ),
                (
                    "team-token-mechanism",
                    "Use the DD-018 fixed balanced team-token rule.",
                ),
                (
                    "marginal-team-contribution",
                    "Use the DD-018 exactly-minimal-team contribution rule.",
                ),
                (
                    "universal-pooling-team",
                    "Use the DD-018 universal-pooling team response.",
                ),
            ]
    elif version != "v1":
        raise ValueError(f"unknown benchmark version: {version}")
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
            "schema_version": (
                PROTOCOL_SCHEMA_VERSION
                if version == "v1"
                else (
                    ATTENTION_PROTOCOL_SCHEMA_VERSION
                    if version == "v2"
                    else THRESHOLD_PROTOCOL_SCHEMA_VERSION
                )
            ),
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


def builtin_protocols(version: str = "v1") -> dict[str, BuiltinProtocol]:
    return {
        str(spec["protocol_id"]): BuiltinProtocol(
            protocol_id=str(spec["protocol_id"]),
            description=str(spec["description"]),
            capabilities=frozenset(
                str(value) for value in cast(list[object], spec["capabilities"])
            ),
            output_fields=tuple(str(value) for value in cast(list[object], spec["output_fields"])),
            schema_version=str(spec["schema_version"]),
        )
        for spec in protocol_registry(version)
    }


def metric_registry(version: str = "v1") -> list[dict[str, object]]:
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
    if version in {"v2", "v3"}:
        definitions += [
            (
                "attention-count",
                "Number of agents using the public signal.",
                "agents",
                ["attention_choices"],
            ),
            (
                "public-signal-user-count",
                "Number of agents whose action uses the public signal.",
                "agents",
                ["actions", "public_signal"],
            ),
            (
                "first-use-gain",
                "Discovery gain from the first public-signal user over private-only play.",
                "probability",
                ["discovery_frontier"],
            ),
            (
                "duplicate-use-loss",
                "Discovery loss from duplicate public-signal use relative to one user.",
                "probability",
                ["discovery_frontier"],
            ),
            (
                "attention-wedge",
                "Planner optimum minus the registered voluntary-attention equilibrium.",
                "probability",
                ["planner_optimum", "equilibrium_discovery"],
            ),
            (
                "audience-size",
                "Number of agents given access to the public signal.",
                "agents",
                ["information_permissions"],
            ),
            (
                "publicity-cost",
                "Discovery loss relative to the optimal audience assignment.",
                "probability",
                ["audience_frontier"],
            ),
            (
                "conditional-attention-category",
                "Registered conditional policy used on disagreement.",
                "category",
                ["contingent_policy"],
            ),
        ]
        if version == "v3":
            definitions += [
                (
                    "planner-discovery",
                    "Exact deterministic minimum-team planner discovery.",
                    "probability",
                    ["planner_frontier"],
                ),
                (
                    "expected-viable-candidates",
                    "Expected count of candidates meeting the declared threshold.",
                    "candidates",
                    ["occupancies", "threshold"],
                ),
                (
                    "zero-worst-equilibrium-games",
                    "Registered games whose worst weak pure equilibrium has zero discovery.",
                    "games",
                    ["equilibrium_registry"],
                ),
                (
                    "pair-instability-games",
                    "Registered games with no pairwise-strict-stable weak pure equilibrium.",
                    "games",
                    ["pair_deviations"],
                ),
                (
                    "tau-instability-games",
                    "Registered games with no exact-size-tau-strict-stable weak equilibrium.",
                    "games",
                    ["tau_deviations"],
                ),
                (
                    "tied-mode-failure-games",
                    "Registered games where tied-mode uniform mixing is not an equilibrium.",
                    "games",
                    ["mixed_action_payoffs"],
                ),
                (
                    "planner-strict-gain-rows",
                    "Exact rows where the dynamic planner strictly exceeds autonomous play.",
                    "rows",
                    ["dynamic_values"],
                ),
                (
                    "visibility-joint-loss-cells",
                    "Fixed-budget cells where visibility lowers discovery and dispersion.",
                    "cells",
                    ["visibility_control"],
                ),
                (
                    "stopping-action-savings-cells",
                    "Cells where stopping strictly lowers expected actions.",
                    "cells",
                    ["fixed_and_stopping_values"],
                ),
                (
                    "planner-portfolio-rows",
                    "Mechanism rows attaining the minimum-team planner portfolio.",
                    "rows",
                    ["mechanism_registry"],
                ),
                (
                    "pair-stable-rows",
                    "Rows passing the declared strict-member pair-deviation check.",
                    "rows",
                    ["pair_deviations"],
                ),
                (
                    "equilibrium-multiplicity",
                    "Exact pure-equilibrium count or fixture-ordered count vector.",
                    "count-or-vector",
                    ["equilibrium_registry"],
                ),
            ]
    elif version != "v1":
        raise ValueError(f"unknown benchmark version: {version}")
    return [
        {
            "schema_version": (
                METRIC_SCHEMA_VERSION
                if version == "v1"
                else (
                    ATTENTION_METRIC_SCHEMA_VERSION
                    if version == "v2"
                    else THRESHOLD_METRIC_SCHEMA_VERSION
                )
            ),
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
    schema_version: str = TASK_SCHEMA_VERSION,
) -> dict[str, object]:
    observables = sorted({metric for values in metrics.values() for metric in values})
    return {
        "schema_version": schema_version,
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


def task_registry(version: str = "v1") -> list[dict[str, object]]:
    canonical = "20260720T190336Z_DD-000_32dd1c32_217c602fa0"
    tasks = [
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
    if version == "v1":
        return tasks
    if version not in {"v2", "v3"}:
        raise ValueError(f"unknown benchmark version: {version}")
    for task in tasks:
        task["schema_version"] = ATTENTION_TASK_SCHEMA_VERSION
    attention_run = "20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b"
    audience_run = "20260721T215811Z_DD-013_09c07448_cdac4fb512"
    conditional_run = "20260721T222047Z_DD-014_f5f099a8_ea0276dd16"
    tasks += [
        _task(
            16,
            "dd012-attention-profiles",
            4,
            ["private-only", "designated-reader", "public-only"],
            {
                "private-only": {
                    "discovery": "15/16",
                    "attention-count": 0,
                    "public-signal-user-count": 0,
                    "first-use-gain": "1/32",
                    "duplicate-use-loss": "0",
                },
                "designated-reader": {
                    "discovery": "31/32",
                    "attention-count": 1,
                    "public-signal-user-count": 1,
                    "first-use-gain": "1/32",
                    "duplicate-use-loss": "0",
                },
                "public-only": {
                    "discovery": "3/4",
                    "attention-count": 4,
                    "public-signal-user-count": 4,
                    "first-use-gain": "1/32",
                    "duplicate-use-loss": "7/32",
                },
            },
            ["DD-C-0059"],
            [attention_run],
            schema_version=ATTENTION_TASK_SCHEMA_VERSION,
        ),
        _task(
            17,
            "dd012-equilibrium-optimum-cell",
            4,
            ["voluntary-attention-equilibrium", "designated-reader"],
            {
                "voluntary-attention-equilibrium": {
                    "discovery": "7/8",
                    "attention-count": 3,
                    "attention-wedge": "3/32",
                },
                "designated-reader": {
                    "discovery": "31/32",
                    "attention-count": 1,
                    "attention-wedge": "0",
                },
            },
            ["DD-C-0060", "DD-C-0061"],
            [attention_run],
            schema_version=ATTENTION_TASK_SCHEMA_VERSION,
        ),
        _task(
            18,
            "dd013-audience-design",
            4,
            ["public-only", "designated-reader", "audience-optimal-assignment"],
            {
                "public-only": {"discovery": "3/4", "audience-size": 4, "publicity-cost": "7/32"},
                "designated-reader": {
                    "discovery": "31/32",
                    "audience-size": 1,
                    "publicity-cost": "0",
                },
                "audience-optimal-assignment": {
                    "discovery": "31/32",
                    "audience-size": 1,
                    "publicity-cost": "0",
                },
            },
            ["DD-C-0062", "DD-C-0063"],
            [audience_run],
            schema_version=ATTENTION_TASK_SCHEMA_VERSION,
        ),
        _task(
            19,
            "dd013-implementation-mechanism",
            4,
            ["audience-optimal-assignment"],
            {
                "audience-optimal-assignment": {
                    "discovery": "31/32",
                    "audience-size": 1,
                    "transfer-budget": "0",
                }
            },
            ["DD-C-0064", "DD-C-0065"],
            [audience_run],
            reward="registered universal-pooling implementation",
            schema_version=ATTENTION_TASK_SCHEMA_VERSION,
        ),
        _task(
            20,
            "dd014-conditional-policies",
            4,
            [
                "conditional-private-dominant",
                "conditional-public-dominant",
                "third-option-contrarian",
            ],
            {
                "conditional-private-dominant": {
                    "discovery": "15/16",
                    "conditional-attention-category": "private-dominant",
                },
                "conditional-public-dominant": {
                    "discovery": "3/4",
                    "conditional-attention-category": "public-dominant",
                },
                "third-option-contrarian": {
                    "discovery": "895/1024",
                    "conditional-attention-category": "third-option-contrarian",
                },
            },
            ["DD-C-0066", "DD-C-0067"],
            [conditional_run],
            evidence="private and public conditionally independent signals",
            schema_version=ATTENTION_TASK_SCHEMA_VERSION,
        ),
    ]
    if version == "v2":
        return tasks

    for task in tasks:
        task["schema_version"] = THRESHOLD_TASK_SCHEMA_VERSION
    dd016_run = "20260722T021526Z_DD-016_00271ff8_123b2809e3"
    dd017_run = "20260722T024032Z_DD-017_033452f6_3d2c74fdfb"
    dd015_run = "20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a"
    dd018_run = "20260722T051847Z_DD-018_a193f602_3b3ddac173"
    tasks += [
        _task(
            21,
            "dd016-threshold-discovery",
            8,
            ["threshold-tied-mode-selection", "threshold-minimum-team-planner"],
            {
                "threshold-tied-mode-selection": {
                    "discovery": "275661897594857/576650390625000",
                    "planner-discovery": "223779310319051/333709716796875",
                    "expected-viable-candidates": "4605284003019928/3243658447265625",
                },
                "threshold-minimum-team-planner": {
                    "discovery": "223779310319051/333709716796875",
                    "planner-discovery": "223779310319051/333709716796875",
                    "expected-viable-candidates": 4,
                },
            },
            ["DD-C-0071", "DD-C-0073"],
            [dd016_run],
            coverage="threshold-two atomic discovery",
            reward="selected equal-split rule or common-payoff planner",
            schema_version=THRESHOLD_TASK_SCHEMA_VERSION,
        ),
        _task(
            22,
            "dd017-threshold-equilibrium-registry",
            6,
            ["threshold-equilibrium-census"],
            {
                "threshold-equilibrium-census": {
                    "zero-worst-equilibrium-games": 52,
                    "pair-instability-games": 8,
                    "tau-instability-games": 35,
                    "tied-mode-failure-games": 21,
                }
            },
            ["DD-C-0075", "DD-C-0076", "DD-C-0077", "DD-C-0078"],
            [dd017_run],
            reward="threshold-adjusted equal split",
            schema_version=THRESHOLD_TASK_SCHEMA_VERSION,
        ),
        _task(
            23,
            "dd015-dynamic-attention",
            3,
            ["dynamic-autonomous-bayes", "dynamic-common-information-planner"],
            {
                "dynamic-autonomous-bayes": {
                    "visibility-joint-loss-cells": 18,
                    "stopping-action-savings-cells": 32,
                },
                "dynamic-common-information-planner": {
                    "planner-strict-gain-rows": 38,
                    "stopping-action-savings-cells": 32,
                },
            },
            ["DD-C-0079", "DD-C-0080", "DD-C-0081"],
            [dd015_run],
            timing="sequential",
            feedback="visible prior actions with fixed-budget or stopping feedback",
            reward="full duplicate credit or common discovery objective",
            schema_version=THRESHOLD_TASK_SCHEMA_VERSION,
        ),
        _task(
            24,
            "dd018-minimum-viable-team-mechanisms",
            4,
            [
                "team-token-mechanism",
                "marginal-team-contribution",
                "universal-pooling-team",
            ],
            {
                "team-token-mechanism": {
                    "planner-portfolio-rows": 5,
                    "pair-stable-rows": 5,
                    "equilibrium-multiplicity": 25,
                },
                "marginal-team-contribution": {
                    "planner-portfolio-rows": 5,
                    "pair-stable-rows": 5,
                    "equilibrium-multiplicity": 21,
                },
                "universal-pooling-team": {
                    "planner-portfolio-rows": 0,
                    "pair-stable-rows": 1,
                    "equilibrium-multiplicity": "21,9,9,3,9",
                },
            },
            ["DD-C-0083", "DD-C-0084", "DD-C-0085", "DD-C-0086"],
            [dd018_run],
            coverage="threshold-two atomic discovery",
            reward="registered common-posterior team mechanism",
            schema_version=THRESHOLD_TASK_SCHEMA_VERSION,
        ),
    ]
    return tasks


def validate_task(task: Mapping[str, object], schema_path: Path | None = None) -> None:
    path = schema_path or repository_root() / "studies/DD-010-discoverybench/schemas" / (
        "task-v3.schema.json"
        if task.get("schema_version") == THRESHOLD_TASK_SCHEMA_VERSION
        else (
            "task-v2.schema.json"
            if task.get("schema_version") == ATTENTION_TASK_SCHEMA_VERSION
            else "task-v1.schema.json"
        )
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


def compatibility_matrix(version: str = "v1") -> list[dict[str, object]]:
    rows = []
    for task in task_registry(version):
        compatible = set(cast(list[str], task["compatible_protocols"]))
        for protocol in protocol_registry(version):
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
