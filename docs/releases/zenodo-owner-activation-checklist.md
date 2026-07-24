# Zenodo owner activation checklist

Compendium v0.1.0 completed this checklist on 2026-07-24. The active,
schema-valid owner authorization and licensing attestations were validated
against the exact tagged source. Synthetic fixtures never authorize release
mode. Future releases require a new authorization and another checklist pass.

Status: **v0.1.0 complete; GitHub Release, Zenodo record, and both DOI roles
verified**.

- [x] Confirm repository licensing and every unresolved item in the artifact
  license matrix.
- [x] Confirm the intended compendium version and immutable tag.
- [x] Run `make compendium-release-readiness VERSION=0.1.0`,
  `make release-readiness`, `make verify`, `make papers`, and
  `make site` from a clean candidate commit.
- [x] Confirm the release manifest exactly matches the candidate commit,
  PDFs, source bundles, claims, studies, runs, and checksums.
- [x] Confirm `CITATION.cff` and any future `.zenodo.json` agree; treat
  `.zenodo.json` as the overriding source if it exists.
- [x] Sign in to Zenodo using the repository owner's account.
- [x] Connect the owner's GitHub account and enable
  `yoheinakajima/distributed-discovery`.
- [x] Create the authorized Git tag and GitHub Release only after every prior
  gate passes.
- [x] Verify Zenodo ingested the exact release and metadata.
- [x] Record the real version DOI and concept DOI only after Zenodo assigns
  them; never prefill either identifier.
- [x] Update the release registry, citation metadata, and public guidance in a
  subsequent reviewed change.

If import fails, preserve the GitHub release and logs, do not invent a DOI,
correct configuration, and follow the current Zenodo recovery path.
