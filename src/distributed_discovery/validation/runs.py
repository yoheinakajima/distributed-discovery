"""Validate immutable run manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from distributed_discovery.validation.bootstrap import repository_root


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_run_manifests(root: Path | None = None) -> int:
    base = root or repository_root()
    schema = json.loads((base / "experiments/manifest.schema.json").read_text())
    validator = Draft202012Validator(schema)
    manifests = sorted((base / "results").glob("**/manifest.json"))
    if not manifests:
        raise RuntimeError("no run manifests found")
    failures: list[str] = []
    for path in manifests:
        data = json.loads(path.read_text())
        for error in validator.iter_errors(data):
            failures.append(f"{path.relative_to(base)}: {error.message}")
        if data.get("validation_status") == "passed" and data.get("run_id") != path.parent.name:
            failures.append(f"{path.relative_to(base)}: run_id does not match directory")
        if data.get("validation_status") == "passed":
            for relative, expected_hash in data.get("outputs", {}).items():
                output = path.parent / relative
                if not output.is_file():
                    failures.append(f"{path.relative_to(base)}: missing output {relative}")
                elif _sha256(output) != expected_hash:
                    failures.append(f"{path.relative_to(base)}: checksum mismatch {relative}")
    if failures:
        raise RuntimeError("run manifest validation failed:\n" + "\n".join(failures))
    print(f"run manifest validation passed ({len(manifests)} manifests)")
    return len(manifests)


if __name__ == "__main__":
    validate_run_manifests()
