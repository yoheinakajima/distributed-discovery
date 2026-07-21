# Integration tests

M1 adds upstream parsing and run-provenance integration tests. This index prevents an unexplained empty directory.

The suite also checks generated paper and public-site contracts. In particular,
`test_three_results_paper_source.py` covers the synthesis paper's required
structure and caveats, generated evidence inputs, immutable-run provenance, and
deterministic-build validation.
