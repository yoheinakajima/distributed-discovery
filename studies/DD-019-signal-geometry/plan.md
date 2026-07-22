# DD-019 execution plan

## Purpose and intended outcome

Construct a versioned finite channel registry and determine whether channels
with identical one-person Bayes accuracy can have different exact pooled
action-budget discovery profiles.

## Current state

Issue #130 and branch `research/dd019-signal-geometry` are active. No run,
claim, or numerical result exists. Program V5 baseline PR #129 is merged.

## Scope and resource audit

Version one fixes `M=4`, `N=3`, `L=1..3` and five exact channel families. The
largest alphabet has eight signals, so labeled enumeration visits at most
2,048 target/signal states per channel; histogram enumeration is smaller.
Runtime is estimated below 10 seconds and capped at 120 seconds; memory is
estimated below 64 MB and capped at 1 GB. All registered probabilities use
exact rational arithmetic.

## Milestones

1. Freeze schema, channel laws, baselines, complexity, and boundaries.
2. Implement labeled enumeration, independent histogram verification, and
   corruption gates.
3. Pass targeted/full validation, commit source, and open a draft PR.
4. Execute exactly one immutable primary configuration.
5. Audit claims separately and integrate report, plots, public data, and page.
6. Pass PR/post-merge CI, Pages, and live-route checks.

## Validation strategy

Check schema and probability normalization, posterior identities, Bayes-action
correspondence, relabeling invariance, `0<=V_L<=1`, monotonicity in `L`, both
exact methods' agreement, baseline bounds, recovery-budget semantics, and
corruptions of channel mass, profile value, and recovery budget.

## Non-goals

No general scalar-sufficiency theorem, strategic equilibrium, threshold-team
technology, canonical `M=16,N=8` exact result, simulation, human data, or
novelty claim is in scope.

## Progress checklist

- [x] V5 baseline merged; live registry audited through DD-018.
- [x] Issue, branch, bounded fixture, resource estimate, and exactness plan set.
- [x] Schema, model, implementation, verifier, config, and tests pass.
- [ ] Clean source commit and draft PR precede the sole primary run.
- [ ] Evidence, claims, report, plots, public data, and study page pass.
- [ ] PR, post-merge workflows, and live routes pass.

## Recovery

Read this plan, `README.md`, `status.yml`, and `configs/baseline.yml`; inspect
Git state. Never run the primary target from a dirty tree or repeat a passing
primary configuration for freshness.

## Discoveries and retained failures

- The first full repository gate rejected the unrecognized public phase
  `registered-source-development`; it was changed to the supported
  evidence-neutral phase `registered`.
- A targeted test after the site build loaded a previously built non-editable
  wheel and reproduced the already-fixed impossible-observation divide-by-zero.
  Reinstalling the local package after adding its new directory resolves this
  environment-cache failure. It created no run or evidence.
