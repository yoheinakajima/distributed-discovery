# Documentation-only validation

## Scope

The final documentation branch is rebased on `main` `5028802f932474dfa8a0312649235bca8f0b0661`. Its merge-base is that same SHA. Relative to main, it changes exactly:

- `docs/research-roadmap.md`
- `docs/theorem-roadmap.md`
- `reports/roadmap-consolidation/backlog-audit.md`
- `reports/roadmap-consolidation/decision-log.md`
- `reports/roadmap-consolidation/parallel-safety.md`
- this validation record

The changed-scientific-file count and changed-site/route count are both zero.

## Scientific invariants at the rebased base

| Invariant | Value |
| --- | --- |
| Claim ledger SHA-256 | `28db2396941cd52dacd8b0d7f7da89a3757e69d91d48f9f90784fde502164239` |
| Manifest inventory | 42 paths; SHA-256 `49e2557e20c031f4095cb9142fb859c1b90b651f8569534d66bff4a700b00e8f` |
| Study inventory | 21 directories; SHA-256 `7c7f02091ca776ba92d64ae7ebbc7da039102d9d477b826a35517115d3ee5ad5` |
| Paper-source content SHA-256 | `a723dcc500a234c1f15b8d9fa6c0a596d46a0884c1e4c40d9c6c7b3a20a1775c` |
| Site builder SHA-256 | `dd3b5b7eef9f3de30bcedb67faacb1fb8a270ad71413179d4f05b2509726aa95` |
| Tracked scientific-path inventory SHA-256 | `9f36ee589c3d49687d8a187163c2cba4af0bec6d75a2ade7f0df9a04fe9c780a` |

These values are inherited from the rebased main; this branch changes none of
the underlying claim, manifest, study, paper, site, source, test, result, or
route files.

## Checks

- `git diff --check main...HEAD` passes after the final documentation edit.
- Link/path checks for all five local Markdown links introduced by the two
  roadmap documents pass.
- `make bootstrap` passes its 11 required-file checks.
- `make verify` passes: Ruff format/check, MyPy on 121 source files, and all
  194 tests.
- No research target, immutable-run target, paper build, or site build was run.
