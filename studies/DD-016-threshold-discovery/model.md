# Frozen model

There are M >= 2 candidates, one hidden target with posterior
pi=(pi_1,...,pi_M), N >= 1 agents, and a threshold
tau in {1,...,N}. Each agent takes one candidate action. If n_j agents
choose candidate j, it opens exactly when n_j >= tau. With one atomic
target, group discovery is

G(n;pi,tau) = sum_j pi_j 1{n_j >= tau}.

The deterministic planner selects one joint occupancy vector. Independent
mixed actions draw agents separately from one action distribution. A
correlated recommendation can coordinate a joint distribution over action
profiles. Strategic decentralized choice uses individual expected payoffs.
A named selection rule chooses one element from an equilibrium
correspondence; it is not the correspondence itself.

The canonical fixture has M=16, N=8, clue accuracy p=1/5, uniform wrong
clue probability 4/75, and tau=2. Conditional on clue counts C_j, the
pooled posterior is proportional to (15/4)^(C_j). The registered tied-mode
rule has every agent independently mix uniformly over posterior modes. It is
one selected symmetric rule, not a uniqueness claim.

Coverage technology is frozen: one target, deterministic opening at the
threshold, no value beyond opening, no execution failure, no replication
benefit, and no cross-candidate overlap. Results do not transfer automatically
to noisy, reusable, overlapping, or multi-target action technologies.
