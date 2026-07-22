# DD-022 Coordination-Free Positive Sharing execution plan

## Purpose and intended outcome

Prove or reject a strict positive value of sharing under a protocol that is
coordination-free in the frozen DD-022 sense: simultaneous anonymous agents,
no role labels or assignment, no visible prior action, no correlated public
randomization, no post-disclosure communication or personalized advice, and
independent private randomization only. Complete the exact research package,
public Lab, merged deployment, and the separate post-merge paper-admission gate.

## Current state

At `2026-07-22T20:40:56Z`, clean `main` and `origin/main` both resolved to
`06523c8d9ff6d0f4e66457997f5094b69065ec95`. The connected GitHub view found
no open pull request and issue #32 as the sole pre-existing open issue. The
registry ends at DD-021 and no DD-022 issue, study, or branch existed. Issue
#150 now authorizes DD-022 and branch
`research/dd022-coordination-free-positive-sharing` is the sole substantive
lane. The one authorized `gh auth status` probe found no authenticated CLI
host; use SSH for Git and the connected GitHub integration for issue/PR work.

## Scope

The primary theorem fixes two binary targets, a uniform prior, two agents,
binary point signals with accuracy `p in (1/2,1)`, and a world-level mixture:
with probability `rho` both signals equal one common draw, otherwise they are
conditionally independent draws. Agents split a unit prize equally when they
select the true target. The private game restricts the selected class to
anonymous label-equivariant strategies that follow the private signal with
probability `r`. The shared game publicly reveals both signals and selects the
anonymous symmetric Nash equilibrium in each posterior game. The theorem slice
is `p=3/5`; the bounded extension uses exact rational `p` and `rho` grids.

## Non-goals

No asymmetric role allocation is called coordination-free. No claim covers all
equilibria, coalition-proofness, correlated equilibrium, learning dynamics,
arbitrary targets or agents, human or real data, the optional per-agent-copying
law, the optional large canonical diagnostic, manuscript drafting, submission,
DOI, release, upstream mutation, or the isolated ActiveGraph repository.

## Assumptions

The source mixture is drawn once at the world level. Actions are simultaneous;
private randomization seeds are independent. Shared evidence and its common
posterior are allowed, but no public random seed or action authority is. Total
realized prize is one exactly when discovery occurs and zero otherwise.
DD-021's `V_2=1` in the binary two-action benchmark is centralized and is used
only as an upper comparator.

## Milestones

1. **Registration and analytic freeze (complete):** live audit, issue, branch,
   draft PR, model, proof obligations, literature boundary, resource and
   corruption contracts.
2. **Exact implementation (complete):** closed forms, direct state/deviation enumeration,
   complete selected-class and bounded pure correspondences, tests, and exact
   root certificate.
3. **Immutable evidence (complete):** full pre-run gate, clean source commit, one primary
   run, result integration, and separate claim audits.
4. **Public integration and research merge (complete):** Findings, relationships, Lab,
   full local/remote acceptance, merge, Pages, live routes, issue closure, and
   clean synchronized main.
5. **Paper-admission gate (decision complete; merge pending):** separate documentation-only issue/branch/PR after
   Milestone 4; decide admit/hold/reject and, if admitted, create only a paper
   issue, paper ExecPlan, theorem/section map, and ownership map.

## Progress checklist

- [x] Read repository authority, prior Program V5 gate, required predecessor
  studies, claim/reproducibility/governance policies, market/dependence code,
  site relationships, Labs, and tests.
- [x] Audit Git/worktrees, registry, claims tail, open issues/PRs, and the one
  authorized CLI authentication probe.
- [x] Create issue #150 and the research branch.
- [x] Freeze study documents, exact grid, complexity, certificate, and draft PR.
- [x] Prove the private and shared selected equilibria including boundaries.
- [x] Prove the exact selected `p=3/5` positive-sharing threshold.
- [x] Implement two methods, pure-correspondence audit, and corruptions.
- [x] Pass pre-run acceptance and commit a clean source state.
- [x] Execute the primary configuration exactly once.
- [x] Audit claims and integrate exact evidence and public presentation.
- [x] Pass full local acceptance.
- [x] Merge/deploy, close #150, and synchronize main.
- [ ] Merge the completed documentation-only paper-admission decision.

## Discoveries and surprises

- The user-requested `docs/research-output-architecture.md` is absent. The
  earlier DD-021 ExecPlan records the same absence; the live replacement
  authority is `docs/research-governance.md` plus
  `docs/paper-family-map.yml`.
- GitHub CLI is unauthenticated, as expected. The connected GitHub integration
  can perform issue and pull-request operations, while SSH remains available
  for Git transport.

## Decision log

- `2026-07-22T20:40:56Z`: allocate DD-022 only after confirming clean expected
  main, no open PR, issue #32 only, a registry ending at DD-021, and no existing
  DD-022 allocation.
- `2026-07-22T20:40:56Z`: omit the optional per-agent-copying and canonical
  large-fixture diagnostics unless the primary theorem, exact bounded extension,
  and completion gates finish with ample capacity.
- `2026-07-22T20:40:56Z`: treat the selected anonymous symmetric equilibrium,
  full pure correspondence, direct-private rule, and centralized benchmark as
  four separately labeled objects.
- `2026-07-22T21:00:00Z`: independent equilibrium enumeration found that
  signal-ownership-aware symmetric rules split the targets on disagreement.
  Narrow the public theorem to the posterior-only, provenance-blind identical-
  mixing selection; preserve the broader correspondence as a negative result.
- `2026-07-22T21:00:00Z`: correct the mechanism language: the public agreement
  pattern updates the latent dependence posterior but does not reveal the
  realized source branch.
- `2026-07-22T21:02:00Z`: the pre-run gate passed strict Ruff, strict MyPy,
  all 241 tests, claim and 50-manifest validation, all six paper builds, and a
  75-page site build covering 26 studies. The 42-cell preview classified six
  positive, 18 negative, and 18 neutral selected comparisons.
- `2026-07-22T21:03:34Z`: execute the sole primary run from clean commit
  `2376d5b7`; run `20260722T210334Z_DD-022_2376d5b7_ad67765ca8` passed in
  0.297666 seconds at 21.719 MB peak memory.
- `2026-07-22T21:15:00Z`: browser QA exercised all four Lab controls, observed
  exact gain `9/1672` at `p=3/5,rho=3/4`, retained exactly one selected table
  row, and found no console error.
- `2026-07-22T21:19:00Z`: final local acceptance passed strict lint/typecheck,
  all 244 tests, 110 claim records, 51 manifests, all six paper builds, the
  76-page/26-study site, checksum and relationship validation, focused secret
  and host-path scans, and clean pinned upstream state.
- `2026-07-22T21:45:00Z`: PR #151 merged as `c8a11bd3`; post-merge CI
  `29959514182`, Pages `29959514196`, and nine live route checks passed. Issue
  #150 closed and local `main` synchronized.
- `2026-07-22T21:45:35Z`: issue #152 decided to admit the qualified paper
  candidate and created paper issue #153. Admission remains planning-only and
  requires the selected-equilibrium and every-equilibrium-failure boundaries.

## Validation strategy

Use exact `Fraction`/integer algebra for every equilibrium and theorem sign.
Method A evaluates the symbolic closed forms. Method B enumerates target,
source-mixture, signal, action-randomization, and unilateral-deviation states
without importing Method A's equilibrium formulas. Check normalization,
target/label and player symmetry, payoff budget balance, bounds, best responses,
boundary cases, root polynomial and isolating interval, signs on both sides,
method agreement, pure correspondences, and every registered corruption.
Then run repository claim, manifest, paper, site, relationship, checksum,
security, host-path, license, provenance, upstream, browser, accessibility, CI,
Pages, and live-route gates.

## Commands and expected observations

- `make bootstrap`: install the locked environment.
- `uv run --no-editable pytest ...`: targeted DD-022 model, verifier, CLI,
  claims, and site tests pass with exact values.
- `make verify`: Ruff, strict MyPy, complete tests, claims, and manifests pass.
- `make papers`: all existing papers rebuild; the research lane creates no new
  manuscript.
- `make site`: all routes, exact downloads, no-JavaScript tables, and
  relationships validate.
- The DD-022 primary target refuses a dirty tree, creates one immutable run ID,
  stays below its registered time/memory caps, and is never rerun for freshness.

## Artifacts produced

This plan; the DD-022 study package; exact source and tests; one immutable run;
separate claim checks; result tables/certificates; Findings, relationship, and
Lab integration; research merge/deployment evidence; and the later
documentation-only admission decision.

## Blockers

No current blocker. Settings-only issue #32 is unrelated. CLI authentication
failure does not block Git transport or connected GitHub issue/PR operations.

## Recovery and restart instructions

Read this plan, `studies/DD-022-coordination-free-positive-sharing/README.md`,
`plan.md`, and `status.yml`; inspect Git and GitHub state; resume the first
unchecked item. Never rerun a passing DD-022 primary configuration. Preserve
all failed runs, nulls, counterexamples, and selection caveats.

## Outcome and retrospective

The research package is complete, merged, deployed, and live. The exact
selected-equilibrium theorem closes the prior centralized-implementation gap,
while the pure correspondence prevents an every-equilibrium overclaim. Final
closeout requires only merge of the documentation-only admission gate; no
research artifact will change there.
