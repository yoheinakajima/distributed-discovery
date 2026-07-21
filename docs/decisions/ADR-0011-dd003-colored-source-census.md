# ADR-0011: DD-003 color-preserving heterogeneous-source census

- Status: accepted
- Date: 2026-07-20
- Study: DD-003
- Issue: #26

## Context

The homogeneous DD-003 fixture fixes three target labels, four searchers, one to three nonisolated conditionally independent sources, accuracy `2/3`, plurality-winner-set reports, independent-uniform private actions, and union discovery. Its complete 51-graph census finds no pair of nonisomorphic networks with equal complete pairwise action moments and different discovery. That is a bounded null, not a sufficiency theorem.

The smallest controlled perturbation is source-specific accuracy. Accuracy must be part of the latent-source identity: an isomorphism may relabel searchers freely and may relabel source rows only together with their exact accuracy colors.

## Decision

Freeze every base-model primitive except the source-accuracy vector. The registered base census uses two and three sources and four diagnostic profiles:

- `equal-baseline`: every source has accuracy `2/3`, reproducing the prior class;
- `modest`: both `1/2` and `2/3` occur;
- `near-uninformative`: both `1/3` and `2/3` occur, with `1/3` exactly uninformative for three labels;
- `strong`: both `1/3` and `5/6` occur, maximizing the registered contrast without a degenerate perfect source.

Every heterogeneous level must occur. Thus a three-source two-level profile includes both multiplicities. All probabilities use `Fraction` arithmetic. The single controlled expansion is the three-source, three-color profile `(1/3, 2/3, 5/6)`, with every color occurring once.

No graph-isomorphism dependency is added. A primary canonicalizer minimizes the tuple of `(accuracy, adjacency row)` pairs over all source/searcher permutations. A separate adjacent-swap orbit traversal operates on labeled colored objects. Pairwise nonisomorphism is checked directly.

The observable signature stores all first action moments and every `3 x 3` pairwise action-moment matrix under one common searcher permutation. Agreement probabilities are retained only as weaker diagnostics. Private discovery uses the same plurality-set and independent-uniform action rule as the homogeneous run.

## State-size audit

The base class contains 41,612 valid labeled colored objects and 671 color-preserving orbits:

- two sources: 553 labeled objects and 47 orbits;
- three sources: 41,059 labeled objects and 624 orbits.

The controlled three-color expansion adds 12,966 labeled objects and 168 orbits. Each canonical representative evaluates at most `3 * 3^3 = 81` target/source-signal states. The full registered census therefore contains 54,578 labeled objects, 839 orbits, and at most 67,959 primary probability states. This fits the declared 120-second and 512-MB limits without an external isomorphism library.

## Consequences

Any matched-moment discovery difference is an exact bounded counterexample for this registered class. Absence of one is only a complete bounded null. Accuracy profiles are compared as colored generative models, not as interchangeable graph labels. No claim extends to asymmetric priors, dependent sources, source-specific label confusions, noisy searcher observation, larger graphs, or arbitrary accuracy palettes.
