# DD-022 exact report

Primary run `20260722T210334Z_DD-022_2376d5b7_ad67765ca8` passed from clean
source commit `2376d5b7` in 0.297666 seconds with 21.719 MB peak memory. Exact
closed forms and direct target/signal/action/deviation enumeration agree in all
42 registered cells, and all ten corruption gates pass.

## Selected equilibrium theorem

Let `t=2p-1` and `A=t^2+rho(1-t^2)`. In the anonymous label-equivariant private
class, the symmetric Bayes–Nash equilibrium follows the signal with probability
one when `A<=3t`, and otherwise with probability `1/2+3t/(2A)`.

After public disclosure, agreement has posterior `u=1/2+t/(1+A)`. In the
selected posterior-only, provenance-blind identical-mixing game, both agents
choose the favored target with probability one for `u>=2/3`, and with
probability `3u-1` otherwise. Disagreement selects independent half mixing.

At `p=3/5`, selected shared discovery exceeds private-equilibrium discovery
exactly for `rho in ((5 sqrt(73)-17)/48, 1)`. The root is approximately
`0.5358337235`; exact signs are certified between `2679/5000` and `67/125`.
The private regime changes at `7/12`, and shared agreement at `1/6`. Ex-post
budget balance makes total payoff equal discovery, so each symmetric agent
receives half and improves on the same interval.

## Baselines and bounded extension

Direct private clue-following has discovery `(21-6rho)/25` on the canonical
slice. The selected private equilibrium may anti-crowd above `7/12`, so the
positive theorem compares equilibrium with equilibrium. The 42-cell grid
contains six positive, 18 negative, and 18 neutral selected comparisons.

The centralized top-two value is one. Selected shared discovery remains below
it by `(7+3rho)/25` through `rho=1/6` and by
`(4+3rho)/(13+12rho)` above that boundary.

## Selection dependence and negative result

The theorem is not robust to every equilibrium. Opposite constant-target
private pure equilibria exist for every canonical `rho` and discover surely.
When public signals disagree, agents remember signal ownership; “follow my own”
and “oppose my own” are symmetric split equilibria. The selected shared result
therefore requires posterior-only, provenance-blind identical mixing.

Sharing reveals agreement or disagreement and updates beliefs about the latent
source branch. Agreement does not reveal the realized dependence branch, and
sharing neither creates independence nor assigns roles.

## Evidence boundary

No human or real data are used. Counts are exhaustive only for the registered
rational grid. The strict theorem is exact only for `p=3/5` under the frozen
source law and declared selections. The centralized value remains an authority
benchmark, not an implementation claim.
