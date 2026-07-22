# Frozen model boundary

Nature draws `theta` uniformly from `M` finite targets. `N` agents receive
conditionally independent draws from a declared finite target-symmetric
channel `W(s|theta)`. A target-equivariant direct rule `d(s)` has constant
target-conditional accuracy `q`; any set-valued direct correspondence uses an
independent uniform draw.

For `s=1,...,N`, the first `s` signals feed one uniformly tie-broken posterior
MAP action and the remaining `N-s` agents take direct actions. `G_s` is
one-hit group discovery and `C_s` is pooled MAP accuracy. `s=1` is the direct
private baseline, not a distinct zero-sharing state.

After all `N` signals are pooled, `V_L` is expected top-`L` posterior mass for
`L=1,...,min(N,M)` under centralized authority to choose distinct atomic
actions. `P_N` is discovery from `N` independent direct actions. `L*` is the
least registered `L` with `V_L>=P_N`.

The model has no rewards, equilibrium, post-protocol communication, threshold
technology, unreliable execution, or decentralized implementation claim for
the pooled planner.
