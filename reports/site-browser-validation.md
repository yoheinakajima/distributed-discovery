# Research-library browser validation

Validated 2026-07-20 UTC against a local `site/dist` build served over HTTP.
This is a bounded practical browser check, not a claim of WCAG conformance.

| Check | Result |
|---|---|
| Desktop 1280 × 720 research route | One H1, ordered headings, eight visible study cards, no horizontal overflow |
| Mobile 390 × 844 home route | Primary and secondary navigation available, no horizontal overflow after responsive navigation wrapping |
| Keyboard | The skip-to-content link receives focus via Tab |
| Script independence | Generated HTML contains all study cards, claims, evidence summaries, and publication links before the tiny enhancement script runs |
| Routes | `research.html`, nested `research/dd-004.html`, `publications.html`, and the two PDF links load from the local build |
| Semantic/accessibility checks | Generated validation requires header, navigation, main, footer, unique leading H1, descriptions, resolved internal links/fragments, and no local-path/secret-like text |
| Motion | The stylesheet declares a `prefers-reduced-motion` override for smooth scrolling |

The browser check complements the automated site builder tests. It does not test
assistive technology combinations or claim a complete accessibility audit.
