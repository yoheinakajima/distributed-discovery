# Proof record

## Deterministic planner theorem

Let L=floor(N/tau) and write posterior masses in weakly decreasing order.
Any allocation can open at most L candidates: if q candidates open, each has
occupancy at least tau, hence q tau <= N and q <= L. Its discovery value is
the posterior mass of its opened set, so it is no larger than the sum of the
largest min(L,M) posterior masses.

Conversely, assign exactly tau agents to each of the min(L,M)
highest-posterior candidates. If L>M, all candidates are already open;
otherwise this uses L tau <= N agents. Allocate any leftover agents
arbitrarily. Leftovers cannot reduce an already open candidate and, when
L<M, are fewer than tau, so they cannot form another viable team.
The construction attains the bound. Thus the deterministic optimum is the
sum of the top min(floor(N/tau),M) posterior masses.

This proves existence of an optimal minimum-team allocation, not uniqueness:
posterior ties and leftover placement create additional optima.

## Strategic candidate payoff

Suppose every other agent independently chooses candidate j with probability
x_j. Then the number K_j of other agents at j is Binomial(N-1,x_j). An agent
choosing j receives a share of the prize only when K_j >= tau-1; conditional
on that event its share is 1/(K_j+1). Therefore its expected payoff is

V pi_j sum from k=tau-1 to N-1 of
binom(N-1,k) x_j^k (1-x_j)^(N-1-k)/(k+1).

For tau=1, binom(N-1,k)/(k+1)=binom(N,k+1)/N gives
V pi_j [1-(1-x_j)^N]/(N x_j), with continuous limit V pi_j at zero.
For tau=2, subtracting the k=0 term gives

V pi_j ([1-(1-x_j)^N]/(N x_j) - (1-x_j)^(N-1)).

Its limit at zero is zero: the first term and the subtracted term both tend to
one. The implementation also evaluates the original finite binomial sum with
exact rational arithmetic.
