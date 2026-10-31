# DD-024 / track-03 — Negative feedback, revisitation, and failure dependence

Date: 2026-10-31 UTC. Status: **saved novelty screen; no implementation or
numerical experiment**. Scope authority: AO-0018. This is a prospective pivot
from the broad commitment/switching slot to the coordinator-assigned question
of unreliable negative feedback. Static downside portfolios remain outside
this track.

## Decision

**Pivot and proceed only as a bounded inference-and-reliability audit.** Close
the broad candidate claim that allowing revisits or Bayesian updating after a
negative inspection is a new discovery. Both are established search theory.
Also close the proposed interpretation of a simple all-failure search schedule
as a distinct benefit of personality diversity or online adaptivity.

The residual question is narrower: under equal one-attempt detection rates,
equal information, equal attempts, and a fixed initial search portfolio, how
much discovery is lost by misidentifying the dependence of inspection failures?
Can cross-searcher revisitation rescue failures that same-searcher repetition
cannot, and when does that change the preferred continuation portfolio?

This is an additional estimand for the repository's finite discovery model,
not an established globally novel phenomenon, new algorithm, theorem, or
empirical claim. A null or a complete reduction to the named controls is an
acceptable outcome. The coordinator must freeze a final configuration before
any scientific implementation or primary execution.

## Searches and access

Primary publisher, author, and university records were consulted on
2026-10-31. Queries included:

- `optimal search imperfect detection correlated detection probabilities Bayesian search revisit locations searcher`
- `multi agent search unreliable negative observations correlated sensor failures Bayesian search revisiting`
- `optimal search imperfect detection correlated failures multiple searchers overlook probability Stone search theory revisiting`
- `search overlooking dependent probabilities detection`
- `Provable Methods for Searching with an Imperfect Sensor`
- `On Redundancy, Efficiency, and Robustness in Coverage for Multiple Robots`

This is a targeted positioning search, not a systematic review or priority
certificate. Some records were accessible only at abstract level; the overlap
claims below do not exceed the inspected material.

## Closest external work

| Source | Inspected primary record | Exact overlap and remaining boundary |
| --- | --- | --- |
| Chung, T. H., and Silvestrini, R. T. (2014), *Modeling and analysis of exhaustive probabilistic search*, Naval Research Logistics 61, 164–178 | [Publisher and abstract](https://doi.org/10.1002/nav.21574) | Bayesian updating from imperfect positive and negative detections, search decisions, and sensitivity to error rates are established. The proposed comparison isolates the dependence topology of misses while keeping each attempt's marginal reliability fixed. |
| Kasthurirangan, P. N., Nguyen, L., Perk, M., Chakraborty, N., and Mitchell, J. S. B. (2025), *Provable Methods for Searching with an Imperfect Sensor*, ICRA, 3028–3035 | [University publication record](https://researchconnect.stonybrook.edu/en/publications/provable-methods-for-searching-with-an-imperfect-sensor/); [DOI](https://doi.org/10.1109/ICRA55743.2025.11128471) | Budgeted finite-location search with false negatives, revisits, and optimality/complexity questions is direct prior art. This track removes movement costs and does not claim a new search algorithm. The university record supplies the final proceedings author order, which differs from an early preprint listing. |
| Duvocelle, B., Flesch, J., Shi, H. M., and Vermeulen, D. (2021), *Search for a moving target in a competitive environment*, International Journal of Game Theory 50, 547–557 | [Open publisher article](https://doi.org/10.1007/s00182-021-00761-5), especially section 3.1.2 | Multiple searchers, posterior-based search, and indistinguishability of an overlooked target from an empty location are established. Its competitive random-turn, moving-target model is not this fixed four-attempt common-objective comparison. |
| Hazon, N., and Kaminka, G. A. (2008), *On redundancy, efficiency, and robustness in coverage for multiple robots* | [Publisher article](https://doi.org/10.1016/j.robot.2008.01.006) | Repetition can aid robustness; redundancy is not inherently waste. This track studies detection-failure dependence, not geometric spanning-tree coverage, robot motion failure, or a new general robustness result. |

## Repository overlap

- **DD-004** already evaluates perfect-elimination sequential search. Its status
  explicitly requires a new registration for noisy tests.
- **DD-015** already separates visible actions, failed-action feedback, and
  planner versus autonomous choice. Its stopping feedback perfectly eliminates
  attempted targets; the new sensor law changes that inference.
- **DD-005** and the held Reliable Discovery option already identify the
  distinction between coverage redundancy and robustness. This track does not
  reopen the held theorem program or claim a reliability characterization.
- **DD-014** already warns that restricted role classes need not contain the
  unrestricted optimum. The new optimizer is restricted to a declared finite
  continuation class and a fixed initial portfolio.

## Classical reduction that must be retained

With a static single target, false negatives only, and an at-least-one-detection
objective, the only observation path on which further success can matter is
the all-failure path. Once initial evidence is fixed, a deterministic policy's
actions on that path can be written down in advance. Recomputing its posterior
online does not by itself create a larger achievable search portfolio than a
precommitted all-failure schedule. This is a model-structure argument for the
screen, not a promoted project theorem.

The proposed audit therefore compares a calibrated continuation with its
precommitted equivalent and requires equal value. A genuine additional
adaptivity question would need branching nonterminal observations, changing
targets, or another independently registered friction. None is added here.

## Proposed exact model and configuration

This is a proposal, not yet the frozen scientific configuration.

1. Three candidate targets; target `T` uniform. Two searchers receive private
   clues `X_0,X_1`, conditionally independent given `T`. Each clue is correct
   with probability `p`, with uniform wrong labels.
2. Two rounds, one inspection by each searcher per round: four allocated and
   executed attempts for every policy. Round-one actions are fixed at
   `(X_0,X_1)`. All continuation policies receive the same clue pair and both
   round-one detection outcomes after that round. No hidden extra observation
   is supplied to the calibrated policy.
3. A detection is positive exactly when the chosen target equals `T` and the
   corresponding detector bit `D_(i,t)` is one. There are no false positives.
   Every detector bit has marginal success probability `r`.
4. Compare four fully known true detector laws:
   - `iid`: all four bits independent;
   - `searcher_persistent`: one independent bit per searcher, reused in both rounds;
   - `round_common`: one independent bit per round, shared across searchers;
   - `global_common`: one bit shared across both searchers and rounds.
5. If either first-round inspection succeeds, terminal discovery is already
   one; execute a declared harmless default continuation so the attempt count
   remains four. If both fail, choose a continuation pair from all nine ordered
   target pairs. Tie-breaking is deterministic and recorded; invariance checks
   compare values and optimal sets rather than requiring tied policy labels to
   be invariant.
6. Proposed grid: `p in {1/3,1/2,2/3,5/6,1}`,
   `r in {1/4,1/2,3/4,1}`, and the four laws: **80 parameter cells**.
   These counts describe the proposed configuration, not observed findings.

### Policies and fair comparisons

- `calibrated_joint`: select the continuation pair that maximizes terminal
  discovery under the true conditional failure law. This has joint allocation
  authority and is labeled a benchmark, not an equally decentralized agent.
- `precommitted_calibrated`: record the same continuation for each initial clue
  pair before inspecting; it must have the same value as `calibrated_joint`.
- `iid_assumed_joint`: choose a continuation using the `iid` law with the same
  marginal `r`, then evaluate its actual outcomes under each true law.
- `perfect_elimination_joint`: choose the continuation under the incorrect
  assumption `r=1`, restricted to unvisited targets, then evaluate under the
  true law. If the assumed all-failure history has zero probability, assign
  uniform mass to the unvisited targets and apply the same restricted optimizer;
  record the true mass on which this explicit fallback is used.
- `same_searcher_revisit`: continue at `(X_0,X_1)` after two failures.
- `cross_searcher_revisit`: continue at `(X_1,X_0)` after two failures.
- `unvisited_only`: choose the best continuation restricted to targets not
  inspected in round one, evaluated using the true law. This restriction must
  remain explicit and is not a generic explorer personality.

All policies retain the same initial portfolio, evidence access, attempt
budget, source law, and real detector law. Variation in whether a policy uses
the correct law is the treatment, not a concealed information-budget bonus.

### Primary falsifiable estimands

- **Dependence misspecification regret:** true discovery under calibrated
  continuation minus true discovery under the iid-assumed continuation.
- **Failure-elimination regret:** calibrated value minus perfect-elimination
  value, with the fallback's reached probability disclosed.
- **Cross-searcher rescue contrast:** cross-searcher revisit value minus
  same-searcher revisit value; report both unconditional values and the
  disagreement-clue stratum.
- **Schedule-equivalence control:** calibrated minus precommitted calibrated
  value. A nonzero value indicates an implementation or information mismatch.

Also preserve complete continuation tables, optimal-action ties, discovery
probabilities, first-round success probabilities, and policy-selection changes.
No positive sign is prespecified for the cross-searcher contrast across all
failure laws; no numerical result has been calculated for this screen.

## Verification, resources, and stopping proposal

The primary route uses exact rational latent-state weights and unnormalized
posteriors after two failures, checking all nine continuation pairs. The
independent route enumerates complete worlds `(T,X_0,X_1,D_00,D_10,D_01,D_11)`
and directly executes each frozen policy. At most `3*3^2*2^4 = 432` latent
world labels occur per cell; zero-weight labels remain part of the accounting
where convenient. The verifier must not call the primary posterior updater,
optimizer, or value function. It can independently check the saved maximizing
table against every alternative pair.

Required checks: probability normalization, fixed `r` marginals, four attempts,
uniform-wrong-clue law, exact cross-method agreement, value bounds,
target/searcher permutation checks, all laws coinciding at `r=1`, the
all-failure schedule-equivalence control, and calibrated dominance over its
own listed continuation alternatives. Corrupt a detector-law weight, swap a
revisit mapping, alter a selected action/value, and change the budget; each
must be rejected.

Use exact rational arithmetic; seeds are not applicable. Resource proposal:
120 seconds and 1024 MiB, deterministic execution, one primary run, no retries
for favorable results. This is an analytic state-count estimate, not a timed
performance measurement. Stop and preserve a failure on cap breach,
normalization failure, budget mismatch, or verifier disagreement. Do not
silently add diagnostics, intermediate sensor messages, more rounds, or a
larger grid. A fully classical, null, or negative interpretation remains an
acceptable final disposition.
