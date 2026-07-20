from pathlib import Path

from distributed_discovery.validation.bootstrap import validate_repository


def test_repository_contract_files_exist() -> None:
    validate_repository(Path(__file__).parents[2])
