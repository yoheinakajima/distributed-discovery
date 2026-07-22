# DD-017 proof record

## Pure Nash occupancy characterization

At occupancy n, an agent on candidate j receives

`u_j(n)=pi_j/n_j` if `n_j>=tau`, and zero otherwise.

If that agent alone changes to k, its new candidate has occupancy `n_k+1`, so
its deviation payoff is `pi_k/(n_k+1)` when `n_k+1>=tau`, and zero otherwise.
The departure's effect on j does not enter the deviator's payoff. Therefore n
is a weak pure Nash occupancy if and only if, for every occupied j and every
`k != j`, the current payoff is at least this deviation payoff. This condition
is both necessary and sufficient because these are exactly all pure unilateral
action changes.

## Tied-mode symmetric mixture

Let S be the set of posterior maximizers, let `m=|S|`, and let every agent mix
independently and uniformly on S. Every support action has the same posterior
mass and the same selection probability `1/m`, hence the same expected payoff.

For `tau>=2`, a candidate outside S has selection probability zero among all
other agents. A deviator to it faces zero partners and cannot reach the
threshold, so its payoff is zero. Every support action has strictly positive
probability of at least `tau-1` partners and strictly positive posterior mass,
so its payoff is positive. The uniform tied-mode mixture is therefore a
symmetric mixed Nash equilibrium for every finite positive posterior and every
`tau>=2`.

For `tau=1`, an outside candidate opens when the deviator chooses it and pays
its full posterior mass. A support action pays

`pi_max * [1-(1-1/m)^N]/(N/m)`.

Consequently the tied-mode mixture is a symmetric mixed equilibrium at
threshold one if and only if this support payoff is at least every outside
posterior mass. The condition can fail. For example, with N=2 and posterior
`(7/20,7/20,3/10)`, support payoff is `21/80`, strictly below the outside
payoff `3/10`.

These results verify one symmetric mixture. They do not characterize all mixed
equilibria or provide an equilibrium-selection process.

