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

DiscoveryBench v3 is complete and deployed. PR #117 squash-merged as
`3b4fdbe`; issue #116, post-merge CI `29895085124`, Pages `29895085148`, and
the live benchmark, study, schema, and summary routes passed. Synthetic
Experiment v3 is the next sequential Program V4 milestone.

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

Frozen source commit `d265e480` and draft PR #117 preceded the sole v3 run
`20260722T054447Z_DD-010_d265e480_6930915b02`. It passed in 0.544999 seconds,
verified all 36 exact rows, retained 660 exclusions, resolved all provenance,
and rejected all three corruptions. Direct comparison confirms the first 28 v3
metric vectors equal the complete v2 output matrix. DD-C-0087 passed its
separate audit. The immutable run must not be repeated.

Final local acceptance passed bootstrap, Ruff, MyPy on 131 source files, all
208 tests, the 87-claim ledger, all 46 manifests, and the 62-page/22-study site.
The generated benchmark surface selects v3, preserves the v2-only attention
page boundary, publishes all three schemas, and links the immutable run and
DD-C-0087. PR #117 passed both required checks and squash-merged as `3b4fdbe`.
Post-merge CI `29895085124` and Pages `29895085148` passed; issue #116 closed;
the live benchmark, DD-010 study, v3 schema, and summary routes returned HTTP
200. The live summary names the immutable run and reports 24 tasks, 29
protocols, 39 metrics, 36 compatible pairs, and 660 exclusions. The next
milestone is the separately registered Synthetic Experiment v3.

## Implemented-not-evaluated Agents v1 layer

The 2026-07-23 registration gate assigns the software-agent instrument to
DD-010 without allocating a study or claim. Content versions v1/v2/v3 remain
immutable; `agents-v1` is a separate protocol axis. Registration freezes task
families, information rights, architectures, provider candidates, cost
envelope, custody, contamination, trace/redaction, statistical estimands,
metrics, two-path verification, 24 corruptions, schemas, public fixtures, and
offline validators.

The offline implementation and public conformance rehearsal are complete.
Provider calls, model invocations, model downloads, private generation,
provider traces, performance results, and spending remain prohibited. The
exact next gate is DiscoveryBench Agents v1 evaluation campaign registration
and cost authorization. It must be opened separately; this plan creates no
authority for that campaign.

The 2026-07-23 evaluation registration under issue #173 selects a sealed
engineering pilot pending owner authorization and keeps the claim-grade base
blocked on local/open feasibility. The inactive authorization has zero caps
and permits no execution. DD-010 continues to own the instrument; no new study,
claim, private material, trace, result, or run is created.

## AO-0004 public provider-schema conformance boundary

Issue #198 separately registers the public-only provider-schema conformance
repair after the fresh repair-confirmation pilot stopped at its first OpenAI
HTTP 400. The corrected offline reconstruction retains `minItems` and
`maxItems` for the pinned standard OpenAI snapshot and omits only `maxLength`
and `uniqueItems` from that transport. It does not claim which constraint or
other request interaction caused the historical failure because the provider
error body was intentionally not retained.

The canonical semantic contract remains unchanged. Separate OpenAI and
Anthropic transport compilers omit only unsupported transport constraints,
while post-parse validation preserves message length, cardinality, uniqueness,
identity and vocabulary checks; Method C and metric ranges remain mandatory.
The exact mock matrix and all corruptions must pass before an execution freeze.
R3 later stopped after its bounded six-call public sequence without
conformance. Its complete Anthropic response used exactly the 128-token
ceiling but retained no stop reason or validation stage, so truncation is a
hypothesis only and every R3 artifact remains immutable.

The separately authorized R4 repair used a fresh ledger, fixed safe failure
stages, invalid-output hashes without raw retention, and a 256-token
complete-output ceiling for both providers without weakening the semantic
contract. OpenAI and Anthropic each passed their minimal and complete
provider-specific action schemas, and the canonical exactly-one-final-action
semantic contract passed independently. The four ordered calls used 1,603
input tokens and 275 output tokens and cost USD 0.0086685: OpenAI USD
0.0031875 and Anthropic USD 0.005481. No bisection ran. Private and scientific
state remained unchanged.

This is public provider-schema and semantic-contract engineering conformance,
not scientific evidence or model-performance evidence. R1 and R2 remain
superseded and unused; R3 and R4 remain consumed and immutable. A later wholly
fresh sealed repair-confirmation pilot registration required wholly new
private identities and separate owner authority; AO-0006 subsequently
registered and executed that v2 candidate.

## AO-0006 fresh repair-confirmation v2 boundary

AO-0006 froze campaign `treasurebench-agents-v1-repair-confirmation-v2`, batch
`tb-agents-v1-repair-confirmation-v2-b01`, 50 new private tasks, five
architectures, two direct routes, one repeat, a 500-run matrix, and a maximum
256-token output ceiling. Its public synthetic rehearsal completed all 500
runs and rejected all 69 registered corruptions before authorization.

Under the exact R2 owner gate, both direct-provider public canaries passed in
two calls using 1,349 input tokens and 253 output tokens for USD 0.0076095.
Custody creation then failed under the registered coarse class
`custody-creation-failure`. The batch is permanently quarantined with zero
private architecture/model runs. Its provider phase is closed; eight safely
lockable objects are preserved under output lock
`sha256:127a9c796459c7627f6fd90b92ef1587ad0f6b1910b4ff255c2ceb976f3ab25f`;
no provider call followed the lock and no material was unsealed.

The retained private state contains a new seed and task and answer keys but no
task ciphertext, answer ciphertext, or custody manifest. Methods A/B/C,
private pairing, and metric-range checks are not applicable to the unstarted
private matrix. This is a failed DD-010 engineering batch, not scientific or
model-performance evidence. No retry, repair-in-place, replacement, splice,
rescore, ranking, claim, paper result, release, or base campaign is authorized.
