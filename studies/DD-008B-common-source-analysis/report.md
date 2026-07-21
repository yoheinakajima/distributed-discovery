# DD-008B report

Primary clean run `20260721T192412Z_DD-008B_649deb08_29dbeaf3a9` passed. It
records 105 exact threshold rows, reproduces all 126 immutable DD-008A
classification rows, matches 84 separately enumerated private/planner payoff
margins through `N=5`, and checks 16,368 instantiated positive-kernel identities
through `N=32`. Both the altered-threshold and altered-census corruption tests
are rejected.

The analytic result is stronger than the prior finite census: for arbitrary
finite `N>=2`, the private thresholds are strictly decreasing and give a complete
weak pure source-count equilibrium characterization. The planner thresholds are
also explicit. Their first margins establish an all-common trap interval
`[p(1-p)(N-1)/N,p(1-p))` of exact width `p(1-p)/N`.

The audit also retains a negative result. Private acquisition is not globally
below planner acquisition: at `(N,p,c)=(3,4/5,13/375)`, the unique equilibrium
uses two independent sources while the unique planner optimum uses one. This
prevents the focused paper from describing the Common-Source Trap as a universal
under-acquisition theorem.
