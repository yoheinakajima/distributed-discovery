# Zenodo readiness audit

Completion update 2026-07-24: Compendium v0.1.0 is now externally published
and Zenodo-verified. The annotated tag `dd-compendium-v0.1.0` targets
`3ca173f4e9e81a6d0e3e56205e428c596edc050e`; the public Zenodo software record
is <https://zenodo.org/records/21535005>. Its version DOI is
`10.5281/zenodo.21535005` and its concept DOI is
`10.5281/zenodo.21535004`. The sole Zenodo source archive was independently
compared with all 2,379 files in the authorized Git tree and is byte-identical.
The observed record, file checksum, archive SHA-256, and citation convention
are recorded in `docs/releases/releases.yml`. No `.zenodo.json` exists.

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

The prerequisites at the time of this historical audit were: owner resolution
of licensing decisions; a clean, fully validated candidate commit; an
authorized immutable tag and GitHub Release; owner-side Zenodo connection and
repository enablement; successful ingest verification; and recording only the
identifiers Zenodo actually assigns. All were completed for v0.1.0; future
releases require a fresh pass.
