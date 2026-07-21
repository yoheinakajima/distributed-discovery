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
