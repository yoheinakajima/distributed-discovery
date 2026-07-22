import json
import subprocess


def test_dd015_preview() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "--no-editable",
            "python",
            "-m",
            "distributed_discovery.dynamic_attention.study",
            "--preview",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["grid_cells"] == 32
    assert summary["objective_rows"] == 64
    assert summary["verification_checks"] == 128
    assert summary["corruption_gates"] == 4
