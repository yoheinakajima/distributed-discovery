# Track 02 novelty screen: unreliable evidence and random departures

## Record and disposition

- Study: DD-024; authority: AO-0018.
- Search and assessment date: **2026-10-31 UTC**.
- Status: **pivot for coordinator review**. Close the broad novelty claim
  that random behavior protects teams against model error. The narrower
  candidate is an exact finite interaction audit of evidence dependence,
  latent reliability, and discovery thresholds.
- Scientific implementation and primary execution: **none**.
- The configuration below is a **proposal**, not a completed freeze or an
  experimental result. Root admission, implementation, validation, source
  freeze, and the campaign's run gates remain necessary.

The potentially useful output is a matched-budget comparison in one small
discovery game: when an extra randomization device improves a worst-regime
objective, does independent departure from shared evidence obtain the same
benefit as coordinated randomization or reliable diagnostic adaptation?
The existence of a randomization benefit in robust optimization is already
established. This screen offers no global novelty guarantee and does not
propose a new minimax theorem.

## Search record

The following reproducible queries were issued on the date above, followed
by checks of primary-publisher, author, and university records:

```text
Eyster Rabin 2010 naive herding rich information settings Econometrica DOI
Enke Zimmermann 2019 correlation neglect belief formation review economic studies DOI
robust teams randomized strategies uncertainty decentralized decision making common payoff minimax randomization
distributionally robust team decision problems randomized policies correlation information uncertainty
"The Value of Randomized Solutions" "Delage" "Saif" 333 353
"robust team decision-making under uncertainty" 2010 Gulpinar Canakoglu Thoms
"The Value of Randomized Solutions in Mixed-Integer Distributionally Robust Optimization Problems"
"Naïve Herding in Rich-Information Settings"
"Correlation Neglect in Belief Formation"
"Robust team decision-making under uncertainty"
```

The first query's guessed journal was wrong; the retrieved Eyster–Rabin
article is in *American Economic Journal: Microeconomics*. This record
preserves the query as issued without repeating its bibliographic mistake.
The stored [landscape review](../../../../docs/literature/spontaneity-exploration-planning/review.md)
provides additional coordination/noise context; it is not a systematic
novelty certificate.

## Four closest external sources

| Source | What it studies or establishes | Exact overlap and boundary |
| --- | --- | --- |
| Erik Eyster and Matthew Rabin (2010), *Naïve Herding in Rich-Information Settings*, American Economic Journal: Microeconomics 2(4):221–243. [DOI](https://doi.org/10.1257/mic.2.4.221); [author full text](https://scholar.harvard.edu/files/rabin/files/naiveherdingpublished.pdf) | Agents who treat earlier actions as independent expressions of private information can double-count early evidence and become confidently wrong; observing others can hurt under that belief error. | Misspecified dependence and harmful information aggregation are established. The paper does not establish that undirected noise is the best remedy or evaluate this finite discovery team's threshold objective. |
| Benjamin Enke and Florian Zimmermann (2019; online 2017), *Correlation Neglect in Belief Formation*, Review of Economic Studies 86(1):313–332. [DOI](https://doi.org/10.1093/restud/rdx081); [publisher record](https://academic.oup.com/restud/article-abstract/86/1/313/4772809) | Experiments find double-counting of correlated information, heterogeneous bias, and substantial effects of directing attention to dependence and underlying independent signals. | The human premise for correlation neglect is supported independently of this synthetic model. Correcting interpretation is a serious comparator to random departures. The proposed experiment would not estimate this bias or identify human personality types. |
| Erick Delage and Ahmed Saif (2022 issue; online 2021), *The Value of Randomized Solutions in Mixed-Integer Distributionally Robust Optimization Problems*, INFORMS Journal on Computing 34(1):333–353. [DOI](https://doi.org/10.1287/ijoc.2020.1042); [author manuscript](https://tintin.hec.ca/pages/erick.delage/ValueOfRandomization.pdf) | Studies the value of randomization in nonconvex distributionally robust optimization, derives bounds, and supplies algorithms and applications. | Convexifying discrete decisions with a randomization device to improve a worst-case objective is already established. Any positive robust-randomization gap below is an instance of this mechanism, not its discovery. |
| Nalan Gulpinar, Ethem Canakoglu, and Jo Thoms (2010), *Robust team decision-making under uncertainty*, International Journal of Applied Decision Sciences 3(3):206–220. [DOI](https://doi.org/10.1504/IJADS.2010.036099); [university record](https://wrap.warwick.ac.uk/id/eprint/67998/) | Uses robust optimization for centralized team task assignment when success probabilities are uncertain, and compares efficiency with robustness. | Team robustness under uncertain probabilities is already a direct research topic. The candidate differs by putting uncertainty in the shared/private evidence law and explicitly distinguishing private random departures, coordinated mixtures, and threshold success. The primary abstract was checked; full journal access was restricted. |

## Repository overlap and proposed residual

- [DD-001](../../../DD-001-private-information-teams/report.md) establishes
  deterministic sufficiency for the finite known-model common-payoff
  optimum. A randomized team is a mixture over deterministic team plans;
  it cannot exceed their maximum expected value under a fixed prior. This
  rules out presenting ordinary expected-payoff randomization as new.
- [DD-003](../../../DD-003-source-networks/report.md) already shows why
  dependence structure and source accuracy must be specified rather than
  replaced by a single agreement statistic. The candidate must not claim
  to discover that correlated evidence can reduce effective coverage.
- [DD-014](../../../DD-014-conditional-attention/report.md) already
  evaluates private/public/contrarian roles and preserves a counterexample
  to extending a restricted-policy result to unrestricted policies. Its
  lesson directly applies to the six-role library proposed here.
- [DD-015](../../../DD-015-dynamic-attention/report.md) and
  [DD-016](../../../DD-016-threshold-discovery/report.md) already evaluate
  adaptation and threshold discovery. Neither threshold success nor the
  usefulness of conditional roles is a novelty claim by itself.
- The candidate is about **evidence reliability**, not physical execution
  failures after an action. It does not reopen the rejected generic
  reliability/CVaR experiment or an old execution-failure gate.

No identical combination was located in this bounded search: an exact
restricted-role policy audit with two ambiguous source-reliability regimes,
controlled private-source dependence, an equally available reliability
diagnostic, and both one-success and two-success objectives. That absence
is provisional. The residual contribution would be the quantified
interaction and the comparator audit, not a general advantage of
randomness, heterogeneity, or robustness.

## Proposed model and configuration for review

### State, evidence, and timing

There are three target labels and two labeled agents. The target is uniform.
Before observations or any policy randomization, Nature selects one latent
regime `R in {A,B}`. The robust objective evaluates each possible regime,
rather than pretending to know a prior over them.

| Parameter | Regime A | Regime B |
| --- | --- | --- |
| Private clue accuracy `p_R` | `1/3` | `5/6` |
| Shared clue accuracy `q_R` | `5/6` | `1/3` |

All channels are symmetric: each incorrect label has probability
`(1-accuracy)/2`. One public clue `Y` is generated. For the private clues,
with probability `rho`, a single private source is drawn and both agents
receive its value; otherwise two private sources are drawn independently.
The branch and the public source are independent conditional on target and
regime. `rho` is a mixture weight in this specified law, not an asserted
Pearson correlation coefficient.

Before target clues arrive, both agents receive the same reliability
diagnostic. Its frozen modes would be:

- `none`: a single uninformative symbol, providing no random coin;
- `noisy`: a binary label equal to `R` with probability `3/4`;
- `perfect`: a binary label equal to `R` with probability one.

The diagnostic is independent of the target and target clues conditional
on `R`. Both agents see the same diagnostic, public clue, and their own
private clue. No private clue is pooled. Every policy class makes exactly
two actions; no reliability diagnosis consumes an extra search action.
The diagnostic is an explicitly free evidence input in this synthetic
comparison, not an assumed free intervention in a real application.

The diagnostic arrives first and may select an assigned role profile. Each
role then maps the subsequent target clues to an action. Role assignment
cannot additionally depend on the realized public target clue beyond the
role's prescribed mapping. This restriction is essential to the finite
class and is not a statement about all feasible team strategies.

### Declared role repertoire

Each agent may use one of six deterministic maps:

- `P`: follow its private clue;
- `S`: follow the shared clue;
- `C`: if the clues agree, follow them; if they disagree, select the third
  label;
- `K0`, `K1`, `K2`: always select the indicated label.

There are `6^2 = 36` labeled profiles. A deterministic contingent team
chooses a profile for each diagnostic outcome: 36 plans with no diagnostic
and `36^2 = 1296` with a binary diagnostic. All such plans would be
enumerated. These are complete optima **within the stated library and
timing**, not unrestricted optima over all functions of `(private,public)`
clues.

Success means at least `tau` agents select the true target. Freeze
`rho in {0,1/2,1}`, the three diagnostic modes above, and `tau in {1,2}`:
**18 cells**. These are finite expectations, so the proposed uncertainty
method is exact rational arithmetic, with no Monte Carlo seeds or sampling
intervals. One primary sub-run would have a hard limit of **120 seconds and
1024 MiB**. No expansion after seeing results is proposed.

## Estimands and counterfactual comparators

For a complete contingent team plan `d`, evaluate its actual policy-induced
success vector `(V_A(d), V_B(d))`. The primary quantity would be

\[
G = \max_w\min_{R\in\{A,B\}}\sum_d w_d V_R(d)
    - \max_d\min_{R\in\{A,B\}} V_R(d).
\]

The mixture uses a common random device drawn after Nature chooses the
regime; its realized draw is not revealed to Nature before that choice.
This is a coordinated randomization resource. It is not interchangeable
with independently noisy people, and it is labeled as a coordination
benchmark even though its evidence and action counts match the other
classes.

Required comparison rows would be:

1. **Best deterministic contingent maximin plan.** It uses the diagnostic,
   the complete 36-profile library, and the same action budget. Any random
   variation supplied by the diagnostic is already available to this
   baseline; deterministic means conditional on observations, not a
   nonrandom realized action.
2. **Best coordinated mixture of those contingent plans.** This defines
   the first term above and upper-bounds the independent role-randomization
   baselines within the same library.
3. **Nominal plan assuming regime A.** Optimize expected success under A,
   retain a deterministic lexicographic tie rule, and evaluate the resulting
   plan under both regimes. This is a declared misspecification benchmark,
   not a model of a particular human bias.
4. **Known-prior optimal plans.** Use fixed regime-A probabilities
   `{1/4,1/2,3/4}`, updating with the diagnostic. Their weighted objectives
   are expected-value comparisons and must remain separate from maximin
   value. Deterministic sufficiency is an accounting/control check here.
5. **Independent public-following departures.** Each agent follows `S` with
   probability `1-epsilon` and otherwise draws uniformly from the three
   constant maps. Compare the grid `epsilon in {0,1/4,1/2,3/4,1}` for a
   common rate and separate agent rates, allowing rates to depend on the
   diagnostic. Draws are independent across agents and independent of
   evidence conditional on the diagnostic. This is an explicitly bounded
   heuristic grid, not an optimum over all continuous independent mixtures.

Report all regime-specific success probabilities, worst-regime value,
known-prior values, selected profiles, mixture supports/weights, and the
diagnostic used. Primary contrasts would show how `G` and the departure
baselines change with `rho`, `tau`, and diagnostic quality. A positive
`G` supports only the finite maximin comparison; a benefit over public
following alone does not establish a benefit over the strong deterministic
or calibrated baseline.

## Classical reductions, confounds, and falsifiers

- **Known-prior purification remains intact.** If an implementation reports
  that a mixture beats the best deterministic plan for the same fixed
  expected-value objective, it is wrong or has mismatched feasible classes.
- **Minimax convexification is established.** With two regimes, payoff
  vectors lie in two dimensions. The mixed problem reduces to the upper
  convex hull and a one-dimensional adversarial-prior certificate. A
  positive gap by itself is classical robust optimization, not novel
  evidence that noise is socially beneficial.
- **Timing is substantive.** An adversary that observes the realized coin
  before selecting a regime gives a different problem and removes the
  intended insurance interpretation. The proposed timing must be immutable.
- **Environmental signals can randomize behavior.** A noisy public
  diagnostic already supplies common randomness. The strong deterministic
  contingent baseline receives it too; no claim may credit an added coin
  with benefits already obtainable by conditioning on observed signals.
- **The role library is restrictive.** More general policies could use the
  public target label to choose among role profiles or exploit different
  clue-pair mappings. A positive gap does not prove a gap for those larger
  classes. If the desired conclusion needs that extrapolation, close this
  design rather than adding policies after viewing its result.
- **Dependence and threshold effects are not new alone.** Any apparent
  contribution that merely reproduces DD-003 or DD-016 must be reported as
  overlap. The interaction is the only proposed empirical output.
- **A perfect diagnostic is a calibration comparator.** Remaining value
  assigned to ambiguous-regime insurance in that mode must be checked
  carefully against the ability to choose a regime-specific pure optimum.
- **Nulls are substantive.** If independent departures add no value beyond
  a deterministic mixed-role team, or if calibration removes the apparent
  advantage, report that result. No favorable sign is an admission or
  completion requirement.

## Actual evaluation and independent verification proposal

The primary path would compute success probabilities from the specified
source law and the actions of each role. It would enumerate all permitted
contingent plans, build the exact two-dimensional upper hull, and evaluate
its candidate maximin points. It would save every plan's payoff vector and
an attaining mixed policy. With two regime constraints, a support of at
most two plans is sufficient for an optimal hull point; this is a standard
finite convex-geometric reduction, not a novel theorem claim.

The verifier would not import the primary probability evaluator or hull
routine. It would directly enumerate target, public clue, private-source
branch, private clues, and diagnostic values; execute each saved plan's
maps; and reconstruct its vector using rational probabilities. For the
mixed optimum, it would verify a dual certificate: a regime-A weight
`lambda in [0,1]` such that every admissible deterministic plan has weighted
value at most the claimed bound, together with a feasible attaining mixture
whose two regime values meet the claimed lower bound. Pure-plan maxima
would be checked against the complete independently reconstructed list.

Required limits and invariances include probability mass, payoffs in
`[0,1]`, the independent-source and fully shared-source endpoints, perfect
diagnosis, target relabeling, agent exchange, and the difference between
one-success and two-success accounting. Prescribed corruptions would alter
a mixture weight/normalization, a source-branch probability, a diagnostic
probability, and a claimed bound; each must be rejected by a relevant
independent check. Shared frozen assumptions and policy identifiers are
unavoidable dependencies and would be disclosed.

No evaluator may use TreasureBench's stored `expected_metrics` as outcomes.
Stop on source/config mismatch, an invalid comparator budget, a resource
limit, failed corruption rejection, or verifier disagreement. Preserve the
attempt rather than rerunning toward a preferred result.

## Admission recommendation and claim boundary

**Conditional pivot:** admit only if the coordinator accepts a bounded
benchmark interaction audit as the contribution. The primary literature
already explains robust randomization and harmful correlation neglect; this
track cannot honestly promise a new general mechanism. If the admission
standard requires an original general proposition rather than a new exact
comparison in this discovery model, record **close-overlap** without a run.

Even a passing run would concern synthetic policies and success
probabilities in 18 registered cells. It would not establish benefits of
chaotic personalities, a socially optimal proportion of spontaneous people,
superiority of independent noise to deliberate adaptation, or human/social
welfare effects. Root review of this file is the next step; implementation
and primary execution have not started.
