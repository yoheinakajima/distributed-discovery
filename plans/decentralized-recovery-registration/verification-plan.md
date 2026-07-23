# Independent exact verification design

This is a future design retained for audit completeness. No scientific
certificate is executed in the stopped gate.

## Method A — symbolic posterior-region classifier

Input a normalized rational posterior, reduce by a recorded target
permutation, evaluate the labeled simultaneous inequalities, build the
nodewise sequential best-response correspondence, derive Agent 1 continuation
values, and emit complete Nash/SPE correspondence rows plus recovery classes.
It may use the analytic region boundary but may not read Method B outputs.

## Method B — primitive enumerator

Start from immutable DD-021 target, prior, signal alphabet, and channel-law
records. Reconstruct every positive pooled posterior independently. Enumerate
all nine action profiles and every unilateral deviation. Enumerate all three
first actions, nine continuation actions, 27 Agent-2 contingent strategies,
and 81 pure strategy profiles; check second-mover sequential rationality at
all nodes and Agent-1 deviations directly. Compute discovery, payoffs, `P_2`,
and `V_2` without importing Method A's ordering or classification logic.

## Shared inputs and forbidden sharing

Shared inputs are immutable channel records, rational parsing conventions,
target labels, and output schemas. Method B may not import Method A's region
labels, equilibrium predicates, ordered-posterior classifier, continuation
classifier, or recovery function. A common serializer is allowed only after
objects are computed.

## Required agreement and certificates

Check normalization, target permutations, payoff budget, discovery bounds,
private-baseline reconstruction, centralized reconstruction, equilibrium
completeness, best/worst aggregation, pointwise-to-channel lift, exact output
hashes, and source provenance. A certificate would contain input hashes,
method versions, every posterior-class row, every disagreement field, and a
zero-disagreement summary. The stop means no such certificate is produced.
