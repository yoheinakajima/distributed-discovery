# Track 05 novelty screen: information externalities and attribution

## Disposition

**Stop for overlap in this initial campaign.** This slot has no admitted
scientific implementation, frozen configuration, primary run, or numerical
claim. The screen was saved before any implementation or primary work for
this track on 2026-10-31. A stopped screen uses one of the six prospective
slots but consumes no primary sub-run.

The motivating idea is that a searcher can benefit later searchers even when
its own discoveries are few, so direct-hit credit may undervalue its work.
Public information externalities, heterogeneous sources of useful
exploration, and counterfactual contribution rewards already have direct
prior art. This screen did not identify an additional scientific mechanism
that justified a separate primary experiment within the current budget.
This is a scoped research decision, not proof that every possible extension
has been studied.

## Search and source limits

Search date: 2026-10-31. The targeted search combined economics, cooperative
bandits, multi-agent learning, and the repository's completed discovery
studies. Queries included `strategic experimentation information public
good`, `counterfactual rewards multiagent exploration`, `difference rewards
policy gradients`, `Exploration for Free reward heterogeneity`, and the exact
titles below. Publisher, proceedings, author, and institutional sources were
preferred. The inspected material included publisher abstracts, proceedings
records, and the full difference-rewards definitions in source 5. The recent
CCL source is an arXiv preprint; its peer-review status is not assumed.

No search result's absence is evidence of novelty. No empirical effect in
these artificial systems establishes a personality or societal-welfare
effect. The candidate policies have not been implemented or evaluated.

## Closest external work

1. **Bolton, Patrick, and Christopher Harris (1999). Strategic
   Experimentation. Econometrica 67(2), 349–374.**
   [Publisher DOI](https://doi.org/10.1111/1468-0262.00022);
   [author-hosted paper](https://business.columbia.edu/sites/default/files-efs/pubfiles/2032/Strategic_Experimentation.pdf).
   Multi-agent experimentation creates public information, generating both
   free-riding and incentives affected by other agents' future learning.
   This is direct prior art for the broad information-externality mechanism,
   although its dynamic bandit environment is not the repository's finite
   atomic-target model. The author PDF was reachable but the browser text
   extraction was unavailable; publisher metadata and abstract were used.

2. **Keller, Godfrey, Sven Rady, and Martin Cripps (2005). Strategic
   Experimentation with Exponential Bandits. Econometrica 73(1), 39–68.**
   [Publisher abstract and bibliographic record](https://doi.org/10.1111/j.1468-0262.2005.00564.x).
   In the registered stationary Markov strategy class, free-riding produces
   inefficient experimentation. Asymmetric equilibria and role switching
   alter the acquisition of public information. More equitable sharing of
   experimentation can improve efficiency. This already makes stable roles,
   symmetric behavior, and rotation relevant comparators; it does not imply
   that permanent behavioral types are required.

3. **Wang, Xuchuang, Lin Yang, Yu-zhen Janice Chen, Xutong Liu, Mohammad
   Hajiesmaili, Don Towsley, and John C. S. Lui (2023). Exploration for Free:
   How Does Reward Heterogeneity Improve Regret in Cooperative Multi-agent
   Bandits? Proceedings of UAI, PMLR 216, 2192–2202.**
   [Original proceedings record](https://proceedings.mlr.press/v216/wang23a.html).
   An action locally optimal for one agent can supply observations useful to
   another agent for whom that action would be costly. The paper gives
   regret bounds and an algorithm exploiting this structure. Merely adding
   heterogeneous rewards and shared observations would reproduce an
   established source of complementary exploration.

4. **Foerster, Jakob, Gregory Farquhar, Triantafyllos Afouras, Nantas
   Nardelli, and Shimon Whiteson (2018). Counterfactual Multi-Agent Policy
   Gradients. Proceedings of AAAI 32(1).**
   [Publisher record](https://doi.org/10.1609/aaai.v32i1.11794);
   [author-hosted paper](https://www.cs.ox.ac.uk/people/shimon.whiteson/pubs/foersteraaai18.pdf).
   COMA assigns credit using a counterfactual baseline for one agent while
   keeping the other agents' actions fixed. A new experiment cannot claim
   counterfactual contribution or replacement-based credit itself as a new
   mechanism.

5. **Castellini, Jacopo, Sam Devlin, Frans A. Oliehoek, and Rahul Savani
   (2025; first published online 2022). Difference rewards policy gradients.
   Neural Computing and Applications 37, 13163–13186.**
   [Publisher full text](https://doi.org/10.1007/s00521-022-07960-5).
   Section 2.3 explicitly defines a difference reward by replacing one
   agent's action with a default action, and describes a policy-marginalized
   alternative. It also notes that choosing the default can be problematic.
   Thus both the replacement-baseline idea and its sensitivity are already
   explicit. A different arbitrary baseline would not establish novelty.

6. **Aydeniz, Ayhan Alp, Robert Loftin, and Kagan Tumer (2026).
   Counterfactual Conditional Likelihood Rewards for Multiagent
   Exploration. arXiv:2602.11740v1, submitted 12 February 2026.**
   [Original preprint record](https://arxiv.org/abs/2602.11740v1).
   The proposed reward targets an agent's unique contribution to joint
   exploration and discounts redundant individual novelty. The reported
   experiments concern continuous multi-agent domains and sparse team
   rewards. This recent, explicitly unreviewed source overlaps the proposed
   attribution-to-informational-value idea especially closely.

## Repository overlap

| Prior study or record | Existing scope | Consequence for this candidate |
| --- | --- | --- |
| [DD-004 report](../../DD-004-sequential-discovery/report.md) | Exact finite perfect-elimination search, alternative batch schedules, terminal success and expected effort | Failed tests do not automatically improve terminal discovery under a fixed perfect-test count. A claimed information benefit must distinguish terminal discovery from effort or timing. |
| [DD-006 model and report](../../DD-006-discovery-mechanisms/model.md) | Observable individual-success and sole-rescue scores; score-difference transfers and exact incentive checks | Relabeling direct hits and marginal contribution as alternative credit rules is not a new discovery question. |
| [DD-006B](../../DD-006B-joint-discovery-mechanisms/README.md) | Joint information, coverage, and obedience incentives under declared observability | Any new incentive claim must be separated from the existing information-score mechanism and its budget/observability boundaries. |
| [DD-015 model](../../DD-015-dynamic-attention/model.md) | Sequential private/shared clues, action-only versus failure-conditioned histories, individual duplicate credit, and a discovery planner | The nearest finite environment already separates individual incentives, public learning, and union discovery. |
| [DD-005 report](../../DD-005-overlapping-coverage/report.md) | Distinct action labels can duplicate coverage; a lower-ranked action can add otherwise missing coverage | A static example in which a lower direct performer makes the portfolio better is already present. |

## Candidate residual questions tested by the screen

### A. Direct-hit credit versus replacement contribution

A concrete candidate would hold team capacity fixed and define an agent's
contribution as the change in team discovery when its policy is replaced by
a registered homogeneous baseline. It would ask whether direct-hit and
replacement-contribution rankings disagree, and whether a composition
selected by direct hits has lower team discovery.

The candidate has a falsifiable local outcome: no ranking reversal or no
selection loss on the frozen domain. However, the comparison is a direct
instance of established difference rewards. The general possibility of
misranking overlapping contributions is also already witnessed by DD-005.
Neither the fixed-capacity control nor relabeling a difference reward as
information credit creates an additional scientific mechanism.

### B. Failure information as the source of the reversal

A more specific candidate would repeat search, alternate action-only and
failure-conditioned public histories, and ask whether a ranking reversal
depends on information supplied by unsuccessful probes. Its negative
control would remove the informative feedback without changing the action
budget. DD-015 already implements the central feedback distinction, while
DD-004 warns that perfect elimination can affect effort without changing
terminal success. No distinct, preregistrable residual was identified that
avoids reproducing these mechanisms plus a known attribution formula.

### C. Heterogeneous incentives as free exploration

A further candidate would give different agents different locally preferred
targets and share their observations. Source 3 already formalizes this
complementarity with regret guarantees. Making the environment smaller or
renaming those preferences as spontaneous and planned behavior would not
be an advance.

## Decision and preserved route

The present slot therefore closes with **overlap**, not an empirical null
and not a failed primary. No scientific code, numerical table, run manifest,
or new claim is warranted for these candidates. This closure follows from
substantive overlap, not from the old editorial-only authorization boundary;
the current owner has authorized scoped synthetic research.

A future pivot within this slot would need a specific additional question
that survives the above reductions, a declared feedback/credit protocol,
and comparison with homogeneous intermediate, adaptive, rotating, and
coordinated policies where meaningful. A useful extension might address a
new identification limitation or implementation constraint, but no such
result is asserted or promised here. Any pivot must be saved before its
implementation and frozen before its primary run. The campaign does not
silently add a seventh track or spend a primary run on a cosmetic restatement.
