# AO-0009 TreasureBench AO-0008 fixed-full-batch adjudication

## Purpose and intended outcome

This living ExecPlan governs `AO-0009`, a DD-010 engineering-only task with
two phases. Phase A audits the public AO-0008 runtime and implements one
owner-gated, one-use, read-only diagnostic for the retained fixed-full-batch
failure. Phase B uses only the evidence admitted by that bounded diagnostic
to select the appropriate prospective implementation repair, provider
reliability policy gate, agent-protocol policy gate, or honest stop. The task
does not register or execute another private pilot.

The permitted final outcomes are:

- `fixed-batch-root-cause-repaired-full-rehearsal-pass`;
- `provider-reliability-policy-decision-required`;
- `agent-protocol-policy-decision-required`;
- `fixed-batch-diagnostic-inconclusive-defer`;
- `retained-state-integrity-mismatch-stop`.

No outcome is selected before the one-use diagnostic.

## Current state

Registration preparation began on `2026-07-28` from local `main` matching
`origin/main` at `693adaa`. AO-0008 issue #204 and PR #205 are closed and
merged. No substantive pull request is open. The next available Agent
Operations ID is `AO-0009`; issue #206 and branch
`codex/treasurebench-ao0008-fixed-batch-adjudication` now own the substantive
lane.

Five unrelated untracked preservation files pre-exist and are outside scope:

- `papers/information-sharing-frontier/paper-audit 2.json`;
- `papers/information-sharing-frontier/visual-qa 2.md`;
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`;
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`;
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`.

They must remain untouched. Provider calls, credential reads, spend, new real
private material, scientific mutation, paper action, release, and submission
are all zero. The R1 execution freeze and owner-gate handoff were reached
without authorization or retained access. At
`2026-07-29T00:03:24Z`, the owner issued a preauthorization correction because
the frozen runtime persists all 450 traces before its aggregate gates. The
unused R1 gate is prospectively superseded.

The exact R2 owner gate succeeded against frozen diagnostic commit
`fbecbfb89e634967d48931c00e1d8a4fbed81c79` and all twenty protected hashes.
The diagnostic then ran exactly once. It verified the immutable retained
boundary, authenticated all 450 fixed-full-batch traces, emitted only the
allowed public aggregate, and permanently closed private-read authority. The
evidence selected `agent-protocol-policy-decision-required`; AO-0009 makes no
silent protocol normalization, retry, credit, or prospective implementation
repair. Exactly one milestone is active: **M8 — public-safe closeout**.

The AO-0008 boundary is permanent: task `AO-0008`, campaign
`treasurebench-agents-v1-repair-confirmation-v3`, batch
`tb-agents-v1-repair-confirmation-v3-b01`, execution commit
`0f9d82bb50cbb334bea47e24448831faf0cdbed8`, decision
`fresh-pilot-v3-quarantined-engineering-only`, stage `fixed-full-batch`,
failure class `fixed-full-batch-failure`, two passed public canaries, passed
custody and private prefix, 3,067 calls, 2,304,303 input tokens, 444,085 output
tokens, USD 13.1861145 total cost, OpenAI USD 4.5952575, Anthropic USD
8.590857, 3,576 locked objects, output lock
`sha256:e52055b08ca3a8acb1cfb6ac608c6e601f3c618352900f92bf91c5ffc4718dbb`,
closed provider phase, zero calls after lock, no unsealing, and no scientific
or performance evidence.

## DISCUSSION AND DECISION DELTA AUDIT

The complete 36-record `docs/program-memory/registry.yml` was read before
issue or branch creation.

- `PM-0032` is due because the owner explicitly selected another
  repository-native Agent Operations task. It remains implemented and is
  applied through the AO-0009 contract, ExecPlan, generic owner gate, and
  typed handoff.
- `PM-0036` is due because the owner selected adjudication of AO-0008's
  permanent fixed-full-batch quarantine. It remains immutable. The follow-up
  is routed to new record `PM-0037`, this ExecPlan, the fixed AO-0009
  contract, and the future public-safe diagnostic record.
- `PM-0031`, `PM-0033`, `PM-0034`, and `PM-0035` remain implemented
  prerequisites and permanent quarantine or repair boundaries. None is
  reopened or superseded.
- `PM-0014` and `PM-0015` remain evidence-dependent because no claim-grade
  Agents v1 evidence exists. Journal, paper, release, rename, local/open-model,
  theorem, retrievability, and publication triggers remain unfulfilled.
- The difference between 3,067 actual attempts and 3,016 normal calls is
  recorded only as an operational observation and is not routed as a cause.

No owner decision from this intake remains conversation-only. `PM-0037`, the
additive R2 contract, this plan, issue, R2 gate, public outcome, and typed
handoff now carry the complete route. The closeout delta audit preserves all
37 memory records, marks PM-0037 implemented, and creates no new scientific,
paper, release, submission, or private-evaluation authority.

The `2026-07-29` amendment is routed to additive R2 contract
`tasks/treasurebench-ao0008-fixed-batch-adjudication-r2.yml`, updated PM-0037,
this plan, and the future R2 gate and handoff. It preserves every prior
boundary, makes no scientific decision, and supersedes only the unused
one-trace authority surface.

## Scope

1. Register AO-0009 with one issue, task branch, fixed task contract, living
   ExecPlan, and draft pull request.
2. Audit public AO-0008 runtime, control flow, ledgers, encrypted-object
   indexing, pairing bookkeeping, state transitions, failure policy,
   quarantine, and output-lock inventory.
3. Freeze a causal taxonomy spanning provider transport and HTTP terminals,
   schema repair, returned-output parsing, protocol/cardinality, encryption,
   persistence, ledgers, duplicate keys, caps, pairing, completion markers,
   post-batch verification, and bounded-evidence unknowns.
4. Implement one authorization-bound, one-use, read-only diagnostic with an
   exact allowlist, structural object ceilings, pre/post byte and metadata
   snapshots, and permanent read-authority closure.
5. Authenticate aggregate-only fields from exactly all 450 fixed-full-batch
   traces, and read only one selected logical-call context, at most two
   corresponding encrypted provider responses, at most two preceding and two
   following operational records, and one transient operational key.
6. Write one detailed nonpublic diagnostic outside Git and emit only a
   redacted public-safe result.
7. Add synthetic fixtures, corruptions, deterministic fault injection,
   redaction checks, and retained-state immutability tests.
8. After exact authorization, select and execute only the evidence-determined
   prospective branch, then complete permitted public-safe reconciliation,
   validation, merge, CI/Pages, named-route verification, issue closure, and
   synchronized `main`.

## Non-goals

- No reopening, retrying, continuing, executing, reusing, rescoring, splicing,
  mutating, deleting, broadly unsealing, or reauthorizing AO-0008.
- No second private read and no bulk response, trace, task, answer, or custody
  unsealing.
- No OS-CSPRNG seed value, task key, answer key, task or answer ciphertext,
  custody task corpus, answer key, hidden target, unrelated provider response
  or trace, task-level performance, comparison, credential, or private host
  path may be read or disclosed.
- No provider call, credential read, spend, new real private material, new
  campaign or batch identity, or v4 registration.
- No DD-023, claim, scientific run, proof or evidence promotion, paper result,
  ranking, composite, package, release, DOI, submission, or base-campaign
  authority.

## Assumptions

- The public AO-0008 closeout is authoritative only for its declared redacted
  boundary and does not establish the detailed cause.
- Public source may identify causal candidates but cannot select a final
  outcome before the bounded retained-state diagnostic.
- Structural response and trace filenames can be checked against ledger and
  expected pairing identities without reading their encrypted contents.
- If the exact cause cannot be established by one bounded read, the correct
  result is `fixed-batch-diagnostic-inconclusive-defer`; no broader read is
  implied.
- Synthetic fixtures are nonsecret, disposable, and isolated under temporary
  roots; they create no real private campaign material.

## Milestones

- **M0 — complete:** reconcile program memory and live GitHub/repository state;
  register the issue, branch, fixed contract, ExecPlan, and PM-0037 route.
- **M1 — complete:** complete the public runtime, control-flow, ledger,
  encrypted-index, pairing, state, failure, quarantine, and lock audit.
- **M2 — complete:** freeze the causal taxonomy and exact one-use private-read
  allowlist and object/record ceilings.
- **M3 — complete:** implement the authorization-bound read-only diagnostic,
  one-use and no-mutation guards, redaction, synthetic fixtures, and
  corruptions.
- **M4 — complete:** run focused and complete authorization-free validation and
  open the draft pull request.
- **M5 — superseded unused:** R1 froze diagnostic commit `b7a3345`, committed
  and validate-only checked the original gate, and produced the typed handoff;
  no authorization or retained read occurred.
- **M5R2 — complete:** implement the aggregate-only 450-trace correction,
  exact-set structural verification, causal precedence, fixtures, corruptions,
  full validation, R2 execution freeze, R2 gate, and replacement handoff.
- **M6 — complete:** after exact authorization, execute the diagnostic once,
  close private-read authority permanently, and select one permitted outcome.
- **M7 — complete:** record the evidence-determined agent-protocol policy gate
  without changing protocol acceptance, retry, normalization, or scoring.
- **M8 — active:** reconcile public-safe records, repeat the delta audit,
  validate, merge after checks, verify CI/Pages and named routes, close the
  issue, and synchronize `main`.

## Progress checklist

- [x] Read the task intake, root and scoped instructions, planning policy,
  master plan, repository contract, Agent Operations policy, DD-010 README,
  plan, and status.
- [x] Inspect Git, remote, untracked preservation files, recent AO state,
  closed AO-0008 issue/PR, open pull requests, and next AO ID.
- [x] Read and reconcile all 36 program-memory records before issue or branch
  creation.
- [x] Create issue #206 and branch
  `codex/treasurebench-ao0008-fixed-batch-adjudication`.
- [x] Validate the fixed task contract, this living ExecPlan, PM-0037, and
  master-plan registration with Agent Operations and program-memory audits.
- [x] Commit the fixed task contract, this living ExecPlan, PM-0037, and
  master-plan registration as `469c45b`.
- [x] Complete the public runtime, ledger, pairing, quarantine, and output-lock
  audit without resolving retained private state.
- [x] Freeze all fourteen causal classes and the exact five-record,
  3,067-response-envelope, 502-trace-envelope allowlist.
- [x] Implement generic-authorization binding, one-use and no-mutation guards,
  bounded selection, at-most-three-object decryption, transient
  operational-key handling, redaction, schema validation, and integrity stop.
- [x] Pass 18 focused tests, focused Ruff and MyPy, all fifteen classifier
  fixtures, the exact-scale 3,576-object synthetic diagnostic, and the
  complete 50-task/500-pairing rehearsal.
- [x] Commit M1-M3 as `7614365`, push the branch, and open draft PR #207.
- [x] Fix the single full-wall schema inventory expectation from 41 to 42
  without changing runtime or authority.
- [x] Pass the complete authorization-free validation wall: bootstrap, Agent
  Operations, program memory, Agents v1 audit/evaluation/dry run/readiness,
  AO-0009 audit and rehearsal, formatting, Ruff, strict MyPy over 202 source
  files, 656 tests, 110 claims, 51 immutable run manifests, governance and
  publication audits, and offline release verification.
- [x] Commit and push R1 diagnostic freeze `b7a3345`, validate the unused R1
  gate, and render its handoff without authorization or retained access.
- [x] Commit additive R2 correction `89d0100` and route the amendment durably.
- [x] Implement the aggregate-only 450-trace R2 diagnostic and pass focused
  validation.
- [x] Freeze R2 at `fbecbfb`, supersede R1 without use, commit and validate the
  R2 gate and replacement handoff, and stop before retained access.
- [x] Pass the exact R2 owner gate, revalidate all frozen boundaries, and run
  `make treasurebench-fixed-batch-read-only-diagnostic` exactly once.
- [x] Verify the lock, inventory, append-only ledgers, complete response
  correspondence, 2/50/450 trace partition, all 500 pairing records, retained
  immutability, zero provider/credential/spend caps, and permanent closure of
  private-read authority.
- [x] Select `agent-protocol-policy-decision-required` from the public
  aggregate and preserve protocol changes for a separate explicit owner task.
- [x] Complete public-safe reconciliation and pass the complete validation
  wall.
- [x] Ready and squash-merge PR #207 after both exact-head CI runs pass.
- [x] Verify the first post-merge CI and Pages workflows.
- [ ] Correct the stale program and TreasureBench Agents v1 route sources
  found during named live-route verification, verify the corrective CI/Pages
  cycle and all five routes, close issue #206, synchronize `main`, and record
  the terminal handoff.

## Discoveries and surprises

- `2026-07-28`: public source shows that `PilotBatchRunner.run_stage` persists
  each run trace, accumulates protocol errors, and may raise an aggregate
  protocol-gate exception only after the stage loops finish. This is a causal
  candidate for a false completion-marker boundary, not a diagnosis of
  AO-0008.
- `2026-07-28`: the public runtime records provider attempts and encrypted
  responses by logical call key, but does not append a distinct orchestration
  ledger record for every completed pairing. Structural trace-name
  commitments must therefore supply independent pairing completeness without
  bulk decryption.
- `2026-07-28T20:42:34Z`: the exact-scale disposable fixture passes with 3,067
  response envelopes, 502 trace envelopes, all 3,576 locked objects, 3,016
  base logical calls, 500 private pairings, a false completion marker, one
  selected logical call, four neighbors, one selected response, one selected
  trace, no retained mutation, and deterministic cleanup. Its injected
  nonsecret schema-repair failure classifies correctly. This fixture is not
  evidence about AO-0008.
- `2026-07-28T20:49:34Z`: the first full authorization-free wall passed
  bootstrap, all governance and Agents v1 audits, the AO-0009 exact-scale
  rehearsal, formatting, Ruff, strict MyPy over 202 source files, and 655 of
  656 tests. The sole failure was the exact Agents v1 schema-inventory
  regression still expecting 41 schemas after adding the public diagnostic
  schema. Update the hand-checkable expected count to 42 and rerun the
  complete wall; no runtime, authority, or private boundary changes.
- `2026-07-28T20:56:20Z`: the complete wall passes after the exact schema
  inventory correction: 656 tests, 202 MyPy source files, 110 claims, 51
  immutable run manifests, all governance and benchmark audits, and offline
  release verification. No retained AO-0008 state, authorization, credential,
  provider, spend, new private material, scientific record, paper, release,
  or submission surface was accessed or changed.
- `2026-07-29T00:03:24Z`: public source establishes a defect in the unused R1
  authority surface: `PilotBatchRunner.run_stage` persists every trace inside
  the loop and raises aggregate contamination and protocol failures after the
  loops. The sole triggering event may therefore occur in any one of 450
  traces. The live stage used `verify_metrics=false`, so Method A/B and
  metric-range failures were not computed and cannot be immediate causes.
- `2026-07-29T00:14:15Z`: the R2 implementation no longer selects a trace by
  mtime. It requires complete 3,067-attempt/response domain-set equality,
  unique 2/50/450 trace partitioning, authenticates and extracts only
  aggregate signals from all 450 full-batch traces, retains one bounded call
  with two responses and four neighbors, and publishes no provider, model,
  architecture, task, trace-identity, output, action, metric, or performance
  dimension. Twenty-five focused tests pass, including first/middle/final
  contamination and protocol events plus response substitution, orphan,
  duplicate/conflict, missing trace, leakage, and second-read corruptions.
  Exact-scale 3,067-response/502-trace/3,576-object and full
  50-task/500-pairing rehearsals pass.
- `2026-07-29T00:16:48Z`: the first complete R2 wall passed formatting, Ruff,
  strict MyPy over 202 source files, and 659 of 663 tests. Four unchanged
  historical pilot mock tests failed because their safety boundary requires
  the synthetic authorization's current execution commit to be present on a
  remote branch, while R2 milestone commit `9228349` had intentionally not
  yet been pushed. This is a preserved sequencing failure, not an R2
  diagnostic or historical pilot regression. Push the scoped milestone and
  rerun the complete wall from the identical tree.
- `2026-07-29T00:22:40Z`: after pushing the scoped milestone, the complete
  wall passes: formatting over 343 files, Ruff, strict MyPy over 202 source
  files, all 663 tests, 110 claims, 51 immutable run manifests, Agent
  Operations and program-memory audits, benchmark and governance checks, and
  offline verification of seven papers and 119 pages. The exact-scale R2
  rehearsal and 500-pairing rehearsal remain passing. No authorization,
  retained-state read, provider call, credential read, spend, private
  material, scientific mutation, publication action, release, or submission
  occurred. The next commit is the R2 diagnostic execution freeze.
- `2026-07-29`: the exact R2 gate succeeded against execution commit
  `fbecbfb89e634967d48931c00e1d8a4fbed81c79` and twenty protected hashes.
  The one-use diagnostic authenticated the output lock, 3,576-object
  inventory, append-only ledgers, complete 3,067 response-attempt identity
  correspondence, the unique 2/50/450 trace partition, all 450 fixed-batch
  traces, and all 500 pairing records. The completion marker is absent after
  3,016 completed logical calls. No retained state changed, no operational
  key was retained, and provider calls, credential reads, and spend were zero.
- `2026-07-29`: the allowed aggregate reports 32 protocol-nonconforming
  traces, 32 parse/schema-repair exhaustion traces, zero terminal provider
  attempts, zero contamination traces, zero invalid final-cardinality traces,
  and no cap-guard trigger. Under frozen precedence, this selects
  `protocol-contract-nonconformance` with evaluated-agent actor and requires
  an agent-protocol policy decision. It does not justify a silent local
  repair.
- `2026-07-29T01:10:29Z`: public-safe reconciliation passes the complete
  validation wall: formatting over 343 files, Ruff, strict MyPy over 202
  source files, all 663 tests, 110 claims, 51 immutable run manifests,
  Agent Operations and program-memory audits, benchmark and governance
  checks, 89 site pages, and offline verification of seven papers and 119
  pages. The task-specific 25-test suite, exact-scale diagnostic fixture, and
  50-task/500-pairing rehearsal also pass without retained access.
- `2026-07-29T01:27:14Z`: PR #207's two exact-head CI runs pass and the PR
  squash-merges as `0835efe39450a2a51862d6f2c2bfb43ab78a7099`. Exact-merge
  CI run `30413530785` and Pages run `30413530788` pass. The first named-route
  precheck finds that the generated program and Agents v1 sources still end
  at AO-0008 even though the DD-010 study status is reconciled. Correct those
  public site sources, bind them to the tracked AO-0009 outcome, and require a
  fresh exact-SHA CI/Pages cycle before issue closure.

## Decision log

- `2026-07-28`: preserve AO-0008 exactly and allocate no v4 identity.
- `2026-07-28`: classify the task as `private-evaluation` because one exact
  owner-gated retained-state read is required; provider calls, spend, private
  writes, real private generation, and publication remain prohibited.
- `2026-07-28`: require the diagnostic to fail closed or return inconclusive
  if one bounded logical-call context cannot establish causality.
- `2026-07-28T20:21:32Z`: create issue #206 after verifying AO-0008 issue
  #204 and PR #205 are closed, no substantive pull request is open, and
  `main` matches `origin/main`.
- `2026-07-28T20:23:22Z`: the AO-0009 fixed contract, ExecPlan, PM-0037
  route, and master-plan registration pass Agent Operations and program-memory
  audits with ten task contracts, 37 program-memory records, zero adopted
  unrouted items, zero private-path findings, and no consequential activity.
  Complete M0 and begin M1.
- `2026-07-28T20:42:34Z`: complete M1 through M3. The public audit preserves
  the aggregate-protocol-gate source candidate without selecting it. The
  diagnostic freezes five fixed reads, structural metadata for exactly 3,067
  responses and 502 traces, one selected logical call, four neighbors, at
  most two response decryptions, one trace decryption, and one transient
  operational key. Eighteen focused tests, all fourteen causal classes plus
  integrity stop, the exact-scale synthetic fixture, and the full
  50-task/500-pairing rehearsal pass with zero private reads, provider calls,
  credentials, spend, or scientific change. Begin M4.
- `2026-07-28T20:56:20Z`: draft PR #207 is open at pushed head `7614365`.
  Preserve the first wall's one schema-count regression and its correction.
  The identical complete wall then passes. Complete M4 and begin M5; the next
  commit is the exact diagnostic execution freeze.
- `2026-07-29T00:03:24Z`: accept the explicit preauthorization correction
  without creating a new task, issue, branch, PR, session, campaign, or batch.
  Preserve R1 as unused history and refreeze an aggregate-only 450-trace R2
  surface. Begin M5R2.
- `2026-07-29T00:14:15Z`: freeze public causal precedence as integrity,
  response/trace persistence, terminal provider, contamination, final
  cardinality, other protocol, pairing, completion marker, and bounded
  unknown. Parse/schema-repair remains an aggregate signal under other
  protocol because the live stage's post-loop gate was aggregate protocol;
  Method and metric-range classes cannot be immediate live causes.
- `2026-07-29T00:22:40Z`: the remote-presence rerun passes without code
  changes. Supersede the unused R1 gate's resume instruction, freeze R2, and
  bind only the future R2 gate to the aggregate diagnostic surface.
- `2026-07-29`: consume only the exact R2 gate and diagnostic authority. Close
  private-read authority permanently after the first invocation; never use
  the superseded R1 gate.
- `2026-07-29`: select
  `agent-protocol-policy-decision-required`. AO-0009 records the gate but does
  not alter invalid-output credit, normalization, semantic retry, protocol
  acceptance, or scoring. Any such prospective change requires a separate
  explicit owner decision and task.

## Validation strategy

- Validate task, gate, handoff, taxonomy, allowlist, and public result records
  against schemas and cross-record invariants.
- Exercise every causal class with synthetic, nonsecret fixtures and require
  deterministic selection or honest unknown classification.
- Prove one-use behavior, authorization binding, exact record and object
  ceilings, encrypted-object selection, operational-key transience,
  redaction, symlink/mode rejection, output-lock verification, append-only
  chain validation, and complete pre/post snapshot equality.
- Reconstruct the full 50-task/500-pairing synthetic graph and verify
  Methods A/B/C, cardinality, pairing completeness, contamination, metric
  ranges, output locking, redaction, and exact cost accounting.
- Place sole contamination and protocol failures in the first, middle, and
  final full-batch traces and prove identical classification without mtime
  selection. Reject missing, orphaned, substituted, duplicate, or conflicting
  response identities; missing trace domains; dimensional or raw public
  leakage; and a second read.
- Run the private-evaluation acceptance profile and task-specific checks from
  clean committed source before freezing the execution commit.

## Commands and expected observations

- `make treasurebench-fixed-batch-diagnostic-audit` — public audit, taxonomy,
  allowlist, redaction, fixtures, corruptions, and zero-authority checks pass.
- `make treasurebench-fixed-batch-diagnostic-rehearsal` — synthetic one-use
  diagnostic fixtures and the complete 50-task/500-pairing graph pass with
  deterministic cleanup and zero consequential activity.
- `make owner-gate GATE=reports/agent-ops/AO-0009-treasurebench-ao0008-fixed-batch-diagnostic-r2-owner-gate.yml OWNER_GATE_VALIDATE_ONLY=1`
  — validate the committed R2 gate without creating an authorization.
- `make treasurebench-fixed-batch-read-only-diagnostic` — after and only after
  exact authorization, perform the sole bounded retained-state read.

## Artifacts produced

- This living ExecPlan.
- AO-0009 issue #206, branch, fixed and additive R2 task contracts, public
  audit, diagnostic implementation, schemas, fixtures, tests, R2 gate,
  public aggregate outcome, closeout record, and typed handoff.

## Blockers

None. Private-read authority is permanently closed; any request for another
read, provider or credential access, protocol-policy mutation, or new campaign
would be a new boundary requiring separate owner action.

## Recovery and restart instructions

Resume from this plan on the registered AO-0009 branch. Confirm issue #206,
draft PR #207, all five unrelated untracked files, permanent private-read
closure, and M8 as the sole active milestone. Continue the first unchecked
administrative closeout item. Never run the diagnostic again or access the
retained AO-0008 private root.

## Outcome and retrospective

The final evidence outcome is `agent-protocol-policy-decision-required`.
AO-0009's one-use R2 diagnostic established a public-safe operational cause
without mutating or reopening AO-0008: the retained boundary and pairing
graph are intact, while the frozen runner's post-loop protocol gate saw
nonzero protocol nonconformance. The aggregate also reports parse/schema
repair exhaustion; it contains no terminal-provider, contamination,
final-cardinality, cap, or integrity finding.

This is a useful negative boundary. The existing fail-closed protocol cannot
be weakened through an implementation patch disguised as diagnosis. AO-0009
therefore closes with a policy gate, preserves all four Agents v1 campaign
quarantines, creates no scientific or performance result, does not register
v4, and requires a separate explicit owner decision for any future protocol
change or private evaluation.
