# DD-002 results

Primary evidence: `../../../results/verified/20260720T225848Z_DD-002_94607423_e29b1460ae/`.

- `partition-registry.json`: all 15 deterministic policies up to message labels.
- `equilibrium-registry.json`: all 37 posterior games, pure correspondences, global selections, anonymous symmetric equilibria, planner values, and concentration measures.
- `refinement-comparisons.json`: all 45 strict refinement pairs and garbling witnesses.
- `selection-reversal-witness.json`: explicit selection-dependent reversal.
- `witness-verification.json`: independent recomputation result.
- `partition-summary.csv`: compact exact results table.

Preliminary run `20260720T225701Z_DD-002_a12ba3e8_e29b1460ae` remains immutable and valid, but the primary run adds the separate witness verifier. Randomized disclosure is not implemented.

Selection-robustness evidence: `../../../results/verified/20260721T025802Z_DD-002_73a85c71_b0e5b6dc49/`.

- `selection-certificate.json`: all six exact policy catalogues, potential witnesses, strict-best-response absorption distributions, and all 45 refinement comparisons.
- `known-witness-robustness.json`: direct comparison of the original `P00` to `P03` witness under every audited rule.
- `partition-selection-summary.csv`: compact policy-by-rule table.
- `independent-verification.json`: independent recomputation and corruption-test result.

The known reversal occurs only under anonymous-symmetric selection among the audited alternatives. This does not extend the disclosure class: randomized disclosure is still not implemented.
