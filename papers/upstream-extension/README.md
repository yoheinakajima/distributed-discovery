# Additive upstream extension — DD-000

This directory proposes approximately two pages of additive Distributed Discovery context without changing the canonical title, abstract, motivating paradox, results, theorem numbering, or concise narrative.

- `fragments/`: auditable source insertions and replacements.
- `change-memo.md`: exact placement, rationale, non-goals, and reviewer risks.
- `preview/`: compiled patched PDF, sanitized build log, validation metadata, and visual-QA note.
- `integrations/shared-discovery-paradox/patches/0001-distributed-discovery-additions.patch`: reviewable patch against pinned commit `5025cc8e`.

Regenerate and validate with:

```sh
make upstream-patch
```

The script requires a clean pinned upstream cache, uses a disposable detached worktree, applies the patch, compiles with Tectonic 0.16.9, and confirms upstream remains unchanged.
