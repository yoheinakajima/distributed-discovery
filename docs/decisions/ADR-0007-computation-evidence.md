# ADR-0007: Exact versus heuristic computation

**Status:** accepted (DD-000)

## Context
DD-001 may exceed exhaustive search at canonical scale.
## Decision
Estimate complexity before runs; prefer exact rational evaluation; label heuristics as lower bounds; require completeness proof, certificate, or matching bounds for optimality.
## Alternatives considered
Unbounded brute force; heuristic values labeled optima; solver-only opaque output.
## Consequences
Claims may remain intervals or conjectures, preserving integrity and partial progress.
## Reversal conditions
Only stronger validation methods may relax an implementation choice, never the evidence standard.
