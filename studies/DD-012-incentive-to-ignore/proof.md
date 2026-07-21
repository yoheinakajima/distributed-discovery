# Analytic results and proofs

Let `r=1-p`. An ex-ante access gate sends the shared clue to exactly `k`
attending roles. Those roles act on the shared clue; the other `N-k` roles do
not receive it and act on conditionally independent private clues. Thus
“ignore” means non-delivery, not forgetting observed information.

## Discovery: first-use value and duplicate-use loss

At `k=0`, all `N` action-relevant clues are independent, so

`G_N(0)=1-r^N`.

At `k>=1`, discovery fails exactly when the shared clue is wrong and all
`N-k` private-clue actions are wrong:

`G_N(k)=1-(1-q)r^(N-k)`.

The first attention margin is

`G_N(1)-G_N(0)=r^(N-1)(q-p)`.

Every later margin is

`G_N(k+1)-G_N(k)=-(1-q)p r^(N-k-1)` for `k>=1`.

Therefore, for `0<p,q<1`, discovery has unique optimum `k=1` when `q>p`,
unique optimum `k=0` when `q<p`, and tied optima `k in {0,1}` when `q=p`.
Every duplicate user after the first strictly lowers discovery. This is the
scoped **One-Reader Theorem** for the registered follow/private policy class.

## Exact equal-split payoffs

If `X~Binomial(N-k,p)`, an attending agent at a profile with `k>=1`
attenders receives

`A_N(k)=q E[1/(k+X)]`.

If `Z~Binomial(N-k-1,p)`, an ignoring agent at a profile with `k<N`
attenders receives

`I_N(k)=p[q E[1/(k+1+Z)]+(1-q)E[1/(1+Z)]]`.

The two terms condition on whether the shared clue is correct. In every state,
the successful agents' shares sum to one exactly when discovery occurs.
Taking expectations gives

`k A_N(k)+(N-k) I_N(k)=G_N(k)`.

## Private attention thresholds

Let `Delta_k=A_N(k+1)-I_N(k)` be the payoff change when one ignoring role
becomes the `(k+1)`st attender. Conditioning on the shared clue and the
switcher's private clue gives the simpler identity

`Delta_k=q(1-p) E[1/(k+1+Z_k)]-p(1-q) E[1/(1+Z_k)]`,

where `Z_k~Binomial(N-k-1,p)`. A profile with `k` attenders is a weak pure
equilibrium exactly when `Delta_(k-1)>=0` and `Delta_k<=0`, omitting the
inapplicable boundary inequality. Both inequalities are strict for a strict
equilibrium.

The sequence `Delta_k` is strictly decreasing. Couple
`Z_k=Z_(k+1)+B` with `B~Bernoulli(p)`. The first reciprocal expectation
strictly falls with `k`: when `B=1` its adjacent denominators agree, and when
`B=0` the earlier denominator is one smaller. The second reciprocal
expectation strictly rises because removing a Bernoulli trial weakly lowers its
denominator, strictly with positive probability. Its coefficient in `Delta_k`
is negative. Since `0<p,q<1`, at least one strict comparison has positive
weight and hence `Delta_k>Delta_(k+1)`.

Consequently the equilibrium correspondence is a single threshold count, or
two adjacent counts exactly when one `Delta_k` is zero. At the boundaries,

`Delta_0=(q-p) E[1/(1+Binomial(N-1,p))]`,

so all-ignore is an equilibrium exactly when `q<=p`; and

`Delta_(N-1)=q(1-p)/N-p(1-q)`,

so all-attend is an equilibrium exactly when
`q>=Np/(1+(N-1)p)`. Exactly one attender is a weak equilibrium iff
`Delta_0>=0>=Delta_1`.

In particular, when `q>p` the equal-split attention game cannot have an
all-ignore equilibrium even though the social optimum is one reader. It can
instead have excessive attention, including all-attend. When `q<p`, strict
decrease from `Delta_0<0` makes all-ignore the unique strict equilibrium and
the social optimum. These statements concern ex-ante role choice in this
finite access-gated model, not behavioral information avoidance.
