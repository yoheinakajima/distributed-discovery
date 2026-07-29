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

## AO-0010 prospective protocol-validity policy v2 and fresh v4 preparation

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

The policy is frozen before any v4 authorization or generation. AO-0010 is
stopped at its owner-gate boundary: no credential, real private seed, task,
answer, key, ciphertext, provider call, spend, unseal, or scientific evidence
has been created or accessed. AO-0008 and every prior campaign remain
permanently closed and immutable.

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
