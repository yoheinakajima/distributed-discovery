# Program V2 project status and final handoff

_Acceptance prepared 2026-07-21 from merged `main`
`d478a175aa3326a3be1efc1b50b9542e5e1c2011`. This documentation-only handoff
is issue #77 / PR #78; its final squash SHA and post-merge workflow IDs are
recorded by GitHub and in the closing response._

## 1. Executive summary

Program V2 is complete at its registered bounded scope. DD-010 provides an
exact golden benchmark with capability isolation; DD-011 provides a frozen
synthetic experimental design and conditional power grid; DD-008B proves the
general finite-team Common-Source thresholds and records a counterexample to a
tempting universal ordering; the 20-page *Common-Source Trap* working paper is
reproducible and deployed; and the benchmark, experiment, Labs, studies, paper,
and 15 checksum-registered downloads are integrated into the static site.

Final acceptance passed bootstrap, 138 tests, strict mypy over 94 source files,
Ruff, claim/run validation, a focused 30-test certificate/corruption/leakage/
schema audit, all four paper builds, all-page paper QA records, a 48-page site
build, download provenance, secret/host-path/license scans, and pinned-upstream
cleanliness. No completed primary run was duplicated.

## 2. Current main SHA

The final-handoff base is
`d478a175aa3326a3be1efc1b50b9542e5e1c2011`, the squash merge of site PR #76.
PR #78 changes documentation only.

## 3. DD-010 task count

DiscoveryBench v1 contains 15 exact golden tasks covering the 15 required
families.

## 4. DD-010 protocol count

The registry contains 13 protocol contracts. External adapters remain disabled,
credential-free, and absent from CI execution.

## 5. Golden task count

All 15 tasks are golden tasks tied to exact claim/run evidence. No displayed
decimal was substituted for an available exact fraction.

## 6. Compatible task/protocol pair count

Sixteen of 195 declared task/protocol pairs are compatible. The other 179 are
explicit machine-readable exclusions, not benchmark failures.

## 7. Golden suite exact reproduction status

All 16 compatible result vectors pass the separate golden verifier with exact
fractions and claim/run provenance. Task-value and information-boundary
corruptions are rejected.

## 8. Information-leakage test result

Passed. Adversarial protocols cannot read target state, other private signals,
future outcomes, undeclared source identifiers, or evaluator internals. Protocols
receive immutable allow-list views.

## 9. Benchmark primary run

`20260721T183014Z_DD-010_ce930050_8ec718c242`, supporting DD-C-0055.

## 10. DD-011 design cell count

The selected contrast-complete fractional design contains 20 treatment cells
from the declared 180-cell full factorial.

## 11. Primary hypotheses

Six hypotheses are primary and two are secondary. The registry contains eight
frozen hypotheses, 15 outcomes, explicit estimands, directions, analysis models,
and multiplicity families.

## 12. Synthetic response scenarios

Eight versioned scenarios cover rational response, quantal noise, heterogeneous
costs, heterogeneous social preferences, partial mechanism compliance, report
error, attrition, and learning over rounds. They are assumptions, not empirical
behavioral models.

## 13. Power simulation count

The run evaluates 8 hypotheses × 8 scenarios × 6 sample sizes × 1,000
replications = 384 power rows and 384,000 Monte Carlo draws. It also preserves
640 balanced synthetic assignments.

## 14. Sample-size and MDE results

In the favorable rational-response scenario, all eight assumed effects reach
estimated power at least 0.80 by total `N=960`, and seven do so by `N=640`.
First passing sample sizes for H1–H8 are respectively `200, 480, 640, 320, 320,
200, 640, 960`. Conditional MDEs span `0.063164–0.070782` at `N=640` and
`0.051573–0.057793` at `N=960`.

## 15. Calibration failures

The design retains 140 failures among the 192 scenario/hypothesis rows evaluated
at `N=640`, `800`, or `960` that remain below power 0.80. This sensitivity
result prevents the rational scenario from being presented as general power.

## 16. No-human-data status

> **No participants were recruited. No human data were collected. No experiment
> was conducted. Separate ethics and institutional review are required before
> deployment.**

The kit is preregistration-ready, not preregistered or deployed.

## 17. DD-008B analytic outcome

For `q=1-p`, the private gain after `k` independent users is
`A_k = pq E[1/(1+X_k)-1/(N-k+X_k)]`, with `X_k ~ Binomial(k,p)`. The sequence
is strictly decreasing to `A_(N-1)=0`, and count `k` is a weak equilibrium iff
`A_k <= c <= A_(k-1)` with the boundary inequalities omitted as appropriate.
Planner margins are `B_k=p(1-p)^(k+1)` through `N-2`, then zero. The all-common
trap is `[p(1-p)(N-1)/N, p(1-p))`, width `p(1-p)/N`.

The exact fixture `N=3`, `p=4/5`, `c=13/375` has unique equilibrium count two
and planner count one. Therefore this is **not** a universal under-acquisition
theorem. Run `20260721T192412Z_DD-008B_649deb08_29dbeaf3a9` supports theorem
DD-C-0057 and negative result DD-C-0058.

## 18. Common-Source Trap paper title

*The Common-Source Trap: Endogenous Independent Evidence in Distributed
Discovery*.

## 19. Paper page count

20 substantive letter-size pages.

## 20. Paper checksum

SHA-256
`c997bba31c021bd799f2b3a561e8e558a1334f844aa87a448ade10319dac2ad3`.
The PDF is byte-reproducible across isolated builds and all 20 pages passed
Poppler visual inspection.

## 21. Paper public URL

<https://yoheinakajima.github.io/distributed-discovery/publications/common-source-trap.html>
with PDF at
<https://yoheinakajima.github.io/distributed-discovery/downloads/The_Common_Source_Trap.pdf>.
It is a working paper with no DOI, submission, peer review, or verified novelty
claim.

## 22. New site routes

Program V2 exposes `research/dd-008b.html`, `research/dd-010.html`,
`research/dd-011.html`, `benchmark.html`, four nested benchmark routes,
`experiment-kit.html`, three nested experiment-kit routes,
`publications/common-source-trap.html`, `data/downloads.json`, and the validated
paper PDF. The full site contains 48 HTML routes and 40 public data files.

## 23. New Lab routes

`labs/benchmark.html` and `labs/experiment-design.html`; the site contains eight
Lab routes total. Browser checks confirm exact filtering, keyboard-native select
controls, complete no-JavaScript tables, local assets, and zero document
overflow. The Labs accept no submissions.

## 24. Claim count

58 claims: 29 independently reproduced, 15 verified, 7 derived, 3 checked,
3 sourced, and 1 proposed.

## 25. Test count

`make verify` collects and passes 138 tests. The focused final acceptance subset
passes 30 certificate, corruption, leakage, schema, synthetic-design, run, and
site tests.

## 26. Manifest count

All 35 immutable manifests validate; 32 have passing validation status and exit
status zero. Final acceptance created no new run.

## 27. Passing-run count

32 passing immutable runs.

## 28. Paper count

Four validated project-authored PDFs: 12-page Foundations, 14-page Three
Results, 3-page Institutions, and 20-page Common-Source Trap. The additive
upstream preview remains a separate patch artifact, not a fifth project paper.

## 29. CI run IDs

| Milestone | PR | PR CI | Additional PR artifact | Post-merge CI |
| --- | ---: | ---: | ---: | ---: |
| DD-010 | #68 | recorded on PR #68 | path-triggered benchmark/site checks | `29858324779` |
| DD-011 | #70 | `29860373958` | `29860373814` | `29860525523` |
| DD-008B | #72 | `29861791351` | `29861791353` | `29861944847` |
| Common-Source Trap paper | #74 | `29863960868` | `29863960911` | `29864137509` |
| Program V2 site integration | #76 | `29864826334` | not path-triggered | `29864943433` |

All listed runs succeeded. PR #78 and its post-merge CI are the final
documentation-only gates and are recorded in GitHub and the closing response.

## 30. Pages run IDs

Successful post-merge Pages runs: DD-010 `29858324517`, DD-011 `29860525526`,
DD-008B `29861945022`, paper `29864138029`, and site integration
`29864943468`. PR #78's final Pages run is recorded after merge.

## 31. Live route checks

After site PR #76, 17 checks returned HTTP 200: the three Program V2 study
routes; the benchmark overview plus four nested routes; the experiment-kit
overview plus three nested routes; both new Labs; the Common-Source publication
page; `data/downloads.json`; and the validated PDF. The deployed manifest has
15 positive-length entries and 64-character SHA-256 values.

## 32. Issues opened and closed

Program V2 issues #67, #69, #71, #73, and #75 are closed complete. Stale paper
issue #52 was reconciled and closed after confirming completion through PR #54.
Final issue #77 closes with PR #78. Settings issue #32 remains open by design.

## 33. PRs opened and merged

DD-010 #68 → `62d4cd1c0819ae4a16330b22b059ddfbd86107d6`;
DD-011 #70 → `9caf0f975d176aa01e4d6e6e02f1555c1530c44e`;
DD-008B #72 → `24252c897c0cccec765364c6087848f08f27ead1`;
paper #74 → `ee0027f6296f9716dcef885d0317fa9dff5cbedf`;
site #76 → `d478a175aa3326a3be1efc1b50b9542e5e1c2011`.
Final handoff PR #78 is the only active Program V2 PR while this report is
prepared.

## 34. Exact results

DD-010 exactly reproduces 16 compatible golden vectors. DD-008B proves the
threshold ordering and equilibrium-count characterization, including the exact
all-common interval. The paper also preserves DD-008's two-agent interval,
DD-008A's 126-row finite census, DD-006B's 16 strict subsidized mechanism rows,
and DD-009's 20 coherent exact architectures without merging their models.

## 35. Simulated results

DD-010's sensitivity layer uses 8 explicit seeds and 8,000 draws and supports no
exact benchmark claim. DD-011 uses 384,000 seeded draws and reports Wilson
intervals, MDEs, attrition/clustering/noise sensitivity, and conditional power.
Neither suite is empirical evidence about people or organizations.

## 36. Negative and null results

- DD-008B's interior fixture rejects universal under-acquisition.
- DD-011 retains 140 of 192 large-sample calibration failures.
- DD-010 retains 179 incompatible task/protocol pairs as exclusions.
- DD-006B has no weak row in its target-visible/action-hidden regime and no
  budget-balance theorem.
- DD-009 rejects 268 incoherent architecture cells and provides no universal
  ranking.
- Prior bounded nulls and negative results remain in the claim ledger and
  immutable evidence rather than being discarded.

## 37. Refuted conjectures

Common-source incentives do not imply equilibrium independence is always below
the planner count. Pairwise source summaries do not generally identify
discovery. Direct clue-following is not universally optimal. Information
refinement is not universally harmful across equilibrium selections. The term
“Distributed Discovery” has no verified novelty claim.

## 38. Experimental predictions

The frozen DD-011 predictions are: costly independence may be under-acquired
near the all-common boundary; assignment should mechanically raise independent
source use; public disclosure can raise agreement without raising discovery;
and acquisition plus marginal-coverage allocation may be complementary. These
are untested predictions, not treatment effects.

## 39. Open questions

Heterogeneous source quality, correlated “independent” providers, alternative
prize sharing, mixed source choice, dynamic acquisition, reusable evidence
value, and integrated acquisition/truth/allocation with budget balance require
new models. Benchmark expansion requires versioned exact tasks and adapter
conformance. Any human study requires a separate ethics and governance gate.

## 40. Technical debt

Tectonic and Poppler remain system paper dependencies outside `uv`. Browser
smoke tests do not constitute full screen-reader/WCAG conformance. Publication
discovery remains an explicit four-paper builder registry. Settings manifests
are validated offline but unapplied.

## 41. Settings status

The single authorized settings command failed at its first authenticated GitHub
CLI read with exit status 4; no setting changed and no retry was made. Issue #32
records the required Issues-write, Metadata-read, and Administration-write
authority for labels, milestones, homepage metadata, and a safe `main` ruleset.

## 42. Exact blockers

There is no research, build, test, paper, site, CI, Pages, license, provenance,
secret, host-path, download, upstream, or Git blocker. Issue #32 is the sole
operational blocker and does not block Program V2 completion.

## 43. Exact next task

There is no mandatory Program V2 research task. If settings-capable authority is
intentionally supplied, resolve issue #32. Any research extension begins with a
new bounded issue rather than rerunning a completed primary configuration.

## 44. Exact resume command

`git switch main && git pull --ff-only origin main && make verify`

For settings only, the next authorized command is `gh auth login`, followed by
the reviewed steps in `docs/github-setup.md` and issue #32.

## 45. Commit SHAs

Program V2 merge SHAs are `62d4cd1c0819ae4a16330b22b059ddfbd86107d6`,
`9caf0f975d176aa01e4d6e6e02f1555c1530c44e`,
`24252c897c0cccec765364c6087848f08f27ead1`,
`ee0027f6296f9716dcef885d0317fa9dff5cbedf`, and
`d478a175aa3326a3be1efc1b50b9542e5e1c2011`. Primary evidence commits are
embedded in immutable run IDs and manifests.

## 46. PR URLs and exact next file

- <https://github.com/yoheinakajima/distributed-discovery/pull/68>
- <https://github.com/yoheinakajima/distributed-discovery/pull/70>
- <https://github.com/yoheinakajima/distributed-discovery/pull/72>
- <https://github.com/yoheinakajima/distributed-discovery/pull/74>
- <https://github.com/yoheinakajima/distributed-discovery/pull/76>
- <https://github.com/yoheinakajima/distributed-discovery/pull/78>

The exact next file for program orientation is `docs/current-state.md`; for the
only blocker it is `docs/github-setup.md`.
