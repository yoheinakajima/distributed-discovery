# Decentralized Recovery registration stop

Decision: `stop-classical-overlap`
Issue: #162
PR: #163
Study ID allocated: no
Claim or run created: no

## Attempt

The gate froze the smallest bridge from DD-021's centralized posterior top-two
recovery to robust autonomous recovery: three targets, two agents, a pooled
public posterior, one reliable action each, equal sharing of a correct-target
prize, complete simultaneous pure Nash, and complete pure SPE under fixed
sequential arrival with visible prior occupancy.

The final candidate was to characterize exactly when every sequential SPE
covers a centralized top-two set, retain the complementary failure/equality
region, and average that pointwise classification over the inherited DD-021
`M=3,N=2` channels against `P_2(W)` and `V_2^(2)(W)`.

## Exact stop reason

Once the public posterior `mu` is fixed, the simultaneous game is exactly a
singleton congestion/resource-selection game with payoff `mu_j/n_j` and
Rosenthal potential `sum_j mu_j H_(n_j)`. The sequential institution is a
finite perfect-information version solved by ordinary backward induction.

For generic ordered posterior masses `a>b>c`, every pure Nash equilibrium and
every pure SPE cover the top two targets exactly when `b>a/2`. Equality retains
both a top collision and a top-two split, and `b<a/2` selects top collision.
The full labeled inequalities handle all ties but add no different mechanism.
Thus visibility and move order do not enlarge robust recovery in the frozen
model, and the complete characterization is a direct classical specialization.

Korman and Rodeh already place known box distributions, selfish multiple
searchers, group success, congestion reward, natural equal sharing, equilibrium
selection, efficiency, and robustness in a broader multiple-round search
model. The DD-021 private and centralized comparators are meaningful
post-processing labels, but they do not create new equilibrium content.

## Why no information-conditioned residual survived

Private evidence is fully compressed into the public posterior before action.
The equilibrium inequalities require only the posterior resource values. The
direct-private baseline is not used to choose equilibrium actions, and the
centralized comparator only tests the covered set afterward. Averaging over a
finite channel changes weights, not the pointwise game or boundary. The six
required ingredients can be named together, but their conjunction does not
produce a nonclassical statement.

## Why the model is not broadened

Adding reliability, transfers, public seeds, refinements, dynamics, licenses,
extra targets/agents, or provenance uncertainty would change the registered
question and use parameters to evade the stop. Those objects already belong to
later program gates. The negative decision is therefore preserved at the
frozen scope.

## Unaffected evidence

DD-002, DD-017, DD-018, DD-021, DD-022, DD-C-0097 through DD-C-0110, all 51
manifests, all immutable outputs, and all seven papers remain unchanged. The
stop creates no scientific result. It completes an overlap gate and makes
Reliable Discovery the next executable program.
