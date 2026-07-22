# DD-021 General Sharing Frontier Lab browser QA

Date: 2026-07-22. Route tested locally:
`labs/general-sharing-frontier.html` from the validated 74-page site build.

## Interactive checks

- The default `M=4,N=3` half-accurate point row rendered percentages and exact
  fractions consistently, including `G_1=87.5% = 7/8`, increment
  `-12.5% = -1/8`, threshold `50% = 1/2`, and `L*=3`.
- Selecting the guaranteed `K=2` shortlist at `M=4,N=2` changed the exact
  output to increment `8.3% = 1/12`, `L*=1`, strict aggregation-dominated
  sharing, and strict aggregation-dominated consensus.
- Exactly one fallback-table row was visible after the selection.
- URL state encoded family, `M`, `N`, channel, `s`, and `L`; Reset restored the
  canonical default and its encoded URL.
- Channel-family changes constrain the parameter list; `K` is visible in the
  shortlist labels. Step and budget options disable beyond `N-1` and
  `min(N,M)` respectively.
- Browser console warnings and errors: none.

## Accessibility and fallback checks

- Native labeled selects and button provide keyboard-operable controls.
- Every chart has an updated accessible name and visible percentage/fraction
  labels. The complete 177-row table is the text alternative and no-JavaScript
  evidence surface.
- Repository validation confirms heading order, unique IDs, captions, local
  assets, no tracking, reduced-motion CSS, visible focus, responsive auto-fit
  layouts, fragments, downloads, and internal links.
- Static source checks cover the 390, 768, 1280, and 1440 CSS breakpoints,
  overflow containment, dark color variables, and reduced motion. The in-app
  browser's advertised viewport override remained at 1280×720 after requesting
  390×844, so this record does not falsely claim a narrow browser screenshot.

The browser did directly verify the substantive interaction and default-width
render. Narrow-width acceptance is based on the same repository responsive
rules and automated site checks because the browser override was ineffective.
