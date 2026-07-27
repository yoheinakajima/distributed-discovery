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

This is redacted DD-010 engineering status only. The next substantive
candidate is **TreasureBench exact provider-schema conformance repair and
public-canary gate**, a separately registered public-only diagnostic and tiny
canary gate. It creates no DD-023, claim, scientific run, paper result,
performance publication, or base-campaign authority.

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
campaign, reuse of either quarantined pilot, or a new private pilot.
