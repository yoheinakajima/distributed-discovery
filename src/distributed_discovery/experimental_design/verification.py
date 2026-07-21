"""Materially separate DD-011 design, power, and provenance verifier."""

from __future__ import annotations

import copy
import json
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


def _independent_power_checks(power_table: list[dict[str, Any]]) -> int:
    hypothesis_index = {str(row["hypothesis_id"]): row for row in hypotheses()}
    scenario_index = {str(row["scenario_id"]): row for row in response_scenarios()}
    verified = 0
    for row in power_table:
        hypothesis = hypothesis_index[str(row["hypothesis_id"])]
        scenario = scenario_index[str(row["scenario_id"])]
        expected_effect = float(hypothesis["assumed_effect"]) * float(scenario["effect_multiplier"])
        if abs(float(row["assumed_effect"]) - expected_effect) > 1e-6:
            raise ValueError("power row effect does not match the frozen scenario")
        alpha = float(row["multiplicity_alpha"])
        critical = NormalDist().inv_cdf(1.0 - alpha)
        standard_error = float(row["standard_error"])
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


def verify_bundle(bundle: dict[str, Any], root: Path) -> dict[str, Any]:
    design = bundle["design"]
    schema = _load(root / "studies/DD-011-experimental-design/schemas/design-v1.schema.json")
    errors = sorted(
        Draft202012Validator(schema).iter_errors(design), key=lambda item: item.json_path
    )
    if errors:
        raise ValueError(f"design schema failed: {errors[0].message}")
    cells = treatment_cells()
    cell_ids = {row["cell_id"] for row in cells}
    if len(cells) != 20 or len(cell_ids) != 20:
        raise ValueError("treatment registry must contain 20 unique cells")
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
    verified_power_rows = _independent_power_checks(bundle["power_table"])
    exact_source_checks = _verify_exact_sources(root)
    return {
        "passed": True,
        "treatment_cells": len(cells),
        "hypotheses": len(design["hypotheses"]),
        "assignments": len(assignments),
        "power_rows_verified": verified_power_rows,
        "exact_source_checks": exact_source_checks,
        "no_real_data_boundary": True,
    }


def corruption_tests(bundle: dict[str, Any], root: Path) -> dict[str, bool]:
    altered_power = copy.deepcopy(bundle)
    altered_power["power_table"][0]["rejections"] += 1
    power_rejected = False
    try:
        verify_bundle(altered_power, root)
    except ValueError:
        power_rejected = True

    leaked_record = copy.deepcopy(bundle)
    leaked_record["randomization"]["assignments"][0]["participant_id"] = "REAL-001"
    real_data_rejected = False
    try:
        verify_bundle(leaked_record, root)
    except ValueError:
        real_data_rejected = True

    altered_boundary = copy.deepcopy(bundle)
    altered_boundary["design"]["no_human_data"] = False
    boundary_rejected = False
    try:
        verify_bundle(altered_boundary, root)
    except ValueError:
        boundary_rejected = True
    return {
        "altered_power_rejected": power_rejected,
        "real_identifier_rejected": real_data_rejected,
        "altered_boundary_rejected": boundary_rejected,
    }
