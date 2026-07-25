#!/usr/bin/env python3
"""Run the exact authorized read-only diagnosis and emit only a redacted candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.pilot_diagnostic import (
    authorization_path,
    load_diagnostic_authorization,
    run_read_only_diagnostic,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--authorization", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    authorization = load_diagnostic_authorization(repo, args.authorization or authorization_path())
    evidence = run_read_only_diagnostic(repo, authorization)
    print(json.dumps(evidence.public_candidate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
