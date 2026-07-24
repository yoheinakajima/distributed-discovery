# TreasureBench and Treasure Hunt naming migration

This living ExecPlan is maintained under `.agent/PLANS.md`. It records the
editorial, compatibility, CLI, site, and release-metadata migration from the
historical public display name DiscoveryBench to the formal suite name
TreasureBench, together with the Treasure Hunt playable companion. This work
does not create scientific evidence.

## Purpose

Adopt the owner-selected layered naming system:

- formal suite: **TreasureBench**;
- canonical subtitle: **TreasureBench: a benchmark for collective search under
  shared and private evidence.**;
- playable companion: **Treasure Hunt**.

The migration is forward-only. DD-010, claims, runs, immutable result paths,
existing benchmark content versions, and frozen DiscoveryBench schema,
protocol, task, and metric identifiers remain unchanged. Historical routes and
commands remain usable as compatibility surfaces.

## Live state

The pre-mutation audit ran on 2026-07-23 PDT (2026-07-24 UTC).

- Repository: `yoheinakajima/distributed-discovery`.
- Starting branch: `main`.
- Starting and remote `main`: `b242e31680237538e26bae543fdac5db459b0857`.
- Expected PR #179 merge is present at that SHA.
- Open substantive pull requests: none.
- Open issues: issue #32 only; it is settings-only.
- Live Pages root and `benchmark.html`: HTTP 200.
- Scientific inventory: 110 claims through DD-C-0110; 26 studies through
  DD-022; 51 manifests; 48 passing verified-run directories.
- Site baseline: 81 HTML files, 98 JSON files, 201 generated files, 18
  registered Labs plus the Labs index, 23 checksum-covered downloads, and five
  primary-navigation items.
- Paper baseline: seven program PDFs, 119 pages total, with the hashes listed
  under Validation.
- Canonical upstream: commit
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`, PDF
  `cb4816cb3a9cdd8db0210ab8981e3729028eb02ba174f2a7300b617807cc1e04`.
- Baseline Git trees:
  - `claims`: `5f2bf6ca0817866ea6e5697707ee1aa35925d5d7`;
  - `studies`: `7b4dd8ce0d4596324584e14034db3995c99ba2e5`;
  - `results/verified`: `c8fd20f66797c5014acf658a749e7f15fcaf6750`;
  - `papers`: `b2915d025257db02d15a7a620c3fc66b978ffd1a`;
  - `studies/DD-010-discoverybench`:
    `fcc0915e397023661786bfd2ed262b3a6ee76205`.

### Preservation set

These pre-existing untracked files are unrelated owner material. They must not
be edited, staged, moved, deleted, normalized, or cleaned:

- `papers/information-sharing-frontier/paper-audit 2.json`;
- `papers/information-sharing-frontier/visual-qa 2.md`;
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`;
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`;
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`.

`.env.txt`, if present, is out of scope and must not be read or staged.

## DISCUSSION AND DECISION DELTA AUDIT

The repository previously encoded an `owner-name-decision-required` gate for
the public name then displayed as DiscoveryBench. PM-0013 recorded the need to
choose a collision-safe public name and preserved a ranked shortlist as
decision input. The current owner instruction supplies the missing decision and
supersedes every earlier BoxHunt, SearchParty, TreasureHunt-as-formal-token,
ActionPortfolioBench, and DiscoveryBench public-renaming prompt.

The decision delta is:

1. TreasureBench is selected as the formal public suite, subject only to this
   dated, bounded factual collision and compatibility gate.
2. Treasure Hunt is selected as the playable companion, never as a peer
   benchmark or formal namespace.
3. The earlier shortlist becomes historical input and is not re-ranked unless a
   new fatal TreasureBench collision is found.
4. DiscoveryBench becomes a historical/internal compatibility alias. Frozen
   identifiers and immutable evidence keep that spelling.
5. The formal suite and companion are accepted only as one family with a
   machine-enforced two-way funnel.
6. A future move toward `Treasure Hunt` or `Yohei's Treasure Hunt` is merely an
   evidence-dependent option triggered by owner-supplied sustained third-party
   usage evidence.
7. No automated adoption monitoring is authorized.

Every owner-adopted item in the task is routed below. No private social-graph
claim is recorded.

## Fixed owner decisions

- Program identity remains Distributed Discovery.
- The Shared Discovery Paradox remains the canonical result.
- The fixture remains “the sixteen-box model” or “the sixteen-box game.”
- Required formal keywords are `collective search`, `multi-agent`, `benchmark`,
  and `shared`.
- DD-010 remains the instrument and scientific owner.
- The root repository and distribution remain `distributed-discovery`.
- No standalone package is published.
- The sealed TreasureBench Agents v1 engineering pilot remains queued after the
  naming and release-infrastructure sequence.

## Evidence-scoped naming claim

The strongest permitted statement is:

> As of the recorded audit date, no disqualifying same-domain scholarly,
> AI-benchmark, multi-agent-system, package, or active high-confusion product
> collision for the exact name TreasureBench was found in the declared search
> channels.

This is not a claim of global uniqueness, exhaustive search, legal clearance,
trademark clearance, namespace ownership, guaranteed availability, or future
availability.

## Collision gate

Search exact and spaced variants across scholarly indexes, AI/benchmark and
multi-agent uses, product/software uses, GitHub, PyPI, npm, Hugging Face,
domains, and accessible preliminary trademark-register surfaces. Classify
observations with the three-tier rubric. TreasureBench may proceed only if no
Tier 1 collision is found and no unresolved Tier 2 record makes the migration
unsafe.

Permitted decisions:

- `treasurebench-selected-and-implemented`;
- `treasurebench-selected-package-publication-deferred`;
- `treasurebench-blocked-same-domain-collision`;
- `treasurebench-blocked-required-package-namespace`;
- `treasurebench-owner-reconsideration-required`.

No partial rename is permitted after a blocking decision.

## Source-of-truth boundary

Claims and registered studies remain scientific authority. DD-010 remains the
instrument owner. The naming ADR and registry are editorial and compatibility
authority only. The companion is presentation infrastructure and creates no
result, claim, run, theorem, or evidence status.

Git is authoritative for display names, subtitle, keywords, aliases, naming
hierarchy, routes, CLI compatibility, funnel rules, theme scope, collision
audit, rejection history, and the future option trigger. External registries
are observations and owner tasks only.

## Scope

- bounded collision and namespace audit;
- ADR and machine-readable naming registry;
- program-memory, roadmap, publication, and release-metadata routing;
- forward-only public display migration;
- version-transition policy;
- nonbreaking CLI aliases;
- canonical and historical route/JSON compatibility;
- static Treasure Hunt playable companion;
- funnel and lexical-policy validator;
- announcement-copy policy;
- literature disambiguation;
- owner namespace checklist;
- compatibility and closeout audits.

## Non-goals

No provider call, credentials, private task generation, evidence campaign,
sealed pilot, base campaign, scientific study, claim, immutable run, paper
edit, arXiv submission, tag, release, Zenodo deposit, DOI, package publication,
namespace reservation, legal clearance, ActiveGraph integration, SQLite, or
settings change.

## Naming layers

| Layer | Canonical name | Compatibility treatment |
|---|---|---|
| Program | Distributed Discovery | unchanged |
| Formal suite | TreasureBench | current public display |
| Companion | Treasure Hunt | interactive companion only |
| Scientific owner | DD-010 | unchanged |
| Historical display | DiscoveryBench | dated/internal alias |
| Fixture | sixteen-box model/game | unchanged descriptive language |
| Frozen schemas | `discoverybench-*` | unchanged identifiers |
| Root distribution | `distributed-discovery` | unchanged |

## Compatibility matrix

| Surface | Existing behavior | New behavior | Invariant |
|---|---|---|---|
| DD-010 | stable study path and ID | TreasureBench display note | path and ID unchanged |
| Schemas | frozen DiscoveryBench IDs | future transition policy | bytes and IDs unchanged |
| CLI | current benchmark and Agents commands | TreasureBench aliases | old commands still pass |
| Routes | benchmark/DiscoveryBench surfaces | canonical TreasureBench surfaces | old routes HTTP 200 |
| JSON | existing benchmark endpoints | TreasureBench display metadata | load-bearing old JSON remains |
| Runs/results | immutable paths and IDs | none | exact Git trees unchanged |
| Papers | seven working PDFs | future metadata only | sources, PDFs, hashes unchanged |

## Schema/version policy

Frozen `discoverybench-task-v1/v2/v3`, suite, task, protocol, metric, Agents v1,
certificate, and historical result identifiers remain unchanged. The next
substantive nonfrozen content/schema version may adopt TreasureBench only
through an explicit transition and compatibility record. Rebranding alone
does not create a content version.

## Route migration

Create a canonical TreasureBench overview and matching current routes under the
existing builder architecture. Keep every existing benchmark route as an HTTP
200 compatibility page or compatibility-preserving surface, publish canonical
links, prevent loops, preserve DD-010, and keep load-bearing JSON endpoints.
Record aliases in machine-readable route metadata.

## CLI and package aliases

Keep the root distribution and `distributed-discovery` script. Add
`distributed-discovery treasurebench ...` aliases for safe public operations,
delegating to existing implementations. Add a `treasurebench` console-script
alias only if it remains a delegate and packaging tests pass. Preserve current
benchmark, DiscoveryBench, Agents v1, imports, examples, and Make targets.

## Companion design

Treasure Hunt is a dedicated interactive guide rather than a scientific Lab.
It uses the public sixteen-box fixture and existing evidence only. Required
modules:

1. Better maps, one shovel hole.
2. Split the crew.
3. Copied maps.
4. One map reader.
5. Minimum digging crew.

Every metaphor appears next to its formal term, owning studies/claims/evidence,
and limitations. Deterministic illustrative state is explicitly labeled. A
complete no-JavaScript fallback is part of the same page.

## Funnel

- Treasure Hunt prominently states “The playable companion to the TreasureBench
  suite.” and links directly to TreasureBench.
- Current TreasureBench overview surfaces name and link Treasure Hunt in their
  opening material.
- README and future benchmark-paper metadata name the companion early.
- Announcement templates pair both names on first mention.
- Structured metadata identifies formal instrument versus interactive
  companion.
- The naming audit fails when any required edge is missing.

## Theme boundary

Monochrome chart, route, box-grid, X, compass, fragment, shovel, and crew motifs
are allowed only in the companion and restrained links/cards. Scientific
claims, theorems, metric/schema fields, IDs, estimands, comparators, evidence
status, mathematical prose, and immutable evidence remain unthemed. Every
themed element must be removable without changing a scientific result.

## Literature disambiguation

The future benchmark paper must distinguish classical distributed/mobile-agent
treasure-hunt problems—navigation through graphs/grids to an inert hidden
target with traversal, time, advice, memory, or communication complexity—from
TreasureBench’s shared/private evidence, action portfolios, discovery/coverage,
and exact private/planner/equilibrium comparators. Primary citations are
required. No paper is edited or created in this milestone.

## Namespace owner tasks

Prepare, but do not perform, owner checks/reservations for PyPI, npm, GitHub,
Hugging Face, an optional domain, optional social handles, and one-time
USPTO/EUIPO preliminary register scans before a first DOI or package release.
All reservation statuses remain `not-performed`.

## Milestones and progress

- [x] M0: verify live Git/GitHub state, mandatory governance context,
  discussion delta, scientific inventory, paper hashes, site baseline, and
  preservation set.
- [x] M1: perform the bounded TreasureBench collision and namespace search;
  no exact-name Tier 1 collision found at the decision checkpoint.
- [x] M2: commit ADR skeleton and machine-readable naming system.
- [x] M3: route program memory and roadmaps.
- [x] M4: migrate formal public display metadata.
- [x] M5: record schema/version transition and preservation tests.
- [x] M6: implement and test CLI aliases.
- [x] M7: implement route, alias, and JSON compatibility.
- [x] M8: launch the Treasure Hunt companion.
- [x] M9: implement the one-bit accessible visual system.
- [x] M10: implement funnel and lexical-policy audit.
- [x] M11: add communication templates.
- [x] M12: add the literature boundary and paper checklist.
- [x] M13: add the owner namespace checklist.
- [x] M14: reconcile null-safe release/citation/publication metadata.
- [x] M15: complete the historical compatibility audit.
- [x] M16: complete site/public integration.
- [ ] M17: validate, push, ready, merge, verify Pages/live routes, close the
  issue, and synchronize `main`.

Focused acceptance currently passes the naming/schema, frozen-ID, old/new CLI,
program-memory, publication-infrastructure, and complete site-integration
tests. The generated site has 89 HTML pages, 110 public JSON files, 221 total
files, 18 registered Labs, 23 downloads, and five primary-navigation items.

## Discoveries and surprises

- The formal suite can be introduced without a content-version bump because
  the builder can publish canonical display copies while leaving frozen
  lowercase identifiers and historical JSON intact.
- Historical route compatibility is stronger as full HTTP 200 pages with
  visible alias notes and canonical links than as client-side redirects; it
  also preserves fragments and no-JavaScript behavior.
- The existing relationship injector originally attached benchmark evidence
  only to the new canonical task/results routes. Focused integration testing
  caught that the corresponding historical pages had lost their relationship
  panels; both route families now receive the validated relations.
- Treasure Hunt fits a dedicated guide route rather than the Labs registry.
  This keeps its five modules public and interactive without implying
  scientific evidence ownership.

## Decision log

- 2026-07-23: select `treasurebench-selected-and-implemented` after the bounded
  exact-name gate found no disqualifying same-domain collision.
- 2026-07-23: keep `distributed-discovery` as the root distribution and add
  delegating command aliases; authorize no standalone package publication.
- 2026-07-23: preserve historical routes as full HTTP 200 compatibility pages
  with canonical metadata.
- 2026-07-23: classify Treasure Hunt as a presentation-only interactive guide,
  not a registered Lab.
- 2026-07-23: expand program memory from 25 to 29 routed records, including the
  layered system, companion, vernacular trigger, and rejection history.

## Discoveries and surprises

- The exact formal token `TreasureBench` produced no exact scholarly,
  AI-benchmark, multi-agent, package, GitHub-repository, or Hugging Face
  artifact match in the declared checks at the decision checkpoint.
- The spaced phrase “Treasure Bench” produces unrelated furniture/memorial
  products. This is Tier 3 lexical residue, not a same-domain collision.
- “Treasure Hunt” is used in classical navigation, reinforcement-learning,
  active-perception, and multi-agent examples. This is not an exact
  TreasureBench collision, but it makes the formal/companion boundary and
  future-paper disambiguation materially necessary.
- Public domain/RDAP and registry observations are transient and
  nonauthoritative; owner reservation remains a separate action.
- GitHub CLI has no authenticated account in this environment. Repository
  mutations use the connected GitHub application; local Git uses the existing
  SSH remote.

## Decision log

- 2026-07-23: accept the owner decision as the sole active naming decision; do
  not re-rank the historical shortlist.
- 2026-07-23: treat Treasure Hunt literature as a disambiguation requirement,
  not a fatal collision for the exact formal token TreasureBench.
- 2026-07-23: proceed with
  `treasurebench-selected-and-implemented`, conditional on compatibility,
  validation, CI, and live acceptance.
- 2026-07-23: implement the companion as a dedicated guide so its presentation
  role cannot be mistaken for registered scientific ownership.

## Validation

Run and record the repository-required focused tests and:

```text
git diff --check
make bootstrap
make audit-program-memory
make audit-publication-infrastructure
make release-readiness
make audit-treasurebench-naming
make audit-agents-v1
make audit-agents-v1-evaluation
make agents-v1-dry-run
make agents-v1-readiness
make verify
make papers
make site
```

Do not run live provider-backed calibration or preflight targets.

Baseline paper hashes:

- Foundations:
  `8875926a52f0b8e722f7ce827c456c4b694f9e981c21c4b15bf2b3c60b83e76b`
- Three Results:
  `9eb896353b1210706d6108685dde963e02d6a5ebc64af9f9f69c08c01f5ebc96`
- Discovery Institutions:
  `78606f732f105d79395409dcb9d7224d72aa1e44312ca30ff5719d049afd98a8`
- Common-Source Trap:
  `afa9384eca60cf2a0291c2c42012f15ca59bf3d29b7c939b1882a0237ea58ff7`
- Incentive to Ignore:
  `651c91fb68df6b2f1397ca86f3842b7c2fa9c067601957c32401a7f5e95cd24b`
- Threshold Discovery:
  `634e96662989a3fd6efb5fc3e6919883897e60511826e25c6d0176bac4af9249`
- Information Sharing Frontier:
  `a317e8851a84b494d8ef30eccc1e31dd4448dc1bbcd3fb2de0fc2849bd581a13`

The final validation must reproduce 119 pages and exact hashes, unchanged Git
trees for claims, studies, verified results, papers, and DD-010, zero provider
calls, zero private material, and the untouched preservation set.

## Recovery

Changes are additive or compatibility-preserving and are made in small
milestone commits. If a fatal collision appears before public migration, keep
only the audit, owner decision, and reconsideration record; do not partially
rename or launch the companion. If compatibility fails after implementation,
repair the alias/route/CLI surface before making the PR ready. Never rewrite
immutable evidence or force-push.

## Outcome and retrospective

Pending. Normal completion requires a passing collision decision, implemented
formal/companion hierarchy, complete two-way funnel, preserved frozen
identifiers and historical interfaces, unchanged scientific/paper artifacts,
passing CI and Pages, a closed issue, and synchronized `main`.
