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

## AO-0012 prospective open-weight runtime work

AO-0012 audits whether the third-model purpose can be met without a
physically owner-held GPU by a reproducible open-weight, self-operated cloud
runtime. Authorization-free work freezes the exact model revision, original
BF16 artifact checksums, tokenizer, vLLM release and container digest, one
A100 80GB PCIe, CUDA boundary, RunPod Secure Cloud Pod manifest, authenticated
endpoint, no-log proxy, lifecycle, public calibration, corruptions, and
permitted decisions. It changes no base allocation or scientific design.

The sole next execution gate is the generic AO-0012 owner gate for 50 public
pairings. No credential, authenticated RunPod or Hugging Face request, model
download, GPU provision, endpoint, inference, or spend is permitted before
that gate. A later claim-grade registration must independently decide whether
the measured runtime satisfies the third-model design; AO-0012 allocates no
study and creates no claim-grade authority.

The final prospective R4 gate performs pre-ingress issue and draft-PR checks
through unauthenticated public GitHub REST and exact remote-head comparison,
then uses a documented encrypted REST Pod-create body. Its orphan boundary is
an unconditional controller finalizer plus a Pod-resident six-hour self-delete
watchdog, not a native `terminateAfter` claim. R1 through R3 remain unused and
unauthorized.

The exact R4 authorization was later accepted, but the exact live command
stopped before credential ingress because the protected runtime expected a
nonexistent `budget` mapping on the generic owner-gate manifest. No provider
resource, model download, endpoint, inference call, or spend occurred. The
permitted decision is `calibration-integrity-failure-stop`; the attempted R4
authorization is not reusable, and any prospective repair requires a new
owner amendment, protected-tree freeze, and exact gate.

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

## AO-0007 custody-path closeout

AO-0007 separately authorized one bounded retained-state diagnostic. It ran
once, verified the complete declared AO-0006 boundary without mutation, and
identified the exact failure at private task generation: the v2 campaign was
absent from the campaign-permit allowlist. Private-read authority then closed
permanently.

Prospective code now admits that already frozen campaign and enforces atomic
exclusive custody creation plus plaintext equality on sealed-object resume.
The production-path live-mode-equivalent command passes all twenty registered
classes with synthetic nonsecret content, independent AES-256-GCM
verification, six negative classes, and deterministic cleanup. AO-0006 itself
remains immutable and no separate private pilot is registered or authorized.

## AO-0008 wholly fresh repair-confirmation v3 boundary

AO-0008 registers campaign `treasurebench-agents-v1-repair-confirmation-v3`
and batch `tb-agents-v1-repair-confirmation-v3-b01` as wholly fresh identities.
The fixed design remains 50 tasks, five architectures, two exact direct model
routes, one repeat, 500 pairings, 3,016 normal calls, 256 output tokens, USD
11.51 expected, USD 15 conservative, USD 25 hard, and 5,200 calls maximum.

Authorization-free permit, production-custody, 50-task/500-run, Methods A/B/C,
corruption, lock, redaction, contamination, and cost rehearsals passed. Under
the exact owner authorization, public canaries, wholly fresh custody, and the
private prefix then passed. The fixed full batch stopped under registered
class `fixed-full-batch-failure`.

The provider phase closed at 3,067 calls and USD 13.1861145, with all hard
caps intact. A verified output lock binds 3,576 retained objects; no material
was unsealed and no call followed the lock. The campaign and batch are
permanently quarantined. This is engineering disposition only and creates no
scientific, comparative, ranking, paper, release, submission, or base-campaign
state.

## AO-0009 aggregate fixed-batch diagnostic boundary

AO-0009 used the additive R2 authority exactly once. Its aggregate-only read
authenticated all 450 fixed-full-batch traces and verified the output lock,
inventory, append-only ledgers, complete response identities, unique trace
partition, all private pairing records, and retained immutability. The read
authority is permanently closed.

The public aggregate selects `agent-protocol-policy-decision-required`: 32
traces record protocol nonconformance and 32 record parse/schema-repair
exhaustion, while terminal-provider, contamination, final-cardinality, cap,
and integrity counters are zero. AO-0009 does not change the fail-closed
protocol or authorize another private evaluation. Either action requires a
separate explicit owner task; any private evaluation also requires wholly new
identities, execution freeze, and owner gate. No v4 identity was registered by
AO-0009.

## AO-0010 policy v2 and wholly fresh v4 closeout

AO-0010 combines the owner-selected forward-only protocol-validity policy v2
and one wholly fresh v4 engineering pilot in a single Agent Operations task.
It registers campaign `treasurebench-agents-v1-repair-confirmation-v4` and
batch `tb-agents-v1-repair-confirmation-v4-b01`, with 50 new private tasks
allocated as ten tasks from each registered family, five architectures, two
exact direct provider/model routes, one repeat, and 500 intended pairings.

Policy v2 keeps the bounded two-attempt transport policy, exactly one
schema-only repair, zero semantic retries, zero silent normalization, zero
invalid-output credit, exactly-one-final-action semantics, and Method C before
performance interpretation. Protocol-invalid completed responses remain in
the full intended denominator without replacement or invented action and are
reported separately from batch integrity. Registered metric-specific feasible
bounds and architecture-contrast bounds cover all intended pairings;
complete-case estimates cannot be presented as unconditional architecture
effects.

The complete authorization-free wall passed, including zero/mixed/all-invalid
500-pairing batches, first/middle/final invalid events, Methods A/B/C,
independent metric-bound reconstruction, every existing and new relevant
corruption, production permit/custody/output-lock/unseal/redaction/cleanup
rehearsals, and the full repository validation. Execution was frozen at
`5289882dca6b8912a0518bba72aba1f4d595c2a8`, and the exact generic owner
gate and provider re-audit passed. Both public canaries and wholly fresh
custody completed before the private prefix stopped on
`provider-terminal-missing`. Provider access closed after 116 calls, 58,636
input tokens, 13,275 output tokens, and USD 0.3470610. The output lock
verified 150 retained objects without unsealing.

The incomplete batch is permanently quarantined and has no real-data protocol
classification, Methods A/B/C, metric bounds, or performance interpretation.
It cannot be retried, replaced, repaired, reopened, reused, rescored, spliced,
executed, unsealed, or reauthorized. This is DD-010 engineering only and
creates no DD-023, claim, scientific run, evidence promotion, performance
result, ranking, release, submission, or base campaign.

## AO-0011 provider-outcome policy v3 and wholly fresh v5 closeout

AO-0011 adopts the forward-only
provider-outcome policy v3, composes it with unchanged protocol-validity policy
v2, and allocates campaign
`treasurebench-agents-v1-repair-confirmation-v5`, batch
`tb-agents-v1-repair-confirmation-v5-b01`. It creates no retrospective v4
diagnostic and preserves every prior campaign and retained boundary.

Before owner authorization, the implementation must classify the complete
registered provider taxonomy independently, persist one safe terminal trace
per operationally missing pairing, enforce the sequence-only 3-consecutive
and 10-cumulative circuit breaker, quarantine contract/safety failures,
retain missing pairings in all metric denominators, and independently
reconstruct every all-pairing contrast endpoint. The frozen retry contract
remains two identical transport attempts, one schema-only repair, no semantic
or outcome-dependent retry, and no replacement.

The authorization-free acceptance wall comprises the complete 500-pairing
synthetic rehearsal, zero/mixed/all-invalid matrices, first/middle/final
logical-request and pairing missingness, isolated and mixed missingness,
exact circuit thresholds, provider protected classes, post-lock no-call
replay, production custody/commitment/lock/unseal/redaction/cleanup
rehearsals, all inherited and new corruptions, and full repository validation.
Only after the exact execution commit and R2 owner gate were committed did the
task read the two-name credential subset, create real v5 custody, call
providers, spend, and unseal after lock.

The authorized execution completed both public canaries, wholly fresh
50-task custody, the private prefix, and all 500 pairings. The terminal matrix
contains 496 protocol-valid and four protocol-invalid pairings, zero
provider-operational missingness, zero contract/safety failure, and no circuit
breaker. One transient-provider first attempt selected and completed the
frozen five-second fallback before the sole identical retry recovered.

Provider access closed after 3,058 calls and USD 13.0413660. The verified
4,067-object output lock is
`sha256:e18e7f8173f9ac0026f74cd6ff9b577010abdf65620ad269606f6862ff16e47b`.
Post-lock replay/unseal, Methods A/B/C, independent classification and
all-pairing bounds, exact correspondence and cost, contamination,
corruptions, redaction, and retained-state verification pass. No task-level
or comparative performance and no scientific evidence is created.


### AO-0012 R2 preauthorization correction

The unused R1 gate is superseded without authorization. The same public
calibration and runtime identity remain behind
`AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R2`, which adds repository-local
two-name credential ingress, temporary RunPod Secret/template lifecycle,
authorization-bound orphan controls, measured attestation, and exact
success/failure teardown and billing. This remains infrastructure engineering
only and adds no DD-023, private, scientific, base-campaign, performance, or
publication authority.


### AO-0012 R3 exact RunPod API correction

The unused R2 gate is superseded without authorization. R3 preserves the
accepted R2 lifecycle and closeout design while prospectively binding GraphQL
requests to the documented URL-encoded `api_key` query parameter with no
Authorization header, REST requests to Bearer authentication with no API-key
query parameter, and Pod creation to the exact frozen supported field set with
`allowedCudaVersions: ["13.0"]` and no `minCudaVersion`. All R3 rehearsals,
corruptions, transport tests, and validation remain synthetic and
credential-free. Only the unconsumed R3 generic owner gate may later authorize
the public calibration or honest bounded failure closeout.


### AO-0012 R4 public preflight and encrypted REST Pod correction

The unused R3 gate is superseded without authorization. R4 removes the live
dependency on `gh` authentication, verifies issue #212 and draft PR #213 from
public unauthenticated GitHub REST plus exact remote branch state, and creates
the Pod only through documented REST with `volumeEncrypted: true`, no network
volume, and the frozen exact field set. Because that REST surface has no
documented `terminateAfter` field, orphan control is an unconditional
controller finalizer plus a Pod-resident six-hour exact-Pod deletion watchdog.
Only the unconsumed R4 generic owner gate may authorize the unchanged public
calibration or honest bounded failure closeout.
