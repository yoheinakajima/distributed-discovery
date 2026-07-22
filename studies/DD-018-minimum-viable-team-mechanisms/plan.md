# DD-018 execution plan

## Purpose and intended outcome

Compare the registered ten-mechanism portfolio with exact finite methods while
keeping planner implementation, obedience, strict unilateral incentives,
pair/tau-player stability, budget balance, and equilibrium multiplicity
separate.

## Current state

DD-015 and DD-018 are merged and deployed. DD-018 PR #114 squash-merged as
`6a533d1`; issue #113, post-merge CI `29893840755`, Pages `29893840796`, and
the live study and JSON passed. DiscoveryBench v3 is the next sequential
Program V4 milestone.

## Scope

Version one fixes `M=3`, `N=4`, `tau=2`, five normalized weakly descending
posterior fixtures, and one common-posterior allocation stage. The planner
profile assigns two agents to each of the top two candidates. The exact census
compares central assignment, random matching, team tokens, exclusive coalition
rights, a correlated mediator, universal pooling, sole-team rescue, marginal
coalition contribution, threshold-adjusted equal split, and a pairwise
matching market.

The primary labeled evaluator enumerates all 81 action profiles per fixture.
The independent table evaluator checks 4,050 mechanism-fixture-profile entries,
recommendation supports, exhaustive planner occupancies, unilateral, pair, and
tau-player strict-member deviations, and equilibrium counts. Runtime is
estimated below 15 seconds and capped at 120 seconds; memory is estimated below
64 MB and capped at 1 GB.

## Non-goals

No private information is reported inside this stage, so report truthfulness is
explicitly not applicable. No coalition-proof, strong-equilibrium, unrestricted
mechanism-design, arbitrary transfer, endogenous matching, human behavior,
general theorem, or novelty claim is made. Strict-member pair and tau-player
blocking are named finite checks, not coalition-proofness.

## Milestones

1. Freeze mechanism semantics, fixtures, counts, caps, and evidence boundary.
2. Implement labeled evaluator, independent table verifier, and corruption gates.
3. Pass targeted and full repository acceptance; freeze source in a clean commit.
4. Execute exactly one immutable primary configuration and audit claims separately.
5. Integrate report, public-safe data, site metadata, CI, Pages, and live routes.

## Progress checklist

- [x] DD-015 predecessor and documentation closeout merged and deployed.
- [x] Issue and isolated branch created.
- [x] Model, mechanism registry, state count, runtime/memory caps, and exactness plan frozen.
- [x] Targeted and repository verification pass.
- [x] Clean source commit and one immutable primary run pass.
- [x] Claims, report, public data, and documentation are audited.
- [x] PR CI, merge, post-merge CI/Pages, issue closure, and live routes pass.

## Validation strategy

Check posterior normalization and ordering, 81 labeled profiles, recommendation
support normalization, exhaustive planner equality, exact discovery and payout
bounds, zero external subsidy, authority-versus-incentive labels, independent
equilibrium counts, candidate relabeling where ranks are preserved, and four
corruptions of discovery, equilibrium multiplicity, budget status, and mechanism
count.

## Discoveries and surprises

- The first targeted CLI preview stopped because the pair-market equilibrium
  call passed the coalition size both positionally and by keyword. Five direct
  hand tests had passed; no run directory or evidence was created. The call was
  corrected before any full preview.
- A direct targeted pytest invocation lost the repository `PYTHONPATH` after
  `uv` refreshed the non-editable install and failed import collection. The
  Make-based environment and a bootstrap restore the declared source path; this
  was an execution-environment failure, not a model result.
- The first full repository gate stopped at MyPy because the independent
  verifier imported `planner_value` transitively through the model module.
  Importing the function from its defining threshold module preserves behavior
  and makes the dependency boundary explicit.
- After that correction, full acceptance passed Ruff, MyPy on 130 source files,
  all 206 tests, the unchanged 82-claim ledger, all 44 existing manifests, and
  a 62-page/22-study site build. The final semantic audit changed committed
  rows' equilibrium multiplicity from the misleading integer one to explicit
  non-applicability and marked unilateral pair-market deviations infeasible
  under binding within-pair choice. The targeted verifier still passes; the
  full gate is repeated before the source commit.
- The passing dirty-tree preview reports 40 of 50 planner-portfolio rows, 31 of
  35 unilateral-applicable obedient rows, 29 pair/tau-stable rows in that
  unilateral-applicable subset, five of five marginal-contribution planner and
  stability rows, and zero of five universal-pooling planner rows. These are
  regression targets, not research evidence.
- Frozen source commit `a193f602` and draft PR #114 preceded the sole primary
  run `20260722T051847Z_DD-018_a193f602_3b3ddac173`. It passed in 0.432822
  seconds; all 50 rows agree with the independent table, all five planner
  fixtures pass exhaustive occupancy checks, and all four corruptions are
  rejected. DD-C-0083 through DD-C-0086 passed separate scoped audits.
- Final local evidence acceptance passed bootstrap, Ruff, MyPy on 130 source
  files, all 206 tests, the 86-claim ledger, all 45 manifests, and the
  62-page/22-study site build. The next action is the evidence commit and push;
  remote gates remain pending.

## Commands and expected observations

- `make dd018-preview`: exact non-evidence summary only.
- `make verify`: formatting, types, all tests, claims, and manifests pass.
- `make dd018-team-mechanisms`: only from a clean source commit; creates one
  immutable run and refuses overwrite.

## Blockers

None. GitHub CLI remains unauthenticated; the connected GitHub integration and
SSH cover ordinary issue, PR, push, merge, and workflow checks. Settings issue
#32 is unrelated.

## Recovery and restart instructions

Inspect Git state, this plan, and `configs/baseline.yml`. Do not run the primary
target until source is committed and the worktree is clean. Never rerun a
passing immutable configuration for freshness.

## Outcome and retrospective

The bounded study and deployment are complete. Forty of 50 recommendations attain
planner discovery; collapse can remain individually or pair stable; three
registered eligibility/contribution rules support the planner recommendation
in all five fixtures but retain substantial equilibrium multiplicity. These are
finite common-posterior results, not report-truthfulness or coalition-proofness
claims. PR #114 merged as `6a533d1`; post-merge CI and Pages passed, issue #113
closed, and the live route and JSON returned HTTP 200 with the immutable run and
all four claim IDs. DiscoveryBench v3 is the next authorized milestone.
