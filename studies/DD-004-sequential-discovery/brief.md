# DD-004 research brief — Sequential Distributed Discovery

## Motivating question

How does outcome feedback change the value of diversity, the allocation of parallel versus sequential capacity, and the action budget required to reach a discovery benchmark?

## Minimum viable model

- One target on \(M\le8\) atomic locations with a known posterior.
- At most \(B\le4\) searches, allocated in batches according to a declared batch-size vector.
- Searching a location reveals perfectly whether the target is there; a success stops the process.
- A planner selects later actions after observed failures. Actions are costless except for count in the first model.
- Compare a fully parallel top-\(B\) portfolio, one-at-a-time adaptation, and intermediate batches.

No private information or strategic rewards enter the first model. Noisy tests, replenishing candidates, and information spillovers are later extensions.

## Relationship to the canonical benchmark

The canonical benchmark is simultaneous and values discovery by a fixed terminal budget. DD-004 activates the feedback arrow from discovery to information while holding atomic coverage fixed. Under perfect elimination and a fixed maximum budget, sequential adaptation may reproduce a preordered top-\(B\) list; its value may instead appear in expected cost or time. Establishing that boundary is the first task.

## Main quantities

- Adaptive frontier \(V_B^{\mathrm{seq}}(I)\) and parallel frontier \(V_B^{\mathrm{par}}(I)\).
- Adaptivity gap and batching gap.
- Discovery by a deadline and expected actions to success/stopping.
- Sequential recovery budget relative to a parallel/private benchmark.
- Redundant or dominated re-search under noisy execution.
- Value of failure feedback and marginal value of one additional round.

## Adjacent literature

Optimal search is the operational parent; Golovin and Krause (2011) provide adaptive-submodularity language and guarantees under specific assumptions. The canonical recovery budget supplies a static comparison. Results must not borrow adaptive-greedy guarantees unless their hypotheses are proved.

## Likely methods

Finite-horizon dynamic programming; exact posterior updates; policy-tree enumeration for tiny fixtures; coupling arguments for perfect elimination; adaptive-submodularity checks; later approximation algorithms with explicit certificates.

## Falsifiable questions

1. Under perfect atomic elimination and a fixed maximum action count, does sequential feedback leave terminal discovery unchanged while reducing expected actions?
2. Which smallest noisy or state-coupled fixture gives a strict terminal adaptivity gain?
3. Can intermediate batches capture most expected-cost benefit with fewer rounds?
4. Does a static recovery budget overstate or understate sequential capacity needs under a deadline?

## Dependencies and risks

Depends on DD-000 budget/frontier definitions and DD-005 if coverage overlaps. Risks are comparing policies under different stopping costs, treating a policy tree as a fixed portfolio, state explosion, hidden information acquisition by an action, and assuming adaptive submodularity.

## First executable experiment

Implement exact dynamic programming for \(M\le8,B\le4\) with rational posteriors and perfect elimination. Verify against exhaustive policy trees for \(M\le4\). Compare terminal discovery, expected actions, and deadline success across every integer batch partition of \(B\).

## Completion criteria

- Timing, feedback, stopping, and cost objectives are separate primitives.
- The perfect-elimination baseline is solved exactly or bounded with a certificate.
- Any strict adaptivity example identifies the assumption causing it.
- Dynamic programming matches an independent tiny policy-tree evaluator.
- Sequential and parallel budgets are compared on identical objectives.
