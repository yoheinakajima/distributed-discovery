# Executed plan

Validate the task schema and adversarial bad fixtures; construct fifteen exact
golden tasks and thirteen built-in protocol contracts; enumerate the complete
declared compatibility matrix; execute every compatible pair with exact
fractions; run a bounded seeded sensitivity suite only after exact validation;
and preserve task-level results, profiles, Pareto comparisons, exclusions, and
provenance. A separate verifier recomputes every golden value, rechecks
capabilities and counts, and rejects one corrupted value and one leaked target
capability.

The primary ceiling is 15 tasks, 13 protocols, 195 candidate pairs, 60 seconds,
and 1 GB. No checkpoint may overwrite an immutable run.

The v2 attention extension appends five tasks, eight protocols, and eight
metrics. Its ceiling is 20 tasks, 21 protocols, 420 candidate pairs, 60 seconds,
and 1 GB. It must preserve every v1 default and golden vector, independently
recompute attention values, and reject value, access, and compatibility
corruptions before any seeded sensitivity calculation.

The active v3 Program V4 extension appends four tasks, eight protocols, and
twelve metrics. Its frozen ceiling is 24 tasks, 29 protocols, 39 metrics, 696
candidate pairs, 36 compatible exact rows, 660 explicit exclusions, 60
seconds, and 1 GB. Version-preservation tests compare every v1 and v2 output
vector before the eight new exact rows. The independent verifier reconstructs
all expected values directly from the immutable DD-016, DD-017, DD-015, and
DD-018 evidence records and repeats schema, provenance, count, capability, and
three corruption checks. No composite score or external adapter is enabled.

Issue #116 and branch `research/discoverybench-v3-program-v4` are active. No
v3 benchmark run or claim exists before the clean-source execution gate.

The first full v3 repository gate stopped at MyPy because a generic JSON-like
certificate value was passed directly to `int` in the new registered-count
check. The runner now rejects noninteger count values before comparing them;
the exact registry and targeted tests were already passing, and no run or
evidence directory was created.

After the count-type correction, pre-run acceptance passed Ruff, MyPy on 131
source files, all 208 tests, the unchanged 86-claim ledger and 45 manifests,
and the 62-page/22-study site. Exact dirty-tree previews reproduce 16 v1, 28
v2, and 36 v3 compatible rows with all version-preservation and corruption
checks passing. The next action is the frozen source commit and draft PR; only
then may the one v3 benchmark configuration execute.
