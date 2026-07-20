# Master execution plan

> The M0–M9 material below is retained as historical execution evidence. Current operational state and the active A–E queue are recorded in the opening sections, blockers, and recovery instructions; stale no-remote/private statements inside completed-milestone history describe the state at that time.

## Purpose and intended outcome

Bootstrap and execute a durable, auditable research program for Distributed Discovery while preserving the Shared Discovery Paradox repository as the canonical, read-only public presentation.

## Current state

The historical M0–M9 bootstrap and operational Milestone A are complete. DD-001A merged as `c16144e8a3f5287d1117b768856f559064a89bc0`; DD-001B merged as `7e637c1dc191b90f8de477ae05a779a254e35055`, with Pages run `29785199359` passing. **Active milestone: D — DD-002 bounded deterministic disclosure, issue #7, branch `research/dd002-disclosure-fixture`, draft PR #15.**

## Scope

Completed M0–M9 infrastructure and evidence, followed by the authorized queue: A public/MIT/Pages cleanup; B DD-001A policy signatures and certification; C DD-001B two-agent thresholds; D bounded DD-002 disclosure; E bounded DD-003 source graphs; integrated handoff.

## Non-goals

Changing canonical upstream, publishing a release or DOI, adding telemetry, starting DD-004–DD-007 implementations, asserting novelty before literature review, or presenting exploratory computations as verified. Public source and Pages deployment are now explicitly authorized.

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
- D DD-002 bounded disclosure fixture: implementation, primary evidence, and claim audit complete; PR #15 validation/merge pending.
- E DD-003 bounded source-graph fixture: pending D.
- Integrated handoff: pending E or a hard execution limit.

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
- [ ] Merge DD-002 PR #15 after CI and verify live Pages.
- [ ] Execute DD-003 with issue #10, one branch, and one PR.

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
- 2026-07-20: preliminary DD-001A run `20260720T220911Z_DD-001_6822d4c6_40bf5b06a5` passed the computational reduction audit, but claim review found its `certified_interval` output key was too strong because the pooled benchmark is explicitly not a private-team certificate. The run remains immutable and valid as a preliminary audit; presentation was corrected before the primary run.
- 2026-07-20: primary DD-001A run `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5` started from clean commit `b1d8d431` and passed in 13.73 seconds. It independently reproduced all 21 exact tiny optima and raw-policy multiset tie counts, matched matching/reference and closed-form feasibility through M=5, reconstructed all audited signatures, and passed the independent structural certificate verifier.
- 2026-07-20: the signature theorem reduces each policy losslessly to targetwise incoming counts and fixed-point indicators. At canonical M=16, exact counts are 148,348,284,928 feasible labeled signatures and 5,806 individual target orbits, but independently quotienting agents loses relative target alignment. The eight-agent multiset count before a global target quotient has 85 digits, so the declared naive enumeration exceeds its resource budget. This is not a private-team objective upper bound.
- 2026-07-20: DD-001B primary run `20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1` passed in 35.86 seconds. It proves the exact three-family thresholds \(1/M\) and \(1/(M-1)\), exhaustively certifies the unrestricted continuous informative envelope for M=3,4,5, and records p=0 counterexamples that refute an all-p extension.
- 2026-07-20: DD-002 primary run `20260720T225848Z_DD-002_94607423_e29b1460ae` enumerated all 15 deterministic disclosure policies, 37 posterior games, 256 global pure-equilibrium selections, and 45 strict refinement pairs. Exactly one refinement lowers the declared anonymous-symmetric selection, while every pure equilibrium and the planner improve for that witness; the reversal is selection-dependent.

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

Milestone A produced the reconciled public/MIT/Pages state, passing PR #12, deterministic paper artifact workflow, five live research issues, and a successful post-merge Pages smoke test. DD-001A produced the lossless signature theorem and exact feasibility proof, independent implementations and tests, two immutable passing runs, primary reduction/certificate artifacts, claims DD-C-0023 through DD-C-0025, a global report, and a working-paper fragment. DD-001B produced exact restricted thresholds, a bounded unrestricted census, and claims DD-C-0026 through DD-C-0028. DD-002 produced the complete bounded deterministic-disclosure registry, independent reversal verifier, exact refinement census, claims DD-C-0029 through DD-C-0031, and an information-design outline.

## Blockers

No current local blocker. GitHub CLI is installed but unauthenticated; the connected GitHub app and SSH cover issue/PR and Git transport operations. Labels, milestones, homepage, and ruleset/repository-setting writes have a precise capability-specific blocker until CLI OAuth or equivalent settings access is available. The prepared issues retain their intended metadata in their bodies.

## Recovery and restart instructions

On branch `research/dd002-disclosure-fixture`, validate and commit immutable run `20260720T225848Z_DD-002_94607423_e29b1460ae` plus claims DD-C-0029 through DD-C-0031, finish PR #15, and verify post-merge Pages. Then sync `main` and begin DD-003 issue #10. Preserve the deterministic-policy and selected-equilibrium scope of the DD-002 reversal.

## Outcome and retrospective

M0–M9, Milestone A, DD-001A, and DD-001B meet their criteria. DD-002 establishes a complete bounded deterministic-disclosure census and an exact selection-dependent harmful-information witness; PR #15 is the active integration boundary. After it merges, the next bounded milestone is DD-003.
