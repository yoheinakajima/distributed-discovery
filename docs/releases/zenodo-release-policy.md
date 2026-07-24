# Zenodo release policy

This policy governs stable archival releases. Compendium v0.1.0 was published
and verified on 2026-07-24 as annotated tag `dd-compendium-v0.1.0`, a public
GitHub Release, and Zenodo record `21535005`. Its version DOI is
`10.5281/zenodo.21535005`; its concept DOI is
`10.5281/zenodo.21535004`. Future versions require separate authorization.

## Release identity

A compendium release uses a Git tag governed by
[`release-tagging-policy.md`](release-tagging-policy.md), a GitHub Release, and
a validated release evidence manifest. The owner-enabled GitHub integration
archives each authorized release. The Zenodo concept DOI is cited only when
the intended object is the evolving compendium; exact reproduction cites the
version DOI.

Paper citations remain paper-specific. A load-bearing claim citation includes
the paper identifier or immutable source, claim ID, immutable run ID where
applicable, and checksum where the exact file matters. A living site URL is a
discovery aid, not the sole load-bearing source.

## Required release contents

- repository source at one immutable commit and tag;
- the seven validated local PDFs and their checksums;
- paper citation metadata and source-bundle paths;
- claim ledger, registered-study index, immutable run records, schemas, and
  validation reports appropriate to the version;
- a manifest conforming to
  `release-evidence-manifest.schema.json`;
- root `CITATION.cff`, license, changelog, and reproducibility instructions.

No release may contain a fabricated or provisional DOI, arXiv ID, run, claim,
or result. Missing external identifiers are JSON/YAML null values.

## Metadata and activation

`CITATION.cff` describes the compendium. Per-paper metadata stays in
`docs/publication/paper-citation-metadata.yml`. If `.zenodo.json` is later
added, Zenodo treats it as metadata precedence over `CITATION.cff`; the two
must be deliberately reconciled before release.

The v0.1.0 integration and ingest are directly verified. Any future repository
or integration change remains an owner-side action. Automation and API
credentials are outside the default release workflow; an activation checklist
is a gate, not evidence of a successful future ingest.

## Failure recovery

Never move or overwrite an existing release tag. If validation fails before a
release, fix the candidate and rerun the full gate. If an error is discovered
after publication, preserve the affected version, document the correction,
and issue a new version. Withdraw only when required, retaining a durable
correction record. A failed or partial Zenodo import must not be represented
as a DOI-bearing release.

Policy inputs were checked on 2026-07-23 against the official
[Zenodo GitHub integration](https://help.zenodo.org/docs/github/enable-repository/),
[CITATION.cff guidance](https://help.zenodo.org/docs/github/describe-software/citation-file/),
[`.zenodo.json` guidance](https://help.zenodo.org/docs/github/describe-software/zenodo-json/),
and [DOI versioning guidance](https://zenodo.org/help/versioning). Recheck
current service behavior at release time.
