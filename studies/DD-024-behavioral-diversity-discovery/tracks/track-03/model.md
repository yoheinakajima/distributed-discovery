# Track 03 model: negative-feedback dependence and rescue

Prepared 2026-10-31 for DD-024 / AO-0018. This document freezes the bounded
model admitted after [the saved novelty screen](novelty.md). Its estimand is
the cost of a misspecified failure law and the value of a specific rescue
assignment. It does not model personality, establish a benefit of online
adaptivity, or assert a globally novel search result.

## State, information, and resources

There are three target labels, two searchers, and two rounds. A single static
target `T` is uniform on `{0,1,2}`. Given `T`, clues `X0` and `X1` are independent;
each equals `T` with probability `p`, and each wrong label has probability
`(1-p)/2`. The first-round action pair is fixed at `(X0,X1)` for every policy.

Each searcher executes one inspection in each round: four attempts, including
after a successful first round. At the round boundary every continuation
policy has the same clue pair and the same two binary detection outcomes.
There are no intermediate observations within either round. A joint allocator
can assign the ordered pair of second-round actions; this is explicit joint
allocation authority, not a decentralized personality type.

Detection is positive exactly when the attempted label equals `T` and its
detector bit is one. There are no false positives. The four detector bits are
ordered `(D00,D10,D01,D11)`, with searcher index first and round index second.
Every bit has the same marginal reliability `r`, independently of target and
clues. Four distinct dependence laws are compared:

| Law | Generative definition, with independent Bernoulli(`r`) latent bits |
| --- | --- |
| `iid` | Four independent bits, one per attempt |
| `searcher_persistent` | `(U0,U1,U0,U1)` |
| `round_common` | `(U0,U0,U1,U1)` |
| `global_common` | `(U,U,U,U)` |

The objective is the probability of at least one positive detection by the
end of round two. If the first round succeeds, every feedback-using policy
executes default tail `(0,0)`. The precommitted control instead executes its
already specified tail; the objective is already one on either path. Thus
each policy still executes four attempts, although successful paths have no
remaining effect on this objective.

## Seven specified policies

For a double-failure history, every continuation is one of the nine ordered
pairs in `{0,1,2}^2`. Ties use the lexicographically first ordered pair. The
complete maximizing set for the calibrated policy is also retained.

| Policy | Continuation rule |
| --- | --- |
| `calibrated_joint` | Maximize terminal discovery under the true failure law, conditional on the clue pair and two failures. |
| `precommitted_calibrated` | Fix the same clue-indexed tail table before observations, then dispatch its tail without using the first-round outcomes. |
| `iid_assumed_joint` | Select the best tail under independent detector failures with the correct marginal `r`; evaluate under the true law. |
| `perfect_elimination_joint` | Assume perfect detection and select the best tail restricted to labels not inspected in round one. |
| `same_searcher_revisit` | Use tail `(X0,X1)`. |
| `cross_searcher_revisit` | Use tail `(X1,X0)`. |
| `unvisited_only` | Under the true law, select the best tail restricted to labels not inspected in round one. |

Precommitment fixes a conditional lookup table; it does not disclose either
searcher's clue to the other before the round boundary. All policies receive
the same evidence at the same time. The calibrated and iid-assumed policies
differ in their assumed detector dependence, not their actual sensor budget.

The perfect-elimination assumption can assign zero probability to a genuinely
reached failure history, for example with perfect clues and imperfect sensors.
The rule is therefore completed prospectively: assign uniform weight to
unvisited labels and apply the same restricted optimizer. At least one label
is unvisited because there are three labels and two initial actions. The
output records both which clue pairs require this fallback and the true
probability mass of reaching those double-failure histories. The fallback
does not represent a Bayesian posterior under an impossible assumed event.

## Exact evaluation and restriction boundary

For target `t` and clue pair `x`, define the unnormalized source mass

`w(t,x) = (1/3) P(X0=x0 | T=t) P(X1=x1 | T=t)`.

Each detector law partitions the four attempt indices into independent
detector groups. If a schedule inspects target `t` using `k` distinct groups,
the probability of missing it on every relevant attempt is `(1-r)^k`.
Let `m(t,x)` be that miss probability for the two first-round actions, and
`m(t,x+b)` for the four-action schedule with tail `b`. The unnormalized
additional discovery mass from tail `b` is

`R(x,b) = sum_t w(t,x) [m(t,x) - m(t,x+b)]`.

The first-round success mass for clue pair `x` plus `R(x,b)` gives terminal
success mass. Maximizing this over nine tails is exact for this fixed
first-round portfolio, two-round model, and joint continuation class.
Randomizing among tails cannot improve a linear expected-success objective
above the best deterministic tail. Nothing here optimizes initial actions,
proves an unrestricted discovery optimum, or licenses a conclusion about
decentralized agents.

The precommitted control is evaluated separately as the source-weighted
four-action schedule success `sum_t w(t,x) [1-m(t,x+b)]`. Its difference from
the calibrated value must be zero. With a static target and no false positives,
only the double-failure path can still improve this objective. Accordingly,
the control prevents attributing the same conditional schedule's benefit to
an extra power of online updating. This is a model check, not a promoted
adaptivity theorem.

## Frozen grid and estimands

The primary configuration is [config.json](config.json):

- `p` in `{1/3,1/2,2/3,5/6,1}`;
- `r` in `{1/4,1/2,3/4,1}`;
- the four detector laws above;
- **80 parameter cells**, one primary execution, exact rational arithmetic,
  and no random seeds;
- a combined evaluation-and-verification cap of **120 seconds and 1024 MiB**.

The four primary contrasts are calibrated minus iid-assumed discovery,
calibrated minus perfect-elimination discovery, cross-searcher minus
same-searcher revisit discovery, and calibrated minus precommitted discovery.
The last is a mandatory zero control. Every policy's overall discovery value
and its value conditional on disagreeing clues are saved. The disagreement
stratum is `null` when its conditioning event has zero probability, rather
than an invented zero success rate.

The calibrated regrets are nonnegative by the declared finite action-class
construction; their magnitude and parameter dependence are the diagnostic
outcomes. The rescue contrast has no imposed positive sign across laws.
All results remain exact bounded computations, including nulls and reductions
to established imperfect-detection search or redundancy mechanisms.

## Independent verification and stops

The independent route generates complete worlds from target, clue, and
independent Bernoulli draws, using separate case logic for the four detector
laws. At most `3 * 3^2 * 2^4 = 432` world labels occur per cell. It directly
executes the nine candidate continuations and separately executes all four
attempt slots of each saved policy, including after success. It does not call
the primary miss formula, source-weight helper, score function, or optimizer.

Required checks cover normalization, all four `r` marginals, saved detector
weights, all candidate values, chosen actions and ties, all saved policy
values, the disagreement stratum, fallback mass, four attempts per policy,
target/searcher relabeling of candidate values, perfect-detection equivalence,
finite-class dominance, and precommitment equivalence. Four deliberate
corruptions change a detector weight, a revisit mapping, a saved value, and an
attempt budget; each must be rejected.

Configuration constants, fraction serialization, and summary formatting are
shared across routes and disclosed as shared infrastructure. The verifier
independently recomputes the scientific values before checking summaries.
The coordinator supplies source provenance, immutable outputs, and hard caps.
Stop and preserve cap breaches, normalization or budget failures, and any
method disagreement. Do not enlarge the grid, retry for a preferred result,
or add another observation mechanism within this registration.
