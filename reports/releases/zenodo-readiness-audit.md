# Zenodo readiness audit

Update 2026-07-24: the deterministic offline Compendium v0.1.0 candidate
toolchain is implemented and its five dry-run assets pass byte-identical
double-build and independent verification. The repository remains **not
externally release-ready**: no tag or GitHub Release exists, Zenodo activation
and ingestion are unverified, manuscript/PDF/generated-figure owner licensing
attestations remain pending, and no DOI exists. The exact next gate is an
owner-authorized external publication followed by observed Zenodo ingestion.

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
