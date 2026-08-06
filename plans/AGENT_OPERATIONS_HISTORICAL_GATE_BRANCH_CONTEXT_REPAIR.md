# AO-0013 historical owner-gate synthetic branch-context repair

## Purpose and intended outcome

Repair the repository-wide Pages verification regression exposed after the
exact-head squash merge of PR #213. The only implementation change is an
explicit synthetic-only branch-context seam for the historical AO-0012 R5 and
R7 authorization fixtures. Real authorization validation continues to read and
enforce the actual Git branch by default.

## Current state

- At 2026-08-06T06:04:32Z, PR #213 squash-merged exact head
  `6794ee7b44e35f79cef72a958d2cf82f8139e368` into `main` as
  `3dc9c66b62dac1d6e407f80755e31631acc8159f`.
- Issue #212 remains open and the AO-0012 source branch remains retained at the
  exact historical head.
- Main CI run `31076079006` passed.
- Pages run `31076078996` failed during `make verify`: 1,044 tests passed and
  exactly two synthetic authorization fixtures failed with
  `live branch mismatch`.
- The Pages workflow intentionally switches to
  `benchmark/treasurebench-agents-v1-sealed-pilot`; the two fixtures invoke R5
  and R7 validators whose production default correctly requires the historical
  AO-0012 branch.
- Issue #218 and branch
  `agent/agent-ops-historical-gate-branch-context-repair` register AO-0013 from
  exact starting main `3dc9c66b62dac1d6e407f80755e31631acc8159f`.
- No provider-neutral task is registered. Local checkpoint
  `87e263005a7d968f4465429c963a2e155cc7ee85` is planning evidence only and is
  not an authority or input to this repair.

## DISCUSSION AND DECISION DELTA AUDIT

- Read `docs/program-memory/registry.yml` completely before issue and branch
  registration.
- PM-0040 remains routed to immutable AO-0012/RunPod closeout history. This
  repair does not reopen its provider path, gates, or historical ambiguity.
- The owner-selected non-RunPod provider-neutral direction is deliberately
  deferred. Its local roadmap checkpoint is not routed into AO-0013 because the
  owner requires green post-merge Pages before that separate task is
  registered.
- No evidence-dependent trigger in the registry is activated by a synthetic
  CI fixture repair. No owner decision remains only in conversation: the
  repair boundary is fixed in the AO-0013 contract and this plan.

## Scope

- Add one keyword-only synthetic branch-context parameter to each of the R5 and
  R7 authorization validators.
- Accept that parameter only when an explicit synthetic gate override and
  synthetic live-state validator are supplied.
- Keep the no-argument production path unchanged: resolve the current Git
  branch and require the historical AO-0012 branch.
- Update the two synthetic fixtures and add fail-closed regressions.
- Preserve the observed failed Pages run and all AO-0012 history.

## Non-goals

- No repair merge, Pages deployment, or issue closure in the authorization-free
  lane.
- No provider-neutral package, provider access, credentials, resources, model,
  inference, calibration, spend, private work, scientific work, or publication.
- No RunPod action or characterization of the ambiguous historical Secret.
- No modification of the five historical untracked files.

## Assumptions

- The two failures reproduced by Pages are the complete observed regression.
- A synthetic-only injected branch context is sufficient because the fixtures
  already inject both an in-memory gate and a no-network live-state validator.
- The production default must remain observable through a regression that
  rejects the actual non-AO-0012 task branch.

## Milestones

1. Register AO-0013 contract, plan, issue, and branch.
2. Implement the two synthetic-only seams and deterministic regressions.
3. Run focused validation and the complete repository/Pages-equivalent wall.
4. Commit, push, open the draft PR, and pass exact-head checks.
5. Freeze execution commit, protected tree, merge owner gate, and handoff; stop.

## Progress checklist

- [x] Reverified PR #213 merge, issue #212, retained branch, main CI, and failed Pages state.
- [x] Read the applicable instructions, Agent Operations policy, study context, and program-memory registry.
- [x] Registered issue #218 and the AO-0013 task branch.
- [x] Validated and committed the fixed task contract and living ExecPlan as `412c4e3`.
- [x] Implemented and focused-tested the synthetic-only seam.
- [ ] Run the complete verification wall and Pages-equivalent branch-context wall.
- [ ] Push and open one draft PR.
- [ ] Freeze and validate the exact merge owner gate and handoff.

## Discoveries and surprises

- The normal main CI workflow passed because it runs only integration,
  regression, and unit test directories; the Pages `make verify` wall also runs
  the top-level historical fixtures and exposed the two failures.
- The Pages workflow's historical pilot branch switch is intentional and
  predates AO-0012. Replacing that branch is outside this task and would risk
  changing other historical verification semantics.
- The smallest fail-closed seam requires all three synthetic signals together:
  an explicit branch context, an in-memory gate override, and a nonproduction
  live-state validator. Supplying a branch context to the production live-state
  validator is rejected before branch comparison.

## Decision log

- 2026-08-06: Treat the failed Pages run as a repository verification defect,
  not an AO-0012 runtime or scientific result.
- 2026-08-06: Use explicit dependency injection only for synthetic callers;
  keep the production default tied to the actual repository branch.
- 2026-08-06: Defer provider-neutral work until a later authorized merge makes
  Pages green.
- 2026-08-06T13:38:59Z: Focused Ruff and strict MyPy passed; 33 R5/R7 tests
  passed, including exact synthetic context, wrong-context rejection,
  production-validator override rejection, and default live-branch rejection.

## Validation strategy

- Validate the task contract schema and Agent Operations audit.
- Run both historical fixture files directly.
- Prove the synthetic seam accepts only the exact registered branch and rejects
  a wrong context.
- Prove the default production path still rejects the current repair branch.
- Run Ruff, strict MyPy, all tests, claims/run-manifest checks, Agent Operations,
  program-memory, paper, site, and offline release checks via `make verify`.
- Repeat `make verify` after switching only the local branch label to the exact
  Pages workflow branch context, then restore the AO-0013 branch.
- Run the normal site build as the remaining Pages-equivalent build step.

## Commands and expected observations

- `uv run pytest tests/test_treasurebench_open_weight_cloud_runtime_r5.py tests/test_treasurebench_open_weight_cloud_runtime_r7.py`: all focused fixtures pass without network or credentials.
- `make verify`: complete repository wall passes on the task branch.
- `git switch --force-create benchmark/treasurebench-agents-v1-sealed-pilot HEAD && make verify`: Pages branch-context verification passes.
- `make site`: the companion site builds without deployment.
- `make audit-agent-ops`: all task, gate, and handoff invariants pass.

## Artifacts produced

- `tasks/agent-operations-historical-gate-branch-context-repair.yml`
- `plans/AGENT_OPERATIONS_HISTORICAL_GATE_BRANCH_CONTEXT_REPAIR.md`
- Minimal R5/R7 source and fixture changes.
- A later exact owner gate and owner-gate-required handoff under
  `reports/agent-ops/`.

## Blockers

- Repair PR readiness and merge remain blocked until a later exact owner
  authorization validates the frozen merge gate.
- The provider-neutral task remains blocked until the repair is merged and
  post-merge Pages is green.

## Recovery and restart instructions

Resume AO-0013 from issue #218, branch
`agent/agent-ops-historical-gate-branch-context-repair`, this plan, and the
fixed task contract. Confirm the five unrelated untracked files remain the only
out-of-scope worktree entries. Continue from the first unchecked milestone and
stop before merge unless the exact committed AO-0013 owner gate is authorized.

## Outcome and retrospective

Pending. Record every failed validation and the exact final owner-gate state
without rewriting earlier observations.
