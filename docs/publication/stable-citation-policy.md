# Stable citation policy

A load-bearing scientific citation resolves to an immutable object: a specific
arXiv version, a version-specific repository release DOI, a formally published
version, or a tagged repository release with an immutable evidence manifest.
The living site may support discovery and verification but is not sufficient
by itself.

Preferred evidence citation fields are:

1. paper-specific arXiv version when real;
2. version-specific compendium release DOI when real;
3. claim ID;
4. immutable run ID for generated evidence;
5. file checksum when the file is load-bearing.

Use a concept/latest DOI only when the citation intentionally means the
evolving compendium. Never fabricate a DOI, arXiv identifier, release tag, or
realistic-looking placeholder. Until an identifier exists, store `null` and
cite the current working-paper metadata plus claim/run/checksum provenance
without pretending immutability.

Example, before external identifiers exist:

> Nakajima (2026), *paper title*, working paper; arXiv version: null;
> compendium release DOI: null; claim: `DD-C-xxxx`; immutable run:
> `YYYY...`; artifact SHA-256: `<computed checksum>`.

The symbolic values above are field descriptions, not reserved identifiers.
Root `CITATION.cff` remains the compendium citation. Per-paper metadata is
separate.
