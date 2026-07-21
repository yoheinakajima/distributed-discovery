# ADR-0016: DD-009 aligned architecture atlas

DD-009 fixes `M=3`, `N=2`, a uniform target, `2/3`-accurate signals, and an
independent-source cost of `1/8` per agent. The atlas crosses five declared axes
but does not evaluate their full Cartesian product blindly. A deterministic
validity predicate classifies all 288 cells and evaluates only the 20 coherent
cells. Every rejection and reason remains in the output registry.

The primary evaluator uses exact target/signal state enumeration. It reports
channels, information cost, expected actions, action quality, distinct actions,
discovery, protocol loss against the signal-contingent two-action planner,
average private payoff, social net value net of information and external
transfer cost, transfer budget, rounds, truthfulness, obedience, and a precisely
scoped equilibrium-multiplicity field. Non-strategic cells report their single
registered deterministic profile; DD-006A and DD-006B report unilateral
best-response multiplicity at the truthful profile, not total game equilibria.

Pareto dominance maximizes discovery, action quality, and social net value and
minimizes information cost, external transfer budget, and rounds. Incentive
labels are displayed but excluded from that ordering because protocol control,
selected equilibrium, weak implementation, and strict implementation are not a
single cardinal scale. The atlas is a finite synthetic comparison, not a
universal ranking or real-world recommendation.
