# DD-003 bounded source-network report

## Primary evidence

Run `20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1` started from clean commit `2ea8dad5`, completed in 2.00 seconds under a 120-second cap, and passed every configured and independent check.

## Complete graph class

The exact labeled valid-graph counts are 1, 79, and 2161 for one, two, and three sources. Quotienting independent source/searcher relabeling yields exactly 1, 8, and 42 canonical graphs, for 51 total. A separate adjacent-swap orbit traversal reproduces these counts; a verifier that does not import the primary model checks validity, pairwise nonisomorphism, every stored moment signature, and every discovery value.

## Pairwise-moment bounded null

Uniform target-label symmetry fixes every scalar report's first one-hot moment. The full pairwise second-moment matrix is represented by six exact action-agreement probabilities up to a common searcher relabeling. Ten signatures each match two nonisomorphic graphs. None of these ten pairs differs in private discovery. This is a complete bounded null for the frozen graph class and signal law, not a general sufficiency theorem.

## Scalar counterexamples

Average pairwise agreement loses information present in the matrix. Graphs `K2N4:00011110` and `K2N4:01111111` both have average agreement `3/4`, but exact private discovery is `8/9` and `31/36`, differing by `1/36`. Across the census, 22 matched-average pairs differ in discovery; 59 graph pairs with matched source HHI also differ. Thus neither scalar is sufficient on this class.

## Next conjectures

The natural next test varies source accuracy, introduces documented heterogeneous accuracies, or enlarges the graph class to five searchers/four sources while preserving exact certification. A full pairwise-moment insufficiency claim remains open. “Effective channels” remains a family of defined diagnostics, not a validated universal scalar.
