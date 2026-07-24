# Zenodo owner activation checklist

The offline v0.1.0 toolchain is ready for validation, but this checklist is
inactive until the owner supplies a real schema-valid authorization and
licensing attestations. Synthetic fixtures never authorize release mode.

Status: **pending owner action; no integration is enabled by this record**.

- [ ] Confirm repository licensing and every unresolved item in the artifact
  license matrix.
- [ ] Confirm the intended compendium version and immutable tag.
- [ ] Run `make compendium-release-readiness VERSION=0.1.0`,
  `make release-readiness`, `make verify`, `make papers`, and
  `make site` from a clean candidate commit.
- [ ] Confirm the release manifest exactly matches the candidate commit,
  PDFs, source bundles, claims, studies, runs, and checksums.
- [ ] Confirm `CITATION.cff` and any future `.zenodo.json` agree; treat
  `.zenodo.json` as the overriding source if it exists.
- [ ] Sign in to Zenodo using the repository owner's account.
- [ ] Connect the owner's GitHub account and enable
  `yoheinakajima/distributed-discovery`.
- [ ] Create the authorized Git tag and GitHub Release only after every prior
  gate passes.
- [ ] Verify Zenodo ingested the exact release and metadata.
- [ ] Record the real version DOI and concept DOI only after Zenodo assigns
  them; never prefill either identifier.
- [ ] Update the release manifest, citation registry, and public guidance in a
  subsequent reviewed change.

If import fails, preserve the GitHub release and logs, do not invent a DOI,
correct configuration, and follow the current Zenodo recovery path.
