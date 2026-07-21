# ADR-0010: Exact DD-002 equilibrium-selection catalogue

**Status:** accepted for bounded exact audit (DD-002)

## Context

The frozen DD-002 fixture has a complete pure-equilibrium correspondence and one
anonymous-symmetric mixed selection. Its known disclosure reversal is explicitly
selection-dependent. Robustness must be tested without changing the posterior
games, silently favoring one equilibrium, or introducing a continuous numerical
root when exact finite procedures are available.

Every message game has two players, three locations, posterior masses
\(\mu=(\mu_0,\mu_1,\mu_2)\), and equal-split payoffs. If the action profile is
\((a,b)\), player payoff is \(\mu_a\) when actions differ and \(\mu_a/2\) when
they coincide. Discovery is the posterior mass of the union of chosen actions.

## Alternatives considered

| Procedure | Definition and evidence burden | Decision |
|---|---|---|
| Best pure equilibrium | Maximum discovery over the complete pure correspondence | Select as an optimistic envelope; report that it is a welfare selector, not equilibrium uniqueness |
| Worst pure equilibrium | Minimum discovery over the complete pure correspondence | Select as a pessimistic envelope |
| Potential-maximizing equilibrium | Exact Rosenthal potential; ties require an explicit rule | Select, uniformly over all labeled global potential maximizers |
| Best-response basin | Requires initial-state and move tie-breaking rules | Select, with uniform initial pure profiles and uniform strict best-response moves |
| Risk dominance | No canonical extension from \(2\times2\) to the present three-action games | Reject for this milestone |
| QRE or replicator dynamics | Continuous branches, precision, continuation, and root certification add burden | Defer; unnecessary for the first exact catalogue |
| Logit stochastic stability | Requires a noise family and limiting-tree certificate | Defer until the exact basin result identifies a need |
| Trembling-hand/proper equilibrium | Requires a fully specified perturbation sequence and may remain set-valued | Defer |

The existing anonymous-symmetric equilibrium and the two-action planner remain
baseline comparators. Randomized disclosure remains outside this milestone.

## Exact potential

For a posterior \(\mu\), define

\[
\Phi(a,b)=
\begin{cases}
\frac32\mu_a,&a=b,\\
\mu_a+\mu_b,&a\ne b.
\end{cases}
\]

This is the Rosenthal potential obtained by summing \(\mu_x/k\) for the first
and second user of each occupied location. Every unilateral payoff difference
equals the corresponding potential difference. Hence every global potential
maximizer is a pure Nash equilibrium, and every strict best-response move raises
\(\Phi\). The finite dynamics below therefore terminate.

## Selected procedures

For each public message:

1. **Best pure:** select the largest discovery value in the complete pure Nash
   correspondence.
2. **Worst pure:** select the smallest discovery value in that correspondence.
3. **Uniform potential maximum:** maximize \(\Phi\) over all nine labeled action
   profiles and average discovery uniformly over every tied maximizer. Tied
   profiles and distinct tied discovery values are stored.
4. **Uniform strict-best-response basin:** start uniformly over all nine labeled
   pure profiles. At a non-equilibrium state, form every unilateral move to a
   payoff-maximizing action that strictly improves the mover's payoff, and choose
   uniformly among those player/action moves. Absorption probabilities and every
   transition are exact rational numbers.

Partition values average message values using exact message probabilities. A
refinement is harmful for a rule exactly when its partition value is lower than
the coarser value. Counts of improvements, harms, and ties are reported
separately. Potential ties and basin branch dependence are never collapsed into
an unsupported uniqueness claim.

## Certificate and scope

The primary implementation exports all posteriors, pure equilibria, potential
maximizers, strict-best-response transitions, per-initial-state absorption
tables, partition aggregates, and refinement comparisons. A separate verifier
reconstructs the games directly from the likelihood, checks the exact-potential
identity on every unilateral deviation, verifies each absorption Bellman
equation rather than solving the dynamics, and recomputes all aggregates. A
corrupted absorption entry must be rejected.

This is a complete exact catalogue only for the frozen four-evidence-state,
three-location, two-searcher deterministic-disclosure fixture. Equality or
reversal counts are not extrapolated to other games or disclosure kernels.
