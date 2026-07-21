"""Versioned DD-011 design, outcome, hypothesis, and scenario registries."""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "dd011-experiment-v1"
NO_HUMAN_DATA_NOTICE = (
    "No participants were recruited. No human data were collected. No experiment was "
    "conducted. Separate ethics and institutional review are required before deployment."
)

FACTOR_LEVELS: dict[str, tuple[str, ...]] = {
    "acquisition": ("free_common", "costly_independent", "assigned_independent"),
    "attribution": ("absent", "protected"),
    "disclosure": ("private", "public", "public_verifiable"),
    "timing": ("simultaneous_hidden", "sequential_visible"),
    "reward": (
        "equal_split",
        "universal_pooling",
        "sole_rescue",
        "marginal_coverage",
        "dd006b_joint",
    ),
}

_BASELINE = {
    "acquisition": "free_common",
    "attribution": "absent",
    "disclosure": "private",
    "timing": "simultaneous_hidden",
    "reward": "equal_split",
}


def _cell(cell_id: str, **updates: str) -> dict[str, str]:
    cell = {"cell_id": cell_id, **_BASELINE, **updates}
    return cell


def treatment_cells() -> list[dict[str, str]]:
    """Return the frozen 20-cell estimand-covering fractional design."""

    return [
        _cell("T00-baseline"),
        _cell("T01-costly", acquisition="costly_independent"),
        _cell("T02-assigned", acquisition="assigned_independent"),
        _cell("T03-attribution", attribution="protected"),
        _cell("T04-public", disclosure="public"),
        _cell("T05-verifiable", disclosure="public_verifiable"),
        _cell("T06-visible", timing="sequential_visible"),
        _cell("T07-pooling", reward="universal_pooling"),
        _cell("T08-rescue", reward="sole_rescue"),
        _cell("T09-coverage", reward="marginal_coverage"),
        _cell("T10-joint", reward="dd006b_joint"),
        _cell(
            "T11-assigned-attribution",
            acquisition="assigned_independent",
            attribution="protected",
        ),
        _cell(
            "T12-verifiable-visible",
            disclosure="public_verifiable",
            timing="sequential_visible",
        ),
        _cell(
            "T13-costly-coverage",
            acquisition="costly_independent",
            reward="marginal_coverage",
        ),
        _cell(
            "T14-assigned-coverage",
            acquisition="assigned_independent",
            reward="marginal_coverage",
        ),
        _cell("T15-public-pooling", disclosure="public", reward="universal_pooling"),
        _cell(
            "T16-verifiable-joint",
            attribution="protected",
            disclosure="public_verifiable",
            reward="dd006b_joint",
        ),
        _cell(
            "T17-assigned-joint",
            acquisition="assigned_independent",
            attribution="protected",
            disclosure="public_verifiable",
            reward="dd006b_joint",
        ),
        _cell(
            "T18-costly-attribution",
            acquisition="costly_independent",
            attribution="protected",
        ),
        _cell(
            "T19-visible-coverage",
            timing="sequential_visible",
            reward="marginal_coverage",
        ),
    ]


def outcomes() -> list[dict[str, str]]:
    return [
        {
            "outcome_id": "independent_source_acquisition",
            "role": "primary",
            "unit": "binary",
            "definition": (
                "One if the assigned source choice is an independent channel before evidence "
                "is observed."
            ),
        },
        {
            "outcome_id": "truthful_report",
            "role": "primary",
            "unit": "binary",
            "definition": (
                "One if the submitted report equals the participant's observed synthetic signal."
            ),
        },
        {
            "outcome_id": "action_obedience",
            "role": "primary",
            "unit": "binary",
            "definition": "One if the action equals the treatment-specific recommendation.",
        },
        {
            "outcome_id": "distinct_informed_actions",
            "role": "primary",
            "unit": "team proportion",
            "definition": "Distinct evidence-supported actions divided by the team action budget.",
        },
        {
            "outcome_id": "discovery",
            "role": "primary",
            "unit": "binary team outcome",
            "definition": "One if at least one team action covers the realized synthetic target.",
        },
        {
            "outcome_id": "social_net_value",
            "role": "primary",
            "unit": "expected payoff",
            "definition": "Team discovery value minus declared source and mechanism costs.",
        },
        {
            "outcome_id": "communication_volume",
            "role": "secondary",
            "unit": "message count",
            "definition": "Number of submitted treatment-permitted messages.",
        },
        {
            "outcome_id": "disclosure_precision",
            "role": "secondary",
            "unit": "proportion",
            "definition": "Truthful disclosed reports divided by all disclosed reports.",
        },
        {
            "outcome_id": "action_concentration",
            "role": "secondary",
            "unit": "Herfindahl index",
            "definition": "Sum of squared action shares within a team-round.",
        },
        {
            "outcome_id": "source_concentration",
            "role": "secondary",
            "unit": "Herfindahl index",
            "definition": "Sum of squared source-choice shares within a team-round.",
        },
        {
            "outcome_id": "response_time",
            "role": "secondary",
            "unit": "seconds",
            "definition": "Elapsed synthetic decision time from screen display to submission.",
        },
        {
            "outcome_id": "confidence",
            "role": "secondary",
            "unit": "0-100 scale",
            "definition": "Pre-specified confidence response submitted before outcome feedback.",
        },
        {
            "outcome_id": "individual_payoff",
            "role": "secondary",
            "unit": "experimental points",
            "definition": "Declared base reward plus transfer minus evidence cost.",
        },
        {
            "outcome_id": "transfer_budget",
            "role": "secondary",
            "unit": "experimental points",
            "definition": "Total externally financed transfer in a team-round.",
        },
        {
            "outcome_id": "equilibrium_consistent_behavior",
            "role": "secondary",
            "unit": "binary",
            "definition": (
                "One if behavior lies in the treatment's frozen exact-model response set."
            ),
        },
    ]


def hypotheses() -> list[dict[str, Any]]:
    """Return hypotheses frozen before any synthetic power result exists."""

    return [
        {
            "hypothesis_id": "H1",
            "question": "Do participants under-acquire costly independent evidence?",
            "treatment_cell": "T02-assigned",
            "control_cell": "T01-costly",
            "outcome": "independent_source_acquisition",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "blocked linear probability model",
            "role": "primary",
            "multiplicity_family": "acquisition",
            "assumed_effect": 0.20,
        },
        {
            "hypothesis_id": "H2",
            "question": "Does attribution protection increase truthful disclosure?",
            "treatment_cell": "T03-attribution",
            "control_cell": "T00-baseline",
            "outcome": "truthful_report",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "blocked linear probability model",
            "role": "primary",
            "multiplicity_family": "information",
            "assumed_effect": 0.12,
        },
        {
            "hypothesis_id": "H3",
            "question": "Does public action visibility increase action diversity?",
            "treatment_cell": "T06-visible",
            "control_cell": "T00-baseline",
            "outcome": "distinct_informed_actions",
            "estimand": "ITT mean difference",
            "direction": "positive",
            "model": "cluster-robust difference in means",
            "role": "primary",
            "multiplicity_family": "allocation",
            "assumed_effect": 0.10,
        },
        {
            "hypothesis_id": "H4",
            "question": "Does allocation repair outperform disclosure alone?",
            "treatment_cell": "T19-visible-coverage",
            "control_cell": "T15-public-pooling",
            "outcome": "discovery",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "cluster-robust linear probability model",
            "role": "primary",
            "multiplicity_family": "allocation",
            "assumed_effect": 0.14,
        },
        {
            "hypothesis_id": "H5",
            "question": (
                "Does marginal-coverage reward improve discovery more than universal pooling?"
            ),
            "treatment_cell": "T09-coverage",
            "control_cell": "T07-pooling",
            "outcome": "discovery",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "cluster-robust linear probability model",
            "role": "primary",
            "multiplicity_family": "allocation",
            "assumed_effect": 0.15,
        },
        {
            "hypothesis_id": "H6",
            "question": "Does the DD-006B mechanism improve joint truth and obedience?",
            "treatment_cell": "T16-verifiable-joint",
            "control_cell": "T05-verifiable",
            "outcome": "action_obedience",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "blocked linear probability model",
            "role": "primary",
            "multiplicity_family": "information",
            "assumed_effect": 0.18,
        },
        {
            "hypothesis_id": "H7",
            "question": "Does verifiable provenance improve disclosure precision?",
            "treatment_cell": "T05-verifiable",
            "control_cell": "T04-public",
            "outcome": "disclosure_precision",
            "estimand": "ITT mean difference",
            "direction": "positive",
            "model": "blocked difference in means",
            "role": "secondary",
            "multiplicity_family": "information",
            "assumed_effect": 0.10,
        },
        {
            "hypothesis_id": "H8",
            "question": "Are acquisition assignment and allocation repair complementary?",
            "treatment_cell": "T14-assigned-coverage",
            "control_cell": "T13-costly-coverage",
            "outcome": "social_net_value",
            "estimand": "pre-specified difference-in-differences interaction",
            "direction": "positive",
            "model": "factorial interaction with block fixed effects",
            "role": "secondary",
            "multiplicity_family": "acquisition",
            "assumed_effect": 0.08,
        },
    ]


def response_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "scenario_id": "S1-rational",
            "label": "full rational best response",
            "effect_multiplier": 1.0,
            "noise_multiplier": 0.85,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.0,
        },
        {
            "scenario_id": "S2-quantal",
            "label": "quantal/noisy best response",
            "effect_multiplier": 0.80,
            "noise_multiplier": 1.15,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.02,
        },
        {
            "scenario_id": "S3-costs",
            "label": "heterogeneous source costs",
            "effect_multiplier": 0.70,
            "noise_multiplier": 1.10,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.04,
        },
        {
            "scenario_id": "S4-social",
            "label": "heterogeneous social preferences",
            "effect_multiplier": 0.75,
            "noise_multiplier": 1.20,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.05,
        },
        {
            "scenario_id": "S5-compliance",
            "label": "partial mechanism compliance",
            "effect_multiplier": 0.60,
            "noise_multiplier": 1.15,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.03,
        },
        {
            "scenario_id": "S6-report-error",
            "label": "report error",
            "effect_multiplier": 0.65,
            "noise_multiplier": 1.20,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.03,
        },
        {
            "scenario_id": "S7-attrition",
            "label": "attrition",
            "effect_multiplier": 0.80,
            "noise_multiplier": 1.10,
            "attrition_rate": 0.15,
            "intracluster_correlation": 0.04,
        },
        {
            "scenario_id": "S8-learning",
            "label": "learning over rounds",
            "effect_multiplier": 0.90,
            "noise_multiplier": 1.05,
            "attrition_rate": 0.05,
            "intracluster_correlation": 0.08,
        },
    ]


def design_alternatives() -> list[dict[str, Any]]:
    return [
        {
            "design_id": "full-180",
            "cells": 180,
            "estimand_coverage": "complete main effects and interactions",
            "aliasing": "none",
            "sample_at_32_per_cell": 5760,
            "selected": False,
            "reason": "infeasible sample and operational burden",
        },
        {
            "design_id": "orthogonal-16",
            "cells": 16,
            "estimand_coverage": "main effects plus selected interactions",
            "aliasing": "H7 and H8 contrasts partially aliased",
            "sample_at_32_per_cell": 512,
            "selected": False,
            "reason": "fails complete coverage of the eight frozen estimands",
        },
        {
            "design_id": "contrast-complete-20",
            "cells": 20,
            "estimand_coverage": "all eight frozen contrasts plus mechanism and disclosure anchors",
            "aliasing": "unregistered higher-order interactions remain aliased",
            "sample_at_32_per_cell": 640,
            "selected": True,
            "reason": "smallest audited candidate with complete registered-estimand coverage",
        },
        {
            "design_id": "expanded-24",
            "cells": 24,
            "estimand_coverage": "all frozen contrasts plus four robustness anchors",
            "aliasing": "lower than selected design",
            "sample_at_32_per_cell": 768,
            "selected": False,
            "reason": "no primary-estimand gain over the selected 20-cell design",
        },
    ]


def analysis_plan() -> dict[str, Any]:
    return {
        "estimand": "intent-to-treat",
        "per_protocol": "secondary among synthetically compliant records only",
        "primary_specification": (
            "outcome on treatment indicator and randomization-block fixed effects"
        ),
        "cluster": "session",
        "repeated_rounds": "participant-averaged outcomes, session-clustered inference",
        "missing_data": (
            "retain assignment; missing outcomes remain missing; inverse-probability "
            "sensitivity only"
        ),
        "exclusions": [
            "duplicate synthetic ID",
            "assignment outside manifest",
            "pre-treatment simulator failure",
        ],
        "manipulation_checks": ["source choice", "screen visibility", "reward comprehension"],
        "heterogeneity": ["pre-treatment cost stratum", "round half"],
        "multiplicity": (
            "Holm within each frozen family; power uses conservative Bonferroni family alpha"
        ),
        "stopping_rule": "fixed registered sample; no outcome-dependent stopping",
        "robustness": [
            "cluster ICC sensitivity",
            "attrition sensitivity",
            "noise sensitivity",
            "per-protocol secondary",
        ],
        "post_treatment_controls": "none in the primary specification",
    }


def design_registry() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "study_id": "DD-011",
        "public_status": "synthetic-preregistration-ready-not-preregistered",
        "no_human_data": True,
        "notice": NO_HUMAN_DATA_NOTICE,
        "factor_levels": FACTOR_LEVELS,
        "alternatives": design_alternatives(),
        "treatment_cells": treatment_cells(),
        "outcomes": outcomes(),
        "hypotheses": hypotheses(),
        "response_scenarios": response_scenarios(),
        "analysis_plan": analysis_plan(),
        "reference_claims": ["DD-C-0051", "DD-C-0052", "DD-C-0053", "DD-C-0054"],
        "reference_runs": [
            "20260721T141527Z_DD-008_0d11dc77_7e0c8f1d66",
            "20260721T163030Z_DD-008A_8b70668b_06307caab4",
            "20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b",
            "20260721T171249Z_DD-009_bc78d249_0c3851c41a",
        ],
    }
