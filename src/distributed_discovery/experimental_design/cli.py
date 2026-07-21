"""CLI for inspecting and verifying the DD-011 synthetic experiment kit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from distributed_discovery.experimental_design.model import design_registry, hypotheses
from distributed_discovery.experimental_design.power import (
    generate_assignments,
    simulate_power_table,
)
from distributed_discovery.experimental_design.verification import verify_bundle
from distributed_discovery.validation.bootstrap import repository_root


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--version", choices=("v1", "v2"), default="v1")
    commands = parser.add_subparsers(dest="experiment_command", required=True)
    commands.add_parser("design")
    commands.add_parser("hypotheses")
    assign = commands.add_parser("assign")
    assign.add_argument("--seed", type=int, default=110011)
    assign.add_argument("--participants-per-cell", type=int, default=32)
    power = commands.add_parser("power")
    power.add_argument("--replications", type=int, default=100)
    verify = commands.add_parser("verify")
    verify.add_argument("run_id")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def execute(args: argparse.Namespace) -> object:
    if args.version == "v1":
        registry = design_registry()
        hypothesis_rows = hypotheses()
    else:
        from distributed_discovery.experimental_design.attention_model import (
            design_registry as attention_registry,
        )
        from distributed_discovery.experimental_design.attention_model import (
            hypotheses as attention_hypotheses,
        )

        registry = attention_registry()
        hypothesis_rows = attention_hypotheses()
    if args.experiment_command == "design":
        return registry
    if args.experiment_command == "hypotheses":
        return hypothesis_rows
    if args.experiment_command == "assign":
        return generate_assignments(
            args.seed, args.participants_per_cell, 8, cells_registry=registry["treatment_cells"]
        )
    if args.experiment_command == "power":
        scenario_rows = registry["response_scenarios"]
        return simulate_power_table(
            [110101 + index for index in range(len(scenario_rows))],
            [640],
            args.replications,
            8,
            hypothesis_rows=hypothesis_rows,
            scenario_rows=scenario_rows,
        )
    root = repository_root()
    outputs = root / "results/verified" / args.run_id / "outputs"
    bundle = {
        "design": _load(outputs / "design-registry.json"),
        "randomization": _load(outputs / "randomization-manifest.json"),
        "power_table": _load(outputs / "power-table.json"),
        "calibration": _load(outputs / "calibration-report.json"),
        "exact_model_checks": _load(outputs / "exact-model-checks.json"),
        "synthetic_sample": _load(outputs / "synthetic-sample.json"),
    }
    return verify_bundle(bundle, root, args.version)
