# Decentralized Recovery formal reduction

Date searched: `2026-07-22` (America/Los_Angeles)  
Evidence class: exploratory registration analysis, not a theorem, proof-status
promotion, run, claim, novelty assertion, or systematic review.

## Exact singleton-resource mapping

Fix a public posterior `mu=(mu_1,mu_2,mu_3)`. The two agents are players, the
three targets are singleton resources, an action selects one resource, and
`n_j` is its occupancy. Equal sharing gives

`u_i(j,n)=mu_j/n_j`.

Group discovery is `sum_j mu_j 1{n_j>0}`. This is an ordinary singleton
congestion/resource-selection game with common resource values and decreasing
occupancy payoff. Player-specific values are not needed. It has exact
Rosenthal potential

`Phi(n)=sum_j mu_j H_(n_j)`,

where `H_0=0`, `H_1=1`, and `H_2=3/2`. Hence a distinct pair `(j,k)` has
potential `mu_j+mu_k`, while a collision on `j` has `3mu_j/2`. Pure-equilibrium
existence and finite improvement are classical content, not eligible results.

Rosenthal's original paper defines factor costs as occupancy functions and
constructs the cumulative potential minimization that yields a pure Nash
equilibrium (DOI `10.1007/BF01737559`). Monderer and Shapley define and
characterize potential games (DOI `10.1006/game.1996.0044`). Milchtaich's
player-specific singleton extension proves pure-equilibrium existence even
without a general potential and warns that arbitrary best-reply paths can
cycle (DOI `10.1006/game.1996.0027`); that extension is broader than needed
here.

## Complete simultaneous reduction

For a labeled pair `(i,j)` with `i!=j`, pure Nash requires

`mu_i >= max(mu_j/2, max_(k notin {i,j}) mu_k)`

and the symmetric inequality for `j`. A collision `(j,j)` is Nash exactly when

`mu_j/2 >= max_(k!=j) mu_k`.

These conditions are simply all unilateral deviations in the singleton game.
For a generic strict order `a>b>c`, top-two split is the only pure outcome when
`b>a/2`; top collision is also available at equality; and top collision is the
only pure outcome when `b<a/2`. Target ties are handled by the labeled
inequalities, not by a separate theorem.

## Sequential reduction

Fixed arrival with visible prior occupancy is a finite perfect-information
extensive-form game. After first action `j`, Agent 2's best-response
correspondence is

`BR_2(j)=argmax({mu_j/2} union {mu_k:k!=j})`.

If continuation `beta(j)` joins `j`, Agent 1 receives `mu_j/2`; otherwise Agent
1 receives `mu_j`. A pure SPE is exactly a nodewise best-response map `beta`
and a first action maximizing this continuation payoff. This is ordinary
backward induction. Selten's perfectness paper supplies the extensive-game
refinement boundary (DOI `10.1007/BF01766400`); no refinement beyond pure SPE
is used here.

For generic `a>b>c`, Agent 2 splits after a top first action exactly when
`b>a/2`. Starting on target two always induces Agent 2 to take target one, but
the first mover prefers that deviation only at the same equality boundary. As
a result, every pure SPE covers a top-two set exactly when `b>a/2`; at
`b=a/2` both a collision SPE and a split SPE remain. The sequential institution
does not enlarge the simultaneous every-equilibrium recovery region.

## Implementation distinction

The desired correspondence is coverage of a posterior top-two target set.
Existence of one desirable equilibrium, best-equilibrium attainment,
worst-equilibrium recovery, and every-equilibrium implementation are distinct.
Maskin's implementation definition requires both attainability of desired
outcomes and exclusion of undesired Nash outcomes (DOI
`10.1111/1467-937X.00076`). The equality and collision regions fail that
all-equilibria requirement even though desirable equilibria can exist.

## Multiple-searcher boundary

Korman and Rodeh study treasure in boxes with a known distribution, multiple
selfish parallel searchers, group success probability, congestion reward
policies including natural sharing `C(l)=1/l`, symmetric equilibria, price of
anarchy, and robustness (DOI `10.1016/j.jcss.2020.05.003`). Their main model is
multi-round and also discusses the one-round congestion/potential boundary.
Alpern and Gal provide the broader search-game framework (DOI
`10.1007/b100809`).

The frozen candidate differs by obtaining the box distribution as a pooled
posterior, naming DD-021's private baseline and centralized top-two comparator,
and adding visible sequential occupancy. But once the posterior is fixed, the
equilibrium characterization uses only resource values, occupancy, equal
sharing, and backward induction. Channel averaging is post-processing. A
one-round posterior-weighted restatement does not clear the gate.

## Common-information boundary

No common-information coordinator or decentralized-control reduction is used:
all private signals have already been pooled into one public posterior before
the action game. Adding Nayyar–Mahajan–Teneketzis would pad the map without
changing the formal reduction, so it is recorded as outside the frozen source
set.

## Candidate information-conditioned statement and failure

The strongest candidate was:

> For the frozen `M=3,N=2` game, characterize the public-posterior region in
> which every pure SPE under fixed sequential arrival and visible prior
> occupancy covers a centralized top-two set, characterize the complementary
> region and equality boundary, and average the pointwise classification over
> the inherited DD-021 channel slice against `P_2(W)` and `V_2^(2)(W)`.

The candidate is falsifiable and exactly checkable, but it does not survive the
non-overlap test. Its pointwise content is the classical best-response and
backward-induction calculation above; the public-posterior provenance, private
baseline, and channel average only label inputs and comparisons. The planned
registration decision is therefore `stop-classical-overlap`, subject to the
remaining state-space, verification, corruption, and repository gates.

## Search limitations

The search was targeted to the declared reduction and primary or authoritative
records. It is not a systematic review and makes no novelty or priority claim.
No learning, stochastic stability, correlation, assignment, transfer,
reliability, or common-information sources were added because the frozen model
does not use those concepts.
