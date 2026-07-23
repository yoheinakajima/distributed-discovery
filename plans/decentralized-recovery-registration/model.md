# Frozen candidate model

Nature draws one target from three under a finite rational prior. Two agents
receive signals under one immutable DD-021 `M=3,N=2` channel law. The signals
are pooled and produce a public rational posterior `mu` over the targets.

Each identity-aware agent chooses one reliable atomic target action. If `n_j`
agents choose the true target `j`, each receives `1/n_j`; otherwise payoff is
zero. Expected payoff at the public posterior is `mu_j/n_j`. Discovery is the
posterior mass of the union of selected targets.

## Simultaneous form

Actions are chosen simultaneously and contemporaneous choices are hidden.
There is no assignment, role label beyond identity, transfer, correlated
recommendation, public seed, or post-disclosure message. The complete labeled
pure-Nash correspondence is in scope.

## Sequential visible-occupancy form

Agent 1 moves after observing the public posterior. Agent 2 observes Agent 1's
action and then chooses. The order is fixed and public. No other primitive is
added. The complete pure subgame-perfect correspondence, including off-path
continuations, is in scope.

## Conventions

- Posterior masses may tie or be zero and sum exactly to one.
- A canonical ordering writes `a>=b>=c`, but labeled targets and every
  permutation are retained in the primitive method.
- Weak best-response inequalities define equilibrium. Every indifferent
  action remains in the correspondence.
- A centralized top-two set is any two-target set attaining mass `a+b`; ties
  produce a correspondence.
- Pointwise posterior objects and channel averages are never conflated.

Mixed equilibrium, refinements beyond pure SPE, learning, public
randomization, messages, licenses, markets, transfers, reliability, overlap,
threshold teams, multiple valuable targets, evidence acquisition, missing
provenance, `M>3`, `N>2`, and human or real data are excluded.
