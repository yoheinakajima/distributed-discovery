# Audience-design results and proofs

DD-013 inherits DD-012's three-target environment. Write `r=1-p`. Audience
size and action-mode count are kept separate throughout.

## Binding Audience Theorem

A binding audience of size `m` receives and follows a shared clue of accuracy
`q`; every other role follows an independent private clue of accuracy `p`.
The failure event gives `G_N(0)=1-r^N` and, for `m>=1`,
`G_N(m,q)=1-(1-q)r^(N-m)`.

The first delivery margin is `r^(N-1)(q-p)`. Every later audience increment is
`-(1-q)p r^(N-m-1)<0`. Therefore the binding optimum is uniquely `m=1` when
`q>p`, uniquely `m=0` when `q<p`, and exactly `{0,1}` when `q=p`. This is an
access-gated result for the registered follow/private action class.

## Precision versus publicity

The registered symmetric garbling family replaces the delivered clue accuracy
by `g` with `1/3<=g<=q`. For `m>=1`, its failure probability is
`F_N(m,g)=(1-g)r^(N-m)`.

If `q>p`, compare every feasible `(m,g)` to full precision at one recipient.
Because `1-g>=1-q` and `r^(N-m)>=r^(N-1)`,
`F_N(m,g)>=F_N(1,q)`. Equality requires both `m=1` and `g=q`; otherwise the
comparison is strict. If `q=p`, no delivery and `(m,g)=(1,q)` tie, while all
other feasible garblings are worse. If `q<p`, even the first use at accuracy
`g<=q` has margin `r^(N-1)(g-p)<0`, and additional readers strictly reduce
discovery. Thus the binding optimum weakly dominates every registered
precision-reduced audience, with equality only at a binding-optimal one-reader
design. This is not a Blackwell-order or arbitrary-garbling theorem.

## Action quality, diversity, and effective channels

The probability that a uniformly selected action is correct is
`Q_N(m)=[mq+(N-m)p]/N`. Let `w=(1-p)/2`. With no shared reader, linearity over
the three labels gives `D_N(0)=1-(1-p)^N+2[1-(1-w)^N]`.

For `m>=1`, condition on whether the shared label is correct. With `L=N-m`,

`D_N(m)=q{1+2[1-(1-w)^L]}`

` +(1-q){1+[1-(1-p)^L]+[1-(1-w)^L]}`.

Information-access count is `m`. The action-relevant effective-channel count
is `N` at `m=0` and `N-m+1` at `m>=1`: one common draw plus `N-m` private draws.
These measures need not have the same optimum.

## Voluntary recipients

An audience of size `m` receives the clue. Before realized signals, each
recipient chooses either the registered follow-shared mode or the follow-private
mode; nonrecipients can use only the private mode. If `k` recipients choose the
shared mode, discovery and equal-split payoffs are the DD-012 `k`-reader
quantities.

Let `Delta_k` be DD-012's payoff gain from changing private mode to become
reader `k+1`. A count `k in {0,...,m}` is a weak voluntary-audience equilibrium
iff `Delta_(k-1)>=0` when `k>0` and `Delta_k<=0` when `k<m`. The second condition
is omitted at `k=m` because no additional recipient can switch; nonrecipients
lack access. Strict inequalities give strict equilibrium.

Since `Delta_k` strictly decreases, restricting the audience truncates the
global threshold rather than changing it. In particular, audience one exactly
implements the binding optimum correspondence: its recipient chooses shared
mode when `q>p`, private mode when `q<p`, and is indifferent when `q=p`.
Larger audiences can create duplicate shared use; conditional signal-dependent
responses are outside this ex-ante two-mode class and belong to DD-014.

## Exact institutions

Exclusive delivery to any one assigned identity binds the reader count at one;
random and rotating identity assignments have the same anonymous discovery
metrics. When `q<=p`, withholding delivery binds the zero-reader optimum.

Universal pooling provides a second implementation under full public access.
Every agent receives `1/N` if the team discovers the target and zero otherwise.
The payment is ex-post budget balanced against the unit discovery prize, needs
no external subsidy, and gives every agent expected payoff `G_N(k)/N`. A
unilateral mode change has the same sign as the corresponding change in
discovery. Therefore the weak equilibrium-count correspondence is exactly the
binding optimum: `{1}` for `q>p`, `{0}` for `q<p`, and `{0,1}` for `q=p`.
Counts are strict when `q!=p`. At `q>p`, the `N` possible one-reader identities
remain symmetric equilibria; assignment or rotation selects identity without
changing the implemented count.

The implementation claim is restricted to the registered ex-ante
follow-shared/follow-private deviation class. It does not cover arbitrary
signal-contingent policies, collusion, hidden action technologies, or dynamics.
