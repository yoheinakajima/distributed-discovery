"""Deterministic synthetic assignment and conditional power calculations."""

from __future__ import annotations

import hashlib
import math
import random
from collections import Counter
from statistics import NormalDist
from typing import Any

from distributed_discovery.experimental_design.model import (
    hypotheses,
    response_scenarios,
    treatment_cells,
)


def _derived_seed(base_seed: int, *parts: str) -> int:
    material = "|".join((str(base_seed), *parts)).encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def generate_assignments(
    seed: int,
    participants_per_cell: int,
    session_size: int,
    blocks: tuple[str, ...] = ("B1", "B2", "B3", "B4"),
    cells_registry: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Generate concealed, blocked assignments for synthetic identifiers only."""

    cells = [cell["cell_id"] for cell in (cells_registry or treatment_cells())]
    if participants_per_cell % len(blocks) or participants_per_cell % session_size:
        raise ValueError("participants_per_cell must divide evenly across blocks and sessions")
    slots: list[tuple[str, str]] = []
    per_block = participants_per_cell // len(blocks)
    for block in blocks:
        for cell_id in cells:
            slots.extend((block, cell_id) for _ in range(per_block))
    rng = random.Random(seed)
    rng.shuffle(slots)
    records: list[dict[str, Any]] = []
    for index, (block, cell_id) in enumerate(slots, start=1):
        session_index = (index - 1) // session_size + 1
        records.append(
            {
                "participant_id": f"SYN-P{index:04d}",
                "session_id": f"SYN-S{session_index:03d}",
                "block": block,
                "cell_id": cell_id,
                "assignment_order": index,
            }
        )
    cell_counts = Counter(str(record["cell_id"]) for record in records)
    block_counts = Counter((str(record["block"]), str(record["cell_id"])) for record in records)
    return {
        "seed": seed,
        "participant_prefix": "SYN-P",
        "session_prefix": "SYN-S",
        "allocation_concealment": (
            "Generate the signed manifest before any outcome; release only the next opaque "
            "synthetic assignment after the identifier is enrolled."
        ),
        "assignments": records,
        "balance": {
            "participants": len(records),
            "sessions": len(records) // session_size,
            "cell_count_min": min(cell_counts.values()),
            "cell_count_max": max(cell_counts.values()),
            "block_cell_count_min": min(block_counts.values()),
            "block_cell_count_max": max(block_counts.values()),
            "passed": len(set(cell_counts.values())) == 1 and len(set(block_counts.values())) == 1,
        },
    }


def _family_sizes(hypothesis_rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(row["multiplicity_family"]) for row in hypothesis_rows)


def _standard_error(
    effect: float,
    sample_size: int,
    scenario: dict[str, Any],
    cluster_size: int,
) -> float:
    retained = sample_size * (1.0 - float(scenario["attrition_rate"]))
    if retained <= 1:
        raise ValueError("retained sample must exceed one")
    baseline = 0.50
    treated = max(0.01, min(0.99, baseline + effect))
    per_arm = retained / 2.0
    independent_variance = (
        baseline * (1.0 - baseline) / per_arm + treated * (1.0 - treated) / per_arm
    )
    design_effect = 1.0 + (cluster_size - 1) * float(scenario["intracluster_correlation"])
    return math.sqrt(independent_variance * design_effect) * float(scenario["noise_multiplier"])


def _wilson(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    phat = successes / trials
    denom = 1.0 + z * z / trials
    centre = (phat + z * z / (2.0 * trials)) / denom
    radius = z * math.sqrt(phat * (1.0 - phat) / trials + z * z / (4 * trials**2)) / denom
    return centre - radius, centre + radius


def simulate_power_table(
    scenario_seeds: list[int],
    sample_sizes: list[int],
    replications: int,
    cluster_size: int,
    hypothesis_rows: list[dict[str, Any]] | None = None,
    scenario_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Simulate one-sided conditional power for every frozen hypothesis/scenario/sample."""

    scenarios = scenario_rows or response_scenarios()
    registered_hypotheses = hypothesis_rows or hypotheses()
    if len(scenario_seeds) != len(scenarios):
        raise ValueError("one explicit seed is required per response scenario")
    family_sizes = _family_sizes(registered_hypotheses)
    table: list[dict[str, Any]] = []
    for scenario, base_seed in zip(scenarios, scenario_seeds, strict=True):
        for hypothesis in registered_hypotheses:
            family = str(hypothesis["multiplicity_family"])
            alpha = 0.05 / family_sizes[family]
            critical = NormalDist().inv_cdf(1.0 - alpha)
            effect = float(hypothesis["assumed_effect"]) * float(scenario["effect_multiplier"])
            for sample_size in sample_sizes:
                se = _standard_error(effect, sample_size, scenario, cluster_size)
                row_seed = _derived_seed(
                    base_seed,
                    str(hypothesis["hypothesis_id"]),
                    str(sample_size),
                )
                rng = random.Random(row_seed)
                rejections = 0
                for _ in range(replications):
                    estimate = rng.gauss(effect, se)
                    if estimate / se > critical:
                        rejections += 1
                lower, upper = _wilson(rejections, replications)
                mde = critical * se
                table.append(
                    {
                        "scenario_id": scenario["scenario_id"],
                        "hypothesis_id": hypothesis["hypothesis_id"],
                        "outcome": hypothesis["outcome"],
                        "sample_size": sample_size,
                        "replications": replications,
                        "row_seed": row_seed,
                        "assumed_effect": f"{effect:.6f}",
                        "standard_error": f"{se:.6f}",
                        "multiplicity_alpha": f"{alpha:.6f}",
                        "rejections": rejections,
                        "power": f"{rejections / replications:.6f}",
                        "power_ci_low": f"{lower:.6f}",
                        "power_ci_high": f"{upper:.6f}",
                        "minimum_detectable_effect": f"{mde:.6f}",
                        "status": "synthetic-estimate",
                    }
                )
    return table


def calibration_report(power_table: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [row for row in power_table if int(row["sample_size"]) >= 640]
    failures = [
        {
            "scenario_id": row["scenario_id"],
            "hypothesis_id": row["hypothesis_id"],
            "sample_size": row["sample_size"],
            "power": row["power"],
            "threshold": "0.800000",
        }
        for row in rows
        if float(row["power"]) < 0.80
    ]
    return {
        "criterion": "power >= 0.80 at registered sample sizes of 640 or more",
        "evaluated_rows": len(rows),
        "failures": failures,
        "failure_count": len(failures),
        "retained": True,
    }


def exact_model_checks() -> list[dict[str, Any]]:
    """Frozen project-model limiting cells; these are not human treatment effects."""

    return [
        {
            "check_id": "E1-dd008-trap",
            "claim_id": "DD-C-0051",
            "run_id": "20260721T141527Z_DD-008_0d11dc77_7e0c8f1d66",
            "inputs": {"p": "2/3", "cost": "1/8", "agents": 2},
            "expected": {
                "common_social_value": "2/3",
                "one_independent_net_value": "55/72",
                "planner_gap": "7/72",
                "common_profile_is_equilibrium": True,
            },
            "interpretation": "exact synthetic source-choice ground truth only",
        },
        {
            "check_id": "E2-dd008a-census",
            "claim_id": "DD-C-0052",
            "run_id": "20260721T163030Z_DD-008A_8b70668b_06307caab4",
            "expected": {
                "grid_cells": 126,
                "agent_min": 2,
                "agent_max": 8,
                "direct_agreement": True,
            },
            "interpretation": "bounded exact N=2 through 8 accounting only",
        },
        {
            "check_id": "E3-dd006b-mechanism",
            "claim_id": "DD-C-0053",
            "run_id": "20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b",
            "expected": {
                "strict_rows": 16,
                "maximum_margin": "13/72",
                "truthful_discovery": "11/12",
            },
            "interpretation": "exact registered mechanism fixture only",
        },
        {
            "check_id": "E4-dd009-atlas",
            "claim_id": "DD-C-0054",
            "run_id": "20260721T171249Z_DD-009_bc78d249_0c3851c41a",
            "expected": {"valid_cells": 20, "nondominated_cells": 12, "maximum_discovery": "11/12"},
            "interpretation": "bounded exact Architecture Atlas only",
        },
    ]


def synthetic_sample(
    assignments: dict[str, Any], seed: int, count: int = 120
) -> list[dict[str, Any]]:
    """Create a small plainly synthetic data dictionary example."""

    rng = random.Random(seed)
    sample: list[dict[str, Any]] = []
    for assignment in assignments["assignments"][:count]:
        acquired = int(rng.random() < 0.58)
        truthful = int(
            rng.random()
            < (
                0.72
                + 0.08
                * (
                    assignment["cell_id"]
                    in {"T03-attribution", "T05-verifiable", "T16-verifiable-joint"}
                )
            )
        )
        obeyed = int(rng.random() < (0.68 + 0.12 * str(assignment["cell_id"]).endswith("joint")))
        sample.append(
            {
                **assignment,
                "round": 1,
                "independent_source_acquisition": acquired,
                "truthful_report": truthful,
                "action_obedience": obeyed,
                "synthetic_only": True,
            }
        )
    return sample
