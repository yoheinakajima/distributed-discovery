# DD-005 research brief — Overlapping Coverage

## Motivating question

Which information-frontier, protocol-loss, redundancy, and recovery-budget concepts remain useful when actions cover overlapping sets, multiple outcomes matter, or discovery value is nonbinary?

## Minimum viable model

- A finite universe of elementary outcomes with nonnegative weights.
- Each feasible action covers a declared subset; a portfolio's value is weighted union coverage.
- A finite evidence state induces posterior weights or state-dependent coverage.
- A planner has a cardinality budget \(B\); protocols may repeat actions.
- Start with deterministic monotone submodular coverage, then add stochastic outcomes only after exact fixtures pass.

The atomic box model is the special case where actions cover singleton candidate states and exactly one state has value.

## Relationship to the canonical benchmark

Canonical top-posterior ranking is exact because singleton coverage is modular. With overlap, a lower-ranked action may have larger marginal coverage than a higher-ranked duplicate. DD-005 preserves the information/action accounting but replaces the physical coverage link, testing which atomic identities fail and which generalize.

## Main quantities

- Exact portfolio frontier and protocol loss under weighted coverage.
- Marginal coverage, pairwise overlap, total curvature, and submodularity ratio where defined.
- Greedy value and approximation gap.
- Recovery budget under exact and greedy frontiers.
- Action-label duplication versus covered-outcome redundancy.
- Robustness value of repeated/noisy actions in later models.

## Adjacent literature

Nemhauser, Wolsey, and Fisher (1978) provide classical monotone-submodular maximization; Golovin and Krause (2011) provide adaptive extensions under additional hypotheses; Hazon and Kaminka (2008) warn that redundancy trades efficiency for robustness. Canonical redundant-hit accounting is an atomic identity, not a general overlap formula.

## Likely methods

Exact subset enumeration; integer programming only after a solver/certificate ADR; greedy and lazy-greedy benchmarks; generated hypergraph fixtures; counterexample search for atomic diagnostics; curvature-sensitive bounds; symbolic two/three-action examples.

## Falsifiable questions

1. What is the smallest overlap fixture where top individual posterior value is not the optimal portfolio?
2. Can two protocols have the same distinct-action count but different covered value and protocol loss?
3. Which overlap functional, if any, yields an exact decomposition analogous to redundant hits?
4. How unstable is the recovery budget when an exact frontier is replaced by greedy approximation?

## Dependencies and risks

Depends on DD-000 definitions; DD-004 consumes adaptive coverage only after static structure is stable; DD-007 needs estimable overlap definitions. Risks include mixing action and outcome duplication, claiming exact frontiers from approximations, negative or complementary values that violate submodularity, and using synthetic random hypergraphs with no interpretable structure.

## First executable experiment

Enumerate every portfolio for hand-designed universes up to eight outcomes, ten actions, and budget four. Include atomic controls and systematically introduced overlaps. Compare exact, top-individual, and marginal-greedy portfolios; automatically minimize counterexamples to each atomic diagnostic.

## Completion criteria

- Coverage value and assumptions are explicit and tested.
- Exact small frontiers validate every approximation implementation.
- Atomic identities are either proved under stated conditions or refuted by minimal witnesses.
- Recovery budgets state whether they use exact or approximate frontiers.
- Robustness benefits are separated from pure duplicate waste.
