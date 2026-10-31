# DD-024 track 02: admitted finite robustness audit

## Admission and scope

On 2026-10-31 the coordinator admitted the bounded interaction audit described
in [novelty.md](novelty.md). The broad robust-randomization novelty claim
remains closed. Worldwide novelty is unestablished. Track 01 remains closed
for overlap. This file and [config.json](config.json) specify the prospective
model before scientific implementation; the clean source/PR freeze and
primary execution are later campaign gates.

The estimand concerns a restricted six-role team and ambiguous evidence
quality. It is not a claim about all decentralized policies, human traits,
or societal welfare. All outcome values must come from the declared policy
actions and source probabilities, never hand-entered expected metrics.

## Environment and information

Two agents choose one of three target labels. The true target is uniform.
Nature chooses regime A or B before the diagnostic, target clues, and policy
randomization. In A, private clues are correct with probability `1/3` and the
shared clue with probability `5/6`; in B those accuracies are reversed.
Wrong labels divide the remaining probability equally.

With probability `rho`, both agents receive one common private-source draw.
Otherwise they receive independent private-source draws. The branch and
public clue are conditionally independent given target and regime. This
mixture weight is not defined as a Pearson correlation coefficient.

A common diagnostic arrives before the target clues. It is absent, reports
the regime correctly with probability `3/4`, or reports it perfectly. Given
the regime it is independent of the target and target clues. Every policy
class receives the same diagnostic for its cell, the same shared clue, and
its own private clue; no class pools private clues. Diagnostics consume no
search action in this specified synthetic model. Every team makes exactly
two actions.

## Restricted policies and timing

After the diagnostic and before target clues arrive, the team assigns one
of six roles to each agent:

| Role | Action |
| --- | --- |
| P | Private clue |
| S | Shared clue |
| C | The common label if clues agree; the third label if they disagree |
| K0, K1, K2 | Always the indicated label |

A deterministic contingent plan maps each diagnostic outcome to a labeled
role pair. It cannot reassign the role pair after observing the target clue.
There are 36 plans with no diagnostic and 1,296 with a binary diagnostic.
This class excludes other mappings of clue pairs and public-clue-dependent
role reassignment. Apparent optimality is only within this declared class.

A coordinated mixture draws a complete contingent plan using a common
random device independent of all evidence and Nature's already chosen
regime. Its realization is not disclosed to Nature before Nature's choice.
This common random device is an explicit extra coordination resource, not
an extra clue or action. A deterministic contingent plan already uses any
random variation present in the equally available diagnostic.

Independent departure policies follow the shared clue with probability
`1-epsilon_i` and otherwise select a uniformly random label. Choices are
independent across agents. Rates can depend on the diagnostic. A common
rate and distinct rates are each optimized over the declared five-point
grid, without claiming continuous optimality.

## Objective, cells, comparators, and tie rules

Success requires at least `tau` correct agents. The 18 cells are the Cartesian
product of `rho in {0,1/2,1}`, diagnostic absent/noisy/perfect, and
`tau in {1,2}`. `config.json` lists each cell explicitly.

For every plan, evaluate its regime-conditional success vector. The primary
contrast is best coordinated-mixture worst-regime success minus best
deterministic-contingent worst-regime success. Required secondary comparisons
are the best homogeneous and heterogeneous independent-departure grids,
a nominal optimum assuming A, and expected-success optima under known
regime-A prior probabilities `1/4`, `1/2`, and `3/4`. The known-prior objective
integrates the diagnostic correctly and is kept separate from maximin.

Enumerate roles as `P,S,C,K0,K1,K2`, with agent 1 the outer product coordinate.
Diagnostic order is `none`, or `A,B`. Contingent plan identifiers are their
zero-based product-order index, formatted `d0000`, `d0001`, and so on.
Pure-policy and independent-rate ties use the first declared enumeration.
Rate values increase as in the configuration. A mixed optimum retains the
best pure plan if tied; otherwise the first strictly improving diagonal
intersection encountered on the ordered upper hull is retained. Any
certificate-equivalent maximizer is sufficient for verification; pure and
rate comparators must respect their declared tie rules.

## Evaluation and exactness basis

The primary evaluator factors independent private success conditional on
target and public clue and separately sums the common-private-source
branch. It integrates diagnostic-contingent role assignments exactly. It
then constructs the upper convex hull of the complete finite set of plan
payoff vectors. Pure points and intersections with equal regime value give
candidate maximin optima. A dual regime weight supplies an upper bound for
every deterministic plan, paired with an attaining mixture. These are
standard finite convex-geometric tools, not new theorem claims.

The independent verifier directly enumerates target, public clue, source
branch, private clues, and diagnostic; executes the role actions; and
reconstructs every plan vector. It does not call the primary reward
factorization, plan evaluation, hull optimizer, or departure evaluator.
Its departure check directly enumerates the private randomization devices
and public clue. It checks all dual inequalities and attaining mixed
values without rerunning the hull algorithm.

Both routes share only configuration parsing, rational serialization, and
the declared role identifiers. Shared mathematical assumptions and possible
errors in the model specification are not removed by this independence.

## Prospective checks and stopping rules

Checks cover normalization, probability bounds, agent exchange, target
permutation, the fully independent/shared source limits, one- versus
two-success accounting, known-prior deterministic sufficiency, inclusion of
the homogeneous departure grid in the heterogeneous grid, and inclusion of
both independent grids in the coordinated-mixture class. Perfect diagnosis
must remove the robust-mixture gap within this class.

Adversarial output checks alter a mixture weight, source-branch probability,
diagnostic probability, and dual bound. Verification must reject each.
Focused unit tests may evaluate hand-checkable single cells during
implementation; those are development validation, not primary evidence.

The primary configuration has no random seeds and no sampling uncertainty.
All fractions serialize as `numerator/denominator`, including `0/1` and
`1/1`. A root-run process must enforce 120 seconds and 1024 MiB; the API also
checks elapsed time between cells. An API return does not certify external
resource enforcement or provenance. Stop and preserve failure on a cap,
source/config mismatch, missing policies, invalid comparator accounting,
failed corruption rejection, or unresolved verifier disagreement. There is
one primary sub-run, no result-driven grid expansion, and no replacement run
for an unfavorable or resource-limited result.
