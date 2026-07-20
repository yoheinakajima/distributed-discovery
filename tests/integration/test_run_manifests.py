from pathlib import Path

from distributed_discovery.validation.runs import validate_run_manifests


def test_saved_run_manifests_validate() -> None:
    assert validate_run_manifests(Path(__file__).parents[2]) >= 1
