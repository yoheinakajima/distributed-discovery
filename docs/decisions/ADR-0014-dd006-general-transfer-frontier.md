# ADR-0014: DD-006A normalized linear transfer frontier

DD-006A retains the two-agent, three-target, uniform-prior, conditionally
independent `2/3`-accurate-signal environment. Each agent reports one label;
the direct recommendation correspondence selects the two posterior-leading
distinct actions. Equal reports have two equally good second actions, so the
run compares both fixed role labels and their public 50/50 average rather than
silently selecting a favorable tie break.

The registered class is a symmetric, ex-post budget-balanced transfer difference
`u_i-u_j` whose observable score is a normalized linear combination of: correct
report (target identity), individual success, sole rescue, and report/action
agreement. A regime admits only features observable under that regime. Each
coefficient is in `{-1,-1/2,0,1/2,1}` and the coefficient L1 norm is at most
one. This prevents scale degeneracy and gives a complete finite 41-table
superset of the prior one-feature score-difference rules.

The run checks every unilateral joint report/action deviation for both fixed
tie roles, their public average, weak and strict pure BNE margins, and exact
ex-post balance. It is a bounded normalized linear class, not all transfer
tables, mixed implementation, or a revelation-principle result.
