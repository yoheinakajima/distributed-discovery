# ADR-0003: Machine-readable claim ledger

**Status:** accepted (DD-000)

## Context
Papers, sites, reports, proofs, code, runs, and sources need one audit trail.
## Decision
Use YAML claims validated by JSON Schema, stable `DD-C-*` IDs, and policy-governed promotion.
## Alternatives considered
Prose-only status, issue tracker, database.
## Consequences
Claims remain reviewable in Git; schema evolution requires compatibility care.
## Reversal conditions
Migrate if scale or relational queries materially exceed file-based tooling, preserving stable IDs and history.
