# AO-0007 TreasureBench AO-0006 custody repair

## Purpose and intended outcome

This living ExecPlan governs `AO-0007`, a DD-010 engineering-only task with
two inseparable tracks. Track A implements and, after one exact owner gate,
executes one bounded read-only adjudication of AO-0006's custody-creation
failure. Track B then reproduces the exact failing shape with synthetic
nonsecret content, implements the minimum prospective repair, and proves the
production custody path with a live-mode-equivalent offline conformance
command. The task registers or executes no new private pilot.

The permitted final outcomes are:

- `custody-root-cause-repaired-live-conformance-pass`;
- `custody-root-cause-known-no-safe-repair-defer`;
- `custody-diagnostic-inconclusive-defer`;
- `retained-state-integrity-mismatch-stop`.

The selected outcome after the bounded diagnostic and prospective conformance
is `custody-root-cause-repaired-live-conformance-pass`.

## Current state

At `2026-07-28T05:28:24Z` registration preparation began from local `main`
matching `origin/main` at `2df92d57c5591a65214a187e35ba7982b329dffa`.
No pull request was open. AO-0006 issue #200 and PR #201 are closed after the
quarantine closeout. The next available Agent Operations ID is `AO-0007`;
issue #202 and branch `codex/treasurebench-ao0006-custody-repair` now own the
new substantive lane.

Five unrelated untracked preservation files pre-exist:

- `papers/information-sharing-frontier/paper-audit 2.json`;
- `papers/information-sharing-frontier/visual-qa 2.md`;
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`;
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`;
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`.

They are outside scope and remain untouched. The exact owner authorization was
created, and the diagnostic ran exactly once. It read only the registered
encrypted/redacted allowlist and metadata-only secret-file attributes; it read
no secret value, credential, private host path, task, answer, or raw provider
output. No provider call, spend, retained-state mutation, new real private
material, unsealing, scientific mutation, release, or submission occurred.

The authoritative AO-0006 boundary is permanent:
campaign `treasurebench-agents-v1-repair-confirmation-v2`, batch
`tb-agents-v1-repair-confirmation-v2-b01`, execution commit
`d210b0653677859c79a1fb87d871aaf45f4a81d4`, decision
`fresh-pilot-v2-quarantined-engineering-only`, two successful public canaries,
1,349 input tokens, 253 output tokens, USD 0.0076095 total cost, zero private
architecture/model runs, no task ciphertext, no answer ciphertext, no custody
manifest, no unsealing, and output lock
`sha256:127a9c796459c7627f6fd90b92ef1587ad0f6b1910b4ff255c2ceb976f3ab25f`.

Registration commit `6c7f7b4` passed both Agent Operations and program-memory
audits. The public audit, bounded diagnostic implementation, synthetic fixture,
and live-mode conformance framework are complete without private access.
Draft PR #203 is open. The generic gate was authorized against execution
commit `55a7815c77319e7845238126c6045f2e80026165`; the one-use diagnostic
verified the complete declared boundary and permanently closed private access.
The exact cause is the v2 campaign's absence from the private-generation
permit allowlist. The prospective repair and all twenty live-mode custody
conformance classes now pass with independent verification and six negative
classes. Exactly one milestone is active: **M8 — public-safe closeout,
validation, merge, and synchronization**.

## DISCUSSION AND DECISION DELTA AUDIT

The complete `docs/program-memory/registry.yml` was read before issue or
branch creation.

- `PM-0032` is due because this explicit owner decision invokes the
  repository-native Agent Operations workflow. It remains implemented and is
  applied through the AO-0007 contract, ExecPlan, generic gate, and typed
  handoff; it is not superseded.
- `PM-0033` is due because the owner has selected a new bounded follow-up to
  the completed public schema conformance and later v2 quarantine. It remains
  implemented. AO-0007 routes only custody adjudication and prospective
  repair; it does not register another pilot.
- `PM-0034` is due because the owner explicitly selected adjudication of the
  custody-stage quarantine. It remains implemented and immutable. Its new
  follow-up is routed to a new `PM-0035` record whose canonical destination is
  the AO-0007 task contract and whose boundaries preserve AO-0006 and prohibit
  scientific or private-pilot authority.
- `PM-0014` and `PM-0015` remain evidence-dependent; their claim-grade trigger
  has not occurred.
- No other promotion or review trigger has occurred. No owner decision
  relevant to AO-0007 remains only in conversation once the contract,
  ExecPlan, `PM-0035`, issue, gate, and handoff are committed.

Repeat this audit at closeout. Do not treat the private diagnostic as
scientific evidence.

## Scope

1. Register AO-0007 with one issue, branch, fixed contract, living ExecPlan,
   and draft PR.
2. Audit the public production custody stack and reconstruct the public-safe
   AO-0006 failure boundary without private access.
3. Implement one exact authorization-bound diagnostic command that verifies
   the AO-0006 output lock, exact object inventory, append-only logs,
   read-only selection, pre/post filesystem state, and redaction.
4. Permit the command to decrypt or read only the encrypted or redacted
   custody-failure record and minimum surrounding operational events required
   to identify the exact failing operation.
5. Add synthetic diagnostic fixtures spanning generation, serialization,
   AES-GCM, associated data, nonces, exclusive atomic creation, permissions,
   commitments, manifest creation/persistence, and reload/verification.
6. Add a repository-native offline live-mode custody conformance command that
   uses the production functions and ordering with synthetic content in an
   isolated temporary XDG state root.
7. After the owner-authorized diagnostic, close private access, reproduce the
   exact shape synthetically, make the minimum prospective repair, preserve
   the failure as a regression, and add an independent verifier and
   corruptions.
8. Produce one detailed private diagnostic outside Git and one redacted public
   diagnosis.
9. Under the same authorization, complete public-safe validation, PR
   readiness, merge after checks, normal CI/Pages, live route verification,
   issue closure, and synchronized `main`.

## Non-goals

- Reopening, retrying, executing, reusing, rescoring, splicing, mutating,
  deleting, reauthorizing, or unsealing AO-0006.
- Reading any seed value, task key, answer key, operational key, task text,
  answer, raw provider output, credential, private path, or unrelated object.
- Mutating retained state or making a provider call.
- Registering or executing another private pilot or allocating a v3 identity.
- Creating DD-023, a claim, scientific run, proof or evidence promotion,
  paper result, ranking, composite, package, release, DOI, submission, or
  base-campaign authority.

## Assumptions

- The public AO-0006 closeout is accurate and the bounded diagnostic confirmed
  its retained boundary and the exact private-generation permit failure.
- The retained output lock and inventory must verify before any selected
  record is read.
- A single diagnostic invocation can gather sufficient permitted evidence. A
  second private read is forbidden without a new owner decision and is a task
  stop.
- Synthetic state is nonsecret, disposable, isolated under a temporary XDG
  root, and does not count as new real private campaign material.
- The production custody functions can be exercised offline without provider
  or credential access; any contrary discovery is a hard stop.

## Milestones

- **M0 — complete:** register AO-0007, issue, branch, contract, ExecPlan, and
  program-memory route.
- **M1 — complete:** complete the public custody-stack and AO-0006 public-boundary
  audit.
- **M2 — complete:** implement the authorization-bound read-only diagnostic,
  private-read and mutation guards, redaction, synthetic fixtures, and exact
  record-selection proof.
- **M3 — complete:** implement the live-mode custody conformance framework,
  independent verifier, twenty required coverage classes, interrupted-write
  cases, and corruptions using production functions and ordering.
- **M4 — complete:** run all authorization-free validation, open the draft PR,
  and fix every failure without reading AO-0006 private state.
- **M5 — complete:** freeze the exact diagnostic execution commit, commit one
  generic owner-gate manifest, validate it without authorizing, render the
  schema-valid `owner-gate-required` handoff, and stop exactly once.
- **M6 — complete:** verify authorization and retained-state
  integrity, execute the diagnostic once, write the detailed private record
  outside Git, close private access, and publish only a redacted diagnosis.
- **M7 — complete:** reproduce the exact failing shape synthetically,
  implement the minimum repair, preserve the regression, and complete the
  live-mode conformance and independent verification.
- **M8 — active:** select one permitted outcome; reconcile public-safe
  records, repeat the decision-delta audit, validate, ready and merge the PR,
  verify CI/Pages and named live routes, close the issue, and synchronize
  `main`.

## Progress checklist

- [x] Read root and scoped instructions, planning policy, master plan,
  repository contract, Agent Operations policy, and DD-010 README, plan, and
  status.
- [x] Inspect Git, remote, untracked preservation files, recent AO state, open
  PRs, AO-0006 closeout, and next available AO ID.
- [x] Read and reconcile the complete program-memory registry before issue or
  branch creation.
- [x] Create issue #202 and branch
  `codex/treasurebench-ao0006-custody-repair`.
- [x] Complete the fixed contract, living ExecPlan, and `PM-0035`.
- [x] Validate and commit registration as `6c7f7b4`.
- [x] Complete M1 public custody audit.
- [x] Complete M2 diagnostic implementation and synthetic fixtures.
- [x] Complete M3 live-mode custody conformance implementation and corruptions.
- [x] Open draft PR #203 after the registration skeleton and focused tests
  pass.
- [x] Complete the full authorization-free validation wall.
- [x] Commit exact diagnostic execution freeze
  `55a7815c77319e7845238126c6045f2e80026165`.
- [x] Commit and validate the generic owner-gate manifest.
- [x] Render the schema-valid owner-gate-required handoff and stop.
- [x] After exact authorization, execute the diagnostic once and close private
  access.
- [ ] Complete prospective repair, validation, closeout, merge, deployment,
  issue closure, and main synchronization.

## Discoveries and surprises

- `2026-07-28T05:30:00Z`: the first `make audit-agent-ops` stopped before any
  mutation because YAML parsed the unquoted colon in the first
  `owner_decisions` item as a mapping. Quote the authority-bearing scalar and
  rerun the complete registration audits. No private, provider, credential,
  scientific, or immutable state was touched.
- `2026-07-28T05:31:00Z`: the corrected Agent Operations audit passed all
  eight contracts and sixteen gate-corruption behaviors. The chained
  program-memory audit then stopped because its schema calls task contracts
  `decision-record` destinations rather than accepting a `task-contract`
  destination type. Preserve the contract path, correct only the registry
  type label, and rerun.
- `2026-07-28T05:32:00Z`: registration commit `6c7f7b4` freezes AO-0007,
  issue #202, the task branch, fixed contract, ExecPlan, master-plan lane, and
  PM-0035 after both registration audits pass.
- `2026-07-28T05:36:00Z`: tracked source at exact AO-0006 execution commit
  `d210b0653677859c79a1fb87d871aaf45f4a81d4` supplies a deterministic causal
  candidate. The v2 custody function creates the seed and two keys before
  private task generation; the generator passes the v2 campaign into a
  fail-closed allowlist containing only the original and v1 campaign IDs. The
  offline rehearsal used `public_fixture=True` and bypassed that decision.
  Record this only as a public-source candidate until the owner-gated
  retained-state inventory and ordering check passes.
- `2026-07-28T05:36:00Z`: the public audit also finds prospective conformance
  gaps: shared atomic writes replace existing regular files rather than
  enforcing exclusive creation, and resume of an existing sealed object does
  not prove it represents the requested plaintext. These are not asserted as
  the AO-0006 cause.
- `2026-07-28T05:39:00Z`: the first focused static check stopped on seven
  mechanical Ruff findings: import ordering, three unused imports, two long
  lines, and one nested conditional. Correct formatting only; custody behavior
  was not changed.
- `2026-07-28T05:40:00Z`: the first focused test run stopped with two fixture
  failures because a synthetically created intermediate directory retained the
  process umask mode instead of the required `0700`. Tighten only the fixture
  to normalize every synthetic directory and preserve the production guard.
- `2026-07-28T05:42:00Z`: the corrected focused suite passes seven tests. The
  public-only custody audit also passes with zero retained-state reads or
  writes, provider calls, credential reads, or spend. It independently
  verifies the downstream synthetic AES-GCM path and corruptions while
  preserving the expected pre-repair live-mode permit failure and the two
  registered prospective gaps.
- `2026-07-28T05:49:03Z`: the complete authorization-free
  `private-evaluation` wall passes: bootstrap, both Agents v1 audits, dry run,
  readiness, Agent Operations, program memory, both AO-0007 custody targets,
  repository formatting, lint, full type checking, 580 tests, claims, 51 run
  manifests, editorial and publication audits, and offline compendium
  verification. The expected pre-repair live-mode failure remains intact.
- `2026-07-28T05:51:00Z`: the first live gate validation failed closed because
  the manifest contained an incorrectly expanded full execution SHA. No
  authorization or private access occurred. Correct the binding in a new
  commit, preserve the failed validation in the handoff, and rerun.
- `2026-07-28T05:53:00Z`: the corrected manifest passes live validation from
  the final handoff head with the exact challenge
  `AUTHORIZE AOG-AO-0007-AO0006-CUSTODY-DIAGNOSTIC 55a7815`.
- `2026-07-28T12:40:00Z`: the exact generic gate succeeds, then the diagnostic
  runs once and closes private-read authority. Output lock, inventory, eight
  locked objects, execution identity, append-only logs, stage state, redacted
  summary, and before/after equality pass. The exact cause is
  `v2-campaign-absent-from-private-generation-permit-allowlist`; no secret
  value, credential, private path, provider call, spend, or retained mutation
  occurs.
- `2026-07-28T12:43:01Z`: the prospective repair admits only the already frozen
  v2 campaign, adds atomic exclusive creation for new custody objects, and
  requires existing sealed objects to decrypt to the requested plaintext.
  The 50-task production-path synthetic conformance passes all twenty classes,
  the independent AES-256-GCM verifier, and all six negative classes.
- `2026-07-28T12:48:00Z`: the first post-repair full wall stops at one of 580
  tests. The staged v2 mock resume correctly reaches the new plaintext check,
  but direct Python equality distinguishes the original tuple-rich value from
  its semantically identical JSON-decoded list representation. Compare
  canonical JSON bytes instead; do not relax any cryptographic or identity
  check. The other 579 tests pass.

## Decision log

- `2026-07-28T05:28:24Z`: allocate `AO-0007` after repository-wide collision
  search found AO-0006 as the maximum existing Agent Operations ID.
- `2026-07-28T05:28:24Z`: use branch
  `codex/treasurebench-ao0006-custody-repair`; preserve the five unrelated
  untracked files byte-for-byte and never stage them.
- `2026-07-28T05:28:24Z`: classify the task as `private-evaluation` because
  one exact retained-state read is owner-gated, while fixing provider calls,
  spend, credential reads, retained writes, and real private generation at
  zero.
- `2026-07-28T05:28:24Z`: keep AO-0006, PM-0033, and PM-0034 immutable; route
  the explicit custody adjudication and prospective repair decision into new
  PM-0035 and AO-0007.
- `2026-07-28T05:28:55Z`: create issue #202 through the connected GitHub
  integration, then create the sole task branch
  `codex/treasurebench-ao0006-custody-repair` from exact synchronized main.
- `2026-07-28T05:42:00Z`: keep the production path unchanged before the
  owner-gated diagnostic. Treat the campaign-permit rejection as a
  public-source causal candidate, and treat exclusive creation and duplicate
  mismatch as separate prospective conformance gaps until the retained-state
  adjudication is complete.
- `2026-07-28T05:44:52Z`: open draft PR #203 from the sole substantive branch.
  Do not add its observed number to the already fixed task contract; bind the
  live PR identity in the generic owner-gate manifest and handoff instead.
- `2026-07-28T12:40:00Z`: accept the diagnostic classification as the exact
  engineering cause within authorized evidence, permanently close AO-0007
  private access, and perform no second retained-state read.
- `2026-07-28T12:43:01Z`: select
  `custody-root-cause-repaired-live-conformance-pass`. Preserve AO-0006
  unchanged; apply repair only prospectively and do not allocate a future
  private-pilot identity.

## Validation strategy

Registration must pass the task-contract schema, Agent Operations audit,
program-memory audit, focused plan and contract tests, and `git diff --check`.
The diagnostic implementation must prove exact allowlisted object selection,
pre-access lock and inventory verification, append-only log verification,
zero provider and credential surface, no writes, before/after state equality,
private-path suppression, forbidden-field rejection, redaction, single-use
access closure, and synthetic stage classification.

The live-mode conformance command must use production custody functions and
ordering and cover:

1. OS-CSPRNG seed generation;
2. separate task and answer key generation;
3. private task and answer generation from synthetic fixtures;
4. independent AES-256-GCM encryption;
5. unique nonces;
6. domain-separated associated data;
7. atomic exclusive file creation;
8. directory mode `0700`;
9. file mode `0600`;
10. seed, task, answer, and allocation commitments;
11. task and answer ciphertext persistence;
12. custody-manifest creation;
13. reload and exact verification;
14. wrong-key rejection;
15. corrupted-ciphertext rejection;
16. interrupted-write recovery or refusal;
17. symlink refusal;
18. duplicate-object refusal;
19. no host-path or secret leakage;
20. deterministic cleanup of synthetic temporary state.

An independent verifier must not share the production verification path.
Corruptions must demonstrate rejection of the prior failing shape and each
security boundary. Full acceptance uses the `private-evaluation` profile plus
`make audit-agent-ops`, `make audit-program-memory`, focused custody targets,
`make verify`, and any paper/site checks required by changed public surfaces.

## Commands and expected observations

- `git status --short --branch`: branch matches the contract; only scoped
  changes plus the five preserved untracked files appear.
- `make audit-agent-ops`: every task contract, gate, and handoff validates.
- `make audit-program-memory`: every due owner decision is routed and no
  scientific authority is inferred.
- The future focused diagnostic test command: synthetic valid selections pass;
  forbidden objects, fields, mutations, provider/credential access, path
  leakage, and second access reject.
- The future live-mode conformance command: all twenty coverage classes pass
  from an isolated temporary XDG root, all corruptions reject, and cleanup
  leaves no synthetic state.
- The future exact diagnostic command: before authorization it refuses without
  reading retained state; after authorization it verifies lock and inventory,
  selects only declared records, writes only the outside-Git private diagnostic
  destination, proves retained-state equality, emits the redacted diagnosis,
  and permanently closes its access for AO-0007.

## Artifacts produced

Planned:

- one fixed AO-0007 task contract;
- one living ExecPlan;
- one program-memory routing record;
- one issue, branch, and draft PR;
- one public custody-stack audit;
- one authorization-bound read-only diagnostic command and synthetic fixtures;
- one repository-native live-mode custody conformance command;
- one independent verifier and corruption set;
- one exact diagnostic execution freeze;
- one generic owner-gate manifest;
- one schema-valid owner-gate-required handoff;
- after authorization, one detailed private diagnostic outside Git and one
  redacted public diagnosis;
- one permanent regression fixture and minimum prospective repair if safe.

## Blockers

No authorization-free blocker. The planned and required checkpoint is the
single exact owner gate after M5. AO-0006 private state must not be accessed
before that gate.

## Recovery and restart instructions

Read `AGENTS.md`, `docs/agent-ops/README.md`, the fixed AO-0007 contract, this
plan, both applicable TreasureBench scoped instructions, and DD-010's README,
plan, and status. Inspect branch, issue, PR, current head, untracked
preservation files, and exactly one active milestone. Resume the first
unchecked item. Never inspect a private path, owner authorization, credential,
or retained AO-0006 object during ordinary recovery.

At M5, use only the committed generic gate and schema-valid handoff. After the
diagnostic command completes once, treat AO-0007 private-read authority as
closed; any need for a second read is a hard stop requiring a new owner
decision.

## Outcome and retrospective

Pending. Record the selected permitted outcome only after the diagnostic and
the required validation evidence exist. Do not infer success from
implementation or synthetic rehearsal alone.
