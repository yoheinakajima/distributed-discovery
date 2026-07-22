# Threshold Discovery visual QA

Reviewed 2026-07-22 against `Threshold_Discovery.pdf` with SHA-256
`b38bb30f3ce63889526a092d78dd3f202d3beb54178bcdc272aba85c321b1995`.

Commands:

```sh
make threshold-discovery
pdfinfo papers/threshold-discovery/Threshold_Discovery.pdf
pdftoppm -png -r 120 papers/threshold-discovery/Threshold_Discovery.pdf tmp/pdfs/threshold-discovery/page
```

All 20 page PNGs were inspected at readable resolution. Pages 1-20 have no
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
