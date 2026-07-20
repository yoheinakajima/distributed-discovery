# Master execution plan

## Purpose and intended outcome

Bootstrap and execute a durable, auditable research program for Distributed Discovery while preserving the Shared Discovery Paradox repository as the canonical, read-only public presentation.

## Current state

As inspected on 2026-07-20 UTC, the repository was empty, had no commits or remotes, and was on unborn branch `master`. Work moved to `codex/bootstrap-distributed-discovery`. M0 through M4 are complete. **Active milestone: M5 — Create the Foundations Companion Note.**

## Scope

Milestones M0–M9 in the initiating specification: infrastructure, canonical reproduction, foundations, additive upstream materials, private companion site, foundations note, DD-001, later-study briefs, GitHub organization, and integration.

## Non-goals

Publishing, deploying, changing upstream, asserting novelty before literature review, or presenting exploratory computations as verified.

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
- M5 foundations note: active.
- M6 DD-001 initial research: pending.
- M7 later-study briefs: pending.
- M8 GitHub organization: pending.
- M9 integration and handoff: pending.

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
- [ ] Build and visually validate the foundations companion note.

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

## Decision log

- 2026-07-20: use an isolated upstream cache rather than vendoring, subject to ADR-0001.
- 2026-07-20: use `uv`, pytest, Ruff, mypy, PyYAML, and jsonschema, subject to ADR-0002.

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

## Artifacts produced

M0 produced the instruction system, policies, eight ADRs, four validated workflow skills, complete study registry, claim ledger/schema, package/CLI skeleton, locked environment, Make interface, tests, GitHub templates/workflows, integration boundary, and documentation/result indexes.

M1 produced the upstream lock and source hashes, upstream dependency lock, isolated reproduction wrapper, immutable run artifacts, independent finite-model evaluator, exact-rational/tiny/count-enumeration tests, full-precision regression, manifest validation, baseline report, and baseline claim map DD-C-0003 through DD-C-0015.

M2 produced full foundations/glossary/notation documents, pipeline diagram, canonical/framework mapping, literature search log/evidence map/novelty risks, 15-entry verified bibliography, proposition DD-C-0016 with review, and terminology negative result DD-C-0017.

M3 produced six auditable source fragments, a placement/change memo, a generated review patch against pinned upstream, a patch/apply/compile validator, a deterministic compiled preview with sanitized log and metadata, integration tests, and a visual-QA record.

M4 produced a local four-page static companion, generated canonical/study/claim data, a deterministic builder, semantic/link/content/no-tracking validation, keyboard focus and reduced-motion behavior, responsive light/dark styling, and contrast tests. It was not deployed.

## Blockers

No M0 blocker. No Git remote exists, so later push/draft-PR operations are unavailable unless a private origin is configured.

## Recovery and restart instructions

From the repository root, read the mandatory files in `AGENTS.md`, inspect `git status`, then continue M5 in `papers/foundations/`. Build a concise professional LaTeX note from the formal foundations and literature record, generate numerical tables/figures from validated data, validate references and claim IDs, compile with Tectonic, and render every page for visual QA.

## Outcome and retrospective

M0–M4 meet their criteria. M2 made no general theorem or novelty claim from the atomic model; it records terminology collisions and treats effective channels/source concentration as model-specific or provisional. M3 keeps that calibration in the patch and does not modify canonical upstream. M4 is private, tracker-free, and un-deployed.
