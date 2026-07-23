# Theorem spine — from information to implemented discovery

This is a navigation and synthesis document. It creates no study, claim, proof,
run, or novelty assertion. Every established statement below points to its
registered claim and evidence; every unproved connection is labeled **open**.

## 1. Structural separation

Distributed Discovery separates four objects that are often collapsed:

1. **information** — the signal structure and posterior map;
2. **action portfolio** — the targets actually searched;
3. **discovery technology** — how actions, failures, overlap, and thresholds
   convert a portfolio into success; and
4. **implementation** — who can assign actions and which strategic outcome is
   selected.

The program-level accounting identity is [DD-C-0002](../claims/claims.yml),
while the canonical information/action separation is owned by DD-000 and its
read-only upstream paper. Later claims refine, rather than replace, that
separation.

```text
signal law -> posterior map -> action-budget frontier -> implemented portfolio
     |              |                  |                        |
 geometry       aggregation       recovery budget       authority/selection
```

The final arrow is not automatic. A centralized posterior top-`L` value is an
upper benchmark unless an institution or equilibrium implements it.

## 2. Action-budget discovery profiles

DD-019 makes the action budget explicit. For a finite channel `W`, pooled
posterior information, and binding authority to select `L` distinct targets,
`V_L^(N)(W)` is the expected posterior mass covered by the selected portfolio.
The vector over `L` is an action-budget discovery profile.

- [DD-C-0089](../claims/claims.yml) independently reproduces five exact
  bounded profiles in the registered `M=4, N=3` fixture.
- [DD-C-0090](../claims/claims.yml) gives the exact same-private-accuracy
  counterexample: one scalar does not determine the bounded profile.
- [DD-C-0091](../claims/claims.yml) computes recovery budgets against each
  channel's declared direct-private baseline.

Evidence: [DD-019 study](../studies/DD-019-signal-geometry/README.md) and
[immutable run](../results/verified/20260722T084145Z_DD-019_a77bb786_04a5e9f0c5/manifest.json).
These are pooled-planner values, not strategic implementation results.

## 3. Independent rescue and the sign of sharing

DD-020 isolates the value lost when another autonomous search action is folded
into a common pooled action. In its target-symmetric block-sharing protocol,
the exact decomposition in [DD-C-0092](../claims/claims.yml) writes discovery
as aggregation success plus the chance that an independent private action
rescues pooled failure.

- For the symmetric noisy-point channel, every additional sharing step weakly
  reduces discovery; the precise theorem and boundaries are
  [DD-C-0093](../claims/claims.yml) and [DD-C-0094](../claims/claims.yml).
- The exact census is [DD-C-0095](../claims/claims.yml).
- The five-channel counterexample [DD-C-0096](../claims/claims.yml) shows that
  equal one-person accuracy can coexist with opposite sharing signs.

Evidence: [DD-020 study](../studies/DD-020-incremental-sharing/README.md),
[proof](../studies/DD-020-incremental-sharing/proof.md), and
[immutable run](../results/verified/20260722T142551Z_DD-020_3854fff6_37c11a850a/manifest.json).
The point-channel theorem does not imply arbitrary-channel monotonicity.

## 4. General sharing frontier and centralized recovery

DD-021 expresses the adjacent sharing sign through pooled error contraction.
[DD-C-0097](../claims/claims.yml) proves that a sharing step helps exactly when
the next pooled error contracts faster than the remaining private rescue factor.
Its registered channel census, minimal witnesses, recovery budgets, and bounded
null are [DD-C-0099](../claims/claims.yml) through
[DD-C-0103](../claims/claims.yml).

[DD-C-0098](../claims/claims.yml) proves full-capacity recovery relative to the
declared direct baseline, but only for a **centralized posterior top-`L`
selector**. This is a planner frontier with binding assignment authority; it is
not a decentralized, anonymous, incentive-compatible, or equilibrium
implementation theorem.

Evidence: [DD-021 study](../studies/DD-021-general-sharing-frontier/README.md),
[proof](../studies/DD-021-general-sharing-frontier/proof.md), and
[immutable run](../results/verified/20260722T185924Z_DD-021_3cdbbc40_2fea269a9a/manifest.json).

## 5. Selected coordination-free positive sharing

DD-022 asks whether useful sharing can improve discovery when agents choose
actions themselves. In its exact binary two-agent equal-split game:

- [DD-C-0104](../claims/claims.yml) and [DD-C-0105](../claims/claims.yml)
  characterize the declared private and shared symmetric selections;
- [DD-C-0106](../claims/claims.yml) proves a strict algebraic interval where
  selected shared discovery exceeds selected private discovery;
- [DD-C-0107](../claims/claims.yml) gives the corresponding payoff result;
- [DD-C-0108](../claims/claims.yml) independently reproduces the bounded grid;
- [DD-C-0109](../claims/claims.yml) records the essential limitation: the
  comparison fails as an every-equilibrium statement; and
- [DD-C-0110](../claims/claims.yml) keeps the strictly positive gap to the
  centralized top-two benchmark visible.

Evidence: [DD-022 study](../studies/DD-022-coordination-free-positive-sharing/README.md),
[proof](../studies/DD-022-coordination-free-positive-sharing/proof.md), and
[immutable run](../results/verified/20260722T210334Z_DD-022_2376d5b7_ad67765ca8/manifest.json).
The positive result is posterior-only and selection-dependent; roles,
ownership-conditioned behavior, correlation, refinements, and learning
dynamics are outside its theorem.

## 6. The completed Information Sharing Frontier family

The four studies support one qualified theorem-family working paper:
[*When Does Information Sharing Improve Decentralized Discovery?*](../papers/information-sharing-frontier/README.md).
Its public-facing summary is:

> Sharing helps when it improves the group's map faster than it collapses the
> search portfolio.

That sentence is an editorial synthesis of the registered results above, not a
new universal theorem. The paper's positive result must always appear beside
the every-equilibrium limitation and the centralized-recovery authority
boundary. The living synthesis chapter is mapped in
[chapter-map.yml](../synthesis/architecture-of-distributed-discovery/chapter-map.yml),
with ownership in [paper-family-map.yml](paper-family-map.yml).

## 7. Established links and open arrows

| From | To | Status | Evidence or gate |
| --- | --- | --- | --- |
| Signal geometry | Action-budget profile | **established, bounded** | DD-C-0089–DD-C-0091 / DD-019 |
| Independent rescue | Adjacent sharing sign | **established on declared protocols** | DD-C-0092–DD-C-0097 / DD-020–DD-021 |
| Full pooled information plus top-`L` authority | Recovery of the declared direct baseline | **established, centralized** | DD-C-0098 / DD-021 |
| Shared posterior | Higher decentralized discovery | **established only for the declared selection and interval** | DD-C-0104–DD-C-0108 / DD-022 |
| Selected positive sharing | Every-equilibrium positive sharing | **false in the registered model** | DD-C-0109 / DD-022 |
| Selected shared equilibrium | Centralized top-two value | **strict gap established** | DD-C-0110 / DD-022 |
| Centralized recovery | Robust decentralized recovery | **open** | Requires a separate theorem gate |
| Equilibrium existence | Selection by refinement or learning | **open** | No registered refinement/dynamics evidence |
| One-hit action technology | Unreliable, overlapping, or threshold technology | **open** | Reliable Discovery gate |
| Known source dependence | Missing provenance and identified dependence bounds | **open** | Price of Missing Provenance gate |

## 8. Next-program boundary

No next study ID is allocated here. A continuation may be registered only after
the post-V5 gate records one bounded model, theorem or counterexample target,
literature boundary, state-space cap, independent verifier, corruption plan,
and stop condition. The decision record is
[post-v5-next-program-gate.md](../reports/roadmap-consolidation/post-v5-next-program-gate.md).
Until such registration, DD-019 through DD-022 and their immutable runs remain
closed evidence.
