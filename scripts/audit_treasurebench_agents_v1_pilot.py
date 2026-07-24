#!/usr/bin/env python3
"""Audit the public, offline TreasureBench Agents v1 pilot contracts."""

from __future__ import annotations

import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.pilot import (
    audit_pilot_corruptions,
    pilot_offline_readiness,
)


def main() -> None:
    repo = Path.cwd()
    corruptions = audit_pilot_corruptions(repo)
    failures = [item for item in corruptions if item["status"] != "rejected"]
    if failures:
        raise SystemExit(f"pilot corruption audit failed: {failures}")
    result = {
        **pilot_offline_readiness(repo),
        "corruptions": len(corruptions),
        "corruptions_rejected": len(corruptions),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
