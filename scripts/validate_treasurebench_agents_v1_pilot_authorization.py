#!/usr/bin/env python3
"""Validate the exact local owner authorization without reading credentials."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.pilot import (
    authorization_path,
    execution_tree_hash,
    load_pilot_authorization,
    load_request,
    pilot_offline_readiness,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--print-tree-hash", action="store_true")
    parser.add_argument("--offline-readiness", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.print_tree_hash:
        print(execution_tree_hash(repo, load_request(repo)))
        return
    if args.offline_readiness:
        print(json.dumps(pilot_offline_readiness(repo), sort_keys=True))
        return
    value = load_pilot_authorization(repo, args.authorization or authorization_path())
    print(
        json.dumps(
            {
                "status": "authorized",
                "authorization_id": value["authorization_id"],
                "campaign_id": value["campaign_id"],
                "batch_id": value["batch_id"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
