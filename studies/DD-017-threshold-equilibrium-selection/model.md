# Frozen start-gate model

There are M candidates, N agents, threshold tau, and a strictly positive
posterior pi. An action profile induces occupancy n. Candidate j opens iff
`n_j >= tau`, group discovery is

`G(n)=sum_j pi_j 1{n_j>=tau}`,

and every agent at the true opened target splits a unit prize equally. Thus an
agent choosing j receives ex-ante payoff `pi_j/n_j` when `n_j>=tau`, and zero
otherwise.

A weak pure Nash occupancy has no strictly profitable one-agent action change.
A size-c strict coalition block is a joint action change by c named agents that
makes every coalition member strictly better, holding outsiders fixed. The
registered pairwise and tau-player stability labels mean absence of a block of
exactly size two and exactly size tau respectively. They are not strong,
coalition-proof, core, or transfer-enabled equilibrium claims.

Best and worst equilibrium discovery range over pure Nash occupancies only.
For maximization, price of stability is planner value divided by best pure-Nash
discovery and price of anarchy is planner value divided by worst pure-Nash
discovery. A positive planner value divided by zero is recorded as `infinity`;
zero divided by zero would be recorded as one, although all registered
posteriors are positive.

The tied-mode symmetric mixture assigns equal independent probability to every
highest-posterior candidate and zero elsewhere. It is verified by exact action
payoffs against every pure deviation. This verifies one symmetric mixed profile;
it does not characterize all mixed equilibria, correlated recommendations, or
an equilibrium-selection process.

The start-gate registry freezes eight positive rational posterior fixtures,
N=2 through 6, every tau=1 through N, and M=2 through 4. No human behavior,
stochastic selection, arbitrary coalition size, transfers, repeated play,
execution error, or novelty claim is included.

