# DD-001 report

## Evidence run

Initial-grid primary run: `20260720T200447Z_DD-001_6eb12861_ba766d1eba`. DD-001A signature primary run: `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5`. Earlier passing runs remain preserved, including preliminary signature run `20260720T220911Z_DD-001_6822d4c6_40bf5b06a5`; the primary runs contain the authoritative presentations for their respective milestones.

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

The direct profile is an exact coordinate fixed point. All 16 seeded random starts
and one territorial start converged to it; no configured restart improved the
lower bound. The pooled top-eight value is now exactly certified as
`860391662035297/1001129150390625`. Under the audited emulation proposition it is
a valid upper bound because the pooled planner can reproduce every fixed role
profile and then conditionally optimize the portfolio. Thus the canonical exact
interval is

\[
\frac{325089}{390625}\le T_8(16,1/5)\le
\frac{860391662035297}{1001129150390625}.
\]

Its exact gap is `27224111644672/1001129150390625`, approximately
`0.0271934061994395`. The pooled endpoint is not claimed attainable, globally
tight, or equal to the unresolved private-team optimum. The failed improvement
search is evidence about its algorithm and seed set only.

## Scope and next actions

Randomization cannot improve the finite common-payoff optimum because every randomized team strategy is a mixture over deterministic profiles (DD-C-0018). This does not address equilibrium mixing, communication, sequential feedback, heterogeneous searchers, or non-atomic coverage.

## DD-001A signature reduction

DD-C-0023 proves that `(incoming count, fixed-point indicator)` signatures are lossless for the fixed-profile objective and gives necessary-and-sufficient residual Hall conditions with constructive matching reconstruction. Primary signature run `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5` independently reproduces all 21 tiny optima and raw-policy tie counts (DD-C-0024), while raw enumeration through \(M=5\) agrees with both feasibility implementations.

The exact canonical state-space audit (DD-C-0025) finds 148,348,284,928 feasible
labeled signatures and 5,806 individual target orbits. The eight-agent multiset
count before a global target quotient has 85 digits. Independently canonicalizing
agents is not lossless because relative target alignment matters. This is a proved
reduction plus a documented certification barrier, not an alignment-preserving
improvement over the newly exact pooled upper bound. The direct lower bound and
pooled upper endpoint remain distinct, and global optimality remains unresolved.

Next work is the exact \(N=2\) hybrid-threshold milestone. Future canonical certification must use a joint alignment-preserving state or another independently checkable relaxation before spending large compute.

## DD-001B two-searcher thresholds

The four informative hybrid witnesses share one policy family with exact value \(H_M(p)=[1+(M-2)p]/(M-1)\). Exact factorizations against territorial \(2/M\) and direct \(2p-p^2\) prove the restricted three-family thresholds \(1/M\) and \(1/(M-1)\) for every \(M\ge3\) (DD-C-0026).

Primary run `20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1` exhausts 438,734 two-agent signature multisets and certifies the continuous unrestricted informative envelope for \(M=3,4,5\) (DD-C-0027). Raw and signature enumeration reproduce all four original witnesses. At \(p=0\), exact optima \(11/12\) for \(M=3\) and \(2/3\) for \(M=4\) refute extending the three-family theorem to anti-informative clues (DD-C-0028).

DD-001B and the exact pooled-frontier certificate are complete. After the separate
Three Results synthesis, the next DD-001 milestone is an alignment-preserving
admissible upper relaxation; the canonical optimum remains unresolved.
