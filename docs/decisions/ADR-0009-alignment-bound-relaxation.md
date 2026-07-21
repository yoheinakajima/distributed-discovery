# ADR-0009: Alignment-preserving DD-001 upper relaxation

**Status:** accepted for bounded exact audit (DD-001)

## Context

The DD-001 policy signature is lossless for one agent, but independently
sorting each agent's target columns destroys the relative alignment that enters
the product of conditional failure probabilities. The canonical raw signature
profile space is infeasible. A valid upper-bound method must retain joint
within-target information, prove that every private policy profile embeds, and
produce a certificate simpler than the optimization itself.

## Alternatives considered

| Family | Validity and scale | Certificate burden | Decision |
|---|---|---|---|
| Joint target-column variables with exact per-agent feasibility | Lossless, but canonical state is still enormous | Exact combinatorial certificate is large | Retain as a future hierarchy level |
| Non-signaling/local-consistency LP | Valid if all locality constraints are explicit; symmetry reduction is nontrivial | Rational dual certificate possible | Defer until the count relaxation is audited |
| Lagrangian decomposition | Can upper-bound after dualizing cross-target constraints | Requires exact dual reconstruction and a separate feasibility checker | Defer; unnecessary for the first level |
| LP/MILP consistency hierarchy | Potentially strong | Open-source solver plus independently checked dual/cut certificate | Defer; no dependency is justified yet |
| Exact branch and bound | Valid only with an admissible node bound | Potentially very large proof/checkpoint artifact | Reject as the first canonical method |
| Joint-column global count-budget relaxation | Retains all agents jointly at each target; drops only cross-target identities and feasibility beyond the necessary global count total | Two small exact Bellman tables with inequality and equality witnesses | Select |

## Decision

For target (t), retain the aligned incoming-count column

\[
(c_1(t),\ldots,c_N(t)).
\]

For one agent and target, minimize the conditional failure factor over the
locally possible fixed-point indicator. If (q=(1-p)/(M-1)), define

\[
a(c)=\min_{d\in D(c)}\{1-qc-(p-q)d\},
\]

where (D(0)=\{0\}), (D(M)=\{1\}), and
(D(c)=\{0,1\}) for (0<c<M). Every actual factor is at least (a(c)).

The first exact dynamic program computes

\[
F_N(r)=\min_{c_1+\cdots+c_N=r}\prod_i a(c_i).
\]

Every deterministic policy has incoming counts summing to (M). Therefore
every (N)-policy profile has the globally necessary aligned-column budget

\[
\sum_t\sum_i c_i(t)=MN.
\]

Dropping the separate per-agent budgets, fixed-point compatibility across
targets, and residual Hall feasibility enlarges the feasible set. The second
exact dynamic program computes the relaxed minimum average failure,

\[
\frac1M\min_{r_1+\cdots+r_M=MN}\sum_t F_N(r_t).
\]

One minus this quantity is consequently an admissible private-team discovery
upper bound. Cross-agent alignment inside every target contribution is never
sorted away; only cross-target consistency is relaxed.

The optimizer exports both Bellman tables and predecessor witnesses. A separate
verifier checks every Bellman lower inequality and one equality witness for each
state, derives the final bound independently, and must reject a corrupted entry.
No solver or new dependency is required.

## Consequences and evidence boundary

The relaxation may be loose because it can reassign an agent's incoming-count
budget across target columns inconsistently. Equality with a known lower bound
proves the private optimum only after the exact certificate and embedding proof
pass. Equality on a finite benchmark grid is not by itself a general theorem.
Anti-informative cases are retained because the maximizing local fixed-point
choice changes when (p<q).

## Reversal conditions

Replace or strengthen this first hierarchy level if it is not upper-valid on an
exact fixture, if the independent verifier finds a certificate defect, or if a
higher consistency level yields a strictly better audited bound where this
relaxation remains loose.
