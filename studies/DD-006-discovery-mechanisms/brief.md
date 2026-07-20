# DD-006 research brief — Discovery Mechanisms

## Motivating question

Which reporting and reward mechanisms implement informative communication and differentiated search when agents have private signals, choose actions autonomously, and may receive credit based on incomplete outcome observability?

## Minimum viable model

- \(M=3\) locations, \(N=2\) agents, uniform target, independent rational-accuracy signals.
- Each agent reports a signal/message and chooses one location after a public recommendation.
- The mechanism can condition transfers on reports, recommended actions, and one of three observability regimes: target identity, individual success, or sole rescue only.
- Agents maximize expected transfers minus any stated action cost; social value is union discovery.
- Begin with bounded transfers and ex-post budget balance; test dominant-strategy and Bayes–Nash implementation separately.

Hidden actions and unverifiable reports are explicit variants, not silently assumed away.

## Relationship to the canonical benchmark

The canonical equal-split market measures strategic allocation loss with a shared posterior; sole-rescue rewards implement the top portfolio in pure equilibrium under stated assumptions. DD-006 adds private reports and observability constraints, asking whether information elicitation and action differentiation can be implemented jointly.

## Main quantities

- Implementable discovery frontier by observability/incentive regime.
- Incentive gap between planner and best feasible mechanism.
- Budget surplus/deficit, transfer magnitude, and individual rationality slack.
- Worst/best equilibrium discovery and discovery price of anarchy.
- Reporting accuracy, action differentiation, and collusion deviations.

## Adjacent literature

Covering games and valid-utility mechanisms (Vetta 2002; Gairing 2009) anchor action incentives. Team theory and mechanism design with private information anchor reporting constraints. The canonical sole-rescue theorem is a scoped implementation result, not evidence that the same reward elicits private reports.

## Likely methods

Exact Bayesian-game enumeration; linear incentive inequalities; bounded rational transfer-grid search for the first fixture; later linear programming with dual certificates after an ADR; deviation and equilibrium enumeration; impossibility proofs from conflicting constraints.

## Falsifiable questions

1. Does any symmetric, ex-post budget-balanced transfer table fully implement truthful reporting and differentiated first-best action for the minimum model?
2. Which observability loss first makes full implementation impossible?
3. Can sole-rescue credit preserve action differentiation while destroying truth-telling incentives?
4. What discovery is achievable if only outcomes, not chosen actions, are verifiable?

## Dependencies and risks

Depends on DD-001 private-team policies and canonical reward results. Risks include unjustified use of a revelation principle with hidden actions, equilibrium multiplicity, unbounded transfers, confusing pure with mixed implementation, collusion, and designing against a mechanism-specific tie break.

## First executable experiment

Enumerate bounded symmetric rational transfer tables for the \(M=3,N=2\) fixture under each observability regime. Check every reporting/action deviation exactly, record all equilibria, and search for a matching first-best certificate or a complete bounded impossibility result. Estimate the transfer-table count before running.

## Completion criteria

- Message, action, outcome, transfer, and observability spaces are explicit.
- Incentive and budget constraints are machine-checkable.
- Every implementation claim states equilibrium class and tie handling.
- Claimed impossibility has a complete search boundary or analytic proof.
- Private reporting and action differentiation effects are reported separately.
