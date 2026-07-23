# Benchmark content contract

DiscoveryBench v1/v2/v3 remain immutable exact-content versions. Agents v1 may
reference only declared source task families, claims, immutable runs, action
spaces, information rights, and exact comparator values. It may not edit a
source task, replace a baseline, alter a golden vector, or imply that a model
estimate changes theorem status.

Every generated task records the content sources it derives from, but prompts
remove DD IDs, claim IDs, run IDs, paper titles, theorem names, known values,
and exact public wording. The evaluator retains the source mapping outside the
agent-visible view.

Exact baselines are fractions or exact classifications. Agent outcomes, if
later executed, are stochastic software-agent estimates tied to the complete
execution configuration. Missing observables suppress a metric. No value is
imputed and no composite score is created.
