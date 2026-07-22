# DD-021 General Sharing Frontier ExecPlan

## Purpose and intended outcome

Prove the channel-independent adjacent error-contraction criterion and
full-capacity pooled-planner dominance inside the frozen protocol, then
independently classify a bounded exact registry by sharing curve, full-sharing
consensus regime, and recovery budget. Preserve minimal witnesses or bounded
nulls, one immutable primary run, audited claims, and an output-connected
General Sharing Frontier Lab.

## Current state

Clean main `a560bb771a8ccaf92958bde8e72280e2c968825f` had no open pull request;
issue #32 was the sole open settings issue. Issue #146 and branch
`research/dd021-general-sharing-frontier` now own the only substantive lane.
DD-021 is free and registered. No result, run, claim, or paper is created at
this gate. GitHub CLI is unauthenticated; SSH and the connected GitHub app are
available. Three unrelated auxiliary worktrees remain untouched.

## Scope

Uniform priors on `M=3,4,5`; `N=2,3,4`; finite target-symmetric channels;
conditionally independent signal draws; a declared target-equivariant direct
rule; independent uniform direct and pooled tie-breaking; one pooled MAP
action for block size `s=1,...,N`; remaining direct actions; simultaneous
one-hit atomic discovery; and centralized pooled top-`L` action portfolios for
`L=1,...,min(N,M)`.

The registry has 59 channel laws: 12 symmetric noisy-point, 20 noisy
`K`-shortlist, nine guaranteed `K`-shortlist, nine explicit `K`-exclusion, and
nine confidence-augmented point channels. Combined with three agent counts it
has 177 scenarios. The parameter grid uses exact rational uninformative,
`1/2`, `2/3`, `3/4`, and perfect boundaries only where valid for the family.

## Non-goals

No strategic rewards, equilibrium, assignment incentives, post-signal
communication, source dependence, threshold teams, unreliable execution,
private-team optimum, decentralized implementation claim for planner values,
human or real data, benchmark expansion, paper creation, submission, DOI,
release, settings mutation, or canonical-upstream/ActiveGraph mutation.

## Assumptions

Every registered channel is finite and target-symmetric. Direct-rule accuracy
is constant conditional on the target. Source signals and private tie draws are
independent conditional on the target. Pooled MAP ties are uniform, although
MAP accuracy and top-`L` mass are tie-invariant. The direct-private baseline is
the frozen declared rule, not an unrestricted team optimum.

## Milestones

1. **Complete — analytic gate:** literature review, error-contraction proof,
   full-capacity proof, and independent proof audit.
2. **Complete — exact source gate:** channel registry, labeled method,
   histogram/count-state method, independent verifier, corruption suite, CLI,
   and tests.
3. **Complete — pre-run gate:** full validation, clean source commit, push, and
   draft PR.
4. **Complete — evidence gate:** exactly one immutable primary run, method
   certificate, witness search, claim allocation, and separate claim audits.
5. **Complete — public gate:** report, Findings, relationships, reverse links,
   real Lab, no-JavaScript data, browser/accessibility validation, and local
   acceptance.
6. **Active — merge/deploy gate:** ready PR, passing checks, squash merge, issue closure,
   post-merge CI/Pages, live routes, and synchronized main.
7. Editorial gate: one documentation-only branch and PR deciding whether the
   Information Sharing Frontier paper gate passes.

## Progress checklist

- [x] Read governing instructions, required roadmaps/policies, DD-019/DD-020
  studies, source, tests, claims, runs, relation/result registries, and Lab
  architecture.
- [x] Audit Git, worktrees, live main, open issues/PRs, issue #32, and GitHub
  authority; run `gh auth status` once.
- [x] Confirm DD-021 is free; create issue #146 and the sole research branch.
- [x] Freeze the channel grid, method counts, caps, exactness, certificate,
  minimization order, and corruption plan.
- [x] Complete literature review and both proof records.
- [x] Implement and validate both exact methods and independent verifier.
- [x] Freeze committed source, open draft PR, and run once.
- [x] Audit claims and integrate exact public evidence.
- [x] Build and verify the General Sharing Frontier Lab.
- [ ] Merge/deploy the research PR and close issue #146.
- [ ] Complete the separate documentation-only editorial gate.

## Discoveries and surprises

- The user-requested `docs/research-output-architecture.md` does not exist at
  main; the current authoritative documents are `docs/research-governance.md`
  and `docs/publication-architecture.md`, both read before registration.
- The full-capacity proof does not require the planner to observe private tie
  seeds: conditional on a signal profile, the posterior top-`L` set weakly
  dominates the posterior mass of every realized direct-action union of size
  at most `L`; averaging over private tie draws preserves the inequality.
- The exact descriptive theorem phrase had no relevant statistical or
  collective-search hit in the registered search, but “error contraction
  ratio” is generic elsewhere. The proof uses the descriptive label without a
  novelty or naming claim.
- The first exact method-agreement preview corrected the anticipated minimal
  opposite-sign witness: at `M=3,N=2`, the half-accurate noisy point decreases
  while the guaranteed two-shortlist is neutral. The first strict opposite
  signs occur at `M=4,N=2`, with the point step `-1/4` and guaranteed
  two-shortlist step `+1/12`. The `M=3,N=2` pair still gives the minimal
  same-accuracy recovery separation, with budgets two and one.
- No mixed sharing curve appears in the registered 177-scenario grid. This is
  a bounded null only; no arbitrary-channel monotonicity claim follows.
- The corrected dirty-tree preview classified 126 strict-compression, 16
  strict-aggregation, 35 all-neutral, and zero mixed sharing curves. Its
  full-sharing classes were 78 Shared Discovery Paradox, 16 strict consensus
  dominance, 83 boundary, and zero strict no-gain scenarios. Recovery budgets
  were `L*=1` for 51, `L*=2` for 55, `L*=3` for 64, and `L*=4` for seven.
  These numbers remain diagnostics until the clean committed run reproduces
  them.
- The first full pre-run `make verify` exposed one expected-count regression
  after registering the 25th study. Updating the relationship-registry test
  from 24 to 25 restored the focused site suite (`2 passed`) and the site build
  (`73 pages, 25 studies`); no scientific computation was affected.
- Clean commit `3cdbbc40` produced the sole primary run
  `20260722T185924Z_DD-021_3cdbbc40_2fea269a9a`. It passed in 11.232478
  seconds at 27.266 MB, with both methods and all eight corruptions passing.
- The immutable counts match the preview: sharing curves are 126 strict
  compression, 16 strict aggregation, 35 neutral, and zero mixed; full sharing
  has 78 paradox, 16 strict consensus dominance, 83 boundary, and zero strict
  no-gain cases; recovery budgets are 51/55/64/7 at L*=1/2/3/4.
- The in-app browser verified output changes, URL state, reset, exact/percentage
  agreement, one visible table row, and clean logs. Its viewport override did
  not change the reported 1280×720 viewport, so the browser record preserves
  that limitation and assigns narrow-width acceptance to responsive static and
  automated checks rather than inventing screenshots.
- Rebuilding all six accepted papers changed only Three Results provenance,
  because that artifact hashes the full claim ledger. All 14 regenerated pages
  were visually inspected; content and pagination are unchanged.

## Decision log

- `2026-07-22T18:35:46Z`: allocate DD-021 only after clean expected main, an
  empty PR list, a registry ending at DD-020, and settings-only issue #32 were
  confirmed.
- `2026-07-22T18:35:46Z`: use exclusive public regime labels for counting:
  strict compression, strict aggregation, mixed, or all-neutral; and strict
  no-gain, Shared Discovery Paradox, strict consensus dominance, or boundary.
- `2026-07-22T18:35:46Z`: minimize witnesses lexicographically by `M`, `N`,
  signal alphabet size, maximum parameter denominator, then declared family
  description rank and channel ID.
- `2026-07-22T19:22:00Z`: preserve the absent mixed class as a bounded null and
  retain strict predicates for aggregation and no-useful-sharing witnesses so
  perfect or equality boundaries cannot masquerade as strict examples.
- `2026-07-22T19:12:00Z`: allocate DD-C-0097 through DD-C-0103 only after the
  immutable run passed; keep two analytic theorems, four exact bounded
  computational claims, and one bounded negative result separate.

## Validation strategy

Validate channel schema, nonnegative exact probabilities, conditional
normalization, target symmetry, direct-rule equivariance and accuracy,
posterior normalization, conditional-independence composition, both exact
methods, `G_s` identity, adjacent-difference and error-contraction identities,
ratio/sign labels, `V_L` bounds and monotonicity, full-capacity dominance,
recovery definition, regime exclusivity, method agreement, and witness
minimality. Reject altered channel mass, tie weight, `C_s`, `P_N`, `V_L`,
regime, recovery budget, and source checksum.

## Commands and expected observations

- `make bootstrap`: locked environment and repository schemas pass.
- Targeted DD-021 tests: hand cases, boundaries, both methods, witnesses, CLI,
  and all eight corruptions pass without creating a run.
- `make verify`: lint, strict typing, all tests, claims, and manifests pass.
- Primary target: refuses dirty state, writes a new immutable DD-021 run ID,
  and completes within 120 seconds and 1 GB without overwriting.
- `make papers` and `make site`: existing papers plus new study/Lab routes
  validate; no paper is created in the research PR.

## Pre-run resource and certificate audit

- Channel laws: 59.
- `(channel,N)` scenarios: 177.
- Labeled target/signal-profile states: 936,063 aggregate; 55,550 maximum.
- Histogram target/signal-profile states: 117,433 aggregate; 5,000 maximum.
- Runtime estimate/cap: below 30 seconds / 120 seconds.
- Memory estimate/cap: below 256 MB / 1,024 MB.
- Arithmetic: Python `Fraction`; floats only for public display after exact
  classifications.
- Certificate: `dd021-general-sharing-frontier-certificate-v1` containing
  source/config hashes, both method outputs, exact classifications, witness
  keys, proof-audit flags, corruptions, and validation summaries.
- Partial outcomes: none eligible for claim promotion.

## Artifacts produced

Issue #146, draft PR #147, this ExecPlan, complete study records, sole immutable
run, seven separately audited claims, exact registry and witnesses, two
independent enumeration methods, verifier, eight-corruption suite, report,
Findings, relationships, public data, General Sharing Frontier Lab, browser QA,
CLI, and tests. Merge/deploy and the later documentation-only editorial gate
remain; no failed evidence was overwritten.

## Blockers

No scientific or execution blocker. Issue #32 remains unrelated and
authority-blocked. A genuine execution boundary uses the requested hard-session
checkpoint and names the next exact command and file.

## Recovery and restart instructions

Inspect `git status --short --branch`; read this file plus the DD-021
`README.md`, `plan.md`, and `status.yml`; query issue #146 and the active PR;
resume the first unchecked milestone. Never rerun a passing DD-019, DD-020, or
DD-021 primary configuration for freshness.

## Outcome and retrospective

Pending. Completion requires the research merge/deployment and the separate
editorial-gate merge; neither registration nor a preliminary table is enough.
