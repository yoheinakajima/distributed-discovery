# DD-021 exact report

Primary run `20260722T185924Z_DD-021_3cdbbc40_2fea269a9a` passed from clean
source commit `3cdbbc40` in 11.232478 seconds with 27.266 MB peak memory. It
evaluates 59 channel laws and 177 `(channel,N)` scenarios. Exact ordered-profile
enumeration and an independent histogram/count-state method agree on every
value and witness, and all eight registered corruptions are rejected.

## Analytic frontier

Let `e_s=1-C_s`. In the frozen finite, target-symmetric, conditionally
independent protocol,

`G_s = 1-e_s(1-q)^(N-s)`

and therefore

`G_(s+1)-G_s = (1-q)^(N-s-1)[(1-q)e_s-e_(s+1)]`.

Thus one more shared signal helps exactly when pooled error contracts faster
than the lost independent-rescue factor: `e_(s+1)<(1-q)e_s`. Equality is
neutral and the reversed inequality hurts. When `e_s>0`, this is equivalently
`rho_s=e_(s+1)/e_s < 1-q`. This descriptive “Independent-Rescue
Error-Contraction Criterion” is not asserted to be a novel theorem name.

The sign condition is tight: equality `e_(s+1)=(1-q)e_s` gives exactly zero
increment, while either strict side gives the corresponding strict sign. The
perfect-direct boundary `q=1` and zero pooled error are handled without dividing
by `e_s`; they do not require a ratio convention.

For centralized pooled top-`L` authority, `V_min(N,M)>=P_N`: conditional on
each signal profile, the posterior top-`min(N,M)` target set contains every
target and weakly dominates the posterior mass of any realized union of at
most `min(N,M)` direct actions. This handles direct duplicates, ties, and
`N>M`; it is not a decentralized implementation result. Hence the recovery
budget `L*` always exists and is at most `min(N,M)`, with `L*=1` exactly when
full consensus weakly dominates the private baseline.

## Complete bounded registry

| Classification | Exact count |
| --- | ---: |
| Strict compression-dominated sharing curve | 126 |
| Strict aggregation-dominated sharing curve | 16 |
| All-neutral sharing curve | 35 |
| Mixed sharing curve | 0 |
| Shared Discovery Paradox at full sharing | 78 |
| Strict aggregation-dominated consensus | 16 |
| Full-sharing boundary | 83 |
| Strict no-one-action aggregation gain | 0 |

The absent mixed class is a bounded null over this registry, not a theorem
about arbitrary channels. Weakly, 75 scenarios have `C_N<=q`, while 51 have
`C_N>=P_N`.

Recovery budgets are `L*=1` in 51 scenarios, `L*=2` in 55, `L*=3` in 64, and
`L*=4` in seven. The remaining 126 scenarios are portfolio-dependent: one
pooled action does not recover the declared direct-private baseline, but a
larger centralized action list does.

## Minimal witnesses

Under the frozen lexicographic order, the first same-baseline strict
opposite-sign pair has `M=4,N=2`: both channels have `q=1/2` and private
discovery `P_N=3/4`. The noisy-point channel changes by `-1/4`, while the
guaranteed two-shortlist changes by `+1/12`. Their recovery budgets are two
and one.

The first same-accuracy recovery separation occurs already at `M=3,N=2`:
the half-accurate noisy-point channel has `L*=2`, while the guaranteed
two-shortlist has `L*=1`. The shortlist sharing step is neutral there, which
is why it is not the strict opposite-sign witness.

The first Shared Discovery Paradox witness is the `M=3,N=2` noisy
two-shortlist with accuracy parameter `3/4`: `q=3/8`, `P_N=39/64`, and
`C_N=27/64`. The first strict aggregation-dominated consensus witness is the
`M=4,N=2` guaranteed two-shortlist: `P_N=3/4<C_N=5/6`. The first nonperfect
no-useful-one-action witness is the uninformative `M=3,N=2` point channel:
`C_N=q=1/3<P_N=5/9`.

## Evidence boundary

The registry is exhaustive only for its frozen 59 laws and three agent counts.
It provides exact bounded frequencies and minimal registered witnesses, not a
probability distribution over real organizations. No strategic behavior,
assignment incentives, source dependence, private-team optimum, human data,
real data, decentralized implementation, novelty, or submission claim is
made.

## Relation to DD-019 and DD-020

DD-019 establishes that equal one-person accuracy need not determine a pooled
top-`L` profile. DD-020 decomposes adjacent one-action sharing into aggregation
gain and lost independent rescue, proves point-channel compression, and gives a
fixed guaranteed-shortlist counterexample. DD-021 supplies the general sign
criterion, proves eventual centralized action-budget recovery, and expands the
comparison to a complete bounded registry. It neither changes nor reruns the
DD-019 or DD-020 evidence.

## Next theorem target and package boundary

The next theorem question is decentralized recovery: under what observable,
coordination-free action rule can agents attain `V_L` or a certified fraction
of it without centralized top-`L` authority? The post-merge editorial gate
must decide whether DD-019–DD-021 already support the theorem-family paper or
whether a separate Recovery Budget or coordination-free positive-sharing
package is required.

Candidate later DiscoveryBench tasks are (i) recover the smallest exact `L*`
from a channel law and declared baseline and (ii) classify one adjacent sharing
step from exact error values. Candidate synthetic hypotheses are that people or
agents overweight pooled accuracy relative to lost rescue, and that exposing
the recovery budget changes action diversification. These are proposals only;
no benchmark version, experiment package, human data, or empirical claim is
created here.
