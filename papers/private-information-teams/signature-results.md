# Lossless policy signatures and the canonical barrier

For each deterministic policy, let \(c_t\) count signals sent to target \(t\), and let \(d_t\) indicate whether target \(t\)'s correct signal is sent to itself. Under the symmetric clue model,

\[
s(t)=q c_t+(p-q)d_t,\qquad q=\frac{1-p}{M-1}.
\]

The complete fixed-profile objective therefore depends on a policy only through \(((c_t,d_t))_t\). This compression is exact, not heuristic. After diagonal assignments are removed, signature realizability is a duplicated-column matching problem. Hall's conditions reduce to singleton bounds: with \(n_0\) nonfixed rows and \(r_t=c_t-d_t\), a nonfixed target requires \(r_t\le n_0-1\), while a fixed target requires \(r_t\le n_0\). These conditions are necessary and sufficient and yield a constructive policy reconstruction.

An independent exact signature evaluator reproduces all 21 earlier tiny-grid optima and every raw-policy multiset tie count. For the canonical \(M=16\) fixture, the single-agent space falls from \(16^{16}\) raw policies to 148,348,284,928 feasible labeled signatures. There are 5,806 target-label orbits for one signature, but independently quotienting each agent is invalid because the objective depends on cross-agent target alignment. Before any joint target quotient, the eight-agent signature-multiset count still has 85 digits.

This establishes a useful structural theorem and rules out the declared naive enumeration plan. It does not certify a private-team upper objective value. Direct clue-following remains the exact lower bound \(325089/390625\), and the pooled planner remains only a numerical benchmark under greater information and assignment authority. The next analytic step is the exact two-searcher hybrid threshold.
