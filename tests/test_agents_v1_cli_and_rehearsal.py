from __future__ import annotations

import pytest

from distributed_discovery.benchmark.agents_v1.cli import run_cli
from distributed_discovery.benchmark.agents_v1.rehearsal import (
    readiness_report,
    run_rehearsal,
)


def test_cli_conformance_surfaces() -> None:
    assert run_cli(["versions"])["instrument"] == "discoverybench-agents-v1"
    validation = run_cli(["validate"])
    assert validation == {
        "status": "pass",
        "canonical_cells": 138,
        "prompt_variants": 552,
        "primitive_labeled_states": 58_945,
    }
    assert run_cli(["compile-prompts"])["status"] == "pass"
    assert run_cli(["verify-custody"])["status"] == "pass"
    assert run_cli(["verify-batch"])["status"] == "pass"
    with pytest.raises(PermissionError, match="disabled"):
        run_cli(["live-execute"])


def test_offline_rehearsal_is_deterministic_and_zero_execution() -> None:
    first = run_rehearsal()
    second = run_rehearsal()
    assert first == second
    assert first["status"] == "pass"
    assert first["case_count"] == 50
    assert first["corruptions_rejected"] == 24
    assert first["method_b_errors"] == []
    assert first["provider_calls"] == 0
    assert first["model_invocations"] == 0
    assert first["network_calls"] == 0
    assert first["external_cost_usd"] == "0"
    assert first["private_material_created"] is False
    assert first["scientific_evidence_created"] is False


def test_readiness_stops_before_campaign_registration() -> None:
    report = readiness_report()
    assert report["decision"] == "ready-for-evaluation-registration"
    assert report["future_authorization_required"] is True
    assert report["next_file"] == "plans/DISCOVERYBENCH_AGENTS_V1_EVALUATION.md"
