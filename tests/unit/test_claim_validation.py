from pathlib import Path

import pytest
import yaml

from distributed_discovery.validation.claims import validate_file


def test_valid_claim_fixture_matches_schema() -> None:
    root = Path(__file__).parents[2]
    validate_file(root / "tests/fixtures/valid_claims.yml", root / "claims/schema.json")


def test_invalid_claim_type_is_rejected(tmp_path: Path) -> None:
    root = Path(__file__).parents[2]
    data = yaml.safe_load((root / "tests/fixtures/valid_claims.yml").read_text())
    data["claims"][0]["claim_type"] = "wishful-thinking"
    invalid = tmp_path / "invalid.yml"
    invalid.write_text(yaml.safe_dump(data))
    with pytest.raises(RuntimeError, match="claim validation failed"):
        validate_file(invalid, root / "claims/schema.json")
