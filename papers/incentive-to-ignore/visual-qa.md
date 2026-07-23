# Incentive to Ignore visual QA

- Audit date: 2026-07-21
- Artifact: `The_Incentive_to_Ignore.pdf`
- SHA-256: `651c91fb68df6b2f1397ca86f3842b7c2fa9c067601957c32401a7f5e95cd24b`
- Render: Poppler `pdftoppm`, PNG at 120 DPI
- Pages inspected: all 21 pages
- Result: passed

Every rendered page was inspected for clipping, overflow, collisions, illegible
type, missing glyphs, malformed equations, broken tables, stranded headings,
and excessive blank space. The first render exposed an overwide conditional
phase map and a sparse final references page. The phase map was scaled within
the generator, and a substantive artifact declaration now balances the final
page. The rebuilt 20-page render has no observed visual defects. Any PDF
checksum change invalidates this record and requires a new all-page review.

## Phase 2 editorial rebuild

Reviewed 2026-07-22 after the companion-paper citation, literature, and status
pass. Two consecutive builds were byte-identical at SHA-256
`651c91fb68df6b2f1397ca86f3842b7c2fa9c067601957c32401a7f5e95cd24b`.
All 21 pages were rendered with Poppler and inspected. The final artifact has no
observed clipping, collision, overflow, broken glyph, malformed table or
figure, unresolved reference, or unintended blank page.
