from copy import deepcopy

from distributed_discovery.atlas.model import cartesian_registry, evaluate, validity
from distributed_discovery.atlas.verification import verify_row


def test_validity_registry_is_complete_and_bounded() -> None:
    registry = cartesian_registry()
    valid = [cell for cell in registry if validity(cell)[0]]
    assert len(registry) == 288
    assert len(valid) == 20
    assert {cell["allocation"] for cell in valid} == {
        "direct",
        "consensus",
        "market",
        "planner",
        "sequential",
        "joint",
    }
    assert {cell["reward"] for cell in valid} == {
        "equal-split",
        "pooling",
        "sole-rescue",
        "marginal-coverage",
        "DD-006A",
        "DD-006B",
    }


def test_separate_atlas_evaluator_and_corruption() -> None:
    cell = next(
        cell for cell in cartesian_registry() if validity(cell)[0] and cell["reward"] == "DD-006B"
    )
    row = evaluate(cell)
    assert verify_row(row)
    assert row["discovery"] == "11/12"
    assert row["truthfulness"] == "strict"
    bad = deepcopy(row)
    bad["transfer_budget"] = "99"
    assert not verify_row(bad)
