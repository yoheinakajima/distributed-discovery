# Threshold Discovery visual QA

Reviewed 2026-07-22 against `Threshold_Discovery.pdf` with SHA-256
`634e96662989a3fd6efb5fc3e6919883897e60511826e25c6d0176bac4af9249`.

Commands:

```sh
make threshold-discovery
pdfinfo papers/threshold-discovery/Threshold_Discovery.pdf
pdftoppm -png -r 120 papers/threshold-discovery/Threshold_Discovery.pdf tmp/pdfs/threshold-discovery/page
```

All 21 page PNGs were inspected at readable resolution. Pages 1-21 have no
clipped or overlapping text, broken rules, blank pages, unresolved-reference
markers, unreadable glyphs, black boxes, or overfull tables. The threshold
phase plot, four generated census/integration figures, four generated tables,
equations, bibliography, page numbers, and artifact declaration remain inside
the text block and are legible. The final build log contains no unresolved
reference, unresolved citation, or overfull-box warning.

During review, page 7 exposed a Python escape error that rendered `tau` as
`au` in two generated labels. The builder strings were corrected to raw LaTeX,
the deterministic PDF was rebuilt, and the corrected page was re-rendered and
re-inspected. Page 20's long run IDs were also converted to a readable list;
only pages 7 and 20 changed, and both final renders passed re-inspection.

## Phase 2 editorial rebuild

Reviewed 2026-07-22 after the utility-design literature and publication-status
pass. Two consecutive builds were byte-identical at SHA-256
`634e96662989a3fd6efb5fc3e6919883897e60511826e25c6d0176bac4af9249`.
All 21 pages were rendered with Poppler and inspected. The final artifact has no
observed clipping, collision, overflow, broken glyph, malformed table or
figure, unresolved reference, or unintended blank page.
