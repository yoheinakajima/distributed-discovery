# Independent internal proof audit

Audit date: `2026-07-22`. This review restarts from the frozen model and checks
the proof obligations without treating the census as proof.

## Audit result

The aggregation–rescue identity, the `N=2` identity, and the point-channel
monotonicity proof are internally consistent within the declared assumptions.
The general theorem is not validly exported to the five arbitrary DD-019
channels, and the proof record correctly keeps that comparison bounded.

## Obligation checks

1. **Factorization.** After conditioning on the target, the block uses signals
   disjoint from those of remaining private actors. This justifies multiplying
   failure probabilities. Target symmetry is needed before using scalar `C_s`.
2. **One-step MAP containment.** For `p>1/M`, posterior rank is signal-count
   rank. Adding nomination `x` changes only `x`'s count, so `{old MAP,x}`
   contains a new maximizer for every history and every old uniform tie draw.
3. **Protocol value.** The old MAP failure and the new direct-action success
   are conditionally independent given the target. Their union has value
   `C_s+p(1-C_s)`; this is not an assumption about pooled accuracy.
4. **Strictness.** The all-same-wrong then correct history has positive mass for
   `p in (1/M,1)`. The pre-sharing pair succeeds and the post-sharing singleton
   has positive failure. The residual private-failure multiplier is positive.
5. **Boundaries.** `p=1` gives equality. At `p=1/M`, posterior count ranking is
   invalid because signals are uninformative; the separate independent-uniform
   tie calculation gives strict decline. The proof does not cross below
   `p=1/M`.
6. **Two-agent case.** Exchangeability plus symmetric tie-breaking gives
   `C_2=p`, including the uninformative boundary. Substitution yields the stated
   difference exactly.
7. **Scope.** The argument orders only the named protocol. It proves neither
   action-assignment optimality nor arbitrary-channel monotonicity.

## Computational cross-check role

The two exact census methods, endpoint tests, corruption gates, and DD-019
extension are allowed to detect implementation or transcription errors. They
are not cited as the reason Theorem 3 is true.

