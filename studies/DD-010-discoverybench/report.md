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
