# DD-001 execution plan

## Completed initial phase

1. Froze the finite zero-communication common-payoff model and randomized-policy scope.
2. Derived an exact conditional-failure evaluator and implemented an independent target/signal enumerator.
3. Reduced exhaustive search by agent permutation and audited every configured profile count.
4. Certified a 21-point tiny grid through \(M=4,N=2\) and \(M=3,N=3\).
5. Executed 18 canonical coordinate-ascent starts within a 120-second guardrail and preserved exact policies, seeds, terminations, and bounds.
6. Generated the phase CSV/SVG, proof records, claim checks, report, and working paper draft.

## Next executable phase

- Execute `signature-certificate.yml` from a clean commit after the reference matching checker, reduced Hall checker, reconstruction tests, integer evaluator, and corruption-detecting certificate verifier pass.
- The pre-run cost audit contains 79,745 signature profiles and 181,499 raw policy multisets across all configured accuracies, with a 120-second budget and no retained search frontier. This bounded audit is expected to complete in well under the budget based on the prior 21-case run.
- The analytic pre-run canonical count is 148,348,284,928 feasible labeled signatures and an 85-digit agent-multiset count before target quotienting. Even a minimal 16-component 64-bit failure vector per state would require more than $7\times10^{86}$ bytes. The run must verify these counts before any bound method is selected.
- Treat the 5,806 individual-signature target orbits only as a measurement: independently canonicalizing every agent loses relative target alignment and is not a proved profile reduction.
- Do not launch canonical enumeration. Record the verified reduction and state-space barrier unless a further admissible bound with a simpler certificate is proved within the milestone.
- Derive analytic threshold regions for the constant-plus-signal hybrid observed at \(N=2\) after the signature milestone merges.
- Expand canonical lower-bound search beyond coordinate fixed points only after adding checkpoint/resume support.
- Keep communication budgets deferred until the zero-communication frontier has stronger bounds.

## Guardrails

No heuristic value is labeled optimal. Every added exhaustive case must record its reduced profile count before execution. New dependencies require an ADR. Long searches need time/memory budgets and checkpoints; failed bounds and searches remain in the record. The DD-001A state-space figures above are pre-run deterministic cost estimates, not a new canonical optimum claim.
