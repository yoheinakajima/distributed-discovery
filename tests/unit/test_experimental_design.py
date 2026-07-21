from __future__ import annotations

import copy

import pytest

from distributed_discovery.experimental_design.attention_model import (
    design_registry as attention_design_registry,
)
from distributed_discovery.experimental_design.attention_model import (
    hypotheses as attention_hypotheses,
)
from distributed_discovery.experimental_design.model import design_registry, hypotheses
from distributed_discovery.experimental_design.power import (
    generate_assignments,
    simulate_power_table,
)
from distributed_discovery.experimental_design.study import build_bundle
from distributed_discovery.experimental_design.verification import (
    corruption_tests,
    verify_bundle,
)
from distributed_discovery.validation.bootstrap import repository_root


def test_design_has_complete_registered_contrasts() -> None:
    design = design_registry()
    cells = {row["cell_id"] for row in design["treatment_cells"]}
    assert len(cells) == 20
    assert len(hypotheses()) == 8
    assert all(
        row["treatment_cell"] in cells and row["control_cell"] in cells for row in hypotheses()
    )
    assert design["no_human_data"] is True


def test_assignment_is_seeded_balanced_and_synthetic() -> None:
    first = generate_assignments(42, 8, 8)
    second = generate_assignments(42, 8, 8)
    assert first == second
    assert first["balance"]["passed"] is True
    assert first["balance"]["participants"] == 160
    assert all(row["participant_id"].startswith("SYN-P") for row in first["assignments"])


def test_power_is_seeded_and_reports_uncertainty() -> None:
    seeds = [101, 102, 103, 104, 105, 106, 107, 108]
    first = simulate_power_table(seeds, [200], 25, 8)
    second = simulate_power_table(seeds, [200], 25, 8)
    assert first == second
    assert len(first) == 64
    assert all(row["status"] == "synthetic-estimate" for row in first)
    assert all(
        float(row["power_ci_low"]) <= float(row["power"]) <= float(row["power_ci_high"])
        for row in first
    )


def test_separate_verifier_and_corruption_rejection() -> None:
    config = {
        "randomization_seed": 42,
        "participants_per_cell": 8,
        "session_size": 8,
        "scenario_seeds": [101, 102, 103, 104, 105, 106, 107, 108],
        "sample_sizes": [200],
        "replications": 10,
        "sample_seed": 99,
        "sample_rows": 20,
    }
    bundle = build_bundle(config)
    result = verify_bundle(bundle, repository_root())
    assert result["passed"] is True
    assert result["power_rows_verified"] == 64
    assert all(corruption_tests(bundle, repository_root()).values())


def test_schema_and_real_data_boundary_fail_closed() -> None:
    config = {
        "randomization_seed": 42,
        "participants_per_cell": 8,
        "session_size": 8,
        "scenario_seeds": [101, 102, 103, 104, 105, 106, 107, 108],
        "sample_sizes": [200],
        "replications": 2,
        "sample_seed": 99,
        "sample_rows": 5,
    }
    bundle = build_bundle(config)
    bad = copy.deepcopy(bundle)
    del bad["design"]["analysis_plan"]
    with pytest.raises(ValueError, match="design schema failed"):
        verify_bundle(bad, repository_root())
    leaked = copy.deepcopy(bundle)
    leaked["synthetic_sample"][0]["synthetic_only"] = False
    with pytest.raises(ValueError, match="non-synthetic"):
        verify_bundle(leaked, repository_root())


def test_attention_v2_extends_the_synthetic_design_and_verifies() -> None:
    design = attention_design_registry()
    assert len(design["treatment_cells"]) == 29
    assert len(design["hypotheses"]) == 14
    assert len(design["response_scenarios"]) == 11
    assert design["treatment_cells"][:20] != design_registry()["treatment_cells"]
    assert [row["cell_id"] for row in design["treatment_cells"][:20]] == [
        row["cell_id"] for row in design_registry()["treatment_cells"]
    ]
    assert {row["hypothesis_id"] for row in attention_hypotheses()[8:]} == {
        "H9",
        "H10",
        "H11",
        "H12",
        "H13",
        "H14",
    }
    config = {
        "randomization_seed": 52,
        "participants_per_cell": 8,
        "session_size": 8,
        "scenario_seeds": list(range(201, 212)),
        "sample_sizes": [200],
        "replications": 5,
        "sample_seed": 199,
        "sample_rows": 20,
    }
    bundle = build_bundle(config, "v2")
    assert verify_bundle(bundle, repository_root(), "v2")["power_rows_verified"] == 154
    assert all(corruption_tests(bundle, repository_root(), "v2").values())
