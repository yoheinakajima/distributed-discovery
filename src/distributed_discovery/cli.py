"""Command-line entry point."""

from __future__ import annotations

import argparse

from distributed_discovery.validation.bootstrap import validate_repository
from distributed_discovery.validation.claims import validate_ledger


def main() -> None:
    parser = argparse.ArgumentParser(prog="distributed-discovery")
    parser.add_argument("command", choices=("bootstrap", "validate-claims"))
    args = parser.parse_args()
    if args.command == "bootstrap":
        validate_repository()
    else:
        validate_ledger()


if __name__ == "__main__":
    main()
