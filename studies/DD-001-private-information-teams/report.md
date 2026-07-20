# DD-001 report

## Evidence run

Primary run: `20260720T200447Z_DD-001_6eb12861_ba766d1eba`. Two earlier passing runs are preserved: the first covered 17 grid points; the second covered the final 21 points before the generated figure was added. The primary run contains the complete configuration, exact policies, phase data/figure, canonical restarts, validation, checksums, seeds, and termination reasons.

## Certified tiny-grid results

All 21 configured optima are certified by exhaustive enumeration of every agent-symmetric deterministic policy multiset. The largest per-accuracy search evaluated 32,896 profiles. Exact conditional-factorization values matched an independent target/signal enumeration for every winner, with probability mass exactly one and the bounds

\[
G_{\text{direct}}\le T_N(M,p)\le V_N(I_{\text{pooled}})
\]

holding throughout.

Direct clue-following was optimal at 5 grid points and strictly suboptimal at 16. Some gains are mechanically territorial when \(N\ge M\), but four informative cases with \(N<M\) also refute general clue-following optimality. In particular:

- \(M=3,N=2,p=2/5\): exact optimum \(7/10\), direct \(16/25\), gain \(3/50\).
- \(M=3,N=2,p=7/15\): exact optimum \(11/15\), direct \(161/225\), gain \(4/225\).
- \(M=4,N=2,p=3/10\): exact optimum \(8/15\), direct \(51/100\), gain \(7/300\).
- \(M=4,N=2,p=13/40\): exact optimum \(11/20\), direct \(871/1600\), gain \(9/1600\).

One optimal representative for the first two cases is a hybrid: one agent always searches location 0, while the other uses policy `(1,1,2)` under zero-based indexing. Its six location/agent relabelings tie in the reduced enumeration. This is an exact finite counterexample to general clue-following optimality, not a phase-boundary theorem.

## Canonical lower bound and unresolved optimum

For \(M=16,N=8,p=1/5\), direct clue-following has exact value

\[
1-(4/5)^8=325089/390625=0.83222784.
\]

The direct profile is an exact coordinate fixed point. All 16 seeded random starts and one territorial start converged to it; no configured restart improved the lower bound. The pooled-planner value `0.859421246199` is an independently reproduced numerical upper benchmark under greater information and assignment authority; 1 is the universal exact upper bound. Global private-team optimality remains unresolved. The failed improvement search is evidence about this algorithm and seed set only.

## Scope and next actions

Randomization cannot improve the finite common-payoff optimum because every randomized team strategy is a mixture over deterministic profiles (DD-C-0018). This does not address equilibrium mixing, communication, sequential feedback, heterogeneous searchers, or non-atomic coverage. Next work should prove the observed \(N=2\) hybrid thresholds and implement a certified upper-bound method before spending more compute on the canonical instance.
