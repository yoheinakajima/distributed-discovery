# DD-014 execution plan

## Purpose and intended outcome

Determine whether the DD-012 value of deliberate non-use survives joint
conditioning on private and shared clues, while keeping the restricted policy
boundary and larger-class failure modes explicit.

## Current state

Issue #85 and branch `research/dd014-conditional-attention` are active. The
model, proof boundary, exact primary evaluator, independent table evaluator,
registered grid, raw-policy audit, and tests are implemented. Pre-run findings
are not claim evidence until the clean immutable run passes.

## Scope and non-goals

The main census covers `M=3`, `N in {2,3,4}`, the registered five-value
rational accuracy grid, and all anonymous mixtures of the three complete
agreement-respecting label-equivariant disagreement types. A separate `M=2`,
`N=2` audit covers all sixteen raw deterministic policy tables on four cells.
It is a scope audit, not an unrestricted extension. No human data, external
calls, Monte Carlo, unrestricted `M=3` census, or upstream mutation is in scope.

## Assumptions

Signals are conditionally independent given a uniform target; wrong labels are
uniform over the other labels. Roles choose a deterministic policy ex ante,
and successful roles split a unit reward equally.

## Milestones

1. Freeze the model and prove restricted-class completeness. **Complete.**
2. Implement exact evaluators and corruption checks. **Complete.**
3. Commit the implementation and execute one clean bounded run. **Complete.**
4. Audit claims, report, public data, and Conditional Attention Lab. **Complete.**
5. Pass acceptance, merge, deploy, and verify live routes. **Active.**

## Progress checklist

- [x] Registered issue, branch, grid, caps, and no-partial-result rule.
- [x] Proved the three-policy restricted completeness statement.
- [x] Enumerated 775 anonymous profiles in 75 cells exactly.
- [x] Added a 1,024-profile, 16,384-state raw two-label audit.
- [x] Added an independent verifier and four corruption tests.
- [x] Execute the immutable clean run and record runtime and run ID.
- [x] Promote only claims supported by the preserved run and proof audit.
- [ ] Complete CI, Pages, and live-route checks; local Lab checks pass.

## Discoveries and surprises

The pre-run raw audit finds full discovery from complementary constant policies,
strictly above the restricted private/public subfamily in all four audit cells.
This negative scope result must be preserved. Within the main class,
contrarians tie a planner optimum only when the private clue is uninformative;
they do not improve the unconditional optimum on the frozen grid.

## Decision log

- 2026-07-21: kept the main theorem at the proved three-label symmetry class.
- 2026-07-21: added an adversarial all-table two-label audit rather than
  describing the restricted census as unrestricted.

## Validation strategy

Check normalization and winner-payoff accounting, primary/independent equality,
all unilateral role deviations, planner/equilibrium reconstruction, the DD-012
embedding, raw all-table optima, and rejection of four altered records. Then
run repository, paper/site, artifact, deployment, and live HTTP gates.

## Commands and expected observations

`make dd014-conditional` runs only on a clean committed tree, must finish under
300 seconds and 2 GB, create one immutable run, verify 346,275 main and 16,384
raw labeled states, and reject all four corruptions. `make verify` must pass.

## Artifacts produced

The run will contain the census and CSV, phase map, raw audit, policy registry,
theorem checks, summary, verification, corruptions, manifest, environment,
logs, and validation record.

## Blockers

Settings issue #32 is unrelated. There is no scientific blocker.

## Recovery and restart instructions

Inspect branch status, preserve any created run, and never overwrite or rerun a
passing primary run. Retain a failed run directory and diagnose from its logs.

## Outcome and retrospective

Run `20260721T222047Z_DD-014_f5f099a8_ea0276dd16` passed in 10.761 seconds.
DD-C-0066 through DD-C-0068 and the complete-fallback Lab pass locally. The
raw audit successfully prevented overpromotion: full discovery exists outside
the restricted class. Merge and live deployment remain.
