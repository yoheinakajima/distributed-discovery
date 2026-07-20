---
name: update-upstream-patch
description: Regenerate additive Shared Discovery Paradox paper or site patches against the pinned read-only upstream commit. Use when preparing, refreshing, applying, or validating local upstream-extension patches without modifying or pushing upstream.
---

# Update an upstream patch

1. Read `integrations/shared-discovery-paradox/upstream.lock`, ADR-0001, and the extension change memo.
2. Require a clean pinned upstream cache; fetch via the repository script if absent. Never commit in, push, or alter upstream history.
3. Apply existing patches to a disposable worktree or copy, update additive fragments, and generate minimal reviewable diffs.
4. Preserve the original title, narrative, interactive sequence, theorem numbering, and references where practical.
5. Validate claim-ID metadata, generated numerical sources, paper/site build, tests, and patch applicability.
6. Store fragments/patches and a validation record in this repository; update the integration README and ExecPlan.

Stop and document conflicts when resolution would materially rewrite the canonical presentation.
