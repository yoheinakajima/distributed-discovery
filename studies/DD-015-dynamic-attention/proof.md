# DD-015 analytic record

## Posterior filtering

Let `b(theta)` be the common posterior at a public history and let
`W_p(x|theta)` be the private-clue channel. An autonomous agent with clue `x`
has posterior proportional to `b(theta)W_p(x|theta)` and chooses its
lowest-label maximizer.

For a prescription `f(x)` and observed action `a`, the next fixed-budget common
posterior is proportional to

`b(theta) sum_{x:f(x)=a} W_p(x|theta)`.

Under stopping on success, reaching the next agent additionally establishes
`theta != a`, so the same expression is multiplied by `1{theta != a}` before
normalization. Action evidence and failure evidence are therefore distinct.

## Full-credit equilibrium proposition

In the registered autonomous game, agent `i` receives one if its own action is
the target and zero otherwise. Conditional on any reached information set, its
expected payoff from action `a` is exactly its posterior probability that
`theta=a`. Neither later actions nor duplicate actions change this payoff.
Choosing a posterior mode is therefore a best response at every reached
information set. Applying the lowest-label tie rule gives a pure sequential
Bayesian equilibrium of the declared finite game.

This proposition does not extend to equal-split, sole-rescue, marginal-credit,
or threshold-team rewards; those change the payoff from an action.

## Planner recursion

At each public state the planner chooses one of the `3^3=27` deterministic
private-clue prescriptions. Fixed-budget value averages the continuation value
over action-induced posterior branches and terminates at the posterior mass of
the searched set. Stopping value adds immediate hit mass and continues only on
the failure-conditioned branch. Backward induction over at most three stages is
exact and complete for this prescription class. The separately implemented
labeled enumerator sums every target, shared clue, and private-clue path to
check normalization and the resulting value.
