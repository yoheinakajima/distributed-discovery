# TreasureBench and Treasure Hunt browser validation

Validation date: 2026-07-23 PDT. Target: local static build served from
`site/dist`.

## Result

Desktop and 390 × 844 browser acceptance passed for `treasurebench.html`,
`treasure-hunt.html`, and the historical `benchmark.html` route.

- TreasureBench and Treasure Hunt each render one H1 with valid H1/H2/H3
  hierarchy.
- The TreasureBench opening visibly names and links the companion.
- The Treasure Hunt opening visibly states “The playable companion to the
  TreasureBench suite.” and links to the formal page.
- Both layouts have document `scrollWidth == innerWidth` at 1280 and 390
  pixels. Wide fallback tables are intentionally contained inside labeled
  horizontal-scroll regions; the document itself does not overflow.
- The companion renders all five modules at 366 pixels wide in the 390-pixel
  viewport, and each select control fits at 332 pixels.
- A declared choice updates its associated registered output.
- Keyboard focus on links and controls is visible with a three-pixel outline.
- The inline map has an accessible title and description.
- The companion has one `noscript` block and complete exact fallback tables for
  every module.
- No form, external script, remote runtime service, analytics integration, or
  cookie UI exists.
- Console warning/error logs are empty on all checked routes.
- Primary navigation remains five items.
- The historical page is HTTP 200, visibly explains the DiscoveryBench alias,
  links to TreasureBench, and publishes the correct canonical URL.

The browser review is presentation acceptance, not user research or external
validation.
