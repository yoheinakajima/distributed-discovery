import json
from pathlib import Path

import pytest


def test_passed_canonical_run_full_precision_values() -> None:
    root = Path(__file__).parents[2]
    passed = []
    for manifest_path in (root / "results/baseline").glob("*/manifest.json"):
        manifest = json.loads(manifest_path.read_text())
        if manifest["validation_status"] == "passed":
            passed.append(manifest_path.parent)
    assert passed
    for run_dir in passed:
        metrics = json.loads((run_dir / "metrics.json").read_text())
        assert metrics["consensus"] == pytest.approx(0.383468709731, abs=5e-13)
        assert metrics["market"] == pytest.approx(0.599099252439, abs=5e-13)
        assert metrics["private"] == pytest.approx(0.832227840000, abs=5e-13)
        assert metrics["planner"] == pytest.approx(0.859421246199, abs=5e-13)
        assert metrics["crossover"] == pytest.approx(0.788461656521, abs=5e-13)
        assert metrics["market_distinct"] == pytest.approx(2.673494083278, abs=5e-13)
        assert metrics["private_distinct"] == pytest.approx(6.156849828175, abs=5e-13)
        assert metrics["recovery_budget"] == 7
