"""Run the registered exact DD-021 General Sharing Frontier study."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import resource
import subprocess
import sys
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from distributed_discovery.general_sharing.model import channel_certificate, channel_record
from distributed_discovery.general_sharing.verification import build
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-021-general-sharing-frontier/configs/registry.yml")
SOURCE_PATHS = (
    CONFIG,
    Path("src/distributed_discovery/general_sharing/model.py"),
    Path("src/distributed_discovery/general_sharing/verification.py"),
    Path("src/distributed_discovery/general_sharing/study.py"),
    Path("studies/DD-021-general-sharing-frontier/model.md"),
    Path("studies/DD-021-general-sharing-frontier/literature.md"),
    Path("studies/DD-021-general-sharing-frontier/proof.md"),
    Path("studies/DD-021-general-sharing-frontier/proof-audit.md"),
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(serial(value), indent=2, sort_keys=True) + "\n")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SOURCE_PATHS:
        digest.update(str(relative).encode())
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def bundle(config: dict[str, Any], root: Path) -> dict[str, Any]:
    if config["study_id"] != "DD-021" or config["schema_version"] != (
        "dd021-general-sharing-frontier-v1"
    ):
        raise ValueError("DD-021 config identity mismatch")
    fingerprint = source_fingerprint(root)
    (
        channels,
        labeled_rows,
        histogram_rows,
        witnesses,
        verification,
        corruptions,
        summary,
    ) = build(config, fingerprint)
    schema = json.loads((root / config["channel_schema_path"]).read_text())
    validator = Draft202012Validator(schema)
    public_records = [channel_record(channel) for channel in channels]
    schema_errors = [
        error.message for record in public_records for error in validator.iter_errors(record)
    ]
    if schema_errors:
        raise ValueError(f"DD-021 channel schema errors: {schema_errors[:3]}")
    if not verification["passed"] or not all(corruptions.values()):
        raise RuntimeError("DD-021 exact verification failed")
    return {
        "channels": channels,
        "channel_certificates": [channel_certificate(channel) for channel in channels],
        "rows": labeled_rows,
        "independent_rows": histogram_rows,
        "witnesses": witnesses,
        "verification": {**verification, "channel_schema": True},
        "corruptions": corruptions,
        "summary": {
            **summary,
            "channel_laws": len(channels),
            "source_checksum_sha256": fingerprint,
        },
    }


def _peak_memory_mb() -> float:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value / (1024 * 1024) if sys.platform == "darwin" else value / 1024


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text())
    start_clock = perf_counter()
    data = bundle(config, root)
    elapsed = perf_counter() - start_clock
    peak_memory = _peak_memory_mb()
    if elapsed > config["time_cap_seconds"]:
        raise RuntimeError("DD-021 exceeded its registered time cap")
    if peak_memory > config["memory_cap_mb"]:
        raise RuntimeError("DD-021 exceeded its registered memory cap")
    preview = {
        **data["summary"],
        "witnesses": data["witnesses"],
        "verification_passed": data["verification"]["passed"],
        "all_corruptions_rejected": all(data["corruptions"].values()),
        "elapsed_seconds": round(elapsed, 6),
        "peak_memory_mb": round(peak_memory, 3),
    }
    if args.preview:
        print(json.dumps(serial(preview), indent=2, sort_keys=True))
        return

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip():
        raise RuntimeError("DD-021 primary run requires clean committed source")
    config_hash = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-021_{commit[:8]}_{config_hash[:10]}"
    run = root / "results/verified" / run_id
    if run.exists():
        raise RuntimeError("refusing overwrite")
    outputs = run / "outputs"
    outputs.mkdir(parents=True)
    (run / "config.yml").write_text(config_path.read_text())
    write_json(outputs / "summary.json", data["summary"])
    write_json(outputs / "channels.json", data["channel_certificates"])
    write_json(outputs / "registry.json", data["rows"])
    write_json(outputs / "independent-registry.json", data["independent_rows"])
    write_json(outputs / "minimal-witnesses.json", data["witnesses"])
    write_json(outputs / "verification.json", data["verification"])
    write_json(outputs / "corruption-tests.json", data["corruptions"])
    write_json(
        outputs / "method-agreement-certificate.json",
        {
            "certificate_format": config["certificate_format"],
            "source_checksum_sha256": data["summary"]["source_checksum_sha256"],
            "scenarios": data["summary"]["scenarios"],
            "method_agreement": data["verification"]["method_agreement"],
            "witness_minimality_agreement": data["verification"]["witness_minimality_agreement"],
        },
    )
    write_json(
        outputs / "proof-audit-summary.json",
        {
            "frontier_identity_checked": True,
            "zero_error_boundary_checked": True,
            "duplicates_checked": True,
            "ties_checked": True,
            "n_greater_than_m_checked": True,
            "centralized_authority_boundary_checked": True,
            "decentralized_implementation_not_claimed": True,
            "source": "studies/DD-021-general-sharing-frontier/proof-audit.md",
        },
    )
    ended = datetime.now(UTC)
    validation = {
        **data["verification"],
        "all_corruptions_rejected": all(data["corruptions"].values()),
        "elapsed_seconds": round(elapsed, 6),
        "peak_memory_mb": round(peak_memory, 3),
        "time_cap_seconds": config["time_cap_seconds"],
        "memory_cap_mb": config["memory_cap_mb"],
    }
    write_json(run / "validation.json", validation)
    (run / "stdout.txt").write_text(
        f"{run_id}\nexact General Sharing Frontier registry and verification passed\n"
    )
    (run / "stderr.txt").write_text("")
    input_paths = [root / relative for relative in SOURCE_PATHS]
    input_paths.append(root / config["channel_schema_path"])
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-021",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": ended.isoformat().replace("+00:00", "Z"),
        "exit_status": 0,
        "validation_status": "passed",
        "git_commit": commit,
        "git_dirty": False,
        "upstream_commit": None,
        "command": "make dd021-general-sharing-frontier",
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": file_hash(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): file_hash(path) for path in input_paths},
        "random_seeds": config["random_seeds"],
        "outputs": {
            str(path.relative_to(run)): file_hash(path) for path in sorted(outputs.glob("*"))
        },
        "resource_usage": {
            "elapsed_seconds": round(elapsed, 6),
            "peak_memory_mb": round(peak_memory, 3),
        },
    }
    write_json(run / "manifest.json", manifest)
    write_json(
        run / "environment.json",
        {"python": platform.python_version(), "platform": platform.platform()},
    )
    (run / "README.md").write_text(
        f"# DD-021 {run_id}\n\nExact bounded General Sharing Frontier registry.\n"
    )
    print(run_id)


if __name__ == "__main__":
    main()
