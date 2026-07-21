# Execution plan

- Freeze 20 cells, outcomes, hypotheses, estimands, scenarios, exclusions, and seeds.
- Validate the schema, contrast coverage, synthetic-only identifiers, and analysis plan.
- Generate 640 balanced synthetic assignments and a small example dataset.
- Evaluate 8 hypotheses × 8 scenarios × 6 sample sizes × 1,000 replications.
- Retain all power calibration failures and compare four exact limiting fixtures.
- Run the materially separate verifier and three corruption tests.
- Preserve one clean immutable run, audit any claim, and publish read-only materials.

Compute cap: ten minutes and 2 GB. No outcome-dependent stopping.

The v2 attention extension freezes 29 cells, 14 hypotheses, 19 outcomes, 11
response scenarios, 928 balanced synthetic assignments, and 924 power rows
with 1,000 replications each. It preserves all v1 registries and uses the same
ten-minute/2 GB cap, separate random-stream verifier, three corruption gates,
fixed stopping rule, and absolute prohibition on real participant data.
