# Track 01 novelty screen: persistent roles, rotation, and adaptation

## Record and disposition

- Study: DD-024; authority: AO-0018.
- Search and assessment date: **2026-10-31 UTC**.
- Status: **close-overlap for the original scientific proposal**. The finite
  attribution design below is recorded for review, but is **not an admitted
  primary configuration**.
- Scientific implementation and primary execution: **none**.
- Question screened: do permanent behavioral specialists improve discovery
  beyond equally informed rotating or adaptive generalists when changing
  roles incurs a cost?

The general specialization/switching-cost mechanism is established prior
art. More decisively, the simplest extension of the repository's model makes
two proposed comparisons analytical consequences of the design: unrestricted
adaptive teams can retain any fixed assignment, and swapping prescriptions
between identical agents preserves discovery while adding the prescribed
switching penalty. A numerical demonstration of either fact would not be a
new finding. No global novelty guarantee is claimed, and failure to find a
matching paper would not remove these reductions.

## Search record

Primary-publisher, author, and university records were searched and checked
with the following reproducible query strings. Search results are a dated
landscape screen, not an exhaustive systematic-review certificate.

```text
multi agent task allocation specialization switching costs exploration exploitation division labor adaptive generalists academic
exploration exploitation heterogeneous agents homogeneous switching costs specialization social learning paper
multi armed bandit switching costs team diversity specialization Gittins task switching
"Adaptable and stable decentralized task allocation" authors doi
"Heterogeneous Explore-Exploit Strategies on Multi-Star Networks" authors 2021
"A Normative Account of Specialization" authors
"Evolution of self-organized division of labor" "switching"
"Evolution of self-organized division of labor in a response threshold model" switching costs
"Strategic Experimentation with Exponential Bandits" role switching
"A normative account of specialization" "6431"
```

The stored [interdisciplinary review](../../../../docs/literature/spontaneity-exploration-planning/review.md)
supplies broader context. This screen concentrates on the closest mechanisms
rather than counting every related exploration/exploitation paper.

## Five closest external sources

| Source | What it already establishes or studies | Exact overlap and remaining distinction |
| --- | --- | --- |
| Ana Duarte, Ido Pen, Laurent Keller, and Franz J. Weissing (2012), *Evolution of self-organized division of labor in a response threshold model*, Behavioral Ecology and Sociobiology 66:947–957. [DOI](https://doi.org/10.1007/s00265-012-1343-2); [open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3353103/) | Evolving response thresholds can produce specialization; switching costs and the fitness components being selected materially affect the result. The model also identifies limitations of threshold-based task allocation. | Costly switching as a reason for persistent role differentiation is already explicit. This is an evolutionary colony model, whereas the rejected candidate below is a finite common-payoff team with prescribed policies. |
| Vera A. Kazakova and Gita R. Sukthankar (2020), *Adaptable and stable decentralized task allocation for hierarchical domains*, The Knowledge Engineering Review 35:e26. [DOI](https://doi.org/10.1017/S0269888920000235); [author PDF](https://ial.eecs.ucf.edu/pdf/Sukthankar-KER2020.pdf) | Reinforced response thresholds support specialization and subsequent respecialization when demands change in noncommunicating patrol teams; the study explicitly seeks to reduce wasteful task switching. | Stable versus adaptive specialization under changing demand is already the central question. A new small exact search game would change the environment and method, not originate this mechanism. The indexed primary abstract was inspected; the full PDF could not be fetched by the browser because of its size. |
| Udari Madhushani and Naomi Ehrich Leonard (2021; online 2020), *Heterogeneous Explore-Exploit Strategies on Multi-Star Networks*, IEEE Control Systems Letters 5(5):1603–1608. [DOI](https://doi.org/10.1109/LCSYS.2020.3042459); [author full text](https://naomi.princeton.edu/wp-content/uploads/sites/744/2021/10/MadLeoLCSS2021.pdf) | A heterogeneous exploration rule makes central agents gather information useful to peripheral agents; regret analysis and simulations compare it with a homogeneous rule in the specified distributed bandit model. | Collective gains from differentiated exploratory roles are already studied. Network positions and information access differ in that paper; they would be held equal here. Its comparison does not establish that fixed types beat every adaptive policy. |
| Godfrey Keller, Sven Rady, and Martin Cripps (2005), *Strategic Experimentation with Exponential Bandits*, Econometrica 73(1):39–68. [DOI](https://doi.org/10.1111/j.1468-0262.2005.00564.x); [primary working-paper record](https://www.economics.ox.ac.uk/publication/930544/ora-hyrax) | Strategic experimentation distinguishes symmetric and asymmetric equilibria, the sharing of experimentation burdens, and finite versus arbitrarily frequent role switching. | Fixed versus rotating experimental roles and aggregate information benefits are established topics. The incentives, continuous time, and publicly accumulated learning differ from the common-payoff, fresh-target candidate. Journal and working-paper abstracts were checked; this screen does not claim a full derivation audit. |
| Elizabeth Mieczkowski, Ruaridh Mon-Williams, Neil Bramley, Christopher Lucas, Natalia Vélez, and Tom Griffiths (2025), *A normative account of specialization: How task and environment shape role differentiation in collaboration*. CogSci 2025, p. 6431. [Proceedings record](https://escholarship.org/uc/item/7nh7c08d); [university record](https://www.research.ed.ac.uk/en/publications/a-normative-account-of-specialization-how-task-and-environment-sh/) | Reports three Overcooked-AI experiments connecting specialization with limits to parallel execution and learning demands, including specialization when generalists could theoretically be more efficient. | The specialist/generalist comparison and its dependence on task structure are already explicit. This is a **one-page peer-reviewed conference abstract**, so it is a prior-art signal rather than a fully inspected experimental report. |

## Repository overlap

- [DD-001 report](../../../DD-001-private-information-teams/report.md)
  already optimizes deterministic private-information teams, identifies
  useful heterogeneous/hybrid profiles, and records why ex-ante
  randomization cannot improve the optimum for a known finite common-payoff
  model. Its exact two-agent envelope and hybrid roles cannot be renamed a
  new specialization result.
- [DD-015 model](../../../DD-015-dynamic-attention/model.md) and
  [report](../../../DD-015-dynamic-attention/report.md) already use exact
  adaptive policy optimization and a separate planner benchmark. The
  proposed public Markov accuracy state and prescription-switching penalty
  would be additional assumptions, not a new dynamic-programming method.
- The existing scientific entry point for a one-round private team is
  `src/distributed_discovery/private_teams/model.py::evaluate_formula`;
  `evaluate_direct` enumerates target and private-signal outcomes. Existing
  tests and certificates demonstrate the desired formula/direct-enumeration
  verification pattern.
- The TreasureBench golden-vector evaluator is not a simulator for this
  proposal. Returning `expected_metrics` would supply no scientific
  evidence.

## Analytical screen before any experiment

Let a prescription be a complete map from a private clue to an action, and
let both agents have the same clue accuracy and action repertoire. Three
reductions decide the broad proposal:

1. **Adaptive containment.** If an adaptive team has the same information,
   capabilities, and switching charges as a stable team, it can choose the
   stable team's prescriptions at every date. Therefore its optimized value
   cannot be lower. A strict advantage of stable specialists would reveal an
   excluded option, unequal cost, restricted learning algorithm, or a bug.
2. **Rotation invariance.** With exchangeable agents, independent fresh
   targets, and no agent-specific learning stock, a profile `(f,g)` and
   `(g,f)` have the same period discovery probability. Forced identity
   rotation changes only the switching charge. For distinct fixed maps over
   three periods it incurs four agent-prescription changes. Calling that
   difference a discovered benefit of personality diversity would be
   misleading.
3. **Static reduction.** With constant signal accuracy and nonnegative
   switching cost, repeating an optimal one-round profile is optimal for
   the labeled adaptive class: there is no payoff-relevant information or
   capability to accumulate. The one-round optimization is already DD-001.

These are design checks, not new theorem claims or requested proof-status
promotions. They are reasons to stop an overlapping experiment before
spending a primary run.

## Screened finite design, retained to make the decision reviewable

This design is a possible **diagnostic illustration only**. It is not frozen
or authorized for primary execution by this file. If the coordinator wants
its quantitative attribution map despite the overlap, that narrower purpose
must be recorded explicitly before implementation and freeze.

| Item | Proposed value |
| --- | --- |
| Agents / targets / horizon | 2 / 3 / 3 periods |
| Target law | A new independent uniform target each period |
| Public regime | `L` or `H`, initially uniform; Markov probability of staying `s` |
| Private clues | Conditionally independent symmetric channels; correctness `p_z`, each wrong label probability `(1-p_z)/2` |
| Prescriptions | All `3^3 = 27` deterministic maps per agent; `729` labeled pairs |
| Timing | Observe public regime, assign prescriptions, draw private clues, act; no pooling of private clues |
| Cost | `c` per agent whose complete prescription changes from the preceding period; initial assignment free |
| Main grid | `(p_L,p_H)=(1/3,2/3)`, `s in {0,1/2,1}`, `c in {0,1/12,1/3}`: 9 cells |
| Stationary controls | `(p_L,p_H)` equal to `(1/3,1/3)` or `(2/3,2/3)`, `s=1/2`, the same three costs: 6 cells |
| Objective | Expected sum of discoveries minus prescription-switching charges; also report gross discovery and expected switches separately |
| Total | 15 exact cells, no Monte Carlo and no random seed |
| Proposed cap | One primary sub-run, 120 seconds, 1024 MiB, only if a later admission/freeze occurs |

Changing a prescription is not the same as changing the realized action.
A stable clue-following policy can select different labels in successive
periods without paying this role-change cost. This assumption must be stated
wherever outputs are interpreted.

### Strong comparators and possible estimands

All classes receive the same public regime and private clues and make two
actions per period. Initial fixed designs are selected after observing the
initial regime, so the adaptive class has no initial-information advantage.

- Best stable homogeneous pair `(f,f)` over all 27 maps.
- Best stable labeled pair over all 729 profiles.
- Best alternating pair, swapping agent identities each period, with the
  initial pair selected over the same 729 profiles.
- Best adaptive homogeneous pair, using public regime and previous map.
- Best adaptive labeled pair, using public regime and previous pair. This
  is the strongest comparator under the same evidence and prescription
  repertoire, not a planner that sees other agents' private clues.
- A declared intermediate-policy grid: independently draw each agent's
  prescription from identity with weight `1-epsilon` and the three constant
  maps with weight `epsilon/3`; `epsilon in {0,1/4,1/2,3/4,1}`. Compare a fixed
  epsilon and a regime-contingent pair of epsilons. Charge changes in the
  realized prescription. This is a bounded baseline grid, not an optimum
  over all stochastic policies.

Candidate quantities would be the stable heterogeneous-minus-homogeneous
gap, the adaptive-minus-stable gap, and gross discovery versus switching
expenditure. The persistence-minus-forced-rotation difference is an
accounting control, not a novelty claim. A finite quantitative map of these
gaps would be new output in this repository; the mechanisms and dominance
directions would not be new scientific discoveries.

## Evaluation and independent verification if the diagnostic is admitted

The proposed primary evaluator would calculate actual prescribed actions and
exact rational discovery rewards, then solve the finite dynamic program.
The per-agent Hamming switching charge permits separable max-plus updates
over the two prescription coordinates; this avoids a needlessly expensive
all-pairs transition search. No fitted expected-metric table would be used.

A separate verifier would independently enumerate every one-period target
and clue tuple, check all stored Bellman inequalities and the attaining
action at each state, and enumerate the selected policy along complete
public-regime paths. It would share the frozen model/configuration but not
import the primary reward evaluator or optimizer. Gross discovery and
switches would be reconstructed separately before computing net value.

Required checks would include probability mass, label and agent permutation,
zero cost, constant-regime limits, adaptive containment, fixed/rotating gross
reward equality, gross discovery in `[0,3]`, and switches in `[0,4]`.
Corruptions would change a reward numerator, a switching count, and a
selected Bellman action/value; each must fail its relevant check. Resource
stops, mismatches, or incomplete certificates would remain failures, not
reasons to rerun or expand the grid.

## Decision and promotion boundary

**Close the original proposal for overlap without a primary run.** The
listed sources already cover specialization, changing demand, and switching
costs; the simplest canonical-model extension adds comparisons whose signs
are fixed by containment or accounting. An additional agent-specific
learning state, unequal capabilities, or a restricted controller could
change that conclusion, but each would require its own fresh novelty screen
and fair-comparator rationale. Such additions are not silently admitted
here.

The retained design makes a possible educational or benchmark audit
concrete. Its admission would require the narrower purpose to be explicit;
it could not support claims that persistent human types are necessary,
that planning/spontaneity is measured by these maps, or that social welfare
has been evaluated.
