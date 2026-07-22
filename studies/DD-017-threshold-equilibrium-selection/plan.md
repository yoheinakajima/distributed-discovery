# DD-017 execution plan

## Purpose and intended outcome

Characterize the bounded pure-Nash occupancy correspondence and audit whether
equilibria survive pairwise or minimum-team strict-improvement coalitions.

## Current state

DD-016 merged through PR #102 at `571a8ddf360b356b8b947ea740b124cf035563b8`.
Issue #103 and branch `research/dd017-threshold-equilibrium-selection` are
active. The model, bounded registry, implementation, independent labeled
verifier, corruption gates, and tests are being frozen before any primary run.

## Scope and resource estimate

Eight rational posterior fixtures cover M=2,3,4. For every N=2,...,6 and every
tau=1,...,N, the registry contains 160 games and 3,728 occupancy states. The
independent verifier visits 87,216 labeled action profiles, plus exact opponent
profiles for tied-mode payoff checks. Expected runtime is 60 seconds, capped at
300 seconds and 1 GB.

## Milestones

1. Freeze concepts, literature boundary, registry, and resource caps. **Complete.**
2. Implement pure, pairwise, tau-player, welfare, and tied-mode checks. **Complete.**
3. Pass targeted and repository tests; commit the frozen implementation. **Active.**
4. Execute one clean immutable registry run and audit any claims separately.
5. Decide the next bounded extension toward correlated or selection objects.

## Validation strategy

Compare occupancy-level Nash conditions with a labeled action-profile
enumerator. Rebuild coalition blocks from removal/addition occupancies and an
exact payoff-compatible matching, and directly enumerate opponent action
profiles for mixed-action payoffs. Hand-check threshold-two crowding and pair
blocks. Reject a removed equilibrium, altered best discovery, altered pair
stability, and altered tied-mode classification.

## Preserved boundaries

Weak Nash, strict-member pair stability, exact-size-tau strict-member
stability, and one symmetric mixture are separate labels. No full strong
equilibrium, coalition-proof equilibrium, correlated equilibrium, stochastic
selection, human behavior, or universal mechanism is claimed.

## Preliminary non-evidence observation

A dirty-tree preview traversed all 160 games and 3,728 occupancy states; the
independent verifier checked 87,216 labeled profiles. It found 52 games with
zero worst-equilibrium discovery, eight with no pairwise-strict-stable pure
equilibrium, 35 with no exact-size-tau-strict-stable pure equilibrium, and 21
tied-mode symmetric-mixture failures. These counts are regression targets only
until a clean immutable run and separate claim audit pass.

## Recovery

Inspect this plan and Git state. Do not execute a primary configuration before
the implementation is committed and the tree is clean. Preserve any run
directory and never rerun a passing primary configuration for freshness.

## Outcome and retrospective

Pending.
