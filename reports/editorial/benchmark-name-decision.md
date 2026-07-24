# Benchmark public-name decision

Decision: **`owner-name-decision-required`**.

ActionPortfolioBench leads the deterministic score at 91, followed by
SearchPortfolioBench at 86. Although the leader clears the 85-point floor and
has no exact-name collision found, its five-point lead is below the required
eight points and the audit cannot remove scholarly or legal ambiguity.
Automatic selection therefore fails.

No rename is implemented. `DiscoveryBench` remains the historical/internal and
current repository display name so the tree is coherent, but it is blocked for
the first external benchmark scholarly artifact because of the fatal ICLR 2025
collision. DD-010, claims, runs, paths, schemas, routes, and CLI behavior are
unchanged.

The owner must select and clear an external public name, record it in
`benchmark-name-decision.yml`, and authorize a dedicated compatibility-
preserving rename. Until then, a partial rename or public release is
prohibited.
