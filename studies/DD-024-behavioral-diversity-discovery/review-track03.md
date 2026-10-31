# Internal scientific review: track 03

Reviewed 2026-10-31, completed at 21:45:54 UTC. This review was performed by
a separate campaign agent from the track-03 implementation author. It is an
internal pre-execution check, not external peer review or a proof certificate.

## Verdict

**No blocking scientific or implementation defect identified in the reviewed
version.** The implementation is consistent with the declared fixed-initial-
portfolio, two-round, joint-continuation model. The candidate enumeration is
complete for that class, the four-attempt/two-clue budgets match, and the
independent raw-world route checks the substantive mathematics without using
the primary miss formula or optimizer. The track is suitable for the
coordinator's clean-source freeze and bounded primary execution, subject to
the campaign's existing gates.

The findings below preserve two important interpretation limits: equality of
detector-bit marginals is an ex ante statement, and the registered cross-
searcher rescue contrast has a simple structural explanation. Neither the
nonnegative calibrated regrets nor precommitment equivalence constitutes an
unexpected new adaptivity finding.

## Reviewed artifacts

- [Scientific model](tracks/track-03/model.md).
- [Prospective configuration](tracks/track-03/config.json).
- [Novelty screen](tracks/track-03/novelty.md) and
  [implementation record](tracks/track-03/implementation.md).
- [Evaluator and verifier](../../src/distributed_discovery/behavioral_diversity/feedback.py).
- [Focused tests](../../tests/unit/test_behavioral_diversity_feedback.py).

Content hashes at review:

| Artifact | SHA-256 |
| --- | --- |
| `feedback.py` | `39151f8fb53d7f7f32467dcb570a6c774c39de99569bffab5b3c2f627875d8f8` |
| `track-03/model.md` | `09be9b6286e7fd38c1767170733db860e38114de06480818d32b1e5d95ff2526` |
| `track-03/config.json` | `1ce71830257c4e424ac7ec597d1cdaf1dc8a628b40c2a80ac8cdca556281fad2` |
| `test_behavioral_diversity_feedback.py` | `b23415f0c85e703e6c8a171ac05d447bca9144b1dc301ca27bcabcbded4f8ec9` |

No scientific source, model, config, test, claim, result, or shared plan was
edited during this review. This review document is the sole written artifact.

## 1. Finite completeness and objective accounting

For each of nine clue pairs, the first-round actions are fixed. The only
histories that can improve the terminal at-least-one-detection objective are
the histories where both first inspections failed. A positive detection
already fixes terminal success to one. On a double-failure history there
are exactly nine ordered second-round action pairs and no observation
between the two second-round attempts.

`PAIRS` explicitly lists all `3 * 3` ordered tails. `_scores` evaluates each
one; `_best` retains all ties and selects their first lexicographic member.
Independent optimization of each clue-indexed continuation is therefore
complete for the declared information, objective, fixed initial portfolio,
and joint allocation authority. Randomizing tails cannot improve their
linear expected payoff. This does not cover a choice of initial actions,
additional rounds, decentralized implementation, a moving target, or a
different stopping/effort objective.

The primary formula is valid under dependence: the event of missing on all
four attempts is a subset of the event of missing on the first two. Their
probability difference is exactly the probability of first-round failure
followed by second-round detection. Factoring those miss probabilities by
the distinct independent latent detector groups matches the registered
four failure laws. Unnormalized source weights are appropriate because
the conditional normalizer is the same for every candidate tail at a
given clue/failure history.

Zero-probability clue/history cases receive complete lexicographic policy
entries and contribute zero value. Perfect-elimination's impossible-assumed-
history fallback is stated before execution, checked independently, and
accompanied by the true reached probability mass. It is not silently treated
as a valid posterior under the false perfect-detection model.

## 2. Identical budgets and dependence interpretation

All policies use the same two initial private clues, the same fixed first
actions, the same shared clue pair and two binary detection outcomes at the
round boundary, and the same two subsequent inspection slots. The verifier
directly executes four attempts even after first-round success and checks
their expected count is four for every policy. The choice of default tail
after success has no effect on this terminal-success objective.

The raw detector bits are latent; receiving two detection outcomes does not
reveal those bits independently of whether a searched label was correct.
The saved policy choices depend on the clue pair and relevant detection
history, not on the simulation's hidden target or latent detector values.
Joint assignment authority is explicitly shared by the optimizing
comparators. It should not be described as an advantage of a personality
type or an individual agent operating without coordination.

**Nonblocking reporting clarification:** every detector bit has the same
unconditional marginal success probability `r`. Conditional reliability
after a failed search is generally different under the four dependence
laws. That difference is the mechanism being tested. Reports should say
"matched ex ante detector reliabilities" rather than imply that conditional
success rates remain equal after all observed histories.

The iid-assumed policy uses the correct marginal `r` but the wrong dependence
law when the true law is not iid. Its actual payoff is evaluated under the
true law. The perfect-elimination policy changes the reliability assumption
and restricts the action set; its loss should be described as the loss from
that specified rule, including the explicitly completed impossible-history
cases, rather than a universal cost of Bayesian versus non-Bayesian people.

## 3. Precommitment is a valid matched control

The precommitted policy fixes the clue-indexed tail lookup table before
observations. At the round boundary it receives the same clue pair as the
other policies and dispatches the table entry without consulting detection
outcomes. It is not an unconditional action pair chosen before any clue,
and it is not given early access to both clues.

Its equality with the calibrated feedback policy is appropriate here.
Both use the same tail on the only outcome branch where terminal success
can still change. They may execute different tails after a first success,
but that branch already has objective value one. The primary evaluates
precommitment through a four-action miss formula, while the independent
verifier executes its noncontingent tail even after success. This avoids
merely copying the calibrated scalar into the control result.

The mandatory zero contrast correctly prevents attributing the calibrated
schedule's performance to a new general benefit of online feedback.

## 4. Independent verification and corruption sensitivity

The primary constructs detector-group miss probabilities. The verifier
instead draws the one, two, or four independent Bernoulli latent variables
appropriate to each law, expands their detector patterns, enumerates target
and clue worlds, and checks realized detection predicates. Its clue weights
are calculated separately. It then verifies all 81 clue/tail combinations
per cell, all chosen policies and tie sets, full policy execution, the
disagreement stratum, fallback mass, all four detector marginals, and the
derived contrasts.

Shared items are constants/schema, rational serialization, and summary
formatting. They do not substitute for recomputing scientific values.
The review additionally disabled `_groups`, `_miss`, `_pattern_weights`,
`_weights`, `_scores`, `_best`, `_primary_row`, and `run` after constructing
one small result. Verification still passed. Thus the reviewed verifier
does not rely on these primary scientific routines at runtime.

The internal negative controls actually send damaged single-cell artifacts
through `_audit`: a detector-pattern weight, the cross-revisit mapping, a
saved value, and the attempt budget. All were rejected in the review
fixture. A further corruption of a saved candidate-rescue mass was also
rejected. These tests are substantively relevant to the scientific model;
they are not only successful JSON parsing.

## 5. Structural rescue control and reporting limit

For the persistent-searcher law, a cross revisit can add success when the
clues disagree, exactly one initial clue names the target, the searcher
initially assigned that target has a dead detector, and the other searcher
has a live detector. The corresponding source factor is `2p(1-p)` and the
detector factor is `r(1-r)`. Thus the hand-check expression for the
cross-minus-same contrast in this model is `2p(1-p)r(1-r)`.

For iid failures, exchanging searcher identities leaves the relevant
attempt distribution unchanged. For round-common and global-common
failures, swapping the same pair of targets does not change its detection
event. Their cross-minus-same contrast is zero. This is a model sanity
check, not a newly promoted theorem or research claim.

**Nonblocking wording recommendation:** the model says the rescue contrast
has no imposed positive sign across laws. It is not forced positive by an
optimizer, but its sign is structurally nonnegative for these four laws.
The synthesis should make that reduction visible. A grid of positive
persistent-searcher cells illustrates the declared dependence law; it does
not establish that arbitrary common failures favor cross assignments or
that an unexpected general diversification principle was discovered.

## Development validation performed

Only one explicitly non-primary configuration was evaluated during this
review: `p=2/3`, `r=1/2`, law `searcher_persistent`, with `expected_cells=1`.
It used `PYTHONPATH=src .venv/bin/python` and an in-memory script; no result
file or run manifest was created. The hand rescue contrast is `1/9`.
The independent verifier passed with:

- One cell, 81 candidate tails, and 567 relabeling equalities checked.
- Four attempts, two clues, and two shared first-round outcomes per policy.
- All eight primary scientific routines disabled while verification ran.
- All four required corruptions rejected, plus the additional candidate-
  value corruption.

The existing focused test source was reviewed; its analytical perfect-clue
and perfect-detection controls agree with the model. The frozen 80-cell
primary grid was not executed, sampled for findings, or altered during this
review. Runtime, cap compliance, immutable provenance, and final primary
verification remain the coordinator's responsibility.
