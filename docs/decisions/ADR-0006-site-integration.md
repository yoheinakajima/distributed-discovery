# ADR-0006: Additive static site integration

**Status:** accepted (DD-000)

## Context
The original six-minute experience must remain primary and upstream is read-only.
## Decision
Build a dependency-light private static companion and generate patchable upstream fragments after inspecting the pinned site.
## Alternatives considered
Rewrite the site, adopt a heavy framework, deploy a separate public application.
## Consequences
Local review stays simple; exact visual reuse waits for M1 inspection.
## Reversal conditions
Align with upstream tooling if its pinned architecture makes direct additive patches safer.
