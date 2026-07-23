# Phase 2 external legibility and methods consolidation

This living ExecPlan follows `.agent/PLANS.md`. It implements issue #165 from
starting commit `60517b4a31be417d078ea0868d30622077af2c0d` on
`docs/phase-2-external-legibility`. The task is editorial, governance,
literature, publication, site, methods, and registration preparation. It is
not a theorem-execution or evidence-producing lane.

## Purpose and fixed boundary

Phase 1 consists of Programs V1--V5, the Information Sharing Frontier,
post-V5 theorem-spine consolidation, and the decentralized-recovery
classical-overlap stop. Phase 2 holds all theorem-family execution. It may
improve legibility and machinery without creating a study, claim, immutable
run, theorem, proof, theorem-family paper, parameter grid, provider call,
model evaluation, external contact, or upstream mutation.

Reliable Discovery remains the next major theorem-family candidate but is
deferred. The next substantive session after this plan must be a new
DiscoveryBench Agents v1 registration session.

## Current state

As of `2026-07-23T05:56:07Z`, M0--M13 and every local pre-merge
acceptance gate are complete. Issue #165 owns the work, draft PR #166 is open,
and the branch remains `docs/phase-2-external-legibility`. The scientific
inventory is unchanged at 110 claims through DD-C-0110, 26 studies through
DD-022, 51 manifests, and 48 passing immutable runs. The branch contains no
DD-023, DD-C-0111, provider call, model evaluation, external contact, Reliable
Discovery registration, or ActiveGraph/upstream mutation. M14 is active only
for commit, push, CI, merge, Pages, live-route acceptance, issue closure, and
main synchronization.

## Scope, non-goals, and assumptions

Scope is the owner-authorized Phase 2 editorial and governance consolidation:
literature transmission, publication hierarchy and status, claim prominence,
the three-result reading path, factual methods, maturity and external-review
preparation, unregistered theorem-gate maps, the DiscoveryBench Agents v1
registration prospectus, and the related static-site presentation.

Non-goals are theorem execution, study registration or execution, claim or run
creation, new scientific conclusions, submission, release, DOI, peer review,
reviewer contact, provider/model calls, cost authorization, private holdout
generation, ActiveGraph integration, or canonical-upstream mutation.

The plan assumes Git files and existing Make/Python workflows remain
authoritative, GitHub Pages deploys only from `main`, and the five preserved
untracked duplicates belong to another context and remain untouched.

## Live start and preservation set

- `origin/main`: `60517b4a31be417d078ea0868d30622077af2c0d`.
- Open substantive PRs at start: none.
- Open issues at start: settings-only #32; Phase 2 issue #165 was then opened.
- Issue #162 is closed at `stop-classical-overlap` and is not reopened.
- Auxiliary worktrees are read-only for this task.
- Five unrelated untracked duplicate files existed before mutation. They must
  never be opened, edited, staged, moved, cleaned, deleted, or normalized:
  - `papers/information-sharing-frontier/paper-audit 2.json`
  - `papers/information-sharing-frontier/visual-qa 2.md`
  - `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`
  - `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`
  - `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`

The machine-readable baseline is
`reports/phase-2/phase-2-before-state.yml`.

## Milestones

- [x] M0: audit live state, freeze invariants, complete the required source
  reading, open issue #165, and record the preservation set.
- [x] M1: encode the Phase 2 directive and reconcile current-facing program
  documentation without rewriting history.
- [x] M2: establish and audit the four-layer publication hierarchy.
- [x] M3: audit the canonical anchor, paper ownership, and companion citations.
- [x] M4: add the literature-family transmission registry, schema, validator,
  tests, and build gate.
- [x] M5: map all claims into a separate editorial-prominence registry and add
  its schema, validator, tests, and audit.
- [x] M6: add the contextual “Start Here — Three Results” reading path.
- [x] M7: complete a bounded editorial pass over all seven project PDFs,
  rebuild twice, audit statements, and inspect every rendered page.
- [x] M8: add a dry factual Phase 1 methods record and audit.
- [x] M9: add separate scientific-readiness and external-validation ledgers.
- [x] M10: prepare economic-theory and AGT reader packets without contacts.
- [x] M11: record three unregistered theorem gates and their permitted stops.
- [x] M12: prepare the DiscoveryBench Agents v1 registration prospectus only.
- [x] M13: align the public site, relations, statuses, and contextual routes.
- [ ] M14: run full local acceptance, ready and merge the PR, verify CI and
  Pages, close #165, and synchronize `main`.

Only one milestone is active at a time. Findings, validation commands, paper
hashes, workflow IDs, and completion evidence will be appended as work
advances.

## Validation contract

Required local acceptance is `git diff --check`, `make bootstrap`, focused
schema/literature/prominence/hierarchy/relations tests, `make verify`,
`make papers` twice with byte comparison, and `make site`. Final checks compare
the baseline and after-state for claims, evidence status, manifests, passing
runs, verified results, studies, upstream pin, paper statement ownership,
routes, public data, Labs, downloads, and the five preserved untracked files.
Browser checks cover keyboard focus, headings, reduced motion, JavaScript-off
fallbacks, console errors, horizontal overflow, internal scrolling, desktop,
and 390-pixel containment.

## Decisions and surprises

- The prior handoff reported four unrelated untracked duplicates. Live
  inspection found five. The additional
  `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml` is included
  in the same preservation set; none of the five has been opened.
- The GitHub CLI has no authenticated account in this environment. That probe
  was made once. Git operations use the existing SSH remote and GitHub issue,
  PR, and workflow mutations use the connected GitHub application.
- The initial implementation placed the theorem-gate and DiscoveryBench
  prospectus reports under `docs/`. Closeout moved them to the exact required
  `reports/roadmap-consolidation/` paths, expanded every required field, and
  updated links and tests without changing scientific content.
- The handoff reported 254 tests. The completed theorem-gate completeness
  regression raises the authoritative collection to 255.
- A direct system-Python focused test attempt could not import `pytest`; this
  was an invocation error, not a repository failure. The pinned
  `PYTHONPATH="$PWD/src" uv run --no-editable pytest ...` invocation passed.
- The first restarted `make verify` stopped because Ruff would reformat the
  new test file. Running the repository formatter changed only that test;
  the complete repeated gate then passed.

## Validation evidence

At `2026-07-23T05:56:07Z`:

- `git diff --check`: passed.
- `make bootstrap`: passed, including 11 required files and the fixture claim
  validator.
- focused Phase 2 editorial and site tests: 8 passed.
- `make verify`: passed; Ruff format/lint passed, MyPy passed for 159 source
  files, all 255 tests passed, all 110 claims and 51 manifests validated, the
  literature audit reported 15 families and 31 paper-citation checks, and the
  prominence audit mapped all 110 claims.
- `make papers` was run twice consecutively. Both builds produced the same
  seven SHA-256 hashes recorded in
  `reports/editorial/phase-2-paper-change-audit.yml`; all 119 pages have
  current visual-QA records.
- `make site`: passed with 79 HTML routes and 26 studies.
- local browser QA at desktop and 390 pixels passed with no console errors or
  page-level overflow, as recorded in
  `reports/site-phase-2-browser-validation.md`.

## Artifacts produced

The canonical directive, publication hierarchy, citation graph, literature
registry/schema/validator, complete prominence registry/schema/validator,
Start Here and Methods routes, seven editorially revised PDFs and their audit
records, methods and maturity records, two reader packets, three unregistered
theorem gates, DiscoveryBench Agents v1 gate/prospectus, and before/after state
snapshots are complete. The principal inventories are
`reports/phase-2/phase-2-before-state.yml` and
`reports/phase-2/phase-2-after-state.yml`.

## Blockers

No substantive blocker remains. The remaining work requires only the
authorized GitHub closeout sequence. Issue #32 is settings-only and is not a
research, editorial, CI, or Pages blocker.

## Recovery and restart instructions

If interrupted before merge, run `git status --short --branch`, verify that
the five preservation-set files remain untracked, inspect PR #166, and resume
M14. Do not stage with `git add .`; stage tracked changes plus the explicit
Phase 2 artifact paths only. After merge, synchronize `main` with
`git pull --ff-only origin main`, verify workflows and live routes, close issue
#165, and leave the preservation set untouched.

## Outcome and retrospective

Pre-merge outcome: Phase 2 is canonical locally, the scientific evidence set
is frozen, all editorial and public artifacts pass local acceptance, and the
next substantive session is explicitly DiscoveryBench Agents v1 registration.
Final merge, workflow, Pages, live-route, and issue-close evidence will be
recorded on PR #166 and issue #165 during M14.
