# Model

Each task declares its world, prior, target law, evidence and dependence,
per-agent information, communication and source-choice permissions, message and
action spaces, coverage, budget, timing, feedback, rewards, objectives,
evaluator type, seeds, and claim/run provenance. A protocol receives an
immutable capability view containing only the fields named by the task and the
protocol contract. The evaluator retains target state and reference values.

Golden tasks are exact reproductions of registered finite project fixtures.
Simulated tasks are seeded estimates with confidence intervals. Missing
observables suppress a metric rather than silently imputing it.
