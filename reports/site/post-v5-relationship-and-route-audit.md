# Post-V5 relationship and route audit

Date: `2026-07-22` (America/Los_Angeles)
Scope: presentation and navigation only; no study, claim, run, paper artifact,
or scientific status change.

## Route matrix

| Route | Required forward content | Required reverse relationship | Required marker |
| --- | --- | --- | --- |
| `/program.html#information-sharing-frontier` | DD-019–DD-022 theorem spine, positive result, adjacent every-equilibrium limitation, centralized boundary, next gate | links to four studies, working paper, theorem-spine source | `From information to implemented discovery` |
| `/research/dd-019.html` | scoped study and evidence | paper, Program/synthesis anchor, related DD-020–DD-022, claim, run, Lab, exact data | `Where this work appears` |
| `/research/dd-020.html` | scoped study and evidence | same family reverse edges | `DD-C-0092` |
| `/research/dd-021.html` | centralized recovery scope | same family reverse edges | `DD-C-0098` |
| `/research/dd-022.html` | selected positive and negative scopes | same family reverse edges | `DD-C-0109` |
| `/results.html` | DD-020–DD-022 finding cards | each relevant card links into the sharing family | `coordination-free-selection-boundary` |
| `/labs/incremental-sharing.html` | immutable DD-019/DD-020 outputs | study, paper, Program/synthesis, claims, runs, exact data | `Evidence runs` |
| `/labs/general-sharing-frontier.html` | immutable DD-021 outputs | study, paper, Program/synthesis, claims, run, exact data | `Public data` |
| `/labs/coordination-free-positive-sharing.html` | immutable DD-022 outputs | study, paper, Program/synthesis, claims, run, exact data | `Evidence runs` |
| `/publications/information-sharing-frontier.html` | validated working-paper status and download | DD-019–DD-022, Program/synthesis, Findings, Labs, DD-C-0089–DD-C-0110, four runs, exact data | `Related research` |
| `/claims.html` and `/evidence.html` | stable claim/run records | reached from every scoped relationship panel | claim IDs and run IDs |

The relationship registry remains one machine-readable source at
`/data/relations.json`. The `sharing-frontier` family supplies the fragment
anchor so every family link terminates at the relevant living-synthesis section
of the existing Program page. No new route or global-navigation item is added.

## Reverse-link expectations

- Each DD-019–DD-022 study page links to the Information Sharing Frontier
  publication and `program.html#information-sharing-frontier`.
- The publication page links back to all four studies, all routed Findings,
  all three relevant Labs, all 22 claims, all four immutable runs, and all
  registered public exact-data files.
- Each routed Finding and Lab links back to its owning study/studies, working
  paper, Program/synthesis anchor, claims, runs, and data where present.
- The Program page links to all four studies, the working paper, and the
  repository theorem spine.

## Content and status markers

The exact positive marker is “DD-022 proves an exact interval.” It is
immediately followed by “does not hold across every equilibrium” and the
centralized posterior top-`L` limitation. The page says Program V5 and the
working paper are complete; it does not state submission, DOI, release,
acceptance, peer review, or a new research authorization.

## Viewport and interaction coverage

Automated site validation covers internal links/fragments, heading order,
unique IDs, captions, local assets, no tracking, no remote runtime, focus
visibility, reduced motion, no-JavaScript fallbacks, and download checksums.
Manual browser QA covers desktop and `390` CSS pixels on the root, Program,
Research, Results, Labs, Papers, publication, four study, three Lab, Claims,
and Evidence routes. Checks include semantic headings, exact status wording,
keyboard focus, link destinations, table internal scrolling, body-width
containment, and console errors.

## Intentionally absent relationships

- DD-019 has no separate Signal Geometry Lab; its immutable channel/profile
  evidence is intentionally exposed through the Incremental Sharing Lab and
  exact data.
- The living synthesis has no separate public route. Its public anchor is the
  existing Program section, with repository source links for the prospectus,
  maps, and theorem spine.
- The paper has no DOI, journal, submission, release, acceptance, peer-review,
  citation-metric, or external-runtime relationship.
- Reliable Discovery, Missing Provenance, and the recommended bridge have no
  study/Lab/paper edges because none is registered.

## Local validation result

Pass. The focused integration test reports `2 passed`; `make site` reports 77
pages and 26 studies. The generated build report records 110 claims, 48 passing
runs, seven publications, internal-link/fragment, public-safety, download-
checksum, local-asset, no-JavaScript fallback, no-tracking, accessibility, and
semantic-structure checks as true. The relation graph has 26 study records, 15
Findings, 18 Labs, seven papers, 24 benchmark tasks, 110 claims, and 38 routed
runs. A separate marker audit passes all ten repaired Program/study/paper/
Finding/Lab routes in the matrix.

## Deployed acceptance

Pass. Branch CI `29969577304` and paper/site build `29969577290` passed; PR
#159 squash-merged as `8ea3495ccfeacb2c0b4d408d70df1f39718c1a02`;
post-merge CI `29969705255` and Pages `29969705284` passed. Every required live
route plus `data/relations.json` returned HTTP 200. Desktop and 390-pixel
browser QA passed all 16 routes with one H1, valid heading progression, no
page-width overflow, required relationship/status markers and destinations,
visible keyboard focus, and no console warnings or errors. The live paper PDF
retained SHA-256
`2f8b68d5a690e6369e4c3236313eb93f060bfbe73ec531903c090f6ec6f8b6a1`.
