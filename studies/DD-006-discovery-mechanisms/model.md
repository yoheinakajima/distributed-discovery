# Registered score-difference model

ADR-0012 fixes two agents, three equiprobable targets, conditionally independent
signals of accuracy `2/3`, truthful direct recommendations, and three observable
scores: target identity, individual success, and sole rescue. Each agent receives
coefficient `c` times its score minus its peer's score, for `c ∈ {-1, 0, 1}`.
The census evaluates pure Bayesian report-action deviations exactly; it does not
search arbitrary transfer tables or mixed equilibria.
