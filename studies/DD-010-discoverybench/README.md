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
