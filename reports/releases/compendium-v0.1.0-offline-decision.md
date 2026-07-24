# Compendium v0.1.0 offline release decision

Decision: **`offline-release-candidate-toolchain-ready`**.

This is an offline implementation decision, not a publication decision. The
candidate is version `0.1.0`, candidate tag `dd-compendium-v0.1.0`, and future
title **Distributed Discovery Research Compendium v0.1.0**.

## Frozen content boundary

The future compendium will identify repository source at one explicit immutable
revision and attach five deterministic assets: an evidence manifest, checksum
file, paper citation metadata, a normalized seven-paper bundle, and release
notes. The paper bundle includes tracked declared content under the seven local
paper roots. It excludes transient build logs, caches, collision-copy files,
untracked files, private material, credentials, local authorization, site
output, Git metadata, and a duplicate of the read-only upstream paper.

The seven PDFs retain their exact repository hashes and 119-page total. Local
paper status remains working paper, research note, or synthesis note as recorded
in the lifecycle registry. This archive creates no peer-review, acceptance,
journal-publication, or external-validation implication.

## Deterministic representation

ZIP members are sorted lexically, timestamped `1980-01-01 00:00:00`, stored
with regular-file mode `0644`, encoded as UTF-8, and compressed with DEFLATE
level 9. The builder reads only Git-tracked regular files. The final source
revision is an explicit CLI input, so no committed manifest claims the commit
that contains itself.

Dry-run artifacts use a fixed caller-supplied UTC timestamp and null external
coordinates. Release mode remains a local asset build and requires a separately
supplied, schema-valid owner authorization. It cannot tag, push, create a
release, upload, or contact Zenodo.

## External boundary

No Git tag, GitHub Release, Zenodo deposit, DOI, arXiv or journal submission,
package publication, provider call, private benchmark material, study, claim,
run, theorem, estimate, or paper edit is authorized here. Owner licensing
attestations, explicit release authorization, GitHub execution, and observed
Zenodo ingestion are later gates.
