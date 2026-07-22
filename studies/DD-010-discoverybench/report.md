# DD-010 report

Primary clean run `20260721T183014Z_DD-010_ce930050_8ec718c242` validates all 15
versioned golden tasks, 13 capability-declared built-ins, and 19 metrics. The
complete 195-cell compatibility matrix has 16 declared compatible pairs and
179 explicit exclusions. Every compatible metric vector reproduces its exact
source fixture and is independently recomputed. Immutable task views reject
target state, other private signals, future outcomes, undeclared sources,
evaluator state, expected values, and provenance; value and leakage corruption
tests pass.

Results remain task-level vectors, family profiles, and scoped Pareto rows. No
composite score is active. A subsequent sensitivity suite uses eight fixed
seeds and 1,000 Bernoulli draws per seed, yielding mean discovery estimate
`0.65737500`; it is a synthetic calibration estimate, not exact evidence or a
real-world performance claim. DiscoveryBench is not a hosted leaderboard.

Selective-attention v2 run
`20260721T230249Z_DD-010_add85590_56c61a2195` preserves the complete v1 metric
matrix and extends the registry to 20 tasks, 21 protocols, and 27 metrics. Its
420-cell compatibility matrix contains 28 exact compatible rows and 392
explicit exclusions. The separate verifier recomputes every row, resolves its
DD-012--DD-014 provenance, and rejects altered values, hidden target-state
access, and a corrupted compatibility count. Claim DD-C-0069 is limited to
these registered fixtures; v2 remains opt-in and activates no composite score.

Program V4 v3 run `20260722T054447Z_DD-010_d265e480_6930915b02` preserves all
v1 and v2 metric vectors and extends the opt-in registry to 24 tasks, 29
protocols, and 39 metrics. Its 696-cell compatibility matrix has 36 exact
compatible rows and 660 explicit exclusions. Eight new rows reproduce DD-016
threshold discovery, DD-017 equilibrium selection, DD-015 dynamic attention,
and DD-018 team mechanisms. The independent verifier reconstructs every value,
resolves every claim/run reference, enforces prohibited capability access, and
rejects value, compatibility, and information-leakage corruptions. The run
completed in 0.544999 seconds under its 60-second cap. V3 remains opt-in, has no
composite score, and does not evaluate external agents.
