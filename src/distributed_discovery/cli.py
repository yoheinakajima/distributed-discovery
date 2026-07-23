"""Command-line entry point."""

from __future__ import annotations

import argparse
import json

from distributed_discovery.benchmark.agents_v1.cli import configure as configure_agents
from distributed_discovery.benchmark.agents_v1.cli import execute as execute_agents
from distributed_discovery.benchmark.cli import configure as configure_benchmark
from distributed_discovery.benchmark.cli import execute as execute_benchmark
from distributed_discovery.experimental_design.cli import configure as configure_experiment
from distributed_discovery.experimental_design.cli import execute as execute_experiment
from distributed_discovery.validation.bootstrap import validate_repository
from distributed_discovery.validation.claims import validate_ledger


def main() -> None:
    parser = argparse.ArgumentParser(prog="distributed-discovery")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("bootstrap")
    commands.add_parser("validate-claims")
    configure_benchmark(commands.add_parser("benchmark"))
    configure_agents(commands.add_parser("agents-v1"))
    configure_experiment(commands.add_parser("experiment"))
    args = parser.parse_args()
    if args.command == "bootstrap":
        validate_repository()
    elif args.command == "validate-claims":
        validate_ledger()
    elif args.command == "benchmark":
        print(json.dumps(execute_benchmark(args), indent=2, sort_keys=True))
    elif args.command == "agents-v1":
        print(json.dumps(execute_agents(args), indent=2, sort_keys=True))
    else:
        print(json.dumps(execute_experiment(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
