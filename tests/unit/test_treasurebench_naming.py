from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import yaml

from distributed_discovery import cli

ROOT = Path(__file__).resolve().parents[2]

FROZEN_SCHEMAS = {
    "task-v1.schema.json": "5bfca5952c35823986137f4c13740d9c56d90ef1fdb0d11ac7f9bd2c0fa90d92",
    "task-v2.schema.json": "c52bb69bbfa76ffeee316b02aad3d5c0d72ab46643de596cc2025f64344bc6f2",
    "task-v3.schema.json": "9da2709a5790afeecd7c8e6dac81c3215cbdb15731f6dd6a77ddda2e6ce7c5d1",
}


def _run_audit() -> dict[str, object]:
    path = ROOT / "scripts/audit_treasurebench_naming.py"
    spec = importlib.util.spec_from_file_location("audit_treasurebench_naming", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit()


def test_naming_schema_funnel_routes_and_lexical_policy() -> None:
    result = _run_audit()
    assert result["decision"] == "treasurebench-selected-and-implemented"
    assert result["formal_suite"] == "TreasureBench"
    assert result["companion"] == "Treasure Hunt"
    assert result["historical_alias"] == "DiscoveryBench"
    assert result["funnel"] == "pass"
    assert result["canonical_routes"] == result["historical_routes"] == 7
    assert result["legal_clearance"] is False
    assert result["namespace_reserved"] is False


def test_frozen_discoverybench_schema_bytes_and_ids_are_unchanged() -> None:
    directory = ROOT / "studies/DD-010-discoverybench/schemas"
    for name, expected_hash in FROZEN_SCHEMAS.items():
        path = directory / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash
        assert "/discoverybench-task-v" in json.loads(path.read_text(encoding="utf-8"))["$id"]


def test_version_transition_does_not_create_a_rebranding_content_version() -> None:
    transition = yaml.safe_load(
        (ROOT / "docs/benchmark/treasurebench-version-transition.yml").read_text(encoding="utf-8")
    )
    assert transition["new_content_version_created"] is False
    assert transition["root_distribution"] == "distributed-discovery"
    assert transition["frozen_identifiers_unchanged"] is True


def test_distributed_discovery_and_treasurebench_cli_aliases_match(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["distributed-discovery", "agents-v1", "versions"])
    cli.main()
    historical = json.loads(capsys.readouterr().out)

    monkeypatch.setattr(sys, "argv", ["distributed-discovery", "treasurebench", "versions"])
    cli.main()
    formal = json.loads(capsys.readouterr().out)

    monkeypatch.setattr(sys, "argv", ["treasurebench", "versions"])
    cli.treasurebench_main()
    standalone = json.loads(capsys.readouterr().out)

    assert historical == formal == standalone
    assert formal["instrument"] == "discoverybench-agents-v1"


def test_treasure_hunt_never_enters_formal_identifiers() -> None:
    formal_sources = [
        ROOT / "claims/claims.yml",
        *sorted((ROOT / "studies/DD-010-discoverybench/schemas").glob("*.json")),
        *sorted((ROOT / "docs/benchmark/agents-v1").glob("*.schema.json")),
    ]
    assert all("Treasure Hunt" not in path.read_text(encoding="utf-8") for path in formal_sources)
