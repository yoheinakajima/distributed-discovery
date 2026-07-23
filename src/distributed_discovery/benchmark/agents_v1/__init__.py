"""Offline DiscoveryBench Agents v1 instrument implementation."""

from distributed_discovery.benchmark.agents_v1.generation import (
    canonical_cells,
    generate_public_calibration,
)
from distributed_discovery.benchmark.agents_v1.rehearsal import run_rehearsal

__all__ = ["canonical_cells", "generate_public_calibration", "run_rehearsal"]
