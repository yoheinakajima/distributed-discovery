# Information boundary

Evaluated agents receive immutable allow-list views. They may see only the
task-local synthetic observations, action vocabulary, declared source/action
costs, reward rule, topology, remaining message budget, visible messages
permitted by that topology, and the structured-output schema.

They may not receive target state, evaluator state, expected metrics, exact
baselines, claim/run/study identifiers, public benchmark task IDs, generator
parameters not rendered in the prompt, other agents' private signals,
undeclared source identities, future outcomes, answer keys, seed material,
holdout commitments, repository files, network access, provider secrets, or
prior-batch outputs.

Model output is untrusted. Parsing occurs against a closed schema. Text outside
declared visible-message fields is rejected, not interpreted as an action.
Final grading uses structured actions and primitive evaluator state only.

No hidden chain of thought is requested, stored, inferred, or scored. A
provider's internal reasoning field, if any, is outside the instrument and must
be disabled or discarded at collection.
