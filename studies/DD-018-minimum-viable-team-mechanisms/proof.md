# Analytic and exact-computation record

For four agents and threshold two, the deterministic planner can open at most
two candidates. Because candidate value is atomic at opening and posterior
mass is weakly descending, assigning exactly two agents to each of candidates
one and two attains the upper bound `pi_1 + pi_2`. This is the DD-C-0071
planner theorem specialized to the DD-018 boundary.

For ordinary threshold-adjusted equal split, an agent at a candidate with
occupancy `n_j >= 2` receives posterior expected payoff `pi_j/n_j`; below two,
payoff is zero. Team tokens and exclusive rights restrict eligibility to the
two assigned agents. Sole-team rescue sets every payout to zero unless exactly
one candidate is viable. Marginal coalition contribution pays `pi_j/2` only at
occupancy exactly two. In every case, summed posterior expected payouts are no
greater than posterior mass opened, so the registered rules use no external
subsidy.

The primary evaluator enumerates all `3^4=81` labeled action profiles. At every
recommended profile it enumerates every unilateral destination, every named
pair and joint destination pair, and every exact-size-two tau-player deviation.
It also counts every labeled pure Nash profile under unilateral deviations; the
pairwise market instead counts pure equilibria of the nine two-pair candidate
choices. Authoritative central and random assignments have no post-assignment
equilibrium multiplicity and are recorded as not applicable.

The independent evaluator constructs its own full action table, independently
replaces coalition actions, checks strict-member improvements, recomputes
equilibrium counts, reconstructs recommendation supports, and exhausts all
15 three-candidate occupancy vectors for the planner value. The 50 rows agree
exactly. This is a finite verification record, not a proof for mechanisms,
posteriors, agent counts, or thresholds outside the frozen configuration.
