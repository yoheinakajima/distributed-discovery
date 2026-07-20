# DD-007 research brief — Empirical Discovery Audits

## Motivating question

Which observable event and provenance data identify, estimate, or bound protocol loss, recovery budgets, duplicate action, source concentration, effective channels, and latent copying in real discovery systems?

## Minimum viable model

- Repeated independent discovery sessions generated from the canonical atomic model.
- A mixture of private, consensus, and assigned protocols with a declared common-cue copying rate.
- Event-level records for session, actor, timestamp, candidate/action, source identifier, score or report, and outcome.
- Configurable missing source IDs, action-matching error, and outcome censoring.
- Start with known protocol labels; hide them only in a later identification experiment.

The synthetic model is a recovery test, not an empirical validation of the canonical process.

## Relationship to the canonical benchmark

Canonical outputs supply known ground truth for discovery, distinct actions, copying, and planner gain. DD-007 asks which diagnostics recover those quantities from event logs and how misspecification breaks recovery. It consumes source-network definitions from DD-003 and overlap definitions from DD-005 when those stabilize.

## Main quantities

- Action-label duplication, unique actions, pairwise overlap, and action Herfindahl index.
- Source degree/concentration, provenance overlap, and missingness rate.
- Observed discovery with uncertainty intervals.
- Model-based frontier, protocol loss, and recovery budget with sensitivity bounds.
- Latent copying estimates and calibration error.
- Identification region when protocol/source provenance is partially hidden.

## Adjacent literature

Rzhetsky et al. (2015) provide a science-of-science experiment-choice application; organizational/network literatures motivate concentration measures. Standard missing-data, measurement-error, causal-inference, and off-policy-evaluation tools are required before observational interpretation. Canonical inversion from duplicate proposals is model-specific.

## Likely methods

Synthetic data generators; exact expectations and Monte Carlo with declared seeds; bootstrap or analytic uncertainty; calibration plots; partial-identification bounds; missingness and matching-error sensitivity; held-out recovery; later preregistered case-study protocols.

## Falsifiable questions

1. With known protocol and complete provenance, can a copying estimator recover the canonical parameter with calibrated uncertainty?
2. Is action duplication alone insufficient to distinguish copying from a consensus/action-protocol mixture?
3. How much missing provenance makes source concentration or effective channels unidentified?
4. Do benchmark-relative protocol-loss estimates remain directionally correct under posterior-score miscalibration?

## Dependencies and risks

Depends on DD-000 run discipline, DD-003 source diagnostics, DD-005 coverage definitions, and possibly DD-004 timing. Risks include structural nonidentification, privacy constraints, selection/censoring, unstable entity matching, treating scores as calibrated posteriors, survivorship bias, and converting a synthetic recovery success into an empirical claim.

## First executable experiment

Define a versioned event schema and generate seeded canonical sessions over a grid of copying, protocol mix, sample size, provenance missingness, and action-matching error. Estimate discovery and descriptive concentration first; then test a copying estimator against known truth with confidence-interval coverage and explicit misspecification cases.

## Completion criteria

- Event ontology, provenance unit, and missing-data assumptions are versioned.
- Every estimator has a declared target and synthetic ground truth.
- Seeds, sample sizes, uncertainty method, and failures are retained.
- Identification and descriptive diagnostics are not conflated.
- No real-system claim is made before a separate data/ethics and identification review.
