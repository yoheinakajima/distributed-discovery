# AO-0016 Information Sharing Frontier post-merge Explore Science polish

## Purpose and intended outcome

Apply only repository-supported clarity and provenance repairs from the owner-supplied
10-page Explore Science report to the accepted working paper. Produce one deterministic
draft-PR review surface and a versioned private owner upload handoff. This task makes no
new scientific evidence or external submission.

## Current state

- `main` is `41987a6a35e0d967ee75ef6e4acf214c808fef92`, the merge of PR #224.
- The accepted source SHA-256 is
  `3e671abbd5381d29fe55e273d153aa2ec5124d311103bd75ba6444e40e5fad32`.
- The accepted PDF is 28 pages at SHA-256
  `cfc892fd1a74f6fc7ebbc9b4152f678f4696448e37fdeb46ba376f0ac30a4c58`.
- Owner-supplied report: local-only SHA-256
  `9dadff0334b67d33c169a1dc659142aed655574aef22d95d0d75fb6fc2d26924`,
  10 pages, score 97/100 Platinum, zero major and six minor findings. It has no
  manuscript input hash, so report/manuscript byte identity is strongly supported by
  matching page/table/theorem references but is not cryptographically proved.
- Issue #225 and branch `agent/information-sharing-frontier-explore-polish` own this
  new post-merge editorial lane.

## DISCUSSION AND DECISION DELTA AUDIT

- The program-memory registry was read before task registration. PM-0005 through
  PM-0007 remain implemented preprint-routing policy, immutable-citation policy, and
  submission self-containment policy; none authorizes upload or status promotion.
- PM-0009 remains routed: Information Sharing Frontier is a preprint candidate, not a
  submitted paper. PM-0010 remains deferred.
- The owner adopted only evidence-backed report improvements. The report is diagnostic
  intake, not claim, theorem, run, or publication authority.
- Earlier AO-0015 is superseded only as a completed closeout. Its existing immutable
  DD-019--DD-022 evidence, Compendium v0.1.0 history, and public status remain intact.

## Scope

Editorial/provenance clarification only: A1, B1, B3, B4, C1, and B2 if existing
formulas and immutable output support it. Regenerate derived assets, package existing
sources, rebuild twice, inspect every rendered page, and stop at draft-PR review.

## Non-goals

No new theorem, claim, study, run, search, evidence update, lifecycle promotion,
provider call, spend, submission, license selection, DOI, release, merge, undraft,
manual deployment, or branch deletion.

## Milestones

1. [x] Reverify live base, report identity, scoped authority, dependency PRs, and source identities.
2. [x] Create issue #225, fixed task contract, branch, and this living ExecPlan.
3. [x] Record a discrepancy table and implement only supported manuscript/generator/test changes.
4. [x] Rebuild paper and source package twice; render and inspect all pages.
5. [x] Run focused and complete validation walls; regenerate site; prepare versioned owner-local handoff.
6. [ ] Draft PR #226 is open; await exact-head checks and stop at owner merge gate. The
   content commit is `8372583e552f774424ad4e90bf9455e9aea26190`; a following
   receipt-only commit binds the local handoff without self-reference.

## Discoveries and surprises

- C1's reviewer-proposed `D` criterion was incomplete. The immutable generator defines
  `D-boundary` as all remaining equality cases after A (`C_N<q`), B
  (`q<C_N<P_N`), and C (`C_N>P_N`), not merely `C_N=P_N`.
- The existing exact DD-022 certificate proves the theorem only at `p=3/5`; any
  higher-accuracy explanation must remain a descriptive registered-grid statement unless
  it follows directly from already registered formulas.

## Decision log

- 2026-08-30: A1, B1, B3, B4 accepted as manuscript clarifications. C1 accepted only
  from generator/registry semantics. B2 conditionally accepted subject to exact
  formula/registry support; otherwise defer it rather than create research.

## Validation strategy

Run focused source/immutable-evidence regressions, paper-native validation, deterministic
paper and extracted-package rebuilds twice, all-page visual QA, `git diff --check`, Agent
Operations/program-memory/publication/release audits, then `make verify`, `make papers`,
and `make site`.

## Commands and expected observations

- `./papers/information-sharing-frontier/validate.sh` validates existing DD-019--DD-022
  evidence and manuscript contracts without executing a scientific run.
- `make information-sharing-frontier` builds a 26--40 page deterministic PDF.
- `python scripts/build_information_sharing_frontier_arxiv_package.py --check` (or its
  repository-native equivalent) extracts and rebuilds the portable package twice.

## Artifacts produced

- Draft artifacts: report disposition; source SHA-256
  `b7a6489bc96acbfbfa6fe57cf20fdf97d25e81fe62bf2e250d985291afcb2688`;
  28-page PDF SHA-256
  `8d116b86cdbbc6cda66d65ac72077d29c15b05b86f4dc862ee8ec8e69d8f4ac0`;
  portable archive SHA-256
  `02c2090e239a8799fc751bee1b20074991502616f2053140b127a867228612e2`;
  local handoff `information-sharing-frontier-2026-08-30-explore-polish`.

## Blockers

- None at registration. Stop on unsupported B2/C1 semantics, identity drift, validation
  failure, nondeterminism, visual defect, status change, or any scope expansion.

## Recovery and restart instructions

Reverify `main`, issue #225, branch state, report/source/PDF hashes, scoped instructions,
and no substantive open PR before continuing. Resume from the first incomplete milestone.
Never infer merge or external-submission authority from this editorial task.

## Outcome and retrospective

- Focused regressions, paper-native validation, deterministic portable extraction build,
  `make verify` (1,100 passed), `make papers` (121 pages / seven PDFs), and `make site`
  (89 pages / 26 studies) pass. All 28 revised PDF pages were rendered and inspected.
- Pending: commit, exact draft-PR head, terminal GitHub checks, then owner merge review.
