# Agents v1 contamination threat model

Attack surfaces are public DiscoveryBench vectors, paper prose, claim/run IDs,
generator parameter names, future cross-batch traffic, evaluator access, prompt
injection, and model pretraining that may contain this public repository.

The primary control is isomorphism without scientific relabeling: sealed tasks
preserve the exact primitive state and grading rule while removing repository
names, IDs, expected values, and distinctive wording. Twelve registered probes
run before release, never only after a surprising result. Probe suppression is
itself a registered corruption.

False positives are material: common mathematical language and a correct
solution can overlap public prose. Therefore lexical overlap alone is
`inconclusive-overlap`, not evidence of memorization. Direct protected-value
access is the only automatic leakage classification. The remaining categories
require the predeclared multi-marker rules and are reported by model family and
batch without a provider ranking.
