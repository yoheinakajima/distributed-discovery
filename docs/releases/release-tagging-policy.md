# Release tagging policy

Compendium versions use semantic versioning. The authorized tag form is:

`dd-compendium-vMAJOR.MINOR.PATCH`

- **MAJOR** changes an incompatible public data, evidence, or citation
  contract.
- **MINOR** adds compatible studies, claims, papers, or public interfaces.
- **PATCH** corrects compatible documentation, metadata, validation, or
  packaging.

The first candidate version may be `0.1.0`, but no candidate string creates a
tag or release authority. Tags are immutable, annotated, and point to the
exact reviewed release commit. A failed candidate reuses neither a published
tag nor a DOI; it is corrected before publication or issued as a new version.

The first release is now immutable: annotated tag `dd-compendium-v0.1.0`
points to source revision
`3ca173f4e9e81a6d0e3e56205e428c596edc050e`. Its external identifiers and
asset hashes are recorded in [`releases.yml`](releases.yml).

Release filenames must be stable within a version. Historical run IDs, claim
IDs, study IDs, and checksums are never rewritten to match a release number.
