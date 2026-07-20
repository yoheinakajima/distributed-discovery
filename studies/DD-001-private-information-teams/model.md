# DD-001 model — private-information teams without communication

## Primitives

There are \(M\ge2\) candidate locations, \(N\ge1\) searchers, and one target \(\theta\), initially uniform on \(\{0,\ldots,M-1\}\). Conditional on \(\theta\), private signals are independent and

\[
\Pr(X_i=x\mid\theta)=
\begin{cases}
p,&x=\theta,\\
(1-p)/(M-1),&x\ne\theta.
\end{cases}
\]

A deterministic role policy is a complete function \(f_i:\{0,\ldots,M-1\}\to\{0,\ldots,M-1\}\). The team commits to the labeled profile \(f=(f_1,\ldots,f_N)\) before the target and signals are realized. At action time searcher \(i\) observes only \(X_i\), cannot communicate, and takes action \(f_i(X_i)\). Shared or private randomization may be selected ex ante, but DD-C-0018 shows that some deterministic profile weakly dominates every randomized mixture for this finite common-payoff optimum.

The team value is

\[
T_N(M,p)=\max_f \Pr\left(\theta\in\{f_1(X_1),\ldots,f_N(X_N)\}\right).
\]

This M6 study does **not** implement a communication budget, sequential actions, strategic rewards, nonuniform priors, heterogeneous accuracy, or overlapping coverage.

## Exact fixed-profile formula

For policy \(f_i\) and target \(t\), define

\[
s_i(t)=\Pr(f_i(X_i)=t\mid\theta=t)
=\sum_{x:f_i(x)=t}\Pr(X_i=x\mid\theta=t).
\]

Conditional signal independence gives

\[
G(f)=\frac1M\sum_{t=0}^{M-1}\left[1-\prod_{i=1}^N(1-s_i(t))\right].
\]

`evaluate_formula` computes this expression with `Fraction`. `evaluate_direct` independently sums over all \(M^{N+1}\) target/signal tuples and also returns total probability mass. Every exact-grid winner was checked by both paths with normalization exactly one.

## Symmetries and search size

Each agent has \(M^M\) deterministic policies, so labeled profiles number \(M^{MN}\). Because the common objective is invariant to agent permutation, exhaustive optimization enumerates policy multisets only:

\[
\binom{M^M+N-1}{N}.
\]

No location-label symmetry is used in the completeness count; retaining it keeps the certificate transparent. The largest configured case, \(M=4,N=2\), has 256 policies per agent, 65,536 labeled profiles, and 32,896 agent-symmetric profiles per accuracy. This is below the configured 50,000-profile guardrail. The canonical \(M=16,N=8\) space is intentionally not enumerated.

## Benchmarks and bounds

- Direct clue-following uses \(f_i(x)=x\) and has value \(1-(1-p)^N\).
- Territorial assignment gives searcher \(i\) a constant action \(i\bmod M\), with value \(\min\{N,M\}/M\).
- The private-team frontier is at least the direct value because clue-following is feasible.
- A pooled planner that observes all signals and retains assignment authority can emulate any private-team profile, so \(T_N(M,p)\le V_N(I_{\text{pooled}})\) under that explicit emulation condition (DD-C-0019).

## Bounded canonical optimization

For one coordinate \(i\), hold other policies fixed and let \(w_t\) be their conditional probability of all failing at target \(t\). For observed signal \(x\), the exact best response chooses action \(a\) maximizing

\[
w_a\Pr(X_i=x\mid\theta=a).
\]

The implementation performs cyclic exact best responses until a coordinate fixed point or a configured sweep limit. This is coordinate ascent, not branch-and-bound: every final value is a constructive lower bound. Multiple seeds and an exact local-deviation check do not certify global optimality.
