# Common-Source Trap visual QA

- Audit date: 2026-07-21
- Artifact: `The_Common_Source_Trap.pdf`
- SHA-256: `c997bba31c021bd799f2b3a561e8e558a1334f844aa87a448ade10319dac2ad3`
- Render: Poppler `pdftoppm`, PNG at 120 DPI
- Pages inspected: all 20 pages
- Result: passed

Every rendered page was inspected for clipping, overflow, collisions, illegible
type, missing glyphs, malformed equations, broken tables, stranded headings,
and excessive blank space. Connector-label collisions found in the first render
of Figures 7 and 9 were removed in the generator and the complete PDF was
rebuilt. A nearly empty final references page was replaced by a substantive
extension-audit appendix; the resulting references page is balanced and fully
legible. The final render has no observed visual defects. Any PDF checksum
change invalidates this record and requires a new all-page review.
