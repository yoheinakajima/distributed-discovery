# DD-016 execution plan

## Purpose and intended outcome

Prove the minimum-viable-team planner result and independently reproduce the
canonical threshold fixture and phase diagram with two exact state
representations.

## Current state

Issue #101 and draft PR #102 are open. The bounded evidence package is complete
on branch research/dd016-threshold-discovery: the source was frozen before the
single passing primary run, and the run-backed claims passed separate audits.
Remote acceptance, merge, deployment, and the DD-017 handoff remain.

## Scope

The general deterministic theorem uses arbitrary finite posterior vectors.
The exact canonical computation uses M=16, N=8, p=1/5, and tau=1,...,8.
Method A enumerates all 490,314 labeled clue-count vectors. Method B aggregates
false-label occupancy histograms. Both use exact rational arithmetic and must
agree on every registered metric.

## Non-goals

No human data, experiment, behavioral equilibrium assertion, universal
coalition-formation theorem, noisy execution, replication value, unrestricted
mechanism, paid API, or novelty claim. DD-017 owns the wider equilibrium
correspondence and coalition-stability analysis.

## Assumptions

Signals are conditionally independent given a uniform target and wrong labels
are uniform. Ties use the declared protocol-specific rule. Equal splitting
applies only to strategic candidate payoffs.

## Milestones

1. Freeze literature, model, proof, config, and cost estimate. **Complete.**
2. Implement both exact evaluators, theorem audit, and tests. **Complete.**
3. Commit the frozen implementation and run one clean primary configuration. **Complete.**
4. Independently audit claims, report, public data, and corruption rejection. **Complete.**
5. Pass repository/site acceptance, push, merge, and verify deployment. **Active.**

## Progress checklist

- [x] Issue and isolated branch.
- [x] Explicit model boundary and planner proof.
- [x] Focused literature records and novelty-risk update.
- [x] Labeled and histogram exact evaluators.
- [x] Independent verification and four corruption gates.
- [x] Clean immutable run.
- [x] Claims, report, result index, and public metadata.
- [ ] CI, merge, post-merge CI, Pages, and live route.

## Discoveries and surprises

The planner statement needs min(L,M) when team capacity exceeds the candidate
count, and it is an existence theorem rather than a uniqueness theorem.
The preliminary non-evidence execution completed Method A's 490,314 vectors in
12.445 seconds and Method B's 67 histograms in 0.029 seconds. Both reduce to 30
aggregate signal classes and agree on every exact phase row. At tau=2 they
independently recover all supplied regression targets; exact fractions, not
the copied decimals, are retained by the implementation.

The sole primary run `20260722T021526Z_DD-016_00271ff8_123b2809e3` completed
from clean commit `00271ff8` in 11.998247 seconds. Both methods agree, all four
corruptions are rejected, and claims DD-C-0071 through DD-C-0074 passed their
separate evidence audits.

## Decision log

- 2026-07-22: define failed subthreshold attempts as agent-actions assigned to
  positive but nonviable occupancies; report viable candidate count separately.
- 2026-07-22: define effective team count for the registered independent
  tied-mode distribution as inverse action-concentration.

## Validation strategy

Check normalization, posterior ordering, tie shares, tau=1 recovery, the tau=2
symbolic identity and zero limit, exhaustive small planner allocations, method
equality, canonical regression tolerances, occupancy bounds, and rejection of
altered posterior weight, occupancy probability, mode count, and planner mass.

## Commands and expected observations

Targeted tests must pass before make dd016-threshold. The primary run must start
from a clean commit, enumerate 490,314 labeled count vectors, complete under
600 seconds and 2 GB, and produce no valid partial claim outcome.

## Artifacts produced

Model, proof, literature review, config, exact code, independent verifier,
tests, primary manifest and outputs, report, claims, and public metadata.

## Blockers

Shared Lab/site implementation is intentionally deferred until Labs V2 merges.
This does not block study-specific public metadata or the automatically
generated study page.

## Recovery and restart instructions

Inspect Git state and this plan. Never overwrite a run directory or rerun a
passing primary configuration merely for freshness. Preserve any failed run.

## Outcome and retrospective

The bounded scientific package is complete. The planner theorem required the
finite-candidate `min(...,M)` qualification, and selected tied-mode behavior had
to remain distinct from the unresolved equilibrium correspondence. The two
exact state representations matched without rerunning the primary configuration.
Remote acceptance, merge, deployment, and the DD-017 handoff remain.
