# Frozen model and mechanism semantics

Let a single hidden target lie in three candidates with common posterior
`pi_1 >= pi_2 >= pi_3 > 0`. Four labeled agents choose one candidate each. A
candidate is discovered exactly when at least two agents choose it. There is no
value above threshold, execution noise, action cost, or information-report
stage. The planner therefore assigns size-two teams to candidates one and two,
with discovery `pi_1 + pi_2`.

All strategic prize rules are evaluated in posterior expectation. Ordinary
threshold-adjusted equal split gives an agent at a viable candidate `j` payoff
`pi_j/n_j`. Team tokens and exclusive rights restrict prize eligibility to the
assigned size-two coalition. Sole-team rescue pays only when exactly one
candidate is viable. Marginal coalition contribution pays `pi_j/2` to each
member only when occupancy is exactly two. Total payout never exceeds opened
posterior mass, and no external subsidy is permitted.

Central assignment and random matching are authoritative: their deviations are
not applicable, not strategically deterred. The correlated mediator is
nonbinding. Pairwise matching fixes pairs `(1,2)` and `(3,4)` and permits a
binding joint candidate choice within each pair; its relevant deviations are
pair deviations. Other noncommitted rows check unilateral, every pair, and
every size-two (`tau`-player) strict-member deviation separately. Because
`tau=2`, the last two sizes coincide but remain separately named records.

The five posterior fixtures and every institutional field are frozen in the
configuration. The result is a bounded common-posterior allocation census. It
does not establish report truthfulness, coalition-proofness, or a general
implementation theorem.
