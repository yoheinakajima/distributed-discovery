# Result index

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
