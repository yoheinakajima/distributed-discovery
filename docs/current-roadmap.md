# Current roadmap — Program V3

Programs V1 and V2 are complete at their registered scopes. Program V3 is the
authorized active sequence. Each research milestone still requires its own
bounded issue, state-space/resource estimate, evidence category, independent
verification plan, and corruption test where certificates are used.

| Work | Status | Durable boundary / next question |
| --- | --- | --- |
| Program V3 baseline | complete through PR #80 | DD-012 through DD-015 are registered and deployed without creating research evidence. |
| DD-012 Incentive to Ignore | complete and deployed through PR #82 | Preserve DD-C-0059 through DD-C-0061 and the immutable primary run. |
| DD-013 Audience Design | complete and deployed through PR #84 | Preserve DD-C-0062 through DD-C-0065, the primary run, and Audience Lab. |
| DD-014 Conditional Attention | complete and deployed through PR #87 | Preserve DD-C-0066 through DD-C-0068, the passing run, bounded class, and raw larger-class counterexample. |
| DD-015 Dynamic Attention | optional registration | Begin only after required Program V3 milestones if capacity remains; keep stopping and fixed-budget objectives distinct. |
| Program V3 focused paper | complete and deployed through PR #90 | The deterministic 20-page *Incentive to Ignore* paper, nine generated evidence assets, citation audit, all-page visual review, Pages, and live PDF pass. |
| Program V3 benchmark, experiment, and site integration | benchmark v2 implementation passes locally on issue #91 | Commit and run the clean immutable 20-task attention benchmark, then extend the synthetic kit and publish the final accessible surface. |
| DD-010 DiscoveryBench | complete and deployed | Preserve v1's 15-task exact golden suite and capability isolation. New tasks or adapters require a versioned registration; no public submissions or universal score. |
| DD-011 Experimental Design and Power | complete synthetic package and deployed | Power is conditional on eight declared synthetic scenarios. Human deployment requires separate ethics, consent, privacy, pilot, and institutional review. |
| DD-008B Common-Source Analysis | complete and deployed | The general threshold theorem holds only for the frozen homogeneous equal-prize model. Extend to heterogeneous accuracy, source dependence, mixed choice, or dynamics under a new model. |
| Common-Source Trap working paper | complete and deployed | Working paper only: no DOI, submission, peer review, or verified novelty claim. |
| Program V2 public surface | complete and deployed | Preserve static/no-tracking/no-submission behavior, no-JS fallbacks, route registry, and download checksum manifest. |
| Integrated acquisition/truth/allocation mechanism | open research question | Seek a source-endogenous, truth/obedience-compatible, budget-balanced mechanism with explicit observability; DD-006B does not establish one. |
| Empirical validation | prohibited in current phase | No real or human data until a new ethics, identification, privacy, retention, and governance gate is authorized. |
| Repository settings (#32) | blocked on authority | Authenticate intentionally with settings-capable credentials, then follow `docs/github-setup.md`; do not retry blindly. |

High-value theoretical questions are heterogeneous source quality, correlated
independent sources, alternative prize sharing, dynamic acquisition, reusable
evidence value, and equilibrium selection beyond anonymous pure source counts.
High-value benchmark questions are new exact tasks, adapter conformance, and
robust multi-metric aggregation without collapsing the registry into an
unexplained score.

Operational resume commands for the active benchmark extension:

```sh
git switch benchmark/attention-extension
make verify
```

The next file is `plans/MASTER_EXEC_PLAN.md`; DiscoveryBench v2 proceeds from
its frozen implementation to a clean immutable run and claim audit. For
settings-only work, use `docs/github-setup.md` and issue #32.
