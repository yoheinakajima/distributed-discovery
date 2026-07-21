# UI polish and branding ExecPlan

## Purpose and intended outcome

Deliver issue #86: a parallel-safe, accessible polish of the generated public
research library. The finished site will use the approved Distributed Discovery
brand hierarchy, one five-item global navigation, progressive technical
disclosure, responsive layouts, and plain-language presentation copy without
changing scientific statements, exact values, evidence boundaries, claims,
runs, study registrations, or paper source.

## Current state

Opened 2026-07-21T22:13:49Z from `origin/main`
`a7b622aabc919238b29d452eb7263a1722cbbfe4` in a dedicated sibling worktree on
branch `site/ui-polish-and-branding`. GitHub reported no open pull requests. The source
site currently renders two always-visible navigation rows, six primary links,
serif body copy, narrow global containers, oversized standard headings, fixed
two/three-column grids, and a seven-column scrolling pipeline.

## Scope

- Audit and document the current navigation, content hierarchy, responsive
  behavior, accessibility, and high-conflict site surfaces.
- Add presentation-only copy, status-label, and shell helpers.
- Redesign the home, Research, Results, Labs, Papers, benchmark, experiment-kit,
  study, claim, evidence, and publication presentations while preserving routes.
- Add responsive design tokens, tables, cards, filters, breadcrumbs, footer
  resources, and optional JavaScript enhancements.
- Add automated and manual QA, screenshots, issue/PR metadata, and deployment
  verification.

## Non-goals

- No scientific research or new study ID.
- No scientific claim, exact-value, theorem, proof, evidence-status, run,
  registry, paper-source, upstream, or data-generation change.
- No new external dependency, font, analytics, account, submission path, or API.

## Assumptions

- `main` and the generated evidence are authoritative.
- An absent open research PR means Phase A and Phase B may share one UI PR,
  subject to a second overlap check before integration and again before merge.
- Static HTML remains the no-JavaScript source of truth; JavaScript only improves
  filtering and disclosures.

## Milestones

1. Baseline safety, build, screenshots, and audit. **Complete.**
2. Branding, copy map, design tokens, and isolated prototype. **Complete.**
3. Presentation modules, shell/navigation, page redesign, and tests. **Active.**
4. Browser, visual, accessibility, and full repository validation.
5. Rebase, PR readiness, CI, merge, Pages, and live-route verification.

## Progress checklist

- [x] Read repository and site operating instructions.
- [x] Inspect local Git and live open pull requests.
- [x] Create issue #86 and dedicated worktree/branch.
- [x] Record initial parallel-safety classification.
- [x] Build the current site and record exact baseline counts.
- [x] Capture required baseline screenshots.
- [x] Complete audit, branding report, copy map, tokens, and prototype.
- [ ] Integrate presentation changes and tests.
- [ ] Capture after screenshots and complete manual QA.
- [ ] Run all requested Make targets and invariant checks.
- [ ] Recheck overlap, rebase, push, open/update PR, and complete remote gates.

## Discoveries and surprises

- 2026-07-21T22:13:56Z: The original checkout is named
  `research/dd014-conditional-attention` but points exactly at current `main` and
  has no changes. A dedicated UI worktree avoids touching that checkout.
- 2026-07-21T22:13:49Z: The GitHub CLI is unauthenticated, but the connected
  GitHub app is available for issue, PR, and workflow operations.
- 2026-07-21T22:13:49Z: Both formerly active attention PRs #82 and #84 are
  already merged; the live open-PR query returned an empty set.
- 2026-07-21T22:16:14Z: `make site` passed with 53 pages, 19 studies, 65
  claims, and 34 passing runs. Thirty-six baseline captures cover nine routes
  at four required viewports; none has document-level overflow.
- 2026-07-21T22:18:09Z: All reviewed generated routes expose two header
  navigation layers. At 390 px the Audience Lab keeps the document width safe,
  but its two table contents are 597 px and 409 px inside a 350 px scroll area
  without a visible continuation cue.
- 2026-07-21T22:18:09Z: The five `site/src/*.html` documents are not consumed by
  the current build; the live page shell and nearly all presentation copy are
  inline in the 1,312-line builder.

## Decision log

- 2026-07-21T22:13:56Z: Proceed with integrated Phase A and Phase B because no
  active research PR overlaps shared site files. Recheck before the first shared
  edit and before merge.
- 2026-07-21T22:13:56Z: Keep the current Python static builder and add small
  presentation helpers; do not rewrite evidence-loading or route generation.
- 2026-07-21T22:18:09Z: Use the green-neutral token direction in the isolated
  prototype. It preserves the established planner/private/market/consensus
  colors while giving the public site a restrained, legible identity.
- 2026-07-21T22:18:09Z: Treat `site/src/*.html` as legacy source examples and
  document their non-live status; do not spend merge budget duplicating the
  generated redesign into unused files.

## Validation strategy

Snapshot route paths, exact generated values, claim count, run manifests, paper
source hashes, and study metadata before implementation; compare after. Extend
site integration tests for navigation, copy/status mapping, accessibility
structure, optional filtering, responsive CSS, routes, fragments, evidence links,
and prohibited content. Run the complete requested Make targets. Render and
inspect the required route set at four viewports in light and dark modes, with
keyboard, mobile menu, no-JavaScript, long-content, and horizontal-overflow
checks.

## Commands and expected observations

- `git fetch origin main --prune`: local and remote main match at `a7b622a`.
- GitHub app open-PR search: zero open PRs.
- `make site`: expected to generate and validate all existing routes without
  creating research runs.
- `make bootstrap && make verify && make papers && make site`: expected final
  repository, paper, and site acceptance with unchanged evidence totals.

## Artifacts produced

- Issue #86.
- `reports/ui-refresh/parallel-safety.md`.
- `reports/ui-refresh/audit.md` and `reports/ui-refresh/branding.md`.
- `reports/ui-refresh/before/` with 36 screenshots and viewport metrics.
- `design/site-refresh/copy-map.yml`, `tokens.css`, and the isolated homepage
  prototype.
- This living ExecPlan.

## Blockers

None at plan creation. Any newly opened research PR that changes the builder,
stylesheet, script, route registry, shared shell, or site tests becomes an
integration blocker until it merges or the overlap is explicitly reconciled.

## Recovery and restart instructions

Open the dedicated worktree, inspect `git status --short --branch`, read this
plan and `reports/ui-refresh/parallel-safety.md`, query open GitHub PRs again,
then resume the first unchecked milestone. Never rerun timestamp-generating
research targets. Preserve `site/dist` only as a rebuildable local artifact.

## Outcome and retrospective

Pending.
