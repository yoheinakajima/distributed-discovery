# Track 04 frozen model: information in delivery time

## Question and evidence boundary

This is the bounded timing-channel/policy-restriction audit admitted after the
[saved novelty screen](novelty.md). It asks whether a difference between
event-triggered and fixed message schedules remains after matching timing
frequency, counting information in silence, and allowing a coverage-aware
receiver. It does not claim a new general communication mechanism, a
personality effect, an equilibrium, or global novelty.

The exact prospective grid is [config.json](config.json): 36 source-law cells,
eight schedules, and two receiver classes. The primary produces 576 base
values. Deterministic and zero-information boundaries remain in the grid.
There is no stochastic sampling, fitted parameter, or parameter selection
from results. One primary run is allowed from the coordinator's clean source
freeze, with a 120-second wall-time and 1024-MiB memory cap. Implementation
smoke tests use separate single-cell configurations, never the full grid.

## World, actions, and observations

The target `T` is uniform on labels `0,...,M-1`. Conditional on `T`, independent
clues `X,Y` equal it with probability `p`; clue `Z` equals it with probability
`q`. Each wrong label is uniform on the other `M-1` labels. A observes `X,Z`;
B observes `Y`. All clues exist before any action. Every treatment therefore
has the same three clues and the same source law.

A makes two perfect inspections. Its first is the lowest-label maximizer of
`Pr(T | X,Z)`. If that inspection fails, its second is the lowest-label
posterior maximizer among the other targets. Following success, its second
action is the fixed default label zero. B also makes two inspections, with
the same default after its own first success. All four attempts occur even
after success. The objective is whether any of the four inspections finds
the target. There are no action costs, rewards for speed, or terminal-action
budget savings. A's policy is identical across all communication treatments
and both B policy classes within a cell.

Each searcher observes only its own detection outcome. In particular, B
cannot see A's actions, success, or continuation; those observations cannot
silently add a communication channel. B knows A's policy and source law.

A sends exactly one reliable packet, arriving either before B's first
inspection or between its two inspections. This time is observed. A packet
cannot contain a clue generated after the initial world. There is no cost
or delay to an inspection from sending the packet.

## Communication protocols

Let `C = 1[X=Z]` and
`alpha = p*q + (1-p)*(1-q)/(M-1)`.

| Protocol | Early arrival | Payload | Maximum complete transcript alphabet |
| --- | --- | --- | --- |
| `early` | Always | `X` | `M` |
| `late` | Never | `X` | `M` |
| `agreement_trigger` | Exactly when `C=1` | `X` | `2M` |
| `disagreement_trigger` | Exactly when `C=0` | `X` | `2M` |
| `yoked_agreement` | Independent coin of probability `alpha` | `X` | `2M` |
| `yoked_disagreement` | Independent coin of probability `1-alpha` | `X` | `2M` |
| `early_augmented` | Always | `(X,C)` | `2M` |
| `late_augmented` | Never | `(X,C)` | `2M` |

The two yoked coins are exact integrations, independent of the target and
all three clues. Their marginal timing frequencies equal those of the
corresponding event triggers. Equal packet counts do not equate their
information content: an event receiver can infer `C` from either arrival or
silence before its first action. An early augmented receiver already knows
`X,C`; a late augmented receiver learns neither until its second action.
The source law, arrival frequency, payload alphabet, complete transcript
alphabet, first-information-set masses and target masses, and a complete
receiver policy are retained separately.

First-history keys are `(Y,early,X_or_-1,C_or_-1)`. A missing payload is
represented by `-1`, which is not a target. The `C` component of an event
history is inferred from the known timing rule, including silence; it is not
an extra transmitted payload. Second-history keys are
`(Y,early,X,C_or_-1,B_first_action,B_first_hit)`. These keys retain all
previously available information, the eventual packet, and B's own outcome.

## Two receiver policy classes

**Individual MAP.** B maximizes its immediate probability of personally
finding the target at each stage. After failure it excludes its own first
target and conditions on everything it actually observes. It does not
condition on A having failed. This is a prescribed individual decision rule,
not a claim about a strategic equilibrium. Ties use the lowest label.

**Coverage-aware best response.** A's policy remains fixed. B chooses its
first inspection and every feasible contingent second inspection to maximize
the team's terminal union success. For each first information set, exact
backward induction evaluates every first target and each eventual
second-information-set continuation. At the second stage the relevant
additional mass is on worlds where A has not already found the target.
B does not observe that event; it integrates over it. A first-hit branch
already has team success and uses the default second action. All ties,
including equally useful zero-gain continuations, use the lowest label.

The saved second-stage policy covers every first-action alternative on
positive-mass source worlds, including alternatives not selected by the
optimal first stage. This permits independent local-deviation checks.
Impossible histories are omitted and have the declared default action zero;
they contribute no probability. The output reports zero-mass source worlds.

## Emulation and primary estimands

For each event protocol and each receiver class, create an explicit policy
under early augmented information that executes the event policy: compute
the virtual arrival time from `C`, ignore `X` at the first action on the
virtual-late branch, and use the saved event continuation at the second
action. Save that emulated policy and evaluate its actual union payoff.
It must equal the event policy's value exactly. The emulated policy need
not itself be MAP under the richer early information.

For every cell, trigger, and receiver class, retain:

- Event value minus the better of fixed early/late `X` delivery.
- Event value minus its timing-matched independent yoked control.
- Event value minus early augmented value within the same named class.
- The emulation value and its difference from the event value.

For the coverage-aware class the third contrast must be nonpositive:
early augmented B can emulate the event policy. A positive value is an
implementation/model failure that stops the primary, not a discovery.
Also retain the difference between MAP and coverage-aware timing contrasts
with their constituent values; this is not a unique additive causal
decomposition. No claim about a stable population mixture follows from the
audit.

## Independent verification and corruption boundaries

The primary constructs integer world masses from the symmetric channel and
uses grouped backward induction. The independent verifier reconstructs raw
`(T,X,Z,Y)` probabilities using Fraction products, integrates each timing
coin, independently computes A's actions and B's observable histories, and
executes the saved policies. It does not call the primary world builder,
posterior/observation helpers, or policy optimizer. It checks every
second-action alternative and every first-action alternative using raw
payoff differences. Thus numerical agreement is more than re-reading an
optimizer's returned value.

Checks cover normalization, fixed budgets, timing frequencies, first-history
and target masses, policy completeness, exact payoffs, all local deviations,
emulation, coverage-aware early-information dominance, and a cyclic relabeling
with transformed policy/tie priority. The relabeling is a conjugation check;
it is not a claim that every possible label permutation was separately run
with an unchanged asymmetric tie convention.

Negative controls corrupt the registered trigger metadata, arrival
frequency, an observed silence likelihood, a payload alphabet, and a saved
value. Each is passed through the same independently grounded validation
used for the uncorrupted record. These are small validation corruptions,
not additional primary experiments or deliberate scientific reruns.

Stop on any verifier disagreement, failed corruption detection, information
leakage, emulation failure, invalid budget, or resource-cap breach. Preserve
the attempted output if the coordinator's runner stops. No larger grid,
additional message, changed horizon, or more favorable policy restriction
is silently substituted.
