# DD-016 report

Primary clean run `20260722T021526Z_DD-016_00271ff8_123b2809e3` passed in
11.998247 seconds, below the registered 90-second estimate and 600-second cap.
It records clean source commit `00271ff8fbcb10012c2ae11e256a772662ea5f2b`,
configuration hash `123b2809e3a495c81d877164948d31cd936401eaa126ab40b1baee6d0ee41f55`,
the dependency lock, input and output hashes, and no random seeds.

For any finite posterior, a deterministic planner can open at most
`min(floor(N/tau),M)` candidates. Assigning exactly tau agents to that many
highest-posterior candidates attains the posterior-mass upper bound, so an
optimal minimum-viable-team allocation exists. The result is not a uniqueness
or strategic-implementation theorem. A 63-row exhaustive small-allocation
audit agrees with the proof.

The equal-split deviation payoff is
`V*pi_j*E[1{K_j>=tau-1}/(K_j+1)]`. At tau one it reduces to the ordinary
split-prize factor; at tau two it subtracts `(1-x_j)^(N-1)`. Their zero-choice
limits are one and zero respectively. Thirty-five exact rational checks match
the finite binomial sums.

The canonical tau-two fixture gives exact discovery probabilities:

- common deterministic posterior mode: `37916217637/98876953125`
  (about 0.383468709731);
- independent uniform selection over tied posterior modes:
  `275661897594857/576650390625000` (about 0.478039904380);
- private clue-following: `194017/390625` (0.49668352);
- deterministic paired planner: `223779310319051/333709716796875`
  (about 0.670580744448).

The selected tied-mode mixture has expected distinct candidates
`222783285994256/129746337890625`, viable candidates
`4605284003019928/3243658447265625`, largest crowd
`21276151146203888/3243658447265625`, and pair-collision probability
`3368373871489/4449462890625`. These are derived fractions; supplied decimals
were regression targets only.

Across tau one through eight, common deterministic mode and registered
tied-mode mixing lower discovery relative to private clue-following at tau one
and two, then raise it at tau three through eight. The planner strictly exceeds
the selected mixture in every row. Only one viable coalition can form at tau
five through eight; planner diversification strictly beats common mode at tau
one through four and ties it thereafter.

Method A exhausts all 490,314 labeled clue-count vectors. Method B enumerates
67 false-label occupancy orbits. Both normalize to one, reduce to 30 aggregate
signal classes, and agree on every exact phase row. Altered posterior weight,
occupancy probability, mode count, and planner mass are all rejected. The
tied-mode mixture is one registered selection rule, not the complete strategic
equilibrium correspondence; coalition stability and equilibrium selection are
reserved for DD-017.

Claims DD-C-0071 and DD-C-0072 are verified proof-backed statements.
DD-C-0073 and DD-C-0074 are independently reproduced bounded computations.
