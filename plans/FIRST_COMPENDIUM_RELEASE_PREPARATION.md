# First Compendium v0.1.0 offline release-candidate preparation

## Purpose and intended outcome

Prepare, validate, merge, and deploy every safe repository-local prerequisite
for a future **Distributed Discovery Research Compendium v0.1.0** release
without creating any external release state. The candidate version is `0.1.0`,
the candidate annotated tag is `dd-compendium-v0.1.0`, and the expected future
release title is `Distributed Discovery Research Compendium v0.1.0`.

The normal outcome is
`offline-release-candidate-toolchain-ready`: a deterministic five-asset
builder, a separate verifier, a normalized seven-paper bundle, exact checksum
generation, release evidence and citation metadata, synthetic authorization
validation, a nonexecuting publication plan, validation-only CI, and truthful
release-readiness documentation. A precise permitted stop is successful when
one of the declared boundaries cannot be satisfied.

## Live state

Audit timestamp: `2026-07-24T05:36:08Z`. The primary worktree is the canonical
repository working tree; the similarly named ActiveGraph directory is out of
scope and has not been accessed.

- Starting and synchronized `main`:
  `ec29be1bd632e11dedf02ea18ab14b817fcc8074`.
- `origin/main` matches local `main`; no intervening commit exists.
- PR #181 merged TreasureBench/Treasure Hunt naming as
  `5c407a86019414f90ec46be748ecb515a5a16a6f`.
- PR #182 merged the closeout as
  `ec29be1bd632e11dedf02ea18ab14b817fcc8074`.
- Issue #180 is closed. The only open issue is settings-only #32.
- Release preparation is tracked by issue #183 on branch
  `release/compendium-v0.1.0-preparation`.
- No open pull request exists, so there is no competing substantive canonical
  lane or changed-file overlap.
- `git tag --list` is empty. The public GitHub Releases endpoint returned an
  empty list, and the exact candidate-tag ref query returned an empty list.
- GitHub CLI authentication was probed once and is absent. Public API reads,
  the connected GitHub application, and SSH transport remain sufficient.
- No `.zenodo.json` exists. No repository evidence establishes a Zenodo
  connection, deposit, version DOI, concept DOI, or arXiv identifier.
- Scientific inventory: 110 claims through DD-C-0110; 26 registered studies
  through DD-022; 51 immutable manifests, 48 passing; no DD-023 or DD-C-0111.
- Claim status counts: 47 verified, 49 independently reproduced, seven
  derived, three checked, three sourced, and one proposed.
- Immutable trees at the starting commit:
  `claims/claims.yml` blob `8f262daf3aa43f2505d415988d8eca6f0ecd3a42`;
  `results/verified` tree `c8fd20f66797c5014acf658a749e7f15fcaf6750`;
  `papers` tree `b2915d025257db02d15a7a620c3fc66b978ffd1a`;
  upstream lock blob `af6774acf92f1833a1cca72cf169c268e9a01596`.
- Seven project PDFs contain 119 pages with page counts
  `12, 14, 4, 21, 21, 21, 26`. Their accepted SHA-256 values are:
  `8875926a52f0b8e722f7ce827c456c4b694f9e981c21c4b15bf2b3c60b83e76b`,
  `9eb896353b1210706d6108685dde963e02d6a5ebc64af9f9f69c08c01f5ebc96`,
  `78606f732f105d79395409dcb9d7224d72aa1e44312ca30ff5719d049afd98a8`,
  `afa9384eca60cf2a0291c2c42012f15ca59bf3d29b7c939b1882a0237ea58ff7`,
  `651c91fb68df6b2f1397ca86f3842b7c2fa9c067601957c32401a7f5e95cd24b`,
  `634e96662989a3fd6efb5fc3e6919883897e60511826e25c6d0176bac4af9249`,
  and
  `a317e8851a84b494d8ef30eccc1e31dd4448dc1bbcd3fb2de0fc2849bd581a13`.
- The canonical upstream remains read-only at
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`; its PDF SHA-256 is
  `cb4816cb3a9cdd8db0210ab8981e3729028eb02ba174f2a7300b617807cc1e04`.
- Current local source/test inventory: 181 typed Python files and 355
  collected tests.
- Current local site: 89 HTML pages, 110 JSON files, 221 generated files, 26
  studies, 18 registered Labs, 23 checksum-covered downloads, and five
  primary-navigation items.
- Existing baseline audits pass:
  `make release-readiness`, `make audit-program-memory`,
  `make audit-publication-infrastructure`,
  `make audit-treasurebench-naming`, and `make site`.
- The existing release audit is intentionally weaker than this plan: it
  validates a seven-PDF dry-run record but does not build the future five
  release assets or a normalized source bundle.
- `CITATION.cff` is compendium-level and DOI-free, but
  `date-released: 2026-07-20` incorrectly implies that candidate version 0.1.0
  has already been released. CFF 1.2.0 makes `date-released` optional, so the
  prerelease correction is to remove it while keeping version `0.1.0`.
- `results/index.md` still states 49 manifests / 46 passing and is stale
  relative to the audited 51 / 48 inventory; release-readiness reconciliation
  must correct it.

### Preserved untracked files

The complete starting preservation set is:

- `papers/information-sharing-frontier/paper-audit 2.json`
- `papers/information-sharing-frontier/visual-qa 2.md`
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`

These unrelated duplicate files must not be read, edited, staged, moved,
deleted, normalized, or cleaned. No broad staging command is allowed. A
possible `.env.txt` and any local first-release authorization are explicitly
excluded and must not be read or staged.

## DISCUSSION AND DECISION DELTA AUDIT

The 29-record registry and its supersession map were read before issue or
branch creation. `make audit-program-memory` reports zero owner-adopted unrouted
items, zero duplicate canonical records, and zero raw transcripts.

- PM-0026 and PM-0027 are implemented: TreasureBench is the formal suite and
  Treasure Hunt is its companion. PM-0013 and the old ranked shortlist remain
  superseded as active naming input; DiscoveryBench remains only the frozen
  compatibility alias.
- PM-0012 is the due release-infrastructure record. This task routes the new
  offline preparation authority to this ExecPlan, the release decision, the
  content registry, and the later readiness reports. Its external trigger is
  not satisfied: no tagged release or owner-side Zenodo activation occurs.
- PM-0006's `first-release-freeze` review trigger is not satisfied by an
  offline candidate build. It remains implemented policy and no immutable
  external citation is claimed.
- PM-0024 remains routed. Repository MIT coverage is recorded, while owner
  attestations for paper/PDF release terms, generated figures, third-party
  assets, and upstream treatment remain pending and explicit.
- PM-0009 remains routed: Common-Source Trap is still the first internal arXiv
  freeze candidate. This task does not edit or freeze it.
- PM-0014 and PM-0015 remain evidence-dependent. Claim-grade Agents v1 has not
  run, so the benchmark-paper and publication-recomposition triggers have not
  occurred.
- The sealed TreasureBench Agents v1 engineering pilot remains queued behind
  a separate owner authorization. The public provider-preflight completion
  does not authorize private material or a campaign.
- PM-0028 remains evidence-dependent because no owner-supplied sustained
  third-party-usage evidence was provided.
- Journal-first, omnibus, monolithic benchmark/theory, web-only publication,
  and Foundations-as-vocabulary-preprint options retain their existing
  deferred or rejected dispositions.
- No external action is authorized. No owner decision needed for this offline
  preparation remains only in conversation; the fixed decisions below are
  routed here and will be committed with their canonical release records.

Repeat this audit at issue closeout. If the offline tooling passes, update
PM-0012's durable destinations and review date without claiming that its
external activation trigger occurred.

## Source-of-truth boundary

Git is authoritative for source, scientific evidence, release policy, the
release builder and schemas, citation metadata, and release readiness. A
future annotated tag will identify the immutable source revision only after a
separate owner-authorized task. GitHub Release and Zenodo are external states
and remain unclaimed. No ActiveGraph, SQLite, credential, or private benchmark
system participates.

## Fixed owner decisions

- Candidate version: `0.1.0`.
- Candidate tag: `dd-compendium-v0.1.0`.
- Future title: `Distributed Discovery Research Compendium v0.1.0`.
- The object is a compendium/software archive, not a paper publication.
- Include repository source, seven exact local PDFs, declared paper source
  bundles, paper citation metadata, claims, studies, immutable run records,
  schemas, methods, TreasureBench/Treasure Hunt public infrastructure, release
  evidence, checksums, `CITATION.cff`, `LICENSE`, `CHANGELOG.md`, and
  reproducibility instructions.
- The Shared Discovery Paradox remains separate and read-only. Include its
  lock, attribution, and integration metadata but no duplicate paper bundle.
- External identifier fields remain null in offline artifacts.
- `CITATION.cff` remains compendium-level. It may retain candidate version
  `0.1.0`, must omit a false release date and DOI, and must not add a future
  date.
- Do not add `.zenodo.json`.
- Current repository MIT evidence is preserved; no license changes or legal
  clearance claims are authorized.
- Generated candidate assets live only below ignored
  `build/compendium-release/0.1.0/`.
- A final release manifest receives its source SHA as an explicit argument;
  no committed artifact may self-claim the commit containing itself.

## Scope

1. Freeze a canonical release-content decision and machine-readable registry.
2. Implement deterministic five-asset generation and independent verification.
3. Normalize exactly seven declared paper bundles with sorted paths,
   normalized timestamps and permissions, stable UTF-8 serialization, and
   deterministic compression.
4. Enforce tracked-only content, declared inclusion, and rejection of secrets,
   host paths, local authorization, `.env.txt`, private benchmark material,
   `site/dist`, caches, Git metadata, unlicensed assets, and upstream
   duplication.
5. Add a synthetic-only release-authorization schema and fixtures.
6. Correct and audit the compendium CFF prerelease state.
7. Add release notes, citation metadata generation, a nonexecuting GitHub
   Release/Zenodo plan, Make targets, tests, and validation-only CI.
8. Build twice with the same source revision and timestamp, compare every
   byte, and record sizes, hashes, runtime, and memory.
9. Reconcile release readiness and public-safe status, then validate, merge,
   deploy authorized Pages text if changed, close the issue, and synchronize
   `main`.

## Non-goals

No Git tag, tag push, GitHub Release, asset upload, Zenodo connection/query,
Zenodo deposit, DOI mint/reservation/inference, arXiv or journal action,
package publication, namespace reservation, contact or naming of another
person, provider/model call, private benchmark material, sealed pilot, base
campaign, study, claim, run, theorem, proof promotion, paper-source/PDF edit,
ActiveGraph change, upstream change, credential read, `.env.txt` read, or real
owner-authorization read.

## Release-content decision

Status: M1 decision frozen as `offline-release-candidate-toolchain-ready`.
That outcome remains provisional until all M0-M14 acceptance gates pass.
Permitted stops are:

- `stop-release-content-boundary`
- `stop-paper-bundle-boundary`
- `stop-license-provenance-boundary`
- `stop-citation-metadata-boundary`
- `stop-determinism-boundary`
- `stop-secret-exclusion-boundary`
- `stop-release-schema-boundary`
- `stop-external-service-contract-boundary`

## Asset architecture

Future/dry-run asset names:

1. `distributed-discovery-compendium-v0.1.0-release-evidence-manifest.json`
2. `distributed-discovery-compendium-v0.1.0-SHA256SUMS.txt`
3. `distributed-discovery-compendium-v0.1.0-paper-citation-metadata.yml`
4. `distributed-discovery-compendium-v0.1.0-papers.zip`
5. `distributed-discovery-compendium-v0.1.0-release-notes.md`

The release manifest records hashes for the four peer assets plus the complete
paper-bundle inventory. `SHA256SUMS.txt` covers every asset except itself.
The verifier derives and checks the same rule. No external-identifiers asset is
created offline.

## Determinism

- Sort paths lexicographically by UTF-8 repository-relative archive path.
- Use explicit fixed `generated_utc` and derive a ZIP-compatible normalized
  timestamp from it.
- Normalize archive files to mode `0644`, directories to `0755`, and reject
  symlinks.
- Use `ZIP_DEFLATED` with a fixed compression level and stable member order.
- Serialize JSON with sorted keys, UTF-8, LF, and a trailing newline.
- Emit YAML from normalized ordered data with stable formatting and no aliases.
- Exclude host metadata, absolute paths, Git state beyond the explicit source
  SHA, and all untracked files.
- Build twice in distinct output directories and compare filenames, bytes, and
  hashes.

## Tracked-file boundary and exclusion policy

The content registry is the only authority for archive membership. Candidate
members must resolve to tracked regular files and remain inside the repository.
Reject untracked files, unresolved globs, collisions, symlinks, path traversal,
absolute paths, `.git`, `.env*`, authorization-like local records,
`site/dist`, `build`, `dist`, caches, virtual environments, private/sealed
material, provider credentials/traces, duplicate collision-copy filenames,
and undeclared third-party assets. The verifier repeats the checks from built
bytes rather than trusting the builder.

## CFF policy

Retain CFF 1.2.0, type `software`, candidate version `0.1.0`, the repository,
site, MIT license, author, accurate title/message/abstract, and no DOI. Remove
`date-released` until an actual release exists because the field is optional
and semantically means the software or dataset has been released.

## Licensing boundary

The content registry records the existing MIT evidence per artifact group and
flags all owner attestations still required. Dry-run generation may include the
declared seven local paper bundles for byte-level preparation while the
manifest and readiness decision state that external publication remains
blocked on owner attestations. Unlicensed third-party assets are rejected. This
is an audit, not legal advice or a license change.

## Authorization schema and external-action guard

The tracked template is inactive:
`authorization_status: pending-owner-decision`, `release_allowed: false`,
tag/GitHub/Zenodo permissions false, and package/arXiv/journal/provider/private
permissions false. Tests use only synthetic valid and invalid fixtures.

Normal builder/verifier commands are local and nonmutating. Release mode builds
files only and validates explicitly supplied final coordinates; it does not
tag, push, create a release, upload, or contact Zenodo. External publication
commands appear only as nonexecuting templates in documentation and begin with
real owner-authorization validation.

## Milestones

- **M0 — Live audit and immutable baseline: complete.** Starting state,
  external collision checks, inventories, hashes, policies, official service
  assumptions, preservation set, and discussion delta are frozen above.
- **M1 — Offline release decision: complete.** Markdown/YAML records freeze
  asset, archive, identifier, upstream, and owner-gate semantics.
- **M2 — Release-content registry: complete.** The schema-valid tracked-file
  registry declares every included group, paper invariant, and exclusion.
- **M3 — Deterministic release builder: complete.** Dry-run and guarded local
  release modes inject the explicit source SHA and generate five assets.
- **M4 — Deterministic paper bundle: complete.** The bundle has 132 sorted
  normalized members including its machine-readable inventory.
- **M5 — Release verifier: complete.** Independent checks cover filenames,
  schema, checksums, archive bytes/metadata, exclusions, papers, and nulls.
- **M6 — Authorization schema and synthetic fixtures: complete.** The inactive
  template and synthetic fixtures are tested; synthetic records cannot
  authorize release mode.
- **M7 — CFF prerelease audit and correction: complete.** The false release
  date is removed and no DOI is inserted.
- **M8 — Release notes and citation asset: complete.**
- **M9 — GitHub Release and Zenodo nonexecuting plan: complete.**
- **M10 — Release-candidate Make and validation-only CI: complete.** Focused
  acceptance passes 10 tests.
- **M11 — Double-build acceptance: active.**
- **M12 — Release-readiness reconciliation: pending.**
- **M13 — Public-safe static-site status: pending.**
- **M14 — Full validation, PR merge, Pages, issue closeout, synchronized
  main, and repeated discussion delta: pending.**

Exactly one milestone is active at a time. Update this section after every
material decision, failure, correction, or completed gate.

## Progress checklist

- [x] Synchronize and verify starting `main`.
- [x] Inspect worktrees, remotes, open issues/PRs, issue #180, PRs #181-#182,
  tags, releases, and the candidate-tag collision.
- [x] Read repository governance, release, citation, licensing, paper,
  evidence, TreasureBench, Agents v1, infrastructure, and CI authorities.
- [x] Audit every result manifest and all paper metadata/validation records.
- [x] Verify all seven PDF and source hashes and the 119-page invariant.
- [x] Run the initial program-memory/release/publication/naming/site audits.
- [x] Record the exact unrelated untracked preservation set.
- [x] Complete the opening discussion and decision delta audit.
- [x] Create the release issue and one task branch.
- [x] Complete M1-M10 implementation and focused tests.
- [ ] Complete and record the M11 byte-for-byte double build.
- [ ] Reconcile M12-M13 documentation and public-safe status.
- [ ] Run M14 full local and remote acceptance.

## Discoveries and surprises

- The sandbox initially blocked `.git/FETCH_HEAD` and the shared uv cache;
  approved scoped execution allowed the required synchronization and audits
  without changing repository content.
- GitHub CLI is unauthenticated, matching the durable issue #32 record. The
  probe was performed once and will not be repeated.
- The existing release-readiness record is null-safe but not a future release
  asset builder. Its `source_revision` and `generated_utc` are null by design.
- `CITATION.cff` contains a prerelease semantic defect: the candidate version
  is paired with a historical `date-released`. Official CFF 1.2.0 guidance
  confirms that the field is optional.
- The paper lifecycle uses the currently accepted 21-page values for the three
  20-page-era papers, giving the exact live 119-page total.
- `results/index.md` is stale at 49/46 even though all manifest validation and
  current-facing status records establish 51/48.

## Decision log

- `2026-07-24T05:43:49Z`: create exactly issue #183 and the one requested task
  branch after confirming no competing substantive pull request.
- `2026-07-24T06:00:00Z`: freeze the paper archive at 132 members: 131 tracked
  declared files plus one generated machine-readable inventory.
- `2026-07-24T05:36:08Z`: use the synchronized exact starting SHA rather than
  an inferred future release commit.
- `2026-07-24T05:36:08Z`: treat the five named untracked duplicates as
  inviolable unrelated user work and never use broad staging.
- `2026-07-24T05:36:08Z`: correct the prerelease CFF by omitting
  `date-released`, not by inserting a future date or null value.
- `2026-07-24T05:36:08Z`: retain candidate version `0.1.0` in CFF because the
  repository and release policy already declare that candidate version.
- `2026-07-24T05:36:08Z`: include all seven declared local paper source
  bundles in the deterministic dry-run while keeping external publication
  blocked on owner licensing attestations.
- `2026-07-24T05:36:08Z`: use one deterministic ZIP rather than seven archives
  or a tarball because the fixed asset contract names one `papers.zip`.
- `2026-07-24T05:36:08Z`: reject symlinks rather than attempting to normalize
  them.
- `2026-07-24T05:36:08Z`: make `SHA256SUMS.txt` non-self-referential and
  require the manifest to inventory its peer assets without claiming its own
  containing commit.

### Rejected release-content and archive designs

- Commit generated binary assets: rejected because outputs must remain in an
  ignored build directory and the final source SHA is injected later.
- Archive the entire repository checkout: rejected because it risks untracked,
  private, cache, Git, and host metadata inclusion.
- Duplicate the canonical upstream paper: rejected; include only the lock,
  attribution, and integration metadata.
- Add `.zenodo.json`: rejected because its metadata precedence would silently
  override CFF.
- Reserve a DOI or emit a realistic placeholder: rejected; null is the only
  offline value.
- Use current wall time, filesystem mtime, owner/group, or host permissions:
  rejected as nondeterministic.
- Allow a committed manifest to discover `HEAD` implicitly: rejected because
  it creates self-reference and makes later exact release generation unclear.
- Validate a real local owner authorization: rejected; only synthetic tracked
  fixtures may be read.
- Add an automatic release workflow: rejected; CI remains validation-only and
  credential-free.

## Validation strategy

Focused tests cover schemas, valid/invalid authorization fixtures, tracked-file
selection, required and excluded content, paper archive membership/order,
timestamps, permissions, symlink/path traversal rejection, deterministic
serialization/compression, expected filenames, manifest schema and semantics,
checksum rules, exact PDF hashes/pages/source hashes, source revision and
null/external coordinate behavior, secret/host/private exclusions, Make/CLI
behavior, and a complete double build.

Broad acceptance runs:

```sh
git diff --check
make bootstrap
make audit-program-memory
make audit-publication-infrastructure
make audit-treasurebench-naming
make release-readiness
make audit-agents-v1
make audit-agents-v1-evaluation
make agents-v1-dry-run
make agents-v1-readiness
make compendium-release-dry-run VERSION=0.1.0
make verify-compendium-release VERSION=0.1.0
make compendium-release-readiness VERSION=0.1.0
make verify
make papers
make site
```

The scientific baseline, immutable verified-results tree, paper source/PDF
hashes, upstream pin, external tag/release endpoints, and preservation set are
rechecked before merge and after synchronized-main closeout.

## Commands and expected observations

- Dry-run builds accept explicit 40-hex source SHA and fixed UTC time; five
  assets appear under the ignored version directory with null external IDs.
- The verifier reports exactly seven PDFs, 119 pages, complete declared source
  inventory, normalized ZIP metadata, matching checksums, and no prohibited
  content.
- Two builds from identical arguments have identical asset hashes and bytes.
- Release mode refuses incomplete coordinates and remains file-only even when
  valid coordinates are supplied.
- No validation command creates a tag, release, deposit, DOI, provider call,
  private file, study, claim, run, or paper change.

## Artifacts produced

At M0: this living ExecPlan and the ignored local site build used only for
baseline inventory. No generated release asset is committed.

## Blockers

None for offline implementation. External publication remains intentionally
blocked on real owner authorization, paper/PDF/generated-figure and
third-party-asset attestations, an exact merged release commit, tag and GitHub
Release execution, owner-side Zenodo enablement, and verified ingest.

## Recovery and restart instructions

Run `git status --short --branch`, read this plan from the active milestone,
confirm the five preservation files remain untracked and untouched, inspect the
current issue/PR, and resume the first unchecked item. Never read `.env.txt` or
a local release authorization. Never rerun a scientific study or provider
workflow. Never create a tag, GitHub Release, Zenodo state, or DOI in this task.

## Outcome and retrospective

Pending. On successful M14 closeout, record the issue, PR, merge SHA, branch
and post-merge workflow IDs, live Pages checks, five double-build hashes,
complete paper-bundle inventory, unchanged science/paper/upstream trees, zero
external actions, repeated program-memory delta, exact owner actions still
required, and successor gate:
**Owner-authorized Compendium v0.1.0 external publication and Zenodo
verification**.

The next task's first command will be `git status --short --branch`, and its
future plan file will be `plans/FIRST_COMPENDIUM_RELEASE.md`. That file is not
created here.
