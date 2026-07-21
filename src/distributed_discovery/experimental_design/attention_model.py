"""Versioned selective-attention extension to the DD-011 synthetic design."""

from __future__ import annotations

from typing import Any

from distributed_discovery.experimental_design import model as v1

SCHEMA_VERSION = "dd011-experiment-v2"

ATTENTION_FACTOR_LEVELS: dict[str, tuple[str, ...]] = {
    **v1.FACTOR_LEVELS,
    "public_access": ("none", "all", "one_random", "selected_audience", "designated"),
    "public_precision": ("full", "reduced"),
    "attention_institution": ("none", "nonbinding_ignore", "license"),
    "policy_recommendation": ("none", "conditional", "contrarian_visible"),
}


def treatment_cells() -> list[dict[str, str]]:
    cells = [
        {
            **cell,
            "public_access": "none",
            "public_precision": "full",
            "attention_institution": "none",
            "policy_recommendation": "none",
        }
        for cell in v1.treatment_cells()
    ]
    baseline = dict(cells[0])

    def attention_cell(cell_id: str, **updates: str) -> dict[str, str]:
        return {**baseline, "cell_id": cell_id, **updates}

    cells += [
        attention_cell("T20-public-all", disclosure="public", public_access="all"),
        attention_cell("T21-random-reader", disclosure="public", public_access="one_random"),
        attention_cell(
            "T22-selected-audience", disclosure="public", public_access="selected_audience"
        ),
        attention_cell(
            "T23-reduced-precision",
            disclosure="public",
            public_access="all",
            public_precision="reduced",
        ),
        attention_cell("T24-designated-reader", disclosure="public", public_access="designated"),
        attention_cell(
            "T25-ignore-recommendation",
            disclosure="public",
            public_access="all",
            attention_institution="nonbinding_ignore",
        ),
        attention_cell(
            "T26-attention-license",
            disclosure="public_verifiable",
            public_access="all",
            attention_institution="license",
        ),
        attention_cell(
            "T27-off-signal-rescue",
            disclosure="public_verifiable",
            public_access="all",
            reward="sole_rescue",
            policy_recommendation="conditional",
        ),
        attention_cell(
            "T28-conditional-visible",
            disclosure="public",
            public_access="all",
            timing="sequential_visible",
            policy_recommendation="contrarian_visible",
        ),
    ]
    return cells


def outcomes() -> list[dict[str, str]]:
    return v1.outcomes() + [
        {
            "outcome_id": "public_signal_use",
            "role": "primary",
            "unit": "team proportion",
            "definition": "Actions using the public clue divided by all submitted actions.",
        },
        {
            "outcome_id": "one_reader_alignment",
            "role": "primary",
            "unit": "binary team outcome",
            "definition": "One when exactly one role conditions its action on the public clue.",
        },
        {
            "outcome_id": "off_signal_rescue",
            "role": "secondary",
            "unit": "binary team outcome",
            "definition": "One when discovery is made by an action differing from the public clue.",
        },
        {
            "outcome_id": "contrarian_action",
            "role": "secondary",
            "unit": "team proportion",
            "definition": "Actions choosing the registered third option on clue disagreement.",
        },
    ]


def hypotheses() -> list[dict[str, Any]]:
    return v1.hypotheses() + [
        {
            "hypothesis_id": "H9",
            "question": "Does broadcast induce more public-signal use than one-reader access?",
            "treatment_cell": "T20-public-all",
            "control_cell": "T21-random-reader",
            "outcome": "public_signal_use",
            "estimand": "ITT mean difference",
            "direction": "positive",
            "model": "session-clustered difference in means",
            "role": "primary",
            "multiplicity_family": "attention",
            "assumed_effect": 0.22,
        },
        {
            "hypothesis_id": "H10",
            "question": "Does single-reader access improve discovery relative to full broadcast?",
            "treatment_cell": "T21-random-reader",
            "control_cell": "T20-public-all",
            "outcome": "discovery",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "session-clustered linear probability model",
            "role": "primary",
            "multiplicity_family": "attention",
            "assumed_effect": 0.12,
        },
        {
            "hypothesis_id": "H11",
            "question": "Does an attention license outperform a nonbinding ignore recommendation?",
            "treatment_cell": "T26-attention-license",
            "control_cell": "T25-ignore-recommendation",
            "outcome": "one_reader_alignment",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "blocked linear probability model",
            "role": "primary",
            "multiplicity_family": "implementation",
            "assumed_effect": 0.18,
        },
        {
            "hypothesis_id": "H12",
            "question": "Does a designated reader implement one-reader allocation over broadcast?",
            "treatment_cell": "T24-designated-reader",
            "control_cell": "T20-public-all",
            "outcome": "one_reader_alignment",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "blocked linear probability model",
            "role": "primary",
            "multiplicity_family": "implementation",
            "assumed_effect": 0.24,
        },
        {
            "hypothesis_id": "H13",
            "question": "Do conditional recommendations improve discovery over broadcast?",
            "treatment_cell": "T27-off-signal-rescue",
            "control_cell": "T20-public-all",
            "outcome": "discovery",
            "estimand": "ITT risk difference",
            "direction": "positive",
            "model": "session-clustered linear probability model",
            "role": "secondary",
            "multiplicity_family": "attention",
            "assumed_effect": 0.08,
        },
        {
            "hypothesis_id": "H14",
            "question": "Does action visibility induce the registered contrarian response?",
            "treatment_cell": "T28-conditional-visible",
            "control_cell": "T25-ignore-recommendation",
            "outcome": "contrarian_action",
            "estimand": "ITT mean difference",
            "direction": "positive",
            "model": "session-clustered difference in means",
            "role": "secondary",
            "multiplicity_family": "attention",
            "assumed_effect": 0.07,
        },
    ]


def response_scenarios() -> list[dict[str, Any]]:
    scenarios = [dict(row) for row in v1.response_scenarios()]
    scenarios[0]["label"] = "rational attention equilibrium"
    scenarios[1]["label"] = "noisy best response"
    scenarios[3]["label"] = "social preference heterogeneity"
    scenarios[4]["label"] = "partial compliance"
    scenarios += [
        {
            "scenario_id": "S9-salience",
            "label": "heterogeneous public-clue salience",
            "effect_multiplier": 0.72,
            "noise_multiplier": 1.18,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.05,
        },
        {
            "scenario_id": "S10-memory-leakage",
            "label": "memory leakage across attention modes",
            "effect_multiplier": 0.55,
            "noise_multiplier": 1.22,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.06,
        },
        {
            "scenario_id": "S11-role-aversion",
            "label": "designated-role aversion",
            "effect_multiplier": 0.58,
            "noise_multiplier": 1.20,
            "attrition_rate": 0.0,
            "intracluster_correlation": 0.05,
        },
    ]
    return scenarios


def design_registry() -> dict[str, Any]:
    registry = v1.design_registry()
    return {
        **registry,
        "schema_version": SCHEMA_VERSION,
        "factor_levels": ATTENTION_FACTOR_LEVELS,
        "treatment_cells": treatment_cells(),
        "outcomes": outcomes(),
        "hypotheses": hypotheses(),
        "response_scenarios": response_scenarios(),
        "reference_claims": [
            *registry["reference_claims"],
            "DD-C-0059",
            "DD-C-0060",
            "DD-C-0062",
            "DD-C-0064",
            "DD-C-0066",
            "DD-C-0067",
        ],
        "reference_runs": [
            *registry["reference_runs"],
            "20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b",
            "20260721T215811Z_DD-013_09c07448_cdac4fb512",
            "20260721T222047Z_DD-014_f5f099a8_ea0276dd16",
        ],
    }
