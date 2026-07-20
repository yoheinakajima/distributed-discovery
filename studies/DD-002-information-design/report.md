# DD-002 bounded disclosure report

## Primary evidence

Run `20260720T225848Z_DD-002_94607423_e29b1460ae` started from clean commit `94607423`, completed in 0.018 seconds under a 120-second budget, and passed every configured check. Preliminary passing run `20260720T225701Z_DD-002_a12ba3e8_e29b1460ae` is preserved; the primary adds an independent witness verifier and corruption test.

## Complete bounded fixture

The four evidence states have exactly 15 deterministic partitions up to message-label equivalence. The run evaluates all 37 induced posterior games, stores every message-level pure equilibrium and all 256 global pure-equilibrium selections, and separately records the anonymous symmetric equilibrium required by the brief. The 15 policies yield 45 strict refinement pairs with explicit deterministic garblings. Randomized disclosure is not implemented.

## Selection-dependent reversal

Full pooling gives anonymous-symmetric discovery \(5/9\). The refinement with blocks \(\{0,1\}\) and \(\{2,3\}\) gives \(171/308\), lower by \(1/2772\). Yet every pure equilibrium improves from \(2/3\) to \(3/4\), and the two-action planner improves from \(2/3\) to \(3/4\). The result is therefore selection-dependent, not a Blackwell-frontier violation or an all-equilibrium reversal.

Across the complete lattice, exactly one refinement lowers anonymous-symmetric discovery, eight lower worst-pure discovery, none lowers best-pure discovery, and none lowers planner discovery. DD-C-0029 through DD-C-0031 record the exact bounded results.
