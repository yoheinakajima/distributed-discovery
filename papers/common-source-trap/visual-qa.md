# Common-Source Trap visual QA

- Audit date: 2026-07-21
- Artifact: `The_Common_Source_Trap.pdf`
- SHA-256: `afa9384eca60cf2a0291c2c42012f15ca59bf3d29b7c939b1882a0237ea58ff7`
- Render: Poppler `pdftoppm`, PNG at 120 DPI
- Pages inspected: all 21 pages
- Result: passed

Every rendered page was inspected for clipping, overflow, collisions, illegible
type, missing glyphs, malformed equations, broken tables, stranded headings,
and excessive blank space. Connector-label collisions found in the first render
of Figures 7 and 9 were removed in the generator and the complete PDF was
rebuilt. A nearly empty final references page was replaced by a substantive
extension-audit appendix; the resulting references page is balanced and fully
legible. The final render has no observed visual defects. Any PDF checksum
change invalidates this record and requires a new all-page review.

## Phase 2 editorial rebuild

Reviewed 2026-07-22 after the organizational-search literature and publication
status pass. Two consecutive builds were byte-identical at SHA-256
`afa9384eca60cf2a0291c2c42012f15ca59bf3d29b7c939b1882a0237ea58ff7`.
All 21 pages were rendered with Poppler and inspected. The final artifact has no
observed clipping, collision, overflow, broken glyph, malformed table or
figure, unresolved reference, or unintended blank page.

## AO-0014 Round 1 revision

Reviewed 2026-08-06 after the complete four-review bundle and evidence-bound
editorial revision. Two consecutive native builds were byte-identical at
SHA-256
`ab53c6e4bd099234e42178646abdd7c9692533dfb0b63cea9d3d60ba1ccf1150`.
Poppler 26.08.0 rendered all 21 pages at 120 DPI. Pages 1--19 were inspected in
the first revised build and then confirmed byte-identical as rendered PNGs after
the bibliography-layout repair; pages 20--21 were inspected from the exact final
PDF. No page has clipping, overlap, malformed glyphs, broken equations, table or
figure collisions, stranded headings, missing content, or excessive blank
space. The provisional 22-page build was rejected because its final page held
only one short reference; the smaller bibliography block restores a balanced
21-page artifact.
