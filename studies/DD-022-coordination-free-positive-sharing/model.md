# Frozen model and equilibrium concepts

Nature draws `theta in {0,1}` uniformly. There are two anonymous agents. Signal
accuracy is `p in [1/2,1]` and dependence is `rho in [0,1]`. With probability
`rho`, both agents receive the same common-source signal `Y`, with
`P(Y=theta)=p`. With probability `1-rho`, they receive conditionally independent
signals `X_1,X_2`, each correct with probability `p`. The world-level source
mixture is drawn once; its law and parameters are common knowledge.

Each agent simultaneously chooses one target. If `k>=1` agents select the true
target, each receives `1/k`; otherwise both receive zero. Thus the realized
total prize is exactly the group-discovery indicator. There are no roles,
assignment, visible prior actions, move order, correlated public randomization,
post-disclosure communication, personalized recommendations, binding territory,
or action authority. Behavioral randomization is independent and private.

## Private-information selection

Each agent observes only their own signal. The primary theorem restricts the
selected strategy class to anonymous label-equivariant behavioral rules: follow
the observed signal with probability `r` and choose the other target with
probability `1-r`. The study derives the complete symmetric Bayes–Nash
equilibrium inside this declared class. It separately enumerates all labeled
pure Bayesian strategy profiles from the four maps `{constant 0, constant 1,
follow, oppose}` and does not identify the selected symmetric result with that
full correspondence.

## Shared-information selection

Both realized signals become public before action. For every positive-
probability public profile, agents share the exact posterior and play the
resulting two-action equal-split game. The selected outcome uses an identical
mixed action distribution that depends only on the common posterior, with
independent private mixing. This posterior-only, provenance-blind class is
narrower than the ownership-aware strategy space. The complete posterior-game
pure correspondence and private pure Bayesian correspondence are stored
separately. Zero-probability public
profiles at `rho=1` are labeled off path rather than assigned evidentiary
weight.

## Outcomes and baselines

For each regime the study reports discovery, expected payoff per agent, action
collision, action diversity (probability of distinct actions), expected number
of distinct actions, and average action quality. Direct private clue-following
means `r=1` whether or not it is the selected private equilibrium. The
centralized DD-021 top-two benchmark is `V_2=1` in this binary two-action model;
it is an upper benchmark, not an implementation result. A role-dependent best
asymmetric pure allocation, when shown, is labeled coordinated.

The public agreement pattern updates beliefs about the latent source branch;
it does not reveal that branch. On disagreement, ownership-aware symmetric
rules can split the targets and are an explicit selection caveat.

“Coordination-free” means exactly this frozen simultaneous anonymous protocol.
It does not mean decentralized generally, and asymmetric pure role allocation
is never described as coordination-free.
