"""Command-line entry point."""

from __future__ import annotations

import argparse
import json

from distributed_discovery.benchmark.cli import configure as configure_benchmark
from distributed_discovery.benchmark.cli import execute as execute_benchmark
from distributed_discovery.validation.bootstrap import validate_repository
from distributed_discovery.validation.claims import validate_ledger


def main() -> None:
    parser = argparse.ArgumentParser(prog="distributed-discovery")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("bootstrap")
    commands.add_parser("validate-claims")
    configure_benchmark(commands.add_parser("benchmark"))
    args = parser.parse_args()
    if args.command == "bootstrap":
        validate_repository()
    elif args.command == "validate-claims":
        validate_ledger()
    else:
        print(json.dumps(execute_benchmark(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
