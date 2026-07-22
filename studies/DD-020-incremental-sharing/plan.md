# DD-020 execution plan

## Purpose and intended outcome

Determine exactly how marginal aggregation and lost independent rescue compare
in the registered point channel, then test whether same-accuracy DD-019
channels have different incremental-sharing profiles.

## Current state

Milestone A merged as `dc32ff17`; issue #135 and branch
`research/dd020-incremental-sharing` are active. The live registry ends at
DD-019, so DD-020 is allocated. No run, claim, or numerical result exists.

## Scope

The point-channel census covers `M=2,...,8`, `N=2,...,8`, all `s=1,...,N`,
and 73 declared `(M,p)` cells. It contains 2,555 protocol rows. The two exact
methods process at most 288,530 count vectors in aggregate; the largest single
count-vector set has 6,435 states. The DD-019 extension adds five channels at
`M=4,N=3` and no more than 5,072 labeled target/signal states across block
sizes. Runtime is estimated below 30 seconds and capped at 120 seconds; memory
is estimated below 256 MB and capped at 1 GB. All probabilities are exact
rationals and no partial outcome promotes a claim.

## Non-goals

No private-team optimum, assigned pooled portfolio, strategic reward,
equilibrium, threshold action, randomized information design, human or real
data, general arbitrary-channel monotonicity theorem, submission, DOI, or
novelty claim.

## Assumptions

Uniform target prior; declared finite channel; conditional source
independence; explicit independent uniform MAP tie-breaking; constant
conditional private success within each symmetric channel; simultaneous
one-hit actions; binding duplicate block action; named direct-private baseline.

## Milestones

1. Freeze registration, resource audit, literature boundary, and terminology.
2. Prove or correct the aggregation–rescue identity and point-channel theorem
   progression.
3. Implement count-vector and independent orbit/dynamic exact methods plus
   corruption gates.
4. Pass targeted and full pre-run validation, freeze source, and open the draft
   PR before execution.
5. Execute exactly one immutable primary configuration from the clean commit.
6. Audit claims separately and integrate proof, report, figures, public-safe
   data, study page, and future-Lab data.
7. Pass repository, paper if affected, site, PR, post-merge, Pages, and live
   acceptance.

## Progress checklist

- [x] Milestone A merged, deployed, closed, and synchronized.
- [x] Live registry/open-PR audit and DD-020 issue/branch allocation.
- [x] Frozen model, 73-cell grid, 2,555-row census, state counts, caps,
  exactness plan, and stop rule registered.
- [ ] Complete primary-source literature review and novelty boundary.
- [ ] Complete human-readable analytic proof and independent proof audit.
- [ ] Implement two exact methods, DD-019 extension, and five corruptions.
- [ ] Pass pre-run validation; commit source; open draft PR.
- [ ] Execute the primary configuration once from the clean frozen commit.
- [ ] Audit claims, integrate evidence/public data, and pass full acceptance.
- [ ] Merge, deploy, close, synchronize, and verify live routes.

## Discoveries and surprises

None yet. Preliminary calculations or dirty-tree previews are not evidence and
must be recorded as such if used.

## Decision log

- `2026-07-22T14:13:02Z`: allocate DD-020 only after main `dc32ff17`, no open
  PR, issue #32 as the only existing open issue, and a registry ending at
  DD-019 were confirmed.
- `2026-07-22T14:13:02Z`: use `I_N(W)` for the incremental-sharing profile so
  it cannot be confused with DD-019's action-budget profile.

## Validation strategy

Check channel/config schema, exact normalization, `C_1=p`, identity agreement,
two-method equality, bounds, relabeling invariance, private/full-consensus
endpoints, tie probabilities, increment arithmetic and signs, analytic
regressions, all five DD-019 curves, same-accuracy comparison, and corruptions
of count probability, tie weight, pooled accuracy, discovery, and sign. The
claim audit follows the repository `verify-claim` workflow after the run.

## Commands and expected observations

Targeted tests and preview commands may inspect exact values but create no
evidence. The primary Make target will refuse dirty Git state, identify the run
as `YYYYMMDDTHHMMSSZ_DD-020_<short-sha>_<config-hash>`, finish under registered
caps, preserve outputs/checksums/logs/environment, and never overwrite.

## Artifacts produced

At registration: README, question, brief, model, plan, status, public metadata,
claims view, proof placeholder, literature placeholder, and frozen config.

## Blockers

No scientific blocker. Settings issue #32 is unrelated. The primary run is
blocked by design until literature, proof, implementation, independent
verification, corruptions, tests, clean source commit, and draft PR pass.

## Recovery and restart instructions

Read this plan, `README.md`, `status.yml`, and `configs/census.yml`; inspect Git
and PR state. Resume the first unchecked item. Never execute the primary target
from a dirty tree or rerun a passing primary configuration for freshness.

## Outcome and retrospective

Pending. Preserve a proof, counterexample, bounded null, or stopping boundary
honestly; do not promote a finite-grid failure search to a theorem.
