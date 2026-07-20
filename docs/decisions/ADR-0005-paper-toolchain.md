# ADR-0005: Paper toolchain

**Status:** accepted (DD-000)

## Context
Academic notes need equations, citations, generated tables, and reproducible builds.
## Decision
Use LaTeX source with `latexmk` when available, generated assets, and a validation fallback that reports a missing compiler rather than fabricating a PDF.
## Alternatives considered
Markdown/Pandoc, Typst, committed binary-only documents.
## Consequences
Source is conventional; local compilation needs a TeX distribution.
## Reversal conditions
Reconsider if CI and contributors standardize on another auditable toolchain.
