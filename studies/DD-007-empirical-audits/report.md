# DD-007 synthetic audit report

Primary immutable run `20260721T052307Z_DD-007_af4ea130_72fb89c5fc` validates
46,080 generated event records against `schemas/discovery-events/v1` and audits
96 seeded recovery-grid replicates. Every record is explicitly synthetic.

With no action-matching error, the shared-target-corrected copying estimator has
coverage `1.0` in each of the six copying/provenance conditions. The means are
approximately `0.014`, `0.470`, and `1.000` at true copying `0`, `1/2`, and `1`.
Provenance missingness alone leaves these action-only estimates unchanged. In
contrast, matching error `0.1` produces systematic attenuation: coverage is
`0.5` at true copying `1/2` and `0` at true copying `1`, for both missingness
levels. The estimator is therefore a synthetic recovery diagnostic, not a robust
real-log estimator.

Two explicit identification counterexamples are retained: hidden consensus with
zero copying and private play with full copying both produce duplicate action
pairs, and all-null source IDs are compatible with distinct source allocations.
No empirical, causal, or real-system claim is made by this study.
