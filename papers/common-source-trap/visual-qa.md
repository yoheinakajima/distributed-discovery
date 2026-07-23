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
