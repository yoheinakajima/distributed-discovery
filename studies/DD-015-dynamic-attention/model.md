# Frozen model boundary

There are three uniformly likely targets and `N in {2,3}` sequential agents.
One common shared clue has accuracy `q`; each agent's private clue has accuracy
`p`. Conditional on the target, all clue draws are independent and each wrong
label is uniform over the other two labels.

Every agent observes the shared clue, its private clue, and the declared public
history. Under the fixed-budget objective, the history contains actions only
and all `N` agents act. Under stopping on success, play continues only after an
observed failure, so the public posterior also conditions on the target differing
from every prior action. Expected actions and rounds equal the number of reached
sequential decision nodes; terminal discovery remains a distinct quantity.

Autonomous agents receive full duplicate credit: an agent earns one exactly
when its own action is the target. At every reached information set it chooses
a posterior mode, breaking ties by the lowest action label. This is a pure
sequential Bayesian equilibrium for the declared reward because later actions
do not affect the agent's payoff.

The social planner cannot observe private clues directly. At each shared-clue
and public-history state it commits to a prescription mapping the current
private clue to an action. Exact common-information dynamic programming selects
the prescription maximizing union discovery. A materially separate labeled
policy-tree enumerator recomputes the resulting values.
