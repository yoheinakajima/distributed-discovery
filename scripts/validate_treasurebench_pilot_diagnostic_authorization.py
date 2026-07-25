#!/usr/bin/env python3
"""Validate the exact read-only pilot diagnostic authorization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.pilot_diagnostic import (
    authorization_path,
    diagnostic_tree_hash,
    load_diagnostic_authorization,
    validate_phase_a_documents,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--print-tree-hash", action="store_true")
    parser.add_argument("--validate-phase-a", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.print_tree_hash:
        print(diagnostic_tree_hash(repo))
        return
    if args.validate_phase_a:
        print(json.dumps(validate_phase_a_documents(repo), sort_keys=True))
        return
    value = load_diagnostic_authorization(repo, args.authorization or authorization_path())
    print(
        json.dumps(
            {
                "status": "authorized-read-only",
                "authorization_id": value["authorization_id"],
                "issue": value["issue"],
                "branch": value["branch"],
                "diagnostic_commit": value["diagnostic_commit"],
                "provider_calls": 0,
                "private_state_read": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
