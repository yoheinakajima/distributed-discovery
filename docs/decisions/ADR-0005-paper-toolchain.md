# ADR-0005: Paper toolchain

**Status:** accepted (DD-000)

## Context
Academic notes need equations, citations, generated tables, and reproducible builds.
## Decision
Use LaTeX source with Tectonic 0.16.9 as the pinned self-contained compiler, generated assets, and captured build logs. `latexmk` remains acceptable for upstream compatibility when available.
## Alternatives considered
Markdown/Pandoc, Typst, committed binary-only documents.
## Consequences
Source is conventional; Tectonic downloads its versioned TeX bundle on first use and then supports local builds. Homebrew supplied the 0.16.9 executable in the bootstrap environment.
## Reversal conditions
Reconsider if CI and contributors standardize on another auditable toolchain.
