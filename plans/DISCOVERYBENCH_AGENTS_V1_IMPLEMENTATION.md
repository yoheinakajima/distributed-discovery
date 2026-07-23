# DiscoveryBench Agents v1 offline implementation

This living ExecPlan follows `.agent/PLANS.md`. It implements issue #171 from
clean `main` commit `53edc37e34809c33e334ade79973e315835aa61a`. The work is
offline instrument implementation and execution-readiness validation. It is not
an evaluation campaign and creates no scientific evidence.

## Purpose and intended outcome

Implement the complete registered DiscoveryBench Agents v1 instrument so that
a later owner-authorized provider/model campaign can be registered without
redesigning the benchmark. The expected but not predetermined decision is
`ready-for-evaluation-registration`. A precise registered stop is also a
successful outcome.

## Live baseline

The live audit at `2026-07-23T15:38:56Z` found local and remote `main` at
`53edc37e34809c33e334ade79973e315835aa61a`, the squash merge of PR #170.
Issue #169 is closed with decision `register-instrument-under-dd010`. Branch CI
`30018405916`, branch paper/site `30018405775`, post-merge CI `30018629791`,
and Pages `30018630109` all passed. There is no open pull request. Issue #32
is the only pre-existing open issue and is settings-only.

The frozen scientific inventory is 110 claims through DD-C-0110, 26 studies
through DD-022, and 51 manifests with 48 passing immutable runs. The tracked
`results/verified` tree is
`c8fd20f66797c5014acf658a749e7f15fcaf6750`. No DD-023 or DD-C-0111 exists.
The source tree contains 160 Python files and pytest collects 274 tests.

DiscoveryBench v1/v2/v3 preserve respectively 15/20/24 tasks, 13/21/29
protocols, 19/27/39 metrics, 16/28/36 compatible exact rows, and
179/392/660 exclusions. V1 remains the default, the external adapter is
disabled, prohibited capabilities remain closed, and no composite score
exists.

The seven accepted PDFs total 119 pages and retain the exact registered hashes:

- Foundations: `8875926a52f0b8e722f7ce827c456c4b694f9e981c21c4b15bf2b3c60b83e76b`
- Three Results: `9eb896353b1210706d6108685dde963e02d6a5ebc64af9f9f69c08c01f5ebc96`
- Discovery Institutions: `78606f732f105d79395409dcb9d7224d72aa1e44312ca30ff5719d049afd98a8`
- Common-Source Trap: `afa9384eca60cf2a0291c2c42012f15ca59bf3d29b7c939b1882a0237ea58ff7`
- Incentive to Ignore: `651c91fb68df6b2f1397ca86f3842b7c2fa9c067601957c32401a7f5e95cd24b`
- Threshold Discovery: `634e96662989a3fd6efb5fc3e6919883897e60511826e25c6d0176bac4af9249`
- Information Sharing Frontier: `a317e8851a84b494d8ef30eccc1e31dd4448dc1bbcd3fb2de0fc2849bd581a13`

The upstream pin is
`5025cc8e8f2f8ca015dff2066f08f81ad5715a51`. The registered site baseline is
81 routes, 88 public data files, 18 Labs, 23 downloads, and five navigation
items.

## Scope

1. Build one coherent `distributed_discovery.benchmark.agents_v1` package.
2. Implement exact deterministic public-fixture generation for all five
   registered families and four isomorphic surfaces per canonical cell.
3. Compile leakage-audited prompts and closed capability views.
4. Implement the five registered architecture orchestrators.
5. Implement provider-neutral adapter contracts, deterministic/adversarial
   mocks, disabled injected-transport cloud boundaries, and a no-execution local
   contract.
6. Validate structured visible messages and actions with one schema-only retry.
7. Reconstruct exact comparator objects and compute the registered metric
   vector without a composite.
8. Implement raw/redacted/audit traces and deterministic hashing.
9. Implement commitments, public-toy AEAD envelopes, custody manifests, access
   logs, output locks, and unsealing checks using established libraries only.
10. Implement contamination probes, quarantine, batch planning, zero-spend
    guards, and execution-authorization refusal.
11. Implement an independent primitive verifier and execute all 24 registered
    corruptions on public fixtures.
12. Add CLI/Make interfaces, a deterministic no-network rehearsal, readiness
    decision, DD-010 documentation, and truthful static-site integration.

## Non-goals

No provider/model invocation, local model execution, model download,
credential, private seed, sealed holdout, real answer key, real encryption key,
provider trace, benchmark performance result, spend, scientific claim,
immutable run, new study, paper/PDF/lifecycle change, Reliable Discovery,
person contact, ActiveGraph mutation, SQLite, canonical-upstream mutation,
submission, release, DOI, ranking, leaderboard, or composite score.

## Source-of-truth boundary

Git is authoritative for generator and version registries, public calibration
fixtures, protocol/architecture/adapter contracts, authorization schema,
custody and contamination implementation, trace schemas, metric definitions,
verification, corruptions, and implementation acceptance. Existing immutable
study outputs remain authoritative for theoretical baselines. This gate writes
no artifact under `results/verified`.

## Fixed owner decisions

- DD-010 owns the instrument.
- Content v1/v2/v3 remains immutable; `agents-v1` is a separate protocol axis.
- Offline is the default and normal mode.
- External spend authorization defaults to USD 0.
- Any live-capable boundary is disabled, transport-injected, snapshot-pinned,
  authorization-gated, cost-guarded, custody-gated, and fail-closed.
- Agent-visible prompts expose no DD/claim/run IDs, paper/theorem/result names,
  known values, generator internals, answer data, evaluator state, or custody
  data.
- All outputs are machine-graded; hidden reasoning is never requested, stored,
  inferred, or scored.
- The primary result is a metric vector, never a default composite or universal
  provider ranking.
- Paper source, PDFs, metadata, lifecycle, claim roles, and visual-QA records
  remain unchanged.

## Package layout and architecture

The implementation will live under
`src/distributed_discovery/benchmark/agents_v1/` and reuse the existing DD-010
registries/evaluator. Modules will separate versions/models, generation,
prompts/capabilities, adapters/orchestration, actions/evaluation, traces,
custody, contamination, authorization/batch planning, verification,
corruptions, rehearsal/readiness, and CLI. Public acceptance artifacts live
under `reports/benchmark/`, never `results/verified`.

## Milestones

- **M0 (active):** live audit, mandatory reading, immutable baseline, issue,
  branch, living plan, baseline record, first commit, push, and draft PR.
- **M1:** package architecture and unified version manifest.
- **M2:** deterministic five-family generator and public fixtures.
- **M3:** prompt compiler and leakage audit.
- **M4:** closed capability sandbox.
- **M5:** five architecture orchestrators and exact comparator path.
- **M6:** provider-neutral adapters and deterministic/adversarial mocks.
- **M7:** structured actions and one schema-only retry.
- **M8:** exact baseline reconstruction and metric evaluator.
- **M9:** raw/redacted/audit traces and hashes.
- **M10:** public-toy cryptographic custody implementation.
- **M11:** contamination probes and quarantine.
- **M12:** batch planner and zero-spend cost guard.
- **M13:** execution-authorization schema, fixture, validator, and refusal.
- **M14:** independent primitive verifier.
- **M15:** all 24 corruption executions.
- **M16:** CLI and Make interfaces.
- **M17:** complete deterministic offline rehearsal.
- **M18:** implementation-readiness decision.
- **M19:** DD-010 and static-site integration.
- **M20:** paper/lifecycle and full local acceptance.
- **M21:** final PR, CI, merge, Pages, live acceptance, issue closeout, and
  synchronized `main`.

Exactly one milestone is active at a time.

## Progress checklist

- [x] Inspect branch, worktrees, remotes, and preservation set.
- [x] Fetch/synchronize main with `--ff-only` and verify the expected SHA.
- [x] Inspect open issues/PRs, issue #169, PR #170, closeout, and workflows.
- [x] Verify scientific, benchmark, paper, site, and upstream baselines.
- [x] Complete the mandatory governance, Phase 2, registration, DD-010,
  scientific-owner, implementation, test, and infrastructure reading.
- [x] Open issue #171 and create the implementation branch.
- [ ] Commit/push M0 and open the draft PR.
- [ ] Complete M1 through M20 sequentially.
- [ ] Complete M21 and synchronize `main`.

## Discoveries and surprises

- The expected live baseline and five-file preservation set match exactly.
- The registration implementation is deliberately a registry/schema auditor
  plus one public toy action. It has no real generator, orchestrator, adapter
  contract, evaluator, custody envelope, authorization guard, independent
  implementation verifier, or rehearsal pipeline, so this gate must implement
  those without forking DD-010.
- Existing exact DD-010 code already supplies immutable content registries,
  capability-deny behavior, exact output vectors, a disabled adapter, and a
  materially separate baseline verifier. The new package can extend these
  boundaries while leaving all v1/v2/v3 code paths and outputs unchanged.

## Decision log

- `2026-07-23T15:38:56Z`: no substantive PR conflict exists; issue #171 and
  branch `benchmark/discoverybench-agents-v1-implementation` own the sole lane.
- `2026-07-23T15:38:56Z`: preserve the five unrelated untracked duplicates
  without reading, editing, moving, deleting, normalizing, or staging them.
- `2026-07-23T15:38:56Z`: implement provider request builders/parsers only as
  inert data transforms behind injected transports; do not re-audit provider
  docs unless a contract cannot be derived from the registered official-source
  candidate record.
- `2026-07-23T15:38:56Z`: use established `cryptography` AEAD through the
  development dependency only for fixed public toy keys; private generation
  remains impossible without later authorization and secret context.

## Generator

Generation is deterministic from an explicit public manifest. Every instance
contains separate agent-visible and evaluator-only objects, exact rational
strings, stable ordering, declared target/agent isomorphisms, hidden-label
support, and commitments. The registered totals must remain exactly 138 cells,
552 isomorphic prompts, and 58,945 primitive states. Private mode refuses
without a future validated authorization and custody secret context.

## Prompt compiler and capability isolation

The compiler emits public-calibration and future-private payload shapes without
answer/baseline objects. Leakage lint checks scientific IDs, paper/theorem
language, values sourced from evaluator objects, public IDs/wording, generator
fields, answer fields, and custody fields. Capability views are immutable
allow-lists and prohibit filesystem, shell, network, environment, repository,
secrets, target, evaluator, seed, holdout, prior-batch, and undeclared-signal
access.

## Orchestrators, adapters, and actions

Orchestrators enforce identity, turns, topology, messages, memory, output
rights, two-round/256-token/default limits, one schema retry, and timeout
metadata. Adapters return visible messages, structured actions, usage, errors,
and retry classes only. Deterministic, adversarial, malformed, and timeout
mocks travel through the real orchestration path. Live-capable boundaries
remain disabled and cannot access a network without a later positive
authorization and explicit injected transport.

## Evaluation, traces, custody, contamination, and guards

Method A computes group discovery, coverage, duplication, regrets, recovery,
source diversity, communication compression, equilibrium distances, invalid
actions, compliance, calls, tokens, and cost with exact rational comparator
fields. Traces retain visible protocol state only and have event/whole-trace
hashes plus typed redaction records. Custody uses domain-separated SHA-256 and
AES-256-GCM public toy envelopes with fixed public keys/nonces. Contamination
uses the twelve registered probe classes and preserves inconclusive overlap.
The batch planner exposes low/base/high forecasts while the guard refuses all
positive external spend in this gate.

## Verification and corruptions

Method B reconstructs primitives, rights, exact baselines, metric numerators
and denominators, trace hashes, custody commitments, output locks, aggregation,
exclusions, and zero-cost/no-network status without importing Method A metric
classifications where primitive recomputation is possible. Each of the 24
registered corruptions must fail at its intended component/error class.

## Validation strategy

Run `git diff --check`, `make bootstrap`, focused tests for M1–M16, the complete
offline rehearsal, `make audit-agents-v1`, `make agents-v1-dry-run`,
`make agents-v1-readiness`, `make verify`, `make papers`, and `make site`.
Compare claims, studies, manifests, verified-results tree, existing benchmark
vectors, paper/lifecycle trees, PDF hashes/pages, upstream pin, and preservation
set to M0. Scan for secrets, private material, host paths, SQLite, provider
clients, model execution, network use, hidden-reasoning fields, and scientific
result artifacts. Perform local desktop and 390-pixel browser acceptance.

## Commands and expected observations

- `make audit-agents-v1`: schemas, registries, public fixtures, implementation,
  all corruptions, and no-execution invariants pass.
- `make agents-v1-dry-run`: deterministic public rehearsal writes only a
  disposable or `reports/benchmark/` acceptance artifact, reports zero calls,
  zero cost, no network/model/private material, and stable hashes.
- `make agents-v1-readiness`: independently verifies the rehearsal and emits a
  registered readiness decision.
- `make verify`: Ruff, strict MyPy, all tests, 110 claims, and 51 manifests pass.
- `make papers`: seven accepted hashes and 119 pages remain exact.
- `make site`: truthful implementation status appears without any result,
  leaderboard, composite, provider endorsement, external script, or sixth
  navigation item.

## Artifacts produced

M0 produces this plan and an implementation before-state record. Later
milestones produce the package, schemas/fixtures, tests, CLI/Make commands,
public rehearsal and readiness reports, DD-010 status updates, and static-site
implementation documentation.

## Blockers

None. Issue #32 is settings-only. A future provider/model and cost decision is
intentionally unauthorized and does not block offline implementation.

## Preservation set

These unrelated untracked files predate the task and must remain untouched and
unstaged:

- `papers/information-sharing-frontier/paper-audit 2.json`
- `papers/information-sharing-frontier/visual-qa 2.md`
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`

## Recovery and restart instructions

Run `git status --short --branch`; verify the five preservation files remain
untracked; read the active milestone and latest decision here; inspect issue
#171 and the draft PR; resume the first unchecked item. Never use `git add .`.
Never write under `results/verified`, create private material, or invoke a
provider/model.

## Outcome and retrospective

Pending. Normal completion requires a merged/deployed offline instrument,
passing public rehearsal and all corruptions, Method A/B agreement, zero
network/model/cost/private material, unchanged science and papers, closed issue,
and synchronized `main`.
