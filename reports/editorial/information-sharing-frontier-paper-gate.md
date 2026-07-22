# Information Sharing Frontier paper gate

> Historical gate: this hold was resolved after DD-022 by
> `information-sharing-frontier-paper-admission.md`, which admits the qualified
> candidate for planning only.

Date: `2026-07-22`  
Issue: `#148`  
Pull request: `#149`
Evidence class: documentation and editorial judgment; no research output

## Decision

**Hold the proposed archival paper *When Does Information Sharing Improve
Decentralized Discovery?* for exactly one further registered theorem package:
Coordination-Free Positive Sharing.** This gate creates no study ID, claim,
run, proof, manuscript, submission, release, or DOI.

DD-019 through DD-021 now supply a coherent theorem family. DD-019 identifies
action-budget profiles and a same-accuracy channel separation (DD-C-0089
through DD-C-0091). DD-020 proves the point-channel incremental-sharing result
and independent-rescue decomposition and preserves a positive-shortlist
counterexample to arbitrary-channel monotonicity (DD-C-0092 through
DD-C-0096). DD-021 proves the exact channel-independent error-contraction
criterion and centralized full-capacity recovery theorem, classifies the
registered 177-scenario registry, and preserves its mixed-curve null
(DD-C-0097 through DD-C-0103).

Those results justify the theorem family, but not yet the proposed paper under
its decentralized title. DD-021's `V_L` result assumes centralized authority
to choose the posterior top-`L` targets. Its positive-sharing examples certify
that aggregation can dominate lost rescue under declared channels, but they do
not show that agents without a central portfolio selector can implement a
strict improvement. The missing link is mathematical, not presentational.

## Admission-rule audit

| Criterion | Decision | Reason |
| --- | --- | --- |
| Distinct central question | Pass | The family asks when evidence aggregation outruns the loss of independent rescue. |
| Title-level result | Partial | The exact sign criterion can carry an abstract, but the strongest recovery result is centralized and therefore does not yet carry the proposed decentralized title. |
| Natural literature and referee set | Pass | Information aggregation, team decision theory, social learning, collective search, and decentralized control form a coherent set. |
| Self-contained reason to exist | Hold | The existing pieces support a strong theorem-family account, but the promised decentralized improvement remains an open implementation question. |
| Unlikely to become preliminary before the next gate | Hold | The next declared coordination-free theorem could materially change the headline, scope, and paper architecture. |

The gate therefore does not admit the paper. It also does not require a
separate generic Recovery Budget package before reconsideration: DD-019 and
DD-021 already define and exactly classify the declared centralized recovery
budget. A later recovery paper may still be valuable, but it is not the next
blocking condition for this title.

## Exact next package

The next substantive package, if separately authorized and registered, is
**DD-022 Coordination-Free Positive Sharing**. It must state a finite
decentralized action protocol in which each agent's action is determined by
the permitted local/shared information and public randomness, with no
centralized top-`L` assignment. It must deliver one of three stopping outcomes:

1. a theorem giving sufficient conditions for a strict sharing improvement
   over the named direct-private baseline;
2. a sharp impossibility or minimal counterexample showing why the improvement
   cannot be implemented in the declared class; or
3. a bounded null/classification that honestly closes the registered search
   without paper admission.

Registration must freeze the signal channels, message/shared-information
rule, action authority, collision or duplicate semantics, baseline, objective,
state-space and resource caps, exactness class, independent verification, and
corruption plan. It must explicitly compare the decentralized value with
DD-021's centralized `V_L` upper benchmark without identifying the two.

The next file is `plans/DD022_COORDINATION_FREE_POSITIVE_SHARING.md`. The next
command after this documentation-only gate is merged and local `main` is
synchronized is:

```sh
git status --short --branch
```

Only a new bounded issue may authorize creation of that plan and research
branch.

## Preserved boundaries

- The DD-021 run
  `20260722T185924Z_DD-021_3cdbbc40_2fea269a9a` is not rerun or changed.
- The gate does not generalize the 177-scenario mixed-curve null.
- The full-capacity theorem remains a centralized-planner result.
- No current claim establishes strategic implementation, equilibrium
  selection, human behavior, or empirical effects.
- No manuscript or submission action is authorized.

## Local acceptance

The documentation-only diff passes `git diff --check`, `make bootstrap`,
`make verify`, `make papers`, and `make site`:

- Ruff formatting and lint pass; strict MyPy passes over 148 source files.
- All 235 tests pass; all 103 claims and 50 run manifests validate.
- Six papers rebuild at 12, 14, 3, 20, 20, and 20 pages with their expected
  hashes; no tracked paper artifact changes.
- The site builds 74 HTML routes for 25 studies.
- `claims/`, `results/`, scientific source, tests, and site implementation have
  no diff from the DD-021 research merge.

Branch CI runs `29951796692` and `29951810995` passed. This record is not
post-merge Pages or live-route evidence; those identifiers are retained on
GitHub only after they pass.
