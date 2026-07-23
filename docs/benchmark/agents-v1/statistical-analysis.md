# Statistical analysis preregistration

Status: preregistered, not executed. The primary unit is a sealed task instance
crossed with an exact model snapshot and repeat. Every architecture contrast is
paired on that unit; generator cells and task families define sampling strata.
The future base campaign uses four batches, 200 instances, and three repeats.

## Estimands

The primary object is an eight-dimensional metric vector of paired architecture
differences: group discovery, distinct-action coverage, duplication, planner
regret, private-baseline regret, recovery-budget attainment, source diversity,
and communication-induced action compression. The four primary contrasts are
broadcast minus isolated, designated reader minus broadcast, consensus minus
isolated, and structured portfolio minus consensus.

Distances from best and worst registered equilibria, invalid actions, protocol
compliance, calls, tokens, and cost are secondary. Model-family contrasts are
paired descriptive contrasts. Provider families are not assumed independent,
and no estimate supports inference about people or organizations.

## Errors and uncertainty

The conservative primary estimand retains provider failures and missing
required outputs as zero discovery/attainment and protocol-invalid. An
available-case estimate and explicit error table are sensitivity analyses.
Schema-invalid or invalid actions remain in the denominator and receive zero
task success; they are never silently retried beyond the one registered schema
retry or dropped.

Report 95% stratified paired cluster-bootstrap intervals with 10,000
replicates, clustering by task commitment and stratifying by family and
generator cell. Exact theoretical comparators remain rational fractions and do
not receive stochastic intervals. Apply Holm familywise correction within each
metric/model family across the four primary architecture contrasts. Secondary
intervals are descriptive and receive no uncorrected significance labels.

Execution stops after the fixed four batches and three repeats, not in response
to outcomes. Release requires complete accounting of scheduled configurations,
verified custody commitments, agreement of both verification methods, complete
contamination/corruption checks, and a passing trace-safety audit. No composite
score or universal ranking may be constructed.
