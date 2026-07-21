# Master execution plan

> The M0–M9 and A–E material below is retained as historical execution evidence. Current operational state and the active continuation queue are recorded in the opening sections, blockers, and recovery instructions; stale no-remote/private statements inside completed-milestone history describe the state at that time.

## Purpose and intended outcome

Bootstrap and execute a durable, auditable research program for Distributed Discovery while preserving the Shared Discovery Paradox repository as the canonical, read-only public presentation.

## Current state

### Program V2 completion queue (active, 2026-07-21)

Owner authorization now requires sequential completion of DD-010 DiscoveryBench,
DD-011 Experimental Design and Power, the DD-008B Common-Source analytic gate,
a focused *Common-Source Trap* working paper, public benchmark/experiment Labs,
and a final Program V2 handoff. The live baseline is clean `main`
`9b2096ddcf17585cda84ecc00b6606ef15d791b6`; CI `29852900771` and Pages
`29852901101` passed, sampled public routes return HTTP 200, and no pull request
is open. The only settings blocker remains issue #32; the previously required
single `gh auth status` probe was already exhausted and is not repeated.

The active milestone is DD-010. Its golden registry is capped at 15 tasks and
the built-in protocol registry at 13 declared protocols; compatibility is
computed from explicit capabilities rather than by exposing evaluator state.
The exact primary suite must use immutable task views, exact fractions, a
separate verifier, task-value and information-boundary corruption tests, and a
60-second/1-GB cap. Simulated extensions, if included, are bounded, seeded,
confidence-interval results and are never promoted to exact claims. Subsequent
milestones become active only after the prior issue/PR/CI/Pages/live-route gate
passes.

Progress:

- [x] DD-010 issue, registration, schema, capability boundary, golden tasks,
  protocols, metrics, CLI, exact run, verifier, claim audit, site, merge, CI,
  Pages, and live routes. Local evidence and acceptance are complete in primary
  run `20260721T183014Z_DD-010_ce930050_8ec718c242`; PR/CI/Pages gates remain.
- [ ] DD-011 issue, bounded design, literature record, hypotheses/estimands,
  randomization, synthetic power run, verifier, materials, ethics boundary,
  site, merge, CI, Pages, and live routes.
- [ ] DD-008B analytic gate with exact finite/formula agreement and an honest
  theorem, counterexample, conjecture, or documented barrier outcome.
- [ ] Focused Common-Source Trap paper with source-generated figures/tables,
  deterministic PDF, citation audit, all-page Poppler review, merge, and Pages.
- [ ] Program V2 site/Lab integration and final acceptance/handoff.

Recovery: inspect `git status --short --branch`; resume the sole active milestone
from its study `plan.md`; never rerun an already preserved primary run. If DD-010
has not yet produced its immutable run, the exact next command is
`make dd010-discoverybench`; otherwise use its manifest verifier before any
claim promotion.

### Program V2 baseline (active, 2026-07-21)

DD-008A is merged and deployed through PR #61. Clean primary run
`20260721T163030Z_DD-008A_8b70668b_06307caab4` evaluates the registered
N=2 through 8 rational grid with exact binomial accounting and a direct
target/source-signal enumerator. DD-C-0052 is independently reproduced. Local
acceptance passed and its post-merge CI/Pages gates completed.

DD-006B primary run `20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b` exhausts
60 normalized joint-mechanism rows and 57,600 exact joint deviations. It finds
16 strict rows, maximum all-tie margin `13/72`, truthful differentiated
discovery `11/12`, and no weak target-visible/action-hidden row. A separate
exact evaluator reproduces incentive and accounting certificates. Local
integration passed through PR #63, post-merge CI, Pages, and live route checks.

DD-006B merged and deployed through PR #63 as `c4524e7e`. DD-009 primary run
`20260721T171249Z_DD-009_bc78d249_0c3851c41a` classifies all 288 Cartesian
cells, evaluates 20 coherent architectures, independently reproduces every row,
and yields 12 nondominated cells under the declared six objectives. DD-C-0054
is independently reproduced. DD-009 merged and deployed through PR #65 as
`fc273e94`; post-merge CI `29852583292`, Pages `29852583377`, and all Atlas
route checks passed.

Program V1 is complete through DD-008. The authoritative concise entry points
are `docs/current-state.md` and `docs/current-roadmap.md`. Reconciliation at
`ae8b52c098d358afc63948b7a54d2245cafd7438` found 51 claims (24 independently
reproduced, 13 verified, 7 derived, 3 checked, 3 sourced, 1 proposed), 21
passing immutable runs among 24 manifests, 68 Python sources, 26 public HTML
routes, 15 public data files, six Labs routes, three project-authored papers,
and 111 tests. CI and Pages succeeded and public root, Labs, and publications
returned HTTP 200. DD-007 is synthetic-only; issue #32 remains settings-only.

The active sequence is: DD-008A N-agent endogenous evidence acquisition,
DD-006B joint truthful discovery mechanisms, DD-009 bounded Architecture Atlas,
DD-010 DiscoveryBench, DD-011 synthetic experimental design, then a focused
paper and deeper public labs. No real-data work, external model calls,
recruitment, or intervention is authorized. Milestone A is documentation and
registration only; it must not create timestamped research runs.

### Institutional-theory continuation (current, 2026-07-21)

**Completed continuation addendum (2026-07-21).** T is merged through PR #47;
U/DD-006A through PR #49; V/DD-008 through PR #51; W, the validated
*Institutions for Distributed Discovery* synthesis, through PR #54; and X, the
public Labs surface, through PR #56. `main` is
`401258f245ea50fcda5be2c61f78603b3c71e2de`. The current program has 51 claims,
21 passing immutable runs among 24 manifests, three project-authored papers,
and 26 generated public HTML routes. DD-006A is restricted to its registered
normalized linear transfer class; DD-007 remains synthetic-only; DD-008 is an
exact synthetic source-choice fixture. Pages deployment and route validation are
the final operational checks for this addendum; issue #32 remains settings-only.

`main` is `29c37e347a4cbc74a84cd3a23e4105789f7309e9` after PR #45. The prior
N–S queue is complete: research-library PR #36, DD-004 PR #38, DD-005 PR #40,
DD-006 PR #42, DD-007 PR #43, and integration PR #45 are merged. The live
ledger has 49 claims (23 independently reproduced, 12 verified, 7 derived, 3
checked, 3 sourced, and 1 proposed), 21 manifests of which 19 are passing,
60 Python source files, 19 public HTML routes, 13 generated data files, and
two project-authored papers. DD-007 remains synthetic-only. Settings issue #32
remains operational-only because the one required `gh auth status` check found
no authenticated CLI session; no settings mutation is authorized in this state.

The completed sequence was T handoff reconciliation (issue #46), U DD-006A general
transfer frontier, V DD-008 endogenous evidence acquisition, W Discovery Stack
synthesis paper, X interactive labs, then the institutional-program handoff.
Each research milestone requires a bounded registration, immutable evidence,
independent verification, calibrated claims, CI, merge, and Pages validation.

### Historical state

The historical M0–M9 bootstrap, operational Milestone A, research milestones DD-001A/B, bounded DD-002/DD-003, their integrated handoff, and continuation cycles F–M are complete. PR #34 merged as `a3b1f760ff6b4d3d580696e537e5d3f45caf1ed3`; its source checkout is clean on `main`. Claims stop at DD-C-0044; the ledger has 44 claims and 17 immutable manifests. The one authorized settings attempt failed before mutation because GitHub CLI is unauthenticated and is recorded in issue #32. The start-of-phase `gh auth status` check on 2026-07-20 again found no usable CLI session; no settings mutation or retry is authorized.

**Active program phase — research library and bounded extensions.** The next sequence is: (N) build and deploy the public research library; (O) execute/verify DD-004 sequential perfect-elimination baseline; (P) execute/verify DD-005 overlapping-coverage frontiers; (Q) execute/verify a newly registered DD-006 reporting-and-reward fixture; (R) execute/verify DD-007 synthetic audit schema, recovery grid, and identification counterexamples; and (S) integrate the resulting program materials. Each phase requires a bounded issue, coherent branch/PR, immutable evidence, independent check where applicable, claim audit, CI, merge, Pages deployment, and live-route validation.

N completed through merged PR #36 (`1b6f923`) and a successful Pages deployment. O primary run `20260721T050038Z_DD-004_8ab02e7f_71d84de7c4` completed in 0.06 seconds under its 30-second bound: its exact DP and independent tiny policy-path enumerator agree, and terminal discovery is schedule-invariant in the registered perfect-elimination fixtures while expected actions/rounds differ.

## Scope

Completed M0–M9 and A–E evidence, followed by F exact canonical pooled-frontier certificate; G separate Three Results synthesis paper and public Results page; H alignment-preserving DD-001 upper relaxation; I DD-002 equilibrium-selection robustness; J DD-003 heterogeneous source accuracy; K dependency maintenance; L one repository-settings attempt; and M final integration and handoff. Active scope is N–S: research-library site overhaul; exact bounded DD-004 through DD-006 studies; synthetic-only DD-007 audit research; and program integration. Canonical upstream remains read-only.

## Non-goals

Changing canonical upstream, publishing a release or DOI, adding telemetry, making real-organization claims from DD-007 synthetic data, asserting novelty before literature review, or presenting exploratory computations as verified. Public source and Pages deployment are explicitly authorized.

## Assumptions

- Canonical upstream is fetched only into `.cache/upstream/` and pinned before use.
- Python 3.11+ and `uv` provide the primary reproducible environment.
- Missing external credentials or paper toolchains are documented, not bypassed.

## Milestones

- M0 bootstrap: completed 2026-07-20.
- M1 pin and reproduce canonical upstream: completed 2026-07-20.
- M2 formalize foundations: completed 2026-07-20.
- M3 additive paper extensions: completed 2026-07-20.
- M4 private companion site: completed 2026-07-20.
- M5 foundations note: completed 2026-07-20.
- M6 DD-001 initial research: completed 2026-07-20.
- M7 later-study briefs: completed 2026-07-20.
- M8 GitHub organization: completed 2026-07-20.
- M9 integration and handoff: completed 2026-07-20.
- A public/MIT/Pages/GitHub cleanup: completed 2026-07-20.
- B DD-001A policy-signature reduction and certification barrier: completed 2026-07-20.
- C DD-001B two-agent hybrid thresholds: completed 2026-07-20.
- D DD-002 bounded disclosure fixture: completed 2026-07-20.
- E DD-003 bounded source-graph fixture: completed 2026-07-20.
- Integrated A–E handoff: completed 2026-07-20 through PR #17.
- F exact canonical pooled-frontier certificate: completed 2026-07-20 through PR #19.
- G Three Results synthesis paper and public Results page: completed 2026-07-20 through PR #21.
- H alignment-preserving DD-001 upper relaxation: completed 2026-07-20 through PR #23.
- I DD-002 equilibrium-selection robustness: completed 2026-07-20 through PR #25.
- J DD-003 heterogeneous source accuracy: completed 2026-07-20 through PR #27.
- K dependency and Dependabot maintenance: completed 2026-07-20 through PRs #29–#31.
- L single repository-settings attempt: completed 2026-07-20; blocked outcome recorded in issue #32 without retry.
- M continuation integration and handoff: local acceptance complete; documentation PR integration active.

## Progress checklist

- [x] Inspected filesystem and Git state.
- [x] Created safe working branch.
- [x] Completed and validated M0 architecture, policies, skills, package, schemas, templates, and registry.
- [x] Committed M0 as `32dd1c3`.
- [x] Pinned and inspected canonical upstream commit `5025cc8e`.
- [x] Executed the actual upstream verifier with an immutable passing run.
- [x] Independently reproduced blind, private, private-distinct, consensus, planner, and recovery-budget quantities.
- [x] Committed M1 as `dd7f0c6`.
- [x] Formalized the general object, architecture, frontier/loss identity, quantities, institutional matrix, canonical mapping, and pipeline.
- [x] Completed an orientation literature/terminology review with verified metadata and recorded novelty risks.
- [x] Committed M2 as `e1192de`.
- [x] Prepared an additive upstream paper extension, review patch, generator/validator, compiled preview, and visual QA record.
- [x] Built and validated the private companion site extension from generated benchmark and registry data.
- [x] Built and visually validated the 12-page foundations companion note.
- [x] Specified, implemented, executed, independently checked, and reported the initial DD-001 study.
- [x] Upgrade DD-002 through DD-007 into serious executable research briefs without starting the studies.
- [x] Prepare complete local GitHub taxonomy, templates, initial issue drafts, and a guarded setup helper without publishing.
- [x] Run the full acceptance sequence and produce a fresh-checkout handoff.
- [x] Inspect live public repository, Actions, Pages, labels, milestones, issues, PRs, and rulesets.
- [x] Create cleanup issue #6 and branch `chore/public-mit-pages-cleanup` from current `main`.
- [x] Reconcile MIT licensing and current public/Pages wording.
- [x] Create all five prepared live issues; record the settings-capability blocker for labels, milestones, homepage, and safe `main` protection.
- [x] Merge cleanup PR #12 after passing CI and verify live Pages workflow `29781940577` plus all five routes.
- [x] Prove the lossless signature objective identity and exact residual Hall feasibility theorem.
- [x] Implement independent matching/reference and closed-form/scaled signature evaluators with reconstruction and corruption tests.
- [x] Run the bounded DD-001A primary audit; reproduce all 21 tiny optima and raw tie counts; certify the canonical signature state-space counts.
- [x] Add DD-C-0023 through DD-C-0025 with proof/check records and calibrated evidence statuses.
- [x] Merge DD-001A PR #13 after CI and verify Pages run `29784048496`.
- [x] Derive the exact territorial/hybrid/direct threshold theorem for every M at least 3 within the declared families.
- [x] Certify the continuous unrestricted informative envelope for M=3,4,5 across 438,734 exact signature polynomials.
- [x] Reproduce all four known witnesses and refute the unrestricted all-p extension with exact anti-informative counterexamples.
- [x] Merge DD-001B PR #14 after CI and verify live Pages.
- [x] Execute and independently verify the bounded DD-002 deterministic-disclosure fixture.
- [x] Merge DD-002 PR #15 after CI and verify live Pages.
- [x] Execute and independently verify DD-003 on issue #10 and branch `research/dd003-source-graphs`.
- [x] Merge DD-003 PR #16 after CI and verify live Pages.
- [x] Complete broad final acceptance without creating duplicate immutable runs.
- [x] Merge documentation-only integrated handoff PR #17 after CI and verify final Pages.
- [x] Certify the exact canonical pooled frontier for budgets 1–8 by independent labeled-count and histogram/orbit evaluators, probability-mass checks, and corruption testing.
- [x] Replace the numerical DD-001 planner benchmark with an exact certified endpoint while preserving the unresolved private-team optimum.
- [x] Build and visually audit a separate 12–20 page Three Results paper and add a fifth public Results route with generated provenance.
- [x] Implement and audit an alignment-preserving DD-001 upper relaxation; its canonical upper bound equals the direct lower bound and closes the frozen zero-communication optimum.
- [x] Audit the DD-002 witness and all 45 refinements under six declared equilibrium-selection procedures; merged and deployed through PR #25.
- [x] Enumerate the bounded DD-003 colored-source class for a rational heterogeneous-accuracy palette, independently verify its exact counterexample, and merge/deploy PR #27.
- [x] Reconcile Dependabot PRs #1–#5 in separate Actions, low-risk Python, and mypy-2 maintenance branches; update grouping policy.
- [x] Make exactly one settings-capable attempt for repository taxonomy/homepage/protection and record the precise capability result in issue #32.
- [x] Complete broad continuation acceptance without creating duplicate immutable research runs; 95 tests, 44 claims, 17 manifests, both papers, the site, and eleven live routes pass.
- [ ] Review, merge, and deploy the documentation-only Cycle M handoff PR; close issue #33.
- [x] Verify that PR #34 merged as `a3b1f76` and record the unchanged settings-auth blocker without retry.
- [x] Register issue #35 and build the N research-library source, public metadata contract, route registry, safe evidence/download indexes, automated checks, and bounded browser validation on `site/research-library`.

## Discoveries and surprises

- 2026-07-20: host `python3` is 3.9.6; `uv` is available. The project will declare Python >=3.11 and use the locked `uv` environment.
- 2026-07-20: no LaTeX executable was found during the initial inspection; paper validation may require a lightweight fallback or a documented toolchain blocker.
- 2026-07-20: the skill validator failed under host Python because PyYAML was absent, then passed for all four skills under `uv run`.
- 2026-07-20: initial claim validation exposed PyYAML's implicit conversion of unquoted ISO dates to `date` objects; claim dates are now quoted at the serialization boundary. Initial mypy also required the package `py.typed` marker. Both failures were retained here and corrected before commit.
- 2026-07-20: the first M1 execution attempt failed before research computation because Hatchling's editable `.pth` lacked a terminating newline and was ignored by this Python installation. The Make interface now consistently uses `uv --no-editable`; this installs the locked wheel and restores imports without mutating generated environment files.
- 2026-07-20: two upstream verifier executions completed successfully but their wrappers failed after validation while invoking `python -m pip freeze` in a minimal `uv` environment. The source fix did not reach the second run because the non-editable local wheel was stale. Both operational failures are preserved and excluded from claim evidence. Make now places `src/` first on `PYTHONPATH`, while still using locked non-editable dependencies, so research runners always execute current tracked source.
- 2026-07-20: the canonical upstream is MIT-licensed and its current `main` commit is `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`. The verifier, LaTeX paper, bibliography, static site, data, and figures are all present; upstream remains read-only in ignored cache.
- 2026-07-20: evidence run `20260720T190336Z_DD-000_32dd1c32_217c602fa0` passed every upstream assertion, all rounded sanity checks, and independent consensus/planner/private/blind checks. The upstream market and crossover remain verified but not independently reproduced.
- 2026-07-20: “Distributed Discovery” has material terminology collisions, including arXiv:2603.14312 (March 2026) and older resource/service/news-discovery uses. DD-C-0017 records the negative novelty result. Project text now uses an explicit working definition and makes no unique-field/name claim.
- 2026-07-20: team theory directly anticipates DD-001’s decentralized common-payoff policy object; Bayesian persuasion and informational Braess work directly neighbor DD-002. This changes claim calibration, not the registered research questions.
- 2026-07-20: Homebrew supplied Tectonic 0.16.9 after no LaTeX compiler was present. A first compile from repository root failed because Tectonic resolved the upstream `figures/` path relative to the manuscript; a second failed because the requested output directory did not yet exist. Both were operational validation failures. The validator now stages figures only in a disposable worktree, creates its output directory, and leaves canonical upstream clean.
- 2026-07-20: setting `SOURCE_DATE_EPOCH` to the pinned upstream commit timestamp made two consecutive patched-paper builds byte-identical (`0a43360e...`). Full-page rendering and targeted visual inspection found no defects in the additive material.
- 2026-07-20: the pinned upstream guide is a single dependency-free HTML document under MIT license. M4 therefore uses static HTML/CSS, mirrors its typography and color roles, and keeps the canonical public guide as the first link rather than copying or redesigning the interactive sequence.
- 2026-07-20: the first M5 compile exposed an `amsthm`/font-package order conflict, resolved by matching the validated upstream order. The first complete manuscript was 10 pages; substantive additions on feasible protocol classes, admissible comparisons, evidence discipline, and audit design brought it to the requested 12-page minimum without filler.
- 2026-07-20: the paper-specific bibliography omits the canonical entry's long repository URL and abbreviates its pinned commit in print because plainnat produced poor line breaks. The source bibliography and generated provenance retain the full authoritative metadata.
- 2026-07-20: DD-001 agent symmetry reduces exhaustive profiles from `(M^M)^N` to multisets `C(M^M+N-1,N)`. The largest configured search is 32,896 profiles per accuracy; the canonical space remains intentionally unenumerated.
- 2026-07-20: an initial 17-point exact grid was expanded after a bounded audit found informative `N<M` hybrid gains. Three passing runs are preserved; `20260720T200447Z_DD-001_6eb12861_ba766d1eba` is primary because it contains the final 21 points and generated phase figure.
- 2026-07-20: direct clue-following is not generally private-team optimal. At `(M,N,p)=(3,2,2/5)`, exhaustive rational enumeration gives `7/10` versus direct `16/25`. By contrast, 18 canonical coordinate-ascent starts all end at direct value `325089/390625`; this is a lower-bound search observation, not proof of global optimality.
- 2026-07-20: DD-002 through DD-007 can each begin with a bounded exact or seeded synthetic experiment. The briefs make equilibrium selection, latent-source provenance, stopping objectives, overlap assumptions, mechanism observability, and empirical identification explicit before implementation.
- 2026-07-20: the M9 security scan found a local checkout URL in three DD-001 `uv pip freeze` snapshots. The local-project line was redundant with the committed source/lock and was removed; future snapshots filter it. No credential- or token-shaped secret was found.
- 2026-07-20: the clean M8 acceptance run `20260720T202314Z_DD-000_88613408_217c602fa0` passed the pinned verifier and all independent checks. The rebuilt foundations PDF is 12 pages; the additive patched preview is 30 pages and still applies to pristine upstream.
- 2026-07-20: the final staged whitespace audit flagged CRLF endings in upstream-generated CSV evidence as trailing whitespace. Those bytes are covered by the run's output hashes, so the immutable CSVs were preserved and the authored-file whitespace audit was run with that generated output directory excluded.
- 2026-07-20: live `main` advanced to `21bbd5d` with an owner-authored Pages workflow. Run `29779923504` passed, and all five required Pages routes returned HTTP 200. The repository had only 12 default/Dependabot labels, no milestones, no research issues, no rulesets, and five open Dependabot PRs.
- 2026-07-20: GitHub CLI 2.96.0 was installed, but no CLI OAuth session exists. The connected GitHub app has owner/admin access and can manage issues/PRs; SSH handles Git. CLI-only settings will use an authenticated browser or record a capability-specific blocker.
- 2026-07-20: all five prepared issue drafts were applied without duplicates: DD-002 #7, queued DD-007 #8, DD-001A #9, DD-003 #10, and DD-001B #11. Their intended taxonomy is retained in each issue body until settings-capable authentication can create the declared labels and milestones.
- 2026-07-20: `make bootstrap`, `make verify`, `make site`, and `make papers` pass on the cleanup branch; 29 tests, 7 run manifests, 4 site pages, and the 12-page foundations artifact validate. A later post-commit rebuild exposed that the paper's timestamp depended on `HEAD`; this is superseded by the immutable-run epoch fix below.
- 2026-07-20: cleanup PR #12's first artifact run `29781538938` failed after Tectonic installed successfully because Ubuntu lacked the paper validator's `pdfinfo` executable. The artifact workflow now installs `poppler-utils`; the failed run remains linked evidence and is not represented as passing.
- 2026-07-20: the foundations builder formerly derived `SOURCE_DATE_EPOCH` from `HEAD`, so every commit changed the tracked PDF and made the next build dirty. It now uses the immutable passing canonical run's timezone-qualified `started_utc`, records that epoch in generated provenance and validation, tests the conversion independently of Git history, and normalizes Tectonic's parallel `Writing` log lines.
- 2026-07-20: preliminary DD-001A run `20260720T220911Z_DD-001_6822d4c6_40bf5b06a5` passed the computational reduction audit, but claim review found its `certified_interval` output key too strong for the evidence packaged in that run: the pooled endpoint was numerical and the emulation chain was not audited as part of the certificate. The run remains immutable and valid as a preliminary audit; presentation was corrected before the primary run. The later exact-frontier run and DD-C-0019 re-audit separately establish the interval.
- 2026-07-20: primary DD-001A run `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5` started from clean commit `b1d8d431` and passed in 13.73 seconds. It independently reproduced all 21 exact tiny optima and raw-policy multiset tie counts, matched matching/reference and closed-form feasibility through M=5, reconstructed all audited signatures, and passed the independent structural certificate verifier.
- 2026-07-20: the signature theorem reduces each policy losslessly to targetwise incoming counts and fixed-point indicators. At canonical M=16, exact counts are 148,348,284,928 feasible labeled signatures and 5,806 individual target orbits, but independently quotienting agents loses relative target alignment. The eight-agent multiset count before a global target quotient has 85 digits, so the declared naive enumeration exceeds its resource budget. This is not a private-team objective upper bound.
- 2026-07-20: DD-001B primary run `20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1` passed in 35.86 seconds. It proves the exact three-family thresholds \(1/M\) and \(1/(M-1)\), exhaustively certifies the unrestricted continuous informative envelope for M=3,4,5, and records p=0 counterexamples that refute an all-p extension.
- 2026-07-20: DD-002 primary run `20260720T225848Z_DD-002_94607423_e29b1460ae` enumerated all 15 deterministic disclosure policies, 37 posterior games, 256 global pure-equilibrium selections, and 45 strict refinement pairs. Exactly one refinement lowers the declared anonymous-symmetric selection, while every pure equilibrium and the planner improve for that witness; the reversal is selection-dependent.
- 2026-07-20: DD-003 primary run `20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1` enumerated 51 nonisomorphic source graphs, independently reproducing the 1/8/42 orbit counts. Ten full pairwise-moment signatures each match two graphs with identical discovery, a complete bounded null. Mean agreement alone is insufficient: two graphs match at 3/4 but have discovery 8/9 and 31/36.
- 2026-07-20: DD-003 PR #16 passed CI `29787235590` and artifact run `29787235603`, then squash-merged as `54b8713fa7f3b30922a88b60a6dc280319432715`. Post-merge CI `29787309515` and Pages `29787309537` passed; the deployed DD-002/DD-003 completion statuses and all five routes were verified live.
- 2026-07-20: integrated handoff PR #17 passed validation and squash-merged as `b72c01026be5bf7018b3a3e9a464671dce53bcbb`. Post-merge CI `29787687400` and Pages `29787687403` passed. The next program begins from this clean public baseline.
- 2026-07-20: the continuation audit found that DD-C-0006's planner frontier is independently enumerated but stored as decimals. Cycle F therefore requires exact rational artifacts and agreement between a labeled count-vector evaluator over all `C(23,15)=490314` vectors and a separately derived false-count-histogram/orbit evaluator before the exact endpoint can support the private-team interval.
- 2026-07-21: primary exact-frontier run `20260721T012208Z_DD-000_8e4b55e2_e8321d1048` started clean at commit `8e4b55e2`, completed in 8.29 seconds under a 30-second budget, and passed. The 490,314-state labeled evaluator, 67-orbit histogram evaluator, and third partition verifier agree at all budgets with exact unit mass; the verifier rejects a one-unit numerator corruption.
- 2026-07-21: re-audit of the pooled emulation chain establishes the exact valid interval `325089/390625 <= T_8(16,1/5) <= 860391662035297/1001129150390625`, gap `27224111644672/1001129150390625`. The upper endpoint remains unattained and global tightness remains unresolved.
- 2026-07-21: the first ad hoc targeted pytest invocation omitted the Makefile's `PYTHONPATH=src` and stopped during import collection. The identical targeted set passed 12 tests after using the repository execution environment; the immutable primary run and its evidence were unaffected.
- 2026-07-21: exact-frontier PR #19 passed CI `29793343243` and artifact build `29793343234`, received a complete no-findings review, and squash-merged as `8d63201cb3b6633c873494af2ea21402db8752d6`. Post-merge CI `29793437945` and Pages `29793437954` passed; all four current HTML routes, CSS, and deployed claim data returned HTTP 200 with the exact interval.
- 2026-07-21: the first Results-site build stopped with a missing `csv` import after the builder began reading exact role data. Adding the import fixed the operational error; the final builder checksum-validates four immutable source runs and emits exactly five pages plus `data/results.json`.
- 2026-07-21: the first Three Results compile rejected underscores in a generated monospaced provenance path. Replacing that field with a breakable `\path{}` fixed the source error. The first visual pass then exposed cramped tables, overlapping role labels, and poor long-URL justification; all were revised before the final all-page review.
- 2026-07-21: a layout-only rebuild exposed that the synthesis builder's two PDF comparisons shared TeX auxiliary state. The builder now uses two isolated clean compilation directories, normalizes their paths, retains failing logs, and certifies the final 12-page PDF byte-for-byte at SHA-256 `38128dbbb1f531b8ad95151c0ccd4f00b54c04eb8afa1c11ca73f24e5c26b92f`.
- 2026-07-21: targeted tests initially exercised a stale non-editable local wheel, and the first repository-wide lint/typecheck attempts found one unformatted test and an overly broad inferred provenance value type. Reinstalling the local wheel for the targeted check, formatting, and binding the source epoch as a string resolved these operational failures. Final acceptance passes 72 tests, strict mypy, Ruff, claim/run validation, both 12-page papers, and the five-page site.
- 2026-07-21: PR #21 artifact run `29794725150` compiled both clean Three Results PDFs on Ubuntu but failed because the builder also required identical compiler logs. The first clean Tectonic invocation can populate its package cache, so log equality is environment-state equality rather than artifact determinism. The gate now requires identical PDF bytes, validates both logs separately for fatal/reference/citation/overfull failures, stores the second warm-cache log, and records normalized log equality as diagnostic metadata.
- 2026-07-21: Three Results PR #21 passed CI `29794931024` and paper/site build `29794931026`, received complete no-findings review `4740643312`, and squash-merged as `007dc15b89f6d7e98e572d1b164f057c7c38c964`. Post-merge CI `29795041418` and Pages `29795041429` passed; all five pages and result provenance returned HTTP 200 with exact deployed values.
- 2026-07-21: alignment-bound run `20260721T022739Z_DD-001_358cb1eb_cd16846ba5` started clean at commit `358cb1eb`, completed in 0.39 seconds, and passed all 21 tiny fixtures plus two anti-informative checks. Its separate verifier checks every Bellman inequality/equality witness without optimizing and rejects a zeroed final value. The canonical upper bound `325089/390625` meets direct clue-following, proving the deterministic and ex-ante randomized optima (DD-C-0037/DD-C-0038); the relaxation is not universally tight because the `M=3,N=2,p=0` case has upper `1` versus exact `11/12`.
- 2026-07-21: PR #23 passed CI `29796343151` and paper/site build `29796343110`, received complete no-findings review `4740754564`, and squash-merged as `df35f80273f106ef86f623c4676fe2a58757b6ad`. Post-merge CI `29796429926` and Pages `29796429904` passed. The first live smoke-test shell used `path` as a zsh loop variable, overwriting zsh's special command-search array and making `curl`, `rg`, and `jq` temporarily unavailable inside that process; rerunning with variable `route` returned HTTP 200 for all seven routes and verified the exact deployed value and alignment run ID.
- 2026-07-21: DD-002 selection run `20260721T025802Z_DD-002_73a85c71_b0e5b6dc49` passed 15 policies, 37 posterior games, 256 pure selections, 45 refinements, 333 profile states, 1,998 potential/deviation checks, 333 Bellman states, and 270 rule comparisons in 0.089 seconds. An independent verifier reproduces the games, potential identities, and absorption equations and rejects a corrupted absorption probability. The known `P00` to `P03` reversal survives only anonymous-symmetric selection; best pure, worst pure, uniform potential maximum, uniform strict-best-response basin, and planner all improve from `2/3` to `3/4`. Across all refinements their harmful counts are `1,0,8,2,2,0` (DD-C-0039--DD-C-0041).
- 2026-07-21: the first targeted public-integration pytest was deliberately invoked before regenerating the paper artifacts and therefore detected stale provenance; after `make three-results`, all targeted paper/site tests passed. The rebuilt 13-page synthesis PDF is byte-reproducible at SHA-256 `1489d0e2aa3a4dc65b38e1731becaf71dbeb946f3670d09e396a79639415a592`, and all 13 Poppler renders passed visual review.
- 2026-07-21: PR #25 passed CI `29797737821` and paper/site build `29797737785`, received complete no-findings review `4740900193`, and squash-merged as `993b0899421d446f61348a513d2630e0f424e336`. Post-merge CI `29797810807` and Pages `29797810786` passed; all seven routes returned HTTP 200 and the deployed six-rule counts/run provenance match the immutable source.
- 2026-07-21: DD-003 heterogeneous run `20260721T032358Z_DD-003_84238b76_2cbc13e66a` passed in 78.23 seconds under 120 seconds and 512 MB. Primary canonicalization and independent adjacent-swap traversal agree on 41,612 base labeled objects/671 orbits and 12,966 expansion labeled objects/168 orbits. Across 839 networks, 163 complete-moment groups cover 485 networks and 111 groups differ in discovery. The simplest exact colored witness has identical 66-entry first/pairwise moments but discovery `3/4` versus `2/3`, difference `1/12`; an independent verifier reconstructs all entries and rejects a zeroed difference (DD-C-0042--DD-C-0044).
- 2026-07-21: the first post-integration site test caught removal of the established phrase “bounded null, not a theorem.” The wording was restored. The final 14-page synthesis PDF is byte-reproducible at SHA-256 `53cbfa8ccf6f732b13670206f3a8c25627390cbb29206f6b1b017163ae3735bf`, and all 14 Poppler renders passed visual review.
- 2026-07-21: DD-006B primary run `20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b` completed from clean commit `f022a1a5` in 22.55 seconds under the 60-second/1-GB registration. The 60-row exact census and separate evaluator agree on all incentive, discovery, participation, subsidy, ex-post transfer-bound, and liability certificates. Sixteen rows are strict, three use an active positive proper score, maximum all-tie margin is `13/72`, and the target-visible/action-hidden regime has no weak row.
- 2026-07-21: DD-006B integration passed `make verify` with 116 tests and 31 manifests, built a 28-page/11-study site with generated mechanism Lab data, and rebuilt all three papers. The Three Results paper changed only because its generated claim-ledger provenance hash changed; it remains 14 pages, is byte-reproducible at SHA-256 `1ac0700bf2d15a18c58207f2aa45879306f0e09217578ce0de366af2bea0309f`, and all 14 Poppler renders passed visual review.
- 2026-07-21: DD-009 primary run `20260721T171249Z_DD-009_bc78d249_0c3851c41a` completed from clean commit `bc78d249` in 0.20 seconds under the 30-second/512-MB registration. It classifies 288 cells, evaluates 20 coherent architectures, independently reproduces every row, and records 12 nondominated cells. Local integration passes 118 tests, 32 manifests, a 30-page/12-study site, and all three papers. The 14-page Three Results provenance rebuild is byte-reproducible at SHA-256 `d5c4d8e110b82aa34cf1beb3244204d2ad5902c58aaea44a860b40e442dc7b47`; all 14 Poppler renders passed visual review.
- 2026-07-21: DD-009 PR #65 passed all three head checks, squash-merged as `fc273e9401e2f350d436ff6fd6bc5bc3eac93e83`, and closed issue #64. Post-merge CI `29852583292` and Pages `29852583377` passed. The DD-009 study, claim, evidence, study-data, Atlas-data, and Atlas-Lab routes all returned HTTP 200; deployed data reports 20 architectures, 12 nondominated cells, maximum discovery `11/12`, and maximum social net value `5/6`.
- 2026-07-21: heterogeneous-source PR #27 passed CI `29798934183` and paper/site build `29798934209`, received no-findings review `4741011022`, and squash-merged as `4a8f53e90b1ffea233de5b377ba970566d92d670`. Post-merge CI `29798998333` and Pages `29798998329` passed; all seven then-required routes and the exact 839-network data were verified live.
- 2026-07-21: maintenance issue #28 was split by risk class. PR #29 refreshed checkout/setup-uv/Pages actions and Dependabot grouping, PR #30 raised PyYAML/types-jsonschema floors without changing resolved versions, and PR #31 migrated strict checking from mypy 1.20.2 to 2.3.0. All three PRs passed branch and post-merge CI/Pages. Obsolete conflicted Dependabot PRs #1–#5 were closed with replacement links.
- 2026-07-21: mypy 2.3 produced no new diagnostics across 45 source files under either its standard parser or `--native-parser`. Defaults for local partial types and strict bytes required no compatibility override; no global or targeted suppression was added.
- 2026-07-21: the single settings-capable command validated 23 labels, six milestones, and five issue drafts, then failed at its first `gh repo view` with exit status 4. No mutation occurred and no retry was made. Issue #32 records Issues-write, Metadata-read, and Administration-write as the missing authority plus exact resume calls.
- 2026-07-21: final acceptance passed 95 tests, a focused 35-test certificate/provenance audit, strict mypy 2.3, 44 claims, 17 manifests, both papers, the five-page site, secret/license/host-path/upstream checks, all-page Three Results visual QA, and eleven HTTP-200 live routes. A broad local-path regex first stopped on the intentional `file:///private/checkout/...` sanitizer fixture; the host-specific scan then passed. `make upstream-patch` also reordered two parallel Tectonic `Writing` log lines while successfully validating the patch; the incidental log-only change was restored.

## Decision log

- 2026-07-20: use an isolated upstream cache rather than vendoring, subject to ADR-0001.
- 2026-07-20: use `uv`, pytest, Ruff, mypy, PyYAML, and jsonschema, subject to ADR-0002.
- 2026-07-20: project owner explicitly authorizes a public MIT source repository, Actions-built GitHub Pages, GitHub metadata, non-destructive `main` protection, and squash-merging passing queue PRs. Canonical upstream remains read-only.

## Validation strategy

Each milestone runs its targeted Make commands plus schema, unit, integration, and artifact checks. M9 runs `make all`, link/content checks, secret scan, and Git review.

## Commands and expected observations

- `git status --short --branch`, `git remote -v`, `git log`: establish repository condition; observed no commits/remotes.
- `git switch -c codex/bootstrap-distributed-discovery`: create the safe branch; succeeded.
- `uv lock && uv sync --locked`: resolved 21 packages under Python 3.11.15; succeeded.
- Four `quick_validate.py` invocations under `uv run`: all repository skills valid.
- `make bootstrap`: locked environment and 11-file/bootstrap plus valid-claim fixture checks passed.
- `make lint`: Ruff format and lint passed.
- `make typecheck`: strict mypy passed across 11 source files.
- `make test`: 3 tests passed.
- `make validate-claims`: the two-record claim ledger passed JSON Schema validation.
- `make fetch-upstream`: cloned the canonical repository to ignored cache and returned commit `5025cc8e`.
- `uv pip compile ... --no-header --no-annotate`: pinned 11 upstream reproduction packages.
- Three `make reproduce-baseline` executions: the first two exposed and preserved post-validation wrapper failures; the third completed in run `20260720T190336Z_DD-000_32dd1c32_217c602fa0` with validation status `passed`.
- M1 `make lint`, `make typecheck`, `make test`, `make validate-claims`: passed; 10 tests and 3 manifests validated.
- M2 scholarly searches across information ordering/design, team theory, organizational/scientific search, epistemic networks, coverage games, submodularity, robotic redundancy, and terminology collisions; primary/stable records logged in `docs/literature/search-log.md`.
- M2 `make lint`, `make typecheck`, `make test`, `make validate-claims`: passed; 12 tests and 3 manifests validated.
- M3 `make upstream-patch`: patch applied in a disposable worktree and Tectonic 0.16.9 compiled the 30-page preview; two consecutive builds had the same PDF SHA-256. Poppler rendered all pages for visual QA.
- M4 `make site`: built four pages from passing canonical run `20260720T190336Z_DD-000_32dd1c32_217c602fa0` and seven study status/question files. Internal links, semantic landmarks/headings, resolved template data, tracking absence, generated provenance, and primary text contrast checks passed; full repository verification reached 16 tests.
- M5 `make foundations`: generated a canonical table and pooled-frontier figure from validated run artifacts, resolved 15 citation keys and 17 claim IDs, compiled 12 pages with Tectonic 0.16.9, and produced byte-identical PDF SHA-256 `3637f16e...` twice. Poppler rendered all pages; targeted full-resolution review covered data assets, dense lists, and references. Full repository verification reached 18 tests.
- M6 `make dd001`: primary run completed the 21-point exact grid and 18 canonical restarts in 8.4 seconds inside a 120-second budget. Exact formula/direct enumeration, normalization, exhaustive counts, benchmark bounds, seeds, terminations, output hashes, and generated SVG checks passed. Claim-specific audit commands and targeted tests passed; six run manifests now validate.
- DD-001A `make dd001-signatures`: primary run completed the 21-point independent signature grid, feasibility/reconstruction audit, and canonical state-space certificate in 13.73 seconds under a 120-second budget. All validation flags passed; the independent checker accepted the certificate and its corruption test rejects a modified count.
- DD-001B `make dd001-thresholds`: primary run completed the exact restricted-family theorem and bounded unrestricted census in 35.86 seconds; PR #14 and post-merge CI/Pages passed.
- DD-002 `make dd002-disclosure`: primary run completed the entire bounded deterministic-policy lattice in 0.018 seconds. The independent witness verifier, exact posterior/equilibrium checks, planner monotonicity, corruption test, and run manifest validation passed.
- DD-003 `make dd003-source-graphs`: primary run completed the 51-graph exact census in 2.00 seconds. Independent orbit traversal, pairwise nonisomorphism, direct moment/discovery recomputation, bounded-null verification, scalar counterexample verification, and corruption testing passed.
- DD-003 PR/post-merge: required branch workflows passed; issue #10 closed automatically on squash merge; five-route Pages smoke test passed and the live open-problems page contains the independently reproduced DD-003 status.
- Three Results local acceptance: `make verify` passes 72 tests plus strict typing, lint, and 14 immutable run manifests; `make papers` deterministically builds the 12-page Foundations and 12-page Three Results PDFs; `make site` emits five validated pages and four checksum-bound result-source run identifiers. Poppler rendering and all-page inspection validate the synthesis PDF.
- M7 `make verify`: passed after adding six bounded research briefs and linking their next actions into the study registry; no DD-002 through DD-007 experiment was executed and no result claim was added.
- M8 `python scripts/setup_github.py`: validated 23 labels, six milestones, and four nonduplicative initial issue drafts in offline dry-run mode. `make verify` passed 28 tests plus claim and run validation.
- M9 `make all`: formatting, lint, strict typing, 28 unit/integration/regression tests, claim/run validation, a clean canonical reproduction, the 12-page foundations build, and the four-page site build passed. `make upstream-patch`, PDF metadata/render inspection, internal-link/content tests, provenance/hash validation, local-path/token scans, and upstream/Git hygiene checks also passed. A final provenance-sanitizer unit test brought the post-documentation verification total to 29 passing tests; its first format check and a direct audit missing `PYTHONPATH` stopped safely and were corrected before the passing rerun.

## Artifacts produced

M0 produced the instruction system, policies, eight ADRs, four validated workflow skills, complete study registry, claim ledger/schema, package/CLI skeleton, locked environment, Make interface, tests, GitHub templates/workflows, integration boundary, and documentation/result indexes.

M1 produced the upstream lock and source hashes, upstream dependency lock, isolated reproduction wrapper, immutable run artifacts, independent finite-model evaluator, exact-rational/tiny/count-enumeration tests, full-precision regression, manifest validation, baseline report, and baseline claim map DD-C-0003 through DD-C-0015.

M2 produced full foundations/glossary/notation documents, pipeline diagram, canonical/framework mapping, literature search log/evidence map/novelty risks, 15-entry verified bibliography, proposition DD-C-0016 with review, and terminology negative result DD-C-0017.

M3 produced six auditable source fragments, a placement/change memo, a generated review patch against pinned upstream, a patch/apply/compile validator, a deterministic compiled preview with sanitized log and metadata, integration tests, and a visual-QA record.

M4 produced a local four-page static companion, generated canonical/study/claim data, a deterministic builder, semantic/link/content/no-tracking validation, keyboard focus and reduced-motion behavior, responsive light/dark styling, and contrast tests. It was not deployed at the time; the public Pages deployment was added after M9.

M5 produced the 12-page foundations LaTeX note, generated table and figure source with input checksums, paper-specific validated bibliography, claim/citation/source checks, deterministic PDF, sanitized build log, validation record, source tests, and page-level visual-QA record.

M6 produced the frozen zero-communication model; rational factorized and direct evaluators; agent-symmetric exhaustive optimizer; bounded exact coordinate ascent; a guarded 21-point configuration; three immutable passing runs; exact phase data, policies, and SVG; an informative hybrid counterexample; a canonical lower-bound/upper-benchmark record; two proofs; five audited claim records DD-C-0018 through DD-C-0022; a study/global report; and a calibrated working-paper outline.

M7 produced six serious research briefs covering the minimum viable model, canonical relationship, estimands, adjacent literature, methods, falsifiable questions, dependencies, risks, first bounded executable experiment, and completion criteria for DD-002 through DD-007.

M8 produced label and milestone manifests, six issue forms, four substantive initial issue drafts, an evidence-complete pull-request template, a non-destructive setup helper, an application checklist, and integration tests. Nothing was applied to GitHub because the repository has no remote.

M9 produced a clean canonical acceptance run, refreshed generated paper provenance, revalidated both PDFs and the local site, scrubbed redundant private checkout paths from environment snapshots, updated all navigation/status surfaces, and created the comprehensive project handoff.

Milestone A produced the reconciled public/MIT/Pages state, passing PR #12, deterministic paper artifact workflow, five live research issues, and a successful post-merge Pages smoke test. DD-001A produced the lossless signature theorem and exact feasibility proof, independent implementations and tests, two immutable passing runs, primary reduction/certificate artifacts, claims DD-C-0023 through DD-C-0025, a global report, and a working-paper fragment. DD-001B produced exact restricted thresholds, a bounded unrestricted census, and claims DD-C-0026 through DD-C-0028. DD-002 produced the complete bounded deterministic-disclosure registry, independent reversal verifier, exact refinement census, claims DD-C-0029 through DD-C-0031, and an information-design outline. DD-003 produced the complete 51-graph registry, independently reproduced orbit counts and moment/discovery values, a bounded-null certificate, scalar counterexamples, claims DD-C-0032 through DD-C-0034, and an exact SVG figure. Cycle G adds a separate 12-page synthesis paper, three generated figures, a generated evidence-status table, immutable provenance and visual-QA records, a public Results template, checksum-backed result JSON, and exact five-page site validation.

## Blockers

There is no local research, validation, build, CI, Pages, license, provenance, or Git blocker. The sole operational blocker is issue #32: GitHub CLI lacks a settings-capable authenticated session, so the prepared labels, milestones, homepage, and safe `main` ruleset remain unapplied. The connected GitHub app and SSH cover issue/PR and Git transport operations. Do not repeat the settings attempt until the missing authority is intentionally supplied.

## Recovery and restart instructions

Start from `main` with `git switch main && git pull --ff-only origin main && make verify`. For the only operational blocker, authenticate intentionally with `gh auth login` and follow issue #32 plus `docs/github-setup.md`; do not retry blindly. For new research, open a new bounded issue with state-space, time, memory, interruption, and certificate plans before extending DD-001, DD-002, DD-003, or starting DD-004–DD-007. Never rerun a completed primary configuration merely to refresh timestamps.

## Outcome and retrospective

M0–M9, Milestone A, DD-001A/B, bounded DD-002/DD-003, the A–E handoff, and continuation cycles F–L meet their evidence, review, merge, CI, deployment, and live-verification criteria. Cycle M has passed local acceptance and changes documentation only; it is complete when its PR is reviewed, merged, and the final Pages deployment is smoke-tested. The only preserved failure outside completed research is the single settings-authentication blocker in issue #32.
