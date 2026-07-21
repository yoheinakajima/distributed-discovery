# DD-001 results

Primary evidence run: `../../../results/verified/20260720T200447Z_DD-001_6eb12861_ba766d1eba/`.

- `tiny-phase-grid.csv` and `optimal-policies.json`: certified exhaustive finite optima.
- `phase-grid.svg`: generated exact role-gain figure.
- `canonical-restarts.csv` and `canonical-best-policy.json`: bounded heuristic search; lower bound only.
- `validation.json` and `manifest.json`: completeness, independent-evaluator, normalization, bound, seed, and checksum records.

Earlier passing runs `20260720T200124Z_DD-001_6eb12861_f9bcf73ec7` and `20260720T200245Z_DD-001_6eb12861_ba766d1eba` remain immutable and valid for their narrower output sets.

DD-001A signature evidence:

- Primary run: `../../../results/verified/20260720T221139Z_DD-001_b1d8d431_40bf5b06a5/`.
- `tiny-signature-grid.csv`: independent signature reproduction of all 21 exact optima and raw tie counts.
- `feasibility-audits.json`: matching, closed-form Hall, raw-signature, and reconstruction checks through M=5.
- `canonical-state-space.json` and `reduction-certificate.json`: exact finite structural counts and certificate inputs.
- `certificate-verification.json`: independent recomputation result.

Preliminary run `20260720T220911Z_DD-001_6822d4c6_40bf5b06a5` remains immutable. Its computational audit passed, but the primary run supersedes its overstrong presentation key. Neither run certifies a canonical private-team objective upper bound.

DD-001B threshold evidence:

- Primary run: `../../../results/verified/20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1/`.
- `threshold-certificate.json`: continuous exact polynomial envelope for unrestricted M=3,4,5.
- `known-witnesses.json`: all four informative witnesses reproduced by raw and signature enumeration plus independent evaluators.
- `anti-informative-counterexamples.json`: exact p=0 counterexamples to the all-p three-family extension.
- `restricted-phase-table.csv` and SVG: generated threshold samples for M=3 through 8.

Alignment-bound evidence:

- Primary run: `../../../results/verified/20260721T022739Z_DD-001_358cb1eb_cd16846ba5/`.
- `canonical-alignment-bound-certificate.json`: exact two-level Bellman certificate proving the canonical upper bound equals `325089/390625`.
- `independent-verification.json`: statewise inequality/equality audit plus corruption rejection without an optimizer call.
- `tiny-alignment-bounds.csv` and `anti-informative-alignment-bounds.csv`: 21 exact tiny matches and two upper-valid anti-informative checks, including one strict gap.
- `cost-audit.json`: 0.39-second bounded execution, state/transition counts, and certificate size.
