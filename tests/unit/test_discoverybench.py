from __future__ import annotations

import copy

import jsonschema
import pytest

from distributed_discovery.benchmark.evaluator import (
    run_golden_suite,
    run_pair,
    run_simulated_suite,
)
from distributed_discovery.benchmark.model import (
    PROHIBITED_CAPABILITIES,
    DeterministicMockAdapter,
    ExternalAdapter,
    InformationBoundaryError,
    builtin_protocols,
    compatibility_matrix,
    metric_registry,
    protocol_registry,
    task_registry,
    task_view,
    validate_task,
)
from distributed_discovery.benchmark.verification import corruption_tests, verify_certificate
from distributed_discovery.validation.bootstrap import repository_root


def test_registry_counts_and_exact_golden_results() -> None:
    tasks = task_registry()
    assert len(tasks) == 15
    assert len(protocol_registry()) == 13
    assert len(metric_registry()) == 19
    assert len(compatibility_matrix()) == 195
    for task in tasks:
        validate_task(task)
    certificate = run_golden_suite()
    assert certificate["compatible_pairs"] == 16
    assert certificate["excluded_pairs"] == 179
    assert certificate["composite_score"] is None
    assert verify_certificate(certificate, repository_root())["passed"] is True


def test_attention_v2_extends_v1_without_changing_it() -> None:
    v1 = run_golden_suite()
    v2 = run_golden_suite("v2")
    assert (len(task_registry("v2")), len(protocol_registry("v2")), len(metric_registry("v2"))) == (
        20,
        21,
        27,
    )
    assert (v2["candidate_pairs"], v2["compatible_pairs"], v2["excluded_pairs"]) == (
        420,
        28,
        392,
    )
    v1_rows = [(row["task_id"], row["protocol_id"], row["metrics"]) for row in v1["results"]]
    v2_rows = [
        (row["task_id"], row["protocol_id"], row["metrics"])
        for row in v2["results"][: len(v1_rows)]
    ]
    assert v2_rows == v1_rows
    assert verify_certificate(v2, repository_root(), "v2")["passed"] is True
    assert all(corruption_tests(v2, repository_root(), "v2").values())
    row = run_pair(task_registry("v2")[-1], "third-option-contrarian", "v2")
    assert row["metrics"] == {
        "discovery": "895/1024",
        "conditional-attention-category": "third-option-contrarian",
    }


def test_threshold_v3_extends_v2_without_changing_earlier_versions() -> None:
    v1 = run_golden_suite()
    v2 = run_golden_suite("v2")
    v3 = run_golden_suite("v3")
    assert (len(task_registry("v3")), len(protocol_registry("v3")), len(metric_registry("v3"))) == (
        24,
        29,
        39,
    )
    assert (v3["candidate_pairs"], v3["compatible_pairs"], v3["excluded_pairs"]) == (
        696,
        36,
        660,
    )
    v1_rows = [(row["task_id"], row["protocol_id"], row["metrics"]) for row in v1["results"]]
    v2_rows = [(row["task_id"], row["protocol_id"], row["metrics"]) for row in v2["results"]]
    assert [
        (row["task_id"], row["protocol_id"], row["metrics"])
        for row in v3["results"][: len(v1_rows)]
    ] == v1_rows
    assert [
        (row["task_id"], row["protocol_id"], row["metrics"])
        for row in v3["results"][: len(v2_rows)]
    ] == v2_rows
    assert v3["composite_score"] is None
    assert verify_certificate(v3, repository_root(), "v3")["passed"] is True
    assert all(corruption_tests(v3, repository_root(), "v3").values())
    mechanism = run_pair(task_registry("v3")[-1], "marginal-team-contribution", "v3")
    assert mechanism["metrics"] == {
        "planner-portfolio-rows": 5,
        "pair-stable-rows": 5,
        "equilibrium-multiplicity": 21,
    }


def test_bad_task_fixtures_reject_ambiguous_information_and_objectives() -> None:
    missing_information = copy.deepcopy(task_registry()[0])
    del missing_information["per_agent_information"]
    with pytest.raises(jsonschema.ValidationError):
        validate_task(missing_information)
    missing_objective = copy.deepcopy(task_registry()[0])
    del missing_objective["social_objective"]
    with pytest.raises(jsonschema.ValidationError):
        validate_task(missing_objective)
    wrong_count = copy.deepcopy(task_registry()[0])
    wrong_count["per_agent_information"] = [[]]
    with pytest.raises(ValueError, match="per-agent"):
        validate_task(wrong_count)


def test_protocol_view_rejects_hidden_information_and_mutation() -> None:
    task = task_registry()[0]
    protocol = builtin_protocols()["blind-distinct"]
    view = task_view(task, protocol)
    for key in PROHIBITED_CAPABILITIES:
        with pytest.raises(InformationBoundaryError):
            _ = view[key]
    with pytest.raises(TypeError):
        view._values["task_id"] = "changed"  # type: ignore[index]
    with pytest.raises(ValueError, match="incompatible"):
        run_pair(task, "consensus")


def test_external_adapter_is_disabled_and_mock_is_deterministic() -> None:
    view = task_view(task_registry()[0], builtin_protocols()["blind-distinct"])
    with pytest.raises(RuntimeError, match="disabled"):
        ExternalAdapter("external").run(view)
    assert DeterministicMockAdapter().run(view) == DeterministicMockAdapter().run(view)


def test_corruptions_and_seeded_simulation() -> None:
    certificate = run_golden_suite()
    assert all(corruption_tests(certificate, repository_root()).values())
    first = run_simulated_suite([101, 211], 200)
    second = run_simulated_suite([101, 211], 200)
    assert first == second
    assert first["exact"] is False
    assert first["replications_per_seed"] == 200
