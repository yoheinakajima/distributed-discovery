import json
import subprocess


def test_dd021_preview_registry() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "distributed_discovery.general_sharing.study",
            "--preview",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["channel_laws"] == 59
    assert summary["scenarios"] == 177
    assert summary["verification_passed"] is True
    assert summary["all_corruptions_rejected"] is True
    assert summary["witnesses"]["same_baseline_opposite_sign"] is not None
