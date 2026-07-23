# Post-V5 theorem-spine consolidation execution plan

Issue #158 and branch `docs/post-v5-theorem-spine-gate` own this single
documentation, editorial-synthesis, and public-surface lane.

## Purpose and intended outcome

Reconcile the completed Program V5 evidence and deployed 26-page Information
Sharing Frontier working paper across current-facing repository records;
organize the established results as a theorem spine; make public relationships
bidirectional; and choose one next-program gate after a bounded literature and
non-overlap audit. The output creates no research evidence.

## Current state

At `2026-07-23T00:00:13Z`, local and remote `main` are
`a04100e2c8ae10936f972f86a6080a913d64195b`. GitHub has no open pull request;
issue #32 is the sole pre-existing open issue; PRs #155, #156, and #157 are
merged; issue #153 is closed. Main CI `29966091467` and Pages `29966091515`
pass. The live root, Program, Research, Findings, Labs, Papers, Information
Sharing Frontier publication, and PDF routes return HTTP 200; the live PDF
SHA-256 is `2f8b68d5a690e6369e4c3236313eb93f060bfbe73ec531903c090f6ec6f8b6a1`.

The primary worktree contains two unrelated untracked duplicate audit files,
`papers/information-sharing-frontier/paper-audit 2.json` and
`papers/information-sharing-frontier/visual-qa 2.md`; they are preserved and
excluded from this lane. Three auxiliary worktrees and the separate
ActiveGraph repository are read-only for this task. ActiveGraph main is
`b1963fc85f53522726532b159ee377f2dba94940`; adoption decision v3 permits only
optional advisory structural auditing and keeps required evidence-audit CI
disabled.

Pre-change scientific and paper invariants:

- 110 claims; claims Git blob `8f262daf3aa43f2505d415988d8eca6f0ecd3a42`.
- 51 manifests, 48 passing; manifest-set SHA-256
  `dc7140a6bd36e931dc96c0e9eacff2fd734d1d0b69aa6848e20603a5ef2e3163`;
  passing-run-list SHA-256
  `0af5fcc5f049b66a53763a6ccd49107c0ffa27033ac2b947a3f8043b32d18442`.
- `results/verified` Git-tree listing SHA-256
  `50d83d4488a33218f949c520bfa0da9c765ed37677aa3900062b158afac64434`.
- 26 registered study directories; sorted-set SHA-256
  `05c09c15029998698127b5ef68fc0e1df86b6951b6e4feb602db60601bee5585`.
- Seven validated project PDFs have SHA-256 values `e096183159f8c016...`,
  `40506068a03e6e7f...`, `9bad1e7aaebd0785...`, `c997bba31c021bd7...`,
  `ee9e27f741d25a95...`, `b38bb30f3ce63889...`, and
  `2f8b68d5a690e636...`; the exact full list is retained in the stale-state
  audit and final validation report.
- 77 generated HTML routes and 23 downloads; canonicalized route-registry
  SHA-256 `a551b68b644f2974d9870f954c93ea2990550892088491640f89ef485f1bc080`;
  download-manifest SHA-256
  `e26726fb092762c5d2e5acc495fce74ae6835fb88ad0bdd7884487487e949584`.
- Canonical upstream is clean and read-only at
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`.

## Scope

1. Audit and classify stale current-facing status and counts.
2. Reconcile current program, publication, roadmap, study, synthesis, and
   handoff authority surfaces.
3. Add `docs/theorem-spine.md` with exact DD-019–DD-022 and
   DD-C-0089–DD-C-0110 ownership.
4. Repair the Program page and public study/finding/Lab/paper/claim/evidence/
   data/synthesis relationships without adding global navigation or a route.
5. Complete a dated primary-source literature/non-overlap audit and one
   machine-readable A/B/C next-program decision.
6. Prove all forbidden scientific and paper artifacts unchanged, validate,
   merge, deploy, and inspect the live result.

## Non-goals

No new study ID (especially DD-023), theorem, proof, claim, immutable run,
experiment, benchmark version, paper, manuscript edit, paper artifact edit,
submission, DOI, release, journal contact, human or real data, settings change,
upstream mutation, or ActiveGraph integration. Do not run DD-019 through
DD-022 targets or `make all`.

## Assumptions

Canonical Git files and existing Make/Python validation remain authoritative.
The paper is a deployed working paper, not submitted, DOI-bearing, released,
accepted, peer reviewed, or novelty-verified. DD-022 is selected-equilibrium,
posterior-only, and provenance-blind; DD-021's top-`L` recovery is centralized.
Historical records remain historical and receive supersession notes only when
needed to prevent current-state confusion.

## Milestones

- **A — complete:** live-state, invariant, and stale-state audit; registration
  commit; push; draft PR.
- **B — complete:** canonical status, publication, roadmap, and handoff
  reconciliation.
- **C — complete:** theorem-spine document with claim/study/paper/evidence
  routing and established/open-arrow distinction.
- **D — complete:** living-synthesis maps and ownership reconciliation.
- **E — complete:** public site and bidirectional relationship repair plus
  focused tests and route audit.
- **F — complete:** dated literature and non-overlap audit using primary or
  stable scholarly sources.
- **G — active:** one A/B/C next-program gate decision, full validation,
  branch workflows, merge, Pages, live QA, issue closure, and main sync.

## Progress checklist

- [x] Verify local Git, worktrees, branches, remote main, open PRs/issues,
  recent merges, workflows, Pages, live routes, and live PDF checksum.
- [x] Complete the mandatory governance, current-state, paper ownership,
  DD-019–DD-022, synthesis, public relationship, and ActiveGraph reads.
- [x] Freeze pre-change scientific, paper, route, download, upstream, and
  external-audit invariants.
- [x] Create issue #158 and the sole branch.
- [x] Classify current-facing stale state, historical evidence, supersession
  needs, and valid future boundaries without bulk replacement.
- [x] Complete and commit Milestone A artifacts as `059b81a`, push, and open
  draft PR #159.
- [x] Complete Milestones B through F sequentially with plan updates.
- [ ] Complete Milestone G and normal-completion acceptance.

## Discoveries and surprises

- The expected main SHA and inventories match exactly, but current main CI and
  Pages have later successful run IDs (`29966091467`, `29966091515`) from the
  PR #157 closeout than the handoff's pre-#157 workflow expectations.
- Current-facing stale state is concentrated in `README.md`, publication and
  roadmap maps, the Program-page builder/test, `site/README.md`, synthesis
  maps/prospectus, `reports/final-handoff.md`, and the DD-021/DD-022 living
  plan/status surfaces. Dated gate/acceptance reports contain valid historical
  counts and must not be bulk-rewritten.
- The ActiveGraph worktree contains many unrelated untracked duplicate files;
  no file there is modified. Its holdout freeze records importer SHA-256
  `b9a0f4409e3aa53072f391f279cf33dbc11041f5755534177368386551ea79df`.

## Decision log

- `2026-07-23T00:00:13Z`: accept the live state because local, SSH remote, and
  connected GitHub state agree at the expected main SHA; preserve all
  unrelated untracked files and auxiliary worktrees.
- `2026-07-23T00:00:13Z`: use issue #158 and the exact owner-specified branch;
  use SSH plus the connected GitHub app because the single permitted
  `gh auth status` check found no authenticated host.
- `2026-07-23T00:00:13Z`: treat all changes as editorial/presentation-only and
  compare forbidden artifacts to the frozen hashes above after every broad
  build and before merge.
- `2026-07-23T00:02:50Z`: mark Milestone A complete only after checkpoint
  commit `059b81a`, SSH push, and draft PR #159. Advance exactly one active
  milestone to B; no scientific or paper artifact entered the diff.
- `2026-07-23T00:31:00Z`: reconcile current-facing Program V5 and paper status,
  add the evidence-linked theorem spine, and extend synthesis ownership through
  DD-022. Select Outcome A only after the literature refresh identifies the
  direct planner/selection objection and the severe classical congestion/search
  overlap risk; the future registration must permit an overlap-failure stop.
- `2026-07-23T00:47:00Z`: focused relationship tests pass (`2 passed`) and
  `make site` preserves 77 routes, 26 studies, 110 claims, 48 passing runs, and
  seven publications. Advance the sole active milestone to G for broad
  validation, invariant comparison, workflows, merge, deployment, and live QA.

## Validation strategy

Run focused YAML/JSON parsing and theorem-spine/roadmap/publication/
relationship tests before full `git diff --check`, `make bootstrap`, `make
verify`, `make papers`, and `make site`. Validate claims and every manifest;
compare `results/verified`, study set, PDF hashes/page counts, upstream pin,
route and download registries; run secret/private-key and `/Users/` scans;
validate internal links/fragments, reverse relationships, downloads,
no-tracking/no-remote-runtime, accessibility, console logs, keyboard focus, and
desktop/390-pixel width containment. Use the build-paper workflow for paper
provenance and rendered-artifact validation without changing the paper.

## Commands and expected observations

- `git diff --check`: no whitespace errors.
- `make bootstrap`: locked environment and schemas pass.
- Focused tests: stale-status assertions are replaced by deployed-paper,
  selected-equilibrium, centralized-authority, theorem-spine, and reverse-link
  assertions.
- `make verify`: scientific counts remain 110 claims and 51 manifests; tests
  may increase only for scoped documentation/site regressions.
- `make papers`: seven project papers remain 115 total pages; the Information
  Sharing Frontier remains 26 pages at the frozen hash.
- `make site`: 77 routes, 26 studies, 85 public data files, 18 Labs, and 23
  downloads remain unless a legitimate presentation-only registry correction
  changes a generated count and is explained.

## Artifacts produced

Issue #158; draft PR #159; checkpoint commit `059b81a`; this ExecPlan; and
`reports/roadmap-consolidation/post-v5-stale-state-audit.md`. Further artifacts
are appended after creation.

## Blockers

None. Settings issue #32 is separate. CLI authentication is unavailable but
SSH and the GitHub app cover the authorized workflow.

## Recovery and restart instructions

Run `git status --short --branch`, read this plan, inspect issue #158 and the
draft PR once created, and resume the sole active milestone. Never touch the
two untracked duplicate paper-audit files, auxiliary worktrees, ActiveGraph,
paper artifacts, claims, or immutable runs. Never execute DD-019–DD-022 study
targets.

## Outcome and retrospective

Pending. Completion requires squash merge, passing post-merge CI and Pages,
live route/relationship/mobile/desktop/PDF verification, issue closure, and a
synchronized local `main`.
