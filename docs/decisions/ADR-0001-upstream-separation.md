# ADR-0001: Separate canonical upstream

**Status:** accepted (DD-000)

## Context
The public paper/site are canonical and read-only; this workspace needs reproducible access without confusing ownership or history.
## Decision
Clone the pinned upstream into ignored `.cache/upstream/`; commit only the lock, provenance, fragments, and reviewable patches.
## Alternatives considered
Git submodule; full vendoring; developing in upstream.
## Consequences
Reproduction requires a fetch step, while repository histories and publication authority remain separate.
## Reversal conditions
Reconsider only if an explicit upstream integration workflow and licensing decision require another mechanism.
