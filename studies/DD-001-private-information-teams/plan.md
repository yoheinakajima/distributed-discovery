# DD-001 execution plan

## Completed initial phase

1. Froze the finite zero-communication common-payoff model and randomized-policy scope.
2. Derived an exact conditional-failure evaluator and implemented an independent target/signal enumerator.
3. Reduced exhaustive search by agent permutation and audited every configured profile count.
4. Certified a 21-point tiny grid through \(M=4,N=2\) and \(M=3,N=3\).
5. Executed 18 canonical coordinate-ascent starts within a 120-second guardrail and preserved exact policies, seeds, terminations, and bounds.
6. Generated the phase CSV/SVG, proof records, claim checks, report, and working paper draft.

## Completed DD-001A phase

- Primary immutable run `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5` completed in 13.73 seconds under the 120-second budget.
- Reference matching, reduced Hall feasibility, constructive reconstruction, exact integer evaluation, and corruption-detecting certificate checks all passed.
- The signature run independently reproduced all 21 exact-grid optima and raw-policy tie counts.
- The canonical audit certified 148,348,284,928 feasible labeled signatures, 5,806 individual target orbits, and an 85-digit eight-agent multiset count before a global target quotient.
- Independently canonicalizing every agent remains invalid because it loses relative target alignment. No canonical enumeration or objective-certificate claim was made.

## Next executable phase

- Derive exact threshold regions for the constant-plus-signal hybrid observed at \(N=2\).
- Reproduce the derived regions by exhaustive exact enumeration over a declared finite grid and test equality boundaries explicitly.
- Expand canonical lower-bound search beyond coordinate fixed points only after adding checkpoint/resume support.
- Keep communication budgets deferred until the zero-communication frontier has stronger bounds.

## Guardrails

No heuristic value is labeled optimal. Every added exhaustive case must record its reduced profile count before execution. New dependencies require an ADR. Long searches need time/memory budgets and checkpoints; failed bounds and searches remain in the record. The DD-001A state-space figures are verified exact counts, not a canonical optimum claim.
