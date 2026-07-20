# DD-001A signature reduction and certification barrier

## Outcome

DD-001A achieves the accepted structural-reduction outcome, not a solution of the canonical optimum. The primary immutable run is **20260720T221139Z_DD-001_b1d8d431_40bf5b06a5**; it started from clean commit **b1d8d431188457c62648446797dcebdc323ba991**, completed the configured work in 13.73 seconds under a 120-second budget, and passed every validation. Preliminary passing run **20260720T220911Z_DD-001_6822d4c6_40bf5b06a5** is preserved; its presentation key was corrected before the primary run because the pooled benchmark is not a private-team certificate.

## Proved reduction

For policy $f_i$, target $t$, incoming count $c_i(t)$, fixed-point indicator $d_i(t)$, and $q=(1-p)/(M-1)$,

\[
s_i(t)=q c_i(t)+(p-q)d_i(t).
\]

The fixed-profile discovery objective therefore depends on each raw policy only through its targetwise count/fixed-point signature. Signature feasibility is also exact: after fixed rows are removed, the residual duplicated-column matching has only singleton Hall constraints. With $n_0$ nonfixed rows and $r_t=c_t-d_t$, feasibility is equivalent to the local count conditions plus $r_t\le n_0-1$ for nonfixed target $t$ and $r_t\le n_0$ for fixed target $t$. The matching reference implementation reconstructs a raw policy from every feasible signature; the reduced implementation decides the closed-form conditions independently.

For rational $p=A/B$, the optimized evaluator uses scale $D=B(M-1)$ and score

\[
a_i(t)=(B-A)c_i(t)+(AM-B)d_i(t).
\]

It computes the objective from the exact integer failure sum. Canonically, $D=75$ and $a_i(t)=4c_i(t)+11d_i(t)$.

## Independent validation

The primary run:

- reproduces all 21 prior exact tiny-grid optima;
- reconciles every raw-policy multiset tie count from signature multiplicities;
- reproduces the $(M,N,p)=(3,2,2/5)$ hybrid optimum $7/10$;
- matches raw formula evaluation, direct target/signal enumeration, the Fraction signature reference, and the scaled-integer evaluator;
- normalizes probability exactly;
- verifies direct and territorial policies and the stated direct/private/pooled ordering;
- compares matching and reduced feasibility against every locally admissible candidate and every raw policy signature for $M=2,3,4,5$;
- reconstructs every audited feasible signature exactly; and
- passes a separate structural-certificate checker whose corruption test rejects a modified count.

These results support DD-C-0023 through DD-C-0025. DD-C-0023 remains **derived** because its proof, not computation, establishes the theorem. DD-C-0024 is **independently reproduced** because the signature representation and search path are materially distinct from the prior raw-policy enumeration. DD-C-0025 is **verified** for the exact finite counts.

## Canonical state space

At $(M,N,p)=(16,8,1/5)$:

- raw policies per agent: 18,446,744,073,709,551,616;
- feasible labeled signatures per agent: 148,348,284,928;
- individual-signature target-label orbits: 5,806;
- signature multisets after agent permutation but before target quotienting: 5,817,544,508,742,203,415,773,519,264,794,208,893,444,139,238,056,614,203,268,215,932,897,118,628,684,812,510,720.

Even retaining only sixteen 64-bit words per multiset state would require 744,645,697,119,002,037,219,010,465,893,658,738,360,849,822,471,246,618,018,331,639,410,831,184,471,656,001,372,160 bytes. A global target relabeling can reduce a complete profile, but independently replacing every agent signature by one of 5,806 sorted orbits is not lossless: relative target alignments determine the product objective. No unproved quotient was used.

## Evidence boundary and next step

The exact direct lower bound remains $325089/390625=0.83222784$. The pooled-planner value 0.859421246199 remains a numerical upper benchmark under greater information and assignment authority; it is explicitly not a private-team certificate. DD-001A therefore records a proved lossless reduction and a documented barrier to naive exact enumeration. It does not produce a private-team certified interval, prove direct optimality, or supply a counterexample.

The next milestone is DD-001B issue #11: exact two-searcher hybrid formulas and thresholds. Any later canonical method must preserve cross-agent target alignment and provide an independently checkable admissible bound.
