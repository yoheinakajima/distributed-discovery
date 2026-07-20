# DD-002 bounded public-disclosure fixture

## Primitives

The target \(\theta\in\{0,1,2\}\) has uniform prior. The designer observes pooled evidence \(S\in\{0,1,2,3\}\) with likelihood matrix

\[
\Pr(S=s\mid\theta)=
\begin{pmatrix}
1/2&1/8&1/8&1/4\\
1/4&1/2&1/8&1/8\\
1/8&3/8&1/8&3/8
\end{pmatrix}.
\]

A deterministic disclosure is a set partition of the four evidence states. Its public message identifies the block containing \(S\). Message names carry no content, so restricted-growth/canonical set partitions quotient message-label equivalence. There are exactly \(B_4=15\) policies. Randomized disclosure kernels are not implemented.

Two searchers observe the same message and simultaneously choose one of the three target locations. If \(k\) searchers choose the true target, each receives \(1/k\); otherwise payoff is zero. Social discovery is the posterior probability that at least one chosen location is the target.

## Equilibrium treatment

For every posterior game the implementation enumerates every labeled pure Nash equilibrium. A partition's pure-equilibrium correspondence is the Cartesian product of its message-level pure equilibria; all global choices and exact ex-ante discovery values are stored. No favorable pure equilibrium is selected silently.

The declared selected outcome is the anonymous symmetric Nash equilibrium. If the other searcher uses \(x\), choosing location \(a\) yields \(\mu_a(1-x_a/2)\). On support \(K\), indifference gives

\[
x_a=2\left(1-\frac{\lambda}{\mu_a}\right),\qquad
\lambda=\frac{2|K|-1}{2\sum_{a\in K}1/\mu_a}.
\]

The implementation enumerates supports, checks positive support probabilities and unused-action inequalities, and independently verifies best-response payoffs. General asymmetric mixed equilibria are outside this bounded brief; all pure equilibria and the required anonymous symmetric equilibrium are included.

## Information order

For deterministic disclosures, a partition is Blackwell-more-informative when it refines the other partition. The coarser message is obtained by a deterministic garbling that maps every fine block to its containing coarse block. Every reported comparison stores this refinement/garbling witness; no entropy proxy is used.

The pooled two-action planner selects the two highest-posterior locations after each message. Its value is evaluated separately from equilibrium discovery.
