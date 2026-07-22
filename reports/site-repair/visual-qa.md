# Site repair visual QA

Date: 2026-07-22. Baseline: `main` at `8ac0700`.

## Capture matrix

- Before: 60 screenshots in `reports/site-repair/before/`.
- After: 60 screenshots in `reports/site-repair/after/`.
- Viewports: 390×844, 768×1024, 1280×900, and 1440×1000.
- Routes: Findings; DD-012 and DD-016 study pages; Labs index; Sequential, Coverage, Mechanisms, Audit, Evidence Acquisition, Atlas, Threshold, Equilibrium Selection, and Dynamic Attention Labs; Threshold Discovery paper; benchmark results.

## Findings layout measurement

| Width | Visible findings | Stacks | Intersecting pairs before | Intersecting pairs after | Document overflow after |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 390 | 10 | 6 | 0 | 0 | 0 |
| 768 | 10 | 6 | 7 | 0 | 0 |
| 1280 | 10 | 6 | 7 | 0 | 0 |
| 1440 | 10 | 6 | 7 | 0 | 0 |

The after page contains one instance of each registered finding. All additions use `.finding-stack`; the duplicate DD-013 one-reader card and chronological Program V3/V5 piles are gone.

## Lab review

- Sequential places controls, exact result cards, timeline, comparison bars, takeaway, and technical fallback in a readable order.
- Coverage shows named portfolio rules and manual selections rather than a scenario index.
- Mechanisms exposes observability, implementation margins, discovery, and budget limits.
- Audit keeps the synthetic-only boundary prominent and visualizes calibration outputs.
- Evidence Acquisition shows equilibrium/planner source counts, trap status, and welfare consequences.
- Atlas uses named architectures and components, reports invalid combinations explicitly, and highlights the selected Pareto point.
- Threshold displays percentages and expected counts as primary values, exact fractions as secondary copyable values, and a selected phase-chart point. At 390 px the chart scrolls within its own container; document overflow remains zero.

## Responsive and visual result

Pass. Required pages are contained at all four viewports; long titles wrap without collision; exact fractions no longer dominate Threshold; the five-item header collapses to one Menu control at mobile width. The related-resource panels remain below the primary content and do not displace Lab outputs.
