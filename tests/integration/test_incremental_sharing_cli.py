import json
import subprocess


def test_dd020_preview_registry() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "distributed_discovery.incremental_sharing.study",
            "--preview",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["parameter_cells"] == 73
    assert summary["protocol_rows"] == 2555
    assert summary["strictly_negative_point_increments"] == 1848
    assert summary["zero_point_increments"] == 196
    assert summary["positive_point_increments"] == 0
    assert summary["profiles_differ"] is True
