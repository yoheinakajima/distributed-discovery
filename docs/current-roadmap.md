# Current roadmap — Program V4

Programs V1, V2, and the required Program V3 sequence are complete at their
registered scopes. Each new research milestone requires its own
bounded issue, state-space/resource estimate, evidence category, independent
verification plan, and corruption test where certificates are used.

| Work | Status | Durable boundary / next question |
| --- | --- | --- |
| DD-016 Threshold Discovery | complete and deployed through PR #102 | Preserve DD-C-0071 through DD-C-0074 and the immutable primary run; do not treat tied-mode selection as the equilibrium correspondence. |
| DD-017 Equilibrium Selection and Coalition Stability | complete and deployed through PR #104 | Preserve DD-C-0075 through DD-C-0078 and distinct weak-Nash, pairwise, tau-player, and symmetric-mixed meanings. |
| Program V4 later queue | active sequentially after DD-017 | Execute DD-015 at its original boundary, then DD-018 mechanisms, DiscoveryBench v3, synthetic extensions, focused paper, public Labs, and final handoff under separate gates. Program V4 is not complete. |
| Program V3 baseline | complete through PR #80 | DD-012 through DD-015 are registered and deployed without creating research evidence. |
| DD-012 Incentive to Ignore | complete and deployed through PR #82 | Preserve DD-C-0059 through DD-C-0061 and the immutable primary run. |
| DD-013 Audience Design | complete and deployed through PR #84 | Preserve DD-C-0062 through DD-C-0065, the primary run, and Audience Lab. |
| DD-014 Conditional Attention | complete and deployed through PR #87 | Preserve DD-C-0066 through DD-C-0068, the passing run, bounded class, and raw larger-class counterexample. |
| DD-015 Dynamic Attention | active frozen baseline; no result yet | Issue #110 freezes the original `M=3`, `N in {2,3}` visible-action boundary, distinct fixed-budget/stopping objectives, full-credit autonomous equilibrium, exact planner DP, and labeled verifier. Commit and execute only after pre-run acceptance. |
| DD-018 Minimum Viable Team Mechanisms | planned after DD-015 | Register and test exact threshold-team mechanisms only after DD-015 merges and deploys; unilateral implementation is not coalition-proofness. |
| Program V5 — Information Sharing Frontier | authorized after the merged Program V4 handoff | Begin with a documentation-only baseline, then register only Signal Geometry and the Action-Budget Discovery Profile after its channel-law and complexity audit. Do not start V5 research while V4 is active. |
| Program V3 focused paper | complete and deployed through PR #90 | The deterministic 20-page *Incentive to Ignore* paper, nine generated evidence assets, citation audit, all-page visual review, Pages, and live PDF pass. |
| Program V3 benchmark, experiment, and site integration | complete and deployed through PRs #93, #95, and #97 | Preserve version compatibility, static/no-tracking operation, no-JS tables, and exact provenance. |
| Program V3 final acceptance | complete through issue #98 and the final handoff | Preserve the 70-claim/40-manifest audit and do not rerun immutable primary configurations for freshness. |
| DD-010 DiscoveryBench | complete and deployed | Preserve v1's 15-task exact golden suite and capability isolation. New tasks or adapters require a versioned registration; no public submissions or universal score. |
| DD-011 Experimental Design and Power | complete synthetic package and deployed | Power is conditional on eight declared synthetic scenarios. Human deployment requires separate ethics, consent, privacy, pilot, and institutional review. |
| DD-008B Common-Source Analysis | complete and deployed | The general threshold theorem holds only for the frozen homogeneous equal-prize model. Extend to heterogeneous accuracy, source dependence, mixed choice, or dynamics under a new model. |
| Common-Source Trap working paper | complete and deployed | Working paper only: no DOI, submission, peer review, or verified novelty claim. |
| Program V2 public surface | complete and deployed | Preserve static/no-tracking/no-submission behavior, no-JS fallbacks, route registry, and download checksum manifest. |
| Integrated acquisition/truth/allocation mechanism | open research question | Seek a source-endogenous, truth/obedience-compatible, budget-balanced mechanism with explicit observability; DD-006B does not establish one. |
| Empirical validation | prohibited in current phase | No real or human data until a new ethics, identification, privacy, retention, and governance gate is authorized. |
| Repository settings (#32) | blocked on authority | Authenticate intentionally with settings-capable credentials, then follow `docs/github-setup.md`; do not retry blindly. |

After Program V4, the next program is the Information Sharing Frontier. Its
flagship question is when useful private-information sharing improves or
reduces decentralized group discovery. The initial sequence is Signal Geometry,
Incremental Sharing, the General Sharing Frontier, Recovery Budget,
coordination-free positive sharing, and Randomized Information Design. Every
result must name the signal channel, sharing intensity, private baseline, action
budget and technology, authority, reward, and equilibrium selection.

No long-term direction is removed. Reliable Discovery, the Price of Missing
Provenance, Truth/Obedience/Budget Balance, Rate–Discovery, Discovery Order,
dynamic and large-team synthesis, and The Architecture of Distributed Discovery
follow in the order and at the promotion gates in `docs/theorem-roadmap.md`.

Operational resume commands:

```sh
git switch main
git pull --ff-only origin main
make verify
```

The next substantive milestone is DD-015. Its first file is
`studies/DD-015-dynamic-attention/plan.md`; it begins only after the roadmap
reconciliation issue and pull request merge and deployment checks pass. For
settings-only work, use `docs/github-setup.md` and issue #32.
