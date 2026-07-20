# DD-001B two-searcher thresholds

## Three benchmark families

For \(N=2\), compare:

1. two direct clue-followers, with value \(D_M(p)=2p-p^2\);
2. two distinct constant territories, with value \(T_M(p)=2/M\); and
3. a one-reroute hybrid: searcher 1 always searches target 0, while searcher 2 follows every signal except signal 0, which is rerouted to target 1.

The hybrid finds target 0 surely. It finds target 1 with conditional probability \(p+q\), and each of the other \(M-2\) targets with probability \(p\), where \(q=(1-p)/(M-1)\). Hence

\[
H_M(p)=\frac{1+(M-1)p+q}{M}
=\frac{1+(M-2)p}{M-1}.
\]

This family contains all four previously recorded informative witnesses.

## Restricted threshold theorem

For every \(M\ge3\):

\[
H_M(p)-D_M(p)
=\frac{(1-p)(1-(M-1)p)}{M-1},
\]

and

\[
H_M(p)-T_M(p)
=\frac{(M-2)(Mp-1)}{M(M-1)}.
\]

Therefore the best of these three families is territorial below \(p=1/M\), the one-reroute hybrid for \(1/M<p<1/(M-1)\), and direct for \(p>1/(M-1)\), with the displayed adjacent ties at the boundaries. At \(p=1\), direct and hybrid also tie. This is an analytic theorem for the three stated families; it does not assume that they exhaust every deterministic policy profile.

For \(M=2\), two distinct constants cover both targets with value one and are globally optimal.

## Bounded unrestricted classification

Every two-searcher signature profile has a quadratic discovery polynomial in \(p\). For each target, write each success probability as \(\alpha_i+\beta_i p\); then the target contribution is

\[
\alpha_1+\alpha_2-\alpha_1\alpha_2
+(\beta_1+\beta_2-\alpha_1\beta_2-\alpha_2\beta_1)p
-\beta_1\beta_2p^2.
\]

The DD-001B certificate enumerates every feasible signature multiset for each declared \(M\). On \([1/M,1/(M-1)]\), it subtracts every profile polynomial from \(H_M\); on \([1/(M-1),1]\), it subtracts every profile polynomial from \(D_M\). Exact endpoint and convex-vertex checks certify nonnegativity over each continuous interval.

The restriction \(p\ge1/M\) is material. At anti-informative accuracies, symmetric signal-dependent policies can beat all three benchmark families; the run records exact \(p=0\) counterexamples for \(M=3,4\). Thus no unrestricted all-\(p\) phase theorem is inferred from the benchmark comparison.
