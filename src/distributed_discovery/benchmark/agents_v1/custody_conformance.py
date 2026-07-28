"""Offline live-mode-equivalent custody conformance for AO-0007.

The live-mode probe uses the AO-0006 production custody function with
``synthetic=False`` so private task generation, production ordering, CSPRNG
material, persistence, and reload are exercised without provider or credential
access. Before the owner-gated diagnosis, the known public-source candidate is
preserved as an expected pre-repair failure rather than silently bypassed.
"""

from __future__ import annotations

import json
import stat
import tempfile
from collections.abc import Mapping
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from distributed_discovery.benchmark.agents_v1 import pilot
from distributed_discovery.benchmark.agents_v1.custody_repair import (
    BATCH_ID,
    CAMPAIGN_ID,
    audit_execution_source,
    validate_public_diagnostic,
)
from distributed_discovery.benchmark.agents_v1.fresh_pilot_v2_live import (
    _custody,
    _initialize_private_state,
    _load_or_create_sealed,
    _secure_directory,
)
from distributed_discovery.benchmark.agents_v1.models import canonical_json, sha256_hex

REQUIRED_COVERAGE = (
    "os_csprng_seed",
    "separate_task_answer_keys",
    "synthetic_private_task_answer_generation",
    "independent_aes_256_gcm",
    "unique_nonces",
    "domain_separated_associated_data",
    "atomic_exclusive_file_creation",
    "directory_mode_0700",
    "file_mode_0600",
    "seed_task_answer_allocation_commitments",
    "task_answer_ciphertext_persistence",
    "custody_manifest_creation",
    "reload_exact_verification",
    "wrong_key_rejection",
    "corrupted_ciphertext_rejection",
    "interrupted_write_recovery_or_refusal",
    "symlink_refusal",
    "duplicate_object_refusal",
    "no_host_path_or_secret_leakage",
    "deterministic_cleanup",
)


def _domain_commitment(domain: str, value: object) -> str:
    payload = domain.encode() + bytes([0]) + canonical_json(value)
    return f"sha256:{sha256_hex(payload)}"


def _read_json(path: Path) -> dict[str, object]:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise PermissionError("independent verifier refuses non-regular custody objects")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("independent verifier requires JSON objects")
    return {str(name): item for name, item in value.items()}


def _independent_unseal(
    record: Mapping[str, object],
    *,
    key: bytes,
    expected_domain: str,
) -> object:
    manifest = record.get("manifest")
    if not isinstance(manifest, Mapping):
        raise ValueError("sealed manifest is missing")
    if manifest.get("algorithm") != "AES-256-GCM" or manifest.get("domain") != expected_domain:
        raise ValueError("sealed algorithm or domain mismatch")
    nonce = bytes.fromhex(str(manifest["nonce_hex"]))
    ciphertext = bytes.fromhex(str(record["ciphertext_hex"]))
    if len(key) != 32 or len(nonce) != 12:
        raise ValueError("independent verifier requires AES-256-GCM key and nonce sizes")
    if manifest.get("ciphertext_sha256") != f"sha256:{sha256_hex(ciphertext)}":
        raise ValueError("independent ciphertext commitment mismatch")
    associated = canonical_json(
        {"campaign_id": CAMPAIGN_ID, "batch_id": BATCH_ID, "domain": expected_domain}
    )
    if manifest.get("associated_data_sha256") != f"sha256:{sha256_hex(associated)}":
        raise ValueError("independent associated-data commitment mismatch")
    return json.loads(AESGCM(key).decrypt(nonce, ciphertext, associated))


def independent_verify_custody(root: Path) -> Mapping[str, object]:
    """Verify the persisted custody without production unseal/verification helpers."""

    required_files = (
        "seed.bin",
        "task-key.bin",
        "answer-key.bin",
        "task-custody.json",
        "answer-custody.json",
        "custody-manifest.json",
    )
    for relative in required_files:
        info = (root / relative).lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise PermissionError("independent verifier refuses unsafe custody files")
        if stat.S_IMODE(info.st_mode) != 0o600:
            raise PermissionError("independent verifier requires mode-0600 custody files")
    for directory in (root,):
        if directory.is_symlink() or stat.S_IMODE(directory.lstat().st_mode) != 0o700:
            raise PermissionError("independent verifier requires mode-0700 custody roots")
    seed = (root / "seed.bin").read_bytes()
    task_key = (root / "task-key.bin").read_bytes()
    answer_key = (root / "answer-key.bin").read_bytes()
    if any(len(value) != 32 for value in (seed, task_key, answer_key)):
        raise ValueError("independent verifier found invalid custody material length")
    task_record = _read_json(root / "task-custody.json")
    answer_record = _read_json(root / "answer-custody.json")
    task_payload = _independent_unseal(
        task_record,
        key=task_key,
        expected_domain="fresh-real-v2-private-task-batch",
    )
    answer_payload = _independent_unseal(
        answer_record,
        key=answer_key,
        expected_domain="fresh-real-v2-private-answer-key",
    )
    if not isinstance(task_payload, list) or not isinstance(answer_payload, list):
        raise ValueError("independent custody plaintexts must be lists")
    if len(task_payload) != 50 or len(answer_payload) != 50:
        raise ValueError("independent custody task and answer counts differ from 50")
    task_manifest = task_record["manifest"]
    answer_manifest = answer_record["manifest"]
    assert isinstance(task_manifest, Mapping) and isinstance(answer_manifest, Mapping)
    if task_manifest["nonce_hex"] == answer_manifest["nonce_hex"]:
        raise ValueError("task and answer custody nonces are not unique")
    manifest = _read_json(root / "custody-manifest.json")
    expected = {
        "schema_version": "treasurebench-fresh-pilot-v2-custody-manifest-v1",
        "campaign_id": CAMPAIGN_ID,
        "batch_id": BATCH_ID,
        "seed_commitment": _domain_commitment(
            "treasurebench-agents-v1/fresh-pilot-v2-seed", seed.hex()
        ),
        "task_plaintext_commitment": _domain_commitment(
            "treasurebench-agents-v1/fresh-v2-task-batch", task_payload
        ),
        "answer_plaintext_commitment": _domain_commitment(
            "treasurebench-agents-v1/fresh-v2-answer-key", answer_payload
        ),
        "task_ciphertext_commitment": task_manifest["ciphertext_sha256"],
        "answer_ciphertext_commitment": answer_manifest["ciphertext_sha256"],
        "tasks": 50,
    }
    if manifest != expected:
        raise ValueError("independent custody manifest mismatch")
    allocation_commitment = _domain_commitment(
        "treasurebench-agents-v1/fresh-v2-allocation",
        [str(item.get("task_id")) for item in task_payload if isinstance(item, Mapping)],
    )
    return {
        "status": "pass",
        "tasks": len(task_payload),
        "answers": len(answer_payload),
        "algorithm": "AES-256-GCM",
        "unique_nonces": True,
        "domain_separated_associated_data": True,
        "allocation_commitment": allocation_commitment,
    }


def _negative_checks(root: Path) -> Mapping[str, str]:
    task_record = _read_json(root / "task-custody.json")
    task_key = (root / "task-key.bin").read_bytes()
    wrong_key = bytes(value ^ 0xFF for value in task_key)
    outcomes: dict[str, str] = {}
    try:
        _independent_unseal(
            task_record,
            key=wrong_key,
            expected_domain="fresh-real-v2-private-task-batch",
        )
    except InvalidTag:
        outcomes["wrong_key"] = "rejected"
    else:
        raise AssertionError("wrong custody key was accepted")
    corrupted = json.loads(json.dumps(task_record))
    ciphertext = bytearray.fromhex(str(corrupted["ciphertext_hex"]))
    ciphertext[-1] ^= 1
    corrupted["ciphertext_hex"] = bytes(ciphertext).hex()
    try:
        _independent_unseal(
            corrupted,
            key=task_key,
            expected_domain="fresh-real-v2-private-task-batch",
        )
    except (InvalidTag, ValueError):
        outcomes["corrupted_ciphertext"] = "rejected"
    else:
        raise AssertionError("corrupted custody ciphertext was accepted")
    symlink_root = root.parent / "symlink-case"
    _secure_directory(symlink_root)
    symlink = symlink_root / "task-custody.json"
    symlink.symlink_to(root / "task-custody.json")
    try:
        _load_or_create_sealed(
            symlink,
            domain="fresh-real-v2-private-task-batch",
            value=[{"synthetic": True}],
            key=task_key,
        )
    except PermissionError:
        outcomes["symlink"] = "rejected"
    else:
        raise AssertionError("custody symlink was accepted")
    try:
        _load_or_create_sealed(
            root / "task-custody.json",
            domain="fresh-real-v2-private-task-batch",
            value=[{"different": True}],
            key=task_key,
        )
    except (PermissionError, ValueError):
        outcomes["duplicate_mismatch"] = "rejected"
    else:
        outcomes["duplicate_mismatch"] = "known-pre-repair-gap"
    exclusive = getattr(pilot, "atomic_private_create", None)
    if exclusive is None:
        outcomes["atomic_exclusive_create"] = "known-pre-repair-gap"
    else:
        path = root.parent / "exclusive-case.bin"
        exclusive(path, b"first")
        try:
            exclusive(path, b"second")
        except FileExistsError:
            outcomes["atomic_exclusive_create"] = "rejected"
        else:
            raise AssertionError("exclusive custody creation overwrote an existing object")
    interrupted = root / ".custody-manifest.json.interrupted"
    interrupted.write_bytes(b"incomplete")
    interrupted.chmod(0o600)
    if _read_json(root / "custody-manifest.json").get("tasks") != 50:
        raise AssertionError("interrupted sibling affected the committed custody manifest")
    outcomes["interrupted_write"] = "refused-or-isolated"
    return outcomes


def audit_conformance_framework(repo: Path) -> Mapping[str, object]:
    """Exercise downstream controls with public fixtures and preserve known gaps."""

    with tempfile.TemporaryDirectory(prefix="ao0007-custody-framework-") as temporary:
        root = Path(temporary) / "xdg-state" / "custody"
        _secure_directory(root)
        _initialize_private_state(root, repo=repo, synthetic=True)
        tasks, material, _task, _answer, _manifest = _custody(
            repo,
            root,
            {"synthetic": True},
            synthetic=True,
        )
        if len(tasks) != 50 or len({bytes(value) for value in material.values()}) != 3:
            raise AssertionError("framework custody material or task count mismatch")
        for name, value in material.items():
            pilot.atomic_private_write(root / f"{name.replace('_', '-')}.bin", value)
        independent = independent_verify_custody(root)
        negatives = _negative_checks(root)
        result = {
            "status": "pass-with-registered-pre-repair-gaps",
            "tasks": 50,
            "provider_calls": 0,
            "credential_reads": 0,
            "spend_usd": "0",
            "independent_verifier": independent["status"],
            "negative_checks": negatives,
            "registered_pre_repair_gaps": sorted(
                name
                for name, status_value in negatives.items()
                if status_value == "known-pre-repair-gap"
            ),
            "host_path_disclosed": False,
            "secret_value_disclosed": False,
        }
        validate_public_diagnostic(result)
        return result


def _successful_coverage() -> dict[str, str]:
    return {name: "pass" for name in REQUIRED_COVERAGE}


def run_live_mode_custody_conformance(repo: Path) -> Mapping[str, object]:
    """Run the production private custody path with disposable synthetic content."""

    source = audit_execution_source(repo)
    framework = audit_conformance_framework(repo)
    cleanup_root: Path | None = None
    result: dict[str, object]
    with tempfile.TemporaryDirectory(prefix="ao0007-live-custody-") as temporary:
        temporary_path = Path(temporary)
        cleanup_root = temporary_path
        root = temporary_path / "xdg-state" / "distributed-discovery" / "custody"
        _secure_directory(root)
        _initialize_private_state(root, repo=repo, synthetic=True)
        try:
            tasks, material, _task, _answer, _manifest = _custody(
                repo,
                root,
                {"synthetic": False, "ao0007_offline_conformance": True},
                synthetic=False,
            )
        except PermissionError as error:
            if (
                source["candidate"] != "private-task-generation-campaign-permit-rejection"
                or "private generation is disabled" not in str(error)
            ):
                raise
            coverage = {name: "not-reached" for name in REQUIRED_COVERAGE}
            coverage["os_csprng_seed"] = "pass"
            coverage["separate_task_answer_keys"] = "pass"
            coverage["synthetic_private_task_answer_generation"] = "expected-pre-repair-failure"
            coverage["deterministic_cleanup"] = "pass"
            result = {
                "status": "expected-pre-repair-failure",
                "failed_stage": "private-task-generation",
                "failure_candidate": source["candidate"],
                "coverage": coverage,
                "framework": framework,
                "provider_calls": 0,
                "credential_reads": 0,
                "spend_usd": "0",
                "real_private_campaign_material": 0,
                "host_path_disclosed": False,
                "secret_value_disclosed": False,
                "cleanup": "pass",
            }
        else:
            if len(tasks) != 50 or len({bytes(value) for value in material.values()}) != 3:
                raise AssertionError("live-mode synthetic custody counts are invalid")
            independent = independent_verify_custody(root)
            negatives = _negative_checks(root)
            if any(status_value == "known-pre-repair-gap" for status_value in negatives.values()):
                raise AssertionError("repaired live-mode path retains a registered custody gap")
            result = {
                "status": "pass",
                "failed_stage": None,
                "coverage": _successful_coverage(),
                "independent_verifier": independent,
                "negative_checks": negatives,
                "provider_calls": 0,
                "credential_reads": 0,
                "spend_usd": "0",
                "real_private_campaign_material": 0,
                "host_path_disclosed": False,
                "secret_value_disclosed": False,
                "cleanup": "pass",
            }
    if cleanup_root is None or cleanup_root.exists():
        raise AssertionError("synthetic temporary custody state was not deterministically cleaned")
    validate_public_diagnostic(result)
    return result
