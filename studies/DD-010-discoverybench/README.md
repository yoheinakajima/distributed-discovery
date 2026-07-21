# DD-010 — DiscoveryBench

DiscoveryBench is a static, auditable benchmark for how declared multi-agent
protocols convert evidence into search actions. It contains exact golden
fixtures tied to existing project claims and runs plus a small seeded synthetic
sensitivity suite. It is not a hosted leaderboard or a universal measure of
real-world agent quality.

Run `make dd010-discoverybench` only from a clean committed implementation to
create the immutable primary run. Use `distributed-discovery benchmark --help`
for read-only registry and evaluator commands.
