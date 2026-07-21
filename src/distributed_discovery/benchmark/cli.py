"""Read-only command surface for DiscoveryBench."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from distributed_discovery.benchmark.evaluator import (
    run_golden_suite,
    run_pair,
    run_simulated_suite,
)
from distributed_discovery.benchmark.model import metric_registry, protocol_registry, task_registry
from distributed_discovery.benchmark.verification import verify_certificate
from distributed_discovery.validation.bootstrap import repository_root


def configure(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="benchmark_command", required=True)
    commands.add_parser("list-tasks")
    describe_task = commands.add_parser("describe-task")
    describe_task.add_argument("task_id")
    commands.add_parser("list-protocols")
    describe_protocol = commands.add_parser("describe-protocol")
    describe_protocol.add_argument("protocol_id")
    commands.add_parser("list-metrics")
    run = commands.add_parser("run")
    run.add_argument("task_id")
    run.add_argument("protocol_id")
    commands.add_parser("run-golden")
    suite = commands.add_parser("run-suite")
    suite.add_argument("suite", choices=("golden", "simulated"))
    report = commands.add_parser("render-report")
    report.add_argument("certificate", nargs="?")
    verify = commands.add_parser("verify-run")
    verify.add_argument("run")


def _select(values: list[dict[str, object]], key: str, identifier: str) -> dict[str, object]:
    try:
        return next(value for value in values if value[key] == identifier)
    except StopIteration as error:
        raise SystemExit(f"unknown {key}: {identifier}") from error


def execute(args: argparse.Namespace) -> object:
    command = args.benchmark_command
    tasks = task_registry()
    if command == "list-tasks":
        return [{"task_id": task["task_id"], "task_family": task["task_family"]} for task in tasks]
    if command == "describe-task":
        return _select(tasks, "task_id", args.task_id)
    if command == "list-protocols":
        return [
            {"protocol_id": value["protocol_id"], "description": value["description"]}
            for value in protocol_registry()
        ]
    if command == "describe-protocol":
        return _select(protocol_registry(), "protocol_id", args.protocol_id)
    if command == "list-metrics":
        return metric_registry()
    if command == "run":
        task = _select(tasks, "task_id", args.task_id)
        return run_pair(task, args.protocol_id)
    if command in {"run-golden", "run-suite"} and (
        command == "run-golden" or args.suite == "golden"
    ):
        return run_golden_suite()
    if command == "run-suite":
        golden = run_golden_suite()
        if not golden["exact_reproduction_passed"]:
            raise RuntimeError("simulation cannot run before the golden suite passes")
        return run_simulated_suite([101, 211, 307, 401, 503, 601, 701, 809], 1000)
    if command == "verify-run":
        run = Path(args.run)
        if not run.is_absolute():
            run = repository_root() / run
        certificate = json.loads((run / "outputs/golden-certificate.json").read_text())
        return verify_certificate(certificate, repository_root())
    if command == "render-report":
        if args.certificate:
            certificate = json.loads(Path(args.certificate).read_text())
        else:
            certificate = run_golden_suite()
        return {
            "title": "DiscoveryBench report",
            "tasks": certificate["task_count"],
            "protocols": certificate["protocol_count"],
            "metrics": certificate["metric_count"],
            "compatible_pairs": certificate["compatible_pairs"],
            "aggregation": (
                "task vectors, family profiles, and scoped Pareto comparisons; no composite score"
            ),
        }
    raise RuntimeError(f"unhandled benchmark command: {command}")


def run_cli(argv: Sequence[str]) -> object:
    parser = argparse.ArgumentParser(prog="distributed-discovery benchmark")
    configure(parser)
    return execute(parser.parse_args(list(argv)))
