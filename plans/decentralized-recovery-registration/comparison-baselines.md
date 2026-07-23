# Comparison baselines and outcomes

## Centralized comparator

At public posterior `mu`, `V_2^(2)(mu)` is the mass of a posterior top-two set,
`a+b=1-c`. The planner has binding authority to assign distinct target actions.
This is an upper comparator, not decentralized implementation. At channel
level, `V_2^(2)(W)` averages this pointwise value over positive-probability
pooled signal profiles.

## Direct-private comparator

`P_2(W)` is exactly DD-021's declared direct-private discovery baseline. Each
agent applies the channel's target-equivariant direct action correspondence to
their own signal, with independent uniform draws over ties. It is not asserted
to be the private-team optimum or an equilibrium of either shared game.

Conditional on a pooled signal pair, the comparison reconstructs the direct
action union and its posterior mass, averaging only over declared private tie
draws. Averaging those conditional values recovers `P_2(W)`.

## Equilibrium outcomes

For action pair `(i,j)`, discovery is `mu_i` if `i=j` and `mu_i+mu_j` if
`i!=j`. Payoffs are `(mu_i/2,mu_i/2)` on a collision and `(mu_i,mu_j)` on a
split.

For each game form define the complete pure equilibrium set, discovery and
payoff of every equilibrium, best and worst discovery, discovery spread,
every-equilibrium top-two recovery, centralized gaps, and conditional/private
gaps. Channel averages preserve best and worst pointwise selection separately.
Gaps are used; no ratio is retained.
