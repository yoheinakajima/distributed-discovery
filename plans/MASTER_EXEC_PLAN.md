# Master execution plan

## Purpose and intended outcome

Bootstrap and execute a durable, auditable research program for Distributed Discovery while preserving the Shared Discovery Paradox repository as the canonical, read-only public presentation.

## Current state

As inspected on 2026-07-20 UTC, the repository was empty, had no commits or remotes, and was on unborn branch `master`. Work moved to `codex/bootstrap-distributed-discovery`. M0 is committed and M1 passed validation. **Active milestone: M2 — Formalize the Foundations.**

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
- M2 formalize foundations: active.
- M3 additive paper extensions: pending.
- M4 private companion site: pending.
- M5 foundations note: pending.
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
- [ ] Commit M1 and begin literature/terminology review for M2.

## Discoveries and surprises

- 2026-07-20: host `python3` is 3.9.6; `uv` is available. The project will declare Python >=3.11 and use the locked `uv` environment.
- 2026-07-20: no LaTeX executable was found during the initial inspection; paper validation may require a lightweight fallback or a documented toolchain blocker.
- 2026-07-20: the skill validator failed under host Python because PyYAML was absent, then passed for all four skills under `uv run`.
- 2026-07-20: initial claim validation exposed PyYAML's implicit conversion of unquoted ISO dates to `date` objects; claim dates are now quoted at the serialization boundary. Initial mypy also required the package `py.typed` marker. Both failures were retained here and corrected before commit.
- 2026-07-20: the first M1 execution attempt failed before research computation because Hatchling's editable `.pth` lacked a terminating newline and was ignored by this Python installation. The Make interface now consistently uses `uv --no-editable`; this installs the locked wheel and restores imports without mutating generated environment files.
- 2026-07-20: two upstream verifier executions completed successfully but their wrappers failed after validation while invoking `python -m pip freeze` in a minimal `uv` environment. The source fix did not reach the second run because the non-editable local wheel was stale. Both operational failures are preserved and excluded from claim evidence. Make now places `src/` first on `PYTHONPATH`, while still using locked non-editable dependencies, so research runners always execute current tracked source.
- 2026-07-20: the canonical upstream is MIT-licensed and its current `main` commit is `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`. The verifier, LaTeX paper, bibliography, static site, data, and figures are all present; upstream remains read-only in ignored cache.
- 2026-07-20: evidence run `20260720T190336Z_DD-000_32dd1c32_217c602fa0` passed every upstream assertion, all rounded sanity checks, and independent consensus/planner/private/blind checks. The upstream market and crossover remain verified but not independently reproduced.

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

## Artifacts produced

M0 produced the instruction system, policies, eight ADRs, four validated workflow skills, complete study registry, claim ledger/schema, package/CLI skeleton, locked environment, Make interface, tests, GitHub templates/workflows, integration boundary, and documentation/result indexes.

M1 produced the upstream lock and source hashes, upstream dependency lock, isolated reproduction wrapper, immutable run artifacts, independent finite-model evaluator, exact-rational/tiny/count-enumeration tests, full-precision regression, manifest validation, baseline report, and baseline claim map DD-C-0003 through DD-C-0015.

## Blockers

No M0 blocker. No Git remote exists, so later push/draft-PR operations are unavailable unless a private origin is configured.

## Recovery and restart instructions

From the repository root, read the mandatory files in `AGENTS.md`, inspect `git status`, then review the pinned paper bibliography and begin the logged scholarly searches in `docs/literature/search-log.md`. Reconcile `docs/foundations.md`, `docs/glossary.md`, and `docs/notation.md` with upstream before promoting terminology.

## Outcome and retrospective

M0 met its completion criteria after two detected-and-corrected validation issues. M1 met its criteria with a fully pinned upstream run and independent checks; two wrapper failures were preserved as operational negative results and excluded from claim evidence.
