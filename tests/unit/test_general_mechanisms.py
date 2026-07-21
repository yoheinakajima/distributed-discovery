from copy import deepcopy

from distributed_discovery.mechanisms.general import coefficient_vectors, frontier_row
from distributed_discovery.mechanisms.general_verification import verify_row


def test_registered_general_transfer_grid_has_declared_size_and_bounds() -> None:
    vectors = coefficient_vectors()
    assert len(vectors) == 41
    assert all(sum(abs(value) for value in vector) <= 1 for vector in vectors)


def test_general_frontier_row_is_balanced_and_corruption_is_rejected() -> None:
    row = frontier_row("target-identity", coefficient_vectors()[0])
    assert verify_row(row)
    corrupted = deepcopy(row)
    corrupted["coefficients"] = ["2", "0", "0", "0"]
    assert not verify_row(corrupted)
