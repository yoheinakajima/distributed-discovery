import json
import subprocess


def test_dd017_preview_registry() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "distributed_discovery.threshold_equilibrium.study",
            "--preview",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["game_count"] == 160
    assert summary["occupancy_state_count"] == 3728
    assert summary["labeled_profiles"] == 87216
    assert summary["all_corruptions_rejected"] is True
