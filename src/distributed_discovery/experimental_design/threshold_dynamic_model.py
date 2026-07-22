"""Versioned threshold and dynamic extension to the DD-011 synthetic design."""

from __future__ import annotations

from typing import Any

from distributed_discovery.experimental_design import attention_model as v2

SCHEMA_VERSION = "dd011-experiment-v3"

PROGRAM_V4_FACTOR_LEVELS: dict[str, tuple[str, ...]] = {
    **v2.ATTENTION_FACTOR_LEVELS,
    "reward": (*v2.ATTENTION_FACTOR_LEVELS["reward"], "team_tokens"),
    "team_threshold": ("none", "two"),
    "portfolio_rule": (
        "none",
        "paired_planner",
        "common_mode",
        "private_following",
        "team_tokens",
        "dynamic_planner",
    ),
    "history_visibility": ("not_dynamic", "hidden", "visible"),
    "action_horizon": ("one_shot", "fixed_budget", "stopping"),
}


def treatment_cells() -> list[dict[str, str]]:
    defaults = {
        "team_threshold": "none",
        "portfolio_rule": "none",
        "history_visibility": "not_dynamic",
        "action_horizon": "one_shot",
    }
    cells = [{**cell, **defaults} for cell in v2.treatment_cells()]
    baseline = dict(cells[0])

    def program_v4_cell(cell_id: str, **updates: str) -> dict[str, str]:
        return {**baseline, "cell_id": cell_id, **updates}

    cells += [
        program_v4_cell(
            "T29-threshold-paired-planner",
            team_threshold="two",
            portfolio_rule="paired_planner",
        ),
        program_v4_cell(
            "T30-threshold-common-mode",
            team_threshold="two",
            portfolio_rule="common_mode",
        ),
        program_v4_cell(
            "T31-threshold-private-following",
            team_threshold="two",
            portfolio_rule="private_following",
        ),
        program_v4_cell(
            "T32-threshold-team-tokens",
            reward="team_tokens",
            team_threshold="two",
            portfolio_rule="team_tokens",
        ),
        program_v4_cell(
            "T33-dynamic-bayes-hidden-fixed",
            history_visibility="hidden",
            action_horizon="fixed_budget",
        ),
        program_v4_cell(
            "T34-dynamic-bayes-visible-fixed",
            timing="sequential_visible",
            history_visibility="visible",
            action_horizon="fixed_budget",
        ),
        program_v4_cell(
            "T35-dynamic-planner-hidden-fixed",
            portfolio_rule="dynamic_planner",
            history_visibility="hidden",
            action_horizon="fixed_budget",
        ),
        program_v4_cell(
            "T36-dynamic-planner-hidden-stopping",
            portfolio_rule="dynamic_planner",
            history_visibility="hidden",
            action_horizon="stopping",
        ),
    ]
    return cells


def outcomes() -> list[dict[str, str]]:
    return v2.outcomes() + [
        {
            "outcome_id": "viable_team_count",
            "role": "primary",
            "unit": "count",
            "definition": (
                "Candidates receiving at least the registered threshold number of actions."
            ),
        },
        {
            "outcome_id": "threshold_portfolio_efficiency",
            "role": "primary",
            "unit": "proportion",
            "definition": "Realized viable-team discovery divided by the frozen planner value.",
        },
        {
            "outcome_id": "expected_actions",
            "role": "secondary",
            "unit": "action count",
            "definition": "Submitted actions before the fixed horizon or registered stopping time.",
        },
        {
            "outcome_id": "action_savings",
            "role": "secondary",
            "unit": "action count",
            "definition": (
                "Fixed action budget minus submitted actions at the registered stopping time."
            ),
        },
    ]


def hypotheses() -> list[dict[str, Any]]:
    return v2.hypotheses() + [
        {
            "hypothesis_id": "H15",
            "question": (
                "Does paired threshold allocation improve discovery over common-mode crowding?"
            ),
            "treatment_cell": "T29-threshold-paired-planner",
            "control_cell": "T30-threshold-common-mode",
            "outcome": "discovery",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "session-clustered linear probability model",
            "role": "primary",
            "multiplicity_family": "threshold",
            "assumed_effect": 0.18,
        },
        {
            "hypothesis_id": "H16",
            "question": (
                "Do team-token recommendations improve threshold portfolio efficiency over "
                "common mode?"
            ),
            "treatment_cell": "T32-threshold-team-tokens",
            "control_cell": "T30-threshold-common-mode",
            "outcome": "threshold_portfolio_efficiency",
            "estimand": "ITT mean difference",
            "direction": "positive",
            "model": "blocked difference in means",
            "role": "primary",
            "multiplicity_family": "threshold",
            "assumed_effect": 0.14,
        },
        {
            "hypothesis_id": "H17",
            "question": "Does private following increase viable-team count over common mode?",
            "treatment_cell": "T31-threshold-private-following",
            "control_cell": "T30-threshold-common-mode",
            "outcome": "viable_team_count",
            "estimand": "ITT mean difference",
            "direction": "positive",
            "model": "session-clustered difference in means",
            "role": "secondary",
            "multiplicity_family": "threshold",
            "assumed_effect": 0.10,
        },
        {
            "hypothesis_id": "H18",
            "question": (
                "Does hidden history preserve discovery relative to visible action history?"
            ),
            "treatment_cell": "T33-dynamic-bayes-hidden-fixed",
            "control_cell": "T34-dynamic-bayes-visible-fixed",
            "outcome": "discovery",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "session-clustered linear probability model",
            "role": "primary",
            "multiplicity_family": "dynamic",
            "assumed_effect": 0.10,
        },
        {
            "hypothesis_id": "H19",
            "question": (
                "Does the registered stopping policy save actions relative to a fixed planner "
                "horizon?"
            ),
            "treatment_cell": "T36-dynamic-planner-hidden-stopping",
            "control_cell": "T35-dynamic-planner-hidden-fixed",
            "outcome": "action_savings",
            "estimand": "ITT mean difference",
            "direction": "positive",
            "model": "blocked difference in means",
            "role": "primary",
            "multiplicity_family": "dynamic",
            "assumed_effect": 0.20,
        },
        {
            "hypothesis_id": "H20",
            "question": (
                "Does hidden-history planner allocation improve discovery over hidden-history "
                "Bayes behavior?"
            ),
            "treatment_cell": "T35-dynamic-planner-hidden-fixed",
            "control_cell": "T33-dynamic-bayes-hidden-fixed",
            "outcome": "discovery",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "session-clustered linear probability model",
            "role": "secondary",
            "multiplicity_family": "dynamic",
            "assumed_effect": 0.16,
        },
    ]


def response_scenarios() -> list[dict[str, Any]]:
    return [
        *[dict(row) for row in v2.response_scenarios()],
        {
            "scenario_id": "S12-threshold-coordination",
            "label": "threshold-team coordination loss",
            "effect_multiplier": 0.65,
            "noise_multiplier": 1.15,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.05,
        },
        {
            "scenario_id": "S13-visibility-herding",
            "label": "visible-history herding response",
            "effect_multiplier": 0.70,
            "noise_multiplier": 1.18,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.05,
        },
        {
            "scenario_id": "S14-stopping-heterogeneity",
            "label": "heterogeneous stopping compliance",
            "effect_multiplier": 0.60,
            "noise_multiplier": 1.20,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.06,
        },
    ]


def program_v4_model_checks() -> list[dict[str, Any]]:
    """Frozen exact-source fixtures; none is a human treatment effect."""

    return [
        {
            "check_id": "E5-dd016-threshold",
            "claim_ids": ["DD-C-0071", "DD-C-0073"],
            "run_id": "20260722T021526Z_DD-016_00271ff8_123b2809e3",
            "expected": {
                "threshold_rows": 8,
                "common_deterministic_mode": "37916217637/98876953125",
                "paired_planner": "223779310319051/333709716796875",
            },
            "interpretation": "bounded exact threshold-allocation ground truth only",
        },
        {
            "check_id": "E6-dd015-dynamic",
            "claim_ids": ["DD-C-0079", "DD-C-0080", "DD-C-0081"],
            "run_id": "20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a",
            "expected": {
                "objective_rows": 64,
                "planner_strictly_better_rows": 38,
                "visibility_reduces_discovery_fixed_rows": 18,
                "stopping_reduces_expected_actions_rows": 32,
            },
            "interpretation": "bounded exact dynamic-attention ground truth only",
        },
        {
            "check_id": "E7-dd015-threshold-two",
            "claim_ids": ["DD-C-0082"],
            "run_id": "20260722T044453Z_DD-015_34bc4379_33e1da478b",
            "expected": {
                "parameter_cells": 16,
                "objective_rows": 32,
                "join_viable_team_rows": 32,
                "start_new_singleton_rows": 32,
            },
            "interpretation": "bounded exact dynamic threshold-two ground truth only",
        },
        {
            "check_id": "E8-dd018-mechanisms",
            "claim_ids": ["DD-C-0083", "DD-C-0084", "DD-C-0085", "DD-C-0086"],
            "run_id": "20260722T051847Z_DD-018_a193f602_3b3ddac173",
            "expected": {
                "mechanism_fixture_rows": 50,
                "planner_portfolio_rows": 40,
                "marginal_contribution_planner_stable_rows": 5,
                "universal_pooling_planner_rows": 0,
            },
            "interpretation": "bounded exact common-posterior mechanism ground truth only",
        },
    ]


def design_registry() -> dict[str, Any]:
    registry = v2.design_registry()
    alternatives = [
        {
            **row,
            "selected": False,
            "reason": (
                "preserved earlier-version candidate; does not cover all v3 contrasts"
                if row["selected"]
                else row["reason"]
            ),
        }
        for row in registry["alternatives"]
    ]
    alternatives.append(
        {
            "design_id": "threshold-dynamic-37",
            "cells": 37,
            "estimand_coverage": "all twenty frozen v3 contrasts and versioned anchors",
            "aliasing": "unregistered higher-order interactions remain aliased",
            "sample_at_32_per_cell": 1184,
            "selected": True,
            "reason": "bounded additive v3 design covering all registered contrasts",
        }
    )
    return {
        **registry,
        "schema_version": SCHEMA_VERSION,
        "factor_levels": PROGRAM_V4_FACTOR_LEVELS,
        "alternatives": alternatives,
        "treatment_cells": treatment_cells(),
        "outcomes": outcomes(),
        "hypotheses": hypotheses(),
        "response_scenarios": response_scenarios(),
        "reference_claims": [
            *registry["reference_claims"],
            "DD-C-0071",
            "DD-C-0073",
            "DD-C-0079",
            "DD-C-0080",
            "DD-C-0081",
            "DD-C-0082",
            "DD-C-0083",
            "DD-C-0084",
            "DD-C-0085",
            "DD-C-0086",
        ],
        "reference_runs": [
            *registry["reference_runs"],
            "20260722T021526Z_DD-016_00271ff8_123b2809e3",
            "20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a",
            "20260722T044453Z_DD-015_34bc4379_33e1da478b",
            "20260722T051847Z_DD-018_a193f602_3b3ddac173",
        ],
    }
