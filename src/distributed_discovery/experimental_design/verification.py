"""Materially separate DD-011 design, power, and provenance verifier."""

from __future__ import annotations

import copy
import json
import math
import random
from collections import Counter
from pathlib import Path
from statistics import NormalDist
from typing import Any

from jsonschema import Draft202012Validator

from distributed_discovery.experimental_design.model import (
    NO_HUMAN_DATA_NOTICE,
    hypotheses,
    response_scenarios,
    treatment_cells,
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _independent_power_checks(
    power_table: list[dict[str, Any]],
    hypothesis_rows: list[dict[str, Any]],
    scenario_rows: list[dict[str, Any]],
) -> int:
    hypothesis_index = {str(row["hypothesis_id"]): row for row in hypothesis_rows}
    scenario_index = {str(row["scenario_id"]): row for row in scenario_rows}
    family_sizes = Counter(str(row["multiplicity_family"]) for row in hypothesis_rows)
    verified = 0
    for row in power_table:
        hypothesis = hypothesis_index[str(row["hypothesis_id"])]
        scenario = scenario_index[str(row["scenario_id"])]
        expected_effect = float(hypothesis["assumed_effect"]) * float(scenario["effect_multiplier"])
        if abs(float(row["assumed_effect"]) - expected_effect) > 1e-6:
            raise ValueError("power row effect does not match the frozen scenario")
        alpha = 0.05 / family_sizes[str(hypothesis["multiplicity_family"])]
        if abs(float(row["multiplicity_alpha"]) - alpha) > 1e-6:
            raise ValueError("power row multiplicity threshold mismatch")
        critical = NormalDist().inv_cdf(1.0 - alpha)
        retained = int(row["sample_size"]) * (1.0 - float(scenario["attrition_rate"]))
        treated = max(0.01, min(0.99, 0.50 + expected_effect))
        independent_variance = 0.25 / (retained / 2.0) + treated * (1.0 - treated) / (
            retained / 2.0
        )
        design_effect = 1.0 + 7.0 * float(scenario["intracluster_correlation"])
        standard_error = math.sqrt(independent_variance * design_effect) * float(
            scenario["noise_multiplier"]
        )
        if abs(float(row["standard_error"]) - standard_error) > 1e-6:
            raise ValueError("power row standard error mismatch")
        rng = random.Random(int(row["row_seed"]))
        reproduced = sum(
            rng.gauss(expected_effect, standard_error) / standard_error > critical
            for _ in range(int(row["replications"]))
        )
        if reproduced != int(row["rejections"]):
            raise ValueError("independent power recomputation failed")
        if abs(float(row["power"]) - reproduced / int(row["replications"])) > 1e-9:
            raise ValueError("power proportion does not match rejection count")
        verified += 1
    return verified


def _verify_exact_sources(root: Path) -> int:
    source_choice = _load(
        root
        / (
            "results/verified/20260721T141527Z_DD-008_0d11dc77_7e0c8f1d66/"
            "outputs/source-choice-grid.json"
        )
    )
    trap = next(row for row in source_choice if row["accuracy"] == "2/3" and row["cost"] == "1/8")
    if not (
        trap["common_source_trap"]
        and trap["profiles"]["CC"]["social_net_value"] == "2/3"
        and trap["profiles"]["CI"]["social_net_value"] == "55/72"
    ):
        raise ValueError("DD-008 exact limiting cell mismatch")
    n_agent = _load(
        root
        / (
            "results/verified/20260721T163030Z_DD-008A_8b70668b_06307caab4/"
            "outputs/n-agent-summary.json"
        )
    )
    if n_agent != {
        "agent_range": [2, 3, 4, 5, 6, 7, 8],
        "direct_enumerator_agrees": True,
        "grid_cells": 126,
    }:
        raise ValueError("DD-008A source summary mismatch")
    mechanism = _load(
        root
        / (
            "results/verified/20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b/"
            "outputs/joint-mechanism-summary.json"
        )
    )
    if (
        mechanism["strict_rows"] != 16
        or mechanism["maximum_margin"] != "13/72"
        or mechanism["best_strict_discovery"] != "11/12"
    ):
        raise ValueError("DD-006B source summary mismatch")
    atlas = _load(
        root
        / "results/verified/20260721T171249Z_DD-009_bc78d249_0c3851c41a/outputs/atlas-summary.json"
    )
    if (
        atlas["valid_cells"] != 20
        or atlas["pareto_cells"] != 12
        or atlas["maximum_discovery"] != "11/12"
    ):
        raise ValueError("DD-009 source summary mismatch")
    return 4


def _verify_program_v4_sources(root: Path) -> int:
    threshold = _load(
        root
        / (
            "results/verified/20260722T021526Z_DD-016_00271ff8_123b2809e3/"
            "outputs/canonical-metrics.json"
        )
    )
    if (
        threshold["threshold_rows"] != 8
        or threshold["common_deterministic_mode"] != "37916217637/98876953125"
        or threshold["paired_planner"] != "223779310319051/333709716796875"
    ):
        raise ValueError("DD-016 source summary mismatch")
    dynamic = _load(
        root / ("results/verified/20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a/outputs/summary.json")
    )
    if (
        dynamic["objective_rows"] != 64
        or dynamic["planner_strictly_better_rows"] != 38
        or dynamic["visibility_reduces_discovery_fixed_rows"] != 18
        or dynamic["stopping_reduces_expected_actions_rows"] != 32
    ):
        raise ValueError("DD-015 dynamic source summary mismatch")
    threshold_dynamic = _load(
        root
        / (
            "results/verified/20260722T044453Z_DD-015_34bc4379_33e1da478b/"
            "outputs/threshold-two-summary.json"
        )
    )
    if (
        threshold_dynamic["parameter_cells"] != 16
        or threshold_dynamic["objective_rows"] != 32
        or threshold_dynamic["join_viable_team_rows"] != 32
        or threshold_dynamic["start_new_singleton_rows"] != 32
    ):
        raise ValueError("DD-015 threshold-two source summary mismatch")
    mechanisms = _load(
        root / ("results/verified/20260722T051847Z_DD-018_a193f602_3b3ddac173/outputs/summary.json")
    )
    if (
        mechanisms["mechanism_fixture_rows"] != 50
        or mechanisms["planner_portfolio_rows"] != 40
        or mechanisms["marginal_contribution_planner_stable_rows"] != 5
        or mechanisms["universal_pooling_planner_rows"] != 0
    ):
        raise ValueError("DD-018 source summary mismatch")
    return 4


def verify_bundle(bundle: dict[str, Any], root: Path, version: str = "v1") -> dict[str, Any]:
    design = bundle["design"]
    if version == "v1":
        cell_rows = treatment_cells()
        hypothesis_rows = hypotheses()
        scenario_rows = response_scenarios()
        expected_counts = (20, 8, 8)
    elif version == "v2":
        from distributed_discovery.experimental_design.attention_model import (
            hypotheses as attention_hypotheses,
        )
        from distributed_discovery.experimental_design.attention_model import (
            response_scenarios as attention_scenarios,
        )
        from distributed_discovery.experimental_design.attention_model import (
            treatment_cells as attention_cells,
        )

        cell_rows = attention_cells()
        hypothesis_rows = attention_hypotheses()
        scenario_rows = attention_scenarios()
        expected_counts = (29, 14, 11)
    elif version == "v3":
        from distributed_discovery.experimental_design.threshold_dynamic_model import (
            hypotheses as program_v4_hypotheses,
        )
        from distributed_discovery.experimental_design.threshold_dynamic_model import (
            program_v4_model_checks,
        )
        from distributed_discovery.experimental_design.threshold_dynamic_model import (
            response_scenarios as program_v4_scenarios,
        )
        from distributed_discovery.experimental_design.threshold_dynamic_model import (
            treatment_cells as program_v4_cells,
        )

        cell_rows = program_v4_cells()
        hypothesis_rows = program_v4_hypotheses()
        scenario_rows = program_v4_scenarios()
        expected_counts = (37, 20, 14)
        if bundle["exact_model_checks"][-4:] != program_v4_model_checks():
            raise ValueError("Program V4 model-check registry mismatch")
    else:
        raise ValueError(f"unknown experiment version: {version}")
    schema = _load(
        root / f"studies/DD-011-experimental-design/schemas/design-{version}.schema.json"
    )
    errors = sorted(
        Draft202012Validator(schema).iter_errors(design), key=lambda item: item.json_path
    )
    if errors:
        raise ValueError(f"design schema failed: {errors[0].message}")
    cells = cell_rows
    cell_ids = {row["cell_id"] for row in cells}
    if len(cells) != expected_counts[0] or len(cell_ids) != expected_counts[0]:
        raise ValueError("treatment registry has the wrong number of unique cells")
    if len(design["hypotheses"]) != expected_counts[1]:
        raise ValueError("hypothesis registry count mismatch")
    if len(design["response_scenarios"]) != expected_counts[2]:
        raise ValueError("response-scenario registry count mismatch")
    outcome_ids = {row["outcome_id"] for row in design["outcomes"]}
    for hypothesis in design["hypotheses"]:
        if (
            hypothesis["treatment_cell"] not in cell_ids
            or hypothesis["control_cell"] not in cell_ids
        ):
            raise ValueError("hypothesis references an unknown cell")
        if hypothesis["outcome"] not in outcome_ids:
            raise ValueError("hypothesis references an unknown outcome")
    assignments = bundle["randomization"]["assignments"]
    if not assignments or any(
        not str(row["participant_id"]).startswith("SYN-P")
        or not str(row["session_id"]).startswith("SYN-S")
        for row in assignments
    ):
        raise ValueError("non-synthetic identifier rejected")
    counts = Counter(str(row["cell_id"]) for row in assignments)
    if set(counts) != cell_ids or len(set(counts.values())) != 1:
        raise ValueError("randomization is not cell-balanced")
    if not design["no_human_data"] or design["notice"] != NO_HUMAN_DATA_NOTICE:
        raise ValueError("no-real-data boundary is absent")
    if any(not row["synthetic_only"] for row in bundle["synthetic_sample"]):
        raise ValueError("sample contains a non-synthetic record")
    verified_power_rows = _independent_power_checks(
        bundle["power_table"], hypothesis_rows, scenario_rows
    )
    exact_source_checks = _verify_exact_sources(root)
    program_v4_source_checks = _verify_program_v4_sources(root) if version == "v3" else 0
    return {
        "passed": True,
        "treatment_cells": len(cells),
        "hypotheses": len(design["hypotheses"]),
        "assignments": len(assignments),
        "power_rows_verified": verified_power_rows,
        "exact_source_checks": exact_source_checks,
        "program_v4_source_checks": program_v4_source_checks,
        "no_real_data_boundary": True,
    }


def corruption_tests(bundle: dict[str, Any], root: Path, version: str = "v1") -> dict[str, bool]:
    altered_power = copy.deepcopy(bundle)
    altered_power["power_table"][0]["rejections"] += 1
    power_rejected = False
    try:
        verify_bundle(altered_power, root, version)
    except ValueError:
        power_rejected = True

    leaked_record = copy.deepcopy(bundle)
    leaked_record["randomization"]["assignments"][0]["participant_id"] = "REAL-001"
    real_data_rejected = False
    try:
        verify_bundle(leaked_record, root, version)
    except ValueError:
        real_data_rejected = True

    altered_boundary = copy.deepcopy(bundle)
    altered_boundary["design"]["no_human_data"] = False
    boundary_rejected = False
    try:
        verify_bundle(altered_boundary, root, version)
    except ValueError:
        boundary_rejected = True
    results = {
        "altered_power_rejected": power_rejected,
        "real_identifier_rejected": real_data_rejected,
        "altered_boundary_rejected": boundary_rejected,
    }
    if version == "v3":
        altered_source = copy.deepcopy(bundle)
        altered_source["exact_model_checks"][-1]["expected"]["planner_portfolio_rows"] = 41
        source_registry_rejected = False
        try:
            verify_bundle(altered_source, root, version)
        except ValueError:
            source_registry_rejected = True
        results["altered_program_v4_source_registry_rejected"] = source_registry_rejected
    return results
