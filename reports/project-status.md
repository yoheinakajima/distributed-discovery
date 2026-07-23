# Project status — Information Sharing Frontier working paper

Date: 2026-07-22 (America/Los_Angeles)

Programs V1 through V4 are complete at their registered bounded scopes.
Program V5's four studies DD-019 through DD-022 are merged and deployed with
claims DD-C-0089 through DD-C-0110 and four immutable primary runs. Issue #153
is closed after the qualified 26-page theorem-family working paper and public
integration merged through PR #155, followed by a presentation-only deployed
mobile-containment correction through PR #156. No study was allocated, no
claim changed, and no research configuration was rerun.

## Inventory

| Measure | Value |
| --- | ---: |
| Studies | 26 |
| Claims | 110 |
| Immutable manifests | 51 |
| Passing immutable runs | 48 |
| Tests | 247 |
| Validated project papers | 7 |
| Paper pages | 115 |
| Public HTML routes | 77 locally generated |
| Public data files | 85 |
| Labs | 18 |
| Checksum-covered downloads | 23 |

## Program V5 continuation milestones

| Milestone | Issue | PR | Merge SHA |
| --- | ---: | ---: | --- |
| Governance and publication architecture | #133 | #134 | `dc32ff17` |
| DD-020 Incremental Sharing | #135 | #136 | `cf7bc67e` |
| Editorial theorem gate and synthesis prospectus | #137 | #138 | `9401fbe7` |
| Public integration and Incremental Sharing Lab | #139 | #140 | `57270680` |
| Final acceptance | #141 | #142 | recorded in GitHub after merge |
| DD-021 General Sharing Frontier | #146 | #147 | `8b444003` |
| Post-DD-021 paper gate | #148 | #149 | recorded by PR #149 |
| DD-022 Coordination-Free Positive Sharing | #150 | #151 | `c8a11bd3` |
| Information Sharing Frontier paper | #153 | #155 | `45bb498f` |
| Deployed mobile-containment correction | #153 | #156 | `fae4a81b` |

## Current acceptance record

- Bootstrap, Ruff, strict MyPy over 159 source files, all 247 tests, the
  110-claim ledger, and all 51 immutable manifests pass.
- Eighteen saved exact-verification records pass; 66 gates across 18 saved
  corruption records are true.
- Twelve JSON schemas validate; the synthetic discovery-event valid fixture is
  accepted and its invalid fixture is rejected.
- Seven project papers rebuild deterministically at 12, 14, 3, 20, 20, 20,
  and 26 pages. The new paper has eight generated figures, eight generated
  tables, exact data, an independent audit, corruption tests, and all-page QA.
- The site builds 77 HTML routes for 26 studies, 85 public data files, 18 Labs,
  and 23 checksum-covered downloads. The live publication and download pass;
  the deployed PDF SHA-256 matches the validation record.
- Browser QA passes substantive point/channel output selection, opposite-sign
  same-accuracy comparison, semantic controls, live status, keyboard focus,
  desktop/mobile containment, internally scrolling tables, and clean logs.
- Paper PR #155 passed branch CI `29964870691` and paper/site build
  `29964870725`, then post-merge CI `29965009706` and Pages `29965009711`.
  Mobile correction PR #156 passed branch CI `29965500859` and paper/site build
  `29965500839`, then post-merge CI `29965642887` and Pages `29965642900`.
- Secret, host-path, license, provenance, Git-cleanliness, and upstream checks
  pass. The upstream clone remains clean at
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`.

No primary run was repeated. Claims, immutable runs, and scientific paper
content are unchanged. No human data exist, and no submission, release, DOI,
settings, or canonical-upstream action occurred.

DD-021's research merge is `8b44400333e156440a22b0d9fe3be37f63d35a08`;
post-merge CI `29951061680` and Pages `29951061715` pass. Its historical paper
hold was satisfied by DD-022. The resulting paper preserves that DD-021's
full-capacity recovery theorem assumes centralized top-`L` authority and that
DD-022's positive comparison is selection-dependent.

## Historical Program V4 milestones

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

## Historical Program V4 acceptance record

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

## Completed Program V5 continuation

DD-019 deployment closeout merged as `5e6c800`; governance/publication PR #134
merged as `dc32ff17`. DD-020's sole primary run is
`20260722T142551Z_DD-020_3854fff6_37c11a850a`; both exact methods and five
corruptions pass. The documentation-only editorial theorem gate and synthesis
prospectus are merged. The exact DD-020 result and output-connected Lab are
deployed through PR #140 as `57270680`; post-merge CI `29933212532` and Pages
`29933212171` pass. Final acceptance is recorded through issue #141 and PR
#142. Settings-only issue #32 remains the sole authority-blocked item.
