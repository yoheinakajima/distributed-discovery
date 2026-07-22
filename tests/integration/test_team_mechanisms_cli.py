import json
import subprocess


def test_dd018_preview_registry() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "distributed_discovery.team_mechanisms.study",
            "--preview",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["posterior_fixtures"] == 5
    assert summary["mechanisms"] == 10
    assert summary["mechanism_fixture_rows"] == 50
    assert summary["independent_action_table_entries"] == 4050
    assert summary["all_corruptions_rejected"] is True
