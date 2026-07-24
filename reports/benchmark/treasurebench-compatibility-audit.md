# TreasureBench historical compatibility audit

Audit date: 2026-07-23 PDT. Starting main:
`b242e31680237538e26bae543fdac5db459b0857`.

Status: **full local and browser gates pass; CI and live Pages acceptance
pending**.

## Preserved scientific objects

- DD-010 remains the instrument owner and its directory and ID are unchanged.
- The 110 claim records still end at DD-C-0110.
- The 26 study records still end at DD-022.
- All 51 immutable manifests and 48 passing verified runs retain their IDs and
  paths; the starting `results/verified` tree is
  `c8fd20f66797c5014acf658a749e7f15fcaf6750`.
- Claim files, verified results, and paper files have no naming-migration diff.
- Protocol IDs, metric IDs, task IDs, historical result keys, and Agents v1
  protocol identifiers remain unchanged.
- DD-010 changes are restricted to current display prose in `README.md` and
  `public.yml`; the study identity and frozen content remain unchanged.

The frozen task schema SHA-256 values remain:

| Schema | SHA-256 |
| --- | --- |
| `task-v1.schema.json` | `5bfca5952c35823986137f4c13740d9c56d90ef1fdb0d11ac7f9bd2c0fa90d92` |
| `task-v2.schema.json` | `c52bb69bbfa76ffeee316b02aad3d5c0d72ab46643de596cc2025f64344bc6f2` |
| `task-v3.schema.json` | `9da2709a5790afeecd7c8e6dac81c3215cbdb15731f6dd6a77ddda2e6ce7c5d1` |

## Interfaces

The root distribution remains `distributed-discovery`. Existing
`distributed-discovery benchmark ...` and `distributed-discovery agents-v1
...` interfaces remain intact. `distributed-discovery treasurebench ...` and
the delegating `treasurebench ...` console alias expose the formal suite
without a standalone package or new implementation.

Seven canonical TreasureBench pages and seven historical `benchmark...` HTTP
200 pages build together. Historical pages carry a visible compatibility note
and canonical link. Existing `data/benchmark/` JSON remains available; current
display copies live under `data/treasurebench/`; no immutable result file was
renamed. `data/route-aliases.json` records the mapping.

The local site builds 89 HTML pages, 110 public JSON files, and 221
total files. It retains 18 registered Labs, 23 checksum-covered downloads, and
five primary-navigation items. Treasure Hunt is a guide, not a Lab.

All 355 tests, strict typing over 181 source files, claim/run/editorial audits,
the naming audit, and release-readiness pass. Browser checks pass at 1280 and
390 × 844 with one H1 per checked page, clean consoles, visible keyboard focus,
no document overflow, local scripts only, five working modules, and complete
no-JavaScript tables. The seven primary PDFs retain their accepted hashes and
119-page total, and paper source has no migration diff.

## External-action boundary

No provider call, private material, package publication, namespace reservation,
tag, release, Zenodo activation, DOI, arXiv submission, or paper edit is part
of this migration. CI and Pages are recorded only after those gates actually
pass.
