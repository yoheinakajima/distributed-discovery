"""Public toy custody vectors using AES-256-GCM and domain-separated commitments."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from distributed_discovery.benchmark.agents_v1.models import VERSIONS, canonical_json, sha256_hex

PUBLIC_TOY_LABEL = b"DiscoveryBench Agents v1 PUBLIC TOY ONLY"
PUBLIC_TOY_KEY = hashlib.sha256(PUBLIC_TOY_LABEL + b"/key").digest()
PUBLIC_TOY_NONCE = hashlib.sha256(PUBLIC_TOY_LABEL + b"/nonce").digest()[:12]


def domain_commitment(domain: str, value: object) -> str:
    payload = domain.encode() + bytes([0]) + canonical_json(value)
    return f"sha256:{sha256_hex(payload)}"


@dataclass(frozen=True)
class ToyCustodyBundle:
    ciphertext: bytes
    manifest: Mapping[str, object]
    access_log: tuple[Mapping[str, object], ...]
    output_lock: str


def seal_public_toy(
    *,
    seed_material: str,
    task_batch: object,
    answer_key: object,
    output: object,
) -> ToyCustodyBundle:
    plaintext = canonical_json({"answer_key": answer_key, "seed_material": seed_material})
    associated_data = canonical_json(
        {"instrument": VERSIONS["instrument"], "classification": "public-toy"}
    )
    ciphertext = AESGCM(PUBLIC_TOY_KEY).encrypt(PUBLIC_TOY_NONCE, plaintext, associated_data)
    manifest = {
        "schema_version": VERSIONS["custody"],
        "classification": "public-toy",
        "algorithm": "AES-256-GCM",
        "nonce_hex": PUBLIC_TOY_NONCE.hex(),
        "ciphertext_sha256": sha256_hex(ciphertext),
        "associated_data_sha256": sha256_hex(associated_data),
        "seed_commitment": domain_commitment("agents-v1/seed", seed_material),
        "task_batch_commitment": domain_commitment("agents-v1/task-batch", task_batch),
        "answer_key_commitment": domain_commitment("agents-v1/answer-key", answer_key),
    }
    access_log = (
        {
            "sequence": 1,
            "actor": "offline-public-toy-rehearsal",
            "operation": "seal",
            "private_material": False,
        },
    )
    return ToyCustodyBundle(
        ciphertext,
        manifest,
        access_log,
        domain_commitment("agents-v1/output-lock", output),
    )


def unseal_public_toy(bundle: ToyCustodyBundle) -> Mapping[str, object]:
    if bundle.manifest.get("classification") != "public-toy":
        raise PermissionError("only public toy custody vectors may be unsealed")
    if sha256_hex(bundle.ciphertext) != bundle.manifest.get("ciphertext_sha256"):
        raise ValueError("ciphertext hash mismatch")
    associated_data = canonical_json(
        {"instrument": VERSIONS["instrument"], "classification": "public-toy"}
    )
    plaintext = AESGCM(PUBLIC_TOY_KEY).decrypt(
        bytes.fromhex(str(bundle.manifest["nonce_hex"])),
        bundle.ciphertext,
        associated_data,
    )
    result = json.loads(plaintext)
    if not isinstance(result, dict):
        raise ValueError("custody plaintext must be an object")
    if domain_commitment("agents-v1/seed", result["seed_material"]) != bundle.manifest.get(
        "seed_commitment"
    ):
        raise ValueError("seed commitment mismatch")
    if domain_commitment("agents-v1/answer-key", result["answer_key"]) != bundle.manifest.get(
        "answer_key_commitment"
    ):
        raise ValueError("answer-key commitment mismatch")
    return {str(key): value for key, value in result.items()}


def verify_output_lock(bundle: ToyCustodyBundle, output: object) -> bool:
    return bundle.output_lock == domain_commitment("agents-v1/output-lock", output)


def require_private_custody(*, authorization: object | None, secret_manager: object | None) -> None:
    if authorization is None or secret_manager is None:
        raise PermissionError("private custody requires a future authorization and secret manager")
