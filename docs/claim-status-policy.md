# Claim status and promotion policy

## Evidence categories

Use the claim types enumerated in `claims/schema.json`. `status` reports workflow maturity, while `claim_type` reports epistemic category; a checked conjecture remains a conjecture.

## Promotion requirements

- **Upstream result:** pinned commit and source location, captured upstream run, parsed full-precision output, and successful comparison before `verified`.
- **Computational result:** deterministic implementation, saved configuration, run manifest, smaller-case tests, and validation record. Exactness additionally needs an auditable exhaustive-completeness argument, checkable solver certificate, proof, or matching bounds.
- **Independent reproduction:** materially independent code or method; parsing or copying upstream output does not qualify.
- **Theorem/proposition/lemma/corollary:** written proof and separate internal-consistency review. Computation alone never promotes a conjecture to theorem.
- **Monte Carlo estimate:** estimator, seeds, sample count, uncertainty method, configuration, and run record.
- **Literature claim:** verified title, authors, date, venue, stable identifier, access date, and source note.

`optimal` requires a proof, exhaustive completeness argument, independently checkable certificate, or matching lower and upper bounds. Heuristic values are lower bounds. A failed counterexample search is evidence, not proof.

## Status meanings

`proposed` is registered without sufficient evidence; `sourced` points to a pinned source; `derived` has a written derivation; `implemented` has code; `checked` passed limited stated checks; `verified` meets policy; `independently-reproduced` adds an independent method; `refuted`, `superseded`, and `retired` preserve history. Promotion records `last_checked` and evidence paths; demotion is allowed when evidence fails.
