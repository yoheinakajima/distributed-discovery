# DD-001B exact two-searcher thresholds

## Result

The four informative tiny-grid counterexamples are members of one family. One searcher always covers target 0; the other follows its signal except that signal 0 is rerouted to target 1. Its exact value is

\[
H_M(p)=\frac{1+(M-2)p}{M-1}.
\]

Against direct \(D_M(p)=2p-p^2\) and distinct territories \(T_M(p)=2/M\), exact factorizations prove the three-family phase theorem:

- territorial below \(p=1/M\);
- one-reroute hybrid for \(1/M<p<1/(M-1)\);
- direct above \(p=1/(M-1)\);
- adjacent ties at both thresholds.

This theorem holds for every \(M\ge3\) within the three declared policy families.

## Bounded unrestricted classification

Primary run **20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1** started from clean commit **b2cc23f4**, finished in 35.86 seconds under a 120-second budget, and passed. It represents every two-searcher signature profile as an exact quadratic in \(p\). For \(M=3,4,5\), it exhausts 438,734 feasible signature multisets and verifies nonnegative optimizer margins at every interval endpoint and interior convex vertex.

Consequently, for these three values of \(M\), the unrestricted deterministic optimum is the one-reroute hybrid throughout \([1/M,1/(M-1)]\) and direct throughout \([1/(M-1),1]\). All four known witnesses are reproduced by raw policies, signatures, formula evaluation, and direct target/signal enumeration.

## Necessary boundary

The informative restriction is essential. At \(p=0\), exact signature and raw-policy enumeration give unrestricted optima \(11/12\) for \(M=3\) and \(2/3\) for \(M=4\), above the three-family benchmarks \(2/3\) and \(1/2\). Signal-dependent no-fixed-point policies exploit reliably wrong clues. Thus the natural all-\(p\) extension is refuted.

## Evidence scope

DD-C-0026 is an analytic restricted-family theorem. DD-C-0027 is a complete continuous but bounded computational classification for \(M=3,4,5\), conservatively **checked**. DD-C-0028 independently reproduces the two anti-informative counterexamples. The evidence supports, but does not prove, the conjecture that the informative hybrid/direct envelope extends to all \(M\).
