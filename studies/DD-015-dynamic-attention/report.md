# DD-015 report

Primary clean run `20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a` passed in
13.971626 seconds from source commit `92d53ac111812089c67bec049d5eb4e41d676cf0`.
It evaluates 32 rational parameter cells and 64 fixed-budget/stopping objective
rows. Exact common-information dynamic programming exhausts all 27
private-clue prescriptions at each reachable state. The separate labeled
policy-tree verifier checks both protocols across 5,184 unique target/signal
paths, yielding 128 exact value checks and four corruption rejections.

Under full duplicate credit, posterior-mode choice is a pure sequential
Bayesian equilibrium: an agent's payoff is its own posterior correctness and is
unaffected by later duplicates. The common-payoff planner strictly exceeds this
autonomous equilibrium in 38 of 64 rows. Autonomous policies exhibit positive
previous-action following in 32 rows and positive leaning against a repeated
prior action in 50 rows, so visible histories can produce either local response.

Stopping on success uses fewer expected actions than fixed budget in all 32
parameter cells. This efficiency comparison is separate from terminal discovery
and from fixed-budget visibility because continuation reveals that prior actions
failed.

The bounded visibility-dispersion candidate fails. Against otherwise identical
history-hidden Bayes action, visible-action inference improves neither discovery
nor expected distinct actions in any of the 32 fixed-budget cells. It strictly
reduces both in 18 and ties in 14. This is a first-class bounded negative result,
not a general theorem that visibility is harmful.

Claims DD-C-0079 through DD-C-0081 passed separate proposition,
computational-result, and negative-result audits. The model does not cover
equal-split congestion, signaling equilibria, mixed strategies, human behavior,
or threshold-team rewards. The threshold-two extension remains separately
labeled and must not be inferred from this baseline.
