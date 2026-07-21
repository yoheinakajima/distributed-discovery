# Public-site UX audit

Audit completed 2026-07-21 against the 53-route local build from
`a7b622aabc919238b29d452eb7263a1722cbbfe4`. The required route set was rendered
at 390×844, 768×1024, 1280×900, and 1440×1000. This is a presentation audit,
not a scientific review and not a claim of WCAG conformance.

## Executive finding

The site is evidentially careful and structurally sound, but it asks a new reader
to understand the repository before it explains the idea. The public thesis,
canonical paradox, and paths into the work are less prominent than registry
status, counts, exactness language, and provenance. Navigation and typography
compound the problem: two always-visible link rows occupy the header, the serif
body and large display scale make the site read like a long paper, and every
page is constrained to a narrow research-note column even when it contains
tools or wide tables.

The refresh should preserve the current evidence contracts and route set while
reordering the experience: question and consequence first, result and scope
next, technical provenance behind clear disclosure.

## Baseline evidence

- Build: 53 HTML routes, 19 studies, 65 claims, 34 passing runs, four papers.
- Screenshots: 36 captures under `reports/ui-refresh/before/` plus machine-read
  viewport metrics in `metrics.json`.
- Each reviewed page has one H1 and two header navigation regions/layers.
- No reviewed route produced document-level horizontal overflow.
- At 390 px, the Audience Lab tables require internal horizontal scrolling
  (597 px and 409 px content widths inside a 350 px viewport) without a visible
  cue that more columns exist.

## Navigation problems

- The generated shell exposes six primary destinations plus seven utilities in
  a second always-visible row. Thirteen global choices compete before the page
  begins.
- On mobile, both rows wrap; the brand, primary links, and utilities become
  several visually similar lines. The hierarchy between “where am I?” and
  “other repository resources” disappears.
- `Publications` is used where the requested reader-facing label is `Papers`.
- Nested routes do not mark their parent destination as current, so study,
  paper, Lab, benchmark, and experiment pages lose global orientation.
- Breadcrumb-like eyebrow text is visually styled as taxonomy but is not a
  consistent breadcrumb component.
- The footer contains only Home and Repository, so removing the utility row
  requires a structured replacement rather than link deletion.

## Hierarchy problems

- The homepage opens with “A research program in Distributed Discovery” and
  immediately reports ledger/run/publication counts. Neither the short public
  descriptor nor the paradox appears in the first viewport.
- The H1 can reach 4.5rem on standard generated pages; the Audience Lab capture
  demonstrates a title dominating most of the laptop viewport.
- Research cards lead with raw phase strings and finish with claim/run counts.
  The question, human status, and most useful result are not visually primary.
- Study pages place raw registry and evidence strings immediately beneath the
  lede. The reader meets internal workflow vocabulary before “The question.”
- Results are a flat list of studies rather than findings grouped by the reader’s
  question. Claim IDs and phase labels are more prominent than findings.
- Labs are presented as another undifferentiated card list. Cards do not answer
  what can be changed, what will be seen, or which study supports the Lab.
- Paper checksums are foregrounded in catalogue cards, while purpose and status
  are missing or secondary.

## Typography problems

- `body` uses a serif stack at 1.08rem everywhere, including navigation-adjacent
  prose, controls, cards, and tables. This blurs the difference between editorial
  explanation and application UI.
- H1 uses `clamp(2.5rem, 7vw, 4.5rem)` and standard page titles have no separate
  generated-shell constraint. Long study and Lab titles become oversized.
- Uppercase eyebrow text is useful for context but overused for raw phases,
  claim IDs, navigation context, and card labels.
- Monospace IDs wrap safely, but hashes and JSON vectors remain dense and
  visually compete with their explanation.

## Grid and overflow problems

- `.grid-2`, `.result-grid`, and `.stats` use fixed columns, producing awkward
  pairing and row height when item counts or copy lengths vary.
- The legacy seven-stage `.pipeline` forces a seven-column minimum and internal
  horizontal scroll; arrows are positioned for one horizontal row only.
- `.matrix` is itself a block-level scroll container. Scrolling works, but the
  affordance is invisible, headers are not sticky, and there is no edge cue or
  explicit “scroll to see more” helper.
- Dense JSON metric vectors have no sensible minimum width or summary before the
  full table. Scientific values must remain intact, but their first presentation
  can be clearer.
- The universal 44rem `.narrow` container is suitable for prose, not Labs,
  card catalogues, benchmark matrices, or experiment tables.

## Responsive problems

- The mobile header wraps rather than becoming one coherent disclosure.
- The 768 px screenshots show desktop-style navigation pressure and oversized
  headings before the layout has room to breathe.
- Cards collapse only below 680 px; fixed columns at intermediate widths still
  yield uneven density.
- The pipeline’s only responsive behavior is overflow, not a mobile sequence.
- Touch targets are not consistently near 44 px, especially header utilities,
  filter anchors, and inline control links.

## Copy problems

- Raw public phases such as `complete-bounded-study` appear on primary cards and
  study introductions.
- Evidence strings such as
  `three-verified-theorems-and-independently-reproduced-voluntary-census` appear
  as prose without translation.
- Early labels include “exact golden benchmark,” “golden tasks,” “protocol
  contracts,” “metric registry,” “exact result vectors,” “conditional power,”
  “passing immutable runs,” “evidence boundary,” and “public sources.” They are
  accurate technical vocabulary but poor first-contact language.
- The homepage says what the library contains, not why a group can make a better
  guess and still search worse.
- “Discovery Stack Labs” introduces another synthesis brand where the simpler
  public label “Labs” is sufficient.

## Accessibility problems and strengths

Strengths:

- One H1, ordered headings, header/nav/main/footer landmarks, skip link,
  description metadata, local runtime assets, visible focus, reduced-motion
  handling, captions on the major generated data tables, and complete no-JS Lab
  fallbacks.
- No analytics, tracking, cookie, account, submission, or external runtime.

Problems:

- The second header row carries an accessibility label but is visually a second
  global nav, increasing traversal burden.
- Mobile navigation has no labelled menu disclosure and produces a long wrapped
  sequence before content.
- Research phase anchors are not labelled filters and provide no live result
  count. There is no text search.
- Internal table scrolling is not announced visually; some generated Lab tables
  omit captions.
- Nested routes lack a consistent current-parent state and breadcrumb landmark.
- Status meaning relies partly on internal wording. Color is not the only signal,
  but human-readable status text is required.
- Focus is visible, yet compact inline links and controls do not consistently
  provide touch-sized targets.

## Information-architecture problems

- Foundations and Applications sit beside Research and Results as if all are
  equivalent entry points; Benchmark and Experiment Kit are buried in utility
  navigation despite being important tools.
- The site does not explicitly separate “start here,” findings, studies, tools,
  papers, and technical evidence.
- Claim and run inventories are valuable but appear too close to the primary
  story. They belong in contextual technical details and the footer resource
  index.
- The homepage is a generated study catalogue, duplicating the Research page
  instead of orienting a first-time reader.

## Site-builder technical debt

- `build.py` is 1,312 lines and mixes evidence validation, data copying, page
  shell, navigation, copy, catalogue rendering, Labs, metadata, sitemap, and
  validation.
- Most pages are long inline f-strings, making copy changes risky and difficult
  to review separately from evidence interpolation.
- The five `site/src/*.html` files are no longer consumed by `build()`; their
  old one-row companion navigation and copy can drift from the live generated
  shell. They are legacy prototypes, not templates in the current build path.
- Status display has no central mapping function. Machine phases, registry
  statuses, evidence statuses, and publication statuses are formatted ad hoc.
- `_page()` decides prefix depth with a single slash check, which works for the
  current one-level nested routes but is not a general relative-link helper.
- The validator checks baseline semantics but not one global navigation layer,
  five primary items, table captions everywhere, raw phase leakage, copy-map
  validity, research filters, or responsive-layout contracts.

## High-risk merge-conflict surfaces

- `src/distributed_discovery/site/build.py`
- `site/src/styles.css`
- `site/src/site.js`
- `tests/integration/test_site_build.py`
- Route generation and the `_page()` shell

These files are safe to integrate only while no active research PR changes them.
The UI work must be rebased on current `main` and preserve all newly added
research routes, metadata, evidence links, downloads, and Labs.

## Recommended direction

Use one five-item nav (Home, Research, Results, Labs, Papers), a native mobile
details/summary menu, structured footer utilities, breadcrumbs, sans-serif UI
typography, distinct prose/general/wide containers, responsive auto-fit cards,
a six-step wrapping process sequence, visible table-scroll wrappers, and a
presentation copy/status layer. Put scientific text and exact values behind the
same evidence-loading paths; change only the order, labels, and visual priority
of their presentation.
