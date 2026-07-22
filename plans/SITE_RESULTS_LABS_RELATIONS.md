# Findings, Labs, and relationship navigation repair

## Purpose and intended outcome

Repair the public research library so findings do not overlap, every Lab control changes a substantive presentation-layer output, exact values remain available without dominating the interface, and readers can navigate bidirectionally among findings, studies, Labs, papers, benchmark tasks, experiment materials, claims, runs, and public data.

## Current state

Complete at `2026-07-22T18:01:03Z`. PR #144 merged as `be4b380`; issue #143 closed; PR CI run 350, Paper and Site Builds run 72, post-merge CI run 351, and Pages run 76 passed. All 17 required live URLs returned HTTP 200 and the deployed content markers and relation counts matched the validated build.

## Scope

Presentation-layer source, generated public site, presentation registries, tests, and site-repair reports. Preserve every inbound route and the five-item primary navigation.

## Non-goals

No research claim, immutable run, scientific value, theorem statement, evidence status, study source, paper source, manifest, or canonical-upstream change. No timestamp-generating research target.

## Assumptions

Existing immutable/public data are authoritative. Controls may use selects, named buttons, or segmented comparisons when a continuous control is not supported. A Guided Exhibit remains a Lab only when its controls map to substantive output.

## Milestones

1. **Audit (complete):** complete mandatory reads, inventory source/data/relations, build baseline, capture required screenshots, and write route audit.
2. **Findings (complete):** replace append-only Results markup with a thematic registry and normal-flow finding stacks; add overlap/uniqueness/link/overflow tests.
3. **Core Labs (complete):** retire the generic scenario-slider system and rebuild Sequential, Coverage, Mechanisms, Audit, Evidence Acquisition, and Architecture Atlas from verified public data.
4. **Interpretation (complete):** polish Threshold numeric presentation and improve the remaining output-connected Labs without broadening scientific scope.
5. **Relations and navigation (complete):** add and validate the presentation relationship registry, generate public JSON and reverse links, and refine contextual navigation while retaining five global items.
6. **Acceptance (complete):** captured final screenshots, completed browser/accessibility/performance/relationship reports, preserved protected inventories, passed all four Make gates, rebased, merged PR #144 after CI, passed Pages deployment, and verified live routes.

## Progress checklist

- [x] Read repository instructions and the complete user brief.
- [x] Inspect local Git/worktrees/branches/log, connected GitHub PRs, and active-branch changed files.
- [x] Create issue #143 and isolated branch/worktree.
- [x] Record the parallel-safety audit.
- [x] Complete all mandatory audit reads and frozen inventories.
- [x] Build and capture baseline site at four viewports.
- [x] Fix findings architecture and overlap first.
- [x] Rebuild/reclassify the six placeholder Labs.
- [x] Improve Threshold and the remaining output-connected Labs.
- [x] Add validated relations and reverse links.
- [x] Complete final visual, accessibility, performance, and relationship QA.
- [x] Pass `make bootstrap`, `make verify`, `make papers`, and `make site` without research execution.
- [x] Rebase, merge a passing PR, verify Pages and live routes, and close issue #143.

## Discoveries and surprises

- The clean auxiliary UI closeout branch changes documentation and reports only, despite its name.
- The roadmap auxiliary worktree contains unrelated untracked duplicate-suffix files; they remain untouched.
- Baseline browser measurement found seven intersecting finding pairs at every tested width above the 760 px mobile breakpoint and none at 390 px; document overflow is zero at every width.
- The required capture list contains 15 routes, producing 60 baseline screenshots across four viewports.
- The first Atlas build attempt stopped before generation on a nested f-string syntax error; extracting the option rendering into a separate expression fixed it without changing data.
- The first Audit interaction check exposed a presentation-key mismatch (`0` options versus `0.0` row attributes). The failed selection returned “not registered”; normalizing option values to the immutable output representation is the corrective action.
- The first relationship build rejected a DD-001 claim-supported DD-000 run as inconsistent ownership. Runs may legitimately support downstream studies through claims, so validation now requires run existence while retaining strict study/claim ownership checks.
- The first responsive smoke pass found 300 px of Threshold document overflow at 390 px because the phase chart intentionally retained a 40 rem readable plotting width. Constraining overflow to the chart container removed document overflow while keeping the chart horizontally inspectable.
- Browser screenshot capture can stall on a reused tab with large pages. Fresh short-lived tabs made the 60-capture after matrix reliable; viewport overrides must be applied after creating each tab.
- Replacing DD-012's 7,350-row presentation table with local-JSON interaction plus one exact no-JavaScript representative row reduced that page from 2,294,266 bytes/110,426 nodes to 10,689 bytes/293 nodes.
- The first `make verify` attempt stopped at the format check for four changed Python files. Running the repository's Ruff formatter was the complete corrective action; no semantic or evidence file changed.
- The next full `make verify` attempts exposed one unused local, generated-HTML line-length lint, and two missing type annotations/control-flow typing issues. Narrow presentation-builder corrections resolved them; the final gate passes 228 tests, 96 claims, and 49 manifests.

## Decision log

- `2026-07-22T16:39:41Z`: proceed from `8ac0700` because no open PR or shared-site overlap exists; preserve auxiliary worktrees.
- `2026-07-22T16:39:41Z`: treat all work as presentation-only and freeze scientific/paper/run/claim/manifest inventories before implementation.
- `2026-07-22`: replace both the Results content model and CSS first; a CSS-only patch would preserve the duplicate DD-013 entry and chronological append-only failure mode.
- `2026-07-22T17:51:33Z`: accept implementation commit `0881230` after all four Make gates, protected-path diff, open-PR query, and 60-before/60-after evidence-count checks pass.
- `2026-07-22T18:01:03Z`: accept squash merge `be4b380` after PR CI run 350 and Paper and Site Builds run 72 pass; post-merge CI run 351 and Pages run 76 also pass. Verify 17 live URLs at HTTP 200, six live finding stacks with ten findings, zero generic core-Lab placeholders, the DD-012 reverse panel, and all declared relation entity counts.

## Validation strategy

Use static registry/schema tests, interaction tests proving each control changes named output, browser bounding-box and overflow checks at 390×844, 768×1024, 1280×900, and 1440×1000, no-JavaScript and keyboard checks, route/reverse-link validation, numeric formatting tests, frozen protected-inventory/checksum comparisons, and all four repository Make gates.

## Commands and expected observations

- `make bootstrap`: dependencies/install checks pass without creating research evidence.
- `make verify`: all unit/integration/schema/provenance tests pass; no research target runs.
- `make papers`: existing papers rebuild/validate with unchanged source and scientific content.
- `make site`: all routes, internal links, public data, accessibility structure, and site-specific tests pass.

## Artifacts produced

Issue #143; this ExecPlan; the findings and relations registries; six core Lab builders; shared numeric formatting; presentation tests; 60 before and 60 after screenshots; and the audit, parallel-safety, visual-QA, accessibility, performance, and relationship reports in `reports/site-repair/`.

## Blockers

None at plan creation. A later shared-site branch overlap or unavailable GitHub/Pages authority must be recorded rather than bypassed.

## Recovery and restart instructions

No active milestone remains. For a future site continuation, start from `be4b380` or later main, inspect open PRs and worktrees, preserve the protected inventories, and register a new living ExecPlan before substantive work.

## Outcome and retrospective

Presentation implementation, local QA, GitHub acceptance, and live deployment are complete. Ten unique findings render in six normal-flow thematic stacks with zero intersections or document overflow at all four required widths. Six placeholder Labs now expose substantive registered outputs; Threshold uses readable primary values plus exact secondary values and a phase chart. The validated relation graph spans 5 programs, 9 theorem families, 24 studies, 10 findings, 16 Labs, 6 papers, 24 benchmark tasks, 6 experiment modules, 96 claims, 36 claim-linked runs, and 20 public-data routes. PR #144 merged as `be4b380`, issue #143 closed, all required workflows passed, and every required live route returned HTTP 200 with deployed content matching the validated build.
