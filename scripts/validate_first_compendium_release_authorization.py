#!/usr/bin/env python3
"""Validate one explicitly supplied first-compendium release authorization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import build_compendium_release as builder
import jsonschema


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--allow-synthetic-fixture", action="store_true")
    args = parser.parse_args(argv)
    try:
        record = builder.validate_authorization(
            args.authorization,
            source_revision=args.source_revision,
            allow_synthetic=args.allow_synthetic_fixture,
        )
    except (
        builder.ReleaseBuildError,
        jsonschema.ValidationError,
        OSError,
        ValueError,
    ) as exc:
        print(f"authorization validation failed: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "authorization_status": record["authorization_status"],
                "candidate_tag": record["candidate_tag"],
                "source_revision": record["source_revision"],
                "valid": True,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
