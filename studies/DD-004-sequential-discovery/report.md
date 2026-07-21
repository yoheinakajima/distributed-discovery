# DD-004 perfect-elimination report

Primary immutable run `20260721T050038Z_DD-004_8ab02e7f_71d84de7c4` fixes a
finite atomic model with rational priors, at most four non-repeated perfect
tests, success stopping, and every ordered batch composition of the test budget.
The exact Bellman DP agrees with a separate exhaustive no-repeat policy-path
enumerator on all tiny `M<=4, B<=4` cases.

For the asymmetric eight-target prior, every schedule with budget four has
terminal discovery `7/10`; fully parallel uses four actions in one round, while
fully sequential uses expected actions `109/40` over expected rounds `109/40`.
For the uniform-eight control, every schedule has terminal discovery `1/2`;
parallel uses four actions in one round and sequential uses expected actions and
rounds `13/4`. Thus perfect failure feedback does not improve terminal discovery
under the fixed count objective, but it can reduce expected actions while adding
rounds. This is a bounded model result, not a noisy-test or general adaptivity
claim.
