# DD-010 — DiscoveryBench

DiscoveryBench is a static, auditable benchmark for how declared multi-agent
protocols convert evidence into search actions. It contains exact golden
fixtures tied to existing project claims and runs plus a small seeded synthetic
sensitivity suite. It is not a hosted leaderboard or a universal measure of
real-world agent quality.

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

DiscoveryBench Agents v1 is registered under DD-010 as an offline instrument,
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

## Registered evaluation campaign

Issue #173 registers, but does not authorize or execute, the evaluation
campaign. The selected next tier is a 50-task sealed engineering pilot using
two exact cloud snapshots, one repeat, all five architectures, and exact
comparators. It is non-inferential. The future 200-task base allocation covers
all 138 generator cells plus 62 boundary-priority repeats, but base execution
is blocked because the audited 16-GB host is ineligible for the exact
local/open candidate.

No model call, invocation, download, cost, private material, trace, result,
claim, run, or DD-023 exists. Owner authorization remains pending.
