# Track 06 novelty screen: reliable execution and downside

## Disposition

**Stop for overlap in this initial campaign.** This slot has no admitted
scientific implementation, frozen configuration, primary run, or numerical
claim. The screen was saved before any implementation or primary work for
this track on 2026-10-31. A stopped screen uses one of the six prospective
slots but consumes no primary sub-run.

Diversifying failure exposure, repeating unreliable actions, and optimizing
downside under uncertain coverage are established research problems. The
screen did not identify a discovery-specific residual that merits a
separate primary experiment under this campaign's initial bounded scope.
This is a scoped overlap judgment, not a statement that reliable discovery
has no open problems.

## Search and source limits

Search date: 2026-10-31. Queries included `correlated failures submodular
coverage`, `Risk-Aware Submodular Optimization for Multirobot Coordination`,
`Failure-Resilient Coverage Maximization With Multiple Robots`, `On
redundancy efficiency and robustness coverage multiple robots`, and
`Planning to Fail reliability multirobot task allocation`. The search
compared primary robotics/reliability/optimization sources with the
repository's explicit Reliable Discovery roadmap.

Publisher abstracts and metadata were checked against author or
institutional records. Source 3's author-hosted accepted manuscript was
also available. Some IEEE full-text pages require browser scripting, and
the Elsevier direct-open request returned HTTP 403; author copies and
publisher-indexed text supplied the bounded summaries below. Source 6 is a
NASA-hosted symposium presentation, not treated as a journal experiment.
This is a targeted novelty screen, not an exhaustive systematic review.

## Closest external work

1. **Hazon, Noam, and Gal A. Kaminka (2008). On redundancy, efficiency,
   and robustness in coverage for multiple robots. Robotics and Autonomous
   Systems 56(12), 1102–1114.**
   [Publisher DOI](https://doi.org/10.1016/j.robot.2008.01.006);
   [author record](https://u.cs.biu.ac.il/~kaminkg/publications/b2hd-ras08.html);
   [author-hosted manuscript](https://u.cs.biu.ac.il/~kaminkg/Publications/papers/ras08.pdf).
   The paper separates redundancy, completion time, and robustness to robot
   failure, with both analytical and empirical comparisons. Duplication can
   improve coverage performance under declared technologies. Thus reducing
   duplication is not a universal measure of improvement, and showing that
   reliability makes some repetition useful is established territory.

2. **Stancliff, Stephen B., John M. Dolan, and A. Trebi-Ollennu (2009).
   Planning to Fail—Reliability Needs to Be Considered a Priori in Multirobot
   Task Allocation. Proceedings of IEEE SMC, 2362–2367.**
   [Institutional original-paper record](https://publications.ri.cmu.edu/planning-to-fail-reliability-needs-to-be-considered-a-priori-in-multirobot-task-allocation).
   The study compares initial plans that account for robot failures and
   backup work with plans that only react after failure. The extra work
   following a failure can change other robots' risks. Consequently,
   adding reliability-aware planning or contingent backup alone would not
   supply a distinct mechanism.

3. **Ishat-E-Rabban, Md., and Pratap Tokekar (2021). Failure-Resilient
   Coverage Maximization With Multiple Robots. IEEE Robotics and Automation
   Letters 6(2), 3894–3901.**
   [Publisher DOI](https://doi.org/10.1109/LRA.2021.3067275);
   [accepted manuscript](https://raaslab.org/pubs/rabban2021failure.pdf);
   [preprint record](https://arxiv.org/abs/2007.02204).
   The declared problem chooses one trajectory per robot to maximize
   coverage after a worst-case subset fails. The paper studies approximation
   algorithms and compares with brute force. A finite robust-coverage
   example under lost agents would therefore need an additional
   discovery-specific question beyond this established objective.

4. **Wilder, Bryan (2018). Risk-Sensitive Submodular Optimization.
   Proceedings of AAAI 32(1).**
   [Publisher record](https://doi.org/10.1609/aaai.v32i1.12121).
   This work optimizes conditional value at risk for continuous submodular
   objectives and obtains related randomized-set guarantees. It includes
   sensor-placement applications. Replacing expected discovery with a
   lower-tail risk objective does not by itself create a new optimization
   concept.

5. **Zhou, Lifeng, and Pratap Tokekar (2022). Risk-Aware Submodular
   Optimization for Multirobot Coordination. IEEE Transactions on Robotics
   38(5), 3064–3084.**
   [Publisher DOI](https://doi.org/10.1109/TRO.2022.3158227);
   [publisher abstract](https://ieeexplore.ieee.org/document/9750919/);
   [author publications record](https://zhourobotics.github.io/publications/).
   The formulation uses CVaR with discrete submodular selection and matroid
   constraints. Applications include sensor selection with failures and
   adaptive replanning. A claim that downside-aware coordinated selection
   beats a risk-ignorant policy would closely overlap this literature.

6. **Jones, Harry W. (2025 presentation; NASA record acquired 2024).
   Common Cause Failures Dominate and Defeat Redundancy. 71st Annual
   Reliability and Maintainability Symposium, 27–30 January 2025.**
   [NASA Technical Reports Server record](https://ntrs.nasa.gov/citations/20240013667).
   The presentation explains the failure floor caused by shared failure
   mechanisms and the value of reducing common exposure. It supplies a
   direct primary institutional statement of the common-cause boundary;
   no empirical rate or peer-reviewed journal status is inferred here.

## Repository overlap and preserved scope

| Prior study or record | Existing scope | Consequence for this candidate |
| --- | --- | --- |
| [DD-005 report](../../DD-005-overlapping-coverage/report.md) | Finite weighted coverage and overlapping action effects | A new label for overlap or action variety cannot be the contribution. Execution failure would change the technology and needs an explicit law. |
| [DD-004 report](../../DD-004-sequential-discovery/report.md) | Perfect execution and elimination, terminal success versus expected effort | Noisy execution is outside that result, but being outside a prior scope is not itself evidence of novelty. |
| [DD-015 model](../../DD-015-dynamic-attention/model.md) | Sequential private information and failure-conditioned decisions under perfect execution | If action failure becomes ambiguous, the posterior and its information set must be changed explicitly; an uninformed baseline would be unfair. |
| [Theorem roadmap](../../../docs/theorem-roadmap.md) | Classical independent-attempt allocation, heterogeneous reliability, correlated failure, repetition, overlap, and confirmation | The simplest proposed reliability grid is already an acknowledged classical baseline or preserved research target. |
| [Reliable Discovery portfolio entry](../../../docs/strategic-direction/optionality-portfolio.yml) | Preserved major candidate with explicit overlap/reliability-baseline requirements | This synthetic campaign does not promote the separate theorem family or promise a paper. The current owner authorization permits a narrow experiment; overlap, rather than historical authorization, motivates this closure. |
| [Existing literature search log](../../../docs/literature/search-log.md) | Hazon and Kaminka already recorded as adjacent robustness/coverage work | This source and its central warning are not newly discovered repository evidence. |

## Classical reductions and candidate questions

### A. Repetition versus breadth under independent failure

For posterior target masses `mu_j`, independent success probability `r_j`
per attempt on target `j`, and `n_j` attempts, the repository already records
the baseline

`G(n) = sum_j mu_j * (1 - (1 - r_j)^n_j)`.

The marginal gain of another attempt is
`mu_j * r_j * (1 - r_j)^n_j`.
This is the pre-existing separable allocation model, not a new DD-024
result. Choosing between exploration and repetition in this model would
restate the tradeoff. Calling one policy spontaneous and the other planned
would add an unsupported psychological interpretation.

### B. Matched marginals, common failure, and apparent diversity

A concrete diagnostic candidate would cross search-action diversity with
failure-domain diversity while keeping every agent's marginal success
probability, evidence, and action budget equal. It would test whether an
apparent fixed-mixture advantage disappears once a homogeneous policy can
use the same distribution over failure domains.

This has a falsifiable finite-model comparison, but the motivating effect
is classical common-cause reliability. If the generalist can reproduce the
same joint action and failure-domain distribution, equality follows from
the model's construction. If it cannot, the restriction must have a
substantive basis independent of a desired mixture advantage. No such
additional restriction was justified by this screen. Running the obvious
crossed grid would illustrate a known confound rather than resolve a new
discovery mechanism.

### C. Downside constraints and failed-action ambiguity

A CVaR or worst-case coverage variant overlaps sources 3–5. A sequential
variant in which an unsuccessful test could mean either a wrong target or
an execution fault would require an explicitly latent failure process and
a Bayes-correct adaptive comparator. Comparing a reliability-aware mixture
against a generalist that incorrectly treats all failures as elimination
would manufacture an advantage through model misspecification. No precise
nonoverlapping question was identified that justifies that additional
model, posterior, and verification burden in this initial campaign.

## Decision and preserved route

This slot closes with **overlap**, not a numerical null and not a failed
primary. There is no scientific code, result table, run manifest, or new
claim for this track. The broad reliability family remains scientifically
interesting, but the campaign does not consume a run merely because a
candidate can be parameterized.

A later pivot within this slot would need to specify the failure law,
available diagnostics, shared exposure, repetition technology, objective,
and fair comparator information before implementation. Its contribution
would have to survive the classical allocation, common-cause, robust
coverage, and risk-sensitive optimization reductions above. It must not
equate behavioral difference with fault independence or imply any result
about human reliability or welfare. No theorem-family promotion, seventh
track, or extra primary run follows from this preserved route.
