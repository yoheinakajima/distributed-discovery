"""Validate the minimum restartable repository contract."""

from __future__ import annotations

from pathlib import Path

REQUIRED_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agent/PLANS.md",
    "plans/MASTER_EXEC_PLAN.md",
    "docs/project-charter.md",
    "docs/repository-contract.md",
    "docs/claim-status-policy.md",
    "docs/reproducibility.md",
    "claims/claims.yml",
    "claims/schema.json",
    "studies/index.md",
)


def repository_root(start: Path | None = None) -> Path:
    candidate = (start or Path.cwd()).resolve()
    for directory in (candidate, *candidate.parents):
        if (directory / "pyproject.toml").is_file():
            return directory
    raise RuntimeError("repository root containing pyproject.toml not found")


def validate_repository(root: Path | None = None) -> None:
    base = root or repository_root()
    missing = [relative for relative in REQUIRED_PATHS if not (base / relative).is_file()]
    if missing:
        raise RuntimeError(f"missing required repository files: {', '.join(missing)}")
    empty = [relative for relative in REQUIRED_PATHS if not (base / relative).read_text().strip()]
    if empty:
        raise RuntimeError(f"empty required repository files: {', '.join(empty)}")
    print(f"bootstrap validation passed ({len(REQUIRED_PATHS)} required files)")


if __name__ == "__main__":
    validate_repository()
