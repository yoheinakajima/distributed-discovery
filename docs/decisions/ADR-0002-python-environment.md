# ADR-0002: Python dependency and environment management

**Status:** accepted (DD-000)

## Context
Runs need a supported Python, deterministic dependencies, linting, typing, schemas, and tests.
## Decision
Use Python >=3.11, a `src/` layout, `uv.lock`, pytest, Ruff, mypy, PyYAML, and jsonschema.
## Alternatives considered
System Python/pip, Poetry, Conda, or standard library alone.
## Consequences
`uv sync --locked` supplies consistent tooling; the host Python version is irrelevant after bootstrap.
## Reversal conditions
Change if `uv` becomes unavailable or a study requires an incompatible scientific stack, with a migration plan.
