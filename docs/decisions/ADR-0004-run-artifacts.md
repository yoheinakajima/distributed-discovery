# ADR-0004: Immutable compact run artifacts

**Status:** accepted (DD-000)

## Context
Numerical claims require commands, inputs, environment, outputs, hashes, and validation.
## Decision
Write immutable run directories with UTC/Git/config-derived IDs and commit compact important artifacts.
## Alternatives considered
Ad hoc logs, mutable latest-results folders, external-only tracking.
## Consequences
Runs are auditable and diffable at some storage cost.
## Reversal conditions
Adopt an artifact service only under ADR-0008 while retaining manifests and checksums in Git.
