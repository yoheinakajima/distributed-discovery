# Master execution plan

> The M0–M9 and A–E material below is retained as historical execution evidence. Current operational state and the active continuation queue are recorded in the opening sections, blockers, and recovery instructions; stale no-remote/private statements inside completed-milestone history describe the state at that time.

## Purpose and intended outcome

Bootstrap and execute a durable, auditable research program for Distributed Discovery while preserving the Shared Discovery Paradox repository as the canonical, read-only public presentation.

## Active continuation — Governance and Incremental Sharing (2026-07-22)

### Purpose and intended outcome

Complete the next single-lane Program V5 continuation: formalize the research
and publication hierarchy; execute and independently verify Incremental Sharing
and Independent Rescue as the next live study; apply the editorial theorem
gate; and publish the program map and an output-connected Incremental Sharing
Lab. Preserve the distinction among registered studies, theorem-family papers,
the living synthesis, and infrastructure.

### Current state

The live audit at `2026-07-22T13:55:13Z` found clean `main` at
`5e6c800213232be2fdcdc2aa19027fb5a8400e85`, matching `origin/main`; no open
pull request; issue #32 as the only pre-existing open issue; 91 claims, 48
manifests with 45 passing runs, 23 studies, six validated papers, 69 HTML
routes, 67 public data files, and 16 Labs. CI `29906411957` and Pages
`29906411981` pass for that main commit, and the root plus DD-019 study/data,
Claims, and Evidence routes return HTTP 200. The one authorized `gh auth
status` call found no authenticated CLI host, so settings mutation is not
retried; SSH and the connected GitHub integration remain available.

Two older auxiliary worktrees exist. The roadmap worktree contains unrelated
untracked files and neither auxiliary worktree is used or modified by this
continuation. All substantive work remains in the primary worktree with one
active branch and pull request at a time.

### Scope

1. Issue #133 and branch `docs/research-governance-publication-architecture`:
   governance, publication architecture, synthesis scaffold, factual status
   reconciliation, and the public program page; no research evidence.
2. After merge, allocate the next live study ID and execute Incremental Sharing
   under a newly frozen exact model, independent verifier, corruption tests,
   immutable run, and separate claim audits.
3. After research merge, apply the Incentive to Ignore and Threshold Discovery
   editorial gates and add the living-synthesis prospectus; no new run.
4. After editorial merge, publish the DD-020 result and output-connected Lab,
   then perform full repository, paper, site, browser, accessibility, security,
   provenance, and live-route acceptance.

### Non-goals

No General Sharing Frontier stretch study unless all four required milestones
are merged and capacity remains. No submission, arXiv upload, DOI, release,
journal contact, human data, real data, settings retry, canonical-upstream
mutation, or rerun of any passing primary configuration.

### Assumptions

The symmetric noisy-point theorem begins at `p>=1/M`; the registered direct
private action is the Bayes point action; pooled ties use independent uniform
randomization; the first research study is simultaneous, common-objective,
one-hit search without strategic rewards. Every broader statement remains a
conjecture until proof or an exact counterexample supplies the permitted status.

### Milestones

- **A (complete):** governance and publication architecture, issue #133 and
  PR #134.
- **B (active):** DD-020 Incremental Sharing and Independent
  Rescue.
- **C:** editorial theorem gate and synthesis prospectus.
- **D:** public DD-020 integration and output-connected Lab.
- **Acceptance:** complete repository/paper/site/live audit and final handoff.

### Progress checklist

- [x] Read the governing instructions, required current-state documents,
  DD-019, DD-012--014, relevant DD-001/DD-002/DD-010 records, and current site
  builders.
- [x] Audit local Git, worktrees, remote main, open issues/PRs, CI, Pages, live
  routes, and factual inventories; run `gh auth status` exactly once.
- [x] Create issue #133 and the sole active Milestone A branch.
- [x] Complete, validate, merge, deploy, close, and synchronize Milestone A.
- [ ] Register and complete DD-020 Incremental Sharing and Independent Rescue.
- [ ] Apply and merge the editorial theorem gate and synthesis prospectus.
- [ ] Build and deploy the DD-020 public integration and Lab.
- [ ] Run final acceptance and reconcile every required handoff document.

### Discoveries and surprises

- `studies/index.md` still labels DD-019 deployment pending, while PR #131 and
  deployment closeout PR #132 are merged and current-state/live-route evidence
  confirms deployment.
- `reports/project-status.md`, `reports/final-handoff.md`, `site/README.md`, and
  portions of the roadmap retain pre-DD-019 inventory or resume language.
- The GitHub Pages builds endpoint returns 404 without settings-capable
  authentication, but the public Actions API records the successful Pages
  workflow and live routes pass; this is not a research blocker.
- The first targeted site test invoked `uv run --no-editable pytest` directly
  after a package reinstall and loaded the previously installed non-editable
  package rather than current `src`. It failed because `program.html` and the
  footer link were absent from that stale package. Re-running with the
  Makefile-equivalent `PYTHONPATH="$PWD/src"` passed all 13 targeted tests; no
  research output or run was created.
- Milestone A PR #134 passed push CI `29926942819`, PR CI `29926944262`, and
  paper/site build `29926944328`, squash-merged as `dc32ff17`, and closed issue
  #133. Post-merge CI `29927131835`, Pages `29927132030`, and the live Program,
  Research, Papers, and route-registry pages pass. The live registry still ends
  at DD-019, so issue #135 and branch `research/dd020-incremental-sharing`
  allocate DD-020.

### Decision log

- `2026-07-22T13:55:13Z`: preserve the user-specified four-milestone order and
  branch names; use the connected GitHub integration for issues/PRs/merges and
  SSH for Git transport because CLI authentication is unavailable.
- `2026-07-22T13:55:13Z`: do not remove or clean the unrelated auxiliary
  worktrees; record them and keep this continuation in the primary worktree.
- `2026-07-22T13:55:13Z`: Milestone A is documentation/presentation only, so
  its acceptance must demonstrate unchanged claims, manifests, passing runs,
  scientific outputs, and paper PDF checksums.
- `2026-07-22T14:03:38Z`: retain the direct non-editable targeted-test failure
  as an environment-cache observation and use the repository Make targets,
  which export `src`, for authoritative validation.
- `2026-07-22T14:13:02Z`: mark Milestone A complete only after merge,
  post-merge CI/Pages, live-route checks, issue closure, and synchronized clean
  main. Allocate DD-020 only after the repeated live registry and open-PR audit.

### Validation strategy

Milestone A runs `git diff --check`, `make bootstrap`, `make verify`, and `make
site`, compares frozen inventories/checksums, then checks branch and post-merge
CI/Pages plus live routes. Milestone B adds targeted exact-method agreement,
normalization, bounds, invariance, theorem regressions, all registered
corruptions, one clean immutable primary run, separate claim audits, paper
provenance checks if affected, and visual QA. Milestones C and D do not execute
research targets. Final acceptance runs all named Make gates plus claim,
manifest, exact-verifier, corruption, schema, route, browser, accessibility,
PDF, secret, host-path, license, provenance, and upstream-cleanliness audits.

### Commands and expected observations

- `make verify`: the existing suite passes without executing registered long
  studies; counts rise only when the scoped milestone adds tests or claims.
- `make site`: all routes, fragments, downloads, no-JavaScript fallbacks, and
  public-safety checks pass; Milestone A adds `program.html` without changing
  research inventories.
- The eventual registered DD-020 primary target runs once from clean committed
  source after its draft PR opens and writes a new immutable directory.

### Artifacts produced

Issue #133; draft PR #134; `docs/research-governance.md`;
`docs/publication-architecture.md`; `docs/paper-family-map.yml`; the seven-file
living-synthesis scaffold; the contextual `program.html` builder and tests; and
`reports/governance-publication-architecture-validation.md`. No DD-020 ID,
claim, run, or result exists yet.

### Blockers

No scientific blocker. Settings issue #32 remains authority-blocked and
separate. A genuine environment boundary uses the user-specified hard-session
checkpoint without presenting incomplete work as completion.

### Recovery and restart instructions

Inspect `git status --short --branch`, read this section and the nearest active
study files, query open PRs/issues, and resume the first unchecked item. Do not
rerun any passing primary configuration. If Milestone A is merged, synchronize
`main` before allocating the next live study ID.

### Outcome and retrospective

Milestone A is complete and deployed without changing evidence inventories or
paper PDFs. Its hierarchy resolves the previous ambiguity between a study and
a paper while keeping program synthesis non-evidentiary. Milestone B is the
sole active milestone. Update after every material decision, failed check,
immutable run, claim audit, merge, and deployment.

## Current state

### Program V4 complete; Information Sharing Frontier queue next (2026-07-22)

Owner authorization on 2026-07-22 starts Program V4, *Threshold Discovery:
Coordination, Crowding, and Minimum Viable Teams*, sequentially after the
completed Program V3 handoff at clean `main` commit
`cb60a882e72056c669871b53ef26d10ae9edee27`. The Program V4 research object is
posterior-ranked finite search with threshold success; it must distinguish
deterministic planner allocations, correlated recommendations, and strategic
decentralized choice. Its public qualification is: when actions require teams,
form the smallest viable teams and diversify those teams. The program slogan
remains “Share the evidence. Diversify the actions.”

The required Program V4 order is: (1) Program V3 editorial synchronization
without new research evidence; (2) DD-016 threshold discovery; (3) DD-017 equilibrium
selection and coalition stability; (4) DD-015 at its original registered
boundary; (5) DD-018 minimum-viable-team mechanisms; (6) DiscoveryBench v3
and the synthetic experimental extension; (7) the focused paper; (8) public
Threshold, equilibrium, dynamic, and mechanism Labs; and (9) final acceptance
and handoff. Each executed study requires a bounded registration, resource
estimate, immutable primary run, independent verifier, corruption test where
applicable, claim audit, public-safe data, and local acceptance before any
remote transaction.

After the merged Program V4 handoff, Program V5 begins with a
documentation-only baseline and then one bounded Signal Geometry study. The
Information Sharing Frontier moves ahead of Reliable Discovery without deleting
or weakening any later theorem-roadmap direction.

The initial local safety audit is recorded in
`reports/program-v4/parallel-safety.md`. The GitHub CLI remains unauthenticated
and is not retried, but the connected GitHub integration and SSH transport
support issues, pull requests, merges, CI/Pages inspection, and live-route
verification. Program V4 is complete at its registered bounded scope. The
documentation-only final handoff on issue #126 creates no research run or
claim; after it merges, V5.0 is the sole next milestone.

Progress:

- [x] V4.1 — Synchronize V3 public copy and validate local public artifacts.
- [x] V4.2 — Register, execute, independently verify, and integrate DD-016.
- [x] V4.3 — Register, execute, independently verify, and integrate DD-017.
- [x] V4.R — Merge the documentation-only Information Sharing Frontier roadmap
  reconciliation without changing claims, runs, studies, scientific source,
  papers, site routes, or public data.
- [x] V4.4 — Execute DD-015 at its registered baseline, then separately assess
  the bounded threshold extension.
- [x] V4.5 — Execute and verify DD-018 mechanisms.
- [x] V4.6 — Extend DiscoveryBench and the synthetic experiment kit.
- [x] V4.7 — Build the focused paper and Program V4 Labs.
- [x] V4.8 — Run final acceptance, reconcile documentation, and hand off.
- [x] V5.0 — Merge the Program V5 documentation baseline after V4 handoff.
- [x] V5.1 — Register, execute, verify, merge, and deploy the first bounded
  Signal Geometry and Action-Budget Discovery Profile study as DD-019.

Validation strategy: use `make bootstrap`, `make verify`, `make papers`, and
`make site` at the prescribed gates; retain immutable run artifacts and run
specific certificate, corruption, schema, browser, accessibility, checksum,
license, host-path, provenance, and upstream-cleanliness checks before final
acceptance. Do not rerun a passing primary configuration only to refresh time
or provenance.

Recovery: inspect `git status --short --branch`, read this section,
`docs/current-roadmap.md`, and `reports/final-handoff.md`, then continue the
first unchecked item. No Program V4 immutable primary run may be rerun for
freshness. After the merged handoff, open the documentation-only V5.0 baseline;
do not register the first V5 study before that baseline merges.

### Program V4 progress log

- 2026-07-22: Program V4 handoff PR #127 passed both branch workflows and
  squash-merged as `63c235c`, closing issue #126. Post-merge CI `29903494511`
  and Pages `29903493659` passed, and the root, route registry, Threshold Lab,
  and focused-paper routes returned HTTP 200. V5.0 issue #128 and branch
  `docs/program-v5-information-sharing-frontier` are now the sole active lane.
  This baseline is documentation-only and creates no study ID, claim, run,
  result, or scientific source.
- 2026-07-22: Program V5 baseline PR #129 passed both branch workflows and
  squash-merged as `ac2fb32`; post-merge CI `29904077156` and Pages
  `29904077239` passed. The live registry contains 22 studies through DD-018,
  so issue #130 and branch `research/dd019-signal-geometry` register DD-019.
  Its exact `M=4`, `N=3`, five-channel source has at most 2,048 labeled
  target/signal states per channel. Two exact methods, schema and normalization
  checks, profile bounds, same-accuracy test, and three corruption gates pass;
  full pre-run acceptance is 216 tests, 88 claims, 47 manifests, and a
  69-page/23-study site. No DD-019 run or claim exists before the clean source
  commit and draft PR.
- 2026-07-22: DD-019 source froze as `a77bb786` and draft PR #131 opened before
  the sole primary run `20260722T084145Z_DD-019_a77bb786_04a5e9f0c5`. The run
  passed exact labeled and independent histogram agreement for all 15 profile
  entries and rejected three corruptions. The half-accurate point and
  guaranteed two-shortlist share one-person accuracy `1/2` and direct private
  discovery `7/8` but have profiles `(7/12,43/54,25/27)` and `(17/18,1,1)`;
  their recovery budgets are three and one. DD-C-0089 through DD-C-0091 pass
  separate audits at the bounded computational scope. The active gate is full
  acceptance, ready PR, merge, post-merge CI/Pages, issue closure, and live
  routes. The primary run must not be repeated.
- 2026-07-22: DD-019 final local acceptance passed bootstrap, Ruff, MyPy on
  138 source files, all 217 tests, the 91-claim ledger, all 48 manifests, six
  papers totaling 89 pages, and the 69-page/23-study site. The Three Results
  paper changed only through generated claim-ledger provenance, remains 14
  pages, and passed a new all-page visual review at SHA-256 `8ea2afc82a4a`.
  The exact DD-019 profile SVG also passed visual review. The active action is
  the evidence commit, push, ready PR #131, CI, merge, Pages, and live route.
- 2026-07-22: DD-019 PR #131 passed CI `29905637596`, paper/site build
  `29905637109`, and push CI `29905634475`, then squash-merged as `59f6f85`,
  closing issue #130. Post-merge CI `29905840583` and Pages `29905840831`
  passed. The live study, study JSON, claims, evidence, and research routes
  returned HTTP 200 with the immutable run and DD-C-0089–0091. Browser QA
  confirmed semantic landmarks, exact content, claim links, and width
  containment. V5.1 is complete; Incremental Sharing remains unregistered.

- 2026-07-22: owner authorization reconciles the long-term theorem portfolio
  with Program V5, the Information Sharing Frontier. Live audit found clean
  `main` at `86998dff`, no open pull request, only settings issue #32 open, 78
  claims, 38 verified-run manifests, 21 study directories, six paper validation
  records, and no Labs V2 branch or route. `gh auth status` was run exactly once
  and found no authenticated host; issue and PR work uses the connected GitHub
  integration and SSH, while settings mutation remains unattempted. Issue #108
  and branch `docs/information-sharing-frontier-roadmap` are active. This is a
  documentation-only milestone: it creates no claim, run, study, study ID,
  scientific code, paper, site route, or public data. Exactly one active
  milestone is V4.R; after its merge the next milestone is DD-015.
- 2026-07-22: V4.R local acceptance passed `git diff --check`, `make
  bootstrap`, Ruff formatting and lint, MyPy on 121 source files, all 194 tests,
  the 78-claim ledger, and all 42 run manifests. The changed-file audit contains
  only six documentation and planning files and no claim, result, study,
  scientific source, paper, site source, generated route, or public-data file.
  The active gate is the clean documentation commit, draft PR, CI, merge,
  post-merge CI/Pages verification, issue closure, and main synchronization.

- 2026-07-22: V4.1 updated the generated home and Results copy without creating
  research evidence. The home now includes the validated Incentive to Ignore
  finding after the initial viewport, retains the canonical guide, and preserves
  the original slogan while adding the team-specific qualification. Results now
  link DD-012 first- and duplicate-use effects, the exact bounded
  excessive-attention census, DD-013's audience result, and DD-014's
  larger-class counterexample. DD-015 stays registered and unexecuted; the
  metadata-driven Papers surface continues to verify its card, PDF, source,
  checksum, and citation.
- 2026-07-22: The focused presentation tests passed 13 tests and make site
  passed with 59 pages and 19 studies. The first full gate stopped at ruff
  format --check because the edited generator and test needed formatting; that
  non-scientific failure is retained. After formatting, make verify passed
  Ruff, MyPy on 113 source files, and all 183 tests. Make papers passed all
  five papers, including the 20-page Incentive to Ignore PDF with SHA-256
  prefix ee9e27f741d2, and make site passed.

Active milestone: V4.2 DD-016 registration, literature review, model/proof,
and bounded exact implementation. No DD-016 numerical claim may be promoted
before its independent verifier and immutable primary run pass.

- 2026-07-22: editorial PR #100 passed CI and squash-merged as eb639f85.
  Main and the DD-016 branch were synchronized to the merge. DD-016 issue #101
  now records the bounded scope. The focused literature pass, qualified planner
  proof, strategic payoff derivation, registered 490,314-vector configuration,
  labeled evaluator, 67-orbit histogram evaluator, exact occupancy accounting,
  threshold phase diagram, verifier, four corruption gates, and six targeted
  tests are implemented. A preliminary dirty-tree check found exact agreement
  across 30 signal classes and recovered all candidate canonical regressions;
  it is explicitly not research evidence. Make verify passes 189 tests and
  make site passes 60 routes and 20 studies. The only active milestone is the
  clean source commit and single immutable DD-016 primary run.
- 2026-07-22: the frozen DD-016 source was committed as 00271ff8 and draft PR
  #102 opened. The one registered primary execution created immutable run
  `20260722T021526Z_DD-016_00271ff8_123b2809e3` in 11.998247 seconds from a
  clean tree. Its 490,314-vector and 67-orbit methods normalize and agree on all
  eight threshold rows; 63 planner audits, 35 payoff audits, and four corruption
  gates pass. Separate claim audits promote DD-C-0071 and DD-C-0072 to verified
  and DD-C-0073 and DD-C-0074 to independently reproduced. The active V4.2
  gate is repository/site acceptance, PR CI, merge, post-merge CI, Pages, and
  the live study route; the primary run must not be repeated.
- 2026-07-22: DD-016 local acceptance passed `make bootstrap`, Ruff, MyPy on
  117 source files, all 189 tests, the 74-claim ledger, all 41 manifests, and
  `make site` with 60 pages and 20 studies. Draft PR #102 can advance after the
  evidence commit is pushed and its GitHub checks pass.
- 2026-07-22: PR #102 passed CI and artifact checks, squash-merged as 571a8ddf,
  closed issue #101, and passed post-merge CI run 29885814993 and Pages run
  29885814975. The live DD-016 study and JSON returned HTTP 200 with the run and
  DD-C-0071 through DD-C-0074. V4.2 is complete and its primary run must not be
  repeated.
- 2026-07-22: V4.3 started from merged main on
  `research/dd017-threshold-equilibrium-selection` with issue #103. The frozen
  start-gate registry contains 160 games, 3,728 occupancy states, 87,216 labeled
  verifier profiles, exact strict-member pair and tau-player deviation audits,
  and a separate tied-mode mixed-payoff check. Preliminary dirty-tree counts are
  not evidence. The active gate is full validation and a clean source commit
  before any DD-017 primary run.
- 2026-07-22: DD-017 pre-run acceptance passed Ruff, MyPy on 121 source files,
  all 194 tests, the unchanged 74-claim ledger and 41 manifests, and `make site`
  with 61 pages and 21 studies. The implementation remains non-evidence until
  committed and executed once from a clean tree.
- 2026-07-22: DD-017 source was frozen as 033452f and draft PR #104 opened.
  The one registered primary run
  `20260722T024032Z_DD-017_033452f6_3d2c74fdfb` passed in 8.234274 seconds from
  a clean tree. It confirms 52 zero-worst-discovery games, eight games without
  a pairwise-strict-stable pure equilibrium, 35 without an exact-size-tau-
  strict-stable pure equilibrium, and 21 tied-mode failures, all at tau one.
  Separate audits promote DD-C-0075 and DD-C-0076 to verified and DD-C-0077
  and DD-C-0078 to independently reproduced. The active V4.3 gate is local
  acceptance, PR CI, merge, post-merge CI, Pages, and live-route validation.
- 2026-07-22: DD-017 local acceptance passed Ruff, MyPy on 121 source files,
  all 194 tests, the 78-claim ledger, all 42 manifests, and `make site` with 61
  pages and 21 studies. Draft PR #104 can advance after the evidence commit and
  its remote checks pass.
- 2026-07-22: PR #104 passed CI and artifact checks, squash-merged as 5028802f,
  closed issue #103, and passed post-merge CI run 29886907269 and Pages run
  29886907217. The live DD-017 study and JSON returned HTTP 200 with the run and
  DD-C-0075 through DD-C-0078. V4.3 is complete; the next sequential milestone
  is V4.4, DD-015 at its original registered boundary.
- 2026-07-22: roadmap PR #109 squash-merged as `6cd7190`; post-merge CI
  `29890818431`, Pages `29890818405`, and the public root passed, closing issue
  #108. DD-015 issue #110 and branch `research/dd015-dynamic-attention` are now
  the sole active lane. The original baseline freezes 32 parameter cells, 64
  fixed/stopping objective rows, 5,184 unique labeled target/signal paths, a
  full-duplicate-credit sequential Bayesian equilibrium, an exact common-
  information planner DP, and a separate labeled verifier with four corruption
  gates. Non-evidence preview regression targets include 38 strict planner
  gains and a bounded null for visibility-improved dispersion. After retained
  Ruff, MyPy, and public-phase integration failures were corrected, pre-run
  `make verify` passed MyPy on 125 source files, all 198 tests, the unchanged
  78-claim ledger, and all 42 existing manifests. The active gate is bootstrap,
  site validation, the clean source commit, and exactly one primary run.
- 2026-07-22: DD-015 primary run
  `20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a` passed in 13.971626 seconds,
  supporting verified DD-C-0079 through DD-C-0081. Only after that baseline
  passed, secondary threshold-two run
  `20260722T044453Z_DD-015_34bc4379_33e1da478b` passed in 13.842954 seconds and
  supports planner-only DD-C-0082. The baseline retains the 18-of-32 bounded
  visibility-herding negative result; the threshold extension preserves
  fixed/stopping discovery and reduces actions in all 16 cells while exercising
  all registered team-action categories. The active gate is full acceptance,
  PR #111 CI/merge, post-merge CI/Pages, and live routes. Neither run may be
  repeated for freshness.
- 2026-07-22: PR #111 passed CI and artifact checks, squash-merged as
  `9f2fc1e`, and closed issue #110. Post-merge CI run `29892156549` and Pages
  run `29892156556` passed. The live DD-015 study and JSON returned HTTP 200
  with both immutable run IDs and DD-C-0079 through DD-C-0082. V4.4 is
  complete; DD-018 is the next sequential milestone.
- 2026-07-22: DD-015 deployment closeout PR #112 merged as `ece0db1` and
  passed post-merge CI `29892572238` and Pages `29892572237`. DD-018 issue
  #113 and branch `research/dd018-minimum-viable-team-mechanisms` are the sole
  active lane. Its v1 start gate freezes `M=3`, `N=4`, `tau=2`, five posterior
  fixtures, ten mechanisms, 50 mechanism-fixture rows, 81 labeled action
  profiles per fixture, and a 4,050-entry independent action-table audit. No
  DD-018 run or claim exists; the next gate is targeted and repository
  verification before the clean source commit.
- 2026-07-22: DD-018 source froze as `a193f602` and draft PR #114 opened before
  the sole primary run `20260722T051847Z_DD-018_a193f602_3b3ddac173`. The run
  passed in 0.432822 seconds. The primary 81-profile evaluator and independent
  4,050-entry table agree on all 50 rows, all five planner audits pass, and four
  corruptions are rejected. Separate audits promote DD-C-0083 through
  DD-C-0086 as verified bounded computational results. The active gate is full
  repository/site acceptance, evidence commit, PR CI/merge, post-merge
  CI/Pages, issue closure, and live routes; the run must not be repeated.
- 2026-07-22: DD-018 PR #114 passed CI and paper/site artifact checks and
  squash-merged as `6a533d1`, closing issue #113. Post-merge CI
  `29893840755` and Pages `29893840796` passed. The live study and JSON returned
  HTTP 200 with the immutable run and DD-C-0083 through DD-C-0086. V4.5 is
  complete; DiscoveryBench v3 is the next sequential milestone.
- 2026-07-22: DD-018 closeout PR #115 merged as `f45c18b` and passed
  post-merge CI `29894183858` and Pages `29894183861`. DiscoveryBench v3 issue
  #116 and branch `research/discoverybench-v3-program-v4` are the sole active
  lane. Its frozen registration has 24 tasks, 29 protocols, 39 metrics, 696
  candidate pairs, 36 compatible exact rows, and 660 explicit exclusions. It
  adds four DD-016/017/015/018 tasks while preserving v1 and v2, capability
  isolation, disabled external adapters, and no composite score. No v3 run or
  claim exists before the clean-source gate.
- 2026-07-22: DiscoveryBench v3 source froze as `d265e480` and draft PR #117
  opened before the sole run `20260722T054447Z_DD-010_d265e480_6930915b02`.
  The run passed in 0.544999 seconds with 24 tasks, 29 protocols, 39 metrics, 36
  independently reproduced exact rows, and 660 exclusions. V1/v2 metric
  vectors are preserved, all provenance and capability checks pass, three
  corruptions are rejected, and no composite score exists. DD-C-0087 passed
  its separate audit. The active gate is full repository/site acceptance,
  evidence commit, PR CI/merge, post-merge CI/Pages, issue closure, and live
  benchmark/data routes; the run must not be repeated.
- 2026-07-22: DiscoveryBench v3 PR #117 passed CI and paper/site artifact
  checks and squash-merged as `3b4fdbe`, closing issue #116. Post-merge CI
  `29895085124` and Pages `29895085148` passed. The live benchmark, DD-010
  study, v3 schema, and summary routes returned HTTP 200; the live summary
  names the immutable run and reports the frozen 24/29/39 registries with 36
  compatible pairs and 660 exclusions. The benchmark half of V4.6 is complete;
  Synthetic Experiment v3 is next, and the benchmark run must not be repeated.
- 2026-07-22: DiscoveryBench v3 closeout PR #118 merged as `f80112c`; post-merge
  CI `29895505006` and Pages `29895505051` passed. Synthetic Experiment v3
  issue #119 and branch `research/synthetic-experiment-v3-program-v4` are the
  sole active lane. Its frozen registration has 37 cells, 20 hypotheses, 23
  outcomes, 14 response scenarios, 1,184 assignments, 1,680 power rows, and
  1,680,000 seeded draws under 600-second/2 GB caps. It preserves v1/v2,
  retains all calibration failures, checks four Program V4 source fixtures,
  and prohibits human execution. No v3 run or claim exists before the clean
  source commit and draft PR.
- 2026-07-22: Synthetic Experiment v3 pre-run acceptance passed bootstrap,
  Ruff, MyPy on 133 source files, all 210 tests, the unchanged 87-claim ledger
  and 46 manifests, and the 62-page/22-study site. Small seeded verifier tests
  preserve v2 power rows under shared seeds, check all four Program V4 source
  fixtures, and reject altered power, source registry, identifiers, and the
  no-human-data boundary. The next gate is the source commit and draft PR; no
  registered v3 run has executed.
- 2026-07-22: Synthetic Experiment v3 source froze as `5743ccb` and draft PR
  #120 opened before the sole run
  `20260722T061958Z_DD-011_5743ccba_19b6517655`. The run passed in 0.874741
  seconds at 33.094 MB with 1,184 assignments, 1,680 power rows, 1,680,000
  seeded draws, complete shared-seed v2 preservation, four independently
  checked Program V4 source fixtures, and four rejected corruptions. All 644 of
  840 sub-0.80 large-sample calibration rows are retained. DD-C-0088 passed its
  separate audit. The active gate is full repository/site acceptance, evidence
  commit, PR CI/merge, post-merge CI/Pages, issue closure, and live routes; the
  run must not be repeated.
- 2026-07-22: Synthetic Experiment v3 final local acceptance passed bootstrap,
  Ruff, MyPy on 133 source files, all 210 tests, the 88-claim ledger, all 47
  manifests, and the 63-page/22-study site. The generated experiment surface
  selects v3, retains all 644 failures, preserves v2 attention and power rows,
  publishes all three schemas, links DD-C-0088 and the immutable run, and keeps
  the no-human-data warning. The next action is the evidence commit and push.
- 2026-07-22: Synthetic Experiment v3 PR #120 passed CI and paper/site artifact
  checks and squash-merged as `0f7a234`, closing issue #119. Post-merge CI
  `29896864562` and Pages `29896864602` passed. The live experiment-kit,
  threshold/dynamic experiment, DD-011, v3 schema, claims, summary, and
  calibration routes returned HTTP 200; the public data confirm the frozen
  counts, all 644 retained failures, and `no_human_data: true`. Milestone V4.6
  is complete. The focused *Threshold Discovery* paper is next.
- 2026-07-22: Threshold Discovery paper issue #122 and branch
  `paper/threshold-discovery` opened from synchronized `main`. The local builder
  checksum-validates seven immutable run families, generates eight evidence
  assets, resolves claims DD-C-0071 through DD-C-0088 and bibliography keys,
  and produces a byte-reproducible 20-page PDF with SHA-256
  `b38bb30f3ce63889526a092d78dd3f202d3beb54178bcdc272aba85c321b1995`.
  Targeted paper/site tests pass, the site emits 64 routes and six papers, and
  all 20 Poppler renders passed visual inspection after correcting a generated
  tau-label escape and improving the run-ID declaration. The all-paper build
  also refreshed stale Program V4 provenance in the unchanged 14-page Three
  Results paper; its deterministic SHA-256 is
  `efd76ae8c7524ebfff6c50ec8b42fb43527a6e47c2ad31cdd3192e0d6935ddfd`, and all
  14 pages passed a new Poppler review. The active gate is full acceptance,
  source commit, PR checks/merge, post-merge CI/Pages, issue closure, and live
  publication/PDF validation.
- 2026-07-22: Threshold Discovery PR #123 passed CI `29900445956` and paper/site
  build `29900445965`, then squash-merged as `ab9cf448`. Post-merge CI
  `29900587931` and Pages `29900587930` passed; the publication, metadata, and
  PDF routes returned HTTP 200, and the live PDF matched SHA-256
  `b38bb30f3ce63889526a092d78dd3f202d3beb54178bcdc272aba85c321b1995`.
  Issue #122 closed. Program V4 Labs issue #124 and branch
  `site/program-v4-output-connected-labs` then opened from synchronized main.
- 2026-07-22: The Program V4 Labs reconstruction replaces the required four
  generic scenarios with exact output selectors over all eight DD-016 phase
  rows, 160 DD-017 games, 64 DD-015 objective rows, and 50 DD-018 mechanism
  rows. Every control selects a distinct registered row, complete static tables
  remain available without JavaScript, and four reduced public JSON datasets
  retain claim/run boundaries. The local site emits 68 routes and 16 Labs.
  Full acceptance passed bootstrap, Ruff, MyPy on 134 source files, all 212
  tests, the 88-claim ledger, all 47 manifests, six papers totaling 89 pages,
  and the site build. Desktop interactions changed substantive exact outputs in
  all four Labs. A 390-by-844 browser check found one labeled control per
  select, a polite live region, one h1/main landmark, a captioned table, no
  document overflow, and no console warnings or errors.
- 2026-07-22: Program V4 Labs PR #125 passed its branch checks and
  squash-merged as `e12d1d2`, closing issue #124. Post-merge CI
  `29902201507` and Pages `29902201604` passed. All four HTML and four data
  routes returned HTTP 200 with their exact immutable run IDs, and deployed
  browser interaction checks passed. Issue #126 and branch
  `docs/program-v4-final-handoff` then opened as a documentation-only gate.
- 2026-07-22: Program V4 final local acceptance passed `make bootstrap`, Ruff,
  MyPy on 134 source files, all 212 tests, the 88-claim ledger, all 47
  manifests, six papers totaling 89 pages, and the 68-page/22-study site. The
  final audit accepted 23 verification and 15 corruption records, accepted the
  valid discovery-event fixture and rejected the invalid fixture, validated 15
  schemas, independently checked the DiscoveryBench v3 24/29/39 registry with
  36 compatible and 660 excluded pairs and no composite score, verified all 22
  public download sizes/checksums, found zero secret candidates and zero public
  host-path leaks across 1,615 tracked files, confirmed five paper provenance
  records and all 47 manifests, and found the MIT-licensed pinned upstream at
  clean `5025cc8`. Every one of 162 deployed public files returned HTTP 200;
  browser checks found one h1/main landmark, no overflow, substantive V4 Lab
  controls, complete no-JavaScript tables, and clean logs. No immutable run was
  repeated.

### Program V3 attention queue (complete, 2026-07-21)

Owner authorization now requires sequential execution of DD-012 Incentive to
Ignore, DD-013 Audience Design and Information Firewalls, DD-014 Conditional
Attention and Contrarian Policies, a focused *Incentive to Ignore* working
paper, DiscoveryBench and synthetic experiment-kit attention extensions, public
Labs/site integration, and a final Program V3 handoff. DD-015 Dynamic Attention
is optional only after the required queue.

The verified start is clean `main`
`99e2098c0f03ec64db274aa7cb04c68e95485223`. Baseline acceptance reproduced 138
tests, 58 claims, 35 manifests of which 32 pass, 15 studies, four validated
papers, and 48 public HTML routes; ten checked Program V2 live routes returned
HTTP 200. No PR was open. The sole pre-existing operational blocker remains
settings issue #32. The one mandated `gh auth status` probe returned no
authenticated host, so settings mutation is not retried and does not block the
research queue.

The registration-only Program V3 baseline completed through issue #79 and PR
#80, squash merge `69ba1c392bb0bda9bc4447c0fac842b8e7308fbf`, passing
post-merge CI and Pages, and live DD-012 through DD-015 routes. DD-012 through
DD-014, the focused paper, DiscoveryBench v2, and the DD-011 synthetic
experiment extension and public Attention/Audience/Conditional Labs are merged,
deployed, and live. Final acceptance proceeds through issue #98 and branch
`docs/program-v3-final-handoff` without duplicating an immutable run.

Progress:

- [x] Program V3 baseline: 19 registered studies, 52 generated routes, 138
  tests, PR #80 merge, post-merge CI/Pages, and all four new live registration
  routes passed.
- [x] DD-012 exact model, theorem/proof audit, rational census, independent
  verifier, reward interventions, claims, public data, and deployment. Model,
  proof, seven-rule registry, exact evaluator, separate direct verifier,
  bounded configuration, primary run
  `20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b`, and DD-C-0059 through
  DD-C-0061, PR #82, post-merge CI/Pages, and live-route checks passed.
- [x] DD-013 binding/voluntary audience frontier, garbling comparison,
  implementable institution, independent verification, claims, and deployment.
  Issue #83 / PR #84 now contain passing run
  `20260721T215811Z_DD-013_09c07448_cdac4fb512`, DD-C-0062 through DD-C-0065,
  the eight-institution registry, Audience Lab, PR #84, post-merge CI/Pages,
  and live routes passed.
- [x] DD-014 conditional policy class, role-profile census, larger-class audit,
  independent verification, claims, and deployment. Issue #85 and branch
  `research/dd014-conditional-attention` contain the frozen class, 75-cell
  exact implementation, independent verifier, four corruption tests, and
  adversarial all-table two-label audit. The source commit, immutable run,
  claim audit, public Lab, merge, and deployment passed. Primary run
  `20260721T222047Z_DD-014_f5f099a8_ea0276dd16` now passes in 10.761 seconds;
  DD-C-0066 through DD-C-0068, PR #87, post-merge CI/Pages, and live routes passed.
- [x] Focused paper, benchmark extension, and synthetic experiment extension.
  PR #90 merged the
  deterministic 20-page paper with nine
  generated evidence assets, PDF SHA-256 `ee9e27f741d2`, and a passing all-page
  Poppler review; post-merge CI/Pages and the live PDF passed. DiscoveryBench
  v2 now passes locally with 20 tasks, 21 protocols, 27 metrics, 28 compatible
  rows, 392 explicit exclusions, v1 regressions, and three corruption gates;
  clean run `20260721T230249Z_DD-010_add85590_56c61a2195`, DD-C-0069, PR #93,
  post-merge CI/Pages, and live public routes passed. DD-011 v2's 29-cell,
  14-hypothesis, 11-scenario package now passes through immutable run
  `20260721T232119Z_DD-011_121162f8_e454b06d2c`, DD-C-0070, PR #95,
  post-merge CI/Pages, and live public routes. No participants were recruited
  and no human data exist.
- [x] Public Labs/site integration. Issue #96 and PR #97 add the
  exact Attention Lab, expand Audience Design across binding and voluntary
  use plus three registered mechanisms, preserve the Conditional Attention
  Lab, and add the required benchmark/experiment navigation. Local acceptance
  passes 182 tests, a 59-route site build, public-safety gates, desktop and
  375-pixel browser interaction, keyboard focus, contained table overflow,
  reduced motion, and clean browser logs. PR #97, post-merge CI `29878042468`,
  Pages `29878042571`, and all required live routes passed.
- [x] Final local acceptance. Issue #98 runs `make bootstrap`, `make verify`,
  `make papers`, and `make site`; 183 tests, 70 claims, all 40 manifests, five
  papers/69 rendered pages, 19 downloads, focused certificate/corruption/schema
  checks, secret/host/license/provenance scans, clean upstream, browser checks,
  and live routes pass. The final documentation PR, post-merge CI/Pages, and
  closing live verification are the only remaining transaction gates.

Recovery: inspect `git status --short --branch` on
`docs/program-v3-final-handoff`, rerun `make verify && make papers && make site`,
then continue issue #98's PR/deployment gates without altering any immutable
run. After merge, resume from clean `main` and `docs/current-roadmap.md`.

### Program V2 completion queue (complete, 2026-07-21)

Owner authorization now requires sequential completion of DD-010 DiscoveryBench,
DD-011 Experimental Design and Power, the DD-008B Common-Source analytic gate,
a focused *Common-Source Trap* working paper, public benchmark/experiment Labs,
and a final Program V2 handoff. The live baseline is clean `main`
`d478a175aa3326a3be1efc1b50b9542e5e1c2011`; CI `29864943433` and Pages
`29864943468` passed, all DD-010, DD-011, DD-008B, and Common-Source Trap
public routes return HTTP 200, and no pull request is open. The only settings blocker remains issue #32; the previously required
single `gh auth status` probe was already exhausted and is not repeated.

The final Program V2 acceptance and handoff milestone under issue #77
and branch `docs/program-v2-final-handoff`. It runs the bounded repository,
certificate, corruption, leakage, schema, synthetic-design, paper, site, scan,
provenance, upstream, and live-route gates, then reconciles every authoritative
documentation surface. It makes no new scientific claim or immutable run.

Progress:

- [x] DD-010 issue, registration, schema, capability boundary, golden tasks,
  protocols, metrics, CLI, exact run, verifier, claim audit, site, merge, CI,
  Pages, and live routes. Primary run
  `20260721T183014Z_DD-010_ce930050_8ec718c242` and DD-C-0055 passed; PR #68
  squash-merged as `62d4cd1c`, post-merge CI/Pages passed, and issue #67 closed.
- [x] DD-011 issue, bounded design, literature record, hypotheses/estimands,
  randomization, synthetic power run, verifier, materials, ethics boundary,
  and site. Primary run `20260721T185647Z_DD-011_fa0271d9_fcaa647c55` and
  DD-C-0056 pass; PR #70 squash-merged as `9caf0f97`, post-merge CI/Pages
  passed, all eight live experiment routes returned HTTP 200, and issue #69
  closed.
- [x] DD-008B analytic gate: general finite-N private-threshold monotonicity and
  equilibrium-count theorem, exact all-common trap width `p(1-p)/N`, and an
  exact N=3 interior over-acquisition counterexample. Primary run
  `20260721T192412Z_DD-008B_649deb08_29dbeaf3a9`; DD-C-0057/DD-C-0058 pass
  through PR #72 squash merge `24252c89`; post-merge CI/Pages passed, live
  routes returned HTTP 200, and issue #71 closed.
- [x] Focused Common-Source Trap paper with source-generated figures/tables,
  deterministic 20-page PDF, citation audit, all-page Poppler review, PR #74
  squash merge `ee0027f6`, post-merge CI/Pages, and live publication/PDF checks.
- [x] Program V2 site/Lab integration through PR #76 squash merge `d478a175`,
  post-merge CI `29864943433`, Pages `29864943468`, 15 required live route
  checks, and a 15-artifact download checksum manifest. Issue #75 is closed.
- [ ] Final Program V2 acceptance and documentation reconciliation are complete
  locally on issue #77 / PR #78; merge, post-merge CI/Pages, and final live
  handoff verification remain.

Recovery: inspect `git status --short --branch`; resume final reconciliation from
`docs/current-state.md`; never rerun the preserved DD-010, DD-011, or DD-008B
primary runs. The exact next command is `make bootstrap && make verify`.

### Program V2 baseline (historical, 2026-07-21)

DD-008A is merged and deployed through PR #61. Clean primary run
`20260721T163030Z_DD-008A_8b70668b_06307caab4` evaluates the registered
N=2 through 8 rational grid with exact binomial accounting and a direct
target/source-signal enumerator. DD-C-0052 is independently reproduced. Local
acceptance passed and its post-merge CI/Pages gates completed.

DD-006B primary run `20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b` exhausts
60 normalized joint-mechanism rows and 57,600 exact joint deviations. It finds
16 strict rows, maximum all-tie margin `13/72`, truthful differentiated
discovery `11/12`, and no weak target-visible/action-hidden row. A separate
exact evaluator reproduces incentive and accounting certificates. Local
integration passed through PR #63, post-merge CI, Pages, and live route checks.

DD-006B merged and deployed through PR #63 as `c4524e7e`. DD-009 primary run
`20260721T171249Z_DD-009_bc78d249_0c3851c41a` classifies all 288 Cartesian
cells, evaluates 20 coherent architectures, independently reproduces every row,
and yields 12 nondominated cells under the declared six objectives. DD-C-0054
is independently reproduced. DD-009 merged and deployed through PR #65 as
`fc273e94`; post-merge CI `29852583292`, Pages `29852583377`, and all Atlas
route checks passed.

Program V1 is complete through DD-008. The authoritative concise entry points
are `docs/current-state.md` and `docs/current-roadmap.md`. Reconciliation at
`ae8b52c098d358afc63948b7a54d2245cafd7438` found 51 claims (24 independently
reproduced, 13 verified, 7 derived, 3 checked, 3 sourced, 1 proposed), 21
passing immutable runs among 24 manifests, 68 Python sources, 26 public HTML
routes, 15 public data files, six Labs routes, three project-authored papers,
and 111 tests. CI and Pages succeeded and public root, Labs, and publications
returned HTTP 200. DD-007 is synthetic-only; issue #32 remains settings-only.

The active sequence is: DD-008A N-agent endogenous evidence acquisition,
DD-006B joint truthful discovery mechanisms, DD-009 bounded Architecture Atlas,
DD-010 DiscoveryBench, DD-011 synthetic experimental design, then a focused
paper and deeper public labs. No real-data work, external model calls,
recruitment, or intervention is authorized. Milestone A is documentation and
registration only; it must not create timestamped research runs.

### Institutional-theory continuation (current, 2026-07-21)

**Completed continuation addendum (2026-07-21).** T is merged through PR #47;
U/DD-006A through PR #49; V/DD-008 through PR #51; W, the validated
*Institutions for Distributed Discovery* synthesis, through PR #54; and X, the
public Labs surface, through PR #56. `main` is
`401258f245ea50fcda5be2c61f78603b3c71e2de`. The current program has 51 claims,
21 passing immutable runs among 24 manifests, three project-authored papers,
and 26 generated public HTML routes. DD-006A is restricted to its registered
normalized linear transfer class; DD-007 remains synthetic-only; DD-008 is an
exact synthetic source-choice fixture. Pages deployment and route validation are
the final operational checks for this addendum; issue #32 remains settings-only.

`main` is `29c37e347a4cbc74a84cd3a23e4105789f7309e9` after PR #45. The prior
N–S queue is complete: research-library PR #36, DD-004 PR #38, DD-005 PR #40,
DD-006 PR #42, DD-007 PR #43, and integration PR #45 are merged. The live
ledger has 49 claims (23 independently reproduced, 12 verified, 7 derived, 3
checked, 3 sourced, and 1 proposed), 21 manifests of which 19 are passing,
60 Python source files, 19 public HTML routes, 13 generated data files, and
two project-authored papers. DD-007 remains synthetic-only. Settings issue #32
remains operational-only because the one required `gh auth status` check found
no authenticated CLI session; no settings mutation is authorized in this state.

The completed sequence was T handoff reconciliation (issue #46), U DD-006A general
transfer frontier, V DD-008 endogenous evidence acquisition, W Discovery Stack
synthesis paper, X interactive labs, then the institutional-program handoff.
Each research milestone requires a bounded registration, immutable evidence,
independent verification, calibrated claims, CI, merge, and Pages validation.

### Historical state

The historical M0–M9 bootstrap, operational Milestone A, research milestones DD-001A/B, bounded DD-002/DD-003, their integrated handoff, and continuation cycles F–M are complete. PR #34 merged as `a3b1f760ff6b4d3d580696e537e5d3f45caf1ed3`; its source checkout is clean on `main`. Claims stop at DD-C-0044; the ledger has 44 claims and 17 immutable manifests. The one authorized settings attempt failed before mutation because GitHub CLI is unauthenticated and is recorded in issue #32. The start-of-phase `gh auth status` check on 2026-07-20 again found no usable CLI session; no settings mutation or retry is authorized.

**Active program phase — research library and bounded extensions.** The next sequence is: (N) build and deploy the public research library; (O) execute/verify DD-004 sequential perfect-elimination baseline; (P) execute/verify DD-005 overlapping-coverage frontiers; (Q) execute/verify a newly registered DD-006 reporting-and-reward fixture; (R) execute/verify DD-007 synthetic audit schema, recovery grid, and identification counterexamples; and (S) integrate the resulting program materials. Each phase requires a bounded issue, coherent branch/PR, immutable evidence, independent check where applicable, claim audit, CI, merge, Pages deployment, and live-route validation.

N completed through merged PR #36 (`1b6f923`) and a successful Pages deployment. O primary run `20260721T050038Z_DD-004_8ab02e7f_71d84de7c4` completed in 0.06 seconds under its 30-second bound: its exact DP and independent tiny policy-path enumerator agree, and terminal discovery is schedule-invariant in the registered perfect-elimination fixtures while expected actions/rounds differ.

## Scope

Completed M0–M9 and A–E evidence, followed by F exact canonical pooled-frontier certificate; G separate Three Results synthesis paper and public Results page; H alignment-preserving DD-001 upper relaxation; I DD-002 equilibrium-selection robustness; J DD-003 heterogeneous source accuracy; K dependency maintenance; L one repository-settings attempt; and M final integration and handoff. Active scope is N–S: research-library site overhaul; exact bounded DD-004 through DD-006 studies; synthetic-only DD-007 audit research; and program integration. Canonical upstream remains read-only.

## Non-goals

Changing canonical upstream, publishing a release or DOI, adding telemetry, making real-organization claims from DD-007 synthetic data, asserting novelty before literature review, or presenting exploratory computations as verified. Public source and Pages deployment are explicitly authorized.

## Assumptions

- Canonical upstream is fetched only into `.cache/upstream/` and pinned before use.
- Python 3.11+ and `uv` provide the primary reproducible environment.
- Missing external credentials or paper toolchains are documented, not bypassed.

## Milestones

- M0 bootstrap: completed 2026-07-20.
- M1 pin and reproduce canonical upstream: completed 2026-07-20.
- M2 formalize foundations: completed 2026-07-20.
- M3 additive paper extensions: completed 2026-07-20.
- M4 private companion site: completed 2026-07-20.
- M5 foundations note: completed 2026-07-20.
- M6 DD-001 initial research: completed 2026-07-20.
- M7 later-study briefs: completed 2026-07-20.
- M8 GitHub organization: completed 2026-07-20.
- M9 integration and handoff: completed 2026-07-20.
- A public/MIT/Pages/GitHub cleanup: completed 2026-07-20.
- B DD-001A policy-signature reduction and certification barrier: completed 2026-07-20.
- C DD-001B two-agent hybrid thresholds: completed 2026-07-20.
- D DD-002 bounded disclosure fixture: completed 2026-07-20.
- E DD-003 bounded source-graph fixture: completed 2026-07-20.
- Integrated A–E handoff: completed 2026-07-20 through PR #17.
- F exact canonical pooled-frontier certificate: completed 2026-07-20 through PR #19.
- G Three Results synthesis paper and public Results page: completed 2026-07-20 through PR #21.
- H alignment-preserving DD-001 upper relaxation: completed 2026-07-20 through PR #23.
- I DD-002 equilibrium-selection robustness: completed 2026-07-20 through PR #25.
- J DD-003 heterogeneous source accuracy: completed 2026-07-20 through PR #27.
- K dependency and Dependabot maintenance: completed 2026-07-20 through PRs #29–#31.
- L single repository-settings attempt: completed 2026-07-20; blocked outcome recorded in issue #32 without retry.
- M continuation integration and handoff: local acceptance complete; documentation PR integration active.

## Progress checklist

- [x] Inspected filesystem and Git state.
- [x] Created safe working branch.
- [x] Completed and validated M0 architecture, policies, skills, package, schemas, templates, and registry.
- [x] Committed M0 as `32dd1c3`.
- [x] Pinned and inspected canonical upstream commit `5025cc8e`.
- [x] Executed the actual upstream verifier with an immutable passing run.
- [x] Independently reproduced blind, private, private-distinct, consensus, planner, and recovery-budget quantities.
- [x] Committed M1 as `dd7f0c6`.
- [x] Formalized the general object, architecture, frontier/loss identity, quantities, institutional matrix, canonical mapping, and pipeline.
- [x] Completed an orientation literature/terminology review with verified metadata and recorded novelty risks.
- [x] Committed M2 as `e1192de`.
- [x] Prepared an additive upstream paper extension, review patch, generator/validator, compiled preview, and visual QA record.
- [x] Built and validated the private companion site extension from generated benchmark and registry data.
- [x] Built and visually validated the 12-page foundations companion note.
- [x] Specified, implemented, executed, independently checked, and reported the initial DD-001 study.
- [x] Upgrade DD-002 through DD-007 into serious executable research briefs without starting the studies.
- [x] Prepare complete local GitHub taxonomy, templates, initial issue drafts, and a guarded setup helper without publishing.
- [x] Run the full acceptance sequence and produce a fresh-checkout handoff.
- [x] Inspect live public repository, Actions, Pages, labels, milestones, issues, PRs, and rulesets.
- [x] Create cleanup issue #6 and branch `chore/public-mit-pages-cleanup` from current `main`.
- [x] Reconcile MIT licensing and current public/Pages wording.
- [x] Create all five prepared live issues; record the settings-capability blocker for labels, milestones, homepage, and safe `main` protection.
- [x] Merge cleanup PR #12 after passing CI and verify live Pages workflow `29781940577` plus all five routes.
- [x] Prove the lossless signature objective identity and exact residual Hall feasibility theorem.
- [x] Implement independent matching/reference and closed-form/scaled signature evaluators with reconstruction and corruption tests.
- [x] Run the bounded DD-001A primary audit; reproduce all 21 tiny optima and raw tie counts; certify the canonical signature state-space counts.
- [x] Add DD-C-0023 through DD-C-0025 with proof/check records and calibrated evidence statuses.
- [x] Merge DD-001A PR #13 after CI and verify Pages run `29784048496`.
- [x] Derive the exact territorial/hybrid/direct threshold theorem for every M at least 3 within the declared families.
- [x] Certify the continuous unrestricted informative envelope for M=3,4,5 across 438,734 exact signature polynomials.
- [x] Reproduce all four known witnesses and refute the unrestricted all-p extension with exact anti-informative counterexamples.
- [x] Merge DD-001B PR #14 after CI and verify live Pages.
- [x] Execute and independently verify the bounded DD-002 deterministic-disclosure fixture.
- [x] Merge DD-002 PR #15 after CI and verify live Pages.
- [x] Execute and independently verify DD-003 on issue #10 and branch `research/dd003-source-graphs`.
- [x] Merge DD-003 PR #16 after CI and verify live Pages.
- [x] Complete broad final acceptance without creating duplicate immutable runs.
- [x] Merge documentation-only integrated handoff PR #17 after CI and verify final Pages.
- [x] Certify the exact canonical pooled frontier for budgets 1–8 by independent labeled-count and histogram/orbit evaluators, probability-mass checks, and corruption testing.
- [x] Replace the numerical DD-001 planner benchmark with an exact certified endpoint while preserving the unresolved private-team optimum.
- [x] Build and visually audit a separate 12–20 page Three Results paper and add a fifth public Results route with generated provenance.
- [x] Implement and audit an alignment-preserving DD-001 upper relaxation; its canonical upper bound equals the direct lower bound and closes the frozen zero-communication optimum.
- [x] Audit the DD-002 witness and all 45 refinements under six declared equilibrium-selection procedures; merged and deployed through PR #25.
- [x] Enumerate the bounded DD-003 colored-source class for a rational heterogeneous-accuracy palette, independently verify its exact counterexample, and merge/deploy PR #27.
- [x] Reconcile Dependabot PRs #1–#5 in separate Actions, low-risk Python, and mypy-2 maintenance branches; update grouping policy.
- [x] Make exactly one settings-capable attempt for repository taxonomy/homepage/protection and record the precise capability result in issue #32.
- [x] Complete broad continuation acceptance without creating duplicate immutable research runs; 95 tests, 44 claims, 17 manifests, both papers, the site, and eleven live routes pass.
- [ ] Review, merge, and deploy the documentation-only Cycle M handoff PR; close issue #33.
- [x] Verify that PR #34 merged as `a3b1f76` and record the unchanged settings-auth blocker without retry.
- [x] Register issue #35 and build the N research-library source, public metadata contract, route registry, safe evidence/download indexes, automated checks, and bounded browser validation on `site/research-library`.

## Discoveries and surprises

- 2026-07-20: host `python3` is 3.9.6; `uv` is available. The project will declare Python >=3.11 and use the locked `uv` environment.
- 2026-07-20: no LaTeX executable was found during the initial inspection; paper validation may require a lightweight fallback or a documented toolchain blocker.
- 2026-07-20: the skill validator failed under host Python because PyYAML was absent, then passed for all four skills under `uv run`.
- 2026-07-20: initial claim validation exposed PyYAML's implicit conversion of unquoted ISO dates to `date` objects; claim dates are now quoted at the serialization boundary. Initial mypy also required the package `py.typed` marker. Both failures were retained here and corrected before commit.
- 2026-07-20: the first M1 execution attempt failed before research computation because Hatchling's editable `.pth` lacked a terminating newline and was ignored by this Python installation. The Make interface now consistently uses `uv --no-editable`; this installs the locked wheel and restores imports without mutating generated environment files.
- 2026-07-20: two upstream verifier executions completed successfully but their wrappers failed after validation while invoking `python -m pip freeze` in a minimal `uv` environment. The source fix did not reach the second run because the non-editable local wheel was stale. Both operational failures are preserved and excluded from claim evidence. Make now places `src/` first on `PYTHONPATH`, while still using locked non-editable dependencies, so research runners always execute current tracked source.
- 2026-07-20: the canonical upstream is MIT-licensed and its current `main` commit is `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`. The verifier, LaTeX paper, bibliography, static site, data, and figures are all present; upstream remains read-only in ignored cache.
- 2026-07-20: evidence run `20260720T190336Z_DD-000_32dd1c32_217c602fa0` passed every upstream assertion, all rounded sanity checks, and independent consensus/planner/private/blind checks. The upstream market and crossover remain verified but not independently reproduced.
- 2026-07-20: “Distributed Discovery” has material terminology collisions, including arXiv:2603.14312 (March 2026) and older resource/service/news-discovery uses. DD-C-0017 records the negative novelty result. Project text now uses an explicit working definition and makes no unique-field/name claim.
- 2026-07-20: team theory directly anticipates DD-001’s decentralized common-payoff policy object; Bayesian persuasion and informational Braess work directly neighbor DD-002. This changes claim calibration, not the registered research questions.
- 2026-07-20: Homebrew supplied Tectonic 0.16.9 after no LaTeX compiler was present. A first compile from repository root failed because Tectonic resolved the upstream `figures/` path relative to the manuscript; a second failed because the requested output directory did not yet exist. Both were operational validation failures. The validator now stages figures only in a disposable worktree, creates its output directory, and leaves canonical upstream clean.
- 2026-07-20: setting `SOURCE_DATE_EPOCH` to the pinned upstream commit timestamp made two consecutive patched-paper builds byte-identical (`0a43360e...`). Full-page rendering and targeted visual inspection found no defects in the additive material.
- 2026-07-20: the pinned upstream guide is a single dependency-free HTML document under MIT license. M4 therefore uses static HTML/CSS, mirrors its typography and color roles, and keeps the canonical public guide as the first link rather than copying or redesigning the interactive sequence.
- 2026-07-20: the first M5 compile exposed an `amsthm`/font-package order conflict, resolved by matching the validated upstream order. The first complete manuscript was 10 pages; substantive additions on feasible protocol classes, admissible comparisons, evidence discipline, and audit design brought it to the requested 12-page minimum without filler.
- 2026-07-20: the paper-specific bibliography omits the canonical entry's long repository URL and abbreviates its pinned commit in print because plainnat produced poor line breaks. The source bibliography and generated provenance retain the full authoritative metadata.
- 2026-07-20: DD-001 agent symmetry reduces exhaustive profiles from `(M^M)^N` to multisets `C(M^M+N-1,N)`. The largest configured search is 32,896 profiles per accuracy; the canonical space remains intentionally unenumerated.
- 2026-07-20: an initial 17-point exact grid was expanded after a bounded audit found informative `N<M` hybrid gains. Three passing runs are preserved; `20260720T200447Z_DD-001_6eb12861_ba766d1eba` is primary because it contains the final 21 points and generated phase figure.
- 2026-07-20: direct clue-following is not generally private-team optimal. At `(M,N,p)=(3,2,2/5)`, exhaustive rational enumeration gives `7/10` versus direct `16/25`. By contrast, 18 canonical coordinate-ascent starts all end at direct value `325089/390625`; this is a lower-bound search observation, not proof of global optimality.
- 2026-07-20: DD-002 through DD-007 can each begin with a bounded exact or seeded synthetic experiment. The briefs make equilibrium selection, latent-source provenance, stopping objectives, overlap assumptions, mechanism observability, and empirical identification explicit before implementation.
- 2026-07-20: the M9 security scan found a local checkout URL in three DD-001 `uv pip freeze` snapshots. The local-project line was redundant with the committed source/lock and was removed; future snapshots filter it. No credential- or token-shaped secret was found.
- 2026-07-20: the clean M8 acceptance run `20260720T202314Z_DD-000_88613408_217c602fa0` passed the pinned verifier and all independent checks. The rebuilt foundations PDF is 12 pages; the additive patched preview is 30 pages and still applies to pristine upstream.
- 2026-07-20: the final staged whitespace audit flagged CRLF endings in upstream-generated CSV evidence as trailing whitespace. Those bytes are covered by the run's output hashes, so the immutable CSVs were preserved and the authored-file whitespace audit was run with that generated output directory excluded.
- 2026-07-20: live `main` advanced to `21bbd5d` with an owner-authored Pages workflow. Run `29779923504` passed, and all five required Pages routes returned HTTP 200. The repository had only 12 default/Dependabot labels, no milestones, no research issues, no rulesets, and five open Dependabot PRs.
- 2026-07-20: GitHub CLI 2.96.0 was installed, but no CLI OAuth session exists. The connected GitHub app has owner/admin access and can manage issues/PRs; SSH handles Git. CLI-only settings will use an authenticated browser or record a capability-specific blocker.
- 2026-07-20: all five prepared issue drafts were applied without duplicates: DD-002 #7, queued DD-007 #8, DD-001A #9, DD-003 #10, and DD-001B #11. Their intended taxonomy is retained in each issue body until settings-capable authentication can create the declared labels and milestones.
- 2026-07-20: `make bootstrap`, `make verify`, `make site`, and `make papers` pass on the cleanup branch; 29 tests, 7 run manifests, 4 site pages, and the 12-page foundations artifact validate. A later post-commit rebuild exposed that the paper's timestamp depended on `HEAD`; this is superseded by the immutable-run epoch fix below.
- 2026-07-20: cleanup PR #12's first artifact run `29781538938` failed after Tectonic installed successfully because Ubuntu lacked the paper validator's `pdfinfo` executable. The artifact workflow now installs `poppler-utils`; the failed run remains linked evidence and is not represented as passing.
- 2026-07-20: the foundations builder formerly derived `SOURCE_DATE_EPOCH` from `HEAD`, so every commit changed the tracked PDF and made the next build dirty. It now uses the immutable passing canonical run's timezone-qualified `started_utc`, records that epoch in generated provenance and validation, tests the conversion independently of Git history, and normalizes Tectonic's parallel `Writing` log lines.
- 2026-07-20: preliminary DD-001A run `20260720T220911Z_DD-001_6822d4c6_40bf5b06a5` passed the computational reduction audit, but claim review found its `certified_interval` output key too strong for the evidence packaged in that run: the pooled endpoint was numerical and the emulation chain was not audited as part of the certificate. The run remains immutable and valid as a preliminary audit; presentation was corrected before the primary run. The later exact-frontier run and DD-C-0019 re-audit separately establish the interval.
- 2026-07-20: primary DD-001A run `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5` started from clean commit `b1d8d431` and passed in 13.73 seconds. It independently reproduced all 21 exact tiny optima and raw-policy multiset tie counts, matched matching/reference and closed-form feasibility through M=5, reconstructed all audited signatures, and passed the independent structural certificate verifier.
- 2026-07-20: the signature theorem reduces each policy losslessly to targetwise incoming counts and fixed-point indicators. At canonical M=16, exact counts are 148,348,284,928 feasible labeled signatures and 5,806 individual target orbits, but independently quotienting agents loses relative target alignment. The eight-agent multiset count before a global target quotient has 85 digits, so the declared naive enumeration exceeds its resource budget. This is not a private-team objective upper bound.
- 2026-07-20: DD-001B primary run `20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1` passed in 35.86 seconds. It proves the exact three-family thresholds \(1/M\) and \(1/(M-1)\), exhaustively certifies the unrestricted continuous informative envelope for M=3,4,5, and records p=0 counterexamples that refute an all-p extension.
- 2026-07-20: DD-002 primary run `20260720T225848Z_DD-002_94607423_e29b1460ae` enumerated all 15 deterministic disclosure policies, 37 posterior games, 256 global pure-equilibrium selections, and 45 strict refinement pairs. Exactly one refinement lowers the declared anonymous-symmetric selection, while every pure equilibrium and the planner improve for that witness; the reversal is selection-dependent.
- 2026-07-20: DD-003 primary run `20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1` enumerated 51 nonisomorphic source graphs, independently reproducing the 1/8/42 orbit counts. Ten full pairwise-moment signatures each match two graphs with identical discovery, a complete bounded null. Mean agreement alone is insufficient: two graphs match at 3/4 but have discovery 8/9 and 31/36.
- 2026-07-20: DD-003 PR #16 passed CI `29787235590` and artifact run `29787235603`, then squash-merged as `54b8713fa7f3b30922a88b60a6dc280319432715`. Post-merge CI `29787309515` and Pages `29787309537` passed; the deployed DD-002/DD-003 completion statuses and all five routes were verified live.
- 2026-07-20: integrated handoff PR #17 passed validation and squash-merged as `b72c01026be5bf7018b3a3e9a464671dce53bcbb`. Post-merge CI `29787687400` and Pages `29787687403` passed. The next program begins from this clean public baseline.
- 2026-07-20: the continuation audit found that DD-C-0006's planner frontier is independently enumerated but stored as decimals. Cycle F therefore requires exact rational artifacts and agreement between a labeled count-vector evaluator over all `C(23,15)=490314` vectors and a separately derived false-count-histogram/orbit evaluator before the exact endpoint can support the private-team interval.
- 2026-07-21: primary exact-frontier run `20260721T012208Z_DD-000_8e4b55e2_e8321d1048` started clean at commit `8e4b55e2`, completed in 8.29 seconds under a 30-second budget, and passed. The 490,314-state labeled evaluator, 67-orbit histogram evaluator, and third partition verifier agree at all budgets with exact unit mass; the verifier rejects a one-unit numerator corruption.
- 2026-07-21: re-audit of the pooled emulation chain establishes the exact valid interval `325089/390625 <= T_8(16,1/5) <= 860391662035297/1001129150390625`, gap `27224111644672/1001129150390625`. The upper endpoint remains unattained and global tightness remains unresolved.
- 2026-07-21: the first ad hoc targeted pytest invocation omitted the Makefile's `PYTHONPATH=src` and stopped during import collection. The identical targeted set passed 12 tests after using the repository execution environment; the immutable primary run and its evidence were unaffected.
- 2026-07-21: exact-frontier PR #19 passed CI `29793343243` and artifact build `29793343234`, received a complete no-findings review, and squash-merged as `8d63201cb3b6633c873494af2ea21402db8752d6`. Post-merge CI `29793437945` and Pages `29793437954` passed; all four current HTML routes, CSS, and deployed claim data returned HTTP 200 with the exact interval.
- 2026-07-21: the first Results-site build stopped with a missing `csv` import after the builder began reading exact role data. Adding the import fixed the operational error; the final builder checksum-validates four immutable source runs and emits exactly five pages plus `data/results.json`.
- 2026-07-21: the first Three Results compile rejected underscores in a generated monospaced provenance path. Replacing that field with a breakable `\path{}` fixed the source error. The first visual pass then exposed cramped tables, overlapping role labels, and poor long-URL justification; all were revised before the final all-page review.
- 2026-07-21: a layout-only rebuild exposed that the synthesis builder's two PDF comparisons shared TeX auxiliary state. The builder now uses two isolated clean compilation directories, normalizes their paths, retains failing logs, and certifies the final 12-page PDF byte-for-byte at SHA-256 `38128dbbb1f531b8ad95151c0ccd4f00b54c04eb8afa1c11ca73f24e5c26b92f`.
- 2026-07-21: targeted tests initially exercised a stale non-editable local wheel, and the first repository-wide lint/typecheck attempts found one unformatted test and an overly broad inferred provenance value type. Reinstalling the local wheel for the targeted check, formatting, and binding the source epoch as a string resolved these operational failures. Final acceptance passes 72 tests, strict mypy, Ruff, claim/run validation, both 12-page papers, and the five-page site.
- 2026-07-21: PR #21 artifact run `29794725150` compiled both clean Three Results PDFs on Ubuntu but failed because the builder also required identical compiler logs. The first clean Tectonic invocation can populate its package cache, so log equality is environment-state equality rather than artifact determinism. The gate now requires identical PDF bytes, validates both logs separately for fatal/reference/citation/overfull failures, stores the second warm-cache log, and records normalized log equality as diagnostic metadata.
- 2026-07-21: Three Results PR #21 passed CI `29794931024` and paper/site build `29794931026`, received complete no-findings review `4740643312`, and squash-merged as `007dc15b89f6d7e98e572d1b164f057c7c38c964`. Post-merge CI `29795041418` and Pages `29795041429` passed; all five pages and result provenance returned HTTP 200 with exact deployed values.
- 2026-07-21: alignment-bound run `20260721T022739Z_DD-001_358cb1eb_cd16846ba5` started clean at commit `358cb1eb`, completed in 0.39 seconds, and passed all 21 tiny fixtures plus two anti-informative checks. Its separate verifier checks every Bellman inequality/equality witness without optimizing and rejects a zeroed final value. The canonical upper bound `325089/390625` meets direct clue-following, proving the deterministic and ex-ante randomized optima (DD-C-0037/DD-C-0038); the relaxation is not universally tight because the `M=3,N=2,p=0` case has upper `1` versus exact `11/12`.
- 2026-07-21: PR #23 passed CI `29796343151` and paper/site build `29796343110`, received complete no-findings review `4740754564`, and squash-merged as `df35f80273f106ef86f623c4676fe2a58757b6ad`. Post-merge CI `29796429926` and Pages `29796429904` passed. The first live smoke-test shell used `path` as a zsh loop variable, overwriting zsh's special command-search array and making `curl`, `rg`, and `jq` temporarily unavailable inside that process; rerunning with variable `route` returned HTTP 200 for all seven routes and verified the exact deployed value and alignment run ID.
- 2026-07-21: DD-002 selection run `20260721T025802Z_DD-002_73a85c71_b0e5b6dc49` passed 15 policies, 37 posterior games, 256 pure selections, 45 refinements, 333 profile states, 1,998 potential/deviation checks, 333 Bellman states, and 270 rule comparisons in 0.089 seconds. An independent verifier reproduces the games, potential identities, and absorption equations and rejects a corrupted absorption probability. The known `P00` to `P03` reversal survives only anonymous-symmetric selection; best pure, worst pure, uniform potential maximum, uniform strict-best-response basin, and planner all improve from `2/3` to `3/4`. Across all refinements their harmful counts are `1,0,8,2,2,0` (DD-C-0039--DD-C-0041).
- 2026-07-21: the first targeted public-integration pytest was deliberately invoked before regenerating the paper artifacts and therefore detected stale provenance; after `make three-results`, all targeted paper/site tests passed. The rebuilt 13-page synthesis PDF is byte-reproducible at SHA-256 `1489d0e2aa3a4dc65b38e1731becaf71dbeb946f3670d09e396a79639415a592`, and all 13 Poppler renders passed visual review.
- 2026-07-21: PR #25 passed CI `29797737821` and paper/site build `29797737785`, received complete no-findings review `4740900193`, and squash-merged as `993b0899421d446f61348a513d2630e0f424e336`. Post-merge CI `29797810807` and Pages `29797810786` passed; all seven routes returned HTTP 200 and the deployed six-rule counts/run provenance match the immutable source.
- 2026-07-21: DD-003 heterogeneous run `20260721T032358Z_DD-003_84238b76_2cbc13e66a` passed in 78.23 seconds under 120 seconds and 512 MB. Primary canonicalization and independent adjacent-swap traversal agree on 41,612 base labeled objects/671 orbits and 12,966 expansion labeled objects/168 orbits. Across 839 networks, 163 complete-moment groups cover 485 networks and 111 groups differ in discovery. The simplest exact colored witness has identical 66-entry first/pairwise moments but discovery `3/4` versus `2/3`, difference `1/12`; an independent verifier reconstructs all entries and rejects a zeroed difference (DD-C-0042--DD-C-0044).
- 2026-07-21: the first post-integration site test caught removal of the established phrase “bounded null, not a theorem.” The wording was restored. The final 14-page synthesis PDF is byte-reproducible at SHA-256 `53cbfa8ccf6f732b13670206f3a8c25627390cbb29206f6b1b017163ae3735bf`, and all 14 Poppler renders passed visual review.
- 2026-07-21: DD-006B primary run `20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b` completed from clean commit `f022a1a5` in 22.55 seconds under the 60-second/1-GB registration. The 60-row exact census and separate evaluator agree on all incentive, discovery, participation, subsidy, ex-post transfer-bound, and liability certificates. Sixteen rows are strict, three use an active positive proper score, maximum all-tie margin is `13/72`, and the target-visible/action-hidden regime has no weak row.
- 2026-07-21: DD-006B integration passed `make verify` with 116 tests and 31 manifests, built a 28-page/11-study site with generated mechanism Lab data, and rebuilt all three papers. The Three Results paper changed only because its generated claim-ledger provenance hash changed; it remains 14 pages, is byte-reproducible at SHA-256 `1ac0700bf2d15a18c58207f2aa45879306f0e09217578ce0de366af2bea0309f`, and all 14 Poppler renders passed visual review.
- 2026-07-21: DD-009 primary run `20260721T171249Z_DD-009_bc78d249_0c3851c41a` completed from clean commit `bc78d249` in 0.20 seconds under the 30-second/512-MB registration. It classifies 288 cells, evaluates 20 coherent architectures, independently reproduces every row, and records 12 nondominated cells. Local integration passes 118 tests, 32 manifests, a 30-page/12-study site, and all three papers. The 14-page Three Results provenance rebuild is byte-reproducible at SHA-256 `d5c4d8e110b82aa34cf1beb3244204d2ad5902c58aaea44a860b40e442dc7b47`; all 14 Poppler renders passed visual review.
- 2026-07-21: DD-009 PR #65 passed all three head checks, squash-merged as `fc273e9401e2f350d436ff6fd6bc5bc3eac93e83`, and closed issue #64. Post-merge CI `29852583292` and Pages `29852583377` passed. The DD-009 study, claim, evidence, study-data, Atlas-data, and Atlas-Lab routes all returned HTTP 200; deployed data reports 20 architectures, 12 nondominated cells, maximum discovery `11/12`, and maximum social net value `5/6`.
- 2026-07-21: heterogeneous-source PR #27 passed CI `29798934183` and paper/site build `29798934209`, received no-findings review `4741011022`, and squash-merged as `4a8f53e90b1ffea233de5b377ba970566d92d670`. Post-merge CI `29798998333` and Pages `29798998329` passed; all seven then-required routes and the exact 839-network data were verified live.
- 2026-07-21: maintenance issue #28 was split by risk class. PR #29 refreshed checkout/setup-uv/Pages actions and Dependabot grouping, PR #30 raised PyYAML/types-jsonschema floors without changing resolved versions, and PR #31 migrated strict checking from mypy 1.20.2 to 2.3.0. All three PRs passed branch and post-merge CI/Pages. Obsolete conflicted Dependabot PRs #1–#5 were closed with replacement links.
- 2026-07-21: mypy 2.3 produced no new diagnostics across 45 source files under either its standard parser or `--native-parser`. Defaults for local partial types and strict bytes required no compatibility override; no global or targeted suppression was added.
- 2026-07-21: the single settings-capable command validated 23 labels, six milestones, and five issue drafts, then failed at its first `gh repo view` with exit status 4. No mutation occurred and no retry was made. Issue #32 records Issues-write, Metadata-read, and Administration-write as the missing authority plus exact resume calls.
- 2026-07-21: final acceptance passed 95 tests, a focused 35-test certificate/provenance audit, strict mypy 2.3, 44 claims, 17 manifests, both papers, the five-page site, secret/license/host-path/upstream checks, all-page Three Results visual QA, and eleven HTTP-200 live routes. A broad local-path regex first stopped on the intentional `file:///private/checkout/...` sanitizer fixture; the host-specific scan then passed. `make upstream-patch` also reordered two parallel Tectonic `Writing` log lines while successfully validating the patch; the incidental log-only change was restored.

## Decision log

- 2026-07-20: use an isolated upstream cache rather than vendoring, subject to ADR-0001.
- 2026-07-20: use `uv`, pytest, Ruff, mypy, PyYAML, and jsonschema, subject to ADR-0002.
- 2026-07-20: project owner explicitly authorizes a public MIT source repository, Actions-built GitHub Pages, GitHub metadata, non-destructive `main` protection, and squash-merging passing queue PRs. Canonical upstream remains read-only.

## Validation strategy

Each milestone runs its targeted Make commands plus schema, unit, integration, and artifact checks. M9 runs `make all`, link/content checks, secret scan, and Git review.

## Commands and expected observations

- `git status --short --branch`, `git remote -v`, `git log`: establish repository condition; observed no commits/remotes.
- `git switch -c codex/bootstrap-distributed-discovery`: create the safe branch; succeeded.
- `uv lock && uv sync --locked`: resolved 21 packages under Python 3.11.15; succeeded.
- Four `quick_validate.py` invocations under `uv run`: all repository skills valid.
- `make bootstrap`: locked environment and 11-file/bootstrap plus valid-claim fixture checks passed.
- `make lint`: Ruff format and lint passed.
- `make typecheck`: strict mypy passed across 11 source files.
- `make test`: 3 tests passed.
- `make validate-claims`: the two-record claim ledger passed JSON Schema validation.
- `make fetch-upstream`: cloned the canonical repository to ignored cache and returned commit `5025cc8e`.
- `uv pip compile ... --no-header --no-annotate`: pinned 11 upstream reproduction packages.
- Three `make reproduce-baseline` executions: the first two exposed and preserved post-validation wrapper failures; the third completed in run `20260720T190336Z_DD-000_32dd1c32_217c602fa0` with validation status `passed`.
- M1 `make lint`, `make typecheck`, `make test`, `make validate-claims`: passed; 10 tests and 3 manifests validated.
- M2 scholarly searches across information ordering/design, team theory, organizational/scientific search, epistemic networks, coverage games, submodularity, robotic redundancy, and terminology collisions; primary/stable records logged in `docs/literature/search-log.md`.
- M2 `make lint`, `make typecheck`, `make test`, `make validate-claims`: passed; 12 tests and 3 manifests validated.
- M3 `make upstream-patch`: patch applied in a disposable worktree and Tectonic 0.16.9 compiled the 30-page preview; two consecutive builds had the same PDF SHA-256. Poppler rendered all pages for visual QA.
- M4 `make site`: built four pages from passing canonical run `20260720T190336Z_DD-000_32dd1c32_217c602fa0` and seven study status/question files. Internal links, semantic landmarks/headings, resolved template data, tracking absence, generated provenance, and primary text contrast checks passed; full repository verification reached 16 tests.
- M5 `make foundations`: generated a canonical table and pooled-frontier figure from validated run artifacts, resolved 15 citation keys and 17 claim IDs, compiled 12 pages with Tectonic 0.16.9, and produced byte-identical PDF SHA-256 `3637f16e...` twice. Poppler rendered all pages; targeted full-resolution review covered data assets, dense lists, and references. Full repository verification reached 18 tests.
- M6 `make dd001`: primary run completed the 21-point exact grid and 18 canonical restarts in 8.4 seconds inside a 120-second budget. Exact formula/direct enumeration, normalization, exhaustive counts, benchmark bounds, seeds, terminations, output hashes, and generated SVG checks passed. Claim-specific audit commands and targeted tests passed; six run manifests now validate.
- DD-001A `make dd001-signatures`: primary run completed the 21-point independent signature grid, feasibility/reconstruction audit, and canonical state-space certificate in 13.73 seconds under a 120-second budget. All validation flags passed; the independent checker accepted the certificate and its corruption test rejects a modified count.
- DD-001B `make dd001-thresholds`: primary run completed the exact restricted-family theorem and bounded unrestricted census in 35.86 seconds; PR #14 and post-merge CI/Pages passed.
- DD-002 `make dd002-disclosure`: primary run completed the entire bounded deterministic-policy lattice in 0.018 seconds. The independent witness verifier, exact posterior/equilibrium checks, planner monotonicity, corruption test, and run manifest validation passed.
- DD-003 `make dd003-source-graphs`: primary run completed the 51-graph exact census in 2.00 seconds. Independent orbit traversal, pairwise nonisomorphism, direct moment/discovery recomputation, bounded-null verification, scalar counterexample verification, and corruption testing passed.
- DD-003 PR/post-merge: required branch workflows passed; issue #10 closed automatically on squash merge; five-route Pages smoke test passed and the live open-problems page contains the independently reproduced DD-003 status.
- Three Results local acceptance: `make verify` passes 72 tests plus strict typing, lint, and 14 immutable run manifests; `make papers` deterministically builds the 12-page Foundations and 12-page Three Results PDFs; `make site` emits five validated pages and four checksum-bound result-source run identifiers. Poppler rendering and all-page inspection validate the synthesis PDF.
- M7 `make verify`: passed after adding six bounded research briefs and linking their next actions into the study registry; no DD-002 through DD-007 experiment was executed and no result claim was added.
- M8 `python scripts/setup_github.py`: validated 23 labels, six milestones, and four nonduplicative initial issue drafts in offline dry-run mode. `make verify` passed 28 tests plus claim and run validation.
- M9 `make all`: formatting, lint, strict typing, 28 unit/integration/regression tests, claim/run validation, a clean canonical reproduction, the 12-page foundations build, and the four-page site build passed. `make upstream-patch`, PDF metadata/render inspection, internal-link/content tests, provenance/hash validation, local-path/token scans, and upstream/Git hygiene checks also passed. A final provenance-sanitizer unit test brought the post-documentation verification total to 29 passing tests; its first format check and a direct audit missing `PYTHONPATH` stopped safely and were corrected before the passing rerun.

## Artifacts produced

M0 produced the instruction system, policies, eight ADRs, four validated workflow skills, complete study registry, claim ledger/schema, package/CLI skeleton, locked environment, Make interface, tests, GitHub templates/workflows, integration boundary, and documentation/result indexes.

M1 produced the upstream lock and source hashes, upstream dependency lock, isolated reproduction wrapper, immutable run artifacts, independent finite-model evaluator, exact-rational/tiny/count-enumeration tests, full-precision regression, manifest validation, baseline report, and baseline claim map DD-C-0003 through DD-C-0015.

M2 produced full foundations/glossary/notation documents, pipeline diagram, canonical/framework mapping, literature search log/evidence map/novelty risks, 15-entry verified bibliography, proposition DD-C-0016 with review, and terminology negative result DD-C-0017.

M3 produced six auditable source fragments, a placement/change memo, a generated review patch against pinned upstream, a patch/apply/compile validator, a deterministic compiled preview with sanitized log and metadata, integration tests, and a visual-QA record.

M4 produced a local four-page static companion, generated canonical/study/claim data, a deterministic builder, semantic/link/content/no-tracking validation, keyboard focus and reduced-motion behavior, responsive light/dark styling, and contrast tests. It was not deployed at the time; the public Pages deployment was added after M9.

M5 produced the 12-page foundations LaTeX note, generated table and figure source with input checksums, paper-specific validated bibliography, claim/citation/source checks, deterministic PDF, sanitized build log, validation record, source tests, and page-level visual-QA record.

M6 produced the frozen zero-communication model; rational factorized and direct evaluators; agent-symmetric exhaustive optimizer; bounded exact coordinate ascent; a guarded 21-point configuration; three immutable passing runs; exact phase data, policies, and SVG; an informative hybrid counterexample; a canonical lower-bound/upper-benchmark record; two proofs; five audited claim records DD-C-0018 through DD-C-0022; a study/global report; and a calibrated working-paper outline.

M7 produced six serious research briefs covering the minimum viable model, canonical relationship, estimands, adjacent literature, methods, falsifiable questions, dependencies, risks, first bounded executable experiment, and completion criteria for DD-002 through DD-007.

M8 produced label and milestone manifests, six issue forms, four substantive initial issue drafts, an evidence-complete pull-request template, a non-destructive setup helper, an application checklist, and integration tests. Nothing was applied to GitHub because the repository has no remote.

M9 produced a clean canonical acceptance run, refreshed generated paper provenance, revalidated both PDFs and the local site, scrubbed redundant private checkout paths from environment snapshots, updated all navigation/status surfaces, and created the comprehensive project handoff.

Milestone A produced the reconciled public/MIT/Pages state, passing PR #12, deterministic paper artifact workflow, five live research issues, and a successful post-merge Pages smoke test. DD-001A produced the lossless signature theorem and exact feasibility proof, independent implementations and tests, two immutable passing runs, primary reduction/certificate artifacts, claims DD-C-0023 through DD-C-0025, a global report, and a working-paper fragment. DD-001B produced exact restricted thresholds, a bounded unrestricted census, and claims DD-C-0026 through DD-C-0028. DD-002 produced the complete bounded deterministic-disclosure registry, independent reversal verifier, exact refinement census, claims DD-C-0029 through DD-C-0031, and an information-design outline. DD-003 produced the complete 51-graph registry, independently reproduced orbit counts and moment/discovery values, a bounded-null certificate, scalar counterexamples, claims DD-C-0032 through DD-C-0034, and an exact SVG figure. Cycle G adds a separate 12-page synthesis paper, three generated figures, a generated evidence-status table, immutable provenance and visual-QA records, a public Results template, checksum-backed result JSON, and exact five-page site validation.

## Blockers

There is no local research, validation, build, CI, Pages, license, provenance, or Git blocker. The sole operational blocker is issue #32: GitHub CLI lacks a settings-capable authenticated session, so the prepared labels, milestones, homepage, and safe `main` ruleset remain unapplied. The connected GitHub app and SSH cover issue/PR and Git transport operations. Do not repeat the settings attempt until the missing authority is intentionally supplied.

## Recovery and restart instructions

Start from `main` with `git switch main && git pull --ff-only origin main && make verify`. For the only operational blocker, authenticate intentionally with `gh auth login` and follow issue #32 plus `docs/github-setup.md`; do not retry blindly. For new research, open a new bounded issue with state-space, time, memory, interruption, and certificate plans before extending DD-001, DD-002, DD-003, or starting DD-004–DD-007. Never rerun a completed primary configuration merely to refresh timestamps.

## Outcome and retrospective

M0–M9, Milestone A, DD-001A/B, bounded DD-002/DD-003, the A–E handoff, and continuation cycles F–L meet their evidence, review, merge, CI, deployment, and live-verification criteria. Cycle M has passed local acceptance and changes documentation only; it is complete when its PR is reviewed, merged, and the final Pages deployment is smoke-tested. The only preserved failure outside completed research is the single settings-authentication blocker in issue #32.
