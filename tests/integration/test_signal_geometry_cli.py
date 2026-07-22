import json
import subprocess


def test_dd019_preview_registry() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "distributed_discovery.signal_geometry.study",
            "--preview",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["channels"] == 5
    assert summary["same_accuracy_witness"] is True
    assert summary["different_profile_witness"] is True
    assert summary["point_recovery_budget"] == 3
    assert summary["shortlist_recovery_budget"] == 1
