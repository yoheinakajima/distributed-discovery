# Project status — Program V3 final acceptance

Date: 2026-07-21 (America/Los_Angeles)

Program V3's required queue is complete at its registered bounded scope.
DD-015 was optional and was not executed. Programs V1 and V2 remain complete.

## Inventory

| Measure | Value |
| --- | ---: |
| Studies | 19 |
| Claims | 70 |
| Immutable manifests | 40 |
| Passing immutable runs | 37 |
| Tests | 183 |
| Validated project papers | 5 |
| Public HTML routes | 59 |
| Public data files | 59 |
| Labs | 12 |
| Checksum-covered downloads | 19 |

## Program V3 milestones

| Milestone | Issue | PR | Merge SHA |
| --- | ---: | ---: | --- |
| Registration baseline | #79 | #80 | `69ba1c392bb0bda9bc4447c0fac842b8e7308fbf` |
| DD-012 | #81 | #82 | `b14fe47359d8a42123b512445a5493d6cf1f7872` |
| DD-013 | #83 | #84 | `a7b622aabc919238b29d452eb7263a1722cbbfe4` |
| DD-014 | #85 | #87 | `9bc1a61ee688ba9fce3504c646c6fab540358447` |
| Focused paper | #88 | #90 | `8a1255ed5a5b7a5a83bae210951afefcbf48afb1` |
| DiscoveryBench v2 | #91 | #93 | `4637944753d3aaab3f57c10de217a06915482189` |
| Synthetic experiment v2 | #94 | #95 | `da3a0c029d605c710a458975c4746ec0da219ebe` |
| Public integration | #96 | #97 | `982ba32873136abbbc96f382cbcc630226a3972d` |
| Final acceptance | #98 | final handoff PR | recorded in GitHub and the closing response |

All substantive milestone issues through #96 are closed by their merged PRs.
Issue #98 closes with the final handoff. Settings issue #32 remains open because
the authorized credentials are unavailable.

## Exact evidence

DD-012 run `20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b` supports
DD-C-0059–0061. DD-013 run
`20260721T215811Z_DD-013_09c07448_cdac4fb512` supports DD-C-0062–0065.
DD-014 run `20260721T222047Z_DD-014_f5f099a8_ea0276dd16` supports
DD-C-0066–0068. DiscoveryBench v2 run
`20260721T230249Z_DD-010_add85590_56c61a2195` supports DD-C-0069. Synthetic
experiment v2 run `20260721T232119Z_DD-011_121162f8_e454b06d2c` supports
DD-C-0070 as Monte Carlo evidence only.

The required results and boundaries are summarized in `docs/current-state.md`.
No immutable run was duplicated during paper, site, or final integration.

## Paper status

All five project papers rebuilt successfully and all 69 pages were rendered and
inspected. Each PDF matches its validation and visual-QA checksum. The paper
page counts are 12, 14, 3, 20, and 20. The focused Program V3 paper is
`The Incentive to Ignore`, 20 pages, SHA-256
`ee9e27f741d25a9597994f18caf2bf406098db7aca4d2ed067a7a011f64be250`.
The Three Results paper received a provenance-only claim-ledger refresh; its
current 14-page PDF SHA-256 is
`d3346c805483bf923064b7c60633ef6dbed702066ad4da241d884856126cbd6f`.

## Acceptance record

- `make bootstrap` passed 11 required-file checks and the claim fixture.
- formatting, Ruff, mypy, 183 tests, 70-claim validation, and all 40 manifest
  validations passed.
- 62 focused certificate, corruption, benchmark leakage, schema, and
  synthetic-boundary tests passed.
- all five PDFs rebuilt byte-reproducibly; 69 rendered pages passed visual QA.
- all five PDF/visual-QA records and 19 download checksums match; paper
  provenance has zero errors.
- secret scan found zero candidate files; public host-path scan found zero;
  the only tracked path-pattern literals are the scanners and their tests.
- the root and pinned upstream licenses are MIT; all 20 installed dependency
  distributions declare license metadata.
- canonical upstream is pinned at `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`
  and its cache is clean.
- browser QA passed exact filtering, keyboard-visible focus, reduced motion,
  desktop/mobile width containment, heading/table semantics, and clean logs.
- every required Program V3 live route returned HTTP 200 after PR #97.

## CI and Pages

| Milestone | Post-merge CI | Post-merge Pages |
| --- | ---: | ---: |
| Baseline | `29868986810` | `29868986666` |
| DD-012 | `29871172110` | `29871172753` |
| DD-013 | `29872695083` | `29872695035` |
| DD-014 | `29874116580` | `29874116570` |
| Focused paper | `29875245781` | `29875245770` |
| DiscoveryBench v2 | `29876322496` | `29876322578` |
| Synthetic experiment v2 | `29877161751` | `29877161805` |
| Public integration | `29878042468` | `29878042571` |

The final handoff's PR and post-merge workflow IDs are recorded after its merge
in GitHub and in the closing response.

## Remaining questions

DD-015's dynamic stopping/fixed-budget distinction, unrestricted conditional
policy classes, heterogeneous attention costs, reader-identity selection,
mixed equilibria, acquisition-plus-attention-plus-action implementation, robust
benchmark aggregation, and any real-data validation remain open. Each requires
a new bounded registration and, for human or real data, separate ethics,
privacy, identification, retention, and governance review.
