# DiscoveryBench Agents v1 registration

This living ExecPlan follows `.agent/PLANS.md`. It implements the owner
authorization from clean `main` commit
`62bd4804e6ea5e8621125335c3a4ffc9024a2871`. This gate registers an offline
benchmark instrument. It does not execute an agent evaluation.

## Purpose and intended outcome

Resolve DiscoveryBench Agents v1 ownership and versioning, then freeze a
versioned, auditable, machine-gradable software-agent benchmark instrument
against existing exact Distributed Discovery baselines. The expected but not
predetermined outcome is `register-instrument-under-dd010`: preserve
DiscoveryBench content versions v1/v2/v3, register `agents-v1` as a separate
evaluation-protocol axis under DD-010, allocate no new study or claim, and
leave provider/model evaluation for a separately authorized evidence package.

## Live starting state

The live audit at `2026-07-23T14:24:07Z` found local and remote `main` at
`62bd4804e6ea5e8621125335c3a4ffc9024a2871`, the squash merge of PR #168.
Issue #167 is closed as completed; its closeout and PR record branch CI
`29987290336`, branch paper/site `29987290334`, post-merge CI `29987459607`,
and post-merge Pages `29987459406`, all successful. There is no open pull
request. Settings-only issue #32 is the only open issue and is not a blocker.
GitHub CLI authentication was probed exactly once and is unavailable; issue and
PR actions use the connected GitHub application and Git transport uses SSH.

The scientific baseline is 110 claims through DD-C-0110, 26 registered studies
through DD-022, 51 immutable manifests with 48 passing runs, 159 Python source
files, no DD-023, and no DD-C-0111. DiscoveryBench v1/v2/v3 are owned by
DD-010 and preserve respectively 15/20/24 tasks, 13/21/29 protocols,
19/27/39 metrics, 16/28/36 compatible exact rows, and 179/392/660 explicit
exclusions. V1 is the CLI default; the external adapter is disabled and has no
provider implementation; no composite score exists.

The seven project PDFs total 119 pages and match their accepted hashes:

- Foundations: `8875926a52f0b8e722f7ce827c456c4b694f9e981c21c4b15bf2b3c60b83e76b`
- Three Results: `9eb896353b1210706d6108685dde963e02d6a5ebc64af9f9f69c08c01f5ebc96`
- Discovery Institutions: `78606f732f105d79395409dcb9d7224d72aa1e44312ca30ff5719d049afd98a8`
- Common-Source Trap: `afa9384eca60cf2a0291c2c42012f15ca59bf3d29b7c939b1882a0237ea58ff7`
- Incentive to Ignore: `651c91fb68df6b2f1397ca86f3842b7c2fa9c067601957c32401a7f5e95cd24b`
- Threshold Discovery: `634e96662989a3fd6efb5fc3e6919883897e60511826e25c6d0176bac4af9249`
- Information Sharing Frontier: `a317e8851a84b494d8ef30eccc1e31dd4448dc1bbcd3fb2de0fc2849bd581a13`

The live site has 80 routes, 87 public data files, 18 Labs, 23 checksum-covered
downloads, and five global-navigation items. The paper lifecycle has eight
records with no archived or superseded current paper. The upstream clone is
clean at `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`, and its pinned PDF hash is
`cb4816cb3a9cdd8db0210ab8981e3729028eb02ba174f2a7300b617807cc1e04`.

## Scope

1. Decide scientific ownership and independent version axes.
2. Freeze task-family generators, agent protocol, architectures, prompts,
   capability boundaries, metrics, estimands, and exclusions.
3. Audit current provider/model candidates from dated official sources without
   calling or downloading them.
4. Freeze a no-spend resource envelope and owner-approval boundary.
5. Design automated cryptographic custody with public toy vectors only.
6. Design contamination probes, trace/redaction policy, verification, and 24
   registered corruptions.
7. Add schemas, public fixtures, validators, tests, and a no-network
   deterministic mock path.
8. Integrate registration-safe status into DD-010 and the static site.
9. Validate, merge, deploy, verify live registries and downloads, close the
   issue, and synchronize `main`.

## Non-goals

No provider or model call; model download; credential; cost; private seed;
real or encrypted holdout; real answer key; evaluated agent team; evaluation
trace; benchmark result; scientific claim; immutable evidence run; human or
organizational evidence; provider ranking; composite score; human scoring or
custody; hidden chain-of-thought request; paper or lifecycle edit; Reliable
Discovery; theorem study; ActiveGraph; canonical-upstream mutation; person
contact; submission; release; DOI; or hosted leaderboard.

## Source-of-truth boundary

Git files remain authoritative for task/generator contracts, protocol and
architecture registries, candidate snapshots, prompts, permissions, metrics,
custody commitments, future traces, and future validation. Existing Python and
Make workflows remain authoritative for schema validation, baseline
recomputation, corruption tests, version preservation, site generation, and
acceptance. Provider dashboards are dated observations, not scientific
authority. ActiveGraph and external operational databases are out of scope.

## Fixed owner decisions

- Program: Distributed Discovery; formal object: discovery architecture.
- Information aggregation is not action allocation.
- Lab: AI-powered under human PI ownership and final gate authority.
- Instrument: open, auditable measurement of software-agent teams against
  exact discovery baselines, not a universal intelligence or accuracy test.
- Existing exact results remain authoritative; future agent evidence is a
  distinct stochastic software-agent category.
- Content v1/v2/v3 are immutable; `agents-v1` is not silently called v4.
- Instrument registration and evaluation campaign are separate objects.
- All tasks are machine-graded; no human rater, judge, reviewer, or custodian.
- Public tasks are calibration only; future evaluation uses sealed isomorphic
  post-freeze holdouts.
- At least two genuinely distinct provider/model families and one feasible
  local/open candidate are required for future execution, without claiming
  independence from provider names.
- Results are metric vectors and predeclared contrasts, never one universal
  ranking.

## Milestones

- **M0 (complete):** live Git/GitHub audit, required reading, immutable baseline,
  preservation set, issue, branch, living plan, and first durable checkpoint.
- **M1 (complete):** ownership/versioning decision and ADR.
- **M2 (complete):** registration-decision skeleton and exact outcome vocabulary.
- **M3 (complete):** benchmark-content and generator version freeze.
- **M4 (complete):** five task-family contracts, ownership map, state/prompt-space counts.
- **M5 (complete):** agent protocol, structured output, and information boundary.
- **M6 (complete):** minimal architecture/protocol contrast registry.
- **M7 (complete):** official provider/model candidate audit and snapshot policy.
- **M8 (complete):** state-space, resource, storage, and low/base/high cost envelope.
- **M9 (complete):** cryptographic custody design and public toy test vectors.
- **M10 (complete):** contamination threat model and quarantine/stop policy.
- **M11 (complete):** raw trace, safety, redaction, and no-chain-of-thought policy.
- **M12 (complete):** statistical design and estimands.
- **M13 (complete):** metric and comparator registry.
- **M14 (complete):** independent Method A/Method B verification design.
- **M15 (complete):** 24-case corruption registry.
- **M16 (complete):** schemas, public valid/invalid fixtures, validators, mock dry run, and
  focused tests.
- **M17 (complete):** exact registration decision.
- **M18 (complete):** apply the selected proceed path without claims, runs, or calls.
- **M19 (complete):** registration-safe static-site integration.
- **M20 (complete):** prove all paper and lifecycle invariants unchanged.
- **M21 (active):** full local acceptance, ready PR, CI, squash merge, Pages, live
  acceptance, issue closeout, and synchronized `main`.

Exactly one milestone is active at a time.

## Progress checklist

- [x] Inspect branch, worktrees, remotes, and preservation files.
- [x] Fetch, synchronize `main` with `--ff-only`, and verify the expected SHA.
- [x] Confirm no commits after the expected SHA and no competing PR.
- [x] Inspect issue #167, PR #168, closeout comment, open issues/PRs, and four
  workflow runs.
- [x] Verify scientific, DD-010, paper, lifecycle, upstream, and live-site
  baselines.
- [x] Complete the mandatory repository, Phase 2, DD-010, prospectus,
  scientific-owner, statistical, safety, and provenance reading.
- [x] Record the five-file preservation set without reading or touching it.
- [x] Create the single registration issue, branch, baseline commit, push, and
  draft PR.
- [x] Complete M1 through M20 sequentially.
- [ ] Complete M21 and synchronize `main`.

## Discoveries and surprises

- The expected main SHA, preservation set, open-issue/PR state, workflows,
  inventory, upstream pin, paper hashes/pages, and live route count all match.
- `gh auth status` is unavailable exactly as expected; public GitHub API
  workflow records and the connected application cover the audit.
- The authoritative manifest validator counts 51 manifests across `results/`;
  48 pass, one is a preserved failed run, and two preserve wrapper failures
  after upstream validation.
- Existing DiscoveryBench already separates content versions, capability views,
  exact result vectors, a deterministic mock, and a disabled external-adapter
  boundary. Agents v1 can therefore remain a separate protocol axis without
  mutating v1/v2/v3.
- The official provider audit admits two fixed cloud model identifiers and one
  revision-pinned open candidate for later consideration; it blocks the Google
  reserve until its weaker stable-name and retention boundaries are resolved.
- `make verify` passes strict MyPy over 160 source files and all 274 tests. The
  offline audit validates 15 schemas, five valid and three invalid fixture
  classes, 24 corruptions, and zero execution artifacts.
- `make papers` reproduces the seven accepted hashes and 119 pages. Its normal
  provenance refresh was restored byte-for-byte, leaving the paper tree
  identical to starting main.
- `make site` produces 81 routes, 88 public data files, 18 Labs, and 23
  checksum-covered downloads. Desktop and 390-pixel browser QA find one H1,
  five primary nav items, no horizontal overflow, no forms, no external
  scripts, visible keyboard focus, reduced-motion CSS, and no console warnings
  or errors.

## Decision log

- `2026-07-23T14:24:07Z`: no substantive PR conflict exists; proceed on the
  single requested registration lane.
- `2026-07-23T14:24:07Z`: preserve the five unrelated untracked duplicate files
  without reading, editing, moving, deleting, normalizing, or staging them.
- `2026-07-23T14:24:07Z`: treat public provider documentation as dated
  candidate observations only; no candidate becomes execution-authorized here.
- `2026-07-23T14:24:07Z`: use public toy seeds and test keys only for custody
  conformance; creating any secret/private seed, holdout, or answer key is
  prohibited.
- `2026-07-23T14:26:03Z`: issue #169 owns the sole registration lane; branch
  `benchmark/discoverybench-agents-v1-registration` was created from the exact
  starting main with the preservation set unchanged.
- `2026-07-23T14:27:00Z`: accept DD-010 instrument ownership with independent
  `agents-v1` protocol versioning; reject the v4 label and defer any evaluation
  study ID until a separately authorized evidence campaign.
- `2026-07-23`: complete M3--M20 with decision
  `register-instrument-under-dd010`; allocate no study or claim and preserve
  all v1/v2/v3 outputs.
- `2026-07-23`: recommend but do not authorize a $750 future execution cap;
  low/base/high dated estimates are $3.16/$537.98/$3,418.56.

## Ownership/versioning decision

Accepted: DD-010 owns the registered instrument, with `agents-v1` as a
protocol axis independent of content v1/v2/v3. No study or claim is allocated.
A future evidence campaign receives a separate execution gate and may receive
a study ID only after implementation, snapshots, cost, holdouts, estimands,
and verification are fully authorized and frozen.

## Instrument/evaluation separation

The instrument contains contracts, schemas, exact baselines, evaluator,
custody/contamination/trace policy, conformance fixtures, verification, and
versioning. A future evaluation campaign selects provider/model snapshots,
generates private batches, executes agents, preserves immutable traces,
estimates stochastic contrasts, and promotes claims only after separate
authorization and verification. This gate registers only the instrument.

## Task-family selection

Frozen: common-source acquisition; one-reader versus broadcast attention;
point versus shortlist sharing; consensus collapse versus portfolio recovery;
and threshold-team formation. The registry has 138 canonical generator cells,
552 isomorphic prompts, and 58,945 primitive labeled task states.

## Model/provider audit

Complete from official sources only, with no calls or downloads. OpenAI
`gpt-5.4-2026-03-05` and Anthropic `claude-sonnet-4-6` satisfy the future
fixed-ID candidate gate; revision-pinned Mistral Small 3.1 is the hardware-gated
open candidate. Gemini 2.5 Pro remains blocked pending a stronger immutable
snapshot and retention verification.

## Statistical design

Frozen. The unit is a paired isomorphic task instance; agent outputs are
stochastic estimates, exact baselines remain fractions, and the primary object
is an eight-metric vector with four predeclared paired architecture contrasts,
fixed batches/repeats, conservative missingness, paired cluster-bootstrap
intervals, and Holm correction.

## Cryptographic custody

Registered. Use established cryptographic libraries; publish commitments,
encrypt future holdouts/keys, log access, lock outputs before unsealing, and
release parameters/seeds/answers only after the campaign lock when safe. No
private material is created in this gate; only domain-separated public SHA-256
toy vectors exist.

## Contamination threat model

Registered. Separate direct leakage, probable memorization, ordinary correct
reasoning, and inconclusive overlap. Lexical overlap alone is not proof.

## Trace and safety policy

Registered. Preserve visible messages, declared actions/tools, metadata,
validation, errors, and hashes only. Never request, infer, store, or score
hidden chain of thought.

## State-space/resource/cost audit

Complete. The low/base/high cloud estimates are $3.16/$537.98/$3,418.56 on
2026-07-23 pricing. The recommended future cap is $750 and is not authorized.
Cost authorization and cost incurred remain false.

## Independent verification

Registered. Method B reconstructs primitives, capability rights, exact
baselines, metrics, commitments, hashes, aggregation, and versions without
importing Method A classifications where primitive recomputation is possible.

## Corruption plan

Complete with the required 24 mutations and rejection classes;
execute only schema/registry and public-toy-fixture corruptions.

## Schemas and fixtures

Fifteen schemas, five valid and three invalid public fixture classes, the
offline registry audit, deterministic mock, commitment checks, isolation,
redaction, trace hashing, and focused tests are implemented. No live provider
client or private generator exists.

## Public integration

Complete locally. The static page and JSON publish purpose, versions,
task-family names, exact evidence
boundaries, and the truthful no-call/no-cost/no-holdout/no-result status. Add no
result route, leaderboard, form, endpoint, remote runtime, or sixth nav item.

## Validation strategy

Run `git diff --check`, `make bootstrap`, focused version/registry/task/
capability/mock/custody/contamination/trace/statistics/metric/corruption/site
tests, `make verify`, `make papers`, and `make site`. Compare frozen Git object
IDs for claims, studies, verified results, paper sources, PDFs, and upstream.
Prove v1/v2/v3 output vectors, 24 tasks, 29 protocols, 39 metrics, 36
compatible rows, 660 exclusions, disabled external adapter, prohibited
capabilities, and no composite are unchanged. Scan for credentials, keys,
tokens, host paths, SQLite, private seeds, holdouts, traces, results, claims,
and runs. Perform desktop and 390-pixel local and deployed browser acceptance.

## Commands and expected observations

- `make bootstrap`: locked dependency/bootstrap checks pass.
- Focused tests: all new registries, schemas, valid fixtures, invalid fixtures,
  public toy vectors, no-network mock path, and registered corruptions pass.
- `make verify`: Ruff, MyPy, full tests, 110 claims, and 51 manifests pass.
- `make papers`: all seven accepted hashes remain exact and pages total 119.
- `make site`: registration-safe routes and data build while navigation remains
  five items and no result/leaderboard appears.

## Artifacts produced

M0 produces this plan and `reports/benchmark/agents-v1-before-state.yml`.
Later milestones produce the requested ADR, decision reports, contracts,
registries, schemas, public fixtures, validators, tests, DD-010 status updates,
and static-site registration surface.

## Blockers

None. Issue #32 is settings-only. A future owner cost decision is intentionally
pending and does not block offline registration.

## Preservation set

These unrelated untracked files predate this task and must remain untouched and
unstaged:

- `papers/information-sharing-frontier/paper-audit 2.json`
- `papers/information-sharing-frontier/visual-qa 2.md`
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`

## Recovery and restart instructions

Run `git status --short --branch`; verify the five preservation files remain
untracked; inspect the issue/PR through the connected GitHub application; read
the active milestone and latest decision here; resume the first unchecked
item. Never use `git add .`. Never rerun a passing DD-010 configuration.

## Outcome and retrospective

Local registration acceptance is complete with decision
`register-instrument-under-dd010`. The scientific inventory and all immutable
evidence remain unchanged. External CI, merge, Pages, live acceptance, issue
closure, and synchronized `main` remain in M21.
