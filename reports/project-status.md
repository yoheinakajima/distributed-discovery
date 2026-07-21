# Project status and final continuation handoff

> Acceptance record prepared 2026-07-21 UTC on `docs/final-continuation-handoff` from merged `main` commit `fa2fd5a473810dc00a5f8b483b4f196a6522f7be`. The documentation-only handoff PR advances `main`; its final merge and deployment identifiers are recorded in that PR and the closing task response.

## 1. Executive summary

The M0–M9 bootstrap, public/MIT/Pages integration, DD-001A/B, bounded DD-002/DD-003 studies, and continuation cycles F–L are complete. Research cycles F–J produced four independently checked immutable runs, claims DD-C-0035 through DD-C-0044, a 14-page synthesis paper, and a public Results page. Dependency cycle K replaced all five stale Dependabot PRs with three reviewed, passing maintenance PRs. Cycle L made the authorized settings attempt exactly once; GitHub CLI authentication failed before mutation and issue #32 records the exact missing authority and commands.

There is no research, validation, CI, build, deployment, license, secret, provenance, or upstream-cleanliness blocker. The only operational blocker is settings-capable GitHub authentication for labels, milestones, repository homepage metadata, and a non-destructive `main` ruleset.

## 2. Current main SHA

The final-acceptance base is `fa2fd5a473810dc00a5f8b483b4f196a6522f7be` (`chore: migrate to mypy 2 (#31)`). The handoff branch was clean at creation and changes documentation only.

## 3. Public, MIT, and Pages status

- Repository: `https://github.com/yoheinakajima/distributed-discovery`, intentionally public.
- License: root MIT license; third-party/upstream boundaries are documented in `LICENSE-STATUS.md`.
- Pages: `https://yoheinakajima.github.io/distributed-discovery/`, live and generated from `main` by Actions.
- Canonical Shared Discovery Paradox upstream: pinned read-only at `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`; cached worktree clean after final validation.

## 4. Exact planner frontier

Run `20260721T012208Z_DD-000_8e4b55e2_e8321d1048` independently enumerates the complete canonical pooled frontier for budgets one through eight. The exact top-eight value is

`860391662035297/1001129150390625 = 0.8594212461994395`.

The exact recovery budget is seven. Labeled-count and histogram/orbit implementations agree, probability mass is exact, and the independent verifier rejects a corrupted frontier.

## 5. Exact canonical DD-001 interval

The frozen deterministic and ex-ante randomized zero-communication private-team frontier is exactly

`[325089/390625, 325089/390625] = [0.83222784, 0.83222784]`.

Direct clue-following attains the lower endpoint. The alignment-preserving Bellman certificate proves the matching upper endpoint.

## 6. DD-001 alignment-preserving relaxation

Run `20260721T022739Z_DD-001_358cb1eb_cd16846ba5` retains aligned incoming-count vectors within every target, relaxes only cross-target feasibility, and is independently verified. Canonically it improves the earlier pooled upper bound from `860391662035297/1001129150390625` to `325089/390625`, closing the gap exactly. It is not universally tight: at `(M,N,p)=(3,2,0)` its upper value is `1` while the exact optimum is `11/12`.

## 7. DD-002 selection robustness

Run `20260721T025802Z_DD-002_73a85c71_b0e5b6dc49` evaluates all 15 policies and 45 strict refinements under six exact procedures. The known pooling-to-refinement reversal survives only anonymous-symmetric selection (`5/9` to `171/308`). Best pure, worst pure, uniform potential maximizer, uniform strict-best-response basin, and planner all improve from `2/3` to `3/4` for that witness. Harmful-refinement counts in that order are `1, 0, 8, 2, 2, 0`.

## 8. DD-003 heterogeneous sources

Run `20260721T032358Z_DD-003_84238b76_2cbc13e66a` enumerates 41,612 valid base labeled colored objects into 671 orbits and 12,966 controlled-expansion objects into 168 orbits: 839 networks total. There are 163 complete first/pairwise-moment groups covering 485 networks; 111 matched groups have different discovery. The simplest exact counterexample has identical 66-entry complete first/pairwise scalar-report moments but discovery `3/4` versus `2/3`, difference `1/12`. A materially separate implementation reconstructs all 839 networks and rejects a zeroed difference.

## 9. Three Results paper

`papers/three-results/Three_Results_in_Distributed_Discovery.pdf` is a deterministic 14-page letter-size PDF with SHA-256 `53cbfa8ccf6f732b13670206f3a8c25627390cbb29206f6b1b017163ae3735bf`. Final acceptance rebuilt it, validated citations/references/provenance, rendered all 14 pages with Poppler, and visually inspected every page without finding clipping, overlap, illegible figures, or malformed references.

## 10. Results page

`https://yoheinakajima.github.io/distributed-discovery/results.html` is live. Its generated data exposes the exact canonical optimum, prior pooled benchmark, six-rule disclosure catalogue, homogeneous bounded null, heterogeneous counterexample, claim IDs, run IDs, and checksum-bound source artifacts.

## 11. Claim count and statuses

The ledger has 44 claims: 19 independently reproduced, 11 verified, 7 derived, 3 checked, 3 sourced, and 1 proposed. DD-C-0035–DD-C-0044 are the continuation claims. Claim-schema validation passes.

## 12. Test count

Final `make verify` passes 95 tests, Ruff formatting/lint, and strict mypy 2.3 across 45 source files. A focused 35-test certificate/provenance suite also passes.

## 13. Manifest count

All 17 immutable run manifests validate. Final acceptance deliberately did not rerun the four completed study targets, because each target creates a new timestamped immutable run and the existing primary runs were already executed, independently checked, merged, and deployed.

## 14. Paper page counts

- Foundations: 12 pages, SHA-256 prefix `e096183159f8`.
- Three Results: 14 pages, SHA-256 `53cbfa8ccf6f732b13670206f3a8c25627390cbb29206f6b1b017163ae3735bf`.
- Additive upstream preview: 30 pages; its patch revalidated against pristine pinned upstream.

## 15. CI run IDs

| PR | Scope | PR CI | PR paper/site | Post-merge CI |
|---:|---|---:|---:|---:|
| #19 | exact pooled frontier | `29793343243` | `29793343234` | `29793437945` |
| #21 | Three Results synthesis | `29794931024` | `29794931026` | `29795041418` |
| #23 | alignment relaxation | `29796343151` | `29796343110` | `29796429926` |
| #25 | DD-002 robustness | `29797737821` | `29797737785` | `29797810807` |
| #27 | DD-003 heterogeneous sources | `29798934183` | `29798934209` | `29798998333` |
| #29 | Actions refresh | `29799265491` | `29799265526` | `29799347668` |
| #30 | Python floors | `29799456223` | not path-triggered | `29799522972` |
| #31 | mypy 2 | `29799629897` | not path-triggered | `29799696893` |

All listed runs succeeded. Actions-refresh configuration jobs `29799350447` and `29799350523` also succeeded.

## 16. Pages run IDs

Post-merge Pages runs succeeded for #19 `29793437954`, #21 `29795041429`, #23 `29796429904`, #25 `29797810786`, #27 `29798998329`, #29 `29799347666`, #30 `29799522952`, and #31 `29799696878`.

## 17. Live route checks

Final smoke testing returned HTTP 200 for all eleven checked routes:

- `/distributed-discovery/`
- `/distributed-discovery/foundations.html`
- `/distributed-discovery/results.html`
- `/distributed-discovery/open-problems.html`
- `/distributed-discovery/applications.html`
- `/distributed-discovery/data/canonical.json`
- `/distributed-discovery/data/results.json`
- `/distributed-discovery/data/claims.yml`
- `/distributed-discovery/data/studies.json`
- `/distributed-discovery/styles.css`
- `/distributed-discovery/site.js`

The live `results.json` exactly matches all four continuation run IDs, `325089/390625`, the 839-network count, and heterogeneous values `3/4` and `2/3`.

## 18. Issues created and closed

Continuation issues #18, #20, #22, #24, #26, and #28 are closed. Settings issue #32 remains open by design. Final-handoff issue #33 closes when the documentation PR merges. Earlier research issues #6, #7, #9, #10, and #11 are closed; queued DD-007 issue #8 remains open.

## 19. Pull requests created and merged

Research/synthesis PRs #19, #21, #23, #25, and #27 and maintenance PRs #29, #30, and #31 were reviewed and squash-merged. Their merge commits are respectively `8d63201`, `007dc15`, `df35f80`, `993b089`, `4a8f53e`, `03290fa`, `d043a43`, and `fa2fd5a`. Public/MIT and A–E integration remain in PRs #12–#17. The documentation-only final handoff is the sole remaining integration PR for this program.

## 20. Dependency PR disposition

Stale conflicted Dependabot PRs #1–#5 are closed, each with a replacement explanation. PR #29 updates checkout to v7, setup-uv to immutable v8.3.2, Pages actions to current majors, and groups future minor/patch updates while leaving majors separate. PR #30 raises the already-resolved PyYAML and types-jsonschema floors with no resolved-version change. PR #31 upgrades mypy 1.20.2 to 2.3.0 and adds ast-serialize 0.6.0; standard and native parsers pass strict checking without suppressions. The lock resolves 22 packages and is current for the declared constraints.

## 21. Settings status

The single authorized attempt ran:

`uv run --no-editable python scripts/setup_github.py --apply --repo yoheinakajima/distributed-discovery`

Local validation found 23 labels, six milestones, and five de-duplicated issue drafts. The first `gh repo view` call failed with exit status 4 because GitHub CLI has no usable authentication, so no setting changed and no retry was made. Issue #32 records the exact token permissions and resume API/commands for labels, milestones, homepage, and the safe `main` ruleset.

## 22. Verified claims

The 11 `verified` claims include upstream facts, bounded censuses, the exact canonical interval before closure, the alignment theorem, and the exact potential-game characterization. Status is claim-specific; no paper-wide peer-review or publication status is implied.

## 23. Independently reproduced claims

The 19 independently reproduced claims cover canonical benchmark quantities, DD-001 tiny optima/signatures/counterexamples, DD-003 homogeneous counts/nulls/scalar counterexamples, the exact canonical optimum, the six-rule selection catalogue, and the colored-source census/counterexample/classification. Independent checks use materially separate enumeration, reconstruction, or Bellman verification paths.

## 24. Certified lower bounds

- Canonical DD-001: feasible direct policy `325089/390625`.
- Finite role witness `(3,2,2/5)`: exact unrestricted optimum `7/10`, exceeding direct `16/25`.
- All lower-bound witnesses are reevaluated exactly; heuristic coordinate ascent is not used as the canonical proof.

## 25. Certified upper bounds

- Canonical DD-001 alignment upper bound: `325089/390625`.
- Superseded but still valid pooled organizational upper bound: `860391662035297/1001129150390625`.
- The alignment theorem applies to the symmetric-report frozen model; it is not an arbitrary-team universal law.

## 26. Certified intervals

- Current canonical private-team interval: `[325089/390625, 325089/390625]`.
- Prior pooled interval: `[325089/390625, 860391662035297/1001129150390625]`, valid but superseded for the frozen canonical optimum.

## 27. Numerical findings

DD-C-0010 and DD-C-0022 remain `checked`: expected-distinct-action diagnostics and coordinate-ascent convergence are useful numerical observations but not promoted to exact general results. The canonical coordinate search found direct as a fixed point and 17 additional starts converged to it; the Bellman certificate, not this search, proves optimality.

## 28. Negative and bounded-null results

- The homogeneous 51-graph DD-003 census contains ten matched complete-pairwise-moment groups and zero within-group discovery differences: a bounded null, not a theorem.
- The alignment relaxation is loose at `(3,2,0)`: `1` versus exact `11/12`.
- Five of six DD-002 evaluations do not reproduce the known selected reversal; best-pure and planner have zero harmful refinements in all 45 pairs.
- Mypy 2.3 produced no new diagnostics under either parser; no compatibility silencing was needed.

## 29. Refuted conjectures

- Direct clue-following is not generally private-team optimal.
- The informative DD-001 three-family phase result does not extend to all `p`.
- “Distributed Discovery” is not a unique phrase or field-name claim.
- Mean pair agreement and source HHI are insufficient in the homogeneous graph census.
- Complete first/pairwise scalar-report moments are insufficient in the registered heterogeneous colored class.

## 30. Open conjectures and questions

- Characterize when the alignment-preserving relaxation is tight and which cross-target constraints strengthen it.
- Determine DD-002 robustness under randomized disclosure, general asymmetric mixed equilibria, and other learning/selection processes.
- Extend DD-003 to continuous accuracies, dependent source laws, asymmetric priors, larger graph classes, or higher-order report laws under new bounded registrations.
- DD-004 through DD-007 remain specified but unexecuted; issue #8 queues only the DD-007 schema.

## 31. Technical debt

- Tectonic 0.16.9 and Poppler remain system-level paper dependencies outside `uv`.
- The static site has automated semantic, link, contrast, and no-tracking checks but no browser-based accessibility audit.
- The upstream patch validator's parallel Tectonic log can reorder two `Writing` lines; final validation passed and the incidental tracked log reorder was restored.
- Settings manifests are validated offline but not applied.

## 32. Exact blockers

Only issue #32 is blocked: the current GitHub CLI session lacks authentication with Issues-write, Metadata-read, and Administration-write authority. The connected app and SSH remain sufficient for issues, PRs, merges, and Git transport.

## 33. Exact next task

Resolve issue #32 when settings-capable authentication is intentionally supplied. Research expansion should otherwise begin with a new bounded issue and resource/certificate plan, not by silently enlarging any completed census.

## 34. Exact resume command

`git switch main && git pull --ff-only origin main && make verify`

For settings specifically, the next authorized command is `gh auth login`; after successful authentication, follow issue #32.

## 35. Commit SHAs

Continuation merge SHAs: `8d63201cb3b6633c873494af2ea21402db8752d6`, `007dc15b89f6d7e98e572d1b164f057c7c38c964`, `df35f80273f106ef86f623c4676fe2a58757b6ad`, `993b0899421d446f61348a513d2630e0f424e336`, `4a8f53e90b1ffea233de5b377ba970566d92d670`, `03290fa66a18c19a76f90f7c9dab5ef56a005f7d`, `d043a438c616e793c00908fa54a7b818466eec82`, and `fa2fd5a473810dc00a5f8b483b4f196a6522f7be`.

Primary evidence commits are embedded in immutable run IDs/manifests; the four continuation runs start from `8e4b55e2`, `358cb1eb`, `73a85c71`, and `84238b76`.

## 36. Pull-request URLs and next file

- `https://github.com/yoheinakajima/distributed-discovery/pull/19`
- `https://github.com/yoheinakajima/distributed-discovery/pull/21`
- `https://github.com/yoheinakajima/distributed-discovery/pull/23`
- `https://github.com/yoheinakajima/distributed-discovery/pull/25`
- `https://github.com/yoheinakajima/distributed-discovery/pull/27`
- `https://github.com/yoheinakajima/distributed-discovery/pull/29`
- `https://github.com/yoheinakajima/distributed-discovery/pull/30`
- `https://github.com/yoheinakajima/distributed-discovery/pull/31`
- `https://github.com/yoheinakajima/distributed-discovery/pull/34` — documentation-only final handoff

The exact operational next file is `docs/github-setup.md`, governed by issue #32. The exact next research planning file is `studies/DD-001/PLAN.md` if the project owner chooses to pursue a stronger alignment hierarchy.
