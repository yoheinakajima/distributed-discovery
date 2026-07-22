# Current roadmap — Program V5 public integration and acceptance

Programs V1, V2, and the required Program V3 sequence are complete at their
registered scopes. Each new research milestone requires its own
bounded issue, state-space/resource estimate, evidence category, independent
verification plan, and corruption test where certificates are used.

| Work | Status | Durable boundary / next question |
| --- | --- | --- |
| DD-016 Threshold Discovery | complete and deployed through PR #102 | Preserve DD-C-0071 through DD-C-0074 and the immutable primary run; do not treat tied-mode selection as the equilibrium correspondence. |
| DD-017 Equilibrium Selection and Coalition Stability | complete and deployed through PR #104 | Preserve DD-C-0075 through DD-C-0078 and distinct weak-Nash, pairwise, tau-player, and symmetric-mixed meanings. |
| Program V4 | complete at its registered bounded scope; final acceptance recorded on issue #126 | Preserve all 88 claims, 47 immutable manifests, negative results, exact/simulated labels, and the no-human-data boundary. The handoff creates no research evidence. |
| Program V3 baseline | complete through PR #80 | DD-012 through DD-015 are registered and deployed without creating research evidence. |
| DD-012 Incentive to Ignore | complete and deployed through PR #82 | Preserve DD-C-0059 through DD-C-0061 and the immutable primary run. |
| DD-013 Audience Design | complete and deployed through PR #84 | Preserve DD-C-0062 through DD-C-0065, the primary run, and Audience Lab. |
| DD-014 Conditional Attention | complete and deployed through PR #87 | Preserve DD-C-0066 through DD-C-0068, the passing run, bounded class, and raw larger-class counterexample. |
| DD-015 Dynamic Attention | complete and deployed through PR #111 | Preserve DD-C-0079 through DD-C-0082, the immutable baseline and separately labeled threshold-two run, the full-credit reward scope, and the bounded visibility-herding null. |
| DD-018 Minimum Viable Team Mechanisms | complete and deployed through PR #114 | Preserve DD-C-0083 through DD-C-0086 and the immutable 50-row census; common-posterior allocation does not test report truthfulness, authoritative implementation is not equilibrium, and pair/tau stability is not coalition-proofness. |
| DiscoveryBench v3 | complete and deployed through PR #117 | Preserve DD-C-0087, the immutable v3 run, v1/v2 defaults and exact vectors, 36 compatible exact rows, 660 exclusions, capability isolation, and no composite score. |
| Synthetic Experiment v3 | complete and deployed through PR #120 | Preserve DD-C-0088, all three immutable versions, the 644 retained calibration failures, shared-seed v2 power rows, and the absolute no-human-data boundary. |
| Threshold Discovery paper | complete and deployed through PR #123 | Preserve the 20-page deterministic working paper, eight source-generated assets, seven immutable run mappings, claim/citation audit, all-page visual QA, and no-DOI/no-submission boundary. |
| Program V4 output-connected Labs | complete and deployed through PR #125 | Preserve exact row selection for all 8 DD-016 threshold rows, 160 DD-017 games, 64 DD-015 objective rows, and 50 DD-018 mechanism rows; every control must alter substantive output and all rows remain available without JavaScript. |
| Program V5 — Information Sharing Frontier | DD-019 through DD-022 exact research complete; DD-022 merge and editorial gate pending | Preserve the evidence hierarchy and execute admission only after the DD-022 research merge. |
| DD-019 Signal Geometry and the Action-Budget Discovery Profile | complete and deployed through PR #131 | Preserve the five channel laws, two-method exact profiles, same-accuracy counterexample scope, named private baseline, and recovery-budget semantics. |
| DD-020 Incremental Sharing and Independent Rescue | complete and deployed through PR #136 | Preserve DD-C-0092 through DD-C-0096 and the sole immutable run; the point theorem does not imply arbitrary-channel monotonicity. |
| DD-021 General Sharing Frontier | complete and deployed through PR #147 as `8b444003` | Preserve DD-C-0097 through DD-C-0103, the sole immutable run, centralized-authority boundary, exact Lab inputs, and mixed-curve bounded null. |
| DD-022 Coordination-Free Positive Sharing | complete bounded exact package under issue #150; merge pending | Preserve the certified selected interval, 42-cell classification, centralized gap, and role/ownership selection caveat. |
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

## Program V5 execution order and gate

The authoritative order is: (1) Signal Geometry and the Action-Budget
Discovery Profile; (2) Incremental Sharing and the Point-Channel Theorem; (3)
the General Sharing Frontier; (4) Recovery Budget; (5) Coordination-Free
Positive Sharing; (6) Randomized Information Design; (7) the Equilibrium
Selection Module; and (8) Mechanism and Design Implications. The versioned
channel proposal and evidence/promotion rules are in
[`program-v5.md`](program-v5.md). DD-019 completed the first package and DD-020
completed the second. The editorial ownership gate is passed: DD-020 belongs
primarily to a future Information Sharing Frontier theorem-family paper, while
*The Incentive to Ignore* may cite it as a companion and be judged
independently. The exact DD-020 public integration merged through PR #140 as
`57270680`; post-merge CI `29933212532`, Pages `29933212171`, all 171 live
files, immutable-source checksums, and deployed browser QA pass. Final
acceptance is recorded through issue #141 and PR #142. No later research
package is authorized or registered by this presentation and closeout work.

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

DD-019 through DD-021 are complete and deployed; none of their primary runs
may be rerun for freshness. The post-DD-021 editorial gate holds the proposed
decentralized paper for exactly one Coordination-Free Positive Sharing
package. DD-022 now supplies that exact package; a separate post-merge
documentation-only gate must decide paper admission.
For settings-only work, use `docs/github-setup.md` and issue #32.
