# DD-024 / track-04 — Communication timing and its hidden information budget

Date: 2026-10-31 UTC. Status: **saved novelty screen; no implementation or
numerical experiment**. Scope authority: AO-0018.

## Decision

**Pivot and proceed only as a bounded timing-channel and policy audit.** Close
the broad candidate that intermittent communication improves collective search
as if it were new: experiments, organizational models, robotics, and
decentralized planning already study that effect and its conditions.

The residual falsifiable question is whether an apparent event-triggered
communication advantage survives (a) matching the timing distribution and
action/message counts, (b) counting information conveyed by silence and
delivery time, and (c) allowing a receiver to ignore early information instead
of forcing immediate imitation. Equal packet counts alone are not an equal
information budget.

This track would supply a finite decomposition for the repository's discovery
objective. It is not a new general result about delayed communication, a new
communication algorithm, a globally novel effect, or a personality experiment.
A complete classical reduction or a null residual is an acceptable outcome.
The coordinator must freeze the final model before implementation.

## Searches and access

Primary papers, publisher records, and author/institutional sources were
consulted on 2026-10-31. Queries included:

- `intermittent communication multi agent search equal communication budget event triggered periodic collective intelligence timing`
- `Hollinger Singh 2012 multirobot coordination intermittent connectivity search communication`
- `event triggered communication silence informative decentralized POMDP communication value information search`
- `Value of Communication In Decentralized POMDPs authors`
- `event silence Dec-POMDP communication`
- `Bernstein Shore Lazer 2018 intermittent breaks interaction collective intelligence PNAS 1802407115`
- `Analyzing myopic approaches Becker authors communication`

This is a bounded prior-art screen, not a systematic review or priority claim.
The 2018 human experiment's full text and the 2009 communication article's
publisher text were inspected. Other entries below were checked through their
primary abstracts/publication records.

## Closest external work

| Source | Primary record | Exact overlap and remaining boundary |
| --- | --- | --- |
| Bernstein, E., Shore, J., and Lazer, D. (2018), *How intermittent breaks in interaction improve collective intelligence*, PNAS 115, 8734–8739 | [Open full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6126746/); [DOI](https://doi.org/10.1073/pnas.1802407115) | Intermittent interaction can retain exploration while supporting learning in human traveling-salesperson tasks. The present candidate is an exact finite search/information-accounting audit, not a replication or a new demonstration of the broad effect. |
| Hollinger, G. A., and Singh, S. (2012), *Multirobot Coordination With Periodic Connectivity: Theory and Experiments*, IEEE Transactions on Robotics 28, 967–973 | [Author-institution publication record](https://publications.ri.cmu.edu/multirobot-coordination-with-periodic-connectivity-theory-and-experiments) | Search with periodic communication constraints, algorithms, and empirical validation is established. There is no movement or connectivity-maintenance cost in the proposed finite model. |
| Becker, R., Carlin, A., Lesser, V., and Zilberstein, S. (2009), *Analyzing Myopic Approaches for Multi-Agent Communication*, Computational Intelligence 25, 31–50 | [Publisher article](https://doi.org/10.1111/j.1467-8640.2008.01329.x) | The decision whether to communicate now or defer, the value of remaining silent, and failures of myopic communication are direct prior art. No general timing-optimization claim survives this overlap. |
| Wu, F., Zilberstein, S., and Chen, X. (2011), *Online planning for multi-agent systems with bounded communication*, Artificial Intelligence 175, 487–511 | [Publisher abstract](https://doi.org/10.1016/j.artint.2010.09.008) | Event-based communication triggered by history inconsistency, deferral, common knowledge, and periodically unavailable channels are established. The proposed contribution is a matched finite audit, not a new event trigger. |
| Trombetta, E. I., Capello, E., Shell, D. A., and Rossi, F. (2026), *Asking for Information by Evaluating the Communication and Coordination Trade-Off in Multi-Agent POMDPs*, IEEE Robotics and Automation Letters 11, 9144–9150 | [IEEE record](https://ieeexplore.ieee.org/abstract/document/11560930); [DOI](https://doi.org/10.1109/LRA.2026.3703246) | Recent work explicitly permits using local information without forced synchronization and asks when communication pays. This blocks treating avoidance of forced consensus as a new conceptual contribution. |

## Repository overlap

- **DD-015:** history visibility and feedback timing already alter finite
  Bayesian action portfolios; changing the amount of information cannot be
  reported as a pure timing effect.
- **DD-020:** sharing can compress action portfolios, but the effect depends
  on the declared signal and action protocol.
- **DD-022:** selected mixing and coordination restrictions matter; benefits
  cannot be generalized across equilibrium/policy classes.
- **DD-000 and the information-comparison literature:** with a common objective
  and an emulation-capable policy class, receiving the same information earlier
  cannot reduce the best achievable value. Harm from early information requires
  a restriction, cost, or change in the information itself. The proposed study
  must keep that control visible and cannot promote it as a new theorem.

## Why the original broad test is insufficient

A schedule that forces everyone to copy a common recommendation as soon as a
message arrives can make early sharing appear harmful by construction. A
trigger chosen using private evidence can encode that evidence in the absence
of a message, and in its eventual delivery time, even when its payload is
unchanged. Thus matching one message per trial does not isolate timing.

The proposed finite audit explicitly distinguishes payload, observable timing,
policy responsiveness, and collective coverage. It preserves a timing-matched
randomized control and an augmented early message whose alphabet equals the
complete event-triggered transcript alphabet.

## Proposed exact model and configuration

This is a proposal, not yet a frozen scientific configuration.

1. One uniform target `T` among `M` labels. Searcher A receives two clues `X,Z`;
   searcher B receives one clue `Y`. All are conditionally independent given
   `T`; `X,Y` have accuracy `p`, and `Z` accuracy `q`, with uniform wrong labels.
   The unequal per-agent clue counts are fixed across every treatment: three
   clues total. All clues exist before actions; there is no late source of fresh
   evidence that only a delayed schedule obtains.
2. Each searcher executes two inspections with perfect detection: four attempts
   in every treatment. Agents observe only their own detection outcomes; the
   other agent's action/outcome is not an uncounted communication channel.
   A uses a fixed local Bayesian rule: inspect its highest-posterior target,
   then the next after failure. Declare a default second action after success.
3. A sends exactly one packet to B, either before B's first or before its
   second action. Delivery is reliable; packet size and transcript alphabet
   are reported separately from packet count. Actions are not delayed or
   deleted to pay for a message. The primary objective is at least one
   successful inspection by the team after the fixed budget.
4. Define `C = 1[X=Z]`. The basic packet payload is always `X`.
   Candidate schedules:
   - `early`: send `X` before B's first action;
   - `late`: send `X` before B's second action;
   - `agreement_trigger`: early iff `C=1`, otherwise late;
   - `disagreement_trigger`: early iff `C=0`, otherwise late;
   - `yoked_random`: a signal-independent early/late draw with the same marginal
     early probability as the corresponding trigger;
   - `early_augmented`: send `(X,C)` before B's first action;
   - `late_augmented`: send `(X,C)` before B's second action.
5. In an informed event-trigger receiver, silence before the first action is
   observed and Bayesian conditioning includes its known trigger rule. A
   separate timing-blind ablation may ignore that information, but is clearly
   labeled misspecified. At the second action the one packet has arrived.
6. Proposed grid: `M in {3,4,5}`,
   `p in {1/M,1/2,3/4,1}`, `q in {1/M,3/4,1}`: **36 cells**.
   The all-state universe has `M^4` target/clue labels, at most 625 per cell,
   before the two-point exact mixture for yoked timing. These are proposed
   resource counts, not observed results.

### Receiver policies and comparator fairness

Evaluate two receiver classes separately:

- **Individual Bayesian MAP:** B maximizes its own immediate detection chance
  given its information, with recorded tie-breaking. Any collective loss from
  premature convergence belongs to this restriction, not to information itself.
- **Coverage-aware finite-horizon best response:** hold A's policy fixed and
  enumerate B's possible first inspections and information-contingent second
  inspections to maximize team union discovery. B conditions on the latent
  possibility that A already covers a target. This is a richer declared
  common-objective policy class, not an equilibrium claim.

The full event transcript `(delivery_time,X)` has at most `2M` symbols. The
augmented packet `(X,C)` also has at most `2M` symbols. Comparing them avoids
giving event triggering an unpriced one-bit channel. Early augmented B must
also be able to execute the event policy by voluntarily withholding use of `X`
on the virtual-late branch. That explicit emulation provides a direct equality
check, and an optimized early-augmented policy supplies the classical
weak-dominance benchmark.

For yoked timing, calculate its exact Bernoulli weight from the source law;
do not estimate it by simulation or choose it after seeing results. In this
symmetric channel, the agreement frequency is
`p*q + (1-p)*(1-q)/(M-1)`. The timing draw is independent of all source states.
This formula is a specification identity to be checked, not a reported
research finding.

### Primary falsifiable estimands

- **Apparent timing gain:** event-triggered discovery minus the better of
  fixed early/late delivery of `X`, within a named receiver class.
- **Evidence-dependent timing contrast:** event-triggered discovery minus its
  exactly timing-matched, signal-independent yoked control.
- **Residual after transcript matching:** event-triggered discovery minus
  early-augmented discovery under the coverage-aware best response. A positive
  value would contradict the declared emulation relation and must stop the run
  for a model or implementation audit, not be celebrated as a novel effect.
- **Policy restriction gap:** the difference between the timing contrasts for
  individual-MAP and coverage-aware receivers. Report constituent values rather
  than claiming a unique additive causal decomposition.

Retain full value tables, receiver policy tables, timing frequencies, packet
counts, transcript alphabets, true information sets, and reached zero-mass
boundaries. A sign change across source accuracies is a bounded observation;
absence of one is a bounded null. No numerical comparison has been run for
this screen.

## Verification, resources, and stopping proposal

The primary route uses exact rational grouping by receiver information set and
finite-horizon backward induction with A's policy fixed. Its independent
verifier enumerates complete `(T,X,Z,Y)` worlds and the timing-control coin,
executes the saved policies, and sums the union-detection indicator directly.
It must not call the primary posterior updater, grouping/value routine, or
optimizer. Optimality is only over the declared finite receiver policy class;
the verifier separately checks each local alternative at every information set.

Required checks: source normalization, exact four-attempt/one-packet budgets,
no hidden observation of A's actions, no information before actual delivery,
correct silence inference, independent yoked coin, agreement-frequency
identity, value bounds, target permutation invariance of values/optimal sets,
event-policy emulation equality, and early-augmented coverage-aware weak
dominance. Corrupt a trigger, an arrival time, a silence likelihood, a payload
alphabet, or a value; each corruption must fail validation.

Use exact arithmetic and exact two-point mixing, so random seeds are not
applicable. Proposed limits are 120 seconds and 1024 MiB, one primary run,
no retry toward a desired sign. The state-space estimate is analytic rather
than timed. Stop on cap breach, information leakage, comparator mismatch, or
independent-verifier disagreement. Do not silently add message-dependent
source quality, nonstationary targets, a larger horizon, or new free messages.
Retain an overlap/negative disposition even if the resulting tables are useful
as an instrument-validation example rather than a new research phenomenon.
