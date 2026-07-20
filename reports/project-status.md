# Project status and final handoff

## 1. Executive summary

Milestones M0 through M9 are complete on `codex/bootstrap-distributed-discovery`. The repository now provides a reproducible canonical benchmark, a formal foundations layer, an additive upstream patch, a local companion site, a 12-page foundations note, bounded DD-001 results, executable DD-002–DD-007 briefs, and offline GitHub organization metadata. A public GitHub source repository was explicitly authorized after M9; the companion site remains un-deployed and canonical upstream remains untouched.

The strongest new research result is scoped: on the 21-case DD-001 tiny grid, exact exhaustive enumeration finds an informative hybrid policy at `(M,N,p)=(3,2,2/5)` with discovery `7/10`, versus direct clue-following `16/25`. The canonical `(16,8,1/5)` private-team optimum remains unresolved; coordinate ascent supplies only a lower bound.

## 2. Repository map

| Path | Purpose |
|---|---|
| `claims/` | Authoritative claim ledger, schema, reviews, and proofs |
| `docs/` | Foundations, notation, literature evidence, ADRs, policies, and setup guides |
| `integrations/shared-discovery-paradox/` | Upstream pin, dependency lock, generated patch, and provenance |
| `papers/` | Additive canonical-paper preview and foundations manuscript |
| `plans/MASTER_EXEC_PLAN.md` | Complete milestone log, failures, decisions, and restart point |
| `results/` | Immutable baseline and DD-001 run records, separated by evidence class |
| `site/` | Dependency-free companion source and generated local build |
| `src/distributed_discovery/` | Independent models, runners, builders, and validators |
| `studies/DD-000`–`DD-007` | Per-study question, model, plan, status, report, and later-study briefs |
| `.github/` | CI, issue forms, taxonomy manifests, initial issue drafts, and PR template |

## 3. Completed milestones

- M0: repository contract, environment, schemas, ADRs, skills, tests, and study registry.
- M1: pinned canonical execution plus independent finite-model reproduction.
- M2: foundations, terminology, notation, institutional mapping, and literature orientation.
- M3: additive paper fragments, generated patch, deterministic 30-page preview, and QA.
- M4: local four-page static companion, generated from validated evidence; not deployed.
- M5: deterministic 12-page foundations note with citation/claim/source validation and visual QA.
- M6: exact DD-001 tiny-grid evaluator, bounded canonical search, five audited claims, and report.
- M7: actionable, falsifiable DD-002 through DD-007 research briefs; no studies executed.
- M8: complete local GitHub organization metadata; intentionally not applied without a remote.
- M9: clean acceptance reproduction, full builds/audits, navigation refresh, and this handoff.

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

## 5. Canonical reproduction status

Acceptance run `20260720T202314Z_DD-000_88613408_217c602fa0` started from clean commit `88613408`, executed the pinned upstream verifier, and independently evaluated blind, private, private-distinct, consensus, planner, recovery-budget, normalization, and a tiny consensus fixture. All checks passed. Selected values are blind `0.5`, consensus `0.383468709731`, market `0.599099252439`, private `0.83222784`, planner `0.859421246199`, and recovery budget `7`.

The run is the current source for the site and foundations note. Claim records retain the earlier independently audited run ID `20260720T190336Z_DD-000_32dd1c32_217c602fa0`; this avoids silently rewriting established provenance.

## 6. Verified claims

The claim ledger has 22 records. Status `verified` applies to DD-C-0007 (canonical market), DD-C-0009 (copying crossover), DD-C-0015 (72-case grid sign-change observation), and DD-C-0017 (terminology non-uniqueness). DD-C-0012 through DD-C-0014 are explicitly `sourced` upstream theorem statements. DD-C-0002, DD-C-0011, DD-C-0016, DD-C-0018, and DD-C-0019 are scoped `derived` results with algebraic or proof records.

## 7. Independently reproduced claims

- DD-C-0003 through DD-C-0006: canonical blind, private, consensus, and pooled-planner discovery.
- DD-C-0008: canonical pooled recovery budget `7`.
- DD-C-0020: all 21 configured DD-001 tiny-case optima by exact agent-symmetric exhaustive enumeration.
- DD-C-0021: exact hybrid witness `7/10 > 16/25` at `(3,2,2/5)`, checked by a materially distinct evaluator.

## 8. Exploratory findings

DD-C-0022 is `checked`, not verified: direct clue-following is an exact coordinate fixed point for the canonical DD-001 fixture, and 17 non-direct starts converged to its value `325089/390625`. This is constructive lower-bound evidence only. DD-C-0010's expected-distinct-action values are also `checked` rather than independently reproduced.

## 9. Refuted claims and negative results

- DD-C-0017 establishes that “Distributed Discovery” is not a unique phrase; no field-name novelty claim is supportable.
- DD-C-0021 refutes the general conjecture that direct clue-following is private-team optimal.
- The complete tiny grid also records null gains wherever direct is exact-optimal; these bounded nulls are not extrapolated.
- The two early M1 runs are preserved operational failures and excluded from research evidence.

## 10. Open research questions

The immediate question is a certified upper bound for the canonical DD-001 private-team optimum. DD-002 through DD-007 remain open and unexecuted: disclosure under strategic concentration, latent source networks, sequential feedback, overlapping coverage, discovery mechanisms, and empirical audit identification. Each study's `brief.md` defines its bounded first experiment and completion criteria.

## 11. Known technical debt

- Canonical DD-001 optimization lacks a global certificate or usable structural reduction.
- Tectonic 0.16.9 and Poppler are system-level build/inspection dependencies, not managed by `uv`.
- The static site has automated semantic/link/content/contrast checks but no browser-based accessibility audit.
- GitHub metadata application is tested only in offline dry-run mode because `gh` is unavailable.
- Three historical DD-001 environment snapshots required an M9 privacy correction: their redundant local-project `file://` line was removed and future capture filters it. Research outputs and hashes were unchanged.
- DD-002 through DD-007 implementations and schemas intentionally do not exist yet.

## 12. Blockers

There is no validation blocker. The public `origin` was explicitly authorized and configured after M9. Draft pull-request creation and label/milestone/issue application still require installation and authentication of `gh`.

## 13. Exact resume point

Read `AGENTS.md`, `.agent/PLANS.md`, this report, `plans/MASTER_EXEC_PLAN.md`, and `studies/DD-001-private-information-teams/`. Inspect `git status`, run `make verify`, then review `.github/initial-issues/dd001-canonical-upper-bound.md`. Estimate the certificate method's state space and memory/time bounds before implementing it. Never describe DD-C-0022 as global optimality.

## 14. Recommended next three tasks

1. DD-001: derive or compute a certified canonical upper bound with a machine-checkable certificate.
2. DD-002: enumerate deterministic partitions for the bounded `M=3,N=2` disclosure fixture and report full equilibrium correspondence.
3. DD-003: enumerate nonisomorphic small source graphs and test whether pairwise report moments are insufficient for discovery prediction.

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

- Study IDs: DD-000 through DD-007; research results only for DD-000/DD-001.
- Claim IDs: DD-C-0001 through DD-C-0022.
- Evidence status: mixed and ledger-controlled; exact status is never inferred from directory placement.
- Commands: `make all`, `make upstream-patch`, PDF inspection, secret/private-path scan, and Git/upstream cleanliness checks.
- Runs: canonical acceptance `20260720T202314Z_DD-000_88613408_217c602fa0`; DD-001 primary `20260720T200447Z_DD-001_6eb12861_ba766d1eba`.
- Generated artifacts: foundations PDF SHA-256 `3293b469a50856b1301a20190b17d3483fcb18558e545b2301968d014fa869b5`; patched-preview PDF SHA-256 `0a43360e59fdbbc4002e2190479871896688b3b4ef640d219313cd9d2ed5acb9`; local four-page site.
- Citation changes: 15 validated bibliography keys; canonical claims trace to the pinned source and/or independent implementation.
- Upstream impact: none. The review patch applies in a disposable worktree; cached upstream is clean.
- Publication impact: repository source and tracked paper artifacts are public by explicit approval; the companion site is not deployed and GitHub metadata remains unapplied.
