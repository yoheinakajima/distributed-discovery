# DD-010 — TreasureBench

TreasureBench is a static, auditable benchmark for how declared multi-agent
protocols convert evidence into search actions. It contains exact golden
fixtures tied to existing project claims and runs plus a small seeded synthetic
sensitivity suite. It is not a hosted leaderboard or a universal measure of
real-world agent quality.

DiscoveryBench is the historical/internal compatibility alias and remains the
correct token in this directory name, frozen schema IDs, task IDs, protocol
IDs, metric IDs, commands, and immutable outputs. No content version was
created for the display rename. Treasure Hunt is the playable companion to the
TreasureBench suite; it is not a separate benchmark.

Run `make dd010-discoverybench` only from a clean committed implementation to
create the immutable primary run. Use `distributed-discovery benchmark --help`
for read-only registry and evaluator commands.

The selective-attention extension is explicitly versioned as v2: it appends
five DD-012--DD-014 tasks, eight protocols, and eight metrics while keeping the
v1 command default and exact output vectors unchanged. Run it from a clean
commit with `make dd010-attention`, or inspect it with
`distributed-discovery benchmark --version v2 run-golden`.

The Program V4 extension is explicitly versioned as v3. It appends four exact
DD-016--DD-018 tasks, eight protocols, and twelve metrics while preserving v1
as the default and v2 as the unchanged attention extension. Inspect it with
`distributed-discovery benchmark --version v3 run-golden`. The registered
primary command is `make dd010-threshold` and may run only from clean committed
source.

V3 primary run `20260722T054447Z_DD-010_d265e480_6930915b02` passed from clean
commit `d265e480` and must not be rerun for freshness. DD-C-0087 and the report
are the bounded evidence record.

## Implemented Agents v1 offline instrument layer

TreasureBench Agents v1 is registered under DD-010 as an offline instrument,
not as benchmark content v4 and not as a new study. It may explicitly select
unchanged v1, v2, or v3 content while independently freezing agent protocol
`agents-v1` and generator `agents-task-generator-v1`.

The implementation realizes five finite task families, five agent architecture
contrasts plus exact comparators, separate metrics with no composite, sealed
custody, contamination probes, safe visible traces, and independent
verification. Its status is `implementation-complete-not-evaluated`. A
deterministic 50-case public rehearsal passes, Method A and Method B agree, and
all 24 public corruptions are rejected. No provider call, model invocation,
model download, private seed, holdout, private answer key, evaluated provider
trace, performance result, external cost, claim, or run exists.

Future evaluation requires its own campaign registration, exact snapshot gate,
explicit owner cost authorization, custody material, and immutable evidence
package. The current v1/v2/v3 commands, outputs, default, and disabled external
adapter remain unchanged.

## AO-0012 open-weight self-operated cloud-runtime gate

AO-0012 is a prospective DD-010 infrastructure task, not a scientific run or
claim-grade campaign. It separates open-weight model-family diversity,
inference-stack transparency, independence from the two proprietary model
providers, owner control, physical locality, and infrastructure-provider
independence. The primary candidate is an open-weight, self-operated cloud
runtime on one RunPod Secure Cloud A100 80GB PCIe with the exact registered
Mistral Small 3.1 24B revision, original BF16 weights, and an immutable vLLM
container. It is never called local and supplies neither physical locality nor
complete infrastructure independence.

Only one ten-task, five-architecture, one-repeat public calibration may later
run behind the exact generic owner gate. It has 50 intended pairings, no
private material, no performance publication, no model-provider API, and no
scientific authority. Until that gate is authorized, credential access,
model download, provisioning, endpoint launch, inference, and spend remain
zero and prohibited. The exact BF16 single-A100 identity fails closed rather
than quantizing, sharding, changing model, or changing GPU class.

The unused R1, R2, and R3 gates are superseded without authorization. R4 preserves
the accepted R2 repository-local credential ingress, temporary RunPod
Secret/template lifecycle, orphan controls, measured attestation, deterministic
success/failure finalizer, exact teardown and billing, and reporting boundary.
It retains URL-encoded
`api_key` query authentication only for RunPod GraphQL, Bearer authentication
only for RunPod REST, and `allowedCudaVersions: ["13.0"]`. R4 also removes any
live `gh` authentication dependency, requires `volumeEncrypted: true` in one
exact REST Pod-create request, and uses a controller finalizer plus Pod-resident
six-hour delete watchdog because the selected encrypted REST surface has no
documented `terminateAfter` field. No real credential, account, artifact,
resource, or spend is accessed by this correction.

The exact R4 owner authorization was later created once, but the exact live
command stopped before `.env.txt` ingress because the protected runtime looked
for a nonexistent generic owner-gate `budget` mapping. The registered outcome
is `calibration-integrity-failure-stop`: zero credentials, RunPod resources,
model downloads, endpoints, inference calls, or spend occurred, and no
teardown or billing ambiguity exists. The attempted authorization cannot be
reused; PR #213 and issue #212 remain open for a separately owner-authorized
prospective repair and refreeze.

## Agents v1 sealed-pilot repair adjudication

The first sealed engineering pilot remains permanently
`sealed-pilot-quarantined-provider-failure`. Issue #191 completed an exact
owner-authorized read-only engineering adjudication without a provider call,
credential read, retained-state mutation, or new private generation.

The redacted aggregate reconstruction found 137 of 500 runs with invalid final
cardinality, including 265 over-budget final outputs; 138 metric records were
affected by credited extra actions, and 57 legacy coverage values exceeded the
registered proportion range. One provider-service event recovered. One
terminal event remains exact-cause unresolved and accounts for one
protocol-invalid run; the other original protocol error is a separate
downstream failure. Detailed dimensions, metric values, sensitivity, and
performance remain private.

The prospective instrument enforces exactly one final action per required
agent through schemas, prompts, parsing, orchestration, both evaluators,
independent Method C, and metric-range checks. The repaired 50-case public
rehearsal rejects 28 of 28 corruptions. Its decision is
`instrument-repaired-fresh-sealed-pilot-required`; a wholly fresh pilot under
separate registration and owner authorization is the next possible gate.

## Agents v1 fresh repair-confirmation closeout

Issue #196 separately registered and authorized a wholly fresh engineering
campaign, `treasurebench-agents-v1-repair-confirmation-v1`, batch
`tb-agents-v1-repair-confirmation-v1-b01`. It stopped at its first public
canary with decision `sealed-pilot-quarantined-provider-failure`: one direct
OpenAI HTTP 400 `schema-or-parameter` attempt, zero Anthropic calls, zero
reported input or output tokens, USD 0.00, and zero private runs.

The provider phase is closed and its six retained objects are locked under
`sha256:8102a6c1b6bda003336d5503136dfe29301b04cb8f35e7740edd8d56f0eb3c1d`.
The R2 authorization is inactive and archived. No task seed, private task,
answer, task key, answer key, task ciphertext, answer ciphertext, or custody
manifest was created. The campaign and batch cannot be retried, repaired,
reopened, reused, rescored, executed, or reauthorized.

This is redacted DD-010 engineering status only. AO-0004 and issue #198 own
the separately registered **TreasureBench exact provider-schema conformance
repair and public-canary gate**. Its R3 public canaries terminated after six
calls without conformance: OpenAI minimal/complete and Anthropic minimal
passed, Anthropic complete was HTTP 200 local-invalid at the exact 128-token
ceiling, and both frozen Anthropic bisections passed. Output truncation remains
a hypothesis because R3 retained neither stop reason nor validation stage.
Every R3 artifact remains immutable.

The separately authorized R4 execution kept the canonical contract unchanged,
used a fresh public ledger, and raised both complete-output ceilings to 256.
OpenAI and Anthropic each passed their minimal and complete provider-specific
TreasureBench action schemas, and independent post-parse validation passed
the exactly-one-final-action semantic contract. The four ordered calls used
1,603 input tokens and 275 output tokens and cost USD 0.0086685: OpenAI USD
0.0031875 and Anthropic USD 0.005481. No bisection ran.

This result is provider-schema and semantic-contract engineering conformance,
not scientific evidence, model-performance evidence, peer review, external
validation, or comparative performance. Private and scientific state
remained unchanged. R1 and R2 remain superseded and unused; R3 and R4 are
consumed and immutable. The next substantive candidate is TreasureBench
Agents v1 wholly fresh sealed repair-confirmation pilot registration. It
was subsequently registered and executed as AO-0006 using wholly new v2
private identities; its terminal quarantine is recorded below.

## Agents v1 fresh repair-confirmation v2 closeout

Issue #200 and PR #201 own AO-0006 campaign
`treasurebench-agents-v1-repair-confirmation-v2`, batch
`tb-agents-v1-repair-confirmation-v2-b01`, and frozen execution commit
`d210b0653677859c79a1fb87d871aaf45f4a81d4`. Both direct-provider public
canaries passed. They used 1,349 input tokens and 253 output tokens and cost
USD 0.0076095: OpenAI USD 0.0027975 and Anthropic USD 0.004812.

The batch then stopped at custody creation with decision
`fresh-pilot-v2-quarantined-engineering-only` and public-safe failure class
`custody-creation-failure`. No private architecture/model run occurred. The
provider phase is closed and eight safely lockable objects are preserved under
output lock
`sha256:127a9c796459c7627f6fd90b92ef1587ad0f6b1910b4ff255c2ceb976f3ab25f`;
no call followed the lock and no material was unsealed.

A new OS-CSPRNG seed and task and answer keys exist only in retained private
state. No task ciphertext, answer ciphertext, or custody manifest was
created. Methods A, B, and C, metric-range checks, and private pairing
verification were not run because the private batch never began. The
50-task/500-run rehearsal and 69 corruption rejections remain offline
instrument validation only.

No private content, performance comparison, ranking, scientific evidence, or
base-campaign authority is created. The v2 campaign and batch are permanently
quarantined and cannot be retried, repaired, reopened, reused, rescored,
spliced, executed, or reauthorized.

## AO-0007 custody diagnosis and prospective repair

Issue #202 and PR #203 implement the separately authorized AO-0007 engineering
follow-up. Its one-use diagnostic verified the AO-0006 output lock, exact
inventory, eight locked objects, identity, append-only logs, stage state,
redacted summary, and before/after state equality. It read no secret value,
task, answer, raw provider output, credential, private host path, or unrelated
object, and permanently closed private access after the invocation.

The exact cause was the v2 campaign's absence from the fail-closed private-task
generation permit allowlist. The repair is prospective only: it admits the
already frozen v2 campaign, adds atomic exclusive creation for new custody
objects, and requires resumed ciphertext to decrypt to the requested
plaintext. The production-path synthetic conformance passes all twenty
registered custody classes, an independent AES-256-GCM verifier, and six
negative classes with deterministic cleanup.

AO-0006 remains permanently quarantined and unchanged. This is engineering
diagnosis and offline conformance, not scientific or model-performance
evidence. No new pilot or v3 identity is registered.

## AO-0008 wholly fresh repair-confirmation v3 closeout

Issue #204 and PR #205 own campaign
`treasurebench-agents-v1-repair-confirmation-v3`, batch
`tb-agents-v1-repair-confirmation-v3-b01`, and frozen execution commit
`0f9d82bb50cbb334bea47e24448831faf0cdbed8`. Both public canaries, wholly
fresh custody, and the private prefix passed.

The fixed full batch then stopped under public-safe class
`fixed-full-batch-failure`, producing decision
`fresh-pilot-v3-quarantined-engineering-only`. The provider phase made 3,067
calls, used 2,304,303 input tokens and 444,085 output tokens, and cost USD
13.1861145: OpenAI USD 4.5952575 and Anthropic USD 8.590857. Every hard cap
held.

Provider access is closed. The output lock covers 3,576 retained objects under
`sha256:e52055b08ca3a8acb1cfb6ac608c6e601f3c618352900f92bf91c5ffc4718dbb`.
No call followed the lock and no material was unsealed. The partial private
batch is not evaluated or published. Methods A/B/C, task-level metrics,
pairings, comparisons, and rankings were not produced after quarantine.

The complete public rehearsal still has 50 synthetic tasks, 500 pairings,
3,014 matrix turns, and 71 registered corruption rejections. It remains
engineering instrumentation only. No private content, claim, scientific run,
paper result, comparison, release, submission, or base-campaign authority is
created. The v3 campaign and batch are permanently quarantined and cannot be
retried, repaired, reopened, reused, rescored, spliced, executed, or
reauthorized.

## AO-0009 aggregate fixed-batch diagnosis

Issue #206 and PR #207 implement one exactly owner-gated, one-use R2
engineering diagnostic of the immutable AO-0008 retained state. It verified
the 3,576-object output lock, inventory, append-only ledgers, complete
3,067-response identity correspondence, unique 2/50/450 trace partition, and
all 500 private pairing records. All 450 fixed-full-batch traces
authenticated. Retained state was not mutated, the operational key was not
retained, and private-read authority is permanently closed.

The allowed aggregate reports 32 protocol-nonconforming traces and 32
parse/schema-repair exhaustion traces. Terminal-provider attempts,
contamination traces, invalid final-cardinality traces, cap-guard triggers,
and integrity failures are zero. Under the frozen runner's post-loop
precedence this selects `agent-protocol-policy-decision-required`.

AO-0009 makes no silent normalization, semantic retry, invalid-output credit,
protocol acceptance, or scoring change. Any such prospective change requires
a separate explicit owner decision and task. This redacted engineering
diagnosis creates no performance result, comparison, ranking, scientific run,
claim, paper result, release, submission, or base-campaign authority. AO-0008
remains permanently quarantined; at AO-0009 closeout, v4 was not registered.

## AO-0010 protocol-validity policy v2 and fresh v4 closeout

Issue #208 and draft PR #209 adopt a forward-only, versioned
protocol-validity policy v2 and prepare one wholly fresh v4 engineering
campaign, `treasurebench-agents-v1-repair-confirmation-v4`, with batch
`tb-agents-v1-repair-confirmation-v4-b01`. Historical policies, schemas,
campaigns, locks, and decisions are unchanged.

Policy v2 separates batch integrity, missing provider terminals,
protocol-valid outputs, and protocol-invalid outputs. A completed provider
response that remains nonconforming after the one registered schema-only
repair is preserved as protocol-invalid evaluated-system behavior. It remains
in every intended-pairing denominator, receives no replacement, semantic
retry, invented action, or invalid-output credit, and does not alone
quarantine the batch. Exact metrics are computed only where defined; registered
metric-specific feasible bounds and architecture-contrast bounds cover all
intended pairings. Valid-output-conditional diagnostics remain explicitly
secondary and selection-conditioned.

Authorization-free validation passes the complete 50-task/500-pairing
rehearsal, zero/mixed/all-invalid scenarios, first/middle/final invalid
positions, Methods A/B/C, 6,400 pairing-level metric intervals, 120 contrast
bounds, independent reconstruction, 104 relevant corruption rejections,
production custody/lock/unseal/redaction/cleanup rehearsals, 62 focused tests,
and the full 725-test repository wall. Protocol-invalid traces alone do not
quarantine; terminal-provider and integrity failures still do.

The policy was frozen before v4 authorization and generation. Execution was
frozen at `5289882dca6b8912a0518bba72aba1f4d595c2a8`; the exact generic owner
gate and current official provider re-audit passed. Both public canaries and
wholly fresh custody then passed. The private prefix stopped on
`provider-terminal-missing`, closing provider access after 116 calls, 58,636
input tokens, 13,275 output tokens, and USD 0.3470610. The verified output
lock covers 150 retained objects under
`sha256:88c442bf6cb5e1b99a893808d423b488d2b1062543a49fcfb32b77f276abaa1c`.
No call followed the lock and no material was unsealed.

The incomplete real batch has no protocol classification, Methods A/B/C,
metric bounds, or performance interpretation. No replacement, splice,
semantic retry, invalid credit, ranking, scientific evidence, or base-campaign
authority exists. V4 and every prior campaign are permanently closed and
immutable.

## AO-0011 provider-outcome policy v3 and wholly fresh v5 closeout

Issue #210 registers one forward-only provider-outcome policy v3 and one
wholly fresh engineering campaign,
`treasurebench-agents-v1-repair-confirmation-v5`, batch
`tb-agents-v1-repair-confirmation-v5-b01`. AO-0010 and the intentionally
coarse v4 quarantine remain permanent; no retrospective v4 diagnosis,
reclassification, private read, unseal, or inference is performed.

Policy v3 separates completed protocol-valid and protocol-invalid responses
from prospectively typed provider-operational missingness and immediate
provider-contract/safety quarantine. Operationally missing pairings preserve
safe prior turns, receive no action or replacement, remain in every intended
denominator, and use metric-specific feasible intervals plus exact operational
metrics. Independent provider classification and independent all-pairing
contrast reconstruction are required.

The sequence-only engineering circuit breaker is frozen at three consecutive
same-provider operationally missing pairings or ten cumulative missing
pairings, with immediate quarantine for any contract/safety failure or
non-valid public canary. There is no scientific missingness threshold and no
rerun-until-availability rule.

The owner-directed R2 correction prospectively supersedes the unused original
gate and adds one deterministic, restart-safe delay before the sole permitted
second identical-request transport attempt. A safely parsed Retry-After value
is clamped to one through 30 seconds; otherwise the frozen class fallback is
two seconds for timeout, transient transport, or invalid provider JSON and
five seconds for rate limit, transient provider, overload, or service error.
There is no jitter, third attempt, semantic retry, outcome-dependent retry,
replacement, or wait after authorization, identity, cap, phase-closure,
retained-state, route, model, contract, or safety failure. Only normalized
retry delay, source, class, and attempt may enter operational records.

Authorization-free validation passed a complete 50-task/500-pairing
rehearsal, 7,900 metric intervals, 144 all-pairing contrast bounds,
zero/mixed/all-invalid and missingness scenarios, 115 v5 boundary corruptions,
28 inherited repaired-instrument corruptions, and disposable
production-path custody, lock, replay, redaction, and cleanup rehearsals.

The exact R2 authorization then completed both public canaries, wholly fresh
50-task custody, the private prefix, and all 500 pairings. Terminal
classification contains 496 protocol-valid and four protocol-invalid
pairings, zero provider-operational missingness, zero contract/safety failure,
and no circuit breaker. One transient-provider first attempt used the frozen
five-second fallback and recovered on the sole identical retry.

Provider access closed after 3,058 calls and USD 13.0413660. The verified
4,067-object output lock is
`sha256:e18e7f8173f9ac0026f74cd6ff9b577010abdf65620ad269606f6862ff16e47b`.
Post-lock replay/unseal, Methods A/B/C, independent classification and bounds,
identity, cost, contamination, corruptions, redaction, and retained-state
checks pass. This remains aggregate DD-010 engineering only and publishes no
task-level or comparative performance.

## Registered evaluation campaign

Issue #173 registers, but does not authorize or execute, the evaluation
campaign. The selected next tier is a 50-task sealed engineering pilot using
two exact cloud snapshots, one repeat, all five architectures, and exact
comparators. It is non-inferential. The future 200-task base allocation covers
all 138 generator cells plus 62 boundary-priority repeats, but base execution
is blocked because the audited 16-GB host is ineligible for the exact
local/open candidate.

Issue #187 completed the separate sealed-pilot gate. Its Phase A contracts,
secure runtime, output-lock and independent-verification path, 50-slot
allocation, command surfaces, and corruption boundaries preceded an exact
owner-authorized provider phase. The resulting 500-run engineering pilot is
retained encrypted and permanently quarantined; its public closeout contains
operational totals only and no task-level or comparative performance.

No DD-023, claim, scientific run, paper result, ranking, leaderboard, or
composite exists. No completed or archived authorization permits the base
campaign, reuse of any quarantined pilot, or a new private pilot.


### AO-0012 R2 preauthorization correction

The unused R1 gate is superseded without authorization. The same public
calibration and runtime identity remain behind
`AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R2`, which adds repository-local
two-name credential ingress, temporary RunPod Secret/template lifecycle,
authorization-bound orphan controls, measured attestation, and exact
success/failure teardown and billing. This remains infrastructure engineering
only and adds no DD-023, private, scientific, base-campaign, performance, or
publication authority.

### AO-0012 R5 generic-gate compatibility repair

R4 was authorized and consumed by a legitimate hard stop before credential
ingress because its task validator read a nonexistent owner-gate `budget`
mapping. R5 may never reuse that authorization and changes only the prospective
adapter to require exact canonical `cumulative_state`, `hard_caps`, and
`remaining_caps`. The runtime, public calibration, caps, lifecycle, and
zero-scientific boundary remain unchanged; only a later exact R5 authorization
can permit live work.
