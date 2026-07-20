---
name: build-paper
description: Build and audit a Distributed Discovery paper from source. Use when compiling foundations, upstream-extension, or study papers and validating generated tables, figures, citations, cross-references, and claim IDs.
---

# Build and validate a paper

1. Read the paper README/build instructions, active ExecPlan, and affected claim records.
2. Regenerate every numeric table and figure from source-of-truth data; verify run IDs and checksums.
3. Check substantive statements have nearby claim-ID comments/metadata and terminology matches status.
4. Validate bibliography metadata, citation resolution, figure/table inputs, labels, references, and links.
5. Build with the pinned/documented toolchain, capture the build log, and fail on unresolved references or citations.
6. Inspect the rendered artifact for layout and confirm limitations and upstream-result attribution.
7. Record commands/artifacts in the ExecPlan. Do not commit an unexplained PDF or a paper that conceals build failures.
