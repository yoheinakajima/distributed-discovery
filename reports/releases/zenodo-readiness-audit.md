# Zenodo readiness audit

Audited 2026-07-23. The repository is **prepared but not release-ready**.

The root `CITATION.cff` correctly describes the compendium and contains no DOI.
Per-paper citation metadata is separate. No `.zenodo.json` exists; if one is
added, its documented metadata precedence must be reconciled deliberately.
There are no Git tags or GitHub Releases, and no evidence that Zenodo is
connected or that this repository is enabled there.

The local dry-run manifest validates the seven exact PDFs, 119 total pages,
source checksums, and current 110-claim/26-study inventory. All external
identifiers and release coordinates remain null.

Missing prerequisites are: owner resolution of licensing decisions; a clean,
fully validated candidate commit; an authorized immutable tag and GitHub
Release; owner-side Zenodo connection and repository enablement; successful
ingest verification; and recording only the identifiers Zenodo actually
assigns.
