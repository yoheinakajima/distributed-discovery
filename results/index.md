# Result index

Current inventory: 35 immutable manifests, of which 32 have passing validation
and exit status zero. Final Program V2 acceptance did not create duplicate runs.

- [`baseline/`](baseline/README.md): canonical upstream reproduction artifacts.
- [`verified/`](verified/README.md): policy-verified results.
- [`exploratory/`](exploratory/README.md): observations and lower bounds not promoted.
- [`refuted/`](refuted/README.md): preserved negative, failed, and superseded results.

The M9 acceptance reproduction is `baseline/20260720T202314Z_DD-000_88613408_217c602fa0`; it started from a clean research commit and passed upstream plus independent checks. Claim records continue to cite their originally audited run IDs. DD-001 through DD-003 passing research runs are under [`verified/`](verified/README.md); each manifest distinguishes analytic, exhaustive, checked, and heuristic evidence.

Milestone A changed public licensing, deployment, and GitHub organization only. Later milestones add new immutable run IDs without altering earlier provenance.

The canonical alignment-bound run is `verified/20260721T022739Z_DD-001_358cb1eb_cd16846ba5`. Its exact Bellman certificate and separate corruption-detecting verifier close the prior canonical DD-001 interval at `325089/390625` while retaining the earlier pooled frontier as valid superseded evidence.

The DD-002 selection-robustness run is `verified/20260721T025802Z_DD-002_73a85c71_b0e5b6dc49`. It stores the exact six-rule catalogue, potential identities, strict-best-response absorption witnesses, all 45 refinement comparisons, and an independent corruption-detecting verification.

The DD-003 heterogeneous-source run is `verified/20260721T032358Z_DD-003_84238b76_2cbc13e66a`. It stores 839 canonical colored networks, the full exact first/pairwise moment census, a `3/4` versus `2/3` discovery counterexample, scalar-diagnostic audits, and a separate corruption-detecting verifier.

The DD-006B joint-mechanism run is
`verified/20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b`. It stores the exact
60-row mechanism registry, incentive slacks, accounting certificates,
DD-006/DD-006A comparison, and independent row verification supporting
DD-C-0053.

The DD-009 Architecture Atlas run is
`verified/20260721T171249Z_DD-009_bc78d249_0c3851c41a`. It preserves all 288
validity decisions, 20 exact architecture rows, the 12-cell bounded Pareto set,
and a separate evaluator supporting DD-C-0054.

The DD-010 DiscoveryBench run is
`verified/20260721T183014Z_DD-010_ce930050_8ec718c242`. It preserves 15 exact
golden tasks, 13 protocol contracts, 19 metrics, all 195 compatibility decisions,
16 exact result vectors, separate recomputation, leakage/value corruption tests,
and a clearly separated 8,000-draw seeded sensitivity suite supporting DD-C-0055.

The DD-011 Experimental Design and Power run is
`verified/20260721T185647Z_DD-011_fa0271d9_fcaa647c55`. It preserves the frozen
20-cell design, 640 balanced synthetic assignments, eight hypotheses, eight
response scenarios, 384 power/MDE rows, 384,000 Monte Carlo draws, all retained
calibration failures, four exact limiting-model checks, and separate
recomputation/corruption evidence supporting DD-C-0056. It contains no human data.

The DD-008B Common-Source Analysis run is
`verified/20260721T192412Z_DD-008B_649deb08_29dbeaf3a9`. It preserves 105 exact
private/planner threshold rows, reproduces all 126 frozen DD-008A classifications,
matches 84 separately enumerated payoff margins, checks 16,368 proof-kernel
instances, and rejects two corruptions. It supports the general finite-`N`
threshold theorem DD-C-0057 and the exact universal-under-acquisition
counterexample DD-C-0058.

The three Program V2 primary runs above are immutable and must not be rerun just
to refresh timestamps. Their public summaries are generated only after manifest
and output checksum validation.
