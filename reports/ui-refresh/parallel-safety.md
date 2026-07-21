# UI refresh parallel-safety report

Recorded 2026-07-21T22:13:56Z for issue #86.

## Baseline and active research state

- Base: `origin/main` at
  `a7b622aabc919238b29d452eb7263a1722cbbfe4`.
- UI branch: `site/ui-polish-and-branding` in a dedicated sibling worktree.
- Live open pull requests: none, according to the connected GitHub app at
  2026-07-21T22:13:49Z.
- Previously active research PRs #82 (DD-012) and #84 (DD-013) are merged into
  the base. There is therefore no active PR changed-file list to overlap.
- The separate local checkout named `research/dd014-conditional-attention` is
  clean and points to the same `a7b622a` commit. It will not be edited.

## File classification

### Safe and additive

- `plans/UI_POLISH_AND_BRANDING.md`
- `reports/ui-refresh/**`
- `design/site-refresh/**`
- New presentation-only Python modules under
  `src/distributed_discovery/site/` before import into the live builder
- New isolated tests that do not alter research evidence expectations

### Shared but low-conflict

- `site/README.md`
- `site/src/README.md`
- Presentation-only documentation and generated-site QA reports

### Shared and high-conflict

- `src/distributed_discovery/site/build.py`
- `site/src/styles.css`
- `site/src/site.js`
- `tests/integration/test_site_build.py`
- Route-registry and shared page-shell logic inside the builder

These files may be integrated only while the live open-PR overlap remains
empty. They require a fresh PR query immediately before editing and before
merge. Research routes, metadata, links, and evidence added by `main` always win
conflict resolution.

### Prohibited

- `studies/**`
- `claims/**`
- `results/**`
- `papers/**`
- canonical upstream contents or patches
- research model, evaluator, verifier, registration, and public-data sources

## Overlap conclusion

No active research pull request currently overlaps the proposed UI scope, so
Phase A and Phase B may proceed in one draft PR. This is a point-in-time finding,
not merge authorization. If a research PR opens against a high-conflict file,
the UI PR remains draft and integration-pending until that research change is
merged and preserved by rebase.

## Recheck protocol

1. Query all open pull requests through the connected GitHub app.
2. List changed filenames for each research PR.
3. Compare them to the high-conflict list above.
4. Fetch `origin/main` and rebase the UI branch.
5. Preserve every new research route, study, claim, run, download, and Lab.
6. Rerun `make bootstrap && make verify && make papers && make site`, refresh
   screenshots, and repeat the open-PR query immediately before merge.

## Integration update

PR #87 merged DD-014 after this report's baseline and changed the shared site
builder, JavaScript, and integration test. The UI branch was rebased onto
`9bc1a61ee688ba9fce3504c646c6fab540358447`. The single semantic conflict was
resolved by retaining the new DD-014 research page, exact generated data,
claims, downloads, JavaScript filter, and Conditional Attention Lab within the
refreshed presentation system.

After integration, `git diff origin/main -- studies claims results papers` is
empty. A clean current-main site build and the UI build share 54 data files;
all 54 have identical SHA-256 hashes. The UI build adds only presentation-facing
`data/canonical.json`. The complete local validation suite and refreshed
responsive capture matrix pass. A final open-PR overlap query is still required
immediately before merge.
