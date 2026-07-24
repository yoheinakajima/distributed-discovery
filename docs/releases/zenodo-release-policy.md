# Zenodo release policy

This policy prepares stable archival releases without authorizing one. The
repository currently has no Git tag, GitHub Release, Zenodo deposit, or DOI.

## Release identity

A compendium release uses a Git tag governed by
[`release-tagging-policy.md`](release-tagging-policy.md), a GitHub Release, and
a validated release evidence manifest. If the owner later enables the GitHub
repository in Zenodo, the ingested release receives a version DOI. The Zenodo
concept DOI is cited only when the intended object is the evolving compendium;
exact reproduction cites the version DOI.

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

The owner must connect GitHub to Zenodo and enable this repository through the
owner-side interface. Automation and API credentials are outside this task.
The activation checklist is a human gate, not evidence that integration is
enabled.

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
