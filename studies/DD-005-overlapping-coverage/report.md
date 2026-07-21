# DD-005 weighted-union coverage report

Primary run `20260721T050706Z_DD-005_be3b544c_98698dee2f` exactly enumerates
all two-action portfolios in three hand-designed deterministic fixtures and
checks the primary frontier with a separate bit-mask implementation.

The atomic singleton control has matching exact, top-individual, and greedy
value `2`. In the four-outcome duplicated-ranking witness, the two individually
highest actions cover the same three outcomes and have value `3`, while pairing
either with the lower-ranked singleton covers all four outcomes and has exact
value `4`. Thus two portfolios can use two distinct action labels yet differ in
covered value; action-label distinctness is not a sufficient coverage statistic.

In the six-outcome greedy witness, the greedy and top-individual portfolios have
value `5`, while the exact portfolio covers all outcomes with value `6`. These
are exact finite counterexamples to treating atomic ranking or a greedy frontier
as exact under overlap. They do not challenge monotone-submodular approximation
guarantees or cover noisy/repeated-action robustness.
