# Corruption design

The structured registry is `corruptions.yml` and is validated against
`corruption-plan.schema.json`. These are future scientific corruptions; only
their registration schema is tested in this gate.

Each mutation must reach semantic verification after parsing. Parse failure
alone is insufficient because it does not demonstrate that the responsible
scientific invariant detects a plausible but wrong value.

The twelve categories are posterior normalization, target permutation,
equal-split payoff, unilateral deviation payoff, Nash label, continuation best
response, SPE label, tie boundary, centralized `V_2`, private `P_2`, best/worst
aggregation, and recovery classification.
