"""Validate claim ledgers against the repository schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from distributed_discovery.validation.bootstrap import repository_root


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_file(data_path: Path, schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = load_yaml(data_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        detail = "\n".join(f"- {list(error.absolute_path)}: {error.message}" for error in errors)
        raise RuntimeError(f"claim validation failed for {data_path}:\n{detail}")


def validate_ledger(root: Path | None = None, fixture: bool = False) -> None:
    base = root or repository_root()
    data_path = base / ("tests/fixtures/valid_claims.yml" if fixture else "claims/claims.yml")
    validate_file(data_path, base / "claims/schema.json")
    print(f"claim validation passed: {data_path.relative_to(base)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    args = parser.parse_args()
    validate_ledger(fixture=args.fixture)


if __name__ == "__main__":
    main()
