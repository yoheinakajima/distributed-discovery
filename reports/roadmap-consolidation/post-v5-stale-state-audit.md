# Post-V5 live-state and stale-state audit

Audit time: `2026-07-23T00:00:13Z`  
Issue: `#158`  
Base main: `a04100e2c8ae10936f972f86a6080a913d64195b`  
Evidence class: repository/public-state audit; no scientific result

## Verified live state

- Local `main`, `origin/main`, SSH `main`, and GitHub default branch agree at
  `a04100e2c8ae10936f972f86a6080a913d64195b`. The user-provided expected SHA
  is exact; no base-main delta requires reconciliation.
- No pull request is open. Issue #32 is the sole pre-existing open issue and is
  settings-only. PRs #155, #156, and #157 are merged; issue #153 is closed.
- Current main CI `29966091467` and Pages `29966091515` completed successfully.
- The live root, Program, Research, Findings, Labs, Papers, Information Sharing
  Frontier detail, and PDF routes return HTTP 200. The live PDF SHA-256 is
  `2f8b68d5a690e6369e4c3236313eb93f060bfbe73ec531903c090f6ec6f8b6a1`.
- Inventory: 247 tests; 110 claims; 51 manifests with 48 passing; 26 studies;
  seven validated project papers totaling 115 pages; 77 HTML routes; 85 public
  data files; 18 Labs; 23 checksum-covered downloads.
- Program V5 run and claim ownership is DD-019
  `20260722T084145Z_DD-019_a77bb786_04a5e9f0c5` / DD-C-0089–0091; DD-020
  `20260722T142551Z_DD-020_3854fff6_37c11a850a` / DD-C-0092–0096; DD-021
  `20260722T185924Z_DD-021_3cdbbc40_2fea269a9a` / DD-C-0097–0103; and DD-022
  `20260722T210334Z_DD-022_2376d5b7_ad67765ca8` / DD-C-0104–0110.
- Canonical upstream remains clean/read-only at
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`.
- ActiveGraph was inspected read-only at
  `b1963fc85f53522726532b159ee377f2dba94940`. Its holdout records frozen
  importer SHA-256
  `b9a0f4409e3aa53072f391f279cf33dbc11041f5755534177368386551ea79df`;
  adoption v3 permits optional advisory structural relationship auditing only,
  retains canonical Git authority, and disables required evidence-audit CI.

Unrelated untracked duplicate audit files exist in both the canonical primary
worktree and ActiveGraph. They are recorded, not removed, staged, or modified.

## Frozen pre-change checksums

| Object | Pre-change value |
| --- | --- |
| Claims ledger Git blob | `8f262daf3aa43f2505d415988d8eca6f0ecd3a42` |
| Manifest-set SHA-256 | `dc7140a6bd36e931dc96c0e9eacff2fd734d1d0b69aa6848e20603a5ef2e3163` |
| Passing-run-list SHA-256 | `0af5fcc5f049b66a53763a6ccd49107c0ffa27033ac2b947a3f8043b32d18442` |
| `results/verified` Git-tree-list SHA-256 | `50d83d4488a33218f949c520bfa0da9c765ed37677aa3900062b158afac64434` |
| Study-directory-set SHA-256 | `05c09c15029998698127b5ef68fc0e1df86b6951b6e4feb602db60601bee5585` |
| Route-registry SHA-256 | `a551b68b644f2974d9870f954c93ea2990550892088491640f89ef485f1bc080` |
| Download-manifest SHA-256 | `e26726fb092762c5d2e5acc495fce74ae6835fb88ad0bdd7884487487e949584` |

Validated project PDF SHA-256 values:

| Paper | SHA-256 |
| --- | --- |
| Foundations | `e096183159f8c016f116b1a97fc0721948bbee2aca6dd1ae251d0a2af95a32e4` |
| Three Results | `40506068a03e6e7ff0dd8c20751b792a9e669e8fd788005dff1c58540131206f` |
| Discovery Institutions | `9bad1e7aaebd07851613f7f38a5c1a3654ca78363cc95f092f5b97bf0f9cee7b` |
| Common-Source Trap | `c997bba31c021bd799f2b3a561e8e558a1334f844aa87a448ade10319dac2ad3` |
| Incentive to Ignore | `ee9e27f741d25a9597994f18caf2bf406098db7aca4d2ed067a7a011f64be250` |
| Threshold Discovery | `b38bb30f3ce63889526a092d78dd3f202d3beb54178bcdc272aba85c321b1995` |
| Information Sharing Frontier | `2f8b68d5a690e6369e4c3236313eb93f060bfbe73ec531903c090f6ec6f8b6a1` |

## Match classification

Class 1 is current-facing stale state and must be corrected. Class 2 is dated
historical evidence and remains unchanged. Class 3 is valid historical evidence
that needs a current-status/supersession note. Class 4 is a valid future
boundary and remains, with wording clarified only if it can be mistaken for
current authorization.

| Path | Matched or equivalent language | Class | Intended treatment |
| --- | --- | ---: | --- |
| `README.md` | “candidate for planning only; no manuscript ... authorized” | 1 | Replace with the deployed 26-page working-paper status and retain no-submission/no-DOI boundaries. |
| `papers/README.md` | “Six project-authored PDFs”; “future ... paper”; “No manuscript expansion” | 1 | Add the seventh paper, 115-page inventory, current PDF hash/status, and deployed ownership. |
| `docs/current-roadmap.md` | “future ... theorem-family paper” and old V5 execution-order prose | 1 | Make the next action the post-V5 decision gate and then a separately authorized registration; retain later portfolio directions. |
| `docs/research-roadmap.md` | admitted candidate but “No manuscript ... authorized” | 1 | Record the completed/deployed working paper and current gate. |
| `docs/theorem-roadmap.md` | “planning only; no manuscript ... authorized” | 1 | Reconcile Program V5 completion and the chosen next-program gate while preserving the long-horizon portfolio. |
| `docs/program-v5.md` | “future ... paper”; issue #153 “planning only” | 1 | Mark DD-019–DD-022 and the working paper complete/deployed; no further V5 study is implied. |
| `docs/publication-architecture.md` | Information Sharing Frontier “planning artifacts only”; DD-020 future ownership | 1 | Represent a validated deployed working paper with no submission/DOI/review authority. |
| `docs/paper-family-map.yml` | `information-sharing-frontier-paper-admitted-planning-only` | 1 | Record deployed working-paper state and retain selection/centralized limitations. |
| `plans/MASTER_EXEC_PLAN.md` | historical headings still say “Active continuation — post-DD-021” | 3 | Add a new opening active continuation and label the retained earlier block superseded/historical; do not rewrite execution history. |
| `plans/DD022_COORDINATION_FREE_POSITIVE_SHARING.md` | “paper-admission ... merge pending”; unchecked merge item | 1 | Record the completed admission, paper build, PRs #155–#157, and deployed status without altering DD-022 evidence. |
| `reports/project-status.md` | current summary followed by an obsolete DD-021 paper hold | 1 | Remove the false current hold; keep older Program V4 acceptance explicitly historical. |
| `reports/final-handoff.md` | title “through DD-021”; 235/103/50/25/six/74/81/17/22 inventory; future paper | 1 | Rewrite opening as a true post-V5 handoff; preserve Program V4 and earlier records under historical headings. |
| `studies/index.md` | paper admission still described as no manuscript authority | 1 | Add the deployed theorem-family paper relationship and require a future bounded registration for new research. |
| `studies/DD-021-general-sharing-frontier/status.yml` | next action preserves “post-DD-021 paper-gate hold” | 1 | Preserve evidence and replace the resolved hold with deployed-paper/current-gate context. |
| `studies/DD-021-general-sharing-frontier/report.md` | “post-merge editorial gate must decide” | 3 | Add a current-status note; retain the dated next-target paragraph as historical interpretation. |
| `site/README.md` | 72 routes, 71 data, 17 Labs, 22 downloads; PR #140 current surface | 1 | Reconcile to 77/85/18/23 and deployed Information Sharing Frontier relationships. |
| `src/distributed_discovery/site/build.py` | Program page ends at DD-021, says future paper/editorial gate/no manuscript | 1 | Replace with the theorem spine, DD-022 positive/failure adjacency, centralized boundary, paper/synthesis/evidence links, and next gate. |
| `tests/integration/test_site_build.py` | asserts “future ... paper” and “No manuscript expansion” | 1 | Replace with focused deployed-paper, theorem-spine, status, relationship, and limitation assertions. |
| `synthesis/.../prospectus.md` | repeated “future Information Sharing Frontier paper”; open General Sharing Frontier | 1 | Route DD-019–DD-022 to the deployed paper; mark the static block-sharing information frontier mature; retain implementation/reliability/provenance gates as open. |
| `synthesis/.../chapter-map.yml` | chapter stops at DD-020; future paper; General Sharing Frontier missing | 1 | Add DD-021/DD-022, full claim ownership, deployed paper, and the open implementation link. |
| `synthesis/.../claim-map.yml` | attention/sharing range ends DD-C-0096 | 1 | Extend through DD-C-0110 with exact primary studies. |
| `synthesis/.../source-map.yml` | only DD-020 and “future ... paper” | 1 | Record all four completed studies/runs and deployed theorem-family paper ownership. |
| `synthesis/.../maturity-map.yml` | open General Sharing/Recovery/coordination-free gates | 1 | Close those declared V5 gates and distinguish decentralized recovery/equilibrium robustness from Reliable Discovery and Provenance. |
| `synthesis/.../status.yml` | current gate awaits General Sharing and Reliable Discovery | 1 | Point to issue #158's next-program editorial decision; no study ID. |
| `reports/editorial/information-sharing-frontier-paper-admission.md` | planning-only admission at its historical date | 3 | Add a concise supersession note; do not rewrite the admission decision. |
| `reports/editorial/information-sharing-frontier-paper-gate.md` | DD-019–DD-021 hold and six-paper/74-route-era counts | 2 | Preserve unchanged; its existing header already identifies the historical resolved hold. |
| `reports/editorial/incentive-to-ignore-theorem-gate.md` | “future Information Sharing Frontier paper” | 2 | Preserve dated editorial evidence; current maps supply the updated status. |
| `reports/editorial/information-sharing-frontier-paper-admission.md` | 244 tests, six papers, 76 routes, 22 downloads | 2 | Preserve as the admission-gate inventory after adding the supersession note. |
| `reports/program-v5-continuation-final-acceptance.md` | 224 tests, six papers, 72 routes, 17 Labs, 22 downloads | 2 | Preserve dated pre-DD-021 acceptance evidence. |
| `reports/dd020-public-integration-validation.md` | 72 routes, 71 data, 17 Labs, 22 downloads | 2 | Preserve dated DD-020 deployment evidence. |
| `CHANGELOG.md` | historical 224/96/49/six/72/71/17/22 entry | 2 | Preserve history; add a new post-V5 consolidation entry only at closeout if warranted. |
| `plans/MASTER_EXEC_PLAN.md` historical blocks | “deployment pending”, six-paper and older inventory counts | 2 | Preserve execution history after adding clear current/superseded labels at the top. |
| `docs/research-governance.md` | “candidate only when ...” | 4 | Preserve: this is the general admission rule, not stale paper status. |
| `docs/theorem-roadmap.md` | Reliable Discovery and Provenance remain open | 4 | Preserve both directions; update only which program is recommended next. |
| paper metadata/README/ownership | working paper, no DOI/submission/review/novelty | 4 | Preserve unchanged; these are current publication boundaries. |

## Audit conclusion

The stale state is editorial and presentational, not scientific. No mismatch
was found in DD-019–DD-022 immutable runs, claim ownership, the 26-page PDF, or
the live deployment. Correction therefore requires targeted current-facing
copy/map/builder/test changes plus explicit historical supersession notes; a
bulk replacement would destroy valid dated evidence and is prohibited.
