# DD-003 results

Primary run `20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1` passed. It stores all 51 canonical graphs, exact protocol and diagnostic summaries, ten matched full pairwise-moment groups, a bounded-null certificate, an exact mean-agreement counterexample, an SVG figure, and independent verification.

The full pairwise matrix has no discovery counterexample within this exact class: ten signatures each match two graphs, and discovery is equal in all ten pairs. The weaker average agreement scalar is insufficient: two graphs share mean agreement `3/4` but have discovery `8/9` and `31/36`. These results do not generalize beyond the frozen signal law and graph class.

Heterogeneous-source evidence: `../../../results/verified/20260721T032358Z_DD-003_84238b76_2cbc13e66a/`.

- `colored-census-certificate.json`: all nine registered spec counts, homogeneous regression, and complete matched-moment census.
- `colored-network-registry.json`: all 839 canonical colored networks with exact moments, diagnostics, and discovery.
- `pairwise-moment-counterexample.json`: explicit `3/4` versus `2/3` discovery witness with identical complete first/pairwise moments.
- `complete-moment-matched-groups.json`: 163 matched groups, of which 111 differ in discovery.
- `independent-verification.json`: separate orbit, isomorphism, moment, discovery, and corruption checks.

This exact counterexample resolves the registered heterogeneity question but remains bounded to ADR-0011.
