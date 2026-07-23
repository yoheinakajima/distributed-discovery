# Post-V5 consolidation local validation

Validation date: `2026-07-22` (America/Los_Angeles)

Issue: `#158`

Branch: `docs/post-v5-theorem-spine-gate`

Evidence class: documentation, synthesis, site, and invariant validation; no
scientific result

## Result

Local acceptance passes. The consolidation changes current-facing editorial
records, the living synthesis, relationship metadata, the existing Program
page, and scoped integration assertions. It adds no study, claim, immutable
run, paper, route, or download and does not change a validated PDF.

`make bootstrap` passed after repairing a stale cached editable-package wheel
with `uv sync --locked --no-editable --reinstall-package
distributed-discovery`; the lockfile and dependency declarations did not
change. Focused YAML and JSON parsing passed, and the focused site relationship
test reported `2 passed`.

`make verify` passed:

- Ruff check and formatting passed.
- mypy passed for 159 source files.
- pytest passed all 247 tests.
- all 110 claim records validate.
- all 51 manifests validate; 48 have `validation_status: passed`.

`make site` passed after the final builder formatting. The generated surface
contains 77 HTML pages, 85 public data files, 18 registered Labs (plus the Labs
index route), 23 checksum-covered downloads, 26 study records, 110 claims, 48
passing runs, and seven publications. Internal links and fragments, public
safety, download checksums, local assets, no-JavaScript fallbacks, no tracking,
accessibility, and semantic structure pass. The scoped generated-marker audit
passes all ten repaired Program/study/Finding/Lab/paper routes.

`make papers` passed all seven project-paper builds. The build temporarily
refreshed two Information Sharing Frontier provenance `source_commit` fields;
both were restored to the frozen accepted value, and a subsequent diff proves
those paper records unchanged.

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

The branch diff contains no path under `claims/` or `results/`. Its only
`papers/` change is the current-facing `papers/README.md`; its only `src/`
change is the presentation-only site builder.

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

Total: 115 pages.

## Safety and provenance

- `git diff --check` passes.
- The private-key/token scan has no candidate.
- The generated site and branch content have no leaked absolute host path.
  Existing tracked `/Users/` strings are a dated historical worktree record or
  defensive test/scan patterns, not public output.
- Repository and pinned-upstream licenses are present.
- Canonical upstream remains clean and read-only at
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`.
- The two unrelated untracked duplicate paper-audit files remain untouched and
  excluded.

## Remote and deployed validation

- Branch CI `29969577304` and paper/site build `29969577290` passed.
- PR #159 squash-merged as
  `8ea3495ccfeacb2c0b4d408d70df1f39718c1a02`.
- Post-merge CI `29969705255` and Pages `29969705284` passed.
- All required live routes and `data/relations.json` returned HTTP 200.
- Desktop and 390-pixel browser QA passed all 16 required routes: one H1,
  valid heading progression, no page-width overflow, required relationship and
  status markers/destinations, visible keyboard focus, and no console
  warnings or errors.
- The deployed Information Sharing Frontier PDF retained SHA-256
  `2f8b68d5a690e6369e4c3236313eb93f060bfbe73ec531903c090f6ec6f8b6a1`.
- Issue #158 closed and local `main` synchronized to the merge; the two
  unrelated untracked duplicate paper-audit files remained untouched.
