# Theorem roadmap and research portfolio

> Phase 2 sequencing note (2026-07-23): all theorem-family execution is held.
> Reliable Discovery is preserved as a major candidate, not queued or promised.
> DiscoveryBench Agents v1 is registered-not-executed under DD-010. The next
> substantive gate is its offline instrument implementation. The
> three unregistered readiness gates are recorded in
> [`reports/roadmap-consolidation/phase-2-theorem-gates.md`](../reports/roadmap-consolidation/phase-2-theorem-gates.md).
> Their timing is governed by the nine-option staged portfolio in
> [`strategic-direction/optionality-portfolio.yml`](strategic-direction/optionality-portfolio.yml);
> none is authorized for theorem execution. The internal Gate C name and
> search-theory succession ambition remain prohibited on public result
> surfaces until their separate gates pass.

## 1. Purpose

**Distributed Discovery** is the research program on *collective search under
dispersed information*. Its formal object is a *discovery architecture*: the
combination of information, action allocation, timing, and implementation rules
that converts evidence into a portfolio of searches.

The public thesis is that **collective intelligence is not sufficient for
collective discovery**. Information aggregation is not action allocation. The
design principle remains **Share the evidence. Diversify the actions.** Its
academically precise qualification is that the optimal amount of action
concentration depends on signal geometry, source dependence, reward congestion,
action technology, reliability, coverage, and the number of actions or agents
required for success. Under Program V4's threshold technology: when actions
require teams, form the smallest viable teams and diversify those teams.

The post-V5 stage seeks general theorems, tight bounds, minimal failure examples,
and independently checkable certificates that explain when finite results
persist, fail, or compose. Diversity is not universally optimal: repetition can
be valuable under execution failure, confirmation, multiple targets,
robustness, overlapping coverage, thresholds, or heterogeneous capability.

This is a portfolio document, not a study registration or result. It assigns no
new study IDs. “The Architecture of Distributed Discovery” is reserved for a
future synthesis-level survey, book, talk, or site section; it is not a rename
of the program.

## 2. Current program state

Program V4, *Threshold Discovery: Coordination, Crowding, and Minimum Viable
Teams*, is complete at its registered bounded scope. DD-016 through DD-018,
DiscoveryBench v3, the synthetic experiment v3 extension, the focused paper,
and four output-connected public Labs are deployed. Its final handoff creates
no new research evidence.

Program V5, *The Information Sharing Frontier*, has completed and deployed its
documentation baseline and DD-019 through DD-022, with exact output-connected
Labs. It asks:
**When does sharing useful private
information improve or reduce decentralized group discovery?** Its qualified
26-page theorem-family working paper is *When Does Information Sharing Improve
Decentralized Discovery?*, with subtitle *Signal Geometry, Independent Rescue,
and the Cost of Common Action*.

The public thesis is: **Sharing helps when it improves the group's map faster
than it collapses the search portfolio.** The technical thesis is that the sign
and value of sharing depend jointly on signal geometry, sharing intensity,
source dependence, action budget, action technology, reward structure, action
authority, and equilibrium selection.

The conceptual center is

`value of sharing = aggregation gain - lost independent rescue value`.

DD-020 proves this exact decomposition for its point channel. DD-021 proves the
channel-independent adjacent error-contraction criterion and centralized
full-capacity recovery within its declared protocol, while its 177-scenario
mixed-curve null remains bounded. DD-022 proves an exact strict sharing interval
in a selected coordination-free equilibrium and preserves the every-equilibrium
failure. The post-DD-022 gate admitted the qualified archival-paper candidate,
and its working paper and public integration are complete; no submission,
release, DOI, or journal contact is authorized. Broader uses remain
conjectural until their own proof or bounded evidence. Active execution truth is in
[theorem-spine.md](theorem-spine.md), active execution truth is in
[current-roadmap.md](current-roadmap.md), and registered evidence is in
[the study registry](../studies/index.md).

## 3. Research style and promotion discipline

Every flagship mathematical project should state which of these objects it
will deliver:

1. **Theorem** on a declared domain.
2. **Tightness** through a matching or nearly matching bound.
3. **Failure** through a minimal counterexample outside that domain.
4. **Certificate** through an independently verifiable finite certificate,
   regression, or test suite.
5. **Literature boundary** distinguishing an extension from a renamed classical
   result.
6. **Operational interpretation** identifying a consequential design decision.
7. **Named comparison baseline**, including its action policy and authority.
8. **Equilibrium-selection scope** when agents choose strategically.
9. **Action-technology scope**, including thresholds, reliability, and overlap.

Exploratory work need not prove a theorem. A flagship paper must identify which
objects it supplies and retain negative results. Exact grids serve theorem
discovery, tightness, failure witnesses, and regressions—not themselves.

An idea may move from roadmap to a registered study only with a precise model;
a falsifiable theorem, counterexample, or identification target; a literature
boundary; a state-space or complexity audit; a proof, enumeration,
LP-certificate, or simulation-verification plan; an independent verifier; a
corruption-test plan; a non-overlap statement; a clear paper, benchmark,
measurement, or infrastructure role; and an explicit stop condition. Study IDs
are assigned only when a bounded issue and ExecPlan are created.

## 3A. North-Star theorem hierarchy

The hierarchy below organizes, rather than replaces, the directions in this
roadmap.

**Tier I — Structural spine**

- Information–Action Separation
- Action-Budget Discovery Profiles
- Recovery Budgets

**Tier II — Major theorem families**

- Information Sharing, Attention, and Recovery
- Source Acquisition and Provenance
- Reliable Discovery and Action Technology
- Discovery Implementation
- Rate–Discovery
- Dynamic and Adaptive Discovery

**Tier III — Meta-theory**

- Discovery Order for Information Structures
- Scaling Laws
- General Theory of Discovery Architectures

Reliable Discovery, Provenance, mechanism theory, Rate–Discovery,
dynamic/adaptive work, large-team limits, and Discovery Order all retain their
existing scopes and promotion gates below.

## 4. Completed Program V4 — Threshold Discovery

**Status: complete at the registered bounded scope.** Program V4 owns threshold
opening, its planner frontier, equilibrium selection and coalition stability,
registered dynamic attention, and minimum-viable-team implementation. It
distinguishes deterministic threshold opening from reliability, stochastic
coverage, overlap, and multi-target value. Later technologies may now use its
stable interfaces while preserving the recorded boundaries.

## 5. Program V5 dimension map

Program V5 varies these dimensions sequentially, not in one giant model:

1. **Signal geometry:** point nomination; shortlist; exclusion; confidence;
   likelihood-ratio distribution.
2. **Sharing intensity:** no pooling; partial pooling; full pooling.
3. **Source dependence:** independent; correlated; copied.
4. **Action budget:** one recommendation; top-`L` portfolio; full action
   capacity.
5. **Action technology:** one hit sufficient; threshold teams; unreliable
   execution; overlap and multi-target value.
6. **Reward structure:** equal split; full duplicate credit; unique rescue;
   marginal contribution; pooling.
7. **Equilibrium selection:** all pure equilibria; best/worst pure; symmetric
   mixed; dynamics; coalition stability; correlated recommendations.
8. **Authority and observability:** binding assignment; autonomous action;
   visible occupancy; hidden action; selective delivery.

## 6. Program V5 provisional work packages

These packages assign no DD IDs. Registration remains sequential.

### A. Signal Geometry and the Discovery Profile

For channel `W` and `N` signals, define

`V_L^(N)(W) = expected optimal posterior mass covered by L distinct pooled actions`

and the action-budget discovery profile

`V_N(W) = (V_1^(N), ..., V_N^(N))`.

Targets are exact point, shortlist, exclusion, and confidence channels;
same-private-accuracy counterexamples; scalar-insufficiency results; exact or
interval-certified phase diagrams; and a reusable channel registry.

### B. Incremental Sharing and the Point-Channel Theorem

Let `G_s(W)` be discovery when a shared-answer block uses `s` agents' signals
and the other `N-s` agents retain private actions. Define `s` so that `s=1` is
the private baseline with one ordinary agent, and test monotonicity for `s>=1`.

Primary conjecture: for the symmetric noisy-point channel, each increase from
`s` to `s+1` after the first shared user reduces discovery in the nondegenerate
ordinary-box model. This is a conjecture, not a theorem.

Progression: `M=N=2`; `N=2` arbitrary `M`; `M=2` arbitrary `N`; bounded
arbitrary `M,N`; then a general proof or minimal counterexample.

### C. General Sharing Frontier

Define `q(W)` as one-person private Bayes-action accuracy, `P_N(W)` as the
declared private-portfolio discovery, and `C_N(W)` as one pooled
consensus-action accuracy. Classify no useful aggregation; the Shared Discovery
Paradox (`q<C_N<P_N`); aggregation-dominated sharing (`C_N>=P_N`); and
portfolio-dependent sharing, where consensus is insufficient but a top-`L`
pooled action is valuable. Seek necessary and sufficient channel conditions.

### D. Recovery Budget

For a named private baseline define

`L*(W) = min {L : V_L^(N)(W) reaches or exceeds that baseline}`.

Targets are exact point- and shortlist-channel recovery budgets; concentration
bounds; conditions for `L*=1` or near-`N`; confidence metadata under tight
budgets; and a threshold-team generalization after Program V4. Recovery-budget
tables outside repository evidence are regression hypotheses only.

### E. Coordination-Free Positive Sharing

Freeze “no coordination” as simultaneous, anonymous, no role labels, no visible
occupancy, no correlated randomization, no assigned action, no post-disclosure
communication, and a declared symmetric equilibrium selection. Study when
sharing exposes hidden correlation and congestion-sensitive rewards induce
greater dispersion. Seek a dependence threshold only after specifying the
source model and equilibrium selection.

### F. Randomized Information Design

Move the existing Randomized Information Design direction inside, or directly
after, the deterministic Program V5 core. It follows Signal Geometry and
Incremental Sharing. Targets remain public stochastic messages, private
messages, correlated recommendations, action recommendations, message-alphabet
bounds, exact rational LPs, primal/dual certificates, and selection robustness.

### G. Equilibrium Selection Module

Every Program V5 result states whether it applies to every pure equilibrium,
worst pure, best pure, a unique equilibrium, anonymous symmetric mixed, a
declared dynamic, coalition-stable outcomes, correlated equilibrium, or a
planner only. “Decentralized” is never a synonym for “uncoordinated.”

### H. Mechanism and Design Implications

Only after the natural sharing frontier is understood, compare preserving
independent sources, revealing source overlap, limiting shared-signal
followers, sending different messages, showing occupancy,
congestion-sensitive rewards, roles, and threshold teams. Each intervention
changes a different primitive.

## 7. Post-V5 research programs, preserved and reordered

The intellectual ranking still places Diversity–Redundancy, Provenance, and
Discovery Order among the highest-reach directions. Program V5 is complete.
The post-V5 audit inserted one bounded implementation bridge before Reliable
Discovery because DD-C-0098 is centralized and DD-C-0109 shows that the
positive decentralized comparison is not robust across equilibria. Issue #162
completed that bridge as the classical-overlap stop recorded below.

### Decentralized Recovery and Equilibrium Robustness — stopped formulation

Issue #162 completes the smallest proposed common-posterior equal-sharing gate
with `stop-classical-overlap`. The simultaneous game is exactly a singleton
congestion/resource-selection game with a Rosenthal potential, and the fixed
sequential visible-occupancy version is solved by ordinary backward induction.
For ordered posterior masses `a>=b>=c`, the same strict `b>a/2` condition
governs every-pure-equilibrium top-two recovery in both forms; equality retains
a collision outcome. The named private baseline and centralized comparator are
ex-post comparisons and do not produce a nonclassical equilibrium statement.
No study ID, claim, run, or paper was created. This formulation remains in the
historical portfolio but is not executable.

### Reliable Discovery — Diversity–Redundancy under reliability and overlap

For posterior mass `mu_j`, per-attempt reliability `r_j`, and `n_j` attempts,

`G(n) = sum_j mu_j [1-(1-r_j)^n_j]`, subject to `sum_j n_j=N`,

with marginal value `Delta_j(n_j)=mu_j r_j(1-r_j)^n_j`. This
separable-concave baseline is classical resource allocation. A Distributed
Discovery contribution must arise from dispersed evidence, heterogeneous
agents, dependence, coverage, strategic implementation, or their composition.
Targets include exact marginal allocation, repetition conditions,
heterogeneous reliability, correlated-failure counterexamples, confirmation,
threshold reliability, overlap, multiple targets, reliability investment,
strategic replication, and reliability-adjusted recovery budgets.

### The Price of Missing Provenance

Given recorded statistics, bound true discovery capacity. For success events
`E_i`, start from sharp union ranges under declared marginals and add
pairwise/higher intersections by finite LP. Pair this with source
identification, moment requirements, attainable correlation gaps, and the
limits of allocation repair. No result proceeds without declared observables
and a sharpness or identification certificate.

### Truth, Obedience, and Budget Balance

Seek necessary and sufficient implementation conditions, not another finite
catalogue. Compare efficient allocation, truthful reports, obedience,
participation, ex-post budget balance, subsidy, hidden action, aggregate-only
observability, anonymity, and coalition stability. Methods include incentive
inequalities, LPs, Farkas certificates, minimum subsidy/observability formulas,
positive mechanisms, and robustness margins.

### Rate–Discovery Theory

Define communication required to attain a discovery target or approximate a
declared planner value. Progress from zero/full pooling to public/private bits,
coordinators, simultaneous and interactive messages, shared randomness, graph
constraints, and role versus evidence messages. Seek list-style lower bounds,
achievability without reconstructing all evidence, planner-emulation costs,
communication recovery budgets, and cases where more communication
synchronizes actions and lowers discovery.

### A Discovery Order for Information Structures

Develop a portfolio information order only after signaling, communication, and
a decentralized counterexample make it nontrivial. Stop before registration if
the proposed order is centralized Blackwell theory in new terminology.

### Dynamic/adaptive synthesis and large-team limits

Integrate perfect elimination, DD-015, dynamic coalition formation, adaptive
coverage, action visibility, stopping, and common-information coordination.
Large-team work follows a named finite theorem and declares its asymptotic
regime and finite correction.

### The Architecture of Distributed Discovery

Reserve the long-term synthesis for the mature theorem, mechanism, benchmark,
and empirical-boundary interfaces. It is not a program rename.

## 8. Execution sequence and single-lane dependencies

1. **Complete:** Program V4 — Threshold Discovery.
2. **Complete:** Program V5 — The Information Sharing Frontier; DD-019 through
   DD-022, the qualified working paper, and public integration are deployed.
3. **Complete stop:** Decentralized Recovery and Equilibrium Robustness at the
   frozen equal-sharing formulation; no study allocated.
4. **Recommended next registration:** Reliable Discovery — Diversity–Redundancy
   under reliability and overlap.
5. **Then:** The Price of Missing Provenance.
6. **Then:** Truth, Obedience, and Budget Balance.
7. **Then:** Rate–Discovery Theory.
8. **Then:** A Discovery Order for Information Structures.
9. **Later:** dynamic/adaptive synthesis and large-team limits.
10. **Long-term synthesis:** The Architecture of Distributed Discovery.

Randomized Information Design is an early Program V5 theory lane, not a
separate simultaneous branch. One substantive branch and one pull request are
active at a time. A later milestone starts only after its predecessor is
merged, deployed where applicable, and closed, except for a single post-merge
documentation closeout completed before the next substantive branch.

## 9. Priority matrix

| Direction | First bounded target | Dependency / stop condition |
| --- | --- | --- |
| Information Sharing Frontier | Complete DD-019–DD-022 theorem family | Preserve the selected-equilibrium and centralized-authority boundaries. |
| Decentralized Recovery | Completed overlap gate at the smallest posterior resource-selection game | Stopped: the result is a classical congestion/backward-induction specialization. |
| Diversity–Redundancy | Exact marginal allocation with finite posterior masses and reliabilities | Next registration; stop if it merely renames separable-concave allocation. |
| Provenance | Sharp union bounds under named observables, then a latent-source fixture | Stop without declared observables and sharpness/identification certification. |
| Mechanism design | Necessary/sufficient implementation and subsidy/observability frontier | Stop if a finite catalogue is presented as global impossibility. |
| Rate–Discovery | Zero versus one public/private bit with a declared list target | Stop if the task merely reconstructs all evidence. |
| Discovery Order | Portfolio information order and separation domain | Require decentralized content beyond Blackwell theory. |
| Dynamic/scale | Adaptive marginal conditions and minimal failures | Wait for DD-015 and a named finite theorem/regime. |

## 10. Paper sequence

All titles are provisional; none implies submission or publication.

1. *Threshold Discovery*.
2. *When Does Information Sharing Improve Decentralized Discovery?* (working paper complete).
3. *When Should Searchers Repeat?*
4. *The Price of Missing Provenance*.
5. *Truth, Obedience, and Budget Balance*.
6. *How Much Must a Team Communicate to Discover?*
7. *A Discovery Order for Information Structures*.
8. *The Architecture of Distributed Discovery*.

## 11. Benchmark and infrastructure implications

Benchmark additions should express theorem interfaces: channel geometry,
recovery budgets, reliability-adjusted portfolios, provenance observables,
message budgets, action authority, feedback visibility, and declared
dependence. Preserve capability isolation, exact golden fixtures, explicit
exclusions, independent recomputation, and corruption gates. Synthetic power
may test declared assumptions; it cannot become behavioral evidence.

## 12. Empirical and ethics boundary

The program may develop schemas, identification analysis, synthetic recovery
audits, and public-safe benchmark data. It must not collect, ingest, infer
about, or validate against real or human data without separately authorized
ethics, privacy, identification, retention, and governance review.

## 13. What not to do

Do not call private accuracy a channel; conflate sharing with common action;
compare consensus with an undefined private baseline; claim maximal diversity
is always optimal; report *the* equilibrium under multiplicity; promote
preliminary shortlist simulations to exact results; assign many study IDs
before execution; or run more than one substantive branch.

Also do not add exact grids without a theorem, counterexample, identification,
or benchmark purpose; rename classical theorems; claim novelty for broad
subjects; treat pairwise disagreement as source independence; call solver
output proof without verification; promote synthetic power to human evidence;
start real-data work without review; or fragment a shared mathematical object
into incompatible packages.

Continue Theorem—Tightness—Failure—Certificate, exact scope labels, literature
boundaries, operational interpretations, named baselines, equilibrium and
action-technology scopes, minimal counterexamples, negative results,
independent verification, public-safe provenance, modular discovery
architectures, and benchmark regressions.

## 14. Roadmap maintenance

Update this document only when a promotion gate is met, a material dependency
changes, a direction is retired or merged, or active work creates a non-overlap
constraint. Keep active execution in `docs/current-roadmap.md`, evidence in
registered studies, and consolidation decisions in
`reports/roadmap-consolidation/`. Do not use this document to promote a claim
or imply execution.

## 15. Provisional next decision points

1. Preserve the completed Program V4 and Program V5 evidence without rerunning
   immutable configurations.
2. Preserve the completed Decentralized Recovery overlap stop; do not broaden
   that model or allocate a study ID to rescue it.
3. Register Reliable Discovery only after its issue and ExecPlan freeze the
   model, comparator, resource cap, evidence category, verifier, corruption
   plan, literature boundary, and stop condition.
4. Keep Randomized Information Design as a later possible extension, not an
   unfinished Program V5 obligation.
5. Before Provenance, specify observables, source model, and
   sharpness/identification target separately.
6. Before Rate–Discovery, choose a list, planner-emulation, or portfolio target
   under a declared communication model.
7. Before Discovery Order, show content beyond centralized Blackwell theory.
