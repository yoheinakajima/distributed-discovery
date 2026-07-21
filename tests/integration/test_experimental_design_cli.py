from __future__ import annotations

import json
import os
import subprocess


def test_experiment_cli_lists_design_and_runs_bounded_power() -> None:
    environment = {**os.environ, "PYTHONPATH": "src"}
    design = subprocess.run(
        ["python", "-m", "distributed_discovery.cli", "experiment", "design"],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    payload = json.loads(design.stdout)
    assert payload["schema_version"] == "dd011-experiment-v1"
    assert len(payload["treatment_cells"]) == 20
    power = subprocess.run(
        [
            "python",
            "-m",
            "distributed_discovery.cli",
            "experiment",
            "power",
            "--replications",
            "2",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    rows = json.loads(power.stdout)
    assert len(rows) == 64
    assert all(row["sample_size"] == 640 for row in rows)

    attention = subprocess.run(
        [
            "python",
            "-m",
            "distributed_discovery.cli",
            "experiment",
            "--version",
            "v2",
            "design",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    attention_payload = json.loads(attention.stdout)
    assert attention_payload["schema_version"] == "dd011-experiment-v2"
    assert len(attention_payload["treatment_cells"]) == 29
    assert len(attention_payload["hypotheses"]) == 14
