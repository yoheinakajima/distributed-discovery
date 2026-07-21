# DD-002 bounded disclosure report

## Primary evidence

Run `20260720T225848Z_DD-002_94607423_e29b1460ae` started from clean commit `94607423`, completed in 0.018 seconds under a 120-second budget, and passed every configured check. Preliminary passing run `20260720T225701Z_DD-002_a12ba3e8_e29b1460ae` is preserved; the primary adds an independent witness verifier and corruption test.

## Complete bounded fixture

The four evidence states have exactly 15 deterministic partitions up to message-label equivalence. The run evaluates all 37 induced posterior games, stores every message-level pure equilibrium and all 256 global pure-equilibrium selections, and separately records the anonymous symmetric equilibrium required by the brief. The 15 policies yield 45 strict refinement pairs with explicit deterministic garblings. Randomized disclosure is not implemented.

## Selection-dependent reversal

Full pooling gives anonymous-symmetric discovery \(5/9\). The refinement with blocks \(\{0,1\}\) and \(\{2,3\}\) gives \(171/308\), lower by \(1/2772\). Yet every pure equilibrium improves from \(2/3\) to \(3/4\), and the two-action planner improves from \(2/3\) to \(3/4\). The result is therefore selection-dependent, not a Blackwell-frontier violation or an all-equilibrium reversal.

Across the complete lattice, exactly one refinement lowers anonymous-symmetric discovery, eight lower worst-pure discovery, none lowers best-pure discovery, and none lowers planner discovery. DD-C-0029 through DD-C-0031 record the exact bounded results.

## Selection robustness

Run `20260721T025802Z_DD-002_73a85c71_b0e5b6dc49` applies six declared rules to the same fixture and independently verifies every posterior game, exact-potential identity, and best-response absorption equation. The game has exact potential
\[
\Phi(a,b)=\begin{cases}3\mu_a/2,&a=b,\\ \mu_a+\mu_b,&a\ne b,\end{cases}
\]
so strict best response terminates.

For the known `P00` to `P03` witness, only the anonymous-symmetric rule reverses: `5/9` falls to `171/308`. Best pure, worst pure, uniform over potential maximizers, the uniform strict-best-response basin, and the planner all improve from `2/3` to `3/4`. Across all 45 refinements, the harmful counts for those six rules are respectively `1, 0, 8, 2, 2, 0`. Potential-maximizer and basin values coincide on all 15 policies, although five policies expose multiple potential discovery values and basin branch dependence. DD-C-0039 through DD-C-0041 record the proof and exact census.

This catalogue establishes that the named reversal is not robust across the audited alternatives; it does not establish monotonicity for every selection process. Randomized disclosure remains outside the registered scope.
