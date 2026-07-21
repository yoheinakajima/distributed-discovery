# UI refresh visual QA

Validated 2026-07-21 against the local generated site after rebasing on
`origin/main` at `9bc1a61ee688ba9fce3504c646c6fab540358447`. This is a
presentation review; it does not change or reinterpret research evidence.

## Capture matrix

Nine representative routes were captured before and after the refresh at
390×844, 768×1024, 1280×900, and 1440×1000: Home, Research, DD-013, Results,
Labs, Audience Lab, Papers, benchmark results, and the experiment kit. The 36
baseline captures are in `before/`; the 36 current captures are in `after/`.
Both directories include machine-readable viewport metrics.

The current matrix has:

- zero document-level horizontal overflows;
- one H1 on every capture;
- one header navigation containing exactly five primary destinations on every
  route;
- no raw machine status used as a standalone visible label; and
- internally scrolling data regions where the table is wider than the page.

## Defects corrected

| Baseline defect | Correction | Verification |
|---|---|---|
| Two always-visible global navigation layers | One five-item global nav; utilities moved to a structured footer | DOM metrics on all 36 captures |
| Mobile header wrapped into several competing rows | Native `details`/`summary` menu with a full static-HTML fallback | 390 px menu opens to five links; document width remains 390 px |
| Homepage led with repository inventory | Paradox, public descriptor, canonical comparison, process, findings, and clear depth choices now lead | Visual review at all four widths |
| Serif UI and oversized standard headings | Sans-serif UI, bounded display scale, restrained serif only for the homepage hook | Visual review of long titles and cards |
| Fixed card and statistic columns | `auto-fit` grids with content-driven minimums | 768 px and 390 px captures |
| Seven-column process rail | Six-step wrapping grid; single-column sequence on phones | Homepage captures |
| Tables scrolled without an explicit cue | Focusable labelled scroll regions, captions, sticky headers, zebra/hover treatment, and a visible hint | Benchmark and Audience Lab mobile checks |
| Raw phase/evidence strings led public cards | Human-readable status labels; formal values retained in Technical details | Research, study, Results, and Papers review |
| Unequal cards left actions floating mid-card | Flex-column cards keep actions at a consistent lower edge | Labs and Research desktop captures |
| Nested pages lacked orientation | Breadcrumb landmark plus local benchmark/experiment navigation | DD-013, Lab, benchmark, and experiment captures |

## Difficult-content review

- Long study titles and questions wrap without clipping at 390 px.
- Study IDs, run IDs, hashes, fractions, and metric vectors use wrapping or
  deliberate internal scrolling rather than widening the document.
- The 672 px benchmark table is contained in a 364 px focusable region at the
  390 px viewport; its caption and “Scroll horizontally” cue remain visible.
- Audience Lab controls stack at 390 px and its exact tables remain available
  in scroll regions.
- The experiment-kit warning remains prominent and unambiguously says the
  package is synthetic and has no participants.
- Unequal card counts and copy lengths were reviewed on Research, Results, and
  Labs at tablet and desktop widths.

## Interaction review

- Research search `Audience` plus the `Key results` filter leaves one matching
  study and the filter reports `aria-pressed="true"`.
- Benchmark task `DB-G12` leaves one exact compatible row and updates the polite
  live region.
- Experiment scenario `S8-learning` leaves 48 synthetic power rows and updates
  the polite live region.
- Audience Lab initially shows one binding row and one feasible garbling row;
  Conditional Attention Lab initially shows one registered exact profile.
- At 390 px the menu is collapsed on load, opens to five links, and introduces
  no document overflow.
- A focused native menu summary renders a 3 px blue outline with a 3 px offset.

## Color and motion

The light and dark token palettes were inspected at the stylesheet level. Key
contrast ratios against the page background are: light primary 15.45:1,
secondary 7.80:1, muted 4.54:1, accent 5.96:1, and focus 4.67:1; dark primary
16.97:1, secondary 11.69:1, muted 7.16:1, accent 10.58:1, and focus 7.86:1.
These calculations are bounded to the named solid-color token pairs, not a full
WCAG conformance claim. Reduced-motion mode disables smooth scrolling and
transitions.

## Outcome

No remaining blocking visual defect was found in the required route/viewport
matrix. The wide scientific tables intentionally remain horizontally
scrollable on small screens; this preserves every value while keeping the page
itself responsive.
