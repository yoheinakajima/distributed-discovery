# DD-001 report

## Evidence run

Initial-grid primary run: `20260720T200447Z_DD-001_6eb12861_ba766d1eba`. DD-001A signature primary run: `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5`. DD-001B threshold primary run: `20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1`. Alignment-bound primary run: `20260721T022739Z_DD-001_358cb1eb_cd16846ba5`. Earlier passing runs remain preserved; these primary runs contain the authoritative presentations for their respective milestones.

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

## Exact canonical optimum

For \(M=16,N=8,p=1/5\), direct clue-following has exact value

\[
1-(4/5)^8=325089/390625=0.83222784.
\]

The direct profile is an exact coordinate fixed point. The earlier 17-start search
did not prove global optimality. The alignment-preserving count-budget relaxation
now gives the exact upper bound `325089/390625`, equal to the attainable direct
value. Its certificate retains every agent jointly within a target column and
relaxes only cross-target consistency beyond the necessary global incoming-count
budget. Consequently

\[
T_8(16,1/5)=\frac{325089}{390625}=0.83222784.
\]

The deterministic and ex-ante randomized optima coincide. The independent
verifier checks every Bellman lower inequality and an exact equality predecessor
for each state without re-running the optimizer, and rejects a corrupted final
value. The prior exact pooled upper endpoint remains valid but is superseded as a
tight characterization of the private team.

## Scope and next actions

Randomization cannot improve the finite common-payoff optimum because every randomized team strategy is a mixture over deterministic profiles (DD-C-0018). This does not address equilibrium mixing, communication, sequential feedback, heterogeneous searchers, or non-atomic coverage.

## DD-001A signature reduction

DD-C-0023 proves that `(incoming count, fixed-point indicator)` signatures are lossless for the fixed-profile objective and gives necessary-and-sufficient residual Hall conditions with constructive matching reconstruction. Primary signature run `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5` independently reproduces all 21 tiny optima and raw-policy tie counts (DD-C-0024), while raw enumeration through \(M=5\) agrees with both feasibility implementations.

The exact canonical state-space audit (DD-C-0025) finds 148,348,284,928 feasible
labeled signatures and 5,806 individual target orbits. The eight-agent multiset
count before a global target quotient has 85 digits. Independently canonicalizing
agents is not lossless because relative target alignment matters. This is a proved
reduction plus a documented enumeration barrier. The later count-budget
relaxation resolves the canonical objective without enumerating this signature
space.

## DD-001B two-searcher thresholds

The four informative hybrid witnesses share one policy family with exact value \(H_M(p)=[1+(M-2)p]/(M-1)\). Exact factorizations against territorial \(2/M\) and direct \(2p-p^2\) prove the restricted three-family thresholds \(1/M\) and \(1/(M-1)\) for every \(M\ge3\) (DD-C-0026).

Primary run `20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1` exhausts 438,734 two-agent signature multisets and certifies the continuous unrestricted informative envelope for \(M=3,4,5\) (DD-C-0027). Raw and signature enumeration reproduce all four original witnesses. At \(p=0\), exact optima \(11/12\) for \(M=3\) and \(2/3\) for \(M=4\) refute extending the three-family theorem to anti-informative clues (DD-C-0028).

## Alignment-preserving count-budget relaxation

DD-C-0037 proves the relaxation is an admissible upper bound for every symmetric-
report DD-001 parameter triple. The immutable primary run reproduces all 21 prior
tiny optima exactly and remains upper-valid on two anti-informative fixtures. It
is deliberately not claimed tight in general: at \(M=3,N=2,p=0\) it returns one
against the exact optimum \(11/12\). Canonically, its target-resource pattern is
sixteen copies of eight and it meets the direct lower bound, proving DD-C-0038.

The next DD-001 question is structural tightness outside the canonical fixture;
the active continuation queue moves first to DD-002 selection robustness.
