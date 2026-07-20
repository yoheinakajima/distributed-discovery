# DD-001A policy signatures

## Lossless objective reduction

For a deterministic policy $f$ and target $t$, define

\[
c_t=|\{x:f(x)=t\}|,\qquad d_t=\mathbf 1\{f(t)=t\},\qquad
q=\frac{1-p}{M-1}.
\]

Exactly $c_t-d_t$ incorrect signals map to $t$, while the correct signal maps to $t$ exactly when $d_t=1$. Therefore

\[
s(t)=\Pr(f(X)=t\mid\theta=t)=q c_t+(p-q)d_t.
\]

The fixed-profile discovery formula uses each policy only through the vector of conditional successes $s(t)$. Consequently it depends on policy $f_i$ only through

\[
\sigma(f_i)=((c_0,d_0),\ldots,(c_{M-1},d_{M-1})).
\]

This is a lossless objective reduction, not a claim that every locally plausible integer vector is realizable.

## Necessary-and-sufficient feasibility theorem

Let $n_0=|\{t:d_t=0\}|$ and $r_t=c_t-d_t$. A proposed signature is realizable by a deterministic policy if and only if:

1. $c_t$ is a nonnegative integer, $d_t\in\{0,1\}$, and $d_t\le c_t$;
2. \(\sum_t c_t=M\); and
3. $r_t\le n_0-1$ when $d_t=0$, while $r_t\le n_0$ when $d_t=1$.

Necessity is immediate except for the first residual bound: a nonfixed row $t$ cannot be assigned to its own column, so column $t$ can receive at most the other $n_0-1$ nonfixed rows. A fixed row has already been removed and its column can receive all $n_0$ residual rows.

For sufficiency, remove every fixed row and its consumed diagonal slot. Duplicate residual column $t$ into $r_t$ slots and connect nonfixed row $x$ to every slot except those of column $x$. The residual capacity total is

\[
\sum_t r_t=M-\sum_t d_t=n_0.
\]

Hall's condition for a singleton row $x$ is exactly $r_x\le n_0-1$. For any row subset of size at least two, every column slot has a neighbor in the subset, so its neighborhood contains all $n_0$ slots and Hall holds automatically. A perfect matching therefore exists. Adding the removed fixed rows reconstructs a policy with the requested signature.

`reference_feasibility` implements the duplicated-slot matching proof and returns an explicit policy or an infeasibility explanation. `reduced_feasibility` independently applies the closed-form Hall conditions. Exhaustive small-$M$ audits compare both decisions with raw policy enumeration.

## Exact scaled objective

Write $p=A/B$ in lowest terms and set $D=B(M-1)$. Then

\[
s_i(t)=\frac{(B-A)c_i(t)+(AM-B)d_i(t)}{D}.
\]

The optimized evaluator therefore uses integer scores

\[
a_i(t)=(B-A)c_i(t)+(AM-B)d_i(t)
\]

and computes

\[
G=1-\frac{\sum_t\prod_i(D-a_i(t))}{M D^N}.
\]

For the canonical $M=16,p=1/5$, $D=75$ and $a_i(t)=4c_i(t)+11d_i(t)$. Exact fractions remain authoritative; the integer representation removes avoidable floating-point arithmetic.

## Counting and symmetry

For a fixed set of $n_0$ nonfixed targets, residual capacities are weak compositions of $n_0$ into $M$ columns, except for the $n_0$ forbidden compositions that place every residual row in one nonfixed diagonal column. Hence the number of feasible labeled signatures is

\[
S_M=\sum_{n_0=0}^{M}\binom{M}{n_0}
\left[\binom{n_0+M-1}{M-1}-n_0\right].
\]

An individual signature's orbit under target relabeling is determined by the multiset of residual counts among fixed targets and the multiset among nonfixed targets. The implementation counts these bounded partitions exactly. This individual quotient is not independently applicable to every agent in a profile: relative target alignments across agents affect the product objective. The bounded DD-001A run measures both counts and deliberately does not treat independently sorted signatures as a lossless profile quotient.

## Evidence boundary

The theorem and integer identity are analytic. The registered `signature-certificate.yml` run audits their implementations, reproduces the existing 21 certified tiny optima and raw-policy tie counts, and measures the canonical state space before any large search. A successful structural certificate does not by itself solve the canonical optimum.
