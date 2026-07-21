# UI refresh accessibility audit

Reviewed 2026-07-21 against the generated local site. This is a bounded manual
and automated audit, not a claim of WCAG conformance or an assistive-technology
certification.

## Structure and orientation

- Every generated route is validated for a unique leading H1 and ordered
  headings.
- The shared shell provides header, one labelled primary navigation, main, and
  footer landmarks.
- Nested routes use an `aria-label="Breadcrumb"` landmark and mark the parent
  primary destination current.
- Benchmark and experiment-kit sections have separate page-local navigation;
  they are not duplicate global navigation.
- A skip-to-content link is present before the header.

## Keyboard and focus

- Links, buttons, inputs, selects, summaries, and focusable table regions use a
  visible 3 px focus outline with a 3 px offset.
- The mobile menu uses native `details` and `summary`, so it remains operable
  without custom keyboard scripting.
- Interactive controls are native labelled inputs/selects. Minimum interactive
  height is 44 px on the compact layouts.
- Reduced-motion preferences disable smooth scrolling and transition effects.

## Labels, status, and announcements

- Research search has a visible label; filter buttons expose `aria-pressed`;
  the result count is a polite live region.
- All Lab filters have visible labels and polite live result messages.
- Machine statuses map to words such as “Completed finite study,” “Active
  research,” and “Planned study.” Raw registry strings remain available only in
  contextual Technical details where needed for provenance.
- Scientific scope is communicated in text, not by color alone.

## Tables and responsive reading

- Every generated table is required to have a caption.
- Wide tables are wrapped in labelled, keyboard-focusable scroll regions with a
  visible horizontal-scroll hint.
- Header cells remain sticky inside a scroll region; row striping and hover are
  supplementary only.
- No tested route widens the document at 390, 768, 1280, or 1440 px.

## Script independence

Generated HTML contains the complete study cards, findings, evidence links,
paper links, benchmark rows, experiment rows, audience rows, and conditional
profiles before JavaScript runs. `noscript` messages explain that all rows
remain available when filtering is unavailable. The mobile navigation is
emitted open in source and collapsed only by the enhancement script, so its
five destinations remain reachable when scripting is disabled.

## Color

Named text/focus token pairs were calculated against the light and dark page
backgrounds. The lowest reviewed pair is light muted text at 4.54:1; the light
focus token is 4.67:1. Dark reviewed pairs range from 7.16:1 to 16.97:1. This
does not cover every composited state or constitute a complete contrast audit.

## Known limits

- No screen-reader/browser combination was tested.
- High-contrast/forced-colors mode was not separately emulated.
- Wide data tables still require horizontal movement on phones by design.
- Dark-mode validation covered token contrast and stylesheet behavior, not a
  second 36-image capture matrix.

Within those limits, no blocking keyboard, semantic, responsive, or no-script
accessibility defect was found.
