# GitHub organization setup

The repository currently has no Git remote, so M8 is represented by local configuration and four nonduplicative initial-issue drafts. Nothing in this setup publishes the private repository.

## Review locally

```sh
uv run --no-editable python scripts/setup_github.py
```

The default mode validates and summarizes `.github/labels.yml`, `.github/milestones.yml`, and `.github/initial-issues/*.md`. It does not call GitHub.

## Apply after a private remote is authorized

Prerequisites: install `gh`, authenticate it to the intended private repository, verify the exact `OWNER/REPO`, and review every draft. Then run:

```sh
uv run --no-editable python scripts/setup_github.py --apply --repo OWNER/REPO
```

Apply mode upserts labels, creates only missing milestones, and creates an initial issue only when no issue with the same exact title exists. It never deletes labels, milestones, or issues. Re-run the default mode and inspect GitHub after application.

## Manual checklist

- Confirm the target repository is private and is the intended project, not canonical upstream.
- Confirm all 23 labels and six milestones have the names in the manifests.
- Confirm the six issue forms render and apply their default labels.
- Review the four initial issue drafts; create no duplicate titles.
- Confirm the pull-request template asks for study/claim IDs, commands, tests, run IDs, artifacts, citations, evidence status, upstream impact, and reproducibility.
- Keep canonical upstream read-only and do not enable publication or deployment workflows.
