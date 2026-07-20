# GitHub organization setup

The repository has a public GitHub remote by explicit project-owner decision. Local configuration contains 23 project labels, six milestones, six issue forms, and five nonduplicative initial-issue drafts. All five draft issues are live as issues #7 through #11; their bodies preserve intended labels and milestones. The connected GitHub app can manage issues and pull requests, but label, milestone, homepage, and ruleset application still requires a GitHub CLI OAuth session or equivalent settings access.

## Review locally

```sh
uv run --no-editable python scripts/setup_github.py
```

The default mode validates and summarizes `.github/labels.yml`, `.github/milestones.yml`, and `.github/initial-issues/*.md`. It does not call GitHub.

## Apply after GitHub CLI access is authorized

Prerequisites: install `gh`, authenticate it to the intended repository, verify the exact `OWNER/REPO`, and review every draft. Then run:

```sh
uv run --no-editable python scripts/setup_github.py --apply --repo OWNER/REPO
```

Apply mode upserts labels, creates only missing milestones, and creates an initial issue only when no issue with the same exact title exists. It never deletes labels, milestones, or issues. Re-run the default mode and inspect GitHub after application.

## Manual checklist

- Confirm the target repository is the intended project, not canonical upstream.
- Confirm all 23 labels and six milestones have the names in the manifests.
- Confirm the six issue forms render and apply their default labels.
- Review the five initial issue drafts; create no duplicate titles.
- Confirm the pull-request template asks for study/claim IDs, commands, tests, run IDs, artifacts, citations, evidence status, upstream impact, and reproducibility.
- Keep canonical upstream read-only. Pages deployment is authorized only through the validated workflow on this repository's `main` branch.
