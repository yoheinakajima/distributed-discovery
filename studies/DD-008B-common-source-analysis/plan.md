# Plan

1. Derive exact gross discovery and type payoffs from the DD-008A model.
2. Express each common-to-independent deviation as a private threshold `A_k`.
3. Prove strict monotonicity of `A_k` by a Bernoulli coupling and a positive
   rational kernel; characterize all weak source-count equilibria.
4. Derive planner thresholds `B_k` and planner-optimal counts.
5. Prove the general all-common trap interval and its large-`N` width.
6. Test whether private acquisition is globally below planner acquisition;
   preserve an exact counterexample if it fails.
7. Check all formulas against the immutable DD-008A grid and a separate direct
   target/signal enumerator, then add corruption tests and an immutable run.

The executable audit is capped at ten minutes and 2 GB. Exact rational algebra,
not search, establishes the general result.
