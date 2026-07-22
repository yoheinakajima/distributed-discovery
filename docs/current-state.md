# Current program state

_Reconciled 2026-07-22 for DD-020 public integration and final acceptance._

Programs V1, V2, and the required Program V3 queue are complete at their
registered bounded scopes. Program V3, *The Incentive to Ignore*, completed
DD-012 through DD-014, the focused working paper, versioned attention
extensions to DiscoveryBench and the synthetic experiment kit, and the public
Attention/Audience/Conditional Labs.

Program V4 is complete at its registered bounded scope. DD-016 proves the
deterministic minimum-viable-team planner value, derives the threshold
split-prize payoff identities, and records an independently reproduced exact
threshold and occupancy census. DD-017 is
complete and characterizes the bounded pure-Nash occupancy correspondence,
small-coalition stability, and one symmetric tied-mode mixture without
identifying that selected rule with all equilibria. DD-015 is complete and
deployed at its bounded dynamic-attention and separately labeled planner-only
threshold-two scopes. DD-018 is complete and deployed at its bounded
common-posterior mechanism scope. DiscoveryBench v3 and Synthetic Experiment
v3 are complete and deployed with all earlier versions preserved. Every
synthetic calibration failure remains public, and no human experiment exists.
The focused *Threshold Discovery* paper is deployed as a 20-page,
byte-reproducible artifact with eight generated assets and all-page visual QA.
Four output-connected Program V4 Labs are deployed through PR #125:
threshold, equilibrium selection, dynamic attention, and team mechanisms. They
select exact immutable-run rows and preserve complete no-JavaScript tables.
The focused paper deployed through PR #123. Issue #126 records the separate
documentation-only final acceptance and creates no research evidence.

Program V5, *The Information Sharing Frontier*, completed its documentation
baseline through PR #129. DD-019's bounded `M=4`, `N=3` primary run passes from
clean source commit `a77bb786`; labeled and histogram methods agree on all five
channel profiles, and three corruptions are rejected. Claims DD-C-0089 through
DD-C-0091 are independently reproduced exact bounded computational results.
PR #131, post-merge CI `29905840583`, Pages `29905840831`, and the live study,
data, claims, evidence, and registry routes pass.
Deployment closeout PR #132 merged as `5e6c800`. Governance/publication PR
#134 then merged as `dc32ff17`, with post-merge CI `29927131835` and Pages
`29927132030` passing. DD-020 Incremental Sharing and Independent Rescue
merged through PR #136 as `cf7bc67e`, with post-merge CI `29929864642` and
Pages `29929864954` passing. Its clean run
`20260722T142551Z_DD-020_3854fff6_37c11a850a` supports DD-C-0092 through
DD-C-0096, and the live study, claim, evidence, and data routes pass. The
documentation-only editorial gate assigns primary ownership to a future
Information Sharing Frontier paper; it creates no claim, run, PDF, or
submission action. The output-connected Incremental Sharing Lab consumes only
the immutable DD-020 point census and five-channel profiles. It exposes 2,044
point transitions and ten channel transitions, including the same-accuracy
opposite-sign comparison, without recomputing the study.

The repository is public and project-authored content is MIT-licensed. The
canonical Shared Discovery Paradox repository remains pinned at
`5025cc8e8f2f8ca015dff2066f08f81ad5715a51`, separate, clean, and read-only.

| Measure | Current value |
| --- | ---: |
| Ledger claims | 96 |
| Passing immutable runs | 46 of 49 manifests |
| Registered studies | 24 |
| Python source files | 142 |
| Public HTML routes | 72 locally generated |
| Public data files | 71 |
| Laboratory routes | 17 |
| Validated project papers | 6 |
| Checksum-registered downloads | 22 |
| Test suite | 224 collected tests |

## Program V5 exact result

DD-020 proves for the registered point channel that
`G_s=1-(1-C_s)(1-p)^(N-s)` and that `G_(s+1)<=G_s`, strictly for `p<1`.
Its 2,555-row exact census has 1,848 negative increments, 196 perfect-signal
ties, and no positives. In the five-channel extension, the half-accurate noisy
point falls `(7/8,3/4,7/12)` while the half-accurate guaranteed shortlist rises
`(7/8,11/12,17/18)`, so one-person accuracy does not determine this profile or
its sign.

- DD-020: `20260722T142551Z_DD-020_3854fff6_37c11a850a`,
  DD-C-0092–0096.

DD-019 compares five declared finite channels at `M=4`, `N=3`. The exact
pooled profiles `(V1,V2,V3)` are `(7/12,43/54,25/27)` for the half-accurate
noisy point and `(17/18,1,1)` for the guaranteed two-shortlist. Both have
one-person Bayes accuracy `1/2` and direct private-portfolio discovery `7/8`,
so one-person accuracy does not determine the complete bounded profile. Their
recovery budgets are respectively three and one. Across all five channels the
recovery budgets are `3,2,1,2,3` in registry order.

- DD-019: `20260722T084145Z_DD-019_a77bb786_04a5e9f0c5`,
  DD-C-0089–0091.

## Program V4 exact result

DD-016's deterministic planner opens the top
`min(floor(N/tau),M)` posterior candidates with minimum-size teams. In the
canonical tau-two fixture, exact discovery is
`37916217637/98876953125` for a common deterministic mode,
`275661897594857/576650390625000` under the registered independent tied-mode
selection, `194017/390625` under private clue-following, and
`223779310319051/333709716796875` for the paired planner. Both exact state
representations agree across all eight threshold rows.

Primary run:

- DD-016: `20260722T021526Z_DD-016_00271ff8_123b2809e3`, DD-C-0071–0074.

DD-017 characterizes weak pure Nash occupancies and proves that uniform mixing
over posterior modes is a symmetric equilibrium for every `tau>=2`, while at
tau one an outside candidate can be profitable. Its 160-game exact registry
contains 52 games with zero worst-equilibrium discovery, eight without a
pairwise-strict-stable pure equilibrium, and 35 without an exact-size-tau-
strict-stable pure equilibrium. All 21 tied-mode failures occur at tau one.

- DD-017: `20260722T024032Z_DD-017_033452f6_3d2c74fdfb`, DD-C-0075–0078.

DD-015 separates full-duplicate-credit sequential Bayesian behavior from an
exact common-information planner under fixed-budget and stopping objectives.
The planner is strictly better in 38 of 64 baseline objective rows. Visible
prior action never improves discovery or dispersion relative to the registered
history-hidden Bayes control; it reduces both in 18 of 32 fixed-budget cells
and ties in 14, a bounded negative result rather than a general theorem.
Stopping uses fewer expected actions in all 32 cells. The separate threshold-
two planner extension preserves discovery and reduces expected actions in all
16 fixed/stopping cells while exercising every registered team-action category.

- DD-015 baseline: `20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a`,
  DD-C-0079–0081.
- DD-015 threshold-two extension:
  `20260722T044453Z_DD-015_34bc4379_33e1da478b`, DD-C-0082.

DD-018 compares ten common-posterior team institutions across five exact
`M=3`, `N=4`, `tau=2` fixtures. Forty of 50 recommendations attain planner
discovery. Among 35 rows with feasible unilateral action changes, 31 are
strictly obedient and 29 pass both strict-member pair and exact-size-two
tau-player checks. Universal pooling and sole-team rescue collapse in every
fixture and never attain the planner portfolio; sole-team rescue nevertheless
makes collapse unilateral- and pair-stable in all five. Team tokens, exclusive
rights, and marginal contribution support the planner recommendation throughout
but retain respectively 25, 25, and 21 pure equilibria per fixture.

- DD-018: `20260722T051847Z_DD-018_a193f602_3b3ddac173`, DD-C-0083–0086.

DiscoveryBench v3 preserves all v1/v2 exact vectors and adds four Program V4
tasks. Its registry contains 24 tasks, 29 protocols, 39 task-level metrics, 36
compatible exact rows, and 660 explicit exclusions among 696 candidate pairs.
All exact vectors are independently reconstructed with capability isolation;
the CLI remains v1 by default and no composite score or external execution is
enabled.

- DiscoveryBench v3: `20260722T054447Z_DD-010_d265e480_6930915b02`,
  DD-C-0087.

Synthetic Experiment v3 preserves the v1 default and every shared-seed v2
power row while adding eight threshold/dynamic cells and six synthetic
contrasts. Its 37-cell registry contains 20 hypotheses, 23 outcomes, and 14
response scenarios; 1,184 balanced synthetic assignments support 1,680 power
rows and 1,680,000 seeded draws. All 644 failures among 840 rows at sample sizes
640 or greater remain published. These are conditional calibration results,
not empirical or behavioral evidence.

- Synthetic Experiment v3:
  `20260722T061958Z_DD-011_5743ccba_19b6517655`, DD-C-0088.

## Program V3 exact results

DD-012's access gate gives
`G_N(0)=1-(1-p)^N` and, for `k>=1`,
`G_N(k)=1-(1-q)(1-p)^(N-k)`. The first reader changes discovery by
`(1-p)^(N-1)(q-p)`; every later reader changes it by
`-(1-q)p(1-p)^(N-k-1)`. Thus one reader is uniquely optimal when `q>p`, zero
when `q<p`, and `{0,1}` tie when `q=p`. Equal-split attention margins strictly
decrease, so pure equilibria are a threshold count or two adjacent counts. The
bounded grid retains 63 excessive-attention cells, 24 all-attend equilibria
despite a unique one-reader optimum, and negative intervention results.

DD-013 proves the same `{0,1}` binding audience correspondence. Every feasible
symmetric garbling is weakly dominated by the binding full-precision optimum:
105 rows tie and 2,520 are strictly worse. Full broadcast is suboptimal in all
175 cells. Voluntary use differs from binding use in 656 of 1,050 settings;
universal pooling implements the optimal count in all 175 cells without
external subsidy but does not select reader identity or conditional policy.

DD-014 proves that replacing a registered third-option contrarian with a
private-dominant role weakly improves discovery for `p>=1/3`, strictly for
`p>1/3`. Contrarians tie an optimum only in 15 uninformative-private cells.
The best weak equilibrium remains inefficient in 23 of 75 cells. A larger raw
two-label audit finds complementary constant policies that beat the embedded
private/public optimum, preventing an unrestricted interpretation.

Primary runs are:

- DD-012: `20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b`, DD-C-0059–0061.
- DD-013: `20260721T215811Z_DD-013_09c07448_cdac4fb512`, DD-C-0062–0065.
- DD-014: `20260721T222047Z_DD-014_f5f099a8_ea0276dd16`, DD-C-0066–0068.
- DiscoveryBench v2: `20260721T230249Z_DD-010_add85590_56c61a2195`, DD-C-0069.
- Synthetic experiment v2: `20260721T232119Z_DD-011_121162f8_e454b06d2c`, DD-C-0070.

DiscoveryBench v2 has 20 tasks, 21 protocols, 27 metrics, 28 compatible exact
rows, and 392 explicit exclusions. DD-011 v2 has 29 treatments, 14 hypotheses,
19 outcomes, 11 response scenarios, 928 balanced synthetic assignments, and
924 power rows from 924,000 seeded draws. It retains 335 below-0.80 large-sample
rows; H13 and H14 remain at 0.764 and 0.632 at N=960 in the favorable rational
scenario. No participants were recruited, no human data were collected, and no
experiment was conducted.

## Publications and public surface

The 20-page *The Incentive to Ignore: Selective Attention and Audience Design
in Distributed Discovery* is a validated working paper with SHA-256
`ee9e27f741d25a9597994f18caf2bf406098db7aca4d2ed067a7a011f64be250`.
It has no DOI, submission, peer review, or verified novelty claim. The public
site includes `labs/attention.html`, `labs/audience-design.html`,
`labs/conditional-attention.html`, `benchmark/attention.html`, and
`experiment-kit/attention.html`, with static no-JavaScript tables and
checksum-bound data downloads.

## Preserved boundaries

The registered mechanisms do not solve unrestricted hidden-action, identity
selection, conditional-policy, mixed-equilibrium, or arbitrary-transfer
problems. The larger DD-014 raw class refutes unrestricted extrapolation of the
three-label theorem. DD-007 and DD-011 remain synthetic-only. No empirical
effect, behavioral information-avoidance result, hosted benchmark ranking, DOI,
release, or upstream modification is claimed.

Repository settings issue #32 remains open by design. The single authorized
authentication probe found no settings-capable CLI session; mutation was not
retried and did not block research.
