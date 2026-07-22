# Program V5 continuation final acceptance

Date: 2026-07-22 UTC

Issue #141 and PR #142 own this documentation-only acceptance. The four
required milestones merged and deployed sequentially:

| Milestone | Issue | PR | Merge | Post-merge CI | Pages |
| --- | ---: | ---: | --- | ---: | ---: |
| Governance/publication architecture | #133 | #134 | `dc32ff17` | `29927131835` | `29927132030` |
| DD-020 Incremental Sharing | #135 | #136 | `cf7bc67e` | `29929864642` | `29929864954` |
| Editorial theorem gate and synthesis prospectus | #137 | #138 | `9401fbe7` | `29931375550` | `29931375465` |
| Public integration and Incremental Sharing Lab | #139 | #140 | `57270680` | `29933212532` | `29933212171` |

## Repository and evidence

- `git diff --check`, bootstrap, Ruff, strict MyPy over 142 source files, all
  224 tests, all 96 claim records, and all 49 manifests pass.
- The inventory remains 24 studies and 46 passing immutable runs.
- Seventeen saved exact-verification records have `passed: true`; 58 gates in
  17 saved corruption records are true. A focused verifier/corruption selector
  passes 18 tests.
- Twelve Draft 2020-12 schemas validate. The synthetic discovery-event valid
  fixture is accepted and its invalid fixture is rejected.
- DD-020 run tree `8e736477a933d1ea1bddcf780d4f230f32885f19` is identical to
  the tree at research merge `cf7bc67e`. No registered study target ran during
  public integration or acceptance.
- DD-019 and DD-020 status records are current. No later Program V5 study is
  registered by this closeout.

One non-authoritative focused-test attempt omitted the repository `src` path
and failed collection against a stale non-editable installation. Repeating the
same selector with the Makefile-equivalent `PYTHONPATH="$PWD/src"` passed 18
tests. The authoritative Make gate had already passed all 224 tests.

## Papers, site, and browser

- All six project papers rebuild deterministically at 12, 14, 3, 20, 20, and
  20 pages. Their validation/provenance records pass, all 89 pages retain
  visual-QA records, and no tracked PDF or scientific paper content changed.
- The site builds 72 HTML routes, 71 public data files, 17 Labs, 22
  checksum-registered downloads, and 171 total public files for 24 studies.
- Local and deployed Incremental Sharing QA covers point/channel modes,
  negative and positive increments, the same-accuracy comparison, the terminal
  eight-agent step, seven labeled selectors, polite live output, keyboard
  focus, chart text alternatives, 390×844 containment, internal table
  scrolling, complete no-JavaScript data, and zero warning/error logs.
- All 171 deployed files return HTTP 200. All 22 local and deployed downloads
  match registered byte counts and SHA-256 values.
- Deployed DD-020 point and channel source hashes are respectively
  `742ece76da5d4746772c5b9065e754b5e24012cae8c899f36d54469c6e796a59`
  and `a4f63d52f402ce14f91e469d4b425ce65a92740b31530c7da9384cc726030e3a`,
  exactly matching the immutable run.

## Safety and boundaries

- Secret and host-path scans find zero candidates in tracked public material.
- Project and pinned-upstream MIT licenses pass. The read-only upstream clone
  is clean at `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`.
- Paper provenance, run-manifest checksums, route registry, sitemap, link,
  accessibility, and download provenance checks pass.
- Claims, immutable runs, and paper PDFs are unchanged from the deployed public
  integration baseline.
- No submission, DOI, release, journal contact, human-data, real-data,
  repository-settings, or canonical-upstream action occurred.
- Issue #32 remains the sole authority-blocked settings item. The one
  authorized unauthenticated CLI probe was not repeated.

AGENTS.md, the repository contract, research governance, and publication
architecture remain the normative rules. Current state/roadmap, theorem and
research roadmaps, Program V5, study registry/status, papers index, ExecPlan,
project status, handoff, root/site READMEs, and changelog are reconciled without
duplicating the long-range portfolio.
