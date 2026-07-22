# The Architecture of Distributed Discovery

## Foundations, Results, and Open Problems — prospectus

Status: living-synthesis prospectus  
Updated: `2026-07-22`  
Submission status: not authorized  
Validated PDF: none

This prospectus specifies the intellectual architecture of a maintained
program synthesis. It is not a paper draft, a novelty claim, or an attempt to
turn every registered study into a chapter-length publication. Its job is to
define the shared object, stabilize notation, connect results whose evidence
and ownership remain elsewhere, preserve negative and bounded findings, and
make the next theorem gates legible.

Every scientific statement below is routed to the public claim ledger. Exact
computational numbers remain owned by immutable runs. Editorial judgments are
identified as editorial judgments. Questions are not written as results.

---

## 1. Program definition

Distributed Discovery studies how an organization or multi-agent system turns
dispersed evidence into a finite portfolio of search actions. The academic
position is **collective search under dispersed information**. The formal
object is a **discovery architecture**: a declared combination of target
prior, signal law, source dependence, observation rights, action technology,
authority, reward, timing, and feedback.

The central distinction is that information aggregation and action allocation
are different operations. An information system ranks possibilities. An
action system determines which possibilities receive attempts. A group may
improve its shared posterior while compressing several actions into one
repeated recommendation. Conversely, a group may preserve diverse attempts
without improving its map. The research problem is to characterize both
margins and the rules connecting them.

The public thesis is deliberately qualified: **collective intelligence is not
sufficient for collective discovery**. It does not say that intelligence,
information, or sharing is harmful. It says that a high-quality belief or
recommendation does not by itself specify a high-value action portfolio. The
design principle—**Share the evidence. Diversify the actions.**—is a prompt to
inspect architecture, not a theorem that every setting should maximize
sharing or diversity.

When actions require teams, the Program V4 qualification applies: form the
smallest viable teams and diversify those teams. DD-C-0071 proves this planner
value only in the frozen atomic threshold-opening model. Reliability,
overlapping targets, correlated execution, learning, and strategic formation
can change the rule. The synthesis must state the qualification beside the
principle rather than letting a memorable phrase outrun its evidence.

This program definition is a working definition (DD-C-0001). The accounting
identity `G_B=V_B-L_B` (DD-C-0002) organizes comparisons but supplies no
monotonicity result on its own. These are foundations for asking questions;
they are not claims that the project owns the surrounding literatures of team
decision, collective search, information design, social learning, mechanism
design, or organizational learning.

## 2. Foundational objects and notation

A chapter on foundations should begin with a target `theta`, an information
architecture `I`, an action budget `B`, a feasible protocol class
`P_B(I)`, and a group discovery event. For atomic search, the event is that at
least one distinct action equals the hidden target. For coverage, threshold,
or unreliable technologies, the event changes and must be declared before a
value is compared.

`G_B(Pi;I)` denotes discovery under one protocol. `V_B(I)` denotes the best
value in the declared feasible class. `L_B(Pi;I)=V_B(I)-G_B(Pi;I)` is protocol
loss. Frontier monotonicity requires emulation: if every protocol feasible
under `I_1` remains feasible under `I_2` with the same outcomes, then the
frontier under `I_2` is weakly larger (DD-C-0016). A realized strategic or
institutional outcome need not inherit that ordering because the feasible
class, incentives, or selection rule may change.

The synthesis should keep seven commonly collapsed objects separate:

1. one-person Bayes accuracy;
2. the full signal channel;
3. a direct private action rule;
4. the private-team optimum;
5. the pooled posterior;
6. a single recommendation or common action;
7. a multi-action portfolio.

DD-C-0090 and DD-C-0096 make the separation concrete. Two channels can have
the same one-person accuracy and the same direct-private baseline while having
different pooled action-budget profiles and opposite incremental-sharing
profiles. Accuracy is therefore not interchangeable with the channel, mutual
information, or portfolio value.

The foundational chapter should also separate authority from information. A
planner that observes all signals and assigns actions has a different feasible
class from autonomous agents who merely see the same posterior. A public
recommendation, a binding license, a correlated mediator, and a market
selection rule are not synonyms. The exact studies repeatedly show why the
distinction is operational: selection-dependent disclosure (DD-C-0030),
information firewalls (DD-C-0064), threshold recommendations (DD-C-0083), and
incremental sharing (DD-C-0094) change different elements of the architecture.

## 3. Evidence discipline and claim ownership

The synthesis should teach the evidence grammar before presenting the result
catalogue. A definition fixes language. An identity follows algebraically from
definitions or conditioning. An analytic theorem needs a written proof and a
separate consistency audit. An exact exhaustive result needs a completeness
argument or certificate. Independent reproduction needs a materially distinct
method. A finite counterexample can refute a universal statement; a finite
failure search cannot prove one. Monte Carlo power is an estimate under a
declared synthetic model and is not human evidence.

The claim ledger is the stable routing layer. The registered study is the
evidence unit: it owns the frozen model, configuration, implementation, proof
or certificate, immutable run, report, and claims. A theorem-family paper is
an editorial unit that owns a durable question. The living synthesis is a
program-level editorial unit. It may explain the same claim, but it does not
silently acquire novelty or primary ownership.

The program already contains useful mismatches in evidence strength, and the
synthesis should preserve them. The policy-signature characterization is a
derived theorem (DD-C-0023), while the canonical private-team optimum has an
independently reproduced exact certificate only at its frozen fixture
(DD-C-0038). The homogeneous pairwise source search is a bounded null
(DD-C-0033), while a heterogeneous perturbation supplies exact
counterexamples (DD-C-0043–0044). The One-Reader statement is an analytic
theorem in a restricted follow/private class (DD-C-0059), while the intervention
catalogue is bounded computation (DD-C-0061). The synthesis should not flatten
these into a list of equally general “findings.”

Primary ownership should be visible in prose and tables. The canonical entry
paper owns the atomic Shared Discovery Paradox. *The Incentive to Ignore* owns
the strategic attention and audience-design theorem family. DD-020 is owned by
the future Information Sharing Frontier paper and is cited by *Incentive* as a
companion. *Threshold Discovery* owns the deterministic minimum-team family
until a Reliable Discovery theorem materially strengthens or absorbs it. The
prospectus itself owns none of these theorems.

## 4. Canonical phenomenon: better ranking, compressed action

The Shared Discovery Paradox is the canonical entry. In the pinned atomic
fixture, private clue-following, one common pooled answer, and a coordinated
pooled portfolio have different discovery values even though the pooled
evidence can improve ranking. Exact canonical values and recovery budget are
routed through DD-C-0003 through DD-C-0008 and the pinned upstream paper. The
synthesis should cite that paper as primary and use only enough detail to
establish the program's basic separation.

The paradox is not “information is bad.” The planner frontier can improve with
information while a particular one-answer protocol loses action coverage. It
is also not “decentralization is good.” Direct independent actions can be
suboptimal when a private team can preassign differentiated policies:
DD-C-0021 gives an exact two-agent hybrid witness, and DD-C-0038 certifies the
direct canonical optimum only within one frozen zero-communication model.

Signal Geometry adds another axis. DD-019 fixes full pooling and varies the
number of distinct pooled actions. Its action-budget discovery profile and
recovery budget quantify how much action capacity is needed to recover a
named private baseline (DD-C-0089–0091). This profile is not an incremental
sharing curve. The former asks how many actions follow a fixed pooled
posterior; the latter asks how many agents contribute signals to one common
action while the remainder retain private actions.

The chapter should end with a diagnostic rather than a universal policy:
declare what improves the map, what compresses the portfolio, and what
authority can repair the compression. That question recurs in attention,
source acquisition, threshold teams, mechanisms, and dynamic search.

## 5. Private roles, disclosure, and source provenance

Three early theorem families show that architecture changes on distinct
margins.

First, private role policies can improve union discovery without
communication. A team commits ex ante to signal-to-action maps. Exact finite
examples show that constant territory and signal-responsive behavior can be
combined to avoid predictable duplication (DD-C-0021). The signature theorem
compresses a policy without losing its target-conditional success vector and
characterizes feasibility with local counts and Hall-type residual bounds
(DD-C-0023). Yet the canonical dimension remains difficult; the exact optimum
there is established by a separate alignment-preserving bound (DD-C-0037–0038).

Second, public disclosure changes both posterior information and the game
played under that information. The bounded DD-002 fixture contains a
refinement that lowers one named anonymous-symmetric outcome while every pure
equilibrium and the planner improve (DD-C-0030). The full deterministic
refinement census and six-rule selection catalogue show that “information
reduced discovery” is incomplete without the equilibrium-selection qualifier
(DD-C-0031, DD-C-0040–0041). The result is adjacent to Blackwell comparison and
Bayesian persuasion but does not solve a randomized disclosure problem.

Third, several reports may inherit dependence from fewer latent sources. The
homogeneous DD-003 census finds no complete first/pairwise-moment
counterexample in its frozen class—a bounded negative result, not a
sufficiency theorem (DD-C-0033). Heterogeneous source accuracies then produce
nonisomorphic networks with the same full pairwise observable object and
different discovery (DD-C-0043–0044). Endogenous acquisition adds a strategic
margin: the Common-Source work proves a finite-`N` threshold in its equal-prize
model and preserves an interior over-acquisition counterexample
(DD-C-0057–0058).

Together these results motivate a Price of Missing Provenance theorem but do
not yet supply it. A future result must specify what the decision maker
observes, which dependence structures remain feasible, and whether the object
is a sharp bound, an identification region, or a mechanism. “Effective sample
size” is not a substitute for that declaration.

## 6. Attention, audiences, and the Incremental Sharing theorem

The Information Sharing, Attention, and Recovery family begins with selective
access. DD-012 has one exogenous shared clue and `N` private point clues.
Giving the shared clue to exactly one role can maximize union discovery; later
duplicate users remove private attempts without improving the common clue.
The One-Reader Theorem and equal-split attention threshold are analytic
results in the declared model (DD-C-0059–0060). The bounded seven-rule census
then separates social attention from private incentives (DD-C-0061).

Audience Design asks who can receive or voluntarily use evidence. Binding
licenses, voluntary use, garbling, and firewall institutions are distinct
objects. The exact results show when access restrictions or mediated
recommendations implement a desired audience under the frozen game
(DD-C-0062–0065). Conditional Attention expands the policy class and preserves
a larger-class counterexample instead of overextending the restricted theorem
(DD-C-0066–0068).

DD-020 closes the next declared gate. Let `C_s` be the accuracy of a pooled
one-action MAP block and `G_s` the union discovery obtained when `N-s`
remaining actors keep direct private actions. Conditional independence yields

`G_s = 1-(1-C_s)(1-q)^(N-s)`

for a target-symmetric channel with constant conditional direct accuracy `q`
(DD-C-0092). The adjacent difference is marginal pooled-accuracy gain minus
the rescue value of the absorbed private action, scaled by the probability
that all other private actions fail.

For the symmetric noisy-point channel, the new signal's direct nomination and
the old pooled MAP cover at least one new pooled maximizer. This posterior
containment gives the general finite ordering `G_(s+1)<=G_s`, strict unless
signals are perfect (DD-C-0094). The two-agent identity `C_2=p` makes the loss
`-p(1-p)` transparent (DD-C-0093). A 2,555-row exact census independently
reproduces the bounded grid (DD-C-0095), but the proof—not the grid—owns the
general statement.

The arbitrary-channel extension supplies the necessary limit. The
half-accurate noisy-point curve falls from `7/8` to `3/4` to `7/12`, whereas
the half-accurate guaranteed two-shortlist rises from `7/8` to `11/12` to
`17/18` (DD-C-0096). Same one-person accuracy therefore does not determine the
incremental-sharing profile or its sign. The point-channel theorem cannot be
advertised as a theorem that sharing generally harms discovery.

The editorial consequence is a two-document architecture. *The Incentive to
Ignore* remains the primary owner of strategic attention and the One-Reader
Theorem. The future Information Sharing Frontier paper owns DD-020 and the
eventual channel classification. The former cites the latter as a companion;
the synthesis explains the connection without merging ownership.

## 7. Action technologies: coverage, thresholds, and reliability

Discovery is not always one atomic hit. DD-005 studies overlapping coverage,
where redundancy may be useful rather than wasteful. DD-016 changes the
technology again: a candidate opens only after receiving a minimum-size team.
For the deterministic atomic threshold model, the planner opens the largest
`min(floor(N/tau),M)` posterior masses with minimum viable teams
(DD-C-0071). Exact strategic payoffs and the bounded canonical census are
separate results (DD-C-0072–0074).

Equilibrium Selection records why a planner theorem does not identify
decentralized behavior. DD-017 distinguishes weak pure Nash, pairwise strict
stability, exact-size-threshold deviations, and one symmetric tied-mode
mixture (DD-C-0075–0078). The concepts are not interchangeable. Dynamic
Attention and the threshold-two extension add time and stopping but preserve
the planner/equilibrium boundary (DD-C-0079–0082).

Minimum Viable Team Mechanisms compares authority, eligibility, reward, and
coalition checks across five exact fixtures. Some authoritative or
eligibility-based institutions attain the planner recommendation; collapse
can remain individually or pairwise stable; and equilibrium multiplicity
persists (DD-C-0083–0086). These are bounded implementation results, not a
general mechanism theorem.

The next Reliable Discovery gate should introduce stochastic action success,
replication value, and correlated execution. A useful theorem would say when
the optimal architecture diversifies, repeats, overlaps, or forms threshold
teams and would recover DD-C-0071 as a special case. The editorial stopping
rule allows one registered attempt. A theorem can absorb or strengthen the
paper; a minimal counterexample can sharpen its boundary; a bounded null or
classification closes the hold and sends *Threshold Discovery* to independent
paper-admission judgment. Indefinite parameter extension is not a gate.

## 8. Implementation, authority, and mechanism design

The Discovery Implementation family asks which rules convert desired
portfolios into actual behavior. The relevant dimensions are information,
action authority, transfers, observability, participation, budget balance,
and equilibrium selection. An institution that assigns the planner portfolio
by authority is not an equilibrium implementation. A reward that supports one
recommended profile does not establish unique selection. A pairwise check is
not coalition-proofness.

DD-006 provides exact finite mechanism comparisons and normalized accounting
boundaries. DD-006B joins truth, action, and transfers in a bounded class and
preserves subsidized versus budget-balanced distinctions (DD-C-0052–0053).
Audience firewalls and DD-018 team institutions add other pieces but do not
solve the integrated problem.

The major theorem target is a truth–obedience–budget-balance characterization
under explicit observability. A successful result should name the message
space, allocation authority, transfers, outside option, deviation class, and
selection concept. It should also state whether evidence acquisition is
endogenous. Without those pieces, an “implementation” claim is likely to mix
several distinct feasible classes.

Randomized Information Design belongs here only after the sender objective and
solution concept are registered. DD-002's deterministic partition lattice and
DD-013's bounded garbling catalogue do not automatically generalize to a
concavification theorem. Likewise, DD-020's point-channel result concerns a
fixed pooling protocol, not an optimal experiment. The synthesis should make
these negative ownership statements as visible as the positive results.

## 9. Dynamic architecture and Rate–Discovery

Sequential search changes what an action reveals and when the protocol may
stop. DD-004 supplies a bounded perfect-elimination schedule. DD-015 shows how
visible prior actions and stopping feedback affect a frozen attention model;
its visibility result is a bounded null/negative finding, not a theorem that
social observation harms learning (DD-C-0081).

The Rate–Discovery family should measure communication or shared-information
cost against attainable discovery. A valid theorem needs a communication
model, message alphabet or bit budget, timing, feedback, action horizon, and
error criterion. The object might be a lower bound, an attainable curve, or a
large-team limit. “More communication” has no stable meaning until these are
fixed.

Adaptive work also requires a declared state and filtration. A greedy rule may
be justified by adaptive submodularity in one coverage setting and fail in an
atomic posterior-ranking problem. The program should resist borrowing a
guarantee from one technology merely because both are described as search.

The synthesis chapter can already compare static, stopping, and threshold
architectures, but it should label Rate–Discovery, dynamic coalition
formation, and large-team scaling as open theorem gates. Existing finite
dynamic results are evidence and design diagnostics, not an asymptotic theory.

## 10. Discovery order and the North-Star hierarchy

The structural spine has three established objects: information–action
separation, action-budget discovery profiles, and recovery budgets. They
support five major theorem families: information sharing/attention/recovery;
source acquisition/provenance; reliable action technology; discovery
implementation; and dynamic Rate–Discovery. The meta-theory asks whether these
can be organized by an order on discovery-relevant information structures,
scaling laws, and a general theory of discovery architectures.

Classical Blackwell comparison orders experiments by centralized decision
value across loss functions. Distributed Discovery needs a more explicit
object because value can depend on a portfolio of actions, local observations,
strategic rewards, and selection. DD-C-0016 gives a safe monotonicity statement
only when one feasible protocol class can emulate another. DD-C-0030 shows why
a selected equilibrium need not follow planner monotonicity. DD-C-0096 shows
why one-person accuracy cannot stand in for the channel.

A Discovery Order theorem would need to say what is held fixed: action budget,
authority, communication, objective, and protocol class. It might compare
channels by all feasible portfolio values, by a family of discovery events, or
by implementable outcomes. These possibilities are open. The synthesis should
not name an order before the definition and separation examples survive
counterexample search.

Scaling laws are similarly open. Large `M`, large `N`, sparse sources,
threshold growth, and communication limits may have different regimes. Exact
finite studies provide regressions and minimal witnesses, not asymptotic
rates. A future scaling claim must specify the sequence of priors, channels,
budgets, and technologies.

## 11. Measurement and infrastructure

DiscoveryBench is infrastructure, not a universal score. Its versioned exact
tasks declare capabilities and explicit incompatibilities; missing metrics are
not imputed (DD-C-0069, DD-C-0087). This permits methods to be compared only
where the target, information, action, reward, and output contract align. A
future external adapter requires a separate authorization and must not turn a
small exact registry into a leaderboard claim.

The synthetic experiment kit translates mathematical contrasts into
conditional power calculations. DD-C-0070 and DD-C-0088 are Monte Carlo
estimates under frozen response scenarios. They are not evidence that people
or deployed agents exhibit the modeled effects. No participant was recruited,
no human or real data were analyzed, and no empirical effect is established.

Labs are explanatory interfaces connected to immutable outputs. A useful Lab
changes substantive model inputs and displays exact outputs, provenance, and a
complete no-JavaScript fallback. It does not create a new result. Schemas,
claim validation, run manifests, corruption tests, PDF checksums, and route
audits serve the same infrastructure role: they make evidence inspectable
without upgrading its epistemic category.

The synthesis should include an evidence-reading guide showing how to move
from a chapter statement to a claim ID, study report, immutable run, verifier,
and test. That path is part of the scholarly contribution of the repository,
but the existence of infrastructure does not satisfy the paper-admission rule.

## 12. Negative results and stopping rules

A living synthesis is especially valuable for evidence that would disappear
from a paper-centered history. The program preserves a bounded pairwise-moment
null, selection-specific failures, anti-informative counterexamples, a visible
action null, equilibrium multiplicity, stable collapse, synthetic power
failures, and the arbitrary-channel limit of point-channel monotonicity.

These results do different jobs. A counterexample refutes a universal claim.
A bounded null says a declared search did not find a difference. A failed
certificate rejects a proposed proof path. An equilibrium multiplicity count
limits implementation language. A synthetic calibration failure limits an
experiment design. They should not be grouped under a vague “limitations”
heading and then forgotten.

Every theorem family needs a stopping boundary. The Information Sharing
family proceeds to the General Sharing Frontier because DD-020 proved the
point case and found an opposite-sign channel. The Reliable Discovery family
gets one registered theorem attempt before the Threshold paper is judged
independently. Discovery Implementation requires a structural theorem rather
than another finite catalogue. Dynamic work requires a named communication or
asymptotic regime. Empirical work remains prohibited until a separate ethics,
privacy, identification, and governance gate is authorized.

Stopping is not failure. A sharp counterexample, a bounded null, or a resource
certificate can define the honest edge of a theorem family and prevent the
program from accumulating unstructured parameter studies.

## 13. Paper architecture

The publication system has four layers.

1. *The Shared Discovery Paradox* is the canonical entry paper and remains
   upstream.
2. Theorem-family papers own durable mathematical questions. Current
   candidates include Common-Source Trap, Incentive to Ignore, Threshold
   Discovery, and a future Information Sharing Frontier paper, each with its
   own gate and scope.
3. *The Architecture of Distributed Discovery* is the living synthesis. It
   supplies common notation, relationships, negative evidence, and open
   problems while citing primary owners.
4. Registered studies and infrastructure expose the reproducible evidence.

The Incremental Sharing gate clarifies why chronology is a poor paper
architecture. DD-020 follows DD-019 in Program V5 and is intellectually
adjacent to DD-012, but it should not simply be appended to the existing
attention paper. Its nonstrategic pooled-signal theorem requires a different
model and literature position. The future family paper can place DD-019's
profile counterexample, DD-020's theorem, and the General Sharing Frontier
under one central question. *Incentive* can remain self-contained and cite the
companion.

The five-part admission rule remains controlling: central question,
title-level result, natural literature/referee set, self-contained reason to
exist, and near-term non-obsolescence. Exact runs, claim counts, length,
polished PDFs, and websites are not admission criteria. No current editorial
map represents submission, acceptance, peer review, release, or DOI status.

## 14. Open theorem gates

The next open gates should be printed as questions with owners and stopping
conditions.

### General Sharing Frontier

Which declared channels are compression dominated, aggregation dominated,
portfolio dependent, or nonmonotone under incremental sharing? DD-019 and
DD-020 are the fixed evidence base. The next study must use exact channel
semantics, named private baselines, action-budget and incremental profiles,
independent verification, and minimal counterexamples. It must not infer a
scalar channel order from one-person accuracy.

### Recovery Budget

How much action capacity repairs the discovery loss induced by a sharing rule?
The answer depends on the baseline, authority, and action technology. DD-019's
bounded recovery budgets are examples, not a general theorem.

### Price of Missing Provenance

What sharp loss or identification region follows when source dependence is
unobserved? The theorem must define observable equivalence and the feasible
latent-source class.

### Reliable Discovery

When should the planner repeat, overlap, diversify, or form minimum teams under
stochastic execution? One registered attempt closes the editorial hold by a
theorem, sharp counterexample, or preserved bounded failure.

### Truth–obedience–budget balance

Which architectures jointly elicit evidence and implement action portfolios
without hidden subsidy? Observability and deviation classes must be explicit.

### Rate–Discovery and dynamics

What communication, time, or feedback rate is necessary and sufficient for a
discovery target? A named regime is required before study allocation.

### Discovery Order and scaling

Can information structures be ordered for portfolio discovery under fixed
protocol constraints? What limits arise as targets, agents, sources, or teams
grow? These remain meta-theory, not announced results.

## 15. Editorial work plan for the living synthesis

The next synthesis work should be modular. First, stabilize a notation table
that maps each chapter's source notation without pretending distinct models
are identical. Second, create claim-addressable chapter briefs: each paragraph
of scientific content lists its claim ID and primary study during drafting.
Third, maintain an explicit negative-results register. Fourth, add theorem
ownership boxes identifying primary papers and companion relationships.
Fifth, update the maturity map only when a claim audit or editorial gate
actually changes.

No validated synthesis PDF is warranted yet. The current source base contains
several strong theorem families, but the Information Sharing, Reliable
Discovery, Implementation, Rate–Discovery, and Discovery Order gates remain
open. A premature omnibus would either repeat working papers or blur evidence
status. The prospectus and machine-readable maps are the appropriate current
artifact.

When a future PDF is authorized, it should be generated from mapped source,
validate every claim reference and citation, distinguish source claims from
editorial synthesis, and pass deterministic build and all-page visual review.
Authorization for that artifact would still not authorize submission or DOI
publication.

---

## Evidence-routing summary

- Canonical entry: DD-C-0003–0008; pinned upstream paper.
- Foundations and private teams: DD-C-0001–0028 and DD-C-0037–0038.
- Disclosure and source provenance: DD-C-0029–0044 and DD-C-0050–0058.
- Attention and sharing: DD-C-0059–0068 and DD-C-0089–0096.
- Action technologies and implementation: DD-C-0044–0048,
  DD-C-0052–0053, and DD-C-0071–0086.
- Infrastructure and synthetic measurement: DD-C-0049, DD-C-0054,
  DD-C-0069–0070, and DD-C-0087–0088.

These ranges are routing aids. The claim ledger's exact statements and scopes
are authoritative. This prospectus creates no scientific claim, run, paper,
submission, or empirical evidence.
