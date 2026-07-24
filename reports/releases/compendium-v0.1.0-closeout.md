# Compendium v0.1.0 external publication closeout

Decision: **`release-published-zenodo-verified`**.

Closeout pull request: #186,
<https://github.com/yoheinakajima/distributed-discovery/pull/186>.

## Immutable release identity

- Version: `0.1.0`
- Annotated tag: `dd-compendium-v0.1.0`
- Tag object: `0fa9bd22b9a49a0e028e6fccda60b9bc2dadc7f6`
- Source revision:
  `3ca173f4e9e81a6d0e3e56205e428c596edc050e`
- GitHub Release:
  <https://github.com/yoheinakajima/distributed-discovery/releases/tag/dd-compendium-v0.1.0>
- GitHub publication time: `2026-07-24T13:52:52Z`

The local and remote references identify an annotated tag object whose peeled
target is the authorized source revision. The tag was pushed once and was not
moved, deleted, or force-updated.

## GitHub Release assets

The public, non-draft, non-prerelease GitHub Release has exactly five custom
assets.

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `distributed-discovery-compendium-v0.1.0-release-evidence-manifest.json` | 4,733 | `a6c742a3a0ed8e962fb24d05bad236c07fe058ce68ba6b5cf2cd057dc1044f9f` |
| `distributed-discovery-compendium-v0.1.0-SHA256SUMS.txt` | 511 | `c6c9417933e305508a3c1ed418fb588b4fa897c471e98076732f30747fcc3231` |
| `distributed-discovery-compendium-v0.1.0-paper-citation-metadata.yml` | 5,725 | `37c66ed19a9d84cc021eb27567fa74fd399b0f73b34b7aae845486c9420e538c` |
| `distributed-discovery-compendium-v0.1.0-papers.zip` | 1,088,601 | `08bab6f3d0fb7b1c6282b8663a11e1709ded0ee93769f7ee60fec690e01af469` |
| `distributed-discovery-compendium-v0.1.0-release-notes.md` | 2,152 | `35d757da84ea3a5400db4e64963c3aee484029fe0e3da9c0c07fa54352128b92` |

Fresh public downloads were byte-identical to the canonical upload set,
`SHA256SUMS` passed, and the independent verifier confirmed 132 normalized
paper-bundle members, seven papers, and 119 pages. GitHub's tag-generated
[source ZIP](https://github.com/yoheinakajima/distributed-discovery/archive/refs/tags/dd-compendium-v0.1.0.zip)
and
[source TAR.GZ](https://github.com/yoheinakajima/distributed-discovery/archive/refs/tags/dd-compendium-v0.1.0.tar.gz)
both resolved with HTTP 200.

## Zenodo record and identifiers

- Record ID: `21535005`
- Record: <https://zenodo.org/records/21535005>
- Status: published
- Resource type: software
- Title: *Distributed Discovery Research Compendium*
- Creator: Yohei Nakajima, represented as `Nakajima, Yohei`
- License: MIT, represented as `mit-license`
- Publication date: `2026-07-24`
- Zenodo version field: `dd-compendium-v0.1.0`
- GitHub relation:
  <https://github.com/yoheinakajima/distributed-discovery/tree/dd-compendium-v0.1.0>
- Version DOI: <https://doi.org/10.5281/zenodo.21535005>
- Concept DOI: <https://doi.org/10.5281/zenodo.21535004>

Zenodo's GitHub integration uses the exact tag string in its `version` field.
The semantic compendium version remains `0.1.0`. The version DOI identifies
this exact release; the concept DOI identifies the evolving compendium and
currently resolves to v0.1.0 as the latest version.

The published record contains one integrated source archive:
`yoheinakajima/distributed-discovery-dd-compendium-v0.1.0.zip`, 25,825,951
bytes, Zenodo checksum `md5:b3484739a08bec27499a580b19755aff`,
independently computed SHA-256
`8f04d5dc25b971c879c59d4f14cccb05459f67269fa486dc9acbdf692a3aa33f`.
All 2,379 archived files are byte-identical to the authorized Git tree. There
are no missing, extra, or mismatched files, no `.env` file, no local
authorization, no Git metadata, and no untracked or private benchmark artifact.
The tagged `CITATION.cff` and all seven primary PDF hashes match.

## Citation convention

For exact reproduction of v0.1.0, cite version DOI
`10.5281/zenodo.21535005`. For the evolving Distributed Discovery compendium,
cite concept DOI `10.5281/zenodo.21535004`. Load-bearing scientific citations
also retain the relevant paper, claim ID, immutable run ID, and artifact
checksum.

The closeout updates `CITATION.cff` on `main` with the actual release date and
version DOI. It does not change the tagged commit. Per-paper DOI fields remain
null because this compendium release does not mint or imply paper-specific
DOIs.

## Preserved scientific and editorial boundary

The release contains 110 claims through DD-C-0110, 26 studies through DD-022,
51 run manifests, and 48 passing immutable runs. It creates no claim, study,
run, theorem, proof promotion, benchmark result, provider evidence, or private
material.

The seven project-authored PDFs remain 119 pages with exact accepted hashes.
Their working-paper, research-note, and synthesis-note lifecycle labels remain
unchanged. The archival compendium release does not imply paper submission,
acceptance, peer review, journal publication, or external scientific
validation.

The repository and original artifacts remain MIT-licensed under the owner
attestation used for this exact release. The release is not legal advice and
does not authorize an arXiv license selection or journal copyright transfer.
The canonical Shared Discovery Paradox upstream remains pinned, separate, and
read-only.

No TreasureBench package was published and no PyPI, npm, or other namespace
was reserved. No provider/model call occurred; private benchmark material
remained absent.

## Validation and correction policy

Pre-tag acceptance passed the required repository, program-memory,
publication, TreasureBench, release, Agents v1, 365-test, typing, claim/run,
seven-paper, and site gates. The public GitHub and Zenodo files were then
downloaded and independently verified.

The closeout branch reruns all required checks and adds focused release
registry, DOI-role, CFF, asset-hash, tag/source, Zenodo-record, program-memory,
site, and false-paper-promotion tests. Final branch and post-merge workflow IDs
are recorded in the issue and final handoff after they complete.

Local closeout acceptance passed on 2026-07-24: CFF 1.2.0 validation, Ruff,
Mypy across 181 source files, 369 Pytest tests, 110-claim validation, 51
manifest validation, program-memory/publication/TreasureBench/release/Agents v1
audits, all seven paper builds, and the 89-page site build. The expected
Information Sharing Frontier provenance refresh produced by `make papers` was
restored to the authorized tracked bytes before commit; no paper source or PDF
change remains.

This version is immutable. Any future scientific or file correction preserves
v0.1.0 and uses a documented new version; the tag and verified external assets
must not be moved or silently replaced.

## Next gate

The exact next gate is **TreasureBench Agents v1 sealed engineering pilot
registration and authorization**. It remains separately authorized,
non-inferential, and provider/private-material gated.
