# DD-017 report

Primary clean run `20260722T024032Z_DD-017_033452f6_3d2c74fdfb` passed in
8.234274 seconds, below the registered 60-second estimate and 300-second cap.
It records clean source commit `033452f6e2217f5e63bded87487bbc35bbd22eeb`,
configuration hash `3d2c74fdfb7ce0cd965373ae0da29545068d2adcf04c9e337be2dee456d77b14`,
the dependency lock, five input hashes, four output hashes, and no random seeds.

The pure-Nash occupancy condition is exact: every incumbent payoff must weakly
exceed the payoff from joining each alternative occupancy. A separate labeled
enumerator reproduces every equilibrium occupancy across 160 registered games,
3,728 occupancy states, and 87,216 labeled action profiles.

Fifty-two games have a pure equilibrium with zero discovery, hence infinite
pure price of anarchy under the registered positive-over-zero convention. This
is a bounded exact multiplicity result, not a general theorem that threshold
games always have inefficient equilibria.

Pairwise and exact-size-tau stability are separate strict-member concepts.
Eight registered games have no pairwise-strict-stable pure Nash equilibrium;
35 have no tau-player-strict-stable pure Nash equilibrium. The independent
audit rebuilds coalitions as removal/addition occupancies and solves an exact
payoff-compatible matching rather than replaying the labeled coalition loop.

Uniform independent mixing over tied posterior modes is always a symmetric
mixed equilibrium for `tau>=2`: support actions have equal positive payoffs,
while an unsupported candidate cannot form a viable team after one deviation.
At `tau=1`, an unsupported candidate opens alone, so the condition can fail.
Exactly 21 of the registered 40 threshold-one games fail; no higher-threshold
game fails. The fixture `(7/20,7/20,3/10)` at N=2 gives support payoff `21/80`
and outside payoff `3/10`.

All four corruptions—removed equilibrium, altered best discovery, altered pair
stability, and altered tied-mode classification—are rejected. DD-C-0075 and
DD-C-0076 are verified proof-backed claims. DD-C-0077 and DD-C-0078 are
independently reproduced bounded computations. No correlated, coalition-proof,
strong-equilibrium, stochastic-selection, or behavioral conclusion is made.
