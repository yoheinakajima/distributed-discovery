# Agent Operations v1

This living ExecPlan implements the repository-native operating layer for
task contracts, scoped instructions, generated execution context, reusable
acceptance profiles, generic owner gates, and structured handoffs. It is an
infrastructure task. It creates no scientific evidence and does not register
or execute the future TreasureBench pilot.

## Purpose and intended outcome

Replace repeated policy-heavy prompts with a durable workflow in which a short
task delta points to repository authority: persistent `AGENTS.md` instructions,
a fixed typed task contract, this mutable ExecPlan, GitHub issue and pull
request state, generated live context, an acceptance profile, owner-gate
manifests, and typed handoffs. Normal completion includes implementation,
tests, documentation, one issue, one branch, one pull request, merge, CI,
post-merge verification, issue closure, and synchronized `main`.

## Current state

Live audit at `2026-07-25T04:23:28Z`:

- repository: `yoheinakajima/distributed-discovery`;
- working directory:
  `/Users/yoheinakajima/Documents/distributed-discovery`;
- local `main`, `origin/main`, and expected start:
  `15b56b5c671ff593fd84c91142c096eba381f4cb`;
- tracked tree clean; exactly five unrelated untracked preservation files;
- no open pull request; issue #32 is the only open issue and is settings-only;
- PR #192 merged as
  `4fb4ef83ac39c11dcbe43bf21a8904d89b12246b`; PR #193 merged as
  `15b56b5c671ff593fd84c91142c096eba381f4cb`; issue #191 is closed;
- current-main CI run `30142005111` and Pages run `30142005117` passed;
- original pilot remains
  `sealed-pilot-quarantined-provider-failure`;
- repair decision remains
  `instrument-repaired-fresh-sealed-pilot-required`;
- selected future option remains a fresh 50-task/500-run confirmation with
  provisional USD 15 expected cost, USD 25 proposed hard cap, and proposed
  OpenAI/Anthropic caps of USD 10/USD 15;
- no fresh pilot issue, branch, call, spend, private generation, authorization,
  DD-023, or DD-C-0111 exists;
- scientific inventory remains 110 claims, 26 studies, and 51 manifests with
  48 passing;
- seven release-registered PDFs remain 119 pages;
- `dd-compendium-v0.1.0`, its GitHub Release, Zenodo records, and DOI roles
  remain published and verified;
- root instructions are 34 lines and no scoped `AGENTS.md` files exist yet;
- CLI uses `argparse`, `uv run --no-editable`, and the root
  `distributed-discovery` entry point; CI splits lint/typecheck,
  integration/regression, unit, claim/run, and release checks.

Preservation file SHA-256 values:

- `papers/information-sharing-frontier/paper-audit 2.json`:
  `1a76c2fdd0b1aa0b925125e18a47d95b60ac8ac0023a51fa80a429cfdd39c507`;
- `papers/information-sharing-frontier/visual-qa 2.md`:
  `0db65b0bdba76a1fa81f6e01a6dbe87d9556511acf9dbe736b8868d2b8a1a6be`;
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`:
  `e86ec4cbfc6462a035de21db26c958f79e995350131e0e89ad18553f7a2b9dd9`;
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`:
  `9716bc644660460b1d9779db2d1d2c6b1c14f38ccbdd648b18e06836dcae729f`;
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`:
  `2886c3d10f2bd1cd643e8306a5182272c6f59784cb16c2b47b29f6ae140d7000`.

## DISCUSSION AND DECISION DELTA AUDIT

The 31-record program-memory registry was read before issue or branch creation.
Every existing owner-adopted record has a canonical destination. No
evidence-dependent trigger has occurred: claim-grade Agents v1 evidence does
not exist, the journal-track trigger has not fired, no new bridge theorem or
third-party naming evidence has been supplied, and the future fresh pilot is
not registered. No existing record becomes superseded merely because this
workflow infrastructure is being added.

The new owner-adopted decision is that future substantive work uses thin task
deltas plus repository-native contracts instead of reserializing stable policy
in prompts. Route it prospectively as `PM-0032` to
`docs/adr/ADR-AGENT-OPERATIONS-V1.md`, with operational detail in
`docs/agent-ops/README.md`, the director contract, schemas, profiles, and this
plan. Historical issues, plans, and prompts remain unchanged. The proposed
TreasureBench fresh-pilot preview is illustrative and non-authoritative.

No owner decision relevant to this task remains only in conversation after the
planned registry, ADR, task contract, and documentation commit. Repeat this
audit before issue closeout.

## Scope

1. Define workflow-only authority, director behavior, task contracts/deltas,
   task types, acceptance profiles, migration, and scoped instructions.
2. Add a typed current-task contract at
   `tasks/agent-operations-v1.yml`.
3. Implement `distributed-discovery agent-ops` context, prompt, owner-gate,
   and handoff commands with Make interfaces.
4. Add JSON Schemas, YAML templates, synthetic fixtures, semantic corruption
   tests, issue/PR templates, audit tooling, and CI integration.
5. Generate a non-authoritative fresh-pilot next-task preview and prove its
   prompt is within the line/byte limits.
6. Complete the single issue/branch/PR lifecycle and post-merge closeout.

## Non-goals

- No scientific study, claim, run, proof, result, paper, or lifecycle change.
- No provider/local-model call, credential read, private-state access, private
  generation, spend, or external publication.
- No fresh-pilot issue, branch, registration, custody, or authorization.
- No change to canonical upstream, release/DOI state, site content, immutable
  runs, claims, study identities, or retained private pilot material.
- No migration or rewriting of historical prompts, issues, plans, or records.
- No instruction that asks an agent to launch another Codex session.

## Assumptions

- Python 3.12 through the locked `uv` environment remains the execution
  runtime.
- GitHub observations are optional inputs to generated context and never
  contract authority.
- Owner authorization is stored outside Git with mode `0600`; synthetic
  fixtures never authorize a consequential action.
- Generic profiles describe gates but cannot grant permission.
- All permission fields default false and changed authority fails closed.

## Milestones

- **M0 — complete:** live audit, decision-delta audit, issue, branch, current-task
  contract, and living plan.
- **M1 — complete:** authority model, director contract, and architecture
  decision.
- **M2 — complete:** task-contract/delta schemas, templates, and task types.
- **M3 — complete:** acceptance profiles and bounded scoped instructions.
- **M4 — complete:** generated context and thin-prompt renderers.
- **M5 — complete:** generic owner-gate schemas, engine, fixtures, and
  corruptions.
- **M6 — complete:** typed structured handoff renderer.
- **M7 — complete:** issue/PR templates and CI/Make integration.
- **M8 — complete:** non-authoritative next-task preview and prompt compression
  acceptance.
- **M9 — active:** broad validation, PR review/merge, post-merge CI/Pages as
  applicable, issue closure, closeout audit, and synchronized `main`.

## Progress checklist

- [x] Read the task contract and mandatory repository/governance/state inputs.
- [x] Verify local/GitHub baseline and recent #191–#193 closeouts.
- [x] Inspect existing CLI, Make, CI, instructions, and preservation state.
- [x] Complete the initial discussion and decision delta audit.
- [x] Create issue, branch, current-task contract, and M0 commit.
- [x] Complete M1 authority documentation and ADR.
- [x] Complete M2 schemas, templates, and task profiles.
- [x] Complete M3 acceptance profiles and scoped instructions.
- [x] Complete M4 context and prompt generation.
- [x] Complete M5 owner-gate engine and corruptions.
- [x] Complete M6 handoff rendering.
- [x] Complete M7 templates and CI/Make integration.
- [x] Complete M8 next-task preview and compression checks.
- [ ] Complete M9 validation, merge, closeout, and main synchronization.

## Discoveries and surprises

- The five unrelated preservation files are the exact five named in the task
  contract and remain untracked; they must never be staged.
- Current `gh` authentication has repository and workflow authority, unlike
  the historical settings-only blocker. Issue #32 remains unrelated.
- Current Pages builds intentionally switch to the historical sealed-pilot
  branch name at the checked-out commit to satisfy registered pilot verification
  context; Agent Operations must not weaken that behavior.
- Existing owner authorization helpers are task-specific. Agent Operations
  adds a generic engine prospectively without rewriting their historical
  evidence.
- The bounded root plus nine scoped instruction files total 9,113 bytes, well
  below the documented 32-KiB aggregate common-task ceiling.
- The GitHub draft PR allocated number #195 after contract registration. The
  fixed contract retains `pull_request: null`; PR #195 is a dynamic observation
  rendered in context and handoffs rather than an in-place authority edit.
- A direct `uv run --no-editable pytest` omitted the repository `src` path and
  loaded the previously installed package, so initial Agent Operations test
  collection failed. The Make-equivalent `PYTHONPATH="$PWD/src"` run passed all
  four focused tests; repository Make targets already export `src`.
- The first full `make verify` passed Ruff, strict MyPy over 188 source files,
  and 433 of 434 tests. The sole failure was the exact historical six-template
  GitHub inventory assertion, which correctly detected the new required
  `agent-task.yml`; the expected set was extended rather than weakening the
  assertion.

## Decision log

- `2026-07-25T04:23:28Z`: use `tasks/` for committed task instances and
  `docs/agent-ops/` for schemas, templates, profiles, and workflow authority.
- `2026-07-25T04:23:28Z`: implement one `agent_ops` Python package and one
  semantic audit entry point so CLI, Make, and tests share validation logic.
- `2026-07-25T04:23:28Z`: keep all generated context, prompts, handoffs, and
  local authorizations under ignored `build/agent-ops/` or a validated
  external symbolic path.
- `2026-07-25T04:23:28Z`: the generic owner-gate engine verifies and
  authorizes only; it never performs the gated consequential action.

## Validation strategy

Each milestone adds schema-valid valid/invalid fixtures and focused tests.
M9 runs:

```sh
git diff --check
make bootstrap
make audit-agent-ops
make audit-program-memory
make audit-publication-infrastructure
make audit-treasurebench-naming
make release-readiness
make audit-agents-v1
make audit-agents-v1-evaluation
make agents-v1-dry-run
make agents-v1-readiness
make verify
make papers
make site
```

After each broad build, restore no file: generated tracked changes must either
be deterministic intended changes or investigated. Recheck scientific,
release, PDF, preservation-file, credential/provider/private, and Git
boundaries explicitly.

## Commands and expected observations

- `make agent-context TASK=tasks/agent-operations-v1.yml`: writes a
  non-authoritative snapshot under `build/agent-ops/`, with optional GitHub
  observations explicitly labeled.
- `make agent-prompt TASK=...`: writes a delta-only bootstrap no larger than
  120 lines/12 KiB; resume rendering stays within 30 lines.
- `make owner-gate GATE=...`: validates the exact repository surface, requires
  `AUTHORIZE <gate-id> <short-sha>`, creates a mode-0600 local authorization,
  and performs no gated action.
- `make agent-handoff TASK=...`: renders a schema-valid compact handoff under
  50 lines.
- `make audit-agent-ops`: validates schemas, profiles, instructions, templates,
  renderers, owner-gate corruptions, path safety, and authority boundaries.

## Artifacts produced

At plan creation: this ExecPlan only. Later milestone artifacts are recorded
append-only here as they are committed.

M0 adds issue #194, branch `infra/agent-operations-v1`, the typed current-task
contract, task-contract and task-delta schema/template skeletons, and focused
schema-validation tests. The focused test gate passed two tests and
`git diff --check`.

M1 adds the workflow authority model, director contract and replacement
bootstrap, ADR, and routed PM-0032 program-memory record. M2 adds seven typed
task profiles and explicit contract-supersession rules. M3 adds seven
acceptance profiles plus nine bounded scoped instruction files for papers,
release records/reports, site, claims, results, studies, and TreasureBench
Agents v1 code/records.

M4 adds offline-first context plus normal/resume thin-prompt renderers under
ignored `build/agent-ops/`, with optional GitHub observations explicitly
labeled non-authoritative. M5 adds the manifest and authorization schemas,
complete confirmation surface, exact challenge, branch/commit/remote/PR/tree/
contract/cap/expiry checks, safe mode-0600 local output, prior-history
preservation, and thirteen registered semantic corruption outcomes. M6 adds
schema-valid YAML and sub-50-line human handoff rendering for all five
checkpoint statuses.

M7 adds Agent Operations issue/PR templates, five Make interfaces, explicit CI
audit execution, and integration with `make verify`. M8 adds the prospective
migration guide and a non-authoritative TreasureBench fresh-pilot task delta.
Its rendered registration-only prompt is 13 lines and 1,047 bytes, contains no
issue/branch/execution authority, and ends at the separately registered pilot
gate.

M9 local acceptance passes `git diff --check`, bootstrap, all named focused
audits and readiness commands, Ruff, strict MyPy over 188 source files, all 434
tests, 110 claims, 51 manifests, the verified seven-paper/119-page release dry
run, all seven deterministic paper builds totaling 119 pages, and the
89-page/26-study site. Paper builds mechanically refreshed two Information
Sharing Frontier source-commit fields; both were restored to their committed
bytes because papers are out of scope. The five unrelated preservation hashes
remain exact. PR checks, review, merge, post-merge verification, issue closure,
closeout audit, and main synchronization remain active.

## Blockers

None. Issue #32 is unrelated. Missing or stale GitHub observations must degrade
to explicit offline state, not block local Agent Operations validation.

## Recovery and restart instructions

Inspect `git status --short --branch`; preserve the five named untracked files;
read root and nearest scoped `AGENTS.md`; read
`tasks/agent-operations-v1.yml`, this plan, issue/PR state, and the latest
generated handoff; then resume the first unchecked item in the sole active
milestone. Never read `.env.txt`, owner authorization files, or retained
private pilot state. Never run a provider command.

## Outcome and retrospective

Pending. Complete only after the implementation is merged, required workflows
and public routes are verified as applicable, the issue is closed, the
closeout delta audit is committed, and local `main` equals `origin/main`.
