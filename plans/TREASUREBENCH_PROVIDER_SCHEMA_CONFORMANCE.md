# TreasureBench provider-schema conformance repair and public-canary gate

This living ExecPlan governs `AO-0004`, a public-only Agent Operations
infrastructure task. It cannot reopen either quarantined TreasureBench
campaign and it stops before credentials, provider calls, or spend.

## Purpose and intended outcome

Diagnose and repair the exact provider-request and strict-JSON-Schema
conformance boundary for TreasureBench Agents v1; separate the canonical
semantic action contract from OpenAI- and Anthropic-specific transport-schema
compilers; add deterministic offline provider linting, safe structured errors,
serialized public fixtures, and a mock canary matrix; then freeze one exact
execution commit and return a generic owner-gate-required handoff for a later
owner-authorized sequence of tiny public canaries.

## Current state

Registration audit at `2026-07-27`:

- `main` and `origin/main` are synchronized at
  `091735a83e3327635d8a3671c65a99a8b8d89cb5`;
- issue #196 is closed and PR #197 squash-merged, so no substantive pull
  request is open;
- issue #198 is the AO-0004 coordination issue and branch
  `benchmark/treasurebench-provider-schema-conformance` is the task branch;
- draft PR #199 is the AO-0004 review surface;
- `AO-0001`, `AO-0002`, and `AO-0003` are allocated, making `AO-0004` the next
  available task identifier;
- the owner selected
  `reports/agent-ops/next-task-treasurebench-provider-schema-conformance.yml`
  as the next substantive gate;
- the repository contains five unrelated untracked files whose names end in
  ` 2`; they are excluded from this task and must remain untouched;
- the failed AO-0002 campaign, batch, execution commit, output lock, HTTP 400
  canary, archived inactive R2 authorization, and quarantine decision remain
  immutable;
- credentials, provider calls, spend, private material, scientific mutation,
  paper work, releases, and a new private pilot remain prohibited before the
  separately committed owner gate.
- the original audit incorrectly classified the standard-model `minItems` and
  `maxItems` properties as OpenAI-ineligible; the owner amendment and current
  official documentation require both constraints to remain in the complete
  pinned GPT-5.4 transport schema;
- `maxLength` and `uniqueItems` are not listed in the current standard-model
  supported properties and remain omitted from the OpenAI transport schema
  with deterministic post-parse enforcement;
- separate provider compilers, offline linting, safe structured errors, nine
  serialized request fixtures, and the four-stage mock canary matrix plus four
  frozen diagnostic bisection fixtures are
  implemented and pass focused validation with zero calls and zero spend.
- superseded R1 execution commit
  `5f1d4b6bdb0d5fce5b4cbfc11f6aceadd910c2c3` is frozen; the committed generic
  owner-gate manifest passed live authorization-free validation but was never
  authorized and may not be consumed;
- `reports/agent-ops/AO-0004-preauthorization-correction.yml` records the
  owner amendment; the repaired runner and R2 execution surface are pending.

## DISCUSSION AND DECISION DELTA AUDIT

The complete `docs/program-memory/registry.yml` was re-read before issue or
branch creation. PM-0033 is the only due item: its explicit registration
trigger occurred when the owner selected the public-only provider-schema
conformance task. It is routed to AO-0004, this plan, the fixed task contract,
the provider audit, the conformance implementation, and the eventual typed
owner-gate handoff. PM-0031 and PM-0032 remain implemented and are preserved;
all evidence-dependent items retain unmet triggers. No scientific,
publication, release, private-pilot, or base-campaign item became due. The
registry will be updated from `routed` to `implemented` only after the task
registration artifacts exist. No owner decision remains only in conversation.
The closeout repeat found no new due discussion item: PM-0033 remains
implemented at its canonical AO-0004 destinations; the evidence-dependent,
scientific, publication, release, private-pilot, and base-campaign triggers
remain unmet.

The owner amendment reopens AO-0004 before authorization. It corrects the
OpenAI standard-model subset audit and requires a committed exact live runner,
append-only public-engineering ledger, deterministic frozen bisection order,
R2 execution freeze, R2 gate, and replacement handoff. This is captured in
the owner-amendment record, this plan, the corrected audit, code, fixtures,
tests, supersession record, and future R2 handoff. It creates no new task,
scientific authority, private authority, or publication authority, so no new
program-memory item is due.

## Scope

1. Register AO-0004 with one GitHub issue, one task branch, one fixed contract,
   one living ExecPlan, and one draft pull request.
2. Re-audit current official OpenAI and Anthropic documentation for the exact
   models, structured-output requests and supported schema subsets, retention,
   errors, retries, and prices.
3. Reconstruct the failed OpenAI request from public fixtures only.
4. Implement one canonical semantic action contract, separate provider
   transport-schema compilers, offline subset linting, provider-independent
   post-parse semantic validation, and safe structured error envelopes.
5. Add the deterministic public-canary matrix and all registered corruptions.
6. Freeze the exact execution surface and commit a generic owner-gate manifest
   with the selected public-only models, routes, calls, and caps.
7. Stop before credential access or any provider call.
8. Correct the OpenAI standard-model subset audit by retaining `minItems: 1`
   and `maxItems: 1` in the complete transport schema.
9. Commit one exact authorization-bound runner with resumability, frozen
   bisection candidates, safe errors, fail-closed caps, and an append-only
   public-engineering ledger before refreezing the R2 surface.

## Non-goals

- No retry, repair in place, reopen, reuse, rescore, reauthorization, or
  execution of AO-0002 or either quarantined campaign or batch.
- No private-data read, write, generation, deletion, or publication and no
  private campaign, custody object, task, answer, seed, key, ciphertext, or run.
- No DD-023, claim, scientific run, evidence or proof promotion, paper,
  ranking, composite, package, release, DOI, submission, or base campaign.
- No alias, fallback, OpenRouter, batch route, regional route, or local model.
- No provider call, credential read, or spend before a later exact owner gate.
- No declaration of provider conformance until the complete TreasureBench
  action schema passes on both exact direct providers.

## Assumptions

- Public source fixtures and immutable redacted AO-0002 records are sufficient
  to reconstruct the serialized request without private-state access.
- Provider transport schemas may omit unsupported keywords only when the
  canonical semantic contract remains unchanged and deterministic post-parse
  checks plus regressions enforce equivalent semantics.
- The generic Agent Operations owner-gate engine is sufficient; no bespoke
  authorization helper is needed.
- Current official documentation is observational input, not permission to
  call a provider or incur spend.

## Milestones

- **M0 — complete:** register AO-0004, create the issue and branch, freeze the
  task contract, validate registration, and open a draft PR after focused
  skeleton tests exist.
- **M1 — complete:** complete and record the official provider-documentation
  audit and exact public serialized-request reconstruction.
- **M2 — complete:** implement the canonical contract, provider-specific
  compilers, offline linters, semantic validator, and safe errors.
- **M3 — complete:** implement the mock canary matrix and every registered
  corruption; pass focused and infrastructure validation.
- **M4 — superseded unused:** the R1 execution surface, gate, and handoff were
  committed and validated without authorization. They receive no authority
  after the owner amendment.
- **M4R — complete, freeze commit pending:** correct the provider audit and
  compiler, implement the
  exact committed live runner and public ledger, freeze deterministic
  bisection candidates, pass focused and full validation, and refreeze the R2
  execution surface.
- **M5R — pending:** supersede R1, commit and validate the R2 owner gate
  without authorization, emit the R2 typed handoff, and stop.
- **M6R — pending owner authorization:** run only the staged public canaries
  under the exact R2 authorization and stopping rule. This milestone must not
  start in the pre-authorization correction turn.

## Progress checklist

- [x] Read repository, Agent Operations, planning, program-memory, scoped
  benchmark, and DD-010 authority.
- [x] Confirm AO-0004 availability and prior-lane GitHub closeout.
- [x] Record the pre-registration discussion and decision delta audit.
- [x] Create issue #198 and the task branch.
- [x] Freeze the fixed task contract.
- [x] Audit current official provider documentation.
- [x] Reconstruct the failed request with public fixtures only.
- [x] Implement provider schema compilers and offline linting.
- [x] Implement provider-independent semantic validation and safe errors.
- [x] Pass the mock canary matrix and all corruptions.
- [x] Open draft PR #199 and pass the complete pre-gate validation wall.
- [x] Create and validate the exact generic owner-gate manifest.
- [x] Return the typed owner-gate-required handoff and stop before calls.
- [x] Record the owner pre-authorization correction without consuming R1.
- [x] Correct the OpenAI standard-model schema subset, audit, fixtures,
  fingerprints, and tests.
- [x] Implement and test the exact authorization-bound public-canary runner.
- [ ] Refreeze, supersede R1, and return the validated R2 gate and handoff.

## Discoveries and surprises

- The first contract audit rejected the unsupported authority-reference type
  `delta`; the schema-valid type is `record`.
- The first program-memory audit rejected a newly invented review trigger.
  PM-0033 therefore retains the registered `explicit-owner-decision` trigger.
- The same audit permits task-contract paths as decision records but not a
  newly invented `task-contract` destination class; the destination path stays
  exact and the registered class is `decision-record`.
- The original runtime built one shared canonical schema for every provider.
  The first AO-0004 audit incorrectly extended the fine-tuned-model
  `minItems` and `maxItems` exclusion to the pinned standard GPT-5.4 snapshot.
  The corrected bounded diagnosis leaves only `maxLength`, `uniqueItems`, or
  another request/schema interaction as documented possibilities; the
  intentionally unretained raw body leaves the historical HTTP 400 cause
  unresolved.
- Anthropic's current subset differs materially: `minItems` is supported only
  at 0 or 1, while the relevant `maxLength`, `maxItems`, and `uniqueItems`
  constraints require provider-independent validation.
- A source-resolution attempt using an unqualified non-editable environment
  imported the prior installed package and failed. The repository Makefile
  already exports `PYTHONPATH=src`; the registered target uses that source
  boundary and now rebuilds byte-identical fixtures.

## Decision log

- `2026-07-27`: allocate AO-0004 to the owner-selected public-only conformance
  task and preserve every AO-0002 quarantine identifier and prohibition.
- `2026-07-27`: cap the later gate-eligible canaries at ten total calls, USD
  1.00 total, USD 0.50 per provider, with expected cost below USD 0.10.
- `2026-07-27`: require both providers' complete action schema—not a trivial
  schema—to pass before any conformance declaration or future private-pilot
  consideration.
- `2026-07-27`: repair two registration-only schema errors without changing
  authority: use the supported `record` reference class and the existing
  `explicit-owner-decision` memory review trigger.
- `2026-07-27T15:57:26Z`: record the official-source audit, bounded diagnosis,
  exact schema and fixture hashes, and zero-call zero-spend activity.
- `2026-07-27`: compile provider transport schemas separately while retaining
  all omitted constraint semantics in the existing provider-independent
  parser, protocol verifier, and metric-range checks.
- `2026-07-27`: open draft PR #199, pass the complete pre-gate validation
  wall, and designate the next commit as the immutable public-canary execution
  surface to which the generic owner gate must bind.
- `2026-07-27`: freeze execution commit
  `5f1d4b6bdb0d5fce5b4cbfc11f6aceadd910c2c3`, commit the generic owner gate,
  and validate its live contract, ancestry, protected trees, caps,
  prohibitions, issue, branch, and draft-PR state without creating an
  authorization or performing a consequential action.
- `2026-07-27T17:46:12Z`: accept the owner's pre-authorization correction,
  prohibit use of the never-authorized R1 gate, retain OpenAI `minItems` and
  `maxItems`, require an exact committed runner and public ledger, and reopen
  the execution freeze as M4R without creating a new task, issue, branch, PR,
  or session.
- `2026-07-27`: retain OpenAI `minItems: 1` and `maxItems: 1`, omit
  `maxLength` and `uniqueItems` from that transport, and leave the historical
  HTTP 400 cause unresolved. Freeze two deterministic diagnostic schemas per
  provider and an exact authorization-bound runner whose maximum projected
  six-call failure path is USD 0.0374255.

## Validation strategy

Validate task, gate, and handoff YAML against Agent Operations schemas. Add
unit tests for canonical semantics, both provider subsets, exact serialization,
safe error normalization, budget/route/model guards, the mock canary matrix,
and every required corruption. Run focused tests, strict MyPy, Ruff, the
infrastructure acceptance profile, TreasureBench audits and rehearsals, then
the full repository verification targets proportional to the final diff.
Confirm credentials, provider calls, spend, private objects, scientific
inventories, and paper/PDF bytes remain unchanged.

## Commands and expected observations

Registration and focused implementation:

    make audit-agent-ops
    make audit-program-memory
    pytest -q tests/unit/test_treasurebench_provider_schema_conformance.py

Pre-gate acceptance:

    make bootstrap
    make audit-agent-ops
    make audit-program-memory
    make audit-agents-v1
    make audit-agents-v1-evaluation
    make agents-v1-dry-run
    make agents-v1-readiness
    make verify
    make owner-gate GATE=<committed-manifest> OWNER_GATE_VALIDATE_ONLY=1

Expected: all commands exit zero; paid calls, credential reads, private-state
changes, scientific mutations, releases, and paper changes remain zero.

Observed through M3: the fixture audit rebuilt five request fixtures and the
matrix byte-identically; 46 focused tests passed; Ruff format and lint passed
over 319 files; strict MyPy passed over 191 source files; Agent Operations and
program-memory audits passed. Provider calls, credential reads, private-state
access, and spend remained zero.

Observed at the M4 execution freeze: bootstrap, Agent Operations,
program-memory, provider-schema, benchmark, evaluation, offline dry-run, and
offline readiness audits passed; Ruff and strict MyPy passed; all 476
repository tests passed; claim and 51 run manifests validated; and the
compendium release dry-run verified offline. No credentials were read, no
provider execution call was made, no private state was accessed, and spend
remained USD 0.

Observed for the corrected M4R candidate: the fixture builder produced nine
serialized requests byte-deterministically; 58 focused provider-schema and
runner tests passed; Ruff passed over 321 files; strict MyPy passed over 192
source files; all 488 repository tests passed; claim and 51 run manifests
validated; and the compendium release dry-run verified offline. The runner
itself was not invoked because no R2 authorization exists. Credential reads,
provider calls, private-state accesses, and spend remained zero.

## Artifacts produced

- `tasks/treasurebench-provider-schema-conformance.yml`
- `plans/TREASUREBENCH_PROVIDER_SCHEMA_CONFORMANCE.md`
- provider documentation audit and public serialized request fixtures
- provider-specific conformance code and regression tests
- exact repository-native command `make treasurebench-provider-schema-canaries`
  and its append-only public-engineering ledger implementation
- nine serialized request fixtures, including four frozen bisection candidates
- one exact committed generic AO-0004 owner-gate manifest
- one schema-valid owner-gate-required handoff

## Blockers

The unused R1 gate is superseded by owner amendment and may not be consumed.
The active work is the offline M4R correction. Credentials, provider calls,
private-state access, and spend remain blocked until a future exact R2 owner
authorization exists.

## Recovery and restart instructions

Start from the task branch and draft PR named by the latest AO-0004 handoff.
Read the fixed task contract, this plan, root and scoped instructions, and the
official-source audit. Leave unrelated untracked files untouched. Do not read
credentials, archived authorization contents, or private state. Before any
post-gate work, validate the exact active authorization, frozen execution
commit, branch/PR ancestry, protected trees, exact routes/models, call and
spend caps, and prohibitions; stop on any mismatch.

## Outcome and retrospective

The R1 offline conformance repair, execution surface, gate, and handoff were
committed but never authorized. The owner amendment supersedes that checkpoint
before use and reopens AO-0004 for a corrected OpenAI schema audit and exact
committed runner. R2 outcome is pending. Credential access, provider calls,
spend, private state, and scientific state remain zero.
