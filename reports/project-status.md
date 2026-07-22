# Project status — Program V4 final acceptance

Date: 2026-07-22 (America/Los_Angeles)

Programs V1 through V4 are complete at their registered bounded scopes.
Program V5 has not yet been registered; its first milestone is a
documentation-only baseline after this handoff merges.

## Inventory

| Measure | Value |
| --- | ---: |
| Studies | 22 |
| Claims | 88 |
| Immutable manifests | 47 |
| Passing immutable runs | 44 |
| Tests | 212 |
| Validated project papers | 6 |
| Paper pages | 89 |
| Public HTML routes | 68 |
| Public data files | 66 |
| Labs | 16 |
| Checksum-covered downloads | 22 |

## Program V4 milestones

| Milestone | Issue | PR | Merge SHA |
| --- | ---: | ---: | --- |
| Editorial synchronization | #99 | #100 | `eb639f85` |
| DD-016 | #101 | #102 | `571a8ddf` |
| DD-017 | #103 | #104 | `5028802f` |
| Roadmap reconciliation | #108 | #109 | `6cd7190` |
| DD-015 | #110 | #111 | `9f2fc1e` |
| DD-018 | #113 | #114 | `6a533d1` |
| DiscoveryBench v3 | #116 | #117 | `3b4fdbe` |
| Synthetic Experiment v3 | #119 | #120 | `0f7a234` |
| Focused paper | #122 | #123 | `ab9cf448` |
| Output-connected Labs | #124 | #125 | `e12d1d2` |
| Final acceptance | #126 | final handoff PR | recorded in GitHub after merge |

## Acceptance record

- Bootstrap, Ruff formatting/lint, strict MyPy on 134 source files, all 212
  tests, the 88-claim ledger, and all 47 manifests pass.
- Six papers rebuild deterministically at 12, 14, 3, 20, 20, and 20 pages;
  the site builds 68 HTML pages for 22 studies.
- All verification/corruption, benchmark golden-certificate, schema,
  checksum, secret, host-path, license, provenance, and upstream-cleanliness
  audits pass.
- Browser QA passes substantive output selection in all four V4 Labs,
  semantic/accessibility checks, desktop/mobile width containment,
  no-JavaScript tables, and clean logs.
- Every one of 162 deployed public files returns HTTP 200.

No immutable primary run was repeated during the paper, Labs, or final handoff.
No human experiment was conducted. Settings issue #32 remains the only
authority-specific operational blocker and does not block research or Pages.

## CI and Pages

Paper PR #123 passed CI `29900445956` and paper/site build `29900445965`;
post-merge CI `29900587931` and Pages `29900587930` passed. Labs PR #125
passed its branch checks; post-merge CI `29902201507` and Pages `29902201604`
passed. Final handoff PR and post-merge workflow IDs are recorded after merge.

## Next authorized milestone

Merge the documentation-only Program V4 handoff and verify post-merge CI,
Pages, and live status. Then open exactly one Program V5 documentation baseline
issue and branch. Do not create a Program V5 study ID, run, or claim in that
baseline.
