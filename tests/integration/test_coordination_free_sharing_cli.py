import json
import os
import subprocess
import sys
from pathlib import Path


def test_dd022_preview_registry() -> None:
    root = Path(__file__).resolve().parents[2]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(root / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "distributed_discovery.coordination_free_sharing.study",
            "--preview",
        ],
        cwd=root,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["cells"] == 42
    assert payload["gain_class_counts"] == {"negative": 18, "neutral": 18, "positive": 6}
    assert payload["verification_passed"] is True
    assert payload["all_corruptions_rejected"] is True
