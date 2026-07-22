# Findings and Labs baseline audit

Baseline: clean `main` commit `8ac0700`, built locally at `2026-07-22`; 72 HTML routes, 24 studies, 96 claims, and 46 passing manifests. Screenshot matrix: 60 viewport captures across 15 required routes at 390×844, 768×1024, 1280×900, and 1440×1000 in `reports/site-repair/before/`.

## Cross-cutting findings

- Results contains 11 `.finding` elements. At 768, 1280, and 1440 widths, seven intersecting pairs occur: every pair among the four Program V3 findings and the pair of Program V5 findings. At 390 px the mobile single-column rule avoids intersections. Document-level overflow is zero at all four widths.
- The one-reader DD-013 finding appears twice. Program V3 and V5 additions bypass the original one-finding-per-group assumption and are appended as chronological piles.
- Sequential, Coverage, Mechanisms, Audit, Evidence Acquisition, and Atlas share one generic range handler. It updates only a scenario number and sentence; no scientific output changes. Their no-JavaScript fallback contains provenance but no representative result.
- Threshold is data-connected but exposes unformatted exact fractions as the primary card values. At 1280 px the numbers wrap across arbitrary digit chunks and occupy the first visual screen without a comparison graphic or interpretation.
- Study pages link forward to claims, runs, and source files but do not expose generated “Where this work appears” reverse links. Findings, Labs, papers, benchmark tasks, and experiment materials have inconsistent one-off links rather than one validated relationship source.
- Existing output-connected Labs retain complete HTML tables, sometimes thousands of hidden rows, and several operate as filters rather than explainers. This is accessible without JavaScript but expensive in DOM size and weak in immediate interpretation.

## Route-by-route record

| Route | Purpose | Current controls → output | Source | Layout / behavior | Context and recommendation |
| --- | --- | --- | --- | --- | --- |
| `results.html` | Plain-language findings | None | Canonical baseline plus registered study summaries | Seven desktop/tablet intersections; no document overflow; mobile stacks | Duplicate DD-013 finding; no registry or systematic reverse links. Generate six thematic groups from one result registry and a right-column `.finding-stack`. |
| `research/dd-012.html` | DD-012 study record | None | `public.yml`, claims, passing runs, artifacts | No overflow; good no-JS behavior because static | Add anchors and generated links to findings, Attention Lab, paper, benchmark/experiment uses, related studies, program/family. |
| `research/dd-016.html` | DD-016 study record | None | Same validated study pipeline | No overflow; static | Add anchors and generated links to Threshold Lab, Threshold paper, benchmark/experiment uses, claims/runs, program/family. |
| `labs.html` | Lab catalogue | None | Hard-coded Lab details | Responsive; no overflow | Classify cards as Interactive model, Data explorer, or Guided exhibit and group by capability/theorem family. |
| `labs/sequential.html` | Compare batching schedules | Scenario index → sentence only | DD-004 run is named but no output loaded | Fake interaction; default-only fallback; mobile contained | Rebuild as data explorer using all 16 exact schedule rows with fixture, budget, schedule, timeline, actions/rounds comparison, reset, URL state, and full fallback. |
| `labs/coverage.html` | Explain overlapping coverage | Scenario index → sentence only | DD-005 run is named but no output loaded | Fake interaction; default-only fallback | Rebuild as guided data explorer over three exact fixtures and named portfolio rules; show union, overlap, gap, action/outcome sets, baseline, reset, URL state. |
| `labs/mechanisms.html` | Compare incentive mechanisms | Scenario index → sentence only | DD-006B run named; generated JSON exposes summary only | Fake interaction; hidden-action limit only in prose | Rebuild from DD-006/DD-006A/DD-006B public data; expose implementation/margin/discovery/subsidy/budget outputs and observability comparison. |
| `labs/audit.html` | Synthetic audit/calibration | Scenario index → sentence only | DD-007 run named but no output loaded | Fake interaction; synthetic boundary not visually prominent | Rebuild as synthetic data explorer over 12 registered conditions; show mean, bias, RMSE, coverage, duplication/provenance metrics, calibration visual, reset, URL state. |
| `labs/evidence-acquisition.html` | Compare source acquisition | Scenario index → sentence only | DD-008 run named but no output loaded | Fake interaction; no phase or welfare output | Rebuild from DD-008/DD-008A/DD-008B exact public outputs; expose team, accuracy, cost, mode, source counts, gap, discovery/net value, trap status, counterexample. |
| `labs/atlas.html` | Explore coherent architectures | Architecture index → sentence only | DD-009 summary/20 rows generated but not wired to UI | Fake interaction despite useful generated JSON; invalid combinations invisible | Rebuild around named coherent rows and component filters; show registered rejection reasons for invalid combinations, exact metrics, Pareto scatter/status, and baseline. |
| `labs/threshold.html` | Explore threshold phase diagram | Threshold select → six exact raw strings | DD-016 exact eight-row public copy | Control is substantive; raw fractions dominate and wrap; complete fallback table | Add human percentage/count displays with exact secondary/copyable values, three-protocol line chart, occupancy consequences, capacity floor, selected-region takeaway, reset and URL state. |
| `labs/equilibrium-selection.html` | Explore exact games | Fixture, agents, threshold → eight outputs | DD-017 exact 160-row public copy | Substantive but table-first and fraction-heavy; full no-JS table | Add formatted primary cards, baseline comparison, compact visual, takeaway; retain technical table/data. |
| `labs/dynamic-attention.html` | Explore dynamic profiles | Agents, p, q, objective → eight outputs | DD-015 exact 64-row public copy | Substantive but table-first; complete fallback | Add formatted immediate cards, protocol comparison visual, takeaway; retain technical table/data. |
| `publications/threshold-discovery.html` | Paper detail/provenance | None | Validated PDF/metadata | Static, responsive | Add generated studies-used, key claims, Labs, findings, and build provenance links. |
| `benchmark/results.html` | Filter compatible exact result vectors | Task filter → visible rows/count | DD-010 v3 | Substantive table filter; no-JS complete table; mobile uses internal scroll | Add immediate selected-task result summary/visual and generated study/claim relationships. |

## Baseline protected inventories

- Claims: 96.
- Passing manifests: 46 of 49 total manifests.
- Registered studies: 24.
- Validated paper routes: 6.
- Generated routes: 72.
- No new research run was created by the baseline build.

The implementation acceptance must compare claim, manifest, passing-run, study, paper-source, paper-PDF, and immutable-output inventories against this baseline.
