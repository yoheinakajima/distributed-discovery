# Master execution plan

## Purpose and intended outcome

Bootstrap and execute a durable, auditable research program for Distributed Discovery while preserving the Shared Discovery Paradox repository as the canonical, read-only public presentation.

## Current state

As inspected on 2026-07-20 UTC, the repository was empty, had no commits or remotes, and was on unborn branch `master`. Work moved to `codex/bootstrap-distributed-discovery`. M0 passed its validation and is ready to commit. **Active milestone: M1 — Pin and Reproduce the Canonical Upstream.**

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
- M1 pin and reproduce canonical upstream: active.
- M2 formalize foundations: pending.
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
- [ ] Commit M0 and fetch/pin canonical upstream for M1.

## Discoveries and surprises

- 2026-07-20: host `python3` is 3.9.6; `uv` is available. The project will declare Python >=3.11 and use the locked `uv` environment.
- 2026-07-20: no LaTeX executable was found during the initial inspection; paper validation may require a lightweight fallback or a documented toolchain blocker.
- 2026-07-20: the skill validator failed under host Python because PyYAML was absent, then passed for all four skills under `uv run`.
- 2026-07-20: initial claim validation exposed PyYAML's implicit conversion of unquoted ISO dates to `date` objects; claim dates are now quoted at the serialization boundary. Initial mypy also required the package `py.typed` marker. Both failures were retained here and corrected before commit.

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

## Artifacts produced

M0 produced the instruction system, policies, eight ADRs, four validated workflow skills, complete study registry, claim ledger/schema, package/CLI skeleton, locked environment, Make interface, tests, GitHub templates/workflows, integration boundary, and documentation/result indexes.

## Blockers

No M0 blocker. No Git remote exists, so later push/draft-PR operations are unavailable unless a private origin is configured.

## Recovery and restart instructions

From the repository root, read the mandatory files in `AGENTS.md`, inspect `git status`, then run `make fetch-upstream`. Inspect and pin the returned upstream commit before executing its verification instructions.

## Outcome and retrospective

M0 met its completion criteria after two detected-and-corrected validation issues (YAML date coercion and missing typing metadata). The repository can now explain its mission, rules, active plan, and next command without this prompt.
