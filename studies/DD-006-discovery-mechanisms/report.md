# DD-006 score-difference mechanism report

Primary immutable run `20260721T051457Z_DD-006_d49a50ea_068bce4af3` enumerates
the nine mechanisms in ADR-0012: three observable score regimes multiplied by
coefficients `-1`, `0`, and `1`. The run evaluates all nine joint
report-action deviations for each of the three signal types using exact rational
probabilities. An independent realized-outcome accounting check verifies that
each score-difference transfer pair sums to zero.

For every positive coefficient, truthful reporting and direct action form a
weak pure Bayesian Nash equilibrium and yield discovery probability `8/9`.
The target-identity regime leaves all 27 symmetric deterministic action maps
as action best responses after truthful reports; the positive individual-success
and sole-rescue regimes leave one each. None of the nine registered mechanisms
makes truthful/direct play strict against all joint report-action deviations.

This is an exact boundary for the deliberately narrow score-difference family.
It does not establish a result for arbitrary transfer tables, mixed strategies,
dominant-strategy implementation, or different outcome observability.
