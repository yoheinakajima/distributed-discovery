# Decentralized Recovery registration local validation

Validation date: `2026-07-22` (America/Los_Angeles)

Issue: `#162`

Branch: `research/decentralized-recovery-registration`

Decision: `stop-classical-overlap`

Evidence class: registration-governance validation; no scientific result

## Result

Local acceptance passes. The gate adds two focused governance tests and
records a classical-overlap stop. It creates no study, claim, immutable run,
research implementation, paper, route, public data file, Lab, or download.
Reliable Discovery is the sole next executable registration direction.

The first `make verify` attempt and a direct Ruff recheck stopped before the
suite at import formatting in the new test. Ruff's mechanical organizer fixed
the block. No research target ran. The complete repeat passed:

- `git diff --check`;
- `make bootstrap` with 11 required files and the valid-claims fixture;
- Ruff formatting and lint;
- strict MyPy over 159 source files;
- all 249 tests, including the two registration decision/schema/corruption
  tests and two focused site relationship tests;
- all 110 claims and all 51 run manifests;
- `make papers`, with seven deterministic PDFs totaling 115 pages; and
- `make site`, with 77 HTML pages and 26 study records.

The paper build temporarily refreshed two Information Sharing Frontier
provenance `source_commit` fields. Both were restored to their accepted values.
The final branch diff contains no path under `claims/`, `results/`, or
`papers/`; all paper PDFs remain byte-identical.

## Frozen invariant comparison

| Object | Post-change value | Result |
| --- | --- | --- |
| Claims-ledger Git blob | `8f262daf3aa43f2505d415988d8eca6f0ecd3a42` | exact |
| Manifest-set SHA-256 | `dc7140a6bd36e931dc96c0e9eacff2fd734d1d0b69aa6848e20603a5ef2e3163` | exact |
| Passing-run-list SHA-256 | `0af5fcc5f049b66a53763a6ccd49107c0ffa27033ac2b947a3f8043b32d18442` | exact |
| `results/verified` Git-tree-list SHA-256 | `50d83d4488a33218f949c520bfa0da9c765ed37677aa3900062b158afac64434` | exact |
| Study-directory-set SHA-256 | `05c09c15029998698127b5ef68fc0e1df86b6951b6e4feb602db60601bee5585` | exact |
| Route-registry SHA-256 | `a551b68b644f2974d9870f954c93ea2990550892088491640f89ef485f1bc080` | exact |
| Download-manifest SHA-256 | `e26726fb092762c5d2e5acc495fce74ae6835fb88ad0bdd7884487487e949584` | exact |

Counts remain 110 claims, 51 manifests, 48 passing runs, 26 studies through
DD-022, 159 Python sources, seven PDFs, 115 paper pages, 77 routes, 85 public
data files, 18 Labs, and 23 checksum-covered downloads. The test count is 249,
up by exactly the two focused governance tests. DD-023 and DD-C-0111 are
absent.

## Paper artifact comparison

| Paper | Pages | SHA-256 | Result |
| --- | ---: | --- | --- |
| Foundations | 12 | `e096183159f8c016f116b1a97fc0721948bbee2aca6dd1ae251d0a2af95a32e4` | exact |
| Three Results | 14 | `40506068a03e6e7ff0dd8c20751b792a9e669e8fd788005dff1c58540131206f` | exact |
| Discovery Institutions | 3 | `9bad1e7aaebd07851613f7f38a5c1a3654ca78363cc95f092f5b97bf0f9cee7b` | exact |
| Common-Source Trap | 20 | `c997bba31c021bd799f2b3a561e8e558a1334f844aa87a448ade10319dac2ad3` | exact |
| Incentive to Ignore | 20 | `ee9e27f741d25a9597994f18caf2bf406098db7aca4d2ed067a7a011f64be250` | exact |
| Threshold Discovery | 20 | `b38bb30f3ce63889526a092d78dd3f202d3beb54178bcdc272aba85c321b1995` | exact |
| Information Sharing Frontier | 26 | `2f8b68d5a690e6369e4c3236313eb93f060bfbe73ec531903c090f6ec6f8b6a1` | exact |

## Safety and provenance

- No tracked diff exists under `claims/`, `results/`, or `papers/`.
- No run directory, study ID, claim ID, SQLite file, human/real dataset,
  private key, token candidate, or public host-specific path was added.
- The repository and pinned-upstream licenses remain present.
- Canonical upstream remains clean and read-only at
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`.
- ActiveGraph remains unchanged.
- All four unrelated untracked duplicate files remain untouched and excluded.

## Remote acceptance

Pending branch CI, paper/site workflow, squash merge, post-merge CI and Pages,
live desktop/390-pixel browser QA, issue closure, and synchronized `main`.
