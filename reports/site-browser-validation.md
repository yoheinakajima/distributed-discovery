# Research-library browser validation

Revalidated 2026-07-21 UTC after the public-site refresh against a local
`site/dist` build served over HTTP. This is a bounded practical browser check,
not a claim of WCAG conformance.

| Check | Result |
|---|---|
| Responsive capture matrix | 36 captures across nine routes at 390×844, 768×1024, 1280×900, and 1440×1000; zero document-level overflow and one H1 per capture |
| Global navigation | One header navigation with Home, Research, Results, Labs, and Papers on every captured route; nested pages mark their parent current |
| Mobile 390 × 844 home route | Native menu is initially collapsed, opens to exactly five links, and leaves document width at 390 px |
| Keyboard/focus | Native menu summary shows a 3 px blue focus outline with a 3 px offset; a skip-to-content link precedes the header |
| Script independence | Generated HTML contains all study cards, claims, evidence summaries, and publication links before the tiny enhancement script runs |
| Routes | `research.html`, nested `research/dd-004.html`, `publications.html`, and the two PDF links load from the local build |
| Semantic/accessibility checks | Generated validation requires header, navigation, main, footer, unique leading H1, descriptions, resolved internal links/fragments, and no local-path/secret-like text |
| Motion | The stylesheet declares a `prefers-reduced-motion` override for smooth scrolling |
| DiscoveryBench desktop | The Lab exposes one labelled native task selector, one H1, a polite live result count, an accessible captioned result table, local CSS/JS only, and no console warnings or errors |
| DiscoveryBench filter | Selecting `DB-G12` leaves exactly its one compatible result row visible and updates the live status text |
| DiscoveryBench mobile 390 × 844 | Main content fits the viewport; the 672 px result table is intentionally contained in a 364 px labelled scroll region with a visible cue |
| DiscoveryBench no-JS | Generated source contains all 16 exact result rows plus a `noscript` explanation; filtering is optional enhancement only |
| DD-011 experiment kit | Overview and design pages expose one H1, the prominent no-human-data warning, captioned alternative/treatment tables, local CSS/JS only, and no console warnings or errors |
| DD-011 Lab filter | The labelled native scenario selector and polite live region show exactly 48 rows for either `S1-rational` or `S8-learning`, with zero rows from another scenario |
| DD-011 mobile 390 × 844 | Main content remains 350 px wide; the 514 px power table scrolls within its 350 px container and document-level horizontal overflow is zero |
| DD-011 no-JS | Generated source contains all 384 power rows plus a `noscript` explanation; the scenario filter is optional enhancement only |
| DD-008B research route | The generated page loads over HTTP with one H1, ordered H2/H3 hierarchy, both scoped claims, the passing immutable run, all three public-source links, local CSS/JS only, and zero desktop horizontal overflow at 1280 px |
| Common-Source Trap publication | The catalogue exposes four cards and links to the dedicated route; the route has one H1, ordered H2 sections, exact working-paper/no-DOI/no-submission/no-peer-review status, local CSS/JS only, zero document overflow, and a PDF link that returns HTTP 200 |
| Program V2 integrated route sweep | All 15 required DD-008B, DD-010, DD-011, benchmark, experiment-kit, Lab, and paper routes load over HTTP with exactly one H1, ordered headings, local runtime assets only, and zero document-level overflow |
| Program V2 interactive controls | Selecting `DB-G12` shows exactly one compatible benchmark row; selecting `S8-learning` shows exactly 48 power rows and no rows from another scenario; both Labs retain complete no-JavaScript tables |
| Research catalogue controls | Searching `Audience` and selecting `Key results` leaves one visible study and exposes `aria-pressed="true"` |
| DD-013 Audience Lab | Initial registered cell shows one binding and one feasible garbling row with a polite explanatory status |
| DD-014 Conditional Attention Lab | Initial registered cell shows one exact profile and explicitly preserves the all-clues evidence boundary |
| Status presentation | No raw machine status is used as a standalone visible label in the 36-capture route matrix |
| Download integrity | The generated manifest covers every paper, schema, and read-only experiment material in `downloads/`, recording and validating byte length and SHA-256 for each artifact |

The browser check complements the automated site builder tests. It does not test
assistive technology combinations or claim a complete accessibility audit.
