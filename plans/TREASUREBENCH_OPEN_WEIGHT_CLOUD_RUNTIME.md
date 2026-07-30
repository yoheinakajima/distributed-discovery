# TreasureBench open-weight cloud-runtime feasibility and conformance

## Purpose and intended outcome

Execute AO-0012 as an infrastructure-only feasibility and conformance task.
Define whether the current third-model purpose can be met by an owner-controlled
open-weight, self-operated cloud runtime; prepare a reproducible single-A100
BF16 deployment and public-only calibration package; and stop at one exact
generic owner gate before credential access, model download, provisioning,
endpoint launch, calibration, or spend. This plan does not register DD-023 or
the claim-grade campaign.

## Current state

At `2026-07-30T13:45:35Z`, local and live `main` both resolve to
`6e86b43a8db8d20380dd64bf9490772b7152f484`. No pull request is open; issue
#32 is the only pre-existing open issue. Issue #212 and branch
`agent/treasurebench-open-weight-cloud-runtime` now register AO-0012. Five
unrelated untracked duplicate files are preserved and excluded from every
task-specific stage.

AO-0011 is complete: 500 intended pairings terminalized as 496
protocol-valid, four protocol-invalid, zero provider-operational missing, and
zero provider contract/safety failure; one frozen five-second transient retry
recovered; Methods A/B/C and independent all-pairing bounds passed. Provider
access and the v5 retained root are permanently closed. No DD-023, claim,
scientific run, paper result, ranking, release, submission, or base-campaign
authority exists.

The current base registration fixes 200 public metadata slots, four batches,
five families, five architectures, three repeats, two proprietary provider
families, and one exact open-weight candidate. The exact candidate is
`mistralai/Mistral-Small-3.1-24B-Instruct-2503` at revision
`68faf511d618ef198fef186659617cfd2eb8e33a`; no weight was downloaded. The
historical 16-GB owner host failed the registered environment gate. AO-0012
tests whether physical ownership was an unnecessary proxy for the separable
model-control and serving-stack-control goals.

## DISCUSSION AND DECISION DELTA AUDIT

All 39 pre-existing program-memory records were read before issue or branch
creation. PM-0039 remains implemented and immutable: AO-0011 is complete
engineering evidence only and its explicit-owner-review trigger does not
reopen v5. PM-0010, PM-0014, PM-0015, and PM-0019 remain deferred,
evidence-dependent, or rejected because no claim-grade evidence trigger has
occurred. No adopted item was unrouted, no superseded item became due, and no
raw conversation is retained.

The new owner decision is routed as PM-0040 and this AO-0012 contract. It
separates open-weight model-family diversity, inference-stack transparency,
independence from the two proprietary model providers, owner control, physical
locality, and infrastructure-provider independence. It adopts no scientific
conclusion and creates no external execution authority before the generic
owner gate. Repeat this audit at closeout; no owner decision may remain only in
conversation.

## Scope

1. Audit the existing base registration and state exactly why the third model
   was required without altering the allocation or scientific design.
2. Define five runtime classes and their control, reproducibility, locality,
   and independence properties in a versioned machine-readable record.
3. Audit current official primary sources for the exact Mistral revision,
   license, tokenizer and chat template, recommended vLLM configuration,
   BF16 memory feasibility, immutable vLLM container, CUDA/driver compatibility,
   and RunPod Pod price, API, storage, network, security, retention, lifecycle,
   and recreation controls.
4. Build an authorization-free immutable manifest, fail-closed startup package,
   authenticated endpoint attestation, repository adapter, synthetic
   corruptions, and tests.
5. Freeze ten public tasks, five architectures, one repeat, 50 intended
   pairings, acceptance rules, operational-only outputs, projection formulas,
   and one pending permitted-decision record.
6. Validate, commit, push, open a draft PR, freeze an execution commit, commit
   one generic owner gate, validate it without authorization, and stop.
7. Only after later exact authorization, run the public calibration, teardown,
   reconcile cost and controls, select one permitted decision, and complete
   the public-safe closeout.

## Non-goals

- No DD-023, study, claim, scientific run, evidence or proof promotion.
- No private material, holdout, retained-root access, credential read, model
  download, RunPod API access, provisioning, endpoint, call, or spend before
  owner authorization.
- No base-allocation change, third-model weakening, quantization, sharding,
  alternate model or GPU, managed endpoint, routed API, fallback, or
  autosubstitution.
- No task, family, architecture, or model performance publication; no ranking,
  composite, leaderboard, paper, release, DOI, submission, or upstream change.

## Assumptions

- Official public documentation and unauthenticated metadata are sufficient to
  prepare the feasibility record without downloading weights or reading a
  token.
- The exact registered revision remains the only candidate identity; any
  upstream drift is recorded but never silently adopted.
- One A100 80GB can hold the official BF16 24B weights only if current official
  engine guidance and measured later calibration both pass the frozen
  single-GPU identity.
- RunPod is compute infrastructure, Mistral is model origin, and vLLM is the
  inference engine; these roles remain separately recorded.

## Milestones

- **M0 — complete:** issue, branch, PM-0040, fixed task contract, living
  ExecPlan, master-plan registration, schema validation, and first
  authority-bearing commit.
- **M1 — active:** existing-design audit, five-class runtime definition, and
  current official-source model/engine/container/CUDA/RunPod feasibility
  record.
- **M2 — pending:** immutable runtime manifest, fail-closed container startup,
  repository endpoint adapter, authenticated attestation, safe telemetry and
  cost ledger, and no-credential deployment package.
- **M3 — pending:** frozen public-only 50-pairing calibration, acceptance,
  permitted-decision record, complete synthetic corruptions, independent
  checks, and focused tests.
- **M4 — pending:** authorization-free full acceptance, clean execution
  commit, push, draft PR, exact-head checks, and protected-tree freeze.
- **M5 — pending:** committed generic owner gate, live validate-only pass,
  schema-valid owner-gate-required handoff, and exact stop.
- **M6 — pending owner authorization:** provision, download, start, attest,
  execute only the public calibration, measure, stop, teardown or detach under
  policy, and reconcile.
- **M7 — pending M6:** select one permitted final decision, validate public-safe
  closeout, merge after checks, verify CI/Pages/routes, close issue, synchronize
  main, repeat the delta audit, and complete the handoff.

## Progress checklist

- [x] Read root, planning, master-plan, repository, Agent Operations, scoped,
  DD-010, and GitHub workflow authority.
- [x] Verify local worktree, local and remote main, worktrees, open issues and
  pull requests, GitHub CLI status, and identity collisions.
- [x] Read and reconcile all 39 program-memory records.
- [x] Create issue #212 and branch
  `agent/treasurebench-open-weight-cloud-runtime`.
- [x] Add and validate PM-0040, the fixed contract, living plan, and master
  continuation.
- [ ] Complete M1 through M4 sequentially without consequential activity.
- [ ] Commit and validate the generic gate and owner-gate-required handoff.
- [ ] Stop before every gated action.

## Discoveries and surprises

- GitHub CLI 2.96.0 is installed but its stored token is invalid. Public list
  operations and SSH transport remain available; issue and PR mutations use the
  connected GitHub integration. The settings-only issue #32 remains separate.
- The existing registration uses `local/open` as a bundled label but its
  machine-readable selection rule actually combines at least six separable
  objectives. AO-0012 must not preserve the bundled wording as if physical
  locality were identical to model or serving-stack independence.
- The first M0 program-memory audit rejected the new descriptive
  `AO-0012-public-calibration-closeout` review token because review classes are
  schema-enumerated. PM-0040 now uses the existing
  `explicit-owner-decision` class; no proposition, route, trigger, or task
  authority changed.
- The second M0 audit rejected `task-contract` as a canonical-destination type.
  Existing TreasureBench program-memory records classify task contracts as
  `decision-record`; PM-0040 now follows that enumerated convention.
- The third M0 audit rejected a reserved future study identifier inside program
  memory. PM-0040 now states the same boundary generically as
  `no scientific-study allocation`, leaving the exact identifier in the task
  contract and plan where it belongs.
- The first combined M0 stage/commit command stopped before staging because the
  sandbox could not create `.git/index.lock`. The task paths remained
  unstaged and no commit was created; the explicit Git operations require the
  repository's approved Git permission.

## Decision log

- `2026-07-30T13:45:35Z`: verify local and live remote main at
  `6e86b43a8db8d20380dd64bf9490772b7152f484`, no open PR, only issue #32
  open, and five unrelated untracked files preserved.
- `2026-07-30T13:45:35Z`: route the new owner decision as PM-0040 and AO-0012;
  preserve PM-0039 and every earlier campaign without access.
- `2026-07-30T13:45:35Z`: classify AO-0012 as infrastructure rather than
  scientific registration or private evaluation. The later public calibration
  is engineering-only and must remain behind the generic owner gate.
- `2026-07-30T13:45:35Z`: freeze the primary identity at RunPod Secure Cloud
  dedicated Pod, one A100 80GB, exact registered Mistral revision, official
  BF16 unquantized weights, pinned vLLM, and an authenticated
  repository-controlled endpoint. Any quantized, sharded, multi-GPU,
  alternate-hardware, managed-endpoint, or routed identity is outside AO-0012.
- `2026-07-30T13:45:35Z`: preserve the first M0 program-memory validation
  failure and use the registry schema's existing `explicit-owner-decision`
  review class instead of expanding stable program-memory policy for one task.
- `2026-07-30T13:45:35Z`: preserve the second M0 validation failure and use the
  existing `decision-record` destination type for the task contract.
- `2026-07-30T13:45:35Z`: preserve the third M0 validation failure and keep the
  program-memory record free of reserved future study identifiers.
- `2026-07-30T13:48:43Z`: complete M0 after Agent Operations accepts 15 task
  contracts with unchanged scientific authority, program memory accepts 40
  records with zero adopted-unrouted or duplicate canonical records, and
  `git diff --check` passes. Begin M1.
- `2026-07-30T13:48:43Z`: preserve the stopped pre-staging Git attempt; rerun
  path-explicit `git add` and `git commit` with approved Git permissions.

## Validation strategy

1. JSON Schema and cross-record validation for the task contract, runtime
   definition, feasibility record, manifest, attestation, calibration,
   corruptions, decision, owner gate, and handoff.
2. Hand-checkable five-class conformance matrix plus independent reconstruction
   of every class/property result.
3. Manifest rejection tests for revision, tokenizer, image digest, GPU,
   quantization, managed endpoint/router, fallback, authentication, logging,
   model/engine drift, malformed attestation, answer/generator access, and
   credential leakage.
4. Synthetic repository-adapter tests for exact action schema,
   protocol-validity policy v2, provider-outcome policy v3 extension, zero
   semantic retry, exact terminal classification, token/latency/throughput/cost
   accounting, and public-only task custody.
5. Complete 50-pairing no-network rehearsal with Methods A/B/C and independent
   bounds, followed by the infrastructure acceptance profile and exact-head CI.
6. Generic owner-gate validation against a clean pushed execution commit and
   live draft-PR ancestry without creating authorization.

## Commands and expected observations

- `make audit-agent-ops` and `make audit-program-memory`: accept AO-0012 and
  PM-0040 with no authority drift.
- Task-specific audit and rehearsal targets added in M2/M3: pass entirely from
  synthetic public fixtures with zero credential, model download, provider
  call, GPU, private, scientific, or spend state.
- `make verify`: preserve all claims, immutable runs, papers, release records,
  prior campaign locks, and closed private/provider boundaries.
- `make owner-gate GATE=reports/agent-ops/AO-0012-open-weight-public-calibration-owner-gate.yml OWNER_GATE_VALIDATE_ONLY=1`: validate the exact live gate and create no authorization.

## Artifacts produced

Issue #212 and the task branch exist. This plan, fixed task contract, PM-0040,
and the master-plan continuation are the M0 registration artifacts. Later
artifacts are recorded only after they exist and validate.

## Blockers

No registration blocker. Consequential execution is intentionally blocked
until M1 through M5 pass and the owner supplies the exact generic-gate
challenge. The unrelated untracked files prevent a globally clean worktree but
do not overlap AO-0012; all staging is path-explicit.

## Recovery and restart instructions

Resume on `agent/treasurebench-open-weight-cloud-runtime`. Read the fixed task
contract and this plan, verify issue #212 and the current draft PR if one
exists, preserve the five unrelated untracked files, and continue the sole
active milestone. Never inspect prior retained roots or authorizations. Before
M5, do not access credentials, RunPod or authenticated Hugging Face APIs,
download weights, provision a GPU, launch an endpoint, run calibration, or
spend.

## Outcome and retrospective

Pending. AO-0012 is complete only after either a permitted calibrated decision
and public-safe closeout or an honest fail-closed terminal decision. The
current required checkpoint is owner-gate-required after authorization-free
work, not completion.
