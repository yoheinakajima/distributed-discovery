"""Bounded, immutable DD-024 runs; readiness never evaluates a scientific cell."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from distributed_discovery.validation.bootstrap import repository_root

STUDY = Path("studies/DD-024-behavioral-diversity-discovery")
MODULES = {"track-02": "robustness", "track-03": "feedback", "track-04": "timing"}
ARTIFACT_INVENTORY = "artifact-hashes.json"
PUBLIC_OUTPUT_SUFFIXES = {".json", ".md"}


def _write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_file(base: Path, relative: Any) -> Path:
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
        or "\\" in relative
    ):
        raise ValueError("unsafe artifact path")
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError(f"unsafe or missing artifact path: {relative}")
    return path


def _check_hashes(base: Path, hashes: Any, label: str) -> dict[str, str]:
    if not isinstance(hashes, dict):
        raise ValueError(f"{label} checksum inventory must be a mapping")
    checked: dict[str, str] = {}
    for relative, expected in hashes.items():
        path = _relative_file(base, relative)
        if not isinstance(expected, str) or _hash(path) != expected:
            raise ValueError(f"{label} checksum mismatch: {relative}")
        checked[relative] = expected
    return checked


def _artifact_files(run: Path) -> dict[str, Path]:
    return {
        str(path.relative_to(run)): _relative_file(run, str(path.relative_to(run)))
        for path in sorted(run.rglob("*"))
        if path.is_file()
        and str(path.relative_to(run)) not in {"manifest.json", ARTIFACT_INVENTORY}
    }


def config_digest(config: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def load_config(root: Path, track: str) -> tuple[Path, dict[str, Any]]:
    if track not in MODULES:
        raise ValueError("track is not admitted for primary execution")
    path = root / STUDY / "tracks" / track / "config.json"
    config: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if config.get("study_id") != "DD-024" or config.get("track_id") != track:
        raise ValueError("configuration identity mismatch")
    if config.get("time_cap_seconds") != 120 or config.get("memory_cap_mb") != 1024:
        raise ValueError("configuration exceeds or changes the registered resource caps")
    if config.get("random_seeds") != {"algorithm": [], "model": None}:
        raise ValueError("this exact finite campaign does not use random sampling")
    frozen = json.loads((root / STUDY / "registered-configs.json").read_text())
    if frozen["tracks"][track]["config_hash_sha256"] != config_digest(config):
        raise ValueError("primary configuration differs from its complete registered grid")
    return path, config


def readiness(root: Path, track: str) -> dict[str, Any]:
    """Check identity and files only, without importing an experiment module."""
    config_path, config = load_config(root, track)
    paths = [
        config_path,
        root / STUDY / "tracks" / track / "model.md",
        root / STUDY / "tracks" / track / "novelty.md",
        root / "tasks/behavioral-diversity-discovery.yml",
        root / "uv.lock",
        root / STUDY / "registered-configs.json",
        root / "src/distributed_discovery/behavioral_diversity" / f"{MODULES[track]}.py",
        *sorted((root / "src/distributed_discovery/behavioral_diversity").glob("*.py")),
    ]
    missing = [str(path.relative_to(root)) for path in paths if not path.is_file()]
    if missing:
        raise ValueError(f"registration files missing: {missing}")
    return {
        "study_id": "DD-024",
        "track_id": track,
        "config_path": str(config_path.relative_to(root)),
        "config_hash_sha256": config_digest(config),
        "git_commit": _git(root, "rev-parse", "HEAD"),
        "git_dirty": bool(_git(root, "status", "--porcelain")),
        "input_hashes": {str(path.relative_to(root)): _hash(path) for path in paths},
        "scientific_cells_evaluated": 0,
    }


def _store_result(output: Path, result: dict[str, Any]) -> None:
    """Shard rows so a scientific table never needs a large opaque artifact."""
    data = dict(result)
    rows = data.pop("rows", None)
    if rows is not None:
        if not isinstance(rows, list):
            raise ValueError("result rows must be a list")
        files = []
        for index, row in enumerate(rows):
            relative = f"rows/{index:04d}.json"
            _write(output / relative, row)
            files.append(relative)
        data["row_files"] = files
    _write(output / "result.json", data)
    if "summary" in result:
        _write(output / "summary.json", result["summary"])


def load_result(output: Path) -> dict[str, Any]:
    result: dict[str, Any] = json.loads((output / "result.json").read_text())
    if "row_files" in result:
        paths = result.pop("row_files")
        for relative in paths:
            if Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise ValueError("unsafe result shard")
        result["rows"] = [json.loads((output / relative).read_text()) for relative in paths]
    return result


def _worker(root: Path, track: str, run: Path) -> int:
    """Evaluate and independently check the frozen configuration in one child."""
    _, config = load_config(root, track)
    module = importlib.import_module(f"distributed_discovery.behavioral_diversity.{MODULES[track]}")
    started = perf_counter()
    try:
        result = module.run(config)
        _store_result(run / "outputs", result)
        verification = module.verify(config, load_result(run / "outputs"))
        _write(run / "outputs/verification.json", verification)
        corruptions = verification.get("corruptions", {})
        passed = bool(
            verification.get("passed")
            and not verification.get("errors")
            and corruptions
            and all(value is True for value in corruptions.values())
        )
        print(json.dumps({"track_id": track, "verification_passed": passed}, sort_keys=True))
        return 0 if passed else 2
    except Exception:
        traceback.print_exc()
        return 1
    finally:
        _write(
            run / "outputs/resources.json",
            {
                "worker_elapsed_seconds": round(perf_counter() - started, 6),
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "memory_limit_bytes": config["memory_cap_mb"] * 1024 * 1024,
                "cpu_limit_seconds": config["time_cap_seconds"],
            },
        )


def _resource_limits() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))


def reserve_attempt(root: Path, track: str, binding: dict[str, Any], run_id: str) -> Path:
    """Atomically consume a track in the Git directory shared by all worktrees."""
    common = Path(_git(root, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = root / common
    directory = common.resolve() / "dd024-primary-reservations"
    directory.mkdir(parents=True, exist_ok=True)
    reservation = directory / f"{track}.json"
    record = {
        "study_id": "DD-024",
        "track_id": track,
        "run_id": run_id,
        "git_commit": binding["git_commit"],
        "config_hash_sha256": binding["config_hash_sha256"],
        "created_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "state": "consumed-before-worker-launch",
    }
    try:
        with reservation.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError("this track already has a shared primary-attempt reservation") from error
    return reservation


def execute(root: Path, track: str) -> Path:
    binding = readiness(root, track)
    if binding["git_dirty"]:
        raise RuntimeError("primary execution requires clean committed source")
    config_path, config = load_config(root, track)
    digest = binding["config_hash_sha256"]
    for existing in (root / "results").glob("**/manifest.json"):
        prior = json.loads(existing.read_text())
        if prior.get("study_id") == "DD-024" and prior.get("track_id") == track:
            raise RuntimeError("this registered track already has a preserved attempt")
    started = datetime.now(UTC)
    run_id = f"{started:%Y%m%dT%H%M%SZ}_DD-024_{binding['git_commit'][:8]}_{digest[:10]}"
    run = root / "results/exploratory" / run_id
    if run.exists():
        raise RuntimeError("refusing to overwrite a run directory")
    reservation = reserve_attempt(root, track, binding, run_id)
    run.mkdir(parents=True, exist_ok=False)
    command = (
        f"PYTHONPATH=src python -m distributed_discovery.behavioral_diversity.study --track {track}"
    )
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-024",
        "track_id": track,
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "exit_status": -1,
        "validation_status": "incomplete",
        "git_commit": binding["git_commit"],
        "git_dirty": False,
        "upstream_commit": None,
        "command": command,
        "config_hash_sha256": digest,
        "dependency_lock_hash_sha256": _hash(root / "uv.lock"),
        "input_hashes": binding["input_hashes"],
        "random_seeds": config["random_seeds"],
        "outputs": {},
        "termination": "reserved-before-worker-launch",
    }
    # A hard interruption can leave an incomplete manifest, never an invisible attempt.
    _write(run / "manifest.json", manifest)
    (run / "reservation.json").write_bytes(reservation.read_bytes())
    (run / "config.json").write_bytes(config_path.read_bytes())
    (run / "reproduce.sh").write_text("#!/bin/sh\nset -eu\n" + command + "\n")
    worker = [
        sys.executable,
        "-m",
        "distributed_discovery.behavioral_diversity.study",
        "--worker",
        "--track",
        track,
        "--run",
        str(run),
    ]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")
    start_clock = perf_counter()
    termination = "completed"
    exit_status = 125
    passed = False
    problems: list[str] = []
    with (run / "stdout.log").open("w") as stdout, (run / "stderr.log").open("w") as stderr:
        process: subprocess.Popen[str] | None = None
        try:
            process = subprocess.Popen(
                worker,
                cwd=root,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                preexec_fn=_resource_limits,
                text=True,
            )
            exit_status = process.wait(timeout=config["time_cap_seconds"])
            if exit_status < 0:
                termination = f"worker-signal-{-exit_status}"
        except subprocess.TimeoutExpired:
            if process is not None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            exit_status, termination = 124, "wall-time-cap"
        except KeyboardInterrupt:
            if process is not None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            exit_status, termination = 130, "coordinator-interruption"
        except (OSError, subprocess.SubprocessError):
            traceback.print_exc(file=stderr)
            exit_status, termination = 125, "worker-launch-failure"
        try:
            verification_path = run / "outputs/verification.json"
            verification = json.loads(verification_path.read_text())
            corruptions = verification.get("corruptions", {})
            passed = bool(
                exit_status == 0
                and verification.get("passed") is True
                and not verification.get("errors")
                and corruptions
                and all(value is True for value in corruptions.values())
            )
            for relative, expected in binding["input_hashes"].items():
                if _hash(root / relative) != expected:
                    passed = False
                    problems.append(f"source input changed during execution: {relative}")
            if not passed and exit_status == 0:
                exit_status, termination = 2, "verification-or-source-check-failure"
        except (OSError, ValueError, TypeError, AttributeError):
            traceback.print_exc(file=stderr)
            problems.append("verification output missing, malformed, or unreadable")
            passed = False
            if exit_status == 0:
                exit_status, termination = 2, "malformed-verification-output"
    for log in (run / "stdout.log", run / "stderr.log"):
        value = log.read_text()
        for prefix, replacement in (
            (str(root), "<repo>"),
            (sys.prefix, "<env>"),
            (sys.base_prefix, "<python>"),
        ):
            value = value.replace(prefix, replacement)
        log.write_text(value)
    _write(
        run / "validation.json",
        {
            "passed": passed,
            "elapsed_seconds": round(perf_counter() - start_clock, 6),
            "time_cap_seconds": config["time_cap_seconds"],
            "memory_cap_mb": config["memory_cap_mb"],
            "termination": termination,
            "problems": problems,
            "exactness_scope": "declared finite model and policy class only",
            "claim_promotion": "separate audit required",
        },
    )
    packages = {
        name: importlib.metadata.version(name) for name in ("PyYAML", "jsonschema", "pytest")
    }
    _write(
        run / "environment.json",
        {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": packages,
        },
    )
    (run / "README.md").write_text(
        f"# DD-024 / {track}\n\nRun `{run_id}`.\n\n"
        "Exact bounded diagnostic; global novelty and human applicability are unestablished.\n\n"
        "`outputs/result.json` indexes complete row files; `outputs/verification.json` records "
        "the independent method and corruptions. A passing run does not promote a claim.\n"
        "\n`reproduce.sh` records the historical primary command. To reproduce the primary, "
        "first register separate reproduction authority, then use a fresh clone at the "
        "manifest's source commit; this campaign "
        "refuses a second primary attempt. To check existing artifacts without creating a run, "
        "use `--track <track-id> --verify-existing <relative-run-directory>`.\n"
    )
    artifacts = {relative: _hash(path) for relative, path in _artifact_files(run).items()}
    _write(run / ARTIFACT_INVENTORY, artifacts)
    outputs = {
        relative: digest
        for relative, digest in artifacts.items()
        if Path(relative).suffix in PUBLIC_OUTPUT_SUFFIXES
    }
    outputs[ARTIFACT_INVENTORY] = _hash(run / ARTIFACT_INVENTORY)
    manifest.update(
        ended_utc=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        exit_status=exit_status,
        validation_status="passed" if passed else "failed",
        outputs=outputs,
        termination=termination,
    )
    _write(run / "manifest.json", manifest)
    if not passed:
        raise RuntimeError(f"preserved unsuccessful primary attempt: {run_id}")
    return run


def verify_existing(root: Path, track: str, run: Path) -> dict[str, Any]:
    """Read-only independent reconstruction of an existing run, never a new primary."""
    run = (root / run).resolve()
    if not run.is_relative_to((root / "results").resolve()):
        raise ValueError("verification requires a repository result directory")
    manifest = json.loads((run / "manifest.json").read_text())
    if manifest.get("study_id") != "DD-024" or manifest.get("track_id") != track:
        raise ValueError("run identity mismatch")
    outputs = _check_hashes(run, manifest["outputs"], "manifest output")
    if ARTIFACT_INVENTORY not in outputs:
        raise ValueError("manifest does not bind the complete artifact inventory")
    artifacts = _check_hashes(
        run,
        json.loads(_relative_file(run, ARTIFACT_INVENTORY).read_text()),
        "artifact inventory",
    )
    if set(artifacts) != set(_artifact_files(run)):
        raise ValueError("artifact inventory does not cover exactly the preserved files")
    public = {
        relative: digest
        for relative, digest in artifacts.items()
        if Path(relative).suffix in PUBLIC_OUTPUT_SUFFIXES
    }
    public[ARTIFACT_INVENTORY] = _hash(run / ARTIFACT_INVENTORY)
    if outputs != public:
        raise ValueError("manifest outputs differ from the safe artifact inventory")
    _check_hashes(root, manifest["input_hashes"], "frozen source")
    config = json.loads((run / "config.json").read_text())
    if config_digest(config) != manifest["config_hash_sha256"]:
        raise ValueError("saved configuration digest mismatch")
    module = importlib.import_module(f"distributed_discovery.behavioral_diversity.{MODULES[track]}")
    verified: dict[str, Any] = module.verify(config, load_result(run / "outputs"))
    return {"run_id": manifest["run_id"], "new_primary_run": False, "verification": verified}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", choices=sorted(MODULES), required=True)
    parser.add_argument("--readiness", action="store_true", help="files and identities only")
    parser.add_argument("--verify-existing", type=Path, help="reconstruct saved evidence read-only")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--run", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = repository_root()
    if args.worker:
        if args.run is None:
            parser.error("internal worker requires its new run directory")
        raise SystemExit(_worker(root, args.track, args.run))
    if args.verify_existing is not None:
        record = verify_existing(root, args.track, args.verify_existing)
        print(json.dumps(record, indent=2, sort_keys=True))
        if not record["verification"].get("passed"):
            raise SystemExit(2)
    elif args.readiness:
        print(json.dumps(readiness(root, args.track), indent=2, sort_keys=True))
    else:
        print(execute(root, args.track).name)


if __name__ == "__main__":
    main()
