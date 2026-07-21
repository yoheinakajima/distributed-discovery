# Project status and final handoff

> Current operational status, refreshed 2026-07-21 UTC. The M0–M9 and A–E handoff sections below remain the evidence baseline; the continuation queue is authoritative in `plans/MASTER_EXEC_PLAN.md`.

## 1. Executive summary

Milestones M0 through M9 and operational Milestone A are complete. Cleanup issue #6 closed through squash-merged PR #12 at `1add8de5a349c57085928da8aa54da85e49c5077`; CI passed, Pages workflow `29781940577` succeeded, and all five required routes returned HTTP 200. The source repository is public under MIT at `https://yoheinakajima.github.io/distributed-discovery/`. Canonical upstream remains untouched.

The authorized A–E queue and continuation cycles F–H are complete and merged. Alignment PR #23 merged as `df35f80273f106ef86f623c4676fe2a58757b6ad`; post-merge CI `29796429926` and Pages `29796429904` passed, and all seven public routes expose the exact canonical optimum `325089/390625` with the correct run provenance. DD-002 selection-robustness issue #24 and branch `research/dd002-selection-robustness` are active.

## Continuation checkpoint

- Current merged baseline: `007dc15b89f6d7e98e572d1b164f057c7c38c964`.
- Exact pooled top-eight endpoint: `860391662035297/1001129150390625`.
- Exact canonical private-team optimum: `325089/390625 = 0.83222784`; the prior pooled interval is valid but superseded.
- Three Results paper: `papers/three-results/Three_Results_in_Distributed_Discovery.pdf`, 12 pages, visually audited.
- Public Results route: `https://yoheinakajima.github.io/distributed-discovery/results.html`.
- Active task: define and execute the exact DD-002 equilibrium-selection catalogue under issue #24.

## 2. Repository map

| Path | Purpose |
|---|---|
| `claims/` | Authoritative claim ledger, schema, reviews, and proofs |
| `docs/` | Foundations, notation, literature evidence, ADRs, policies, and setup guides |
| `integrations/shared-discovery-paradox/` | Upstream pin, dependency lock, generated patch, and provenance |
| `papers/` | Additive preview plus deterministic Foundations and Three Results manuscripts |
| `plans/MASTER_EXEC_PLAN.md` | Complete milestone log, failures, decisions, and restart point |
| `results/` | Immutable baseline and DD-001 run records, separated by evidence class |
| `site/` | Dependency-free companion source and Pages build pipeline |
| `src/distributed_discovery/` | Independent models, runners, builders, and validators |
| `studies/DD-000`–`DD-007` | Per-study question, model, plan, status, report, and later-study briefs |
| `.github/` | CI, issue forms, taxonomy manifests, initial issue drafts, and PR template |

## 3. Completed milestones

- M0: repository contract, environment, schemas, ADRs, skills, tests, and study registry.
- M1: pinned canonical execution plus independent finite-model reproduction.
- M2: foundations, terminology, notation, institutional mapping, and literature orientation.
- M3: additive paper fragments, generated patch, deterministic 30-page preview, and QA.
- M4: four-page static companion generated from validated evidence; it was local-only when M4 closed and is now deployed through Pages.
- M5: deterministic 12-page foundations note with citation/claim/source validation and visual QA.
- M6: exact DD-001 tiny-grid evaluator, bounded canonical search, five audited claims, and report.
- M7: actionable, falsifiable DD-002 through DD-007 research briefs; later execution is tracked separately.
- M8: complete local GitHub organization metadata; prepared issues are live, with settings-only taxonomy blocked on OAuth.
- M9: clean acceptance reproduction, full builds/audits, navigation refresh, and this handoff.
- A: public MIT/Pages cleanup, passing squash merge, and live five-route deployment smoke test.
- DD-001A: lossless signature theorem, exact feasibility/reconstruction, independent tiny-grid reproduction, and canonical state-space certificate; merged.
- DD-001B: exact restricted-family threshold theorem, bounded continuous unrestricted classification, and anti-informative counterexamples; merged through PR #14.
- DD-002: complete bounded deterministic-policy enumeration, exact equilibrium registries, independent reversal verification, and full Blackwell-refinement census; merged through PR #15.
- DD-003: complete 51-graph census, independently reproduced orbit counts and exact outcomes, pairwise-moment bounded null, and scalar counterexamples; merged through PR #16 and deployed.
- F: exact canonical pooled-frontier certificate and exact DD-001 interval; merged through PR #19 and deployed.
- G: separate 12-page Three Results synthesis, generated figures/evidence table, and public Results route; merged through PR #21 and deployed.

## 4. Commands executed

The final sequence ran on Python 3.11.15:

```text
make all
  ruff format --check: 36 files passed
  ruff check: passed
  mypy --strict: 21 source files passed
  pytest: 28 passed
  claim validation: passed
  run-manifest validation: 6 pre-acceptance manifests passed
  canonical reproduction: validation_status=passed
  foundations paper: 12 pages, passed
  site build: 4 pages and 7 open studies, passed

make upstream-patch
  upstream pin/cleanliness: passed
  patch apply/content/compile: passed

pdfinfo + Poppler rendering
  foundations: 12 letter-size pages; targeted pages 1, 4, 8, and 12 visually inspected
  additive preview: 30 letter-size pages

make verify (after final provenance fix and documentation)
  pytest: 29 passed; all other validators passed

git grep secret/private-path patterns
  no credentials or token-shaped secrets; one local package URL class was found and corrected

git -C .cache/upstream/shared-discovery-paradox status --porcelain
  empty output; upstream remains clean at 5025cc8e8f2f8ca015dff2066f08f81ad5715a51
```

The two early M1 wrapper failures, initial paper-toolchain failures, first M8 formatting stop, and their corrections remain documented in the master plan. In the final audit, one direct module check initially lacked the Makefile's `PYTHONPATH`, and the new sanitizer test initially needed formatting; both were corrected and the 29-test rerun passed. The pre-commit whitespace gate also flagged CRLF in immutable upstream-generated CSVs; authored files passed after those hash-covered outputs were excluded. None is represented as passing evidence.

DD-001A primary run `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5` started from clean commit `b1d8d431` and completed in 13.73 seconds under a 120-second limit. It passed 21 exact-grid reproductions, raw tie reconciliation, dual feasibility checks, constructive reconstruction, independent objective evaluation, exact normalization, the structural certificate verifier, and manifest validation.

## 5. Canonical reproduction status

Acceptance run `20260720T202314Z_DD-000_88613408_217c602fa0` started from clean commit `88613408`, executed the pinned upstream verifier, and independently evaluated blind, private, private-distinct, consensus, planner, recovery-budget, normalization, and a tiny consensus fixture. All checks passed. Selected values are blind `0.5`, consensus `0.383468709731`, market `0.599099252439`, private `0.83222784`, planner `0.859421246199`, and recovery budget `7`.

The run is the current source for the site and foundations note. Claim records retain the earlier independently audited run ID `20260720T190336Z_DD-000_32dd1c32_217c602fa0`; this avoids silently rewriting established provenance.

## 6. Verified claims

The claim ledger has 38 records. DD-C-0037 proves the alignment count-budget relaxation is an admissible upper bound; DD-C-0038 independently reproduces the exact canonical deterministic and ex-ante randomized optimum. DD-C-0036 remains a valid superseded interval. DD-C-0029 through DD-C-0035 retain the bounded DD-002/DD-003 and exact pooled-frontier results.

## 7. Independently reproduced claims

- DD-C-0003 through DD-C-0006: canonical blind, private, consensus, and pooled-planner discovery.
- DD-C-0008: canonical pooled recovery budget `7`.
- DD-C-0020: all 21 configured DD-001 tiny-case optima by exact agent-symmetric exhaustive enumeration.
- DD-C-0021: exact hybrid witness `7/10 > 16/25` at `(3,2,2/5)`, checked by a materially distinct evaluator.
- DD-C-0024: all 21 tiny optima and raw-policy multiset tie counts reproduced by exact signature enumeration, with feasibility audited against raw policies through M=5.
- DD-C-0032: all 51 nonisomorphic bounded source graphs, with independent orbit traversal and pairwise nonisomorphism checks.
- DD-C-0033: ten matched pairwise-moment graph pairs and zero private-discovery differences, independently recomputed as a bounded null.
- DD-C-0034: equal mean agreement `3/4` with private discovery `8/9` versus `31/36`, independently recomputed.
- DD-C-0038: exact canonical private-team optimum `325089/390625`, where a feasible direct policy meets an independently checked Bellman upper certificate.

## 8. Exploratory findings

DD-C-0022 is `checked`, not verified: direct clue-following is an exact coordinate fixed point for the canonical DD-001 fixture, and 17 non-direct starts converged to its value `325089/390625`. This is constructive lower-bound evidence only. DD-C-0010's expected-distinct-action values are also `checked` rather than independently reproduced.

## 9. Refuted claims and negative results

- DD-C-0017 establishes that “Distributed Discovery” is not a unique phrase; no field-name novelty claim is supportable.
- DD-C-0021 refutes the general conjecture that direct clue-following is private-team optimal.
- The complete tiny grid also records null gains wherever direct is exact-optimal; these bounded nulls are not extrapolated.
- The two early M1 runs are preserved operational failures and excluded from research evidence.
- DD-003 finds no full pairwise-moment discovery counterexample in the exact 51-graph class; this bounded null is not a general sufficiency theorem.
- DD-C-0034 refutes sufficiency of average pairwise agreement; the same census also refutes source HHI sufficiency.
- The first alignment relaxation is strictly loose at `M=3,N=2,p=0`: upper bound `1` versus exact optimum `11/12`; its canonical equality is not extrapolated.

## 10. Open research questions

The A–E and F–G queues are complete. Cycle H has solved the frozen canonical DD-001 optimum and awaits PR #23 integration. DD-002 selection robustness and DD-003 heterogeneous-source accuracy follow sequentially; DD-004 through DD-007 remain unexecuted, and issue #8 intentionally queues the DD-007 schema only.

## 11. Known technical debt

- The first DD-001 alignment relaxation is not tight for every parameter; stronger per-role cross-target consistency remains a possible hierarchy extension.
- Tectonic 0.16.9 and Poppler are system-level build/inspection dependencies, not managed by `uv`.
- The static site has automated semantic/link/content/contrast checks but no browser-based accessibility audit.
- GitHub metadata application is tested offline; prepared issues are live as #7–#11 and issue/PR access works through the connected app, while CLI-only taxonomy/settings await OAuth authorization.
- Three historical DD-001 environment snapshots required an M9 privacy correction: their redundant local-project `file://` line was removed and future capture filters it. Research outputs and hashes were unchanged.
- Randomized DD-002 disclosure and general asymmetric mixed-equilibrium enumeration remain unimplemented by design; expanding scope requires an ADR and certificate plan.
- DD-003 is fixed to homogeneous source accuracy and four searchers; heterogeneous laws and larger exact graph classes remain unimplemented.
- DD-004 through DD-007 implementations and study-specific schemas do not exist yet.

## 12. Blockers

There is no validation blocker. Public `origin`, Actions, and Pages are active. Issues #6, #7, #9, #10, and #11 are closed; queued DD-007 issue #8 remains open. Only Dependabot PRs #1–#5 remain open. GitHub CLI 2.96.0 is installed but unauthenticated; the 23 prepared project labels, six milestones, homepage metadata, and a non-destructive `main` ruleset remain exact settings-capability blockers. Issue and pull-request operations remain available through the connected GitHub app.

## 13. Exact resume point

On `research/dd002-selection-robustness`, freeze the current DD-002 game and write the selection-catalogue ADR before implementing or running new procedures. The exact next source file is `src/distributed_discovery/information_design/selection.py` after the ADR fixes the rules.

## 14. Recommended next three tasks

1. DD-002: execute the registered equilibrium-selection robustness catalogue.
2. DD-003: execute the bounded heterogeneous-source-accuracy census.
3. DD-003: execute the bounded heterogeneous-source-accuracy census.

## 15. Commit list

- `32dd1c3` — M0 repository bootstrap.
- `dd7f0c6` — M1 canonical reproduction.
- `e1192de` — M2 foundations and literature.
- `6a43879` — M3 additive upstream paper extension.
- `1b7905d` — M4 private companion site.
- `6eb1286` — M5 foundations companion note.
- `16ec4b2` — M6 DD-001 exact tiny results.
- `7c4c25a` — M7 later-study briefs.
- `8861340` — M8 local GitHub organization.
- Final integration and handoff — the commit containing this report.

## 16. Draft pull-request information

Suggested title: `Bootstrap the Distributed Discovery research program`

- Study IDs: DD-000 through DD-007; research results for DD-000 through DD-003.
- Claim IDs: DD-C-0001 through DD-C-0034.
- Evidence status: mixed and ledger-controlled; exact status is never inferred from directory placement.
- Commands: `make all`, `make upstream-patch`, PDF inspection, secret/private-path scan, and Git/upstream cleanliness checks.
- Runs: canonical acceptance `20260720T202314Z_DD-000_88613408_217c602fa0`; DD-001 primary `20260720T200447Z_DD-001_6eb12861_ba766d1eba`; DD-001A primary `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5`; DD-001B primary `20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1`; DD-002 primary `20260720T225848Z_DD-002_94607423_e29b1460ae`; DD-003 primary `20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1`.
- Generated artifacts: foundations PDF SHA-256 `e096183159f8c016f116b1a97fc0721948bbee2aca6dd1ae251d0a2af95a32e4`; patched-preview PDF SHA-256 `0a43360e59fdbbc4002e2190479871896688b3b4ef640d219313cd9d2ed5acb9`; public four-page site.
- Citation changes: 15 validated bibliography keys; canonical claims trace to the pinned source and/or independent implementation.
- Upstream impact: none. The review patch applies in a disposable worktree; cached upstream is clean.
- Publication impact: repository source and tracked paper artifacts are public by explicit approval; Pages is live. Labels, milestones, homepage metadata, and a non-destructive ruleset remain settings-capability blockers.

## 17. Final A–E integration record

1. **Executive summary:** Cleanup, DD-001A, DD-001B, bounded DD-002, and bounded DD-003 are merged; final research claims stop at DD-C-0034.
2. **Public/MIT/Pages status:** The repository is intentionally public under the root MIT license. Third-party notices and read-only upstream separation are intact. Pages is public at `https://yoheinakajima.github.io/distributed-discovery/`.
3. **Branches and PRs merged:** PRs #12–#16 were squash-merged sequentially. Their merge SHAs are `1add8de5a349c57085928da8aa54da85e49c5077`, `c16144e8a3f5287d1117b768856f559064a89bc0`, `7e637c1dc191b90f8de477ae05a779a254e35055`, `526d2f0f19638bc2f87567972135ebac6a74ae63`, and `54b8713fa7f3b30922a88b60a6dc280319432715`.
4. **Issues:** #6, #7, #9, #10, and #11 are closed. Queued DD-007 issue #8 remains open by design.
5. **Commands run:** Milestone-specific exact runners plus `make bootstrap`, `make verify`, `make papers`, `make site`, upstream cleanliness checks, secret/local-path scans, Git reviews, GitHub workflow audits, and live route smoke tests. Exact run commands are stored in each immutable run.
6. **Tests and builds:** The final pre-handoff suite has 66 tests; strict mypy, Ruff, 34-claim validation, 13-run manifest validation, the 12-page foundations build, and the four-page site build pass.
7. **Pages deployment:** DD-003 post-merge Pages run `29787309537` deployed commit `54b8713fa7f3b30922a88b60a6dc280319432715`; `/`, `foundations.html`, `applications.html`, `open-problems.html`, and `styles.css` returned HTTP 200, and the live page contains both completed study statuses.
8. **Verified claims:** The ledger contains 34 records. DD-C-0029 through DD-C-0031 cover DD-002; DD-C-0032 through DD-C-0034 cover DD-003 with independent reproduction status.
9. **Independently reproduced claims:** Canonical benchmark quantities, DD-001 tiny optima and counterexamples, DD-001A tie counts, DD-001B anti-informative witnesses, and all three DD-003 claims have materially separate checks.
10. **Certified bounds:** The canonical DD-001 private-team value is exactly bounded by `[325089/390625, 860391662035297/1001129150390625]`; gap `27224111644672/1001129150390625`. The upper endpoint is not claimed attainable or tight.
11. **Heuristic lower bounds:** Canonical coordinate ascent returns the exact direct value `325089/390625` from the direct, territorial, and 16 seeded random starts; this remains a constructive lower bound only.
12. **New counterexamples:** DD-002 gives the exact selection-dependent disclosure reversal `5/9` to `171/308`. DD-003 gives matched mean agreement `3/4` with private discovery `8/9` versus `31/36`.
13. **Negative and null results:** DD-003 has ten matched complete pairwise-moment graph pairs and zero discovery differences. DD-001B's informative phase does not extend to `p=0`. Randomized DD-002 disclosure was not tested.
14. **Refuted conjectures:** General direct clue-following optimality, the all-`p` three-family DD-001B extension, unique use of “Distributed Discovery,” and sufficiency of average DD-003 pair agreement are refuted in their stated scopes.
15. **Current canonical DD-001 interval:** `[325089/390625, 860391662035297/1001129150390625]`, approximately `[0.83222784, 0.8594212461994395]`. The upper inequality is admissible because pooled observation can emulate every fixed private-team profile and conditionally optimize the same physical portfolio.
16. **DD-002 bounded outcome:** 15 policies, 37 posterior games, 256 global pure-equilibrium selections, 45 strict refinements, one selected reversal, eight worst-pure reversals, and no best-pure or planner reversals.
17. **DD-003 bounded outcome:** 51 canonical graphs (`1/8/42` by source count); ten matched pairwise-moment pairs with a bounded null; 22 matched-average-agreement counterexample pairs and 59 source-HHI counterexample pairs.
18. **Technical debt:** Canonical DD-001 lacks a joint alignment-preserving upper certificate; DD-002 randomized disclosure and general asymmetric mixed equilibria are deferred; DD-003 heterogeneous signal laws and larger exact graph classes are deferred; browser-based accessibility audit remains absent.
19. **Exact blockers:** No research, CI, build, or deployment blocker. Settings-only blockers are GitHub label/milestone creation, homepage metadata, and a safe `main` ruleset because the CLI lacks OAuth and the connected app does not expose those repository settings.
20. **Exact next task:** Merge/deploy the exact frontier certificate, then build the separate Three Results synthesis before beginning the alignment-preserving DD-001 relaxation.
21. **Exact resume command:** `git switch main && git pull --ff-only origin main && make verify`.
22. **Commit SHAs:** Queue merge SHAs are listed in item 3; primary evidence commits are `b1d8d431` (DD-001A), `b2cc23f4` (DD-001B), `94607423` (DD-002), and `2ea8dad5` (DD-003).
23. **Pull-request URLs:** `https://github.com/yoheinakajima/distributed-discovery/pull/12` through `/pull/17`; PR #17 is the documentation-only integrated handoff.
