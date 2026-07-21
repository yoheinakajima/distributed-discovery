# Analytic results and proofs

Let `q=1-p`, let `k` agents use independent sources, and let `m=N-k` use the
common source. When `k<N`, there are `k+1` conditionally independent source
draws, so

`G_N(k,p)=1-q^(k+1)`.

When `k=N`, there are `N` draws, so `G_N(N,p)=1-q^N`; in particular, the last
transition from `N-1` to `N` adds no discovery.

## Type payoffs

For `X_r~Binomial(r,p)`, a common user's gross prize at count `k<N` is

`C_k = p E[1/(m+X_k)]`.

For `0<k<N`, an independent user's gross prize is

`I_k = p[q E(1/(1+X_(k-1))) + p E(1/(m+1+X_(k-1)))]`.

At `k=N`, it is `I_N=p E[1/(1+X_(N-1))]`. Net independent payoff subtracts
`c`; common use is free. Summing type payoffs gives `G_N(k,p)`.

## Private thresholds and equilibrium counts

Define the gross payoff gain from one common user becoming the `(k+1)`th
independent user by `A_k=I_(k+1)-C_k`. For `0<=k<N`, direct subtraction gives

`A_k = pq E[1/(1+X_k)-1/(N-k+X_k)]`.                                      (1)

Thus a weak equilibrium with `k` independent users is characterized exactly by

`A_k <= c <= A_(k-1)`,                                                     (2)

with the missing boundary inequality omitted at `k=0` or `k=N`.

The thresholds are strictly decreasing. Put
`f_m(x)=1/(x+1)-1/(x+m)` and couple
`X_(k+1)=X_k+Y`, where `Y` is Bernoulli(`p`). Conditional on `X_k=x`,

`f_m(x)-E[f_(m-1)(x+Y)]`

equals a fraction with denominator

`(x+1)(x+2)(x+m-1)(x+m)`

and numerator

`(x+1)(x+2)+p(m-2)(2x+m+1)`.

For `m>=2` the numerator and denominator are positive. Multiplication by `pq`
and expectation prove `A_k>A_(k+1)` for `k=0,...,N-2`; equation (1) gives
`A_(N-1)=0`. This proves the threshold ordering and makes (2) a complete
general-`N` pure-equilibrium count characterization, including adjacent weak
counts exactly at a threshold.

## Planner thresholds and the all-common trap

The planner's gross marginal value for transition `k` is

`B_k=pq^(k+1)` for `k=0,...,N-2`, and `B_(N-1)=0`.                         (3)

These thresholds are strictly decreasing, and a planner optimum satisfies the
analogue `B_k<=c<=B_(k-1)`. At the all-common boundary,

`A_0=pq(N-1)/N`, while `B_0=pq`.

Consequently, for every finite `N>=2` and `0<p<1`,

`pq(N-1)/N <= c < pq`                                                     (4)

makes `k=0` a weak source-choice equilibrium while every planner optimum uses
at least one independent source. The interval has exact width `pq/N` and
therefore shrinks to zero as `N` grows.

For fixed `k`, equation (1) also gives

`lim_(N->infinity) A_k = q(1-q^(k+1))/(k+1)`,

because the second reciprocal expectation vanishes and
`E[1/(1+X_k)]=(1-q^(k+1))/((k+1)p)`.

## Exact limit to a universal under-acquisition claim

Private thresholds need not lie below planner thresholds in the interior. At
`N=3`, `k=1`, equation (1) reduces to

`A_1=pq(3-2p)/6`, while `B_1=pq^2`.

Hence `A_1>B_1` exactly when `p>3/4`. With `p=4/5` and `c=13/375`,
`A_1=14/375>c>12/375=B_1`; the unique equilibrium has `k=2`, while the unique
planner optimum has `k=1`. The model therefore supports a general boundary
under-acquisition theorem, not a universal ordering of equilibrium and planner
source counts.
