# Exact canonical pooled-frontier execution plan

1. Freeze `configs/exact-frontier.yml` and the model above.
2. Bound Method A at 490,314 states and the complete run at 30 seconds; use no
   randomness or solver.
3. Implement and unit-test labeled-count, histogram/orbit, and independent
   partition representations, including a tiny direct-enumeration fixture.
4. Commit implementation and configuration so the primary run begins from a
   clean Git state.
5. Execute `make canonical-exact-frontier` once as the primary immutable run.
6. Require exact agreement for budgets one through eight, exact unit mass in both
   primary methods, the configured endpoint and recovery budget, independent
   verifier acceptance, corruption rejection, and elapsed time below budget.
7. Audit DD-C-0006, DD-C-0008, and DD-C-0019 before updating claims or reports.
8. Preserve the distinction between a pooled upper certificate and an attainable
   private-team policy.

The pre-run cost probe used the same declared dimensions but was not retained as
claim evidence: Method A completed in roughly 1.3 seconds and Method B enumerated
67 histogram states in roughly one millisecond on the development host. The
30-second limit leaves substantial validation overhead while remaining bounded.
