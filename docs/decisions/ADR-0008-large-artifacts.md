# ADR-0008: Large artifact policy

**Status:** accepted (DD-000)

## Context
Research runs may create artifacts unsuitable for ordinary Git.
## Decision
Do not commit a single artifact over 10 MB without a new ADR selecting Git LFS, a private release, or an external artifact store. Always commit provenance and checksums.
## Alternatives considered
Commit binaries directly; silently omit them; use an external store by default.
## Consequences
The repository remains manageable and large-result recovery is explicit.
## Reversal conditions
Project hosting/storage constraints or artifact volume justify a documented migration.
