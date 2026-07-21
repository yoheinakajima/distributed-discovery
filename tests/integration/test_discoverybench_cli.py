from __future__ import annotations

from distributed_discovery.benchmark.cli import run_cli


def test_discoverybench_cli_registry_and_run_commands() -> None:
    assert len(run_cli(["list-tasks"])) == 15
    assert len(run_cli(["list-protocols"])) == 13
    assert len(run_cli(["list-metrics"])) == 19
    task = run_cli(["describe-task", "DB-G12"])
    assert task["task_family"] == "dd006b-strict-joint-mechanism"
    protocol = run_cli(["describe-protocol", "dd006b-mechanism"])
    assert protocol["external"] is False
    row = run_cli(["run", "DB-G12", "dd006b-mechanism"])
    assert row["metrics"]["strict-margin"] == "13/72"
    suite = run_cli(["run-golden"])
    assert suite["exact_reproduction_passed"] is True
    report = run_cli(["render-report"])
    assert report["compatible_pairs"] == 16


def test_discoverybench_cli_attention_v2_is_explicit() -> None:
    assert len(run_cli(["--version", "v2", "list-tasks"])) == 20
    assert len(run_cli(["--version", "v2", "list-protocols"])) == 21
    assert len(run_cli(["--version", "v2", "list-metrics"])) == 27
    row = run_cli(["--version", "v2", "run", "DB-G17", "voluntary-attention-equilibrium"])
    assert row["metrics"]["attention-wedge"] == "3/32"
    assert run_cli(["run-golden"])["task_count"] == 15
