# Site repair parallel-safety audit

Timestamp: `2026-07-22T16:39:41Z`

## Decision

Proceed in the dedicated worktree `/Users/yoheinakajima/Documents/distributed-discovery-site-repair` on branch `site/results-labs-relations`, based on clean `main` commit `8ac0700`. No open pull request or active local research branch changes the shared site implementation. Preserve both auxiliary worktrees and their unrelated state.

## Evidence

- `git status --short --branch` in the primary worktree reported clean `main...origin/main`.
- `git worktree list` reported the primary worktree plus `distributed-discovery-roadmap` on `docs/theorem-roadmap-portfolio` and `distributed-discovery-ui` on `codex/site-ui-polish-closeout`.
- `git branch --all` showed no pre-existing `site/results-labs-relations` branch before creation.
- `git log --oneline --decorate -12` placed local and remote `main` at `8ac0700`.
- The connected GitHub integration returned no open pull requests for `yoheinakajima/distributed-discovery`.
- `git diff --name-status main...docs/theorem-roadmap-portfolio` is documentation/report-only. The roadmap worktree also contains four unrelated untracked files with ` 2` suffixes; they are not touched here.
- `git diff --name-status main...codex/site-ui-polish-closeout` changes only roadmap, plan, and browser-validation documents; it does not change `site/`, the site builders, public data, studies, claims, runs, benchmarks, experiment modules, or papers.
- Issue #143 owns this presentation-only task.

## Conflict boundary

If another branch begins changing shared site files before integration, stop integration, finish isolated audit/components, rebase after that branch merges, and never resolve conflicts by deleting a study, claim, paper, route, run, benchmark task, experiment module, or public data file.

## Protected state

Do not modify either auxiliary worktree. Do not change scientific source, exact values, theorem statements, evidence status, claims, immutable runs, manifests, paper source, or canonical upstream.
