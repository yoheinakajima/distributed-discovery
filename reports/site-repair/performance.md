# Site repair performance review

Date: 2026-07-22. The same 72 generated routes were measured before and after using start-tag counts as a stable DOM-size proxy.

| Measure | Before | After | Change |
| --- | ---: | ---: | ---: |
| Total HTML bytes | 8,981,307 | 7,751,076 | −1,230,231 (−13.7%) |
| Total DOM nodes | 335,514 | 243,041 | −92,473 (−27.6%) |
| Mean DOM nodes / page | 4,659.9 | 3,375.6 | −27.6% |
| Largest page | 110,426 nodes | 77,339 nodes | −29.9% |
| CSS | 20,854 bytes | 27,277 bytes | +6,423 |
| JavaScript | 18,155 bytes | 35,669 bytes | +17,514 |

## Selected routes

| Route | Before bytes / nodes | After bytes / nodes |
| --- | ---: | ---: |
| `results.html` | 9,387 / 204 | 11,212 / 214 |
| `labs/threshold.html` | 10,540 / 205 | 23,297 / 392 |
| `labs/atlas.html` | 4,348 / 111 | 123,451 / 1,464 |
| `labs/attention.html` | 2,294,266 / 110,426 | 10,689 / 293 |
| `benchmark/results.html` | 14,951 / 321 | 33,387 / 765 |

The additional CSS/JavaScript supports substantive Lab interaction, URL state, reset behavior, visual comparisons, exact-value presentation, and relationship navigation. The large aggregate improvement comes from moving DD-012's complete interaction source to local JSON and keeping one representative static fallback row.

The remaining largest generated pages are Audience Design (77,339 nodes) and Incremental Sharing (23,003 nodes). Their complete exact tables remain local and collapsed; converting those more complex multi-registry explainers to JSON rendering is a future presentation optimization, not a scientific or correctness blocker. No external library, CDN, API, analytics, or tracking dependency was added.
