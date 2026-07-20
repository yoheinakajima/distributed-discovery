"""Validate or apply the repository's non-destructive GitHub organization metadata."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GITHUB = ROOT / ".github"


def load_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def parse_issue(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} has no YAML front matter")
    _, raw_front, body = text.split("---\n", 2)
    front = yaml.safe_load(raw_front)
    if not isinstance(front, dict) or not body.strip():
        raise ValueError(f"{path} needs mapping front matter and a body")
    return front, body.strip() + "\n"


def checked_list(value: Any, name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{name} must be a list of mappings")
    return value


def run_gh(arguments: list[str], *, capture: bool = False) -> str:
    completed = subprocess.run(
        ["gh", *arguments],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )
    return completed.stdout.strip() if capture else ""


def validate() -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[tuple[Path, dict[str, Any], str]]
]:
    labels = checked_list(load_mapping(GITHUB / "labels.yml").get("labels"), "labels")
    milestones = checked_list(
        load_mapping(GITHUB / "milestones.yml").get("milestones"), "milestones"
    )
    label_names = {str(item.get("name", "")) for item in labels}
    if len(label_names) != len(labels) or "" in label_names:
        raise ValueError("label names must be present and unique")
    milestone_names = {str(item.get("title", "")) for item in milestones}
    if len(milestone_names) != len(milestones) or "" in milestone_names:
        raise ValueError("milestone titles must be present and unique")

    issues: list[tuple[Path, dict[str, Any], str]] = []
    titles: set[str] = set()
    for path in sorted((GITHUB / "initial-issues").glob("*.md")):
        front, body = parse_issue(path)
        title = str(front.get("title", ""))
        issue_labels = front.get("labels")
        if not title or title in titles:
            raise ValueError(f"{path} has a missing or duplicate title")
        if not isinstance(issue_labels, list) or not set(map(str, issue_labels)) <= label_names:
            raise ValueError(f"{path} references an unknown label")
        if str(front.get("milestone", "")) not in milestone_names:
            raise ValueError(f"{path} references an unknown milestone")
        titles.add(title)
        issues.append((path, front, body))
    if not issues:
        raise ValueError("at least one initial issue draft is required")
    return labels, milestones, issues


def apply(
    repo: str,
    labels: list[dict[str, Any]],
    milestones: list[dict[str, Any]],
    issues: list[tuple[Path, dict[str, Any], str]],
) -> None:
    if shutil.which("gh") is None:
        raise RuntimeError("gh is required only for --apply")
    run_gh(["repo", "view", repo, "--json", "nameWithOwner"], capture=True)
    for label in labels:
        run_gh(
            [
                "label",
                "create",
                str(label["name"]),
                "--repo",
                repo,
                "--color",
                str(label["color"]),
                "--description",
                str(label["description"]),
                "--force",
            ]
        )

    existing_milestones = set(
        run_gh(
            [
                "api",
                "--method",
                "GET",
                f"repos/{repo}/milestones",
                "-f",
                "state=all",
                "--paginate",
                "--slurp",
                "--jq",
                ".[][] | .title",
            ],
            capture=True,
        ).splitlines()
    )
    for milestone in milestones:
        title = str(milestone["title"])
        if title not in existing_milestones:
            run_gh(
                [
                    "api",
                    "--method",
                    "POST",
                    f"repos/{repo}/milestones",
                    "-f",
                    f"title={title}",
                    "-f",
                    f"description={milestone['description']}",
                ]
            )

    existing_issues = set(
        run_gh(
            [
                "issue",
                "list",
                "--repo",
                repo,
                "--state",
                "all",
                "--limit",
                "1000",
                "--json",
                "title",
                "--jq",
                ".[].title",
            ],
            capture=True,
        ).splitlines()
    )
    for _path, front, body in issues:
        title = str(front["title"])
        if title in existing_issues:
            continue
        arguments = [
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            title,
            "--body",
            body,
            "--milestone",
            str(front["milestone"]),
        ]
        for label in front["labels"]:
            arguments.extend(["--label", str(label)])
        run_gh(arguments)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="apply metadata using gh")
    parser.add_argument("--repo", help="exact OWNER/REPO target; required with --apply")
    args = parser.parse_args()
    labels, milestones, issues = validate()
    print(
        f"validated GitHub setup: {len(labels)} labels, "
        f"{len(milestones)} milestones, {len(issues)} initial issues"
    )
    if args.apply:
        if not args.repo:
            parser.error("--repo OWNER/REPO is required with --apply")
        apply(args.repo, labels, milestones, issues)
        print(f"applied non-destructive GitHub setup to {args.repo}")
    else:
        print("dry run only; no GitHub calls made")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
