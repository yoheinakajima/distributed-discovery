# DD-020 execution plan

## Purpose and intended outcome

Determine exactly how marginal aggregation and lost independent rescue compare
in the registered point channel, then test whether same-accuracy DD-019
channels have different incremental-sharing profiles.

## Current state

Milestone A merged as `dc32ff17`. DD-020 merged through PR #136 as `cf7bc67e`;
post-merge CI `29929864642`, Pages `29929864954`, and the live study, claim,
evidence, and data routes pass. The sole immutable run and five audited claims
remain authoritative and must not be rerun.

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
- [x] Complete primary-source literature review and novelty boundary.
- [x] Complete human-readable analytic proof and independent proof audit.
- [x] Implement two exact methods, DD-019 extension, and five corruptions.
- [x] Pass pre-run validation; commit source; open draft PR.
- [x] Execute the primary configuration once from the clean frozen commit.
- [x] Audit claims and integrate evidence/public data.
- [x] Pass full local acceptance.
- [x] Merge, deploy, close, synchronize, and verify live routes.

## Discoveries and surprises

The analytic step produced a general point-channel monotonicity proof rather
than only the registered bounded progression. A dirty-tree preview then passed
the implementation checks and displayed candidate exact values. Those values
are preliminary diagnostics only: they are not a run, result, or claim and
cannot be cited until the clean primary execution and claim audit pass.
The first post-run full acceptance attempt stopped at Ruff's format check for
the two newly added audit tests. Formatting those files resolved the only
failure; the complete gate was rerun from the beginning and passed.

## Decision log

- `2026-07-22T14:13:02Z`: allocate DD-020 only after main `dc32ff17`, no open
  PR, issue #32 as the only existing open issue, and a registry ending at
  DD-019 were confirmed.
- `2026-07-22T14:13:02Z`: use `I_N(W)` for the incremental-sharing profile so
  it cannot be confused with DD-019's action-budget profile.
- `2026-07-22`: keep all literature ownership broad and contextual; make no
  first-discovery or field-novelty claim for the narrower registered object.
- `2026-07-22`: separate the uninformative `p=1/M` proof boundary from the
  positive-information count-ranking argument.
- `2026-07-22T14:25:31Z`: pre-run `make bootstrap`, `make verify`, and
  `make site` passed: 222 tests, 91 valid claims, 48 valid run manifests, and
  71 generated pages for 24 studies. Draft PR #136 was already open before
  substantive execution. The next commit freezes the primary-run source.
- `2026-07-22T14:25:51Z`: the sole primary execution passed as
  `20260722T142551Z_DD-020_3854fff6_37c11a850a` from clean commit `3854fff6`
  in 2.428850 seconds. It created 2,555 point rows and five channel profiles;
  both exact methods, every validation gate, and all five corruptions passed.
- `2026-07-22`: separate audits approved DD-C-0092 through DD-C-0096. The
  point theorem is proof-owned; the 73-cell census is regression evidence. The
  guaranteed shortlist supplies an exact arbitrary-channel monotonicity
  counterexample and remains public.
- `2026-07-22`: post-run acceptance passed bootstrap, Ruff, strict MyPy over
  142 source files, all 224 tests, 96 claims, 49 manifests, all six paper
  builds, and a 71-page/24-study site. Adding claims legitimately refreshed
  the Three Results full-ledger provenance checksum; its six owned claims and
  content remain unchanged, and all 14 regenerated pages passed Poppler visual
  review. The DD-020 SVG passed a separate render review after label cleanup.
- `2026-07-22`: PR #136 squash-merged as `cf7bc67e`; issue #135 closed;
  post-merge CI `29929864642` and Pages `29929864954` passed; main synchronized
  cleanly; and the live study, data, claims, and evidence routes returned 200.
- `2026-07-22`: issue #139 and draft PR #140 add an output-connected Lab from
  the sole immutable run without executing research. Local validation covers
  2,044 point transitions, ten registered-channel transitions, the exact
  aggregation-minus-rescue decomposition, same-accuracy opposite signs,
  no-JavaScript tables, keyboard focus, mobile containment, and clean logs.

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

README, question, brief, frozen model/config, living plan, literature boundary,
proof and proof audit, exact implementation and independent verifier, immutable
run, report, claim audits, public metadata, CSV, and SVG.

## Blockers

No scientific blocker. Settings issue #32 is unrelated. The primary run is
complete and must not be rerun. Public integration is presentation-only and
final acceptance follows its deployment.

## Recovery and restart instructions

Read this plan, `README.md`, `status.yml`, and `configs/census.yml`; inspect Git
and PR state. Resume the first unchecked item. Never execute the primary target
from a dirty tree or rerun a passing primary configuration for freshness.

## Outcome and retrospective

Complete and deployed. The exact identity, finite point-channel theorem,
bounded census, and arbitrary-channel counterexample retain separate evidence
status and scope. No General Sharing Frontier result is claimed.
