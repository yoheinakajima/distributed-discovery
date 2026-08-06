#!/usr/bin/env python3
"""Authorization-free AO-0012 runtime audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.open_weight_cloud_runtime import (
    run_offline_rehearsal,
    validate_registration,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rehearsal", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = run_offline_rehearsal(root) if args.rehearsal else validate_registration(root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
