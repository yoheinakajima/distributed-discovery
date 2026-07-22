# Analytic proof record

This record concerns only the model in `model.md`. It does not establish a
private-team optimum or a result for arbitrary channels.

## Definitions

Fix a target `T`. In a block of `s` conditionally independent symmetric point
signals, let `A_s` be the uniformly tie-broken posterior-MAP action and let

`C_s = P(A_s=T)`.

Let the other `N-s` agents take their direct private actions. Their conditional
accuracy is `p`, and their signals are independent of the block conditional on
`T`. Write `G_s` for the probability that the block action or at least one
remaining private action equals `T`.

## Proposition 1 — aggregation–rescue identity

For every registered `M,N,p,s`,

`G_s = 1 - (1-C_s)(1-p)^(N-s)`.

**Proof.** Conditional on `T`, group failure is the intersection of block
failure and failure of all `N-s` remaining direct actions. These events depend
on disjoint conditionally independent signals. Symmetry makes the block
failure probability `1-C_s` for every target, and each direct failure has
probability `1-p`. Multiplication and complementation give the identity. ∎

Subtracting adjacent terms gives the exact diagnostic

`G_(s+1)-G_s = (1-p)^(N-s-1) [C_(s+1)-C_s-p(1-C_s)]`.

Thus pooled accuracy may rise while discovery falls: the required marginal
pooled gain is `p(1-C_s)`, exactly the rescue probability contributed by the
new signal's direct action when the old block is wrong.

## Proposition 2 — the two-agent boundary

For every finite `M>=2` and `p in [1/M,1]`, `C_2=p`. Consequently

`G_1=1-(1-p)^2`, `G_2=p`, and `G_2-G_1=-p(1-p)`.

Equality holds only at `p=1`; otherwise the loss is strict, including at the
uninformative boundary under the declared independent uniform tie rule.

**Proof.** If two signals agree, their common value is MAP. If they differ,
their two nominated targets tie for MAP (at `p=1/M`, all targets tie) and the
declared rule is symmetric. The two signals are exchangeable, so the expected
correctness of the selected action equals the correctness of either signal,
namely `p`. Proposition 1 supplies the remaining formulas. ∎

## Theorem 3 — point-channel monotonicity

For every finite `M>=2`, `N>=2`, `p in [1/M,1]`, and `s=1,...,N-1`,

`G_(s+1) <= G_s`.

The inequality is strict for `p<1` and is equality for `p=1`.

**Proof for `p>1/M`.** Condition on the first `s` signals and let `a` be the old MAP action
after the declared independent uniform tie-break. Let `x` be the next signal.
After adding `x`, every target other than `x` retains its old count, while
`x` gains one. Therefore at least one posterior maximizer after `s+1` signals
lies in the two-action set `{a,x}`: if `x` is not a new maximizer, every old
maximizer remains a new maximizer; if it is, `x` itself is present. For every
realized history, the posterior probability covered by `{a,x}` is consequently
at least the posterior probability of the single new MAP action.

Before sharing `x`, the protocol comprising old block action `a` plus the new
direct action `x` succeeds with probability
`C_s+p(1-C_s)`. Replacing those two actions by one new pooled MAP action has
accuracy `C_(s+1)`, so

`C_(s+1) <= C_s+p(1-C_s)`.

Insert this inequality in the adjacent diagnostic above to obtain
`G_(s+1)<=G_s`.

For strictness when `p<1`, the event that the first `s` signals all nominate
one wrong target `w` and the new signal nominates the true target has positive
probability. The old block plus direct action succeeds on that event. After
pooling, for `s>=2`, `w` remains the unique MAP and the new single action fails;
for `s=1`, the true and wrong targets tie and the independent tie-break has
positive failure probability. Hence the expectation loses positive mass.
When `p=1`, every action is correct and all `G_s=1`.

At the remaining boundary `p=1/M`, signals carry no information. Every pooled
action and every direct action is an independent uniform MAP draw, so
`C_s=1/M` and `G_s=1-(1-1/M)^(N-s+1)`. This is strictly decreasing in `s`.
Together the cases prove the theorem. ∎

## DD-019 extension boundary

For a target-symmetric DD-019 channel with constant conditional direct-action
accuracy `q`, the same conditional-independence argument gives

`G_s(W)=1-(1-C_s(W))(1-q)^(N-s)`.

The point-channel monotonicity proof does **not** extend merely from equal
one-person accuracy: an arbitrary signal can change posterior rankings in ways
not represented by `{old MAP, new direct action}`. The five-channel extension
is therefore a bounded exact comparison, not a general theorem.

## Independent proof audit checklist

- The identity conditions on the target before multiplying failures.
- Uniform priors and target symmetry are used to replace target-specific
  quantities by scalar `C_s` and `p`.
- The point-channel ranking step uses `p>=1/M`; outside it, a signal's nominated
  point need not be the private Bayes action.
- Tie randomization is independent and uniform; no favorable coupled tie is
  smuggled into the strictness argument.
- The theorem compares only adjacent protocols and telescopes to the complete
  ordering; it asserts neither team optimality nor arbitrary-channel order.
- The strict-event argument applies for `p in (1/M,1)`; the uninformative
  boundary is handled separately through independent uniform MAP draws.
