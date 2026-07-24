# TreasureBench Agents v1 sealed engineering pilot

## Purpose and intended outcome

Register, implement, freeze, and—only after exact owner authorization—run one
private, cryptographically sealed, two-cloud TreasureBench Agents v1
engineering pilot. The campaign is `treasurebench-agents-v1-pilot-v1`, batch
`tb-agents-v1-pilot-v1-b01`, with 50 tasks, five families, five architectures,
two exact direct cloud snapshots, one repeat, output lock before unsealing,
and independent Method A/Method B verification.

The pilot is DD-010 instrument engineering. It is non-inferential and cannot
create DD-023, a claim, an immutable scientific run, a paper result, a
leaderboard, a composite score, or authority for the 200-task base campaign.

## Live state

Baseline audit completed at `2026-07-24T15:52:58Z`.

- starting and current `main`:
  `0d3757caf322402c0c47117b3aff0490926a133d`;
- issue: #187;
- draft pull request: #188;
- branch: `benchmark/treasurebench-agents-v1-sealed-pilot`;
- Phase A implementation commit:
  `05bc58e986e34019b59e84a181b8d17789987eac`;
- replacement staged-driver commit:
  `d5b3a23a4c61fc47971f389bc04a0283c87c85b4`;
- current frozen execution-tree hash:
  `sha256:2f4861759237e419e6901ecc3e6b09385712cc9e47912c0944cb3f9e0a8700a7`;
- open substantive pull requests before branch creation: none;
- unrelated open issue #32: settings-only and not a blocker;
- release: annotated `dd-compendium-v0.1.0`, GitHub Release and Zenodo record
  21535005 verified; version DOI `10.5281/zenodo.21535005` and concept DOI
  `10.5281/zenodo.21535004` resolve;
- scientific inventory: 110 claims through DD-C-0110, 26 studies through
  DD-022, 51 manifests, 48 passing immutable runs, no DD-023 or DD-C-0111;
- papers: seven accepted PDFs, 119 pages, registered hashes unchanged;
- source/tests/site: MyPy passes 181 sources, all 369 tests pass, and the
  naming audit reports 89 site pages;
- TreasureBench Agents v1: 138 generator cells, five families, five agent
  architectures, 15 metrics, 24 instrument corruptions, semantic rehearsal
  hash `sha256:d3410ff04bb73dcae929c3abc4cf289d58d6830f2a5ab50ca53764bef4af2c59`;
- public provider calibration: 607 preserved calls, USD 2.311758000,
  direct OpenAI and Anthropic ready, Method A/B agreement and contamination
  checks passing; optional OpenRouter routes ineligible and not substitutes;
- credential source `.env.txt`: ignored, untracked, unstaged, regular file,
  mode 0600; values were not loaded during Phase A audit;
- pinned upstream:
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`, clean detached checkout,
  PDF SHA-256
  `cb4816cb3a9cdd8db0210ab8981e3729028eb02ba174f2a7300b617807cc1e04`.

Preserve, never read, edit, move, delete, normalize, clean, or stage:

- `papers/information-sharing-frontier/paper-audit 2.json`
- `papers/information-sharing-frontier/visual-qa 2.md`
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`

The first claim-inventory query used the nonexistent key `claim_id` and
stopped with `KeyError`; the corrected read used canonical key `id` and
confirmed DD-C-0110. No file changed.

## DISCUSSION AND DECISION DELTA AUDIT

The pre-issue audit read all 30 program-memory records. The automated audit
found zero owner-adopted unrouted items, zero duplicate canonical records, and
zero raw transcripts.

- PM-0030 first stable compendium release: implemented and directly verified.
- PM-0026/PM-0027 TreasureBench/Treasure Hunt naming: implemented; frozen
  DiscoveryBench identifiers remain compatibility authority.
- Public provider calibration: implemented as engineering evidence only.
- Sealed engineering pilot: due and routed to issue #187 and this ExecPlan.
- Claim-grade base campaign: not due; blocked on a feasible local/open model
  and separately gated registration and owner authorization.
- PM-0014 benchmark paper and PM-0015 recomposition: remain
  evidence-dependent because claim-grade evidence does not exist.
- PM-0009 Common-Source Trap: remains the first internal paper-freeze
  candidate; this task authorizes no paper action.
- PM-0016/PM-0017 AI-only lab and no active human workflow: unchanged.
- No pilot-relevant owner decision remains only in conversation; the supplied
  brief, issue #187, and tracked contracts are the durable authority.

Repeat this audit before issue closeout. This section is governance metadata,
not scientific evidence.

## Source-of-truth boundary

Git owns public design, schemas, exact model and architecture contracts,
allocation slots, execution-sensitive code and tree hash, public commitments,
redacted engineering records, verification, corruptions, and decisions.

The local non-synthetic authorization owns permission for the exact execution
commit, branch, issue, campaign, batch, private generation, provider calls,
encryption, unsealing, retention, and caps. It is never committed.

Private encrypted state exists only under the symbolic XDG state location and
is not scientific authority. Claims, studies, immutable runs, papers,
ActiveGraph, SQLite, and canonical upstream remain unchanged.

## Fixed owner decisions

- owner study: DD-010; no new study or claim;
- providers/models: direct OpenAI `gpt-5.4-2026-03-05` and direct Anthropic
  `claude-sonnet-4-6`, no substitution, fallback, or moving alias;
- no local model and no OpenRouter in the pilot;
- 50 tasks, one batch, ten per family, one repeat, five architectures;
- registered plan: 4,800 calls, 9,600,000 input tokens, 1,228,800 output
  tokens, USD 44.832 estimate and USD 56.04 contingency;
- authorization maxima: 5,200 calls, 10,600,000 input tokens, 1,400,000
  output tokens, USD 100 total and USD 50 per provider;
- maximum live concurrency: two providers;
- metrics stay separate; no ranking or composite;
- encrypted raw traces retained 365 days after closeout; deletion requires a
  later logged owner authorization;
- hidden chain of thought is never requested, collected, inferred, stored, or
  scored.

## Scope

Implement the pilot request, pilot-specific authorization, deterministic
allocation, private-state contract, allocation-bound generator, AES-256-GCM
custody, append-only access/call/cost ledgers, resumable runner, exact cost
guards, encrypted traces, deterministic redaction, output lock, unsealing
gate, independent verifier, contamination checks, at least 35 pilot
corruptions, CLI/Make interfaces, synthetic rehearsal, execution freeze,
owner checkpoint, and—only if authorized—Phase B execution and closeout.

## Non-goals

No DD-023, DD-C-0111, scientific run or claim, paper/PDF/lifecycle change,
package, release, tag, DOI, arXiv, journal, leaderboard, composite, provider
superiority claim, ActiveGraph, SQLite, upstream mutation, human scoring,
human custody, hidden reasoning, OpenRouter, local model, hosted Mistral,
Gemini, FlyMyAI, Monid, moving alias, or base campaign.

## Campaign request

The source of truth is
`docs/benchmark/agents-v1/treasurebench-pilot-request.yml`. It binds the
campaign and batch IDs, exact routes, architecture set, counts, caps,
retention, authorization location, and execution-sensitive path set without a
self-referential execution commit.

## Private allocation

`docs/benchmark/agents-v1/treasurebench-pilot-allocation.yml` freezes 50
generator-cell slots, ten per family, with balanced target/agent relabeling
classes, strict/tie/boundary and parser/protocol coverage, public-calibration
and future-base exclusions, and no seed, task text, answer, or outcome-based
selection.

## Providers and models

Current official documentation was rechecked on 2026-07-24. OpenAI still
lists the exact GPT-5.4 snapshot, Responses endpoint, structured outputs,
USD 2.50/15.00 per million input/output tokens, and no deprecation marker.
Anthropic documents `claude-sonnet-4-6` as a pinned dateless 4.6 snapshot,
Messages API structured outputs, USD 3/15 per million input/output tokens,
active status, and retirement no earlier than 2027-02-17. Newer models do not
change the frozen pilot identity.

## Authorization

The pilot-specific schema and validator bind all fixed identities, counts,
caps, permissions, prohibitions, expiration/revocation, and a non-synthetic
owner attestation. Historical issue-#173 authorization remains unchanged.
Synthetic fixtures are marked synthetic and can never authorize live mode.

## Execution-sensitive freeze

The request defines the complete path set. At M13, all sensitive files are
committed, the exact commit and deterministic tree hash are recorded, the
remote head is verified, and later mutation invalidates authorization.
Post-authorization changes are limited to public commitment, ledger, redacted
report, status, and closeout files.

## Credentials

Only `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` may be loaded, and only after an
exact live authorization passes. The strict nonexecuting dotenv parser never
executes or interpolates content. Diagnostics expose names/presence only.
CI and synthetic rehearsal never read `.env.txt`.

## Budget and cost guard

Every planned and actual call is checked before dispatch against total,
provider, call, input-token, and output-token caps. Projected next-call
exposure stops execution before a breach. The append-only ledger is the
resume authority and forbids a duplicate call after a recorded success.

## Private-state layout

Only symbolic XDG locations appear publicly. Runtime directories are 0700 and
files 0600, created atomically without symlinks. Objects include separate seed,
task key, answer key, ciphertexts, access log, encrypted traces, usage/cost
ledger, output lock, unsealed audit working set, and encrypted final audit
package. Private cleanup refuses without logged deletion authorization.

## Seed, task, and answer custody

After authorization and public canaries, OS CSPRNG material is generated.
Domain-separated commitments bind campaign, batch, allocation, seed, tasks,
and answers. Tasks and answers use independent AES-256-GCM keys/nonces and
associated data. Agents cannot access evaluator primitives, keys, answers,
generator internals, exact comparators, or undeclared signals.

## Trace and redaction

Raw visible-message/action/usage/error operational traces are encrypted at
rest. Event and whole-trace hashes, provider request/model IDs, usage, cost,
latency, finish status, and retry class are retained. Credentials, headers,
seed, answers, hidden target before unseal, host paths, PII, proprietary data,
and hidden reasoning are prohibited. Public records contain redacted counts
and commitments only.

## Output lock and unsealing

Provider phase closure hashes every encrypted output, trace, usage/error
record, access log, and cost ledger. No answer or task unseal is permitted
before the immutable output-lock manifest exists. No calls may be inserted
after lock.

## Metrics and Method A/B

Method A computes the registered vector. Method B reconstructs tasks,
information rights, action validity, exact baselines, every metric, counts,
model identity, usage/cost, commitments, hashes, exclusions, and redaction
from primitive records without importing Method A classifications. Any
deterministic disagreement quarantines the pilot.

## Corruptions and contamination

Phase A uses synthetic fixtures for at least the 35 named pilot corruptions.
Each mutation must reject at its intended boundary. Direct or probable
contamination quarantines the real pilot; lexical overlap alone is
inconclusive.

## Public/private result boundary

Public records may disclose identities, counts, commitments, total/provider
usage and cost, operational errors/invalid/refusal counts, protocol
diagnostics, verification/redaction/corruption/contamination status,
quarantine, retention, and final engineering decision.

Private task text, seed, keys, answers, prompts, outputs, detailed task/model/
architecture metrics, unredacted errors, rankings, composites, or inferential
statements never enter Git.

## Milestones

0. M0 baseline audit, mandatory reading, issue, branch, plan.
1. M1 registration decision.
2. M2 request and schema.
3. M3 pilot authorization schema, validator, fixtures.
4. M4 private-state contract.
5. M5 deterministic 50-slot allocation.
6. M6 private generator and custody runtime.
7. M7 resumable guarded runner.
8. M8 trace and redaction runtime.
9. M9 output lock and independent verifier.
10. M10 corruptions and contamination.
11. M11 CLI and Make interfaces.
12. M12 offline sealed rehearsal.
13. M13 execution freeze, push, draft PR, owner checkpoint.
14. M14 authorization/freeze revalidation.
15. M15 public exact-route canaries.
16. M16 real private custody and public commitments.
17. M17 private 10% prefix gate.
18. M18 complete fixed batch.
19. M19 output lock.
20. M20 unseal and Method A.
21. M21 Method B.
22. M22 safety, contamination, and corruptions.
23. M23 redacted engineering summary.
24. M24 roadmap/site reconciliation.
25. M25 validation, merge, Pages, live acceptance, issue closeout, main sync.

Execute sequentially. M0-M13 are complete. The first M14 revalidation passed,
then exposed that the frozen `pilot-live` entry point stopped at the guard and
did not drive the registered stages. No provider call or real private
generation occurred. The execution-sensitive repair is committed and pushed;
M14 must now be repeated against a fresh authorization for the replacement
commit before M15-M25.

## Progress checklist

- [x] M0 mandatory reading and baseline audit.
- [x] M0 issue #187 and exact branch created.
- [x] M0 living plan created.
- [x] M1 registration decision.
- [x] M2 request/schema.
- [x] M3 authorization.
- [x] M4 private-state contract.
- [x] M5 allocation.
- [x] M6 custody.
- [x] M7 runner.
- [x] M8 traces/redaction.
- [x] M9 output lock/verifier.
- [x] M10 corruptions/contamination.
- [x] M11 CLI/Make.
- [x] M12 rehearsal.
- [x] M13 freeze, push, draft PR #188, and authorization checkpoint.
- [ ] M14 authorization and freeze revalidation (**fresh authorization required
  from the clean checkpoint containing replacement commit `d5b3a23`**).
- [ ] M15-M25 remaining Phase B milestones.

## Discoveries and surprises

- Official OpenAI and Anthropic catalogs now list newer model generations, but
  both frozen pilot IDs remain available, fixed, structured-output-capable,
  and not deprecated. The fixed owner decision therefore remains executable.
- The OpenAI Developer Docs MCP was absent; it was registered globally once,
  but a restart would be required. The audit used official OpenAI web pages as
  the skill-directed fallback. No provider API was called.
- The existing repository already supplies strict direct adapters, exact
  orchestration, evaluator/Method B components, redaction, and public-toy
  AES-256-GCM custody. Pilot work extends rather than replaces them.
- The frozen allocation initially balanced target relabeling 26/24 despite its
  audit text claiming 25/25. Slot 050 was corrected before any private
  generation; target and agent classes now both validate at 25/25.
- The complete Phase A rehearsal covers 500 synthetic route/task/architecture
  runs and 500 encrypted traces. All 35 owner-named corruptions plus 41
  additional checks reject, for 76/76 total.
- The first exact M14 revalidation passed without printing credentials or
  authorization contents. Inspection immediately afterward found that the
  frozen live CLI was guard-only. Per the freeze rule, no provider call or real
  private generation was attempted; the authorization was invalidated.
- The replacement driver advances one stage at a time and enforces a committed,
  pushed custody record before the prefix plus a committed, pushed output-lock
  record before unsealing. Its exact synthetic mock completed 500 private runs,
  3,016 simulated provider attempts including canaries, Method A/B agreement,
  zero contamination/protocol findings, and zero new calls on full resume.

## Decision log

- `2026-07-24T15:52:42Z`: issue #187 created after confirming no competing PR.
- `2026-07-24T15:52:58Z`: branch created from exact main
  `0d3757caf322402c0c47117b3aff0490926a133d`.
- `2026-07-24T15:52:58Z`: preserve the five unrelated files and never use
  `git add .`.
- `2026-07-24T15:52:58Z`: keep pilot under DD-010 and retain base campaign as
  separately gated.
- `2026-07-24`: complete M1-M12 with synthetic material only; no credential
  read, provider call, real private state, or cost.
- `2026-07-24T16:26:34Z`: push Phase A implementation commit `05bc58e`,
  verify execution-tree hash `sha256:a6cd789f8f05c049ed5b86dfec551c6ea73ed99797a959f77bda755782ef773c`,
  and open draft PR #188. M13 is complete.
- `2026-07-24T17:28:18Z`: validate the first non-synthetic owner
  authorization, exact execution identity, secure credential-file metadata,
  configured direct keys, caps, permissions, issue, branch, campaign, and
  batch; make no call and create no real private state.
- `2026-07-24T17:51:28Z`: after detecting the guard-only live entry point,
  commit and push execution-sensitive repair `d5b3a23`; freeze tree hash
  `sha256:2f4861759237e419e6901ecc3e6b09385712cc9e47912c0944cb3f9e0a8700a7`.
  The previous authorization is no longer valid.

## Validation strategy

Phase A requires request/authorization/allocation/private-state/custody/
runner/cost/trace/lock/verifier/corruption/CLI tests, a complete 50-slot
synthetic sealed rehearsal, all pilot Make audits, `git diff --check`,
bootstrap, full verify, papers, and site. Live mode must fail closed.

Phase B adds exact authorization/tree/credentials/canary/custody/prefix/cap/
lock/unseal/Method A/B/contamination/corruption/private-leak/redaction checks.
Final validation repeats every repository audit and exact scientific/paper
invariant.

## Commands and expected observations

Use the commands in the owner brief. Offline commands must report no network,
provider call, credential read, or real private material. Live commands must
fail without exact authorization and resume only from the append-only ledger.

## Artifacts produced

This plan, issue #187, the pilot request/authorization/private-state/allocation
contracts, Phase A runtime and tests, synthetic readiness record, execution
freeze, draft PR, and—if authorized—public commitments and redacted closeout.

## Blockers

Phase A has none. Phase B is blocked until a fresh matching non-synthetic local
owner authorization exists for the clean checkpoint containing replacement
commit `d5b3a23` and tree hash
`sha256:2f4861759237e419e6901ecc3e6b09385712cc9e47912c0944cb3f9e0a8700a7`.

## Recovery and restart instructions

1. Work only in this repository and exact branch.
2. Read issue #187 and this plan.
3. Inspect `git status`; preserve the five unrelated files.
4. Resume the first unchecked milestone; exactly one is active.
5. Before any live/private action, validate authorization, branch, issue,
   campaign, batch, commit, tree hash, credentials, caps, and remote ancestry.
6. Never modify an execution-sensitive file after authorization.
7. Never duplicate a paid call already marked successful.

## Outcome and retrospective

Phase A completed at the owner-authorization checkpoint. The 50-slot
public-synthetic sealed rehearsal and all 76 corruption cases pass; repository,
paper, and site acceptance pass; the execution-sensitive tree is frozen and
pushed; and draft PR #188 records the checkpoint. No credential was read, no
provider was called, no real private material was created, and no cost was
incurred.

The exact next action is for the owner to run the supplied helper against this
branch and its final pushed checkpoint commit, then resume the same session.
Any execution-sensitive edit invalidates the tree hash and authorization.
