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

## Registered Agents v1 instrument layer

DiscoveryBench Agents v1 is registered under DD-010 as an offline instrument,
not as benchmark content v4 and not as a new study. It may explicitly select
unchanged v1, v2, or v3 content while independently freezing agent protocol
`agents-v1` and generator `agents-task-generator-v1`.

The registration defines five finite task families, five agent architecture
contrasts plus exact comparators, separate metrics with no composite, sealed
custody, contamination probes, safe visible traces, and independent
verification. Its status is `registered-not-executed`: no model call, model
download, private seed, holdout, answer key, trace, evaluation result, cost,
claim, or run exists.

Future implementation requires its own issue, branch, exact snapshot gate,
explicit owner cost authorization, and evidence package. The current v1/v2/v3
commands, outputs, default, and disabled external adapter remain unchanged.
