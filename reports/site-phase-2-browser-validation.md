# Phase 2 site browser validation

Local acceptance date: 2026-07-22. Surface: generated `site/dist`.

The 79-route build passed its structural validator. Browser checks covered the
new Start Here and Methods routes, Program, Papers, Claims, and a representative
Threshold Lab at 1440×900 and 390×844.

- exactly one H1 and five primary-navigation links appeared on checked routes;
- Start Here preserved the fixed three-result order, scope limitations,
  evidence labels, statuses, and continuation links;
- Program displayed Phase 1 completion, the Phase 2 hold, DiscoveryBench Agents
  v1 as the next registration, and Reliable Discovery as deferred;
- Papers displayed seven artifacts with the expected four working-paper, one
  research-note, and two synthesis-note labels;
- Claims displayed 110 separate prominence badges without changing evidence
  status;
- document and body scroll widths matched each tested viewport;
- the mobile Lab limited wide visual and table content to deliberate
  `overflow-x: auto` regions without page-level horizontal overflow;
- browser console warnings and errors were empty on every checked route;
- the stylesheet contains visible focus rules and a reduced-motion media rule;
- interactive routes retain complete `<noscript>` tables or equivalent static
  fallbacks, verified by the build validator and source inspection.

The checked pages contain no analytics, tracking, form submission, account,
cookie, telemetry, or remote runtime service. This is internal browser QA, not
external validation.
