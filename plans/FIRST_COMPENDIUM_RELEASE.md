# First Compendium external release and durable closeout

## Purpose and intended outcome

Publish and verify Distributed Discovery Research Compendium v0.1.0 from the
owner-authorized source revision, then make the external identifiers and
citation convention durable without changing the tagged commit or scientific
evidence.

Normal completion is `release-published-zenodo-verified`: an immutable
annotated tag, a public GitHub Release with five verified assets, a published
Zenodo software record, resolving version and concept DOIs, a merged
documentation-only closeout, passing CI and Pages, live citation links, a
closed release issue, and synchronized `main`.

## Current state

Live as of 2026-07-24 UTC:

- release issue: #185;
- authorized and tagged source:
  `3ca173f4e9e81a6d0e3e56205e428c596edc050e`;
- annotated tag: `dd-compendium-v0.1.0`;
- tag object: `0fa9bd22b9a49a0e028e6fccda60b9bc2dadc7f6`;
- GitHub Release:
  `https://github.com/yoheinakajima/distributed-discovery/releases/tag/dd-compendium-v0.1.0`;
- GitHub publication time: `2026-07-24T13:52:52Z`;
- Zenodo record: `21535005`,
  `https://zenodo.org/records/21535005`;
- version DOI: `10.5281/zenodo.21535005`;
- concept DOI: `10.5281/zenodo.21535004`;
- both DOI URLs resolve with HTTP 200;
- the sole Zenodo source archive is byte-identical to all 2,379 files in the
  authorized Git tree;
- external publication and file verification are complete;
- branch `release/compendium-v0.1.0-closeout` owns only the remaining
  documentation, citation, validation, PR, merge, deployment, and issue
  closeout.

## DISCUSSION AND DECISION DELTA AUDIT

Initial audit was recorded durably in issue #185 before the tag. Reconciliation
after the first stable release trigger:

- PM-0004, Algorithms and computational complexity: the
  `after-first-stable-release` review trigger is now due. It remains routed and
  deferred until a registered computational problem has a fixed input model
  and complexity measure; the release creates no complexity claim.
- PM-0006, Immutable citation freeze rule: implemented and now exercised by
  the version-specific DOI, immutable tag, evidence manifest, and checksums.
- PM-0012, Zenodo and stable release readiness: the activation trigger
  occurred and the record is promoted from prepared infrastructure to verified
  implementation for Compendium v0.1.0.
- PM-0024, Artifact licensing separation: the release-time review trigger
  occurred; the active owner attestation covered the tagged manuscript source,
  PDFs, generated figures, upstream treatment, and exclusions without changing
  any license.
- PM-0026 and PM-0027: TreasureBench naming and the Treasure Hunt companion
  remain implemented.
- PM-0009: Common-Source Trap remains the first internal arXiv freeze
  candidate; this release does not edit or submit it.
- PM-0014 and PM-0015: the benchmark paper and publication recomposition
  remain evidence-dependent because no claim-grade Agents v1 campaign exists.
- The TreasureBench Agents v1 sealed engineering pilot remains the next
  separately authorized gate.
- No owner decision relevant to this release remains only in conversation.

Repeat this audit immediately before closing issue #185. Record any newly due
item in the registry and its canonical destination; do not create scientific
authority here.

## Scope

- preserve and verify the authorized source SHA;
- record the exact annotated tag object and GitHub Release;
- record the five custom assets, sizes, and SHA-256 values;
- record the GitHub-generated source archives;
- record the Zenodo record, actual metadata, file checksum, version DOI, and
  concept DOI;
- update compendium-level CFF metadata and stable citation guidance;
- add a contextual public release/citation surface while preserving five
  primary navigation items;
- update program state, roadmap, handoff, project status, master plan, program
  memory, release registry, reports, and tests;
- validate, open one draft closeout PR, merge after checks, verify Pages and
  live routes, close issue #185, and synchronize `main`.

## Non-goals

- no change to the tagged commit;
- no study, claim, run, theorem, proof promotion, estimate, or benchmark result;
- no paper source, PDF, lifecycle promotion, arXiv, journal, or peer-review
  action;
- no package publication or namespace reservation;
- no provider/model call or private benchmark access;
- no manual or duplicate Zenodo deposit;
- no modification of ActiveGraph, SQLite, canonical upstream, or repository
  settings issue #32.

## Assumptions

- the owner authorization remains the authority for the exact source revision;
- the Zenodo GitHub integration maps the GitHub tag string
  `dd-compendium-v0.1.0` into its `version` field while the semantic compendium
  version remains `0.1.0`;
- Zenodo's single integrated source ZIP is the current official equivalent of
  the tagged source archive and need not mirror all five GitHub custom assets;
- `CITATION.cff` schema 1.2.0 accepts `doi` and `date-released`;
- correction of future scientific or file errors requires a new release
  version rather than moving this tag or replacing verified assets.

## Milestones

1. M0 preflight, authorization, source, issue, and discussion-delta audit.
2. M1 deterministic double build and full pre-tag validation.
3. M2 annotated tag and GitHub Release publication.
4. M3 fresh-download, source-archive, Zenodo-record, file, and DOI verification.
5. M4 tracked release registry, reports, CFF, state, memory, site, and tests.
6. M5 local closeout validation and draft PR.
7. M6 required checks, merge, final CI/Pages/live acceptance, issue closure,
   synchronized `main`, and retrospective.

Execute these milestones sequentially. M0 through M5 are complete. M6 is the
only active milestone.

## Progress checklist

- [x] M0 exact source and authorization preflight passed.
- [x] M0 issue #185 created as the pre-tag operational ledger.
- [x] M1 two release-mode builds are byte-identical and independently verified.
- [x] M1 full pre-tag acceptance passed with 365 tests.
- [x] M2 annotated tag created and pushed exactly once.
- [x] M2 public GitHub Release created with exactly five custom assets.
- [x] M3 public assets downloaded fresh and verified byte-for-byte.
- [x] M3 GitHub source ZIP and TAR.GZ resolve.
- [x] M3 Zenodo record, source archive, version DOI, and concept DOI verified.
- [x] M4 tracked closeout and public citation surface complete.
- [x] M5 local CFF, formatting, typing, 369-test, claim/run, publication,
  release, Agents v1, paper, and site gates pass.
- [x] M5 all local closeout gates pass and draft PR #186 is open.
- [ ] M6 PR checks, merge, post-merge CI/Pages, live routes, issue closure, and
  synchronized-main acceptance pass.

## Discoveries and surprises

- `make papers` refreshes the Information Sharing Frontier provenance
  `source_commit` fields. The pre-tag clean-state check caught the two working
  tree changes. They were restored byte-for-byte to the authorized commit
  before the tag; no pre-tag commit or branch existed.
- Zenodo ingested the GitHub Release within seconds and archived one source ZIP
  rather than the five custom GitHub assets. This matches the allowed current
  integration behavior.
- Zenodo records the exact GitHub tag string as `version`:
  `dd-compendium-v0.1.0`. The tagged CFF and release registry retain semantic
  version `0.1.0`.
- The concept DOI resolves to the latest version record, currently the same
  v0.1.0 page as the version DOI.
- Program-memory recurring release reviews use the existing canonical
  `release-or-venue-freeze` trigger; introducing near-duplicate trigger names
  would have violated the registry schema.

## Decision log

- 2026-07-24 UTC: accept only source SHA
  `3ca173f4e9e81a6d0e3e56205e428c596edc050e`.
- 2026-07-24 UTC: use generated time `2026-07-24T13:47:29Z` for both canonical
  release builds; keep DOI fields null in immutable GitHub assets because
  Zenodo had not yet assigned identifiers.
- 2026-07-24 UTC: preserve the transient paper-provenance refresh as an issue
  ledger note and restore the authorized bytes before tagging.
- 2026-07-24 UTC: accept Zenodo's one-file GitHub integration archive after
  exact comparison with all 2,379 authorized Git files.
- 2026-07-24 UTC: use the version DOI in `CITATION.cff`; keep the concept DOI in
  the release registry and stable citation guidance.
- 2026-07-24 UTC: add release information contextually to the existing Papers
  route and generated JSON; do not create a sixth primary navigation item.

## Validation strategy

Require:

- schema validation for the release registry and closeout report;
- DOI syntax, role, resolution, and exact-record tests;
- CFF 1.2.0 validation with the actual version DOI and release date;
- exact tag object/source SHA and release URL assertions;
- exact five-asset name/size/SHA-256 assertions;
- exact Zenodo record, source-file checksum, and archive-tree assertions;
- program-memory trigger reconciliation;
- site release/citation copy and JSON tests;
- no false paper-status promotion;
- 110 claims, maximum DD-C-0110, 26 studies, maximum DD-022, 51 manifests, 48
  passing, no DD-023, no DD-C-0111;
- seven PDFs, 119 pages, exact hashes, no paper-source diff;
- no local authorization, credential, host path, private material, provider
  call, package, submission, ActiveGraph, SQLite, or upstream mutation;
- full required Make targets, PR checks, post-merge CI/Pages, and live URLs.

## Commands and expected observations

Closeout validation:

```sh
git diff --check
make bootstrap
make audit-program-memory
make audit-publication-infrastructure
make audit-treasurebench-naming
make release-readiness
make compendium-release-readiness VERSION=0.1.0
make audit-agents-v1
make audit-agents-v1-evaluation
make agents-v1-dry-run
make agents-v1-readiness
make verify
make papers
make site
```

Expected: all commands pass; paper-build provenance refreshes, if any, are
restored before commit and recorded honestly; scientific/paper inventories
remain exact.

External checks:

```sh
gh release view dd-compendium-v0.1.0 --repo yoheinakajima/distributed-discovery
curl --fail --location https://doi.org/10.5281/zenodo.21535005
curl --fail --location https://doi.org/10.5281/zenodo.21535004
```

Expected: the release is public with five assets; both DOI requests resolve to
the published v0.1.0 record.

## Artifacts produced

External:

- issue #185;
- annotated tag `dd-compendium-v0.1.0`;
- GitHub Release and five custom assets;
- Zenodo record 21535005 and one source archive;
- version DOI `10.5281/zenodo.21535005`;
- concept DOI `10.5281/zenodo.21535004`.

Tracked closeout:

- this ExecPlan;
- `docs/releases/releases.yml` and schema;
- Markdown/YAML closeout reports;
- updated CFF, citation policy, current-state/roadmap/handoff/status/master-plan
  and program-memory records;
- contextual site release/citation data and tests.

## Blockers

None at M4 start. If local validation fails, preserve the external release,
keep issue #185 open, record `closeout-validation-failed`, and repair only the
documentation branch. Never modify the tag, release assets, or Zenodo deposit.

## Recovery and restart instructions

1. Work only in this repository and branch
   `release/compendium-v0.1.0-closeout`.
2. Read issue #185 and this plan.
3. Confirm the tag object and peeled target.
4. Confirm the GitHub Release and five asset digests.
5. Confirm Zenodo record 21535005 and both DOI redirects.
6. Inspect `git status`; preserve the five named untracked user files.
7. Continue at the first unchecked milestone.
8. Do not rerun immutable scientific configurations or alter the tagged commit.

## Outcome and retrospective

Pending M4 through M6. Finalize only after the closeout PR is merged, required
post-merge workflows and live citation links pass, issue #185 is closed as
completed, `main` is synchronized, and the final discussion/decision delta
audit finds no release-relevant owner decision stranded in conversation.
