# ADR-0012: DD-006 score-difference mechanism fixture

## Decision

DD-006 first enumerates three symmetric, ex-post budget-balanced score-difference
rules on `M=3`, `N=2`, uniform target, and independent signal accuracy `2/3`.
Each agent reports one of three signals, receives the direct recommendation equal
to its report, and chooses an action. The transfer is the difference between the
agent's and peer's observable score, multiplied by `-1`, `0`, or `1`.

The observable score is respectively correct report against target identity,
individual action success, or sole rescue. The run checks every unilateral joint
report/action deviation from truthful reporting and recommended action under pure
Bayes–Nash expectations. It separately enumerates the 27 symmetric deterministic
report/action profiles. This is not a search over arbitrary transfer tables,
dominant strategies, mixed equilibria, hidden actions, collusion, or a revelation
principle.

## Rationale

The three rules are finite, symmetric, rational, ex-post budget balanced, and
make the observability boundary concrete without silently enlarging mechanism
space. A negative result remains a bounded family result.
