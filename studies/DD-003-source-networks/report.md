# DD-003 bounded source-network report

## Primary evidence

Run `20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1` started from clean commit `2ea8dad5`, completed in 2.00 seconds under a 120-second cap, and passed every configured and independent check.

## Complete graph class

The exact labeled valid-graph counts are 1, 79, and 2161 for one, two, and three sources. Quotienting independent source/searcher relabeling yields exactly 1, 8, and 42 canonical graphs, for 51 total. A separate adjacent-swap orbit traversal reproduces these counts; a verifier that does not import the primary model checks validity, pairwise nonisomorphism, every stored moment signature, and every discovery value.

## Pairwise-moment bounded null

Uniform target-label symmetry fixes every scalar report's first one-hot moment. The full pairwise second-moment matrix is represented by six exact action-agreement probabilities up to a common searcher relabeling. Ten signatures each match two nonisomorphic graphs. None of these ten pairs differs in private discovery. This is a complete bounded null for the frozen graph class and signal law, not a general sufficiency theorem.

## Scalar counterexamples

Average pairwise agreement loses information present in the matrix. Graphs `K2N4:00011110` and `K2N4:01111111` both have average agreement `3/4`, but exact private discovery is `8/9` and `31/36`, differing by `1/36`. Across the census, 22 matched-average pairs differ in discovery; 59 graph pairs with matched source HHI also differ. Thus neither scalar is sufficient on this class.

## Homogeneous boundary

The homogeneous run left full pairwise-moment insufficiency open and identified documented source-accuracy heterogeneity as the smallest controlled perturbation. “Effective channels” remains a family of defined diagnostics, not a validated universal scalar. The registered continuation below executes that perturbation without enlarging the searcher class or changing the action rule.

## Heterogeneous source accuracy

Run `20260721T032358Z_DD-003_84238b76_2cbc13e66a` freezes the base physical and action model but carries exact source accuracy as an isomorphism-preserving color. Four registered base profiles contain 41,612 valid labeled colored objects and 671 orbits; one controlled three-color expansion adds 12,966 labeled objects and 168 orbits. Primary canonical minimization and an independent adjacent-swap traversal agree on every count, and all 50 equal-baseline two/three-source networks reproduce the homogeneous results.

The homogeneous bounded null does not survive. In the simplest exact witness, sources with accuracies `1/2` and `2/3` have degree patterns `(1,4)` and `(4,1)` respectively in one network, and the colors are attached to the opposite degrees in the other. All four first moments and six complete `3 x 3` pairwise action-moment matrices match, but private discovery is `3/4` versus `2/3`, a difference of `1/12`.

Across all 839 registered colored networks, 163 complete-moment signatures match multiple networks, covering 485 networks; 111 of those groups contain different discovery values. The independent verifier reconstructs every signature and value and rejects a corrupted witness difference. DD-C-0042 through DD-C-0044 record the exact bounded census and counterexample. No conclusion extends to continuous accuracy palettes, larger graphs, dependent sources, asymmetric priors, or higher-order report laws.
