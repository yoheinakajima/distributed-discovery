from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_LABELS = {
    "area:foundations",
    "area:paper",
    "area:site",
    "area:infrastructure",
    *(f"study:DD-{index:03d}" for index in range(8)),
    "type:research",
    "type:proof",
    "type:experiment",
    "type:reproduction",
    "type:documentation",
    "type:bug",
    "status:blocked",
    "status:needs-verification",
    "status:verified",
    "claim:conjecture",
    "claim:negative-result",
}

REQUIRED_TEMPLATES = {
    "research-question.yml",
    "computational-experiment.yml",
    "proof-task.yml",
    "reproduction-task.yml",
    "claim-verification.yml",
    "bug-report.yml",
}


def test_github_taxonomy_and_templates_are_complete() -> None:
    label_data = yaml.safe_load((ROOT / ".github/labels.yml").read_text(encoding="utf-8"))
    assert {item["name"] for item in label_data["labels"]} == REQUIRED_LABELS

    milestone_data = yaml.safe_load((ROOT / ".github/milestones.yml").read_text(encoding="utf-8"))
    assert len(milestone_data["milestones"]) == 6
    assert {path.name for path in (ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml")} == (
        REQUIRED_TEMPLATES
    )


def test_github_setup_defaults_to_offline_dry_run() -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts/setup_github.py")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "23 labels, 6 milestones, 4 initial issues" in completed.stdout
    assert "no GitHub calls made" in completed.stdout
