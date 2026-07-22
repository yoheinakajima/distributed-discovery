# Visual QA — Information Sharing Frontier

- Reviewed UTC: `2026-07-22T22:54:18Z`
- Source commit: `d05b4072e91739680ab7918dde50909130d81b4b`
- Build command: `make information-sharing-frontier`
- Artifact: `When_Does_Information_Sharing_Improve_Decentralized_Discovery.pdf`
- PDF SHA-256: `2f8b68d5a690e6369e4c3236313eb93f060bfbe73ec531903c090f6ec6f8b6a1`
- Page count: `26`
- Page size: US Letter, `612 × 792` points

All 26 pages were rendered to PNG with Poppler and reviewed in four complete
contact sheets. Pages containing dense generated assets were also inspected at
full rendered resolution: 3, 10, 14, 16, 18, and 19. The title, abstract,
theorem statements, equations, citations, footers, bibliography, eight figures,
eight tables, and their provenance notes are legible. No clipping, collision,
overflow, broken glyph, blank page, unresolved reference, or unintended host
path is visible.

The first inspection found three defects: registry labels touched, strategic
curve labels overlapped, and the equilibrium-selection diagram was unreadable.
The generator was corrected, the PDF was rebuilt twice byte-identically, and
pages 10, 14, and 16 were rerendered and re-reviewed. The final registry uses
smaller category labels, the strategic plot uses a separated legend, and the
selection map is a four-column authority/strategy table. All three corrections
pass at full rendered resolution.

The final asset and exact-data checksums are recorded in
`source-provenance.json`; the independent audit revalidates each of them and
rejects deliberate metadata corruption in `asset-corruption-tests.json`.
