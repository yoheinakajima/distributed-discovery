# DD-001 execution plan

## Completed initial phase

1. Froze the finite zero-communication common-payoff model and randomized-policy scope.
2. Derived an exact conditional-failure evaluator and implemented an independent target/signal enumerator.
3. Reduced exhaustive search by agent permutation and audited every configured profile count.
4. Certified a 21-point tiny grid through \(M=4,N=2\) and \(M=3,N=3\).
5. Executed 18 canonical coordinate-ascent starts within a 120-second guardrail and preserved exact policies, seeds, terminations, and bounds.
6. Generated the phase CSV/SVG, proof records, claim checks, report, and working paper draft.

## Next executable phase

- Prove the policy-signature objective reduction, decide signature feasibility exactly, reconstruct raw policies, and validate losslessness on the 21-point grid.
- Measure the canonical signature state space before selecting a certified upper-bound method; do not add arbitrary coordinate-ascent restarts.
- Attempt a bounded canonical certificate only after every reduction and pruning rule passes tiny exhaustive checks.
- Derive analytic threshold regions for the constant-plus-signal hybrid observed at \(N=2\) after the signature milestone merges.
- Expand canonical lower-bound search beyond coordinate fixed points only after adding checkpoint/resume support.
- Keep communication budgets deferred until the zero-communication frontier has stronger bounds.

## Guardrails

No heuristic value is labeled optimal. Every added exhaustive case must record its reduced profile count before execution. New dependencies require an ADR. Long searches need time/memory budgets and checkpoints; failed bounds and searches remain in the record.
