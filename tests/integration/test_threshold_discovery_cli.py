import json
import subprocess


def test_tiny_threshold_preview() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "distributed_discovery.threshold_discovery.study",
            "--preview",
            "--tiny",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["labeled_count_vectors"] == 10
    assert summary["method_rows_equal"] is True
    assert summary["threshold_rows"] == 3
